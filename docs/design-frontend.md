# Prompt — Redesign do Frontend da Plataforma de Educação Adaptativa em Programação

Use este prompt para orientar a IA/dev que vai reescrever o frontend. Ele reúne: (1) o contrato de rotas do backend, que define o que cada tela precisa buscar/enviar, (2) a proposta pedagógica (TEACCH + Abordagem Centrada na Pessoa de Carl Rogers + Estilos de Aprendizagem de Felder-Silverman + Metodologias Ativas/Gamificação), que define o _porquê_ de cada tela existir, e (3) diretrizes visuais rígidas contra estética genérica de IA.

---

## 1. Contexto do produto

Plataforma de ensino de programação voltada a **estudantes neurodivergentes** (foco inicial: autismo e TDAH). A hipótese central do projeto (doutorado UFU) é que a combinação de três referenciais resolve problemas concretos de aprendizagem nesse público:

- **TEACCH (Ensino Estruturado):** previsibilidade, estrutura visual, clareza de tarefas, redução de sobrecarga cognitiva, poucas opções por tela para evitar paralisia por escolha.
- **Abordagem Centrada na Pessoa (Carl Rogers):** o aluno é "cliente", não "paciente"; autodireção, liberdade responsável, olhar positivo incondicional, autoavaliação de progresso, ausência de julgamento visível na interface (nada de "errou!", "falhou!" em tom punitivo).
- **Felder-Silverman (estilos de aprendizagem):** o mesmo conteúdo deve poder ser consumido em formatos diferentes (ativo/reflexivo, sensorial/intuitivo, visual/verbal, sequencial/global), e o sistema aprende o estilo do aluno observando interação, não perguntando.
- **Metodologias Ativas / Gamificação (moderada, não infantilizada):** pontuação, sequência de dias ("ofensiva" tipo Duolingo), emblemas, ranking, avatar, "Mapa do Jogo" como navegação da disciplina, batalhas assíncronas entre colegas.
  **Cada decisão de UI feita a seguir deve remeter a pelo menos um desses quatro pilares** — evite adicionar elementos de gamificação ou estrutura "porque fica bonito"; justifique pelo pilar.

O sistema tem 4 papéis hierárquicos: `aluno < professor < coordenador < diretor`. A UI deve ter duas grandes áreas: **Área do Aluno** (jogo/estudo) e **Área de Gestão** (professor/coordenador/diretor — dashboards administrativos, sóbrios, sem elementos de jogo).

---

## 2. Rotas do backend e telas correspondentes

Base URL: `http://127.0.0.1:8000/api/v1`. Auth via Bearer token (`POST /auth/login`). Erros seguem `{ error: { code, message, fields }, request_id }`.

### 2.1 Autenticação e onboarding

| Rota                                                                       | Tela                                                                                                                                                                                                         |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `POST /auth/register`                                                      | Cadastro do aluno (conta nasce inativa — mostrar estado "aguardando aprovação")                                                                                                                              |
| `POST /auth/login`                                                         | Login (rate limit 5/min — tratar erro 429 com mensagem clara)                                                                                                                                                |
| `POST /auth/forgot-password`, `POST /auth/reset-password`                  | Fluxo de recuperação de senha                                                                                                                                                                                |
| `GET /auth/me`                                                             | Contexto global do usuário logado (nome, papel, is_active)                                                                                                                                                   |
| `GET /condicoes-neurodivergencia`                                          | Combo de condições no onboarding do perfil                                                                                                                                                                   |
| `GET /big-five/questionario` + `POST /me/big-five`                         | Questionário TIPI (10 itens) — tela de onboarding, tom neutro, sem gamificar essa etapa (é dado sensível)                                                                                                    |
| `GET/PUT /me/preferencias-acessibilidade`                                  | Painel de acessibilidade (fonte legível, alto contraste, tempo extra, leitura em voz alta, redução de estímulos, tamanho de fonte) — deve estar acessível a 1 clique do header, sempre, em toda a plataforma |
| `POST /alunos/{id}/perfil` + `GET .../perfil` + `GET .../perfil/historico` | Perfil de neurodivergência (append-only, versionado) — tela de consentimento específica (LGPD, dado de saúde), depois tela de histórico em linha do tempo                                                    |

### 2.2 Gestão (Professor+)

