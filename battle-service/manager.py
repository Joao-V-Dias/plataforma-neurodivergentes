"""Pareamento em memoria de usuarios online para partidas (batalhas).

Regra pedida: quando ha pelo menos dois usuarios da MESMA turma conectados
e disponiveis (nao em outro convite/batalha), o servico sugere uma batalha
entre os dois automaticamente (docs/prompt-redesign-frontend.md #3.6: "1x1
entre alunos online na mesma turma"). Cada um aceita ou recusa; se ambos
aceitarem, a batalha comeca. Se algum recusar ou desconectar, o outro volta
para a fila de disponiveis da turma e pode ser pareado de novo.

Estado 100% em memoria e de processo unico - se o servico reiniciar ou
rodar com mais de um worker, filas e convites em andamento sao perdidos.
Suficiente para o escopo pedido; nao usa banco nem Redis."""

import uuid
from dataclasses import dataclass, field

from fastapi import WebSocket


@dataclass
class Jogador:
    usuario_id: uuid.UUID
    nome: str
    turma_id: str
    websocket: WebSocket


@dataclass
class ConviteBatalha:
    batalha_id: uuid.UUID
    jogador_a: uuid.UUID
    jogador_b: uuid.UUID
    aceite: dict[uuid.UUID, bool] = field(default_factory=dict)


class GerenciadorBatalhas:
    def __init__(self) -> None:
        self._conectados: dict[uuid.UUID, Jogador] = {}
        self._disponiveis: dict[str, list[uuid.UUID]] = {}
        self._convites: dict[uuid.UUID, ConviteBatalha] = {}
        self._convite_por_usuario: dict[uuid.UUID, uuid.UUID] = {}
        # Pares que acabaram de se recusar nao sao sugeridos de novo um pro
        # outro nesta sessao - senao os dois voltam pra fila sozinhos e o
        # servico re-sugere a mesma batalha recusada em loop.
        self._pares_recusados: set[frozenset[uuid.UUID]] = set()

    async def conectar(
        self, websocket: WebSocket, usuario_id: uuid.UUID, nome: str, turma_id: str
    ) -> None:
        await websocket.accept()

        if usuario_id in self._conectados:
            # Reconexao (ex: refresh de pagina) - encerra a sessao antiga.
            await self.desconectar(usuario_id)

        self._conectados[usuario_id] = Jogador(usuario_id, nome, turma_id, websocket)
        self._disponiveis.setdefault(turma_id, []).append(usuario_id)
        await self._tentar_sugerir_batalha(turma_id)

    async def desconectar(self, usuario_id: uuid.UUID) -> None:
        jogador = self._conectados.pop(usuario_id, None)
        fila = self._disponiveis.get(jogador.turma_id) if jogador else None
        if fila and usuario_id in fila:
            fila.remove(usuario_id)
        self._pares_recusados = {
            par for par in self._pares_recusados if usuario_id not in par
        }

        convite_id = self._convite_por_usuario.pop(usuario_id, None)
        if convite_id is None:
            return

        convite = self._convites.pop(convite_id, None)
        if convite is None:
            return

        oponente_id = convite.jogador_b if convite.jogador_a == usuario_id else convite.jogador_a
        self._convite_por_usuario.pop(oponente_id, None)
        await self._enviar(
            oponente_id, {"tipo": "batalha_cancelada", "motivo": "oponente_desconectou"}
        )
        await self._tornar_disponivel(oponente_id)

    async def processar_mensagem(self, usuario_id: uuid.UUID, dados: dict) -> None:
        if dados.get("tipo") == "responder_batalha":
            await self._responder_batalha(usuario_id, dados)

    async def _responder_batalha(self, usuario_id: uuid.UUID, dados: dict) -> None:
        convite_id = self._convite_por_usuario.get(usuario_id)
        if convite_id is None or str(convite_id) != str(dados.get("batalha_id")):
            return  # resposta para um convite que ja nao existe mais - ignorada

        convite = self._convites.get(convite_id)
        if convite is None:
            return

        oponente_id = convite.jogador_b if convite.jogador_a == usuario_id else convite.jogador_a

        if not dados.get("aceitar"):
            self._convites.pop(convite_id, None)
            self._convite_por_usuario.pop(usuario_id, None)
            self._convite_por_usuario.pop(oponente_id, None)
            self._pares_recusados.add(frozenset({usuario_id, oponente_id}))
            await self._enviar(
                oponente_id, {"tipo": "batalha_cancelada", "motivo": "oponente_recusou"}
            )
            await self._tornar_disponivel(oponente_id)
            await self._tornar_disponivel(usuario_id)
            return

        convite.aceite[usuario_id] = True
        if not convite.aceite.get(oponente_id):
            return  # aguardando o outro jogador aceitar tambem

        self._convites.pop(convite_id, None)
        self._convite_por_usuario.pop(usuario_id, None)
        self._convite_por_usuario.pop(oponente_id, None)
        for jogador_id, rival_id in ((usuario_id, oponente_id), (oponente_id, usuario_id)):
            await self._enviar(
                jogador_id,
                {
                    "tipo": "batalha_iniciada",
                    "batalha_id": str(convite.batalha_id),
                    "oponente_id": str(rival_id),
                },
            )

    async def _tornar_disponivel(self, usuario_id: uuid.UUID) -> None:
        jogador = self._conectados.get(usuario_id)
        if jogador is None:
            return
        fila = self._disponiveis.setdefault(jogador.turma_id, [])
        if usuario_id not in fila:
            fila.append(usuario_id)
        await self._tentar_sugerir_batalha(jogador.turma_id)

    async def _tentar_sugerir_batalha(self, turma_id: str) -> None:
        fila = self._disponiveis.setdefault(turma_id, [])
        while True:
            # Limpeza defensiva: quem desconectou entre entrar na fila e ser
            # pareado aqui nao deve mais contar.
            fila[:] = [uid for uid in fila if uid in self._conectados]
            if len(fila) < 2:
                return

            id_a = fila[0]
            indice_b = next(
                (
                    i
                    for i in range(1, len(fila))
                    if frozenset({id_a, fila[i]}) not in self._pares_recusados
                ),
                None,
            )
            if indice_b is None:
                return  # id_a so tem, na fila, gente que ja recusou batalhar com ele

            id_b = fila.pop(indice_b)
            fila.pop(0)

            batalha_id = uuid.uuid4()
            convite = ConviteBatalha(batalha_id=batalha_id, jogador_a=id_a, jogador_b=id_b)
            self._convites[batalha_id] = convite
            self._convite_por_usuario[id_a] = batalha_id
            self._convite_por_usuario[id_b] = batalha_id

            jogador_a = self._conectados[id_a]
            jogador_b = self._conectados[id_b]
            await self._enviar(
                id_a,
                {
                    "tipo": "batalha_sugerida",
                    "batalha_id": str(batalha_id),
                    "oponente": {"id": str(id_b), "nome": jogador_b.nome},
                },
            )
            await self._enviar(
                id_b,
                {
                    "tipo": "batalha_sugerida",
                    "batalha_id": str(batalha_id),
                    "oponente": {"id": str(id_a), "nome": jogador_a.nome},
                },
            )

    async def _enviar(self, usuario_id: uuid.UUID, mensagem: dict) -> None:
        jogador = self._conectados.get(usuario_id)
        if jogador is None:
            return
        try:
            await jogador.websocket.send_json(mensagem)
        except Exception:
            await self.desconectar(usuario_id)
