# 0001 — API sem Docker em desenvolvimento local

**Status:** Aceito (Parte 1)

## Contexto

O escopo original não exigia Docker para rodar a aplicação. A equipe
precisava decidir entre containerizar tudo desde o início (API, Postgres,
Redis) ou instalar cada peça diretamente na máquina de desenvolvimento.

## Decisão

Postgres e Redis são instalados e executados diretamente no Windows, sem
Docker. A API roda via `uvicorn` local. Docker é usado **apenas** onde a
containerização resolve um problema que não tem outra solução razoável:
a execução sandboxada de código de aluno (Parte 5 — ver
[ADR 0004](0004-sandbox-docker-para-execucao-de-codigo.md)) e, na Parte 8,
o *build* de uma imagem para deploy (nunca para hospedar a API em
desenvolvimento).

## Consequências

- **Positivo:** ciclo de desenvolvimento mais rápido (sem rebuild de
  imagem, sem overhead de virtualização para cada mudança de código);
  scripts de setup (`scripts/start-redis.ps1`) documentam o processo de
  forma explícita.
- **Negativo:** o ambiente de desenvolvimento não é idêntico ao de
  produção (que deveria containerizar tudo) — mitigado pelo Dockerfile da
  Parte 8, que garante que a aplicação *pode* ser containerizada mesmo
  que não seja assim localmente.
- **Negativo:** onboarding em uma máquina nova exige instalar Postgres e
  Redis manualmente (documentado em `README.md`), em vez de um único
  `docker compose up`.