| Rota                                                                      | Tela                                                                                                                              |
| ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `GET/POST /usuarios`, `GET /usuarios/{id}`, `POST /usuarios/{id}/aprovar` | Painel de gestão de usuários — fila de aprovação de auto-cadastro é uma tela própria, não escondida em detalhe                    |
| `POST/GET /turmas`, `GET /turmas/{id}`                                    | Lista e criação de turmas                                                                                                         |
| `POST /turmas/{id}/professores`                                           | Co-docência                                                                                                                       |
| `POST/GET /turmas/{id}/matriculas`, `DELETE .../matriculas/{aluno_id}`    | Gestão de matrícula (desmatricular preserva histórico — refletir isso no texto da UI, ex. "Remover da turma" em vez de "Excluir") |
| `GET /turmas/{id}/progresso`                                              | Dashboard de progresso agregado da turma — tabela densa e escaneável, não cards decorativos                                       |
| `POST /problemas`, `GET /problemas`, `GET /problemas/{id}`                | CRUD de banco de problemas com editor de casos de teste públicos/ocultos                                                          |
| `POST /problemas/{id}/turmas`                                             | Vincular problema a turma                                                                                                         |
| `GET /problemas/{id}/submissoes`, `GET /submissoes/{id}`                  | Auditoria de submissões                                                                                                           |
| `GET /problemas/{id}/dicas/{aluno_id}`                                    | Painel pedagógico: histórico de dicas + adaptações aplicadas + eficácia (tempo até resolver) — **nunca exposto ao aluno**         |

### 2.3 Área do aluno (jogo)

