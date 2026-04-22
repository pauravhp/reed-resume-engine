"""convert_education_to_multi_entry

Revision ID: f3e1b4c8d2a7
Revises: 5aa343565399
Create Date: 2026-04-21 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'f3e1b4c8d2a7'
down_revision = '5aa343565399'
branch_labels = None
depends_on = None


def upgrade():
    # Add id column with UUID generated for existing rows
    op.execute("ALTER TABLE education ADD COLUMN id UUID NOT NULL DEFAULT gen_random_uuid()")
    # Add display_order column
    op.execute("ALTER TABLE education ADD COLUMN display_order INTEGER NOT NULL DEFAULT 0")
    # Drop the old primary key on user_id
    op.execute("ALTER TABLE education DROP CONSTRAINT education_pkey")
    # Create new primary key on id
    op.execute("ALTER TABLE education ADD CONSTRAINT education_pkey PRIMARY KEY (id)")
    # Remove the server default (Python generates UUIDs for new rows)
    op.execute("ALTER TABLE education ALTER COLUMN id DROP DEFAULT")
    # Add index on user_id for efficient lookups
    op.create_index("ix_education_user_id", "education", ["user_id"])


def downgrade():
    op.drop_index("ix_education_user_id", "education")
    op.execute("ALTER TABLE education DROP CONSTRAINT education_pkey")
    op.execute("ALTER TABLE education DROP COLUMN id")
    op.execute("ALTER TABLE education DROP COLUMN display_order")
    op.execute("ALTER TABLE education ADD CONSTRAINT education_pkey PRIMARY KEY (user_id)")
