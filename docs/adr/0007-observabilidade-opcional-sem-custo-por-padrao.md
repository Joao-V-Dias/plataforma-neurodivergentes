# 0007 — Observabilidade opcional, sem custo por padrão

**Status:** Aceito (Parte 8)

## Contexto

O escopo pede métricas (Prometheus/Grafana) e alertas de erro (Sentry).
Ambos são serviços de terceiros (Sentry é pago/requer conta; Grafana
requer infraestrutura própria para hospedar) que a aplicação não deveria
exigir só para subir em desenvolvimento.

## Decisão

- **Métricas Prometheus:** `prometheus-fastapi-instrumentator` expõe
  `GET /metrics` automaticamente (latência, contagem e status code por
  rota) — habilitado por padrão (`METRICS_ENABLED=true`), sem custo nem
  dependência externa: qualquer Prometheus/Grafana existente pode
  simplesmente apontar para o endpoint.
- **Sentry:** só inicializa com um `SENTRY_DSN` real configurado
  (`app/core/monitoring.py:configurar_sentry`) — mesmo padrão já
  estabelecido para o Groq na Parte 6 ([ADR 0005](0005-groq-como-provedor-do-motor-de-ia.md)):
  a ausência de uma chave de terceiro nunca impede a aplicação de subir,
  só desliga aquela integração especificamente. `send_default_pii=False`
  por padrão, para nunca vazar corpo de request/response (que pode
  conter dado sensível de saúde) para o Sentry.

## Consequências

- **Positivo:** o pipeline de CI (`.github/workflows/ci.yml`) roda sem
  precisar de nenhuma credencial de observabilidade — `SENTRY_DSN` fica
  vazia no ambiente de CI de proposito.
- **Positivo:** ativar monitoramento completo em produção é uma mudança
  de configuração (duas variáveis de ambiente), não uma mudança de
  código.
- **Negativo:** sem Grafana provisionado neste repositório — a decisão
  foi expor a métrica e documentar como conectar, não hospedar um
  dashboard (fora do escopo de "sem Docker para hospedar a API",
  [ADR 0001](0001-api-sem-docker-em-desenvolvimento-local.md)).
- **Negativo:** `GET /metrics` não exige autenticação (padrão do
  `prometheus-fastapi-instrumentator`) — em produção, o acesso deveria
  ser restrito por rede (firewall/VPC), não pela aplicação.
