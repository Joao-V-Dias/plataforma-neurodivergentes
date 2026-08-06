"""Schemas do banco de problemas e submissoes."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.problema import CategoriaTag, NivelDificuldade
from app.models.submissao import StatusSubmissao


class TagPublica(BaseModel):
    id: uuid.UUID
    categoria: CategoriaTag
    codigo: str
    nome: str
    descricao: str | None

    model_config = {"from_attributes": True}


class CasoTesteInputSchema(BaseModel):
    entrada: str = Field(default="", max_length=10_000)
    saida_esperada: str = Field(..., max_length=10_000)
    publico: bool = False


class CriarProblemaRequest(BaseModel):
    titulo: str = Field(..., min_length=2, max_length=200)
    enunciado: str = Field(..., min_length=1, max_length=20_000)
    linguagem: str = Field(..., min_length=1, max_length=30)
    nivel_dificuldade: NivelDificuldade
    tags_codigos: list[str] = Field(default_factory=list)
    casos: list[CasoTesteInputSchema] = Field(..., min_length=1)


class CasoTesteResponse(BaseModel):
    id: uuid.UUID
    entrada: str
    saida_esperada: str
    publico: bool
    ordem: int


class ProblemaResponse(BaseModel):
    id: uuid.UUID
    instituicao_id: uuid.UUID
    titulo: str
    enunciado: str
    linguagem: str
    nivel_dificuldade: NivelDificuldade
    criado_por_id: uuid.UUID
    ativo: bool
    created_at: datetime
    tags: list[TagPublica]

    model_config = {"from_attributes": True}


class ProblemaDetalheResponse(ProblemaResponse):
    # Para Aluno, so os casos publicos vem preenchidos aqui (ver
    # app/api/v1/problemas.py); para Professor+, todos os casos.
    casos: list[CasoTesteResponse]


class VincularTurmaRequest(BaseModel):
    turma_id: uuid.UUID


class SubmeterCodigoRequest(BaseModel):
    codigo_fonte: str = Field(..., min_length=1, max_length=50_000)


class ResultadoCasoResponse(BaseModel):
    caso_teste_id: uuid.UUID
    publico: bool
    passou: bool
    tempo_execucao_ms: int
    # Preenchidos apenas quando o caso e publico - nunca expomos entrada,
    # saida esperada, saida obtida ou erro de um caso oculto (senao o
    # aluno "descobre" o caso oculto via feedback de erro).
    entrada: str | None = None
    saida_esperada: str | None = None
    saida_obtida: str | None = None
    erro: str | None = None


class SubmissaoResponse(BaseModel):
    id: uuid.UUID
    problema_id: uuid.UUID
    aluno_id: uuid.UUID
    status: StatusSubmissao
    tempo_execucao_ms: int
    criado_em: datetime
    resultados: list[ResultadoCasoResponse]


class SubmissaoResumoResponse(BaseModel):
    id: uuid.UUID
    aluno_id: uuid.UUID
    status: StatusSubmissao
    tempo_execucao_ms: int
    criado_em: datetime
