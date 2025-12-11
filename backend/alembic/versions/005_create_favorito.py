"""Create favorito table

Revision ID: 005
Revises: 004
Create Date: 2025-12-10

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create favorito table."""
    op.create_table(
        'favorito',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('ponto_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='CASCADE', name='fk_favorito_usuario'),
        sa.ForeignKeyConstraint(['ponto_id'], ['ponto_turistico.id'], ondelete='CASCADE', name='fk_favorito_ponto'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('usuario_id', 'ponto_id', name='favorito_unique_user_spot')
    )
    
    # Create indexes
    op.create_index('ix_favorito_id', 'favorito', ['id'], unique=False)
    op.create_index('ix_favorito_usuario_id', 'favorito', ['usuario_id'], unique=False)
    op.create_index('ix_favorito_ponto_id', 'favorito', ['ponto_id'], unique=False)
    op.create_index('ix_favorito_created_at', 'favorito', ['created_at'], unique=False)


def downgrade() -> None:
    """Drop favorito table."""
    op.drop_index('ix_favorito_created_at', table_name='favorito')
    op.drop_index('ix_favorito_ponto_id', table_name='favorito')
    op.drop_index('ix_favorito_usuario_id', table_name='favorito')
    op.drop_index('ix_favorito_id', table_name='favorito')
    op.drop_table('favorito')
