"""Create hospedagem table

Revision ID: 003
Revises: 002
Create Date: 2025-12-10

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create hospedagem table with tipo enum."""
    # Create tipo_hospedagem enum type
    op.execute("CREATE TYPE tipo_hospedagem AS ENUM ('hotel', 'pousada', 'hostel')")
    
    op.create_table(
        'hospedagem',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ponto_id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('endereco', sa.Text(), nullable=False),
        sa.Column('telefone', sa.String(length=20), nullable=True),
        sa.Column('preco_medio', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('tipo', sa.Enum('hotel', 'pousada', 'hostel', name='tipo_hospedagem'), nullable=False),
        sa.Column('link_reserva', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['ponto_id'], ['ponto_turistico.id'], ondelete='CASCADE', name='fk_hospedagem_ponto'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('preco_medio >= 0', name='hospedagem_preco_check')
    )
    
    # Create indexes
    op.create_index('ix_hospedagem_id', 'hospedagem', ['id'], unique=False)
    op.create_index('ix_hospedagem_ponto_id', 'hospedagem', ['ponto_id'], unique=False)
    op.create_index('ix_hospedagem_tipo', 'hospedagem', ['tipo'], unique=False)
    op.create_index('ix_hospedagem_preco_medio', 'hospedagem', ['preco_medio'], unique=False)


def downgrade() -> None:
    """Drop hospedagem table and enum type."""
    op.drop_index('ix_hospedagem_preco_medio', table_name='hospedagem')
    op.drop_index('ix_hospedagem_tipo', table_name='hospedagem')
    op.drop_index('ix_hospedagem_ponto_id', table_name='hospedagem')
    op.drop_index('ix_hospedagem_id', table_name='hospedagem')
    op.drop_table('hospedagem')
    op.execute("DROP TYPE tipo_hospedagem")
