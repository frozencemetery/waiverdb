"""add proxyuser waiving support

Revision ID: 0a74cdab732a
Revises: 0a27a8ad723a
Create Date: 2017-11-22 13:31:50.213681

"""

# revision identifiers, used by Alembic.
revision = '0a74cdab732a'
down_revision = '0a27a8ad723a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('waiver', sa.Column('proxied_by', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('waiver', 'proxied_by')
    # ### end Alembic commands ###
