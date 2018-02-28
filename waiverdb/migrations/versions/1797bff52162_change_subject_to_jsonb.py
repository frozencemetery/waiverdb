"""(OBSOLETED) Change waiver.subject column type to JSONB

Revision ID: 1797bff52162
Revises: ed43eb9b221c
Create Date: 2018-02-23 16:37:44.190560

"""

# revision identifiers, used by Alembic.
revision = '1797bff52162'
down_revision = 'ed43eb9b221c'


def upgrade():
    # This migration originally attempted to use the JSONB column type,
    # which would fail on Postgres 9.2.
    # So this is now replaced by ce8a1351ecdc_change_subject_to_json.py
    # however we keep this as a no-op, to avoid breaking any Waiverdb
    # deployment where this migration had successfully been applied.
    pass


def downgrade():
    pass
