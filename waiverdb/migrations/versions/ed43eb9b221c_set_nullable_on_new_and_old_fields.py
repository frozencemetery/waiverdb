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
    # SQLite has some problem in dropping/altering columns.
    # So in this way Alembic should do some behind the scenes
    # with: make new table - copy data - drop old table - rename new table
    with op.batch_alter_table('waiver') as batch_op:
        batch_op.alter_column('subject', nullable=False)
        batch_op.alter_column('testcase', nullable=False)
        batch_op.alter_column('result_id', nullable=True)


def downgrade():
    with op.batch_alter_table('waiver') as batch_op:
        batch_op.alter_column('subject', nullable=True)
        batch_op.alter_column('testcase', nullable=True)
        batch_op.alter_column('result_id', nullable=False)
