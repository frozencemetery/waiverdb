"""set nullable on new and old fields.

Revision ID: ed43eb9b221c
Revises: 71b84ccc31bb
Create Date: 2018-02-14 12:09:42.877375

"""

# revision identifiers, used by Alembic.
revision = 'ed43eb9b221c'
down_revision = '71b84ccc31bb'

from alembic import op


def upgrade():
    op.alter_column('waiver', 'subject', nullable=False)
    op.alter_column('waiver', 'testcase', nullable=False)
    op.alter_column('waiver', 'result_id', nullable=True)


def downgrade():
    op.alter_column('waiver', 'subject', nullable=True)
    op.alter_column('waiver', 'testcase', nullable=True)
    op.alter_column('waiver', 'result_id', nullable=False)
