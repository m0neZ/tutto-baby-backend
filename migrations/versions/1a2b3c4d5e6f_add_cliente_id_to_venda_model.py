"""Add cliente_id to Venda model

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2025-05-23 01:17:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add cliente_id column to vendas table
    op.add_column('vendas', sa.Column('cliente_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_vendas_cliente_id_clientes', 
        'vendas', 'clientes',
        ['cliente_id'], ['id']
    )


def downgrade():
    # Drop foreign key constraint
    op.drop_constraint('fk_vendas_cliente_id_clientes', 'vendas', type_='foreignkey')
    
    # Drop cliente_id column
    op.drop_column('vendas', 'cliente_id')
