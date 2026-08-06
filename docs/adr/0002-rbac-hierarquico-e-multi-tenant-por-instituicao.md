# 0002 — RBAC hierárquico e multi-tenant por instituição

**Status:** Aceito (Parte 2/3)

## Contexto

O escopo exige quatro papéis com uma relação de hierarquia clara
(Diretor > Coordenador > Professor > Aluno) e que múltiplas instituições
usem a mesma plataforma sem enxergar dados umas das outras.

## Decisão

- **RBAC hierárquico, não uma matriz de permissões arbitrária.** Cada
  papel tem uma posição numérica implícita (`app/core/rbac.py`); um
  usuário de papel X pode agir sobre qualquer papel estritamente abaixo
  de X. Isso é suficiente para todas as regras do escopo (criação de
  conta, aprovação, gestão de turma) sem precisar de uma tabela de
  permissões separada — a hierarquia *é* a política.
- **Multi-tenant por `instituicao_id` em toda tabela relevante**, checado
  explicitamente em cada dependency de acesso (`app/api/deps.py`), nunca
  implícito via query global. Um recurso de outra instituição sempre
  resulta em 404 (nunca 403) — o backend não revela que o recurso existe
  fora do escopo do requisitante.

## Consequências

- **Positivo:** adicionar um novo papel (hipoteticamente) significa
  inserir uma posição na lista ordenada, não reescrever uma matriz de
  permissões.
- **Positivo:** o padrão 404-para-recurso-de-outra-instituição é testado
  explicitamente (`app/tests/test_security.py`) e prevê IDOR por
  construção, não por revisão manual de cada endpoint.
- **Negativo:** hierarquia pura não modela exceções pontuais ("este
  Professor específico também pode aprovar alunos", por exemplo) — se o
  produto precisar disso no futuro, vai exigir uma tabela de permissões
  granulares por cima da hierarquia atual, não uma simples extensão dela.
- **Pendência conhecida (Parte 4):** visibilidade de perfil sensível
  ainda é "qualquer Professor+ da instituição", não "só da turma do
  aluno" — documentado em `docs/lgpd.md` como próximo passo.
