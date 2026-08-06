"""Excecoes de regra de negocio da camada de servico. Cada uma e mapeada
para um status HTTP especifico nos routers (app/api/v1/*.py)."""


class EmailJaCadastradoError(Exception):
    pass


class CredenciaisInvalidasError(Exception):
    pass


class ContaInativaError(Exception):
    pass


class ConsentimentoNaoAceitoError(Exception):
    pass


class HierarquiaInvalidaError(Exception):
    """Papel criador nao tem permissao para criar contas do papel alvo."""


class RecursoNaoEncontradoError(Exception):
    pass


class InstituicaoDiferenteError(Exception):
    """Acao envolvendo dois usuarios de instituicoes diferentes (multi-tenant)."""


class AlvoInvalidoError(Exception):
    """Acao aplicada a um usuario de papel incompativel (ex: perfil de
    aluno registrado para um usuario que nao e Aluno)."""


class CondicaoInvalidaError(Exception):
    """Codigo de condicao de neurodivergencia nao existe/nao esta ativo."""
