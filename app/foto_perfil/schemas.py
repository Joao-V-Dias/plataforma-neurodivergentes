"""Schema de resposta da foto de perfil - upload real feito pelo usuario
(ver app/foto_perfil/model.py para a diferenca em relacao ao avatar de
icone em app/schemas/gamificacao.py)."""

import uuid

from pydantic import BaseModel


class FotoPerfilResponse(BaseModel):
    usuario_id: uuid.UUID
    url: str
