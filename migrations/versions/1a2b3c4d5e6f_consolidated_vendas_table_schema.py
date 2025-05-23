"""Consolidated vendas table schema

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2025-05-23 16:22:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2b3c4d5e6f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Get database connection
    conn = op.get_bind()
    
    # Check if vendas table exists
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    # If vendas table doesn't exist, create it with all columns
    if 'vendas' not in tables:
        op.create_table('vendas',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('cliente_id', sa.Integer(), nullable=True),
            sa.Column('cliente_nome', sa.String(100), nullable=False, server_default=''),
            sa.Column('cliente_sobrenome', sa.String(100), nullable=True),
            sa.Column('data_venda', sa.DateTime(), nullable=False),
            sa.Column('data_pagamento', sa.DateTime(), nullable=True),
            sa.Column('valor_total', sa.Float(), nullable=False, server_default='0'),
            sa.Column('forma_pagamento', sa.String(50), nullable=True),
            sa.Column('status', sa.String(50), nullable=False, server_default='Pagamento Pendente'),
            sa.Column('observacoes', sa.Text(), nullable=True),
            sa.Column('desconto_percentual', sa.Float(), nullable=True),
            sa.Column('desconto_valor', sa.Float(), nullable=True),
            sa.Column('troca_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
            sa.ForeignKeyConstraint(['troca_id'], ['trocas.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        return
    
    # If table exists, check for each column and add if missing
    columns = inspector.get_columns('vendas')
    column_names = [col['name'] for col in columns]
    
    # Add cliente_id if missing
    if 'cliente_id' not in column_names:
        op.add_column('vendas', sa.Column('cliente_id', sa.Integer(), nullable=True))
        op.create_foreign_key(None, 'vendas', 'clientes', ['cliente_id'], ['id'])
    
    # Add cliente_nome if missing
    if 'cliente_nome' not in column_names:
        op.add_column('vendas', sa.Column('cliente_nome', sa.String(100), nullable=False, server_default=''))
    
    # Add cliente_sobrenome if missing
    if 'cliente_sobrenome' not in column_names:
        op.add_column('vendas', sa.Column('cliente_sobrenome', sa.String(100), nullable=True))
    
    # Add other columns if missing
    if 'data_venda' not in column_names:
        op.add_column('vendas', sa.Column('data_venda', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
    
    if 'data_pagamento' not in column_names:
        op.add_column('vendas', sa.Column('data_pagamento', sa.DateTime(), nullable=True))
    
    if 'valor_total' not in column_names:
        op.add_column('vendas', sa.Column('valor_total', sa.Float(), nullable=False, server_default='0'))
    
    if 'forma_pagamento' not in column_names:
        op.add_column('vendas', sa.Column('forma_pagamento', sa.String(50), nullable=True))
    
    if 'status' not in column_names:
        op.add_column('vendas', sa.Column('status', sa.String(50), nullable=False, server_default='Pagamento Pendente'))
    
    if 'observacoes' not in column_names:
        op.add_column('vendas', sa.Column('observacoes', sa.Text(), nullable=True))
    
    if 'desconto_percentual' not in column_names:
        op.add_column('vendas', sa.Column('desconto_percentual', sa.Float(), nullable=True))
    
    if 'desconto_valor' not in column_names:
        op.add_column('vendas', sa.Column('desconto_valor', sa.Float(), nullable=True))
    
    if 'troca_id' not in column_names:
        op.add_column('vendas', sa.Column('troca_id', sa.Integer(), nullable=True))
        op.create_foreign_key(None, 'vendas', 'trocas', ['troca_id'], ['id'])


def downgrade():
    # Drop the entire table
    op.drop_table('vendas')
