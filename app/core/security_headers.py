"""Middleware que adiciona headers de seguranca recomendados pela OWASP a
toda resposta. Como esta API nunca serve HTML diretamente (e consumida por
um frontend separado), podemos usar uma CSP restritiva por padrao."""

from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        # HSTS instrui o navegador a so falar HTTPS com este host pelos
        # proximos 2 anos; inofensivo em requisicoes locais por HTTP (o
        # navegador so aplica a regra apos ve-lo numa resposta HTTPS).
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"

        return response
