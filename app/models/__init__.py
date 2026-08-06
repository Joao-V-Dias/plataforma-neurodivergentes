from app.models.audit_log import AuditLog
from app.models.base import Base
from app.models.condicao_neurodivergencia import CondicaoNeurodivergencia
from app.models.instituicao import Instituicao
from app.models.matricula import Matricula
from app.models.password_reset_token import PasswordResetToken
from app.models.perfil_aluno import PerfilAluno, perfil_aluno_condicoes
from app.models.perfil_big_five import PerfilBigFive
from app.models.preferencias_acessibilidade import PreferenciasAcessibilidade
from app.models.refresh_token import RefreshToken
from app.models.turma import Turma, turma_professores
from app.models.usuario import Papel, Usuario

__all__ = [
    "AuditLog",
    "Base",
    "CondicaoNeurodivergencia",
    "Instituicao",
    "Matricula",
    "Papel",
    "PasswordResetToken",
    "PerfilAluno",
    "PerfilBigFive",
    "PreferenciasAcessibilidade",
    "RefreshToken",
    "Turma",
    "Usuario",
    "perfil_aluno_condicoes",
    "turma_professores",
]
