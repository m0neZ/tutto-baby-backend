"""Add missing columns to vendas table

Revision ID: 2a3b4c5d6e7f
Revises: 1a2b3c4d5e6f
Create Date: 2025-05-23 14:12:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a3b4c5d6e7f'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to vendas table
    op.add_column('vendas', sa.Column('cliente_nome', sa.String(100), nullable=False, server_default=''))
    op.add_column('vendas', sa.Column('cliente_sobrenome', sa.String(100), nullable=True))


def downgrade():
    # Drop columns
    op.drop_column('vendas', 'cliente_sobrenome')
    op.drop_column('vendas', 'cliente_nome')
