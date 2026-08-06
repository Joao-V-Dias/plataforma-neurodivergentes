# 0003 — Dados sensíveis versionados append-only

**Status:** Aceito (Parte 3)

## Contexto

`PerfilAluno` (condições de neurodivergência) e `PerfilBigFive` são dado
sensível de saúde (LGPD Art. 5, II). O escopo pede rastreabilidade e
direito de acesso do titular ao histórico completo, não só ao estado
atual.

## Decisão

Nenhuma linha de `PerfilAluno`/`PerfilBigFive` é atualizada (`UPDATE`)
depois de criada. Uma nova versão do perfil é sempre um `INSERT` com
`versao = max(versao existente) + 1`; a versão "vigente" é simplesmente a
de maior `versao` para aquele aluno — sem flag mutável (`ativo`,
`atual`), o que elimina a possibilidade de o histórico ser reescrito por
engano ou má-fé.

## Consequências

- **Positivo:** auditoria trivial — a tabela inteira é o histórico, sem
  precisar de uma tabela de auditoria paralela para este dado específico.
- **Positivo:** atende diretamente o direito de acesso do titular
  (LGPD Art. 18, II) — `GET /alunos/{id}/perfil/historico` devolve tudo.
- **Negativo:** a tabela cresce indefinidamente (uma linha por
  atualização, para sempre) — aceitável no volume esperado da aplicação,
  mas exigiria uma política de retenção/arquivamento em escala muito
  maior.
- **Negativo:** consultas precisam sempre filtrar pela versão mais
  recente (`ORDER BY versao DESC LIMIT 1`) em vez de um simples `WHERE
  ativo = true` — decisão deliberada para não correr o risco de uma flag
  mutável ficar dessincronizada.
