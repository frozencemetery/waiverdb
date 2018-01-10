"""waive absence of result

Revision ID: f2772c2c64a6
Revises: 0a74cdab732a
Create Date: 2017-12-04 10:03:54.792758

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2772c2c64a6'
down_revision = '0a74cdab732a'


def upgrade():
    op.add_column('waiver', sa.Column('result_subject', sa.Text(), nullable=True, index=True))
    op.add_column('waiver', sa.Column('result_testcase', sa.Text(), nullable=True, index=True))

    # SQLite has some problem in dropping/altering columns.
    # So in this way Alembic should do some behind the scenes
    # with: make new table - copy data - drop old table - rename new table
    with op.batch_alter_table('waiver') as batch_op:
        batch_op.alter_column('result_subject', nullable=False)
        batch_op.alter_column('result_testcase', nullable=False)
        batch_op.drop_column('result_id')


def downgrade():
    op.add_column('waiver', sa.Column('result_id', sa.INTEGER(), nullable=True))

    with op.batch_alter_table('waiver') as batch_op:
        batch_op.drop_column('result_testcase')
        batch_op.drop_column('result_subject')
        batch_op.alter_column('result_id', nullable=False)
