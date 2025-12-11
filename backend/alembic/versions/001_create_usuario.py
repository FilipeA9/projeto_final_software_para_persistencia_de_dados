"""Create usuario table

Revision ID: 001
Revises: 
Create Date: 2025-12-10

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create usuario table with role enum."""
    # Create user_role enum type
    op.execute("CREATE TYPE user_role AS ENUM ('USER', 'ADMIN')")
    
    # Create usuario table
    op.create_table(
        'usuario',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('login', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('senha_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('USER', 'ADMIN', name='user_role'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('login'),
        sa.UniqueConstraint('email')
    )
    
    # Create indexes
    op.create_index('ix_usuario_id', 'usuario', ['id'], unique=False)
    op.create_index('ix_usuario_login', 'usuario', ['login'], unique=True)
    op.create_index('ix_usuario_email', 'usuario', ['email'], unique=True)
    op.create_index('ix_usuario_role', 'usuario', ['role'], unique=False)


def downgrade() -> None:
    """Drop usuario table and enum type."""
    op.drop_index('ix_usuario_role', table_name='usuario')
    op.drop_index('ix_usuario_email', table_name='usuario')
    op.drop_index('ix_usuario_login', table_name='usuario')
    op.drop_index('ix_usuario_id', table_name='usuario')
    op.drop_table('usuario')
    op.execute("DROP TYPE user_role")
