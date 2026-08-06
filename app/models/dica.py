"""Dicas progressivas geradas pelo motor de IA adaptativa (Parte 6).

Cada linha e uma dica de UM nivel (1-4) entregue a um aluno para um
problema especifico - nunca atualizamos uma dica existente, cada nivel
pedido gera uma nova linha, preservando o historico completo de
progressao exigido pelo criterio de aceite ("logs demonstram progressao
de nivel de dica").

`adaptacoes_aplicadas` guarda apenas *codigos* das adaptacoes de tom/
estrutura usadas ao montar o prompt (ex: "tdah_passos_curtos",
"neuroticismo_alto_tom_tranquilizador") - nunca a condicao clinica do
aluno em si nem qualquer linguagem de diagnostico (ver docs/lgpd.md e
app/ai/prompts.py). E um log de *auditoria da adaptacao*, nao um
prontuario.

`resolvida_apos` e `tempo_ate_resolver_ms` sao preenchidos depois, quando
o aluno envia uma submissao aceita para o mesmo problema (ver
app/services/dica_service.registrar_resultado_pos_dica, chamado a partir
de app/services/submissao_service) - e o dado de eficacia usado para
calibrar o sistema ao longo do tempo."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDPrimaryKeyMixin


class Dica(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "dicas"

    problema_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("problemas.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    aluno_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # 1 = pergunta socratica, 2 = pista conceitual, 3 = pseudocodigo,
    # 4 = solucao comentada (ver app/ai/prompts.py).
    nivel: Mapped[int] = mapped_column(Integer, nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    adaptacoes_aplicadas: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    # Eficacia (Parte 6, criterio de aceite): preenchido quando uma
    # submissao aceita chega para o mesmo aluno+problema apos esta dica.
    resolvida_apos: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tempo_ate_resolver_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Dica(problema_id={self.problema_id!r}, aluno_id={self.aluno_id!r}, "
            f"nivel={self.nivel!r})"
        )
