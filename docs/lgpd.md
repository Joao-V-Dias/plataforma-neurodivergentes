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

Os dados sensíveis (linhas 2 e 3) só passam a ser coletados a partir da
**Parte 3** (`PerfilAluno`, `PerfilBigFive`). Este documento já estabelece a
base para o consentimento que a Parte 3 vai usar.

## 2. Base legal

- **Dados cadastrais e uso da plataforma:** execução de contrato / interesse
  legítimo educacional (Art. 7º).
- **Dados sensíveis (neurodivergência, Big Five):** consentimento **explícito,
  específico e destacado** (Art. 11, I). Não basta um aceite genérico de
  "termos de uso" — o consentimento para dado sensível precisa ser uma etapa
  própria, que descreva claramente a finalidade (calibrar tom/ritmo das
  dicas de IA, Parte 6) e o fato de não substituir avaliação profissional.

O campo `Usuario.consentimento_lgpd_aceito_em` / `consentimento_lgpd_versao`
(`app/models/usuario.py`, Parte 2) já registra o consentimento geral no
cadastro. **A Parte 3 deve implementar um segundo registro de consentimento,
separado e específico**, no momento em que `PerfilAluno`/`PerfilBigFive`
forem preenchidos — não reaproveitar o consentimento de cadastro para isso.

## 3. Menores de idade

Parte do público-alvo (alunos) é composta por crianças e adolescentes. A
LGPD (Art. 14) exige consentimento **específico e destacado dado por pelo
menos um dos pais ou responsável legal** para tratamento de dados de
menores — e, tratando-se adicionalmente de dado sensível de saúde, esse
consentimento do responsável é ainda mais crítico.

Isso significa que o fluxo de auto-cadastro de aluno (`POST /auth/register`,
Parte 2) **não é suficiente por si só** para menores: a Parte 3/4 precisa
definir e implementar um fluxo de verificação/consentimento do responsável
legal antes de qualquer coleta de `PerfilAluno`. Até lá, o cadastro cobre
apenas dados cadastrais comuns.

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

## 7. Controles técnicos já implementados (Parte 2)

- Senhas com hash Argon2id, nunca texto puro (`app/core/security.py`).
- RBAC hierárquico restringindo quem acessa dados de outros usuários
  (`app/api/deps.py`) — a Parte 3 deve garantir que `PerfilAluno`/Big Five
  só sejam visíveis a papéis com necessidade legítima (o próprio aluno,
  professor da turma, coordenador/diretor da instituição).
- Trilha de auditoria de eventos de autenticação (`app/services/audit.py`),
  a ser estendida na Parte 3+ para CRUD de perfis sensíveis.
- Nenhuma senha ou token bruto é logado (ver `app/core/errors.py`, que
  nunca inclui o valor de campos de input nas respostas de erro).

## 8. Pendências explícitas para as próximas partes

- Parte 3: consentimento específico para dado sensível + fluxo de
  consentimento do responsável legal para menores.
- Parte 3/4: regra de visibilidade de `PerfilAluno`/Big Five por papel.
- Parte 8: criptografia em repouso do banco de dados (infraestrutura) e
  processo formal de resposta a incidentes/vazamento (Art. 48).
