"""Create avaliacao table

Revision ID: 004
Revises: 003
Create Date: 2025-12-10

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create avaliacao table."""
    op.create_table(
        'avaliacao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ponto_id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('nota', sa.Integer(), nullable=False),
        sa.Column('comentario', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['ponto_id'], ['ponto_turistico.id'], ondelete='CASCADE', name='fk_avaliacao_ponto'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE', name='fk_avaliacao_usuario'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('nota BETWEEN 1 AND 5', name='avaliacao_nota_check'),
        sa.UniqueConstraint('ponto_id', 'usuario_id', name='avaliacao_unique_user_spot')
    )
    
    # Create indexes
    op.create_index('ix_avaliacao_id', 'avaliacao', ['id'], unique=False)
    op.create_index('ix_avaliacao_ponto_id', 'avaliacao', ['ponto_id'], unique=False)
    op.create_index('ix_avaliacao_usuario_id', 'avaliacao', ['usuario_id'], unique=False)
    op.create_index('ix_avaliacao_nota', 'avaliacao', ['nota'], unique=False)
    op.create_index('ix_avaliacao_created_at', 'avaliacao', ['created_at'], unique=False)


def downgrade() -> None:
    """Drop avaliacao table."""
    op.drop_index('ix_avaliacao_created_at', table_name='avaliacao')
    op.drop_index('ix_avaliacao_nota', table_name='avaliacao')
    op.drop_index('ix_avaliacao_usuario_id', table_name='avaliacao')
    op.drop_index('ix_avaliacao_ponto_id', table_name='avaliacao')
    op.drop_index('ix_avaliacao_id', table_name='avaliacao')
    op.drop_table('avaliacao')
