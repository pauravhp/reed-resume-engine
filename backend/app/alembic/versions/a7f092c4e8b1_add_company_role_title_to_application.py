"""add_company_role_title_to_application

Revision ID: a7f092c4e8b1
Revises: f3e1b4c8d2a7
Create Date: 2026-04-24 03:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


revision = 'a7f092c4e8b1'
down_revision = 'f3e1b4c8d2a7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('application', sa.Column('company', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('application', sa.Column('role_title', sqlmodel.sql.sqltypes.AutoString(), nullable=True))


def downgrade():
    op.drop_column('application', 'role_title')
    op.drop_column('application', 'company')
