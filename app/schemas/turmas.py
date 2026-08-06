"""Schemas de gestao academica: turmas, co-docencia, matriculas e
progresso agregado."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CriarTurmaRequest(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    periodo: str = Field(..., min_length=1, max_length=50)
    professor_responsavel_id: uuid.UUID


class TurmaResponse(BaseModel):
    id: uuid.UUID
    instituicao_id: uuid.UUID
    nome: str
    periodo: str
    professor_responsavel_id: uuid.UUID
    ativo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TurmaDetalheResponse(TurmaResponse):
    total_professores: int
    total_alunos_ativos: int


class AdicionarProfessorRequest(BaseModel):
    professor_id: uuid.UUID


class MatricularRequest(BaseModel):
    aluno_id: uuid.UUID


class MatriculaResponse(BaseModel):
    id: uuid.UUID
    turma_id: uuid.UUID
    aluno_id: uuid.UUID
    aluno_nome: str
    aluno_email: str
    ativo: bool
    matriculado_em: datetime
    desmatriculado_em: datetime | None


class ProgressoAlunoResponse(BaseModel):
    aluno_id: uuid.UUID
    aluno_nome: str
    problemas_resolvidos: int
    tentativas: int
    tempo_gasto_minutos: int
