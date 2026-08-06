"""Rate limiting contra brute-force, com estado compartilhado no Redis
(assim funciona corretamente mesmo com multiplas instancias da API atras
de um load balancer, nao so em memoria local de um unico processo)."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    # headers_enabled=True exigiria que todo endpoint decorado aceitasse um
    # parametro `response: Response` explicito (limitacao do slowapi); os
    # headers informativos X-RateLimit-* nao sao essenciais ao bloqueio em
    # si, entao mantemos desligado para nao acoplar os endpoints a isso.
    headers_enabled=False,
)
