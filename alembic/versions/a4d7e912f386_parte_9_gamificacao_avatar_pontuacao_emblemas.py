"""parte 9: gamificacao - avatar, pontuacao e emblemas

Revision ID: a4d7e912f386
Revises: d639cf9ceefd
Create Date: 2026-08-30 11:00:00.000000

"""
import uuid
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a4d7e912f386'
down_revision: str | None = 'd639cf9ceefd'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('perfis_jogo',
    sa.Column('aluno_id', sa.UUID(), nullable=False),
    sa.Column('apelido', sa.String(length=40), nullable=True),
    sa.Column('avatar_codigo', sa.String(length=30), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['aluno_id'], ['usuarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_perfis_jogo_aluno_id'), 'perfis_jogo', ['aluno_id'], unique=True)

    op.create_table('pontuacoes',
    sa.Column('aluno_id', sa.UUID(), nullable=False),
    sa.Column('pontos', sa.Integer(), server_default='0', nullable=False),
    sa.Column('sequencia_dias', sa.Integer(), server_default='0', nullable=False),
    sa.Column('maior_sequencia_dias', sa.Integer(), server_default='0', nullable=False),
    sa.Column('ultima_atividade_em', sa.Date(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['aluno_id'], ['usuarios.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pontuacoes_aluno_id'), 'pontuacoes', ['aluno_id'], unique=True)

    op.create_table('emblemas',
    sa.Column('codigo', sa.String(length=50), nullable=False),
    sa.Column('nome', sa.String(length=150), nullable=False),
    sa.Column('descricao', sa.Text(), nullable=True),
    sa.Column('ativo', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_emblemas_codigo'), 'emblemas', ['codigo'], unique=True)

    op.create_table('aluno_emblemas',
    sa.Column('aluno_id', sa.UUID(), nullable=False),
    sa.Column('emblema_id', sa.UUID(), nullable=False),
    sa.Column('conquistado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['aluno_id'], ['usuarios.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['emblema_id'], ['emblemas.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('aluno_id', 'emblema_id')
    )

    # --- Seed do catalogo inicial de emblemas ------------------------
    # Os codigos aqui devem bater com app/services/emblema_service.py.
    # Lista extensivel: novos emblemas podem ser adicionados depois via
    # INSERT direto, sem nova migration de schema.
    emblemas_iniciais = [
        ('primeira_solucao', 'Primeira solução', 'Resolveu o primeiro problema.'),
        ('sequencia_3_dias', 'Três dias seguidos', 'Praticou três dias seguidos.'),
        ('sequencia_7_dias', 'Uma semana inteira', 'Praticou sete dias seguidos.'),
        ('dez_resolvidos', 'Dez resolvidos', 'Resolveu dez problemas.'),
    ]
    emblemas_table = sa.table(
        'emblemas',
        sa.column('id', sa.UUID()),
        sa.column('codigo', sa.String()),
        sa.column('nome', sa.String()),
        sa.column('descricao', sa.Text()),
        sa.column('ativo', sa.Boolean()),
    )
    op.bulk_insert(
        emblemas_table,
        [
            {
                'id': uuid.uuid4(),
                'codigo': codigo,
                'nome': nome,
                'descricao': descricao,
                'ativo': True,
            }
            for codigo, nome, descricao in emblemas_iniciais
        ],
    )


def downgrade() -> None:
    op.drop_table('aluno_emblemas')
    op.drop_index(op.f('ix_emblemas_codigo'), table_name='emblemas')
    op.drop_table('emblemas')
    op.drop_index(op.f('ix_pontuacoes_aluno_id'), table_name='pontuacoes')
    op.drop_table('pontuacoes')
    op.drop_index(op.f('ix_perfis_jogo_aluno_id'), table_name='perfis_jogo')
    op.drop_table('perfis_jogo')
