"""Regra de hierarquia de papeis: Diretor > Coordenador > Professor > Aluno.
Um papel de nivel mais alto tem acesso a tudo que um papel mais baixo tem
(ex: `require_min_role(PROFESSOR)` libera professor, coordenador e
diretor). Para casos que exigem um papel *exato* (ex: uma acao que so o
proprio diretor pode fazer), use os papeis explicitamente em vez do
nivel minimo."""

from app.models.usuario import Papel

NIVEL_HIERARQUIA: dict[Papel, int] = {
    Papel.ALUNO: 1,
    Papel.PROFESSOR: 2,
    Papel.COORDENADOR: 3,
    Papel.DIRETOR: 4,
}


def papeis_a_partir_de(papel_minimo: Papel) -> tuple[Papel, ...]:
    nivel_minimo = NIVEL_HIERARQUIA[papel_minimo]
    return tuple(papel for papel, nivel in NIVEL_HIERARQUIA.items() if nivel >= nivel_minimo)
