"""Excecoes de regra de negocio da camada de servico. Cada uma e mapeada
para um status HTTP especifico no router (app/api/v1/auth.py)."""


class EmailJaCadastradoError(Exception):
    pass


class CredenciaisInvalidasError(Exception):
    pass


class ContaInativaError(Exception):
    pass


class ConsentimentoNaoAceitoError(Exception):
    pass
