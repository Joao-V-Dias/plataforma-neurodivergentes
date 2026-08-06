# 0004 — Sandbox Docker para execução de código do aluno

**Status:** Aceito (Parte 5)

## Contexto

Alunos submetem código Python arbitrário para ser executado e avaliado
contra casos de teste. Rodar código não confiável no processo da própria
API (`exec()`/`subprocess` direto) é uma porta aberta para RCE,
esgotamento de recursos e acesso à rede/disco do host.

## Decisão

Cada submissão roda em um container Docker efêmero e descartável
(`docker run --rm`), com garantias verificadas manualmente uma a uma
antes da implementação (`app/sandbox/executor.py`):

- `--network none` — sem acesso à rede;
- timeout duplo: `timeout {N}s` (coreutils, dentro do container) **e**
  timeout do lado de fora via `subprocess` do Python — um loop infinito
  nunca trava a API, mesmo que o timeout interno falhe por algum motivo;
- `--memory`/`--memory-swap`/`--cpus`/`--pids-limit` — limites de
  recursos, para um processo malicioso não conseguir derrubar o host;
- `--read-only` + `--tmpfs /tmp` — sem escrita persistente no container;
- `--user nobody` — nunca roda como root dentro do container.

Apenas Python é suportado no momento — decisão deliberada de escopo para
não expandir a superfície de ataque do sandbox nesta fase.

## Consequências

- **Positivo:** cada garantia foi validada com `docker run` direto *antes*
  de escrever o código do executor — o processo de implementação já
  incluiu sua própria verificação de segurança, não uma auditoria
  posterior.
- **Negativo:** exige Docker Desktop rodando localmente para os testes de
  `app/tests/test_problemas.py` e para submissões reais — é a única
  exceção à decisão de "sem Docker" da [ADR 0001](0001-api-sem-docker-em-desenvolvimento-local.md).
- **Negativo:** execução é síncrona (a requisição de submissão só
  retorna depois de rodar todos os casos de teste) — sem fila/worker em
  background. Aceitável no volume atual; se o número de submissões
  simultâneas crescer, isso vira um gargalo que exigiria uma fila
  (Celery/RQ) processando em paralelo.
