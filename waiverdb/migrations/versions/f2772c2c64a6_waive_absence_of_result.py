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
    op.add_column('waiver', sa.Column('subject', sa.Text(), nullable=True, index=True))
    op.add_column('waiver', sa.Column('testcase', sa.Text(), nullable=True, index=True))


def downgrade():
    op.drop_column('waiver', 'subject')
    op.drop_column('waiver', 'testcase')
