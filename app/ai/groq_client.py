"""Unica porta de entrada para o provedor de LLM (Groq). Isolado em
`app/ai` de proposito: nenhum router chama esta funcao diretamente - so
`app/services/dica_service.py` a usa, o que garante que toda chamada ao
modelo passa pelas regras de negocio (progressao de nivel, guardrails,
registro de auditoria) antes de qualquer texto do aluno chegar aqui e
antes de qualquer resposta do modelo voltar para a API.

Este modulo nao sabe nada sobre "dica", "nivel" ou "perfil de aluno" - ele
so envia um system prompt + uma mensagem e devolve texto. Toda a logica
pedagogica vive em app/ai/prompts.py e app/services/dica_service.py."""

from functools import lru_cache

import groq

from app.core.config import get_settings
from app.core.logging import get_logger
from app.services.exceptions import GeracaoDicaFalhouError, MotorIaIndisponivelError

logger = get_logger(__name__)


@lru_cache
def _get_client() -> groq.AsyncGroq:
    settings = get_settings()
    return groq.AsyncGroq(api_key=settings.groq_api_key, timeout=settings.groq_timeout_segundos)


async def gerar_texto(*, system_prompt: str, mensagem_usuario: str) -> str:
    """Envia uma unica chamada de chat (sem historico - cada dica e
    independente) e devolve o texto da resposta. Levanta
    MotorIaIndisponivelError se a chave nao esta configurada, ou
    GeracaoDicaFalhouError se a chamada falhar por qualquer motivo (rede,
    timeout, rate limit, erro do provedor) - o chamador nunca ve o erro
    bruto do SDK, so a excecao de dominio."""
    settings = get_settings()
    if not settings.groq_api_key:
        raise MotorIaIndisponivelError("GROQ_API_KEY nao configurada.")

    client = _get_client()
    try:
        resposta = await client.chat.completions.create(
            model=settings.groq_modelo,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensagem_usuario},
            ],
            max_completion_tokens=settings.groq_max_tokens_resposta,
            temperature=0.4,
        )
    except groq.GroqError as exc:
        logger.warning("groq_chamada_falhou", erro=str(exc))
        raise GeracaoDicaFalhouError("Nao foi possivel gerar a dica no momento.") from exc
    except Exception as exc:  # rede, timeout etc. - nao sao groq.GroqError
        logger.warning("groq_chamada_falhou_inesperado", erro=str(exc))
        raise GeracaoDicaFalhouError("Nao foi possivel gerar a dica no momento.") from exc

    conteudo = resposta.choices[0].message.content if resposta.choices else None
    if not conteudo or not conteudo.strip():
        raise GeracaoDicaFalhouError("O motor de IA devolveu uma resposta vazia.")
    return conteudo.strip()
