"""Regras de negocio de autenticacao: registro (auto-cadastro de aluno),
login, rotacao de refresh token (com deteccao de reuso), logout e
recuperacao de senha. Toda decisao de seguranca relevante (o que acontece
quando a senha esta errada, quando um refresh token e reaproveitado etc.)
mora aqui, nao nos routers."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import (
    TokenExpiredError,
    TokenInvalidError,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    gerar_token_opaco,
    hash_password,
    hash_token_opaco,
    password_hash_precisa_atualizar,
    verify_password,
)
from app.models.usuario import Papel, Usuario
from app.repositories import (
    instituicao_repository,
    password_reset_repository,
    refresh_token_repository,
    usuario_repository,
)
from app.services import audit
from app.services.exceptions import (
    ConsentimentoNaoAceitoError,
    ContaInativaError,
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
    RecursoNaoEncontradoError,
)

logger = get_logger(__name__)


@dataclass(frozen=True)
class ParTokens:
    access_token: str
    access_token_expires_at: datetime
    refresh_token: str
    refresh_token_expires_at: datetime
    refresh_token_jti: str


async def registrar_aluno(
    db: AsyncSession,
    *,
    nome: str,
    email: str,
    senha: str,
    aceite_lgpd: bool,
    instituicao_codigo: str,
    ip_address: str | None = None,
) -> Usuario:
    if not aceite_lgpd:
        raise ConsentimentoNaoAceitoError(
            "E necessario aceitar explicitamente a politica de tratamento de dados."
        )

    instituicao = await instituicao_repository.get_by_codigo(db, instituicao_codigo)
    if instituicao is None:
        raise RecursoNaoEncontradoError("Codigo de instituicao invalido.")

    if await usuario_repository.get_by_email(db, email) is not None:
        raise EmailJaCadastradoError("Ja existe uma conta cadastrada com este e-mail.")

    settings = get_settings()
    usuario = await usuario_repository.create(
        db,
        nome=nome,
        email=email,
        senha_hash=hash_password(senha),
        papel=Papel.ALUNO,
        instituicao_id=instituicao.id,
        is_active=False,  # aguarda aprovacao (POST /usuarios/{id}/aprovar, Parte 3)
        consentimento_lgpd_aceito_em=datetime.now(UTC),
        consentimento_lgpd_versao=settings.lgpd_politica_versao,
    )

    await audit.registrar_evento(
        db,
        acao="usuario_registrado",
        entidade="usuario",
        entidade_id=str(usuario.id),
        usuario_id=usuario.id,
        detalhes={"papel": usuario.papel.value, "auto_cadastro": True},
        ip_address=ip_address,
    )
    return usuario


async def _emitir_par_de_tokens(
    db: AsyncSession,
    usuario: Usuario,
    *,
    user_agent: str | None,
    ip_address: str | None,
) -> ParTokens:
    access_token, access_expires = create_access_token(usuario.id, usuario.papel)
    refresh_token, jti, refresh_expires = create_refresh_token(usuario.id, usuario.papel)

    await refresh_token_repository.create(
        db,
        usuario_id=usuario.id,
        jti=jti,
        expires_at=refresh_expires,
        user_agent=user_agent,
        ip_address=ip_address,
    )

    return ParTokens(
        access_token=access_token,
        access_token_expires_at=access_expires,
        refresh_token=refresh_token,
        refresh_token_expires_at=refresh_expires,
        refresh_token_jti=jti,
    )


async def autenticar(
    db: AsyncSession,
    *,
    email: str,
    senha: str,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[Usuario, ParTokens]:
    usuario = await usuario_repository.get_by_email(db, email)

    if usuario is None or not verify_password(senha, usuario.senha_hash):
        await audit.registrar_evento(
            db,
            acao="login_falha",
            entidade="usuario",
            usuario_id=usuario.id if usuario else None,
            detalhes={"email": email.lower(), "motivo": "credenciais_invalidas"},
            ip_address=ip_address,
        )
        raise CredenciaisInvalidasError("E-mail ou senha invalidos.")

    if not usuario.is_active:
        await audit.registrar_evento(
            db,
            acao="login_falha",
            entidade="usuario",
            usuario_id=usuario.id,
            detalhes={"motivo": "conta_inativa"},
            ip_address=ip_address,
        )
        raise ContaInativaError("Conta inativa. Aguarde aprovacao ou contate um administrador.")

    if password_hash_precisa_atualizar(usuario.senha_hash):
        await usuario_repository.atualizar_senha(db, usuario, hash_password(senha))

    tokens = await _emitir_par_de_tokens(db, usuario, user_agent=user_agent, ip_address=ip_address)

    await audit.registrar_evento(
        db,
        acao="login_sucesso",
        entidade="usuario",
        entidade_id=str(usuario.id),
        usuario_id=usuario.id,
        ip_address=ip_address,
    )
    return usuario, tokens


async def renovar_tokens(
    db: AsyncSession,
    *,
    refresh_token_jwt: str,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> ParTokens:
    claims = decode_token(refresh_token_jwt, tipo_esperado=TokenType.REFRESH)

    registro = await refresh_token_repository.get_by_jti(db, claims.jti)
    if registro is None:
        raise TokenInvalidError("Refresh token desconhecido.")

    if registro.revoked_at is not None:
        # Reuso de um refresh token ja rotacionado/revogado: sinal de
        # possivel roubo de token. Reacao: derruba todas as sessoes ativas
        # do usuario e registra o incidente na auditoria.
        await refresh_token_repository.revogar_todos_do_usuario(db, registro.usuario_id)
        await audit.registrar_evento(
            db,
            acao="refresh_token_reutilizado",
            entidade="usuario",
            usuario_id=registro.usuario_id,
            detalhes={"jti": claims.jti},
            ip_address=ip_address,
        )
        logger.warning("refresh_token_reuse_detected", usuario_id=str(registro.usuario_id))
        raise TokenInvalidError(
            "Refresh token ja utilizado. Todas as sessoes foram revogadas por seguranca."
        )

    if registro.expires_at < datetime.now(UTC):
        raise TokenExpiredError("Refresh token expirado.")

    usuario = await usuario_repository.get_by_id(db, registro.usuario_id)
    if usuario is None or not usuario.is_active:
        raise ContaInativaError("Conta inativa.")

    novos_tokens = await _emitir_par_de_tokens(
        db, usuario, user_agent=user_agent, ip_address=ip_address
    )
    await refresh_token_repository.revogar(
        db, registro, substituido_por_jti=novos_tokens.refresh_token_jti
    )

    await audit.registrar_evento(
        db,
        acao="refresh_token_rotacionado",
        entidade="usuario",
        usuario_id=usuario.id,
        ip_address=ip_address,
    )
    return novos_tokens


async def logout(
    db: AsyncSession, *, refresh_token_jwt: str, ip_address: str | None = None
) -> None:
    try:
        claims = decode_token(refresh_token_jwt, tipo_esperado=TokenType.REFRESH)
    except (TokenExpiredError, TokenInvalidError):
        return  # logout e idempotente: token ja invalido nao e um erro

    registro = await refresh_token_repository.get_by_jti(db, claims.jti)
    if registro is not None and registro.revoked_at is None:
        await refresh_token_repository.revogar(db, registro)
        await audit.registrar_evento(
            db,
            acao="logout",
            entidade="usuario",
            usuario_id=registro.usuario_id,
            ip_address=ip_address,
        )


async def solicitar_redefinicao_senha(
    db: AsyncSession, *, email: str, ip_address: str | None = None
) -> str | None:
    """Retorna o token bruto apenas para o chamador decidir se o expoe (em
    dev, sem servico de e-mail configurado); em producao o token deve ser
    entregue exclusivamente por e-mail, nunca na resposta HTTP. Retorna
    None quando o e-mail nao corresponde a nenhuma conta - o chamador deve
    responder de forma identica em ambos os casos, para nao revelar quais
    e-mails estao cadastrados (anti-enumeration)."""
    usuario = await usuario_repository.get_by_email(db, email)
    if usuario is None:
        return None

    settings = get_settings()
    await password_reset_repository.invalidar_pendentes_do_usuario(db, usuario.id)

    token = gerar_token_opaco()
    await password_reset_repository.create(
        db,
        usuario_id=usuario.id,
        token_hash=hash_token_opaco(token),
        expires_at=datetime.now(UTC)
        + timedelta(minutes=settings.password_reset_token_expire_minutes),
    )

    await audit.registrar_evento(
        db,
        acao="senha_esqueci_solicitado",
        entidade="usuario",
        usuario_id=usuario.id,
        ip_address=ip_address,
    )
    logger.info("password_reset_requested", usuario_id=str(usuario.id))
    return token


async def redefinir_senha(
    db: AsyncSession, *, token: str, nova_senha: str, ip_address: str | None = None
) -> None:
    registro = await password_reset_repository.get_valido_por_hash(db, hash_token_opaco(token))
    if registro is None:
        raise TokenInvalidError("Token de redefinicao invalido ou expirado.")

    usuario = await usuario_repository.get_by_id(db, registro.usuario_id)
    if usuario is None:
        raise TokenInvalidError("Token de redefinicao invalido ou expirado.")

    await usuario_repository.atualizar_senha(db, usuario, hash_password(nova_senha))
    await password_reset_repository.marcar_usado(db, registro)
    # Forca novo login em todos os dispositivos apos redefinicao de senha.
    await refresh_token_repository.revogar_todos_do_usuario(db, usuario.id)

    await audit.registrar_evento(
        db,
        acao="senha_redefinida",
        entidade="usuario",
        usuario_id=usuario.id,
        ip_address=ip_address,
    )
