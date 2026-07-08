"""add revoked_tokens table

Revision ID: a1b2c3d4e5f6
Revises: f2bbe6958469
Create Date: 2026-07-08 09:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'f2bbe6958469'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crear la tabla de lista negra de refresh tokens revocados."""
    op.create_table(
        'revoked_tokens',
        sa.Column('id', sa.UUID(as_uuid=False), nullable=False),
        sa.Column(
            'token',
            sa.Text(),
            nullable=False,
            comment='Refresh Token revocado'
        ),
        sa.Column(
            'user_id',
            sa.UUID(as_uuid=False),
            nullable=True,
            comment='UUID del usuario que tenía este token'
        ),
        sa.Column(
            'revoked_at',
            sa.DateTime(timezone=True),
            nullable=False,
            comment='Momento exacto en que fue revocado'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token', name='uq_revoked_token'),
    )
    op.create_index(
        op.f('ix_revoked_tokens_token'),
        'revoked_tokens',
        ['token'],
        unique=True
    )


def downgrade() -> None:
    """Eliminar la tabla de tokens revocados."""
    op.drop_index(op.f('ix_revoked_tokens_token'), table_name='revoked_tokens')
    op.drop_table('revoked_tokens')
