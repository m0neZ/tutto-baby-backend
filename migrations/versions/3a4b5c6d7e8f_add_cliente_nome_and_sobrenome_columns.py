"""Add cliente_nome and cliente_sobrenome columns

Revision ID: 3a4b5c6d7e8f
Revises: 2a3b4c5d6e7f
Create Date: 2025-05-23 15:17:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '3a4b5c6d7e8f'
down_revision = '2a3b4c5d6e7f'
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
