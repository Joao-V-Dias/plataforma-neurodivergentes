# LGPD — Tratamento de Dados Pessoais e Sensíveis

> **Este documento é uma base técnica, não um parecer jurídico.** Antes de
> operar com usuários reais — especialmente menores de idade e dados de
> saúde/neurodivergência — é obrigatório revisar este documento com um
> responsável jurídico/DPO, conforme já sinalizado no escopo do projeto.

## 1. Categorias de dados tratados pela plataforma

| Categoria | Exemplos | Sensibilidade (LGPD) |
|---|---|---|
| Dados cadastrais | nome, e-mail, papel de acesso | Pessoal comum (Art. 5º, I) |
| Perfil de neurodivergência | TDAH, TEA, dislexia, discalculia (Parte 3) | **Sensível — dado de saúde** (Art. 5º, II) |
| Perfil psicológico (Big Five/OCEAN) | scores de personalidade (Parte 3) | **Sensível** (Art. 5º, II, por analogia a dado que revela aspecto da vida íntima/psicológica) |
| Preferências de acessibilidade | fonte, contraste, tempo extra (Parte 3) | Pessoal comum, mas correlacionável a condição de saúde |
| Progresso acadêmico | submissões, tentativas, tempo gasto (Parte 4/5) | Pessoal comum |
| Trilha de auditoria | login, IP, ações administrativas (Parte 2) | Pessoal comum, retenção para segurança |

Os dados sensíveis (linhas 2 e 3) passaram a ser coletados na **Parte 3**
(`PerfilAluno`, `PerfilBigFive`), com o consentimento específico descrito
na seção 2.

## 2. Base legal

- **Dados cadastrais e uso da plataforma:** execução de contrato / interesse
  legítimo educacional (Art. 7º).
- **Dados sensíveis (neurodivergência, Big Five):** consentimento **explícito,
  específico e destacado** (Art. 11, I). Não basta um aceite genérico de
  "termos de uso" — o consentimento para dado sensível precisa ser uma etapa
  própria, que descreva claramente a finalidade (calibrar tom/ritmo das
  dicas de IA, Parte 6) e o fato de não substituir avaliação profissional.

O campo `Usuario.consentimento_lgpd_aceito_em` / `consentimento_lgpd_versao`
(`app/models/usuario.py`, Parte 2) registra o consentimento geral no
cadastro. A Parte 3 implementou o segundo registro, separado e específico:
`PerfilAluno.consentimento_em` / `consentimento_versao`
(`app/models/perfil_aluno.py`), exigido a cada nova versão do perfil via
o campo obrigatório `aceite_consentimento` em `POST /alunos/{id}/perfil`
(`app/schemas/perfis.py`) — nunca reaproveitamos o consentimento de
cadastro para isso. O questionário Big Five, por ser um autorrelato que só
o próprio aluno pode preencher (`app/services/big_five_service.py`), não
tem um segundo consentimento explícito separado ainda; isso fica como
pendência (ver seção 8).

## 3. Menores de idade

Parte do público-alvo (alunos) é composta por crianças e adolescentes. A
LGPD (Art. 14) exige consentimento **específico e destacado dado por pelo
menos um dos pais ou responsável legal** para tratamento de dados de
menores — e, tratando-se adicionalmente de dado sensível de saúde, esse
consentimento do responsável é ainda mais crítico.

Isso significa que o fluxo de auto-cadastro de aluno (`POST /auth/register`,
Parte 2) **não é suficiente por si só** para menores. A Parte 3 implementou
o consentimento específico para dado sensível (seção 2), mas **ainda não**
um fluxo de verificação do responsável legal - isso permanece pendente
(seção 8) e precisa ser resolvido antes de operar com alunos menores de
idade reais.

## 4. Retenção e descarte

- **Dados de conta ativa:** mantidos enquanto o vínculo com a instituição
  existir.
- **Dados sensíveis de saúde/perfil psicológico:** revisão de retenção a
  cada 12 meses de inatividade da conta; anonimização (não apenas exclusão
  lógica) recomendada quando o vínculo com a instituição terminar.
