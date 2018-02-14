"""migrate records from old format to new.

Revision ID: 71b84ccc31bb
Revises: f2772c2c64a6
Create Date: 2018-02-14 12:04:34.688790

"""

# revision identifiers, used by Alembic.
revision = '71b84ccc31bb'
down_revision = 'f2772c2c64a6'

from alembic import op
import sqlalchemy as sa

import requests

from waiverdb.api_v1 import get_resultsdb_result
from waiverdb.models import Waiver


def convert_id_to_subject_and_testcase(result_id):
    try:
        result = get_resultsdb_result(result_id)
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            raise RuntimeError('Result id %s not found in Resultsdb' % (result_id))
        else:
            raise RuntimeError('Failed looking up result in Resultsdb: %s' % e)
    except Exception as e:
        raise RuntimeError('Failed looking up result in Resultsdb: %s' % e)
    if 'original_spec_nvr' in result['data']:
        subject = {'original_spec_nvr': result['data']['original_spec_nvr'][0]}
    else:
        if result['data']['type'][0] == 'koji_build' or \
           result['data']['type'][0] == 'bodhi_update':
            SUBJECT_KEYS = ['item', 'type']
            subject = dict([(k, v[0]) for k, v in result['data'].items()
                            if k in SUBJECT_KEYS])
        else:
            raise RuntimeError('Unable to determine subject for result id %s' % (result_id))
    testcase = result['testcase']['name']
    return (subject, testcase)


def upgrade():
    # Get a session asociated with the alembic upgrade operation.
    connection = op.get_bind()
    Session = sa.orm.sessionmaker()
    session = Session(bind=connection)

    try:
        # querying resultsdb for the corresponding subject/testcase.
        waivers = session.query(Waiver).all()
        for waiver in waivers:
            subject, testcase = convert_id_to_subject_and_testcase(waiver.result_id)
            waiver.subject = subject
            waiver.testcase = testcase
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def downgrade():
    # It shouldn't be possible to downgrade this change.
    # Because the result_id field will not be populated with data anymore.
    # If the user tries to downgrade "result_id" should be not null once again
    # like in the old version of the schema, but the value is not longer available
    raise RuntimeError('Irreversible migration')
