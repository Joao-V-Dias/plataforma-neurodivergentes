from app.models.audit_log import AuditLog
from app.models.avatar import PerfilJogo
from app.models.base import Base
from app.models.condicao_neurodivergencia import CondicaoNeurodivergencia
from app.models.dica import Dica
from app.models.emblema import Emblema, aluno_emblemas
from app.models.instituicao import Instituicao
from app.models.matricula import Matricula
from app.models.password_reset_token import PasswordResetToken
from app.models.perfil_aluno import PerfilAluno, perfil_aluno_condicoes
from app.models.perfil_big_five import PerfilBigFive
from app.models.pontuacao import Pontuacao
from app.models.preferencias_acessibilidade import PreferenciasAcessibilidade
from app.models.problema import CasoTeste, Problema, TagProblema, problema_tags, problema_turmas
from app.models.refresh_token import RefreshToken
from app.models.submissao import Submissao, SubmissaoResultado
from app.models.turma import Turma, turma_professores
from app.models.usuario import Papel, Usuario

__all__ = [
    "AuditLog",
    "Base",
    "CasoTeste",
    "CondicaoNeurodivergencia",
    "Dica",
    "Emblema",
    "Instituicao",
    "Matricula",
    "Papel",
    "PasswordResetToken",
    "PerfilAluno",
    "PerfilBigFive",
    "PerfilJogo",
    "Pontuacao",
    "PreferenciasAcessibilidade",
    "Problema",
    "RefreshToken",
    "Submissao",
    "SubmissaoResultado",
    "TagProblema",
    "Turma",
    "Usuario",
    "aluno_emblemas",
    "perfil_aluno_condicoes",
    "problema_tags",
    "problema_turmas",
    "turma_professores",
]
