"""Add cliente_id to Venda model

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2025-05-23 14:12:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Check if column exists before adding it
    from sqlalchemy import inspect
    
    # Get inspector
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check if column exists
    has_cliente_id = False
    try:
        columns = inspector.get_columns('vendas')
        has_cliente_id = any(col['name'] == 'cliente_id' for col in columns)
    except:
        pass
    
    # Only add if it doesn't exist
    if not has_cliente_id:
        op.add_column('vendas', sa.Column('cliente_id', sa.Integer(), nullable=True))


def downgrade():
    # Drop column
    op.drop_column('vendas', 'cliente_id')