- **Trilha de auditoria (`AuditLog`):** retenção sugerida de 12 meses,
  suficiente para investigação de incidentes de segurança sem virar um
  repositório indefinido de dados pessoais.
- **Refresh tokens e tokens de redefinição de senha:** já expiram
  automaticamente (Parte 2) e não são dados de longo prazo.

## 5. Direitos do titular (Art. 18)

A plataforma deve permitir, quando os dados sensíveis existirem (Parte 3+):
confirmação de tratamento, acesso, correção, anonimização/eliminação,
portabilidade e revogação do consentimento. Revogar o consentimento de
dado sensível não deve impedir o uso básico da plataforma (progresso,
turmas) — apenas desativa a calibração adaptativa da IA (Parte 6), que
deve voltar a um modo neutro/genérico nesse caso.

## 6. Minimização e finalidade

O perfil de neurodivergência e o Big Five existem com uma finalidade única:
calibrar tom, ritmo e formato das dicas da IA (Parte 6). Eles **nunca**
devem ser usados para: ranquear alunos, decisões automatizadas que afetem
avaliação/nota, ou qualquer finalidade fora da adaptação de comunicação
pedagógica. A Parte 6 reforça isso como guardrail técnico (a IA nunca emite
diagnóstico clínico).

## 7. Controles técnicos já implementados

- Senhas com hash Argon2id, nunca texto puro (`app/core/security.py`,
  Parte 2).
- RBAC hierárquico restringindo quem acessa dados de outros usuários
  (`app/api/deps.py`, Parte 2).
- Regra de visibilidade de `PerfilAluno`/Big Five por papel (Parte 3,
  `app/api/deps.py:get_aluno_acessivel`): o próprio aluno sempre acessa; um
  Professor/Coordenador/Diretor só acessa se for da **mesma instituição**
  do aluno — isolamento multi-tenant reforçado por `instituicao_id` em
  toda consulta relevante. A visibilidade ainda é por instituição inteira,
  não por turma específica (turmas só existem a partir da Parte 4) — um
  professor que nunca deu aula para aquele aluno mas é da mesma escola
  ainda tem acesso; isso deve ser restringido quando turmas existirem.
- Vocabulário de condições de neurodivergência como tabela, não enum fixo
  (`app/models/condicao_neurodivergencia.py`) — evita "inventar" categorias
  clínicas hardcoded no código; a lista inicial (TDAH, TEA, Dislexia,
  Discalculia, Disgrafia, Transtorno de Processamento Sensorial) é apenas
  um ponto de partida, extensível via INSERT sem migration de schema.
- Perfis sensíveis são **append-only versionado** (`PerfilAluno`,
  `PerfilBigFive`): nenhuma versão anterior é sobrescrita ou apagada,
  preservando o histórico completo para auditoria e para o direito de
  acesso do titular (Art. 18, II).
- Trilha de auditoria (`app/services/audit.py`) estendida na Parte 3 para
  criação/aprovação de usuário e registro de perfil sensível.
- Nenhuma senha ou token bruto é logado (ver `app/core/errors.py`, que
  nunca inclui o valor de campos de input nas respostas de erro).
- Big Five: instrumento público e validado (TIPI, Gosling et al. 2003),
  nunca itens inventados; a IA (Parte 6) não pode usar esse dado para
  emitir diagnóstico clínico.

## 8. Pendências explícitas para as próximas partes

- Fluxo de verificação/consentimento do responsável legal para alunos
  menores de idade (seção 3) — ainda não implementado; o auto-cadastro
  atual (`POST /auth/register`) trata qualquer aluno como capaz de
  consentir sozinho.
- Consentimento específico separado para o questionário Big Five (hoje
  reaproveita implicitamente o consentimento geral de cadastro).
- Parte 4: restringir a visibilidade de `PerfilAluno`/Big Five de
  "qualquer professor da instituição" para "professor da turma do aluno".
- Parte 8: criptografia em repouso do banco de dados (infraestrutura),
  job de retenção/anonimização automática (seção 4) e processo formal de
  resposta a incidentes/vazamento (Art. 48).
