"""Servico standalone de WebSocket para partidas (batalhas) online.

Roda separado da API principal (app/) - processo, porta e deploy proprios.
Compartilha apenas o SECRET_KEY/JWT_ALGORITHM do login para validar o
access token, sem chamar a API principal nem tocar no banco. Ver README.md
deste diretorio para o protocolo de mensagens e como rodar.
"""

import logging

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from auth import TokenInvalido, validar_token
from manager import GerenciadorBatalhas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("battle-service")

gerenciador = GerenciadorBatalhas()

app = FastAPI(title="Battle Service", version="0.1.0")

# CORS liberado por padrao: este servico so aceita conexoes autenticadas por
# JWT (mesma chave da API principal), entao a origem nao e uma linha de
# defesa aqui.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws/batalha")
async def websocket_batalha(
    websocket: WebSocket,
    token: str = Query(..., description="Access token JWT emitido pelo login da API principal"),
    nome: str = Query(..., min_length=1, max_length=200, description="Nome exibido ao oponente"),
    turma_id: str = Query(
        ..., min_length=1, description="Batalha so pareia usuarios da mesma turma"
    ),
) -> None:
    try:
        usuario_id = validar_token(token)
    except TokenInvalido as exc:
        logger.info("conexao_recusada", extra={"motivo": str(exc)})
        await websocket.close(code=4401, reason="Token invalido ou expirado")
        return

    await gerenciador.conectar(websocket, usuario_id, nome, turma_id)
    logger.info("usuario_conectado", extra={"usuario_id": str(usuario_id)})
    try:
        while True:
            dados = await websocket.receive_json()
            await gerenciador.processar_mensagem(usuario_id, dados)
    except WebSocketDisconnect:
        await gerenciador.desconectar(usuario_id)
        logger.info("usuario_desconectado", extra={"usuario_id": str(usuario_id)})
    except ValueError:
        # receive_json() levanta ValueError se o cliente mandar algo que nao
        # e JSON valido - encerra a conexao em vez de derrubar o servico.
        await gerenciador.desconectar(usuario_id)
        await websocket.close(code=4400, reason="Mensagem invalida")
