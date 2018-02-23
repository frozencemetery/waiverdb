"""Change waiver.subject column type to JSONB

Revision ID: 1797bff52162
Revises: ed43eb9b221c
Create Date: 2018-02-23 16:37:44.190560

"""

# revision identifiers, used by Alembic.
revision = '1797bff52162'
down_revision = 'ed43eb9b221c'

from alembic import op
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB


def upgrade():
    op.alter_column('waiver', 'subject', type_=JSONB, postgresql_using='subject::jsonb')


def downgrade():
    op.alter_column('waiver', 'subject', type_=Text)
