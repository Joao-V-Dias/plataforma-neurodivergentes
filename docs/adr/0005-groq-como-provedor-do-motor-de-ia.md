# 0005 — Groq como provedor do motor de IA (desvio do escopo original)

**Status:** Aceito (Parte 6)

## Contexto

O escopo original da Parte 6 especificava a API da Anthropic como
provedor do motor de dicas progressivas. Por decisão explícita do time
durante a implementação, o provedor usado foi trocado para a
**[Groq](https://groq.com)**.

## Decisão

`app/ai/groq_client.py` isola toda a integração com o SDK oficial `groq`
(modelo padrão `llama-3.3-70b-versatile`, configurável via
`GROQ_MODELO`). Nenhum outro módulo da aplicação — nem os routers, nem o
frontend — sabe que existe um provedor de IA por trás das dicas; só
`app/services/dica_service.py` importa `app.ai`.

A arquitetura em volta do provedor não mudou com a troca: progressão de
nível calculada pelo servidor, guardrails no system prompt
(`app/ai/prompts.py`), registro de eficácia da dica
(`app/models/dica.py`). Trocar de provedor de novo no futuro exigiria
mudanças isoladas em `app/ai/`, sem tocar em `dica_service.py`,
`dica_repository.py` ou nos routers.

## Consequências

- **Positivo:** o isolamento em `app/ai/` (decisão já tomada na Parte 1,
  antes de qualquer código de IA existir) absorveu a troca de provedor
  sem propagar mudanças para o resto do sistema — a camada fez exatamente
  o que era pra fazer.
- **Negativo:** documentação e comentários que mencionavam "Anthropic"
  precisaram ser corrigidos para "Groq" nas Partes 6 e 7 — nenhum código,
  só texto.
- **Neutro:** sem `GROQ_API_KEY` configurada, o motor de dicas responde
  `503 Service Unavailable` de forma controlada (nunca vaza o erro bruto
  do SDK) — o resto da aplicação funciona normalmente. Essa decisão
  (degradar graciosamente em vez de falhar a inicialização) é
  independente do provedor escolhido.
