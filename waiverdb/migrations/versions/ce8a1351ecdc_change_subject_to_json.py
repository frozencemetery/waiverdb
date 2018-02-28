"""Change waiver.subject column type to JSON

Revision ID: ce8a1351ecdc
Revises: 1797bff52162
Create Date: 2018-02-28 14:17:15.545322

"""

# revision identifiers, used by Alembic.
revision = 'ce8a1351ecdc'
down_revision = '1797bff52162'

import json
from alembic import op
from sqlalchemy import Text, text
from sqlalchemy.dialects.postgresql import JSON
from waiverdb.models.base import json_serializer


def upgrade():
    # Re-serialize all subject values to ensure they match the new, consistent
    # serialization we are using.
    connection = op.get_bind()
    for row in connection.execute('SELECT id, subject FROM waiver'):
        fixed_subject = json_serializer(json.loads(row['subject']))
        connection.execute(text('UPDATE waiver SET subject = :subject WHERE id = :id'),
                           subject=fixed_subject, id=row['id'])

    op.drop_index('ix_waiver_subject')
    op.alter_column('waiver', 'subject', type_=JSON, postgresql_using='subject::json')
    op.create_index('ix_waiver_subject', 'waiver', [text('CAST(subject AS TEXT)')])


def downgrade():
    op.drop_index('ix_waiver_subject')
    op.alter_column('waiver', 'subject', type_=Text)
    op.create_index('ix_waiver_subject', 'waiver', ['subject'])
