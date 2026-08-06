"""Router de autenticacao: registro (auto-cadastro de aluno), login,
refresh, logout, recuperacao de senha e dados do usuario autenticado."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import TokenExpiredError, TokenInvalidError
from app.models.usuario import Usuario
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegistroAlunoRequest,
    ResetPasswordRequest,
    TokenResponse,
    UsuarioPublico,
)
from app.services import auth_service
from app.services.exceptions import (
    ConsentimentoNaoAceitoError,
    ContaInativaError,
    CredenciaisInvalidasError,
    EmailJaCadastradoError,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _tokens_para_response(tokens: auth_service.ParTokens) -> TokenResponse:
    return TokenResponse(
        access_token=tokens.access_token,
        access_token_expires_at=tokens.access_token_expires_at,
        refresh_token=tokens.refresh_token,
        refresh_token_expires_at=tokens.refresh_token_expires_at,
    )


@router.post("/register", response_model=UsuarioPublico, status_code=status.HTTP_201_CREATED)
async def registrar(
    payload: RegistroAlunoRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """Auto-cadastro de aluno. A conta nasce inativa, aguardando aprovacao
    (fluxo de aprovacao completo chega na Parte 3/4)."""
    try:
        return await auth_service.registrar_aluno(
            db,
            nome=payload.nome,
            email=payload.email,
            senha=payload.senha,
            aceite_lgpd=payload.aceite_lgpd,
            ip_address=get_client_ip(request),
        )
    except EmailJaCadastradoError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except ConsentimentoNaoAceitoError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
@limiter.limit(lambda: get_settings().rate_limit_login)
async def login(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        _usuario, tokens = await auth_service.autenticar(
            db,
            email=payload.email,
            senha=payload.senha,
            user_agent=request.headers.get("user-agent"),
            ip_address=get_client_ip(request),
        )
    except CredenciaisInvalidasError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    except ContaInativaError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc

    return _tokens_para_response(tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        tokens = await auth_service.renovar_tokens(
            db,
            refresh_token_jwt=payload.refresh_token,
            user_agent=request.headers.get("user-agent"),
            ip_address=get_client_ip(request),
        )
    except TokenExpiredError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    except TokenInvalidError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    except ContaInativaError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc

    return _tokens_para_response(tokens)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    payload: LogoutRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> None:
    await auth_service.logout(
        db, refresh_token_jwt=payload.refresh_token, ip_address=get_client_ip(request)
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
@limiter.limit(lambda: get_settings().rate_limit_forgot_password)
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> ForgotPasswordResponse:
    settings = get_settings()
    token = await auth_service.solicitar_redefinicao_senha(
        db, email=payload.email, ip_address=get_client_ip(request)
    )

    mensagem = (
        "Se este e-mail estiver cadastrado, um link de redefinicao de senha "
        "foi enviado."
    )
    # Nunca revelamos se o e-mail existe ou nao (mesma mensagem sempre); o
    # token so volta na resposta em ambiente que nao seja producao, como
    # substituto temporario de um servico de envio de e-mail real.
    reset_token = token if (token is not None and not settings.is_production) else None
    return ForgotPasswordResponse(message=mensagem, reset_token=reset_token)


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> None:
    try:
        await auth_service.redefinir_senha(
            db,
            token=payload.token,
            nova_senha=payload.nova_senha,
            ip_address=get_client_ip(request),
        )
    except TokenInvalidError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc


@router.get("/me", response_model=UsuarioPublico)
async def me(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    return usuario
