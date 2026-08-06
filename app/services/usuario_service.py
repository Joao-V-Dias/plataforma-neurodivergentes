"""Regras de negocio de gestao de usuarios: criacao hierarquica (Diretor
cria Coordenador, Coordenador cria Professor, Professor cria Aluno - ou
qualquer papel estritamente abaixo do criador) e aprovacao de aluno
auto-cadastrado. Toda escrita e escopada a instituicao do ator: ninguem
cria ou aprova usuario de outra instituicao."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import pode_criar
from app.core.security import hash_password
from app.models.usuario import Papel, Usuario
from app.repositories import usuario_repository
from app.services import audit
from app.services.exceptions import (
    EmailJaCadastradoError,
    HierarquiaInvalidaError,
    InstituicaoDiferenteError,
    RecursoNaoEncontradoError,
)


async def criar_usuario_por_hierarquia(
    db: AsyncSession,
    *,
    criador: Usuario,
    nome: str,
    email: str,
    senha: str,
    papel: Papel,
    ip_address: str | None = None,
) -> Usuario:
    if not pode_criar(criador.papel, papel):
        raise HierarquiaInvalidaError(
            f"Um usuario com papel '{criador.papel.value}' nao pode criar contas "
            f"com papel '{papel.value}'."
        )

    if await usuario_repository.get_by_email(db, email) is not None:
        raise EmailJaCadastradoError("Ja existe uma conta cadastrada com este e-mail.")

    # Contas criadas por uma autoridade nascem ativas - quem criou ja
    # vouches pela identidade da pessoa (diferente do auto-cadastro).
    usuario = await usuario_repository.create(
        db,
        nome=nome,
        email=email,
        senha_hash=hash_password(senha),
        papel=papel,
        instituicao_id=criador.instituicao_id,
        is_active=True,
    )

    await audit.registrar_evento(
        db,
        acao="usuario_criado",
        entidade="usuario",
        entidade_id=str(usuario.id),
        usuario_id=criador.id,
        detalhes={"papel_criado": papel.value, "usuario_criado_id": str(usuario.id)},
        ip_address=ip_address,
    )
    return usuario


async def aprovar_usuario(
    db: AsyncSession,
    *,
    aprovador: Usuario,
    usuario_id: uuid.UUID,
    ip_address: str | None = None,
) -> Usuario:
    usuario = await usuario_repository.get_by_id(db, usuario_id)
    if usuario is None:
        raise RecursoNaoEncontradoError("Usuario nao encontrado.")

    if usuario.instituicao_id != aprovador.instituicao_id:
        raise InstituicaoDiferenteError("Usuario pertence a outra instituicao.")

    await usuario_repository.ativar(db, usuario)

    await audit.registrar_evento(
        db,
        acao="usuario_aprovado",
        entidade="usuario",
        entidade_id=str(usuario.id),
        usuario_id=aprovador.id,
        ip_address=ip_address,
    )
    return usuario
