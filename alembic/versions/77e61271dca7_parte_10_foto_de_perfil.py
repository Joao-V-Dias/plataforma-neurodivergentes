"""parte 10: foto de perfil

Revision ID: 77e61271dca7
Revises: a4d7e912f386
Create Date: 2026-09-03 11:58:41.991629

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '77e61271dca7'
down_revision: str | None = 'a4d7e912f386'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('fotos_perfil',
    sa.Column('usuario_id', sa.UUID(), nullable=False),
    sa.Column('nome_arquivo', sa.String(length=80), nullable=False),
    sa.Column('content_type', sa.String(length=50), nullable=False),
    sa.Column('tamanho_bytes', sa.Integer(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fotos_perfil_usuario_id'), 'fotos_perfil', ['usuario_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_fotos_perfil_usuario_id'), table_name='fotos_perfil')
    op.drop_table('fotos_perfil')
