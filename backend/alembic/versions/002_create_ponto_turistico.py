"""Create ponto_turistico table

Revision ID: 002
Revises: 001
Create Date: 2025-12-10

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create ponto_turistico table."""
    op.create_table(
        'ponto_turistico',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=False),
        sa.Column('cidade', sa.String(length=100), nullable=False),
        sa.Column('estado', sa.String(length=100), nullable=False),
        sa.Column('pais', sa.String(length=100), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=False),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=False),
        sa.Column('endereco', sa.Text(), nullable=False),
        sa.Column('criado_por', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['criado_por'], ['usuario.id'], ondelete='RESTRICT', name='fk_ponto_usuario'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('latitude BETWEEN -90 AND 90', name='ponto_latitude_check'),
        sa.CheckConstraint('longitude BETWEEN -180 AND 180', name='ponto_longitude_check')
    )
    
    # Create indexes
    op.create_index('ix_ponto_turistico_id', 'ponto_turistico', ['id'], unique=False)
    op.create_index('ix_ponto_turistico_cidade', 'ponto_turistico', ['cidade'], unique=False)
    op.create_index('ix_ponto_turistico_estado', 'ponto_turistico', ['estado'], unique=False)
    op.create_index('ix_ponto_turistico_pais', 'ponto_turistico', ['pais'], unique=False)
    op.create_index('ix_ponto_turistico_criado_por', 'ponto_turistico', ['criado_por'], unique=False)
    op.create_index('ix_ponto_turistico_deleted_at', 'ponto_turistico', ['deleted_at'], unique=False)


def downgrade() -> None:
    """Drop ponto_turistico table."""
    op.drop_index('ix_ponto_turistico_deleted_at', table_name='ponto_turistico')
    op.drop_index('ix_ponto_turistico_criado_por', table_name='ponto_turistico')
    op.drop_index('ix_ponto_turistico_pais', table_name='ponto_turistico')
    op.drop_index('ix_ponto_turistico_estado', table_name='ponto_turistico')
    op.drop_index('ix_ponto_turistico_cidade', table_name='ponto_turistico')
    op.drop_index('ix_ponto_turistico_id', table_name='ponto_turistico')
    op.drop_table('ponto_turistico')