| Rota                                                  | Tela                                                                                                                                                                                                                        |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /me/turmas`                                      | Seleção de disciplina/turma — ponto de entrada, deve ser a home do aluno                                                                                                                                                    |
| `GET /me/turmas/{id}/progresso`                       | Progresso pessoal dentro da turma                                                                                                                                                                                           |
| `GET /turmas/{id}/problemas`                          | **"Mapa do Jogo"** — cada problema é uma fase; renderizar como trilha/sequência linear, não como grid solto (pilar TEACCH: sequencial e sem excesso de opções)                                                              |
| `GET /tags`                                           | Filtro por tema/raciocínio na listagem, quando aplicável                                                                                                                                                                    |
| `GET /problemas/{id}`                                 | Tela do problema: enunciado + casos públicos + editor de código                                                                                                                                                             |
| `POST /problemas/{id}/submissoes`                     | Submissão (síncrona — a tela precisa de um estado de loading real enquanto o sandbox roda, com timeout tratado)                                                                                                             |
| `GET /problemas/{id}/minhas-submissoes`               | Histórico pessoal de tentativas                                                                                                                                                                                             |
| `POST /problemas/{id}/dicas` + `GET .../minhas-dicas` | Painel de dicas progressivas (níveis 1–4: pergunta socrática → pista conceitual → pseudocódigo → solução comentada). Tratar `409` (nível máximo) e `503` (IA indisponível) como estados de UI reais, não como erro genérico |

### 2.4 Estados de erro obrigatórios em todas as telas

`400/422` (validação com `fields`), `401/403` (sessão/permissão), `404` (nunca revelar se o recurso existe em outra instituição — mensagem genérica de "não encontrado"), `409` (conflito — ex. já matriculado, nível máximo de dica), `429` (rate limit no login/forgot-password), `503` (IA de dicas fora do ar — a submissão de código continua funcionando mesmo sem dicas).

---

## 3. Funcionalidades da proposta a implementar no frontend

Implementar como parte da experiência do aluno, cada uma amarrada à rota correspondente acima:

1. **Avatar e apelido** (dado local de perfil, não há rota explícita — pode ser modelado como extensão de `preferencias-acessibilidade` ou novo campo de perfil a combinar com o backend). Avatar evolui com pontuação. Função: reduzir ansiedade social e dar camada de privacidade a quem tem dificuldade de socialização.
2. **Mapa do Jogo**: navegação principal da disciplina, uma fase = um problema, avanço predominantemente linear (mas não bloqueado — Rogers pede autodireção), com poucos elementos por vez.
3. **Conteúdo adaptado ao estilo de aprendizagem**: a tela de estudo antes do problema deve poder alternar formato (texto/passo-a-passo/mapa mental/vídeo-áudio) sem forçar escolha explícita — o sistema infere pelo uso.
4. **Pontuação, sequência de dias, ranking (turma / semestre / geral) e emblemas** — usar a rota de progresso como fonte de dado; se o backend ainda não expõe ranking, sinalizar isso claramente no prompt para o time de backend, não simular dado falso na UI final.
5. **Agenda / diário de bordo**: organizador de tarefas com prazos vindos dos problemas vinculados à turma, checklist diário, e um diário de bordo pessoal com opção de compartilhar ou não com o professor.
6. **Batalha**: desafio 1x1 opcional entre alunos online na mesma turma — apenas quando o backend expuser a rota correspondente; até lá, tratar como funcionalidade "em breve" e não simular.
   Onde uma funcionalidade do slide não tiver rota de backend correspondente na tabela acima, **não fabricar dado fake na interface final** — construir o componente já preparado para receber dados reais e marcar com um TODO explícito, ou perguntar ao time de backend antes de ligar a tela.

---

## 4. Diretrizes visuais (regra rígida — leia antes de desenhar qualquer tela)

Ao desenvolver este frontend, evite completamente o estilo visual genérico e facilmente reconhecível como "feito por IA". O design deve parecer criado por um designer e desenvolvedor experiente, com decisões visuais intencionais e coerentes com o propósito do projeto.

**Evite:**

- Gradientes exagerados ou usados apenas como decoração.
- Interfaces excessivamente arredondadas, com `border-radius` em praticamente todos os elementos.
- Cards em excesso para organizar qualquer tipo de informação.
- Sombras fortes ou genéricas em todos os componentes.
- Uso exagerado de glassmorphism, transparências e efeitos de desfoque.
- Paletas de cores muito saturadas ou combinações "tech" previsíveis.
- Roxo/azul neon como escolha padrão.
- Botões enormes ou excessivamente arredondados.
- Ícones decorativos sem função.
- Emojis como elementos principais da interface.
- Textos genéricos como "Bem-vindo à sua jornada", "Transforme sua experiência" ou similares.
- Layouts que parecem seguir templates prontos de dashboards gerados por IA.
- Seções repetitivas com o mesmo padrão de card + ícone + título + descrição.
- Animações excessivas ou efeitos que não contribuem para a experiência.
- Tipografia escolhida apenas porque é popular em interfaces modernas.
- Espaçamentos e componentes excessivamente uniformes a ponto de deixar a interface sem personalidade.
  **Priorize:**
- Hierarquia visual clara.
- Layouts simples, funcionais e bem estruturados.
- Tipografia legível e com personalidade.
- Espaçamento consistente, mas não artificialmente rígido.
- Cores escolhidas de acordo com o contexto e a identidade do projeto.
- Elementos visuais com propósito.
- Contraste adequado e boa acessibilidade.
- Interfaces que pareçam reais e utilizáveis, não apenas bonitas em uma captura de tela.
- Consistência entre páginas e componentes.
- Estados de loading, vazio, erro e sucesso bem pensados.
- Responsividade real para diferentes tamanhos de tela.
- Microinterações discretas e justificadas.
- Componentes que tenham uma função clara em vez de existirem apenas para preencher espaço.
  **Direção estética:**
  Antes de criar cada página, pense primeiro em qual problema aquela interface precisa resolver para o usuário. O visual deve surgir dessa necessidade, e não de tendências de design. Prefira uma estética sóbria, humana, funcional e específica para o projeto, em vez de tentar fazer o site parecer "futurista", "premium", "revolucionário" ou "high-tech". O resultado final deve dar a impressão de que uma equipe de produto realmente projetou e refinou a interface ao longo do tempo, e não de que uma IA recebeu o comando "crie um site moderno". Não copie padrões visuais de outros sites ou templates. Crie uma identidade própria baseada no contexto, público-alvo e finalidade da aplicação.

**Regra principal:** se uma decisão visual parecer uma escolha que uma IA faria automaticamente ao receber o pedido "crie um site moderno", questione essa decisão e procure uma alternativa mais específica, funcional e intencional.

**Reforço específico deste projeto (acessibilidade neurodivergente):** contraste alto por padrão, sem elementos piscando/autoplay de animação, sem excesso de estímulo visual simultâneo, tipografia com boa legibilidade (evitar fontes condensadas ou muito decorativas), e a Área do Aluno deve ser visualmente mais "quieta" do que um jogo comercial — a gamificação é funcional (TEACCH + engajamento), não estética.

---

## 5. Estrutura de páginas sugerida

**Público / Auth:** Login · Cadastro · Esqueci minha senha · Redefinir senha

**Onboarding (pós-cadastro, aluno):** Consentimento LGPD do perfil de neurodivergência → Seleção de condições → Questionário Big Five (TIPI) → Preferências de acessibilidade → Avatar e apelido

**Área do Aluno:** Minhas turmas (home) → Mapa do Jogo da turma → Tela do problema (enunciado + editor + submissão) → Minhas submissões → Dicas do problema → Meu progresso na turma → Agenda/diário de bordo → Painel de acessibilidade (global, sempre acessível)

**Área de Gestão (Professor/Coordenador/Diretor):** Dashboard de turmas → Detalhe de turma (matrículas, professores, progresso agregado) → Fila de aprovação de usuários → Gestão de usuários → Banco de problemas (lista + criação/edição com casos de teste) → Auditoria de submissões → Painel pedagógico de dicas por aluno (histórico + eficácia)

---

## 6. Entregável esperado

Reescrever o frontend seguindo a estrutura acima, ligado às rotas reais do backend (sem mock de dados exceto onde explicitamente marcado como "sem rota ainda"), com os quatro pilares pedagógicos guiando as decisões de interação, e seguindo estritamente as diretrizes visuais da seção 4.
