"""add project description column

Revision ID: a1b2c3d4e5f6
Revises: f3e1b4c8d2a7
Create Date: 2026-04-21

"""
from alembic import op

revision = 'a1b2c3d4e5f6'
down_revision = 'f3e1b4c8d2a7'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TABLE project ADD COLUMN IF NOT EXISTS description TEXT")


def downgrade():
    op.execute("ALTER TABLE project DROP COLUMN IF EXISTS description")
