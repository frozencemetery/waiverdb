"""waive absence of result

Revision ID: f2772c2c64a6
Revises: 0a74cdab732a
Create Date: 2017-12-04 10:03:54.792758

"""

from alembic import op
import sqlalchemy as sa
import requests

from waiverdb.api_v1 import get_resultsdb_result
from waiverdb.models import db, Waiver


# revision identifiers, used by Alembic.
revision = 'f2772c2c64a6'
down_revision = '0a74cdab732a'


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
    op.add_column('waiver', sa.Column('subject', sa.Text(), nullable=True, index=True))
    op.add_column('waiver', sa.Column('testcase', sa.Text(), nullable=True, index=True))

    # querying resultsdb for the corresponding subject/testcase for each result_id
    waivers = Waiver.query.all()
    for waiver in waivers:
        subject, testcase = convert_id_to_subject_and_testcase(waiver.result_id)
        waiver.subject = subject
        waiver.testcase = testcase
        db.session.commit()

    # SQLite has some problem in dropping/altering columns.
    # So in this way Alembic should do some behind the scenes
    # with: make new table - copy data - drop old table - rename new table
    with op.batch_alter_table('waiver') as batch_op:
        batch_op.alter_column('subject', nullable=False)
        batch_op.alter_column('testcase', nullable=False)
        batch_op.alter_column('result_id', nullable=True)


def downgrade():
    # It shouldn't be possible to downgrade this change.
    # Because the result_id field will not be populated with data anymore.
    # If the user tries to downgrade "result_id" should be not null once again
    # like in the old version of the schema, but the value is not longer available
    raise RuntimeError('Irreversible migration')
