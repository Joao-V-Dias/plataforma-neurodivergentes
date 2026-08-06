# Plataforma de Educação Adaptativa em Programação para Pessoas Neurodivergentes

Backend em Python 3.12+ / FastAPI / PostgreSQL / SQLAlchemy 2.0 (async) / Pydantic v2,
com frontend em React 19 / TypeScript / Vite (`frontend/`, Parte 7).

> **Nota sobre este setup:** por decisão do time, a API, o PostgreSQL e o
> Redis rodam **sem Docker** — instalados e executados diretamente na
> máquina (Parte 1). A **Parte 5 é a exceção**: execução de código de
> aluno precisa de isolamento real (container efêmero, sem rede, com
> limites de CPU/memória/tempo), então o Docker Desktop é usado
> especificamente para rodar cada submissão em um container `--rm`
> descartável — nunca para hospedar a API em si.

## Estrutura do projeto

```
app/
  api/          # Routers FastAPI (versionados em api/v1)
  core/         # Config, logging, database, middlewares, error handlers
  models/       # Modelos SQLAlchemy (ORM)
  schemas/      # Schemas Pydantic (request/response)
  services/     # Regras de negócio
  repositories/ # Acesso a dados (queries)
  sandbox/      # Executor de código sandboxado via Docker (Parte 5)
  ai/           # Motor de IA adaptativa - integração com Groq (Parte 6)
  tests/        # Testes pytest
alembic/        # Migrations de banco de dados
scripts/        # Scripts auxiliares de setup local (Postgres/Redis)
frontend/       # SPA React + TypeScript (Parte 7) - ver secao dedicada abaixo
```

## Pré-requisitos

- Python 3.12+ (testado também em 3.14)
- PostgreSQL 16+ instalado localmente
- Redis (ou build compatível) instalado localmente
- Docker Desktop instalado e **rodando** — usado só pelo sandbox de
  execução de código da Parte 5 (`docker run --rm --network none ...`),
  não para hospedar a API. Sem o daemon do Docker ativo, submissões
  falham com status `erro_interno`.
- (Opcional) Uma chave da API da [Groq](https://console.groq.com/keys) em
  `GROQ_API_KEY` — sem ela o motor de dicas da Parte 6 responde
  `503 Service Unavailable` de forma controlada; o resto da API funciona
  normalmente.

## Setup local (sem Docker)

### 1. Ambiente virtual e dependências

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

### 2. PostgreSQL

Se ainda não tiver o PostgreSQL instalado:

```powershell
winget install --id PostgreSQL.PostgreSQL.17 --source winget
```

Crie o usuário e o banco da aplicação (rode como um usuário com acesso ao
`psql`, usando o superusuário `postgres`):

```sql
CREATE ROLE teacher_app LOGIN PASSWORD 'teacher_app_dev_pw';
CREATE DATABASE teacher_platform OWNER teacher_app;
```

### 3. Redis

Se ainda não tiver o Redis instalado (o Redis oficial não roda nativo no
Windows; usamos um build portátil compatível):

```powershell
winget install --id taizod1024.redis-windows-fork --source winget
```

Para subir o Redis localmente:

```powershell
.\scripts\start-redis.ps1
```

Deixe essa janela aberta enquanto desenvolve.

### 4. Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste os valores (host `localhost` para
Postgres/Redis, já que não estamos usando Docker):

```powershell
copy .env.example .env
```

Gere uma `SECRET_KEY` forte:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 5. Migrations

```powershell
.venv\Scripts\python.exe -m alembic upgrade head
```

### 6. Primeira instituição e primeiro usuário (Diretor)

Não existe endpoint público para criar uma instituição ou um Diretor (de
propósito — são ações administrativas raras e sensíveis). Rode o script
de bootstrap:

```powershell
.venv\Scripts\python.exe scripts\seed_diretor.py `
  --instituicao-nome "Sua Escola" --instituicao-codigo ESCOLA01 `
  --nome "Seu Nome" --email diretor@escola.com --senha "SenhaForte123"
```

O `--instituicao-codigo` é o código que alunos usam para se auto-cadastrar
em `POST /auth/register` (`instituicao_codigo` no corpo da requisição).

### 7. Subir a API

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Swagger: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/v1/health

## Autenticação e autorização (Parte 2)

- JWT com access token curto (15 min) + refresh token (7 dias) com
  **rotação**: cada `/auth/refresh` invalida o token anterior e emite um
  novo par. Reuso de um refresh token já rotacionado é tratado como sinal
  de roubo de token e revoga todas as sessões do usuário.
- Senhas com hash Argon2id (`app/core/security.py`), nunca texto puro.
- RBAC hierárquico: `Diretor > Coordenador > Professor > Aluno`
  (`app/api/deps.py`, `app/core/rbac.py`) — um papel de nível mais alto
  acessa tudo que um mais baixo acessa.
- Rate limiting (Redis) em `/auth/login` (padrão `5/minute`) e
  `/auth/forgot-password` (`3/minute`) contra brute-force.
- Auto-cadastro de aluno (`POST /auth/register`) nasce **inativo**,
  aguardando aprovação (`POST /usuarios/{id}/aprovar`, Parte 3).
- Recuperação de senha: token de uso único, expira em 30 min, resposta
  idêntica para e-mail existente/inexistente (anti-enumeration). Como
  ainda não há serviço de e-mail configurado, o token só volta no corpo
  da resposta fora de produção (`APP_ENV != production`) — em produção
  seria enviado por e-mail e nunca retornado na API.
- Trilha de auditoria de eventos de autenticação em `audit_logs`
  (`app/services/audit.py`).
- Ver `docs/lgpd.md` para a política de dados sensíveis (neurodivergência,
  perfil psicológico).

Rotas: `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`,
`POST /auth/logout`, `POST /auth/forgot-password`,
`POST /auth/reset-password`, `GET /auth/me`.

## Modelagem de dados e gestão de usuários (Parte 3)

- **Multi-tenant por instituição**: toda a hierarquia de RBAC é escopada a
  uma `Instituicao` (`app/models/instituicao.py`). Um Diretor/Coordenador/
  Professor só vê e administra usuários da própria instituição.
- **Criação hierárquica de usuários** (`POST /usuarios`): um papel só cria
  contas de papel **estritamente abaixo** dele na hierarquia — Diretor pode
  criar Coordenador, Professor ou Aluno diretamente (não precisa passar por
  Coordenador); Professor só cria Aluno; Aluno não cria ninguém (só se
  auto-cadastra). Contas criadas por staff já nascem ativas.
- **Aprovação de auto-cadastro** (`POST /usuarios/{id}/aprovar`, Professor+
  da mesma instituição): fecha o fluxo "aluno se autocadastra com
  aprovação" iniciado na Parte 2.
- **Perfil de neurodivergência** (`PerfilAluno`, dado sensível de saúde -
  ver `docs/lgpd.md`): multi-select de condições vindas de um vocabulário
  extensível (`GET /condicoes-neurodivergencia`), versionado de forma
  append-only (nunca sobrescreve, sempre soma uma versão nova) e exige
  consentimento específico separado do consentimento geral de cadastro.
  Rotas: `POST/GET /alunos/{id}/perfil`, `GET /alunos/{id}/perfil/historico`.
- **Perfil Big Five**: questionário TIPI de 10 itens (instrumento público
  validado - Gosling, Rentfrow & Swann, 2003), autorrelato exclusivo do
  aluno. Rotas: `GET /big-five/questionario`, `POST /me/big-five`,
  `GET /alunos/{id}/big-five`.
- **Preferências de acessibilidade** (fonte, contraste, tempo extra,
  leitura em voz alta, redução de estímulos): não é dado clínico, mutável
  in-place, qualquer usuário tem a sua. Rotas:
  `GET/PUT /me/preferencias-acessibilidade`.
- **Regra de visibilidade de dado sensível**: o próprio aluno sempre acessa
  seu perfil/Big Five; Professor/Coordenador/Diretor da mesma instituição
  também acessam (`app/api/deps.py:get_aluno_acessivel`). Ainda é escopo de
  instituição inteira, não da turma específica do aluno (pendência —
  ver `docs/lgpd.md`, seção 8).

## Gestão acadêmica: turmas e matrículas (Parte 4)

- **Turma** (`app/models/turma.py`): nome, período, instituição e um
  professor responsável (titular). Professor+ cria (`POST /turmas`); o
  titular é automaticamente vinculado à turma no momento da criação.
- **Co-docência**: múltiplos professores podem ser vinculados a uma turma
  (`POST /turmas/{id}/professores`), além do titular.
- **Visibilidade de turma**: Professor só vê/gerencia as turmas em que está
  vinculado; Coordenador e Diretor veem/gerenciam todas as turmas da
  própria instituição (`app/api/deps.py:get_turma_acessivel`).
- **Matrícula/desmatrícula** (`POST/DELETE /turmas/{id}/matriculas`):
  histórico preservado (`ativo=false` + `desmatriculado_em`, nunca
  apagado); um aluno pode ser rematriculado depois de desmatriculado.
  Matricular exige que o alvo seja um Aluno da mesma instituição da turma.
- **Progresso agregado por turma** (`GET /turmas/{id}/progresso`): problemas
  resolvidos, tentativas e tempo gasto, calculados a partir de `Submissao`
  (Parte 5) — ver `app/services/progresso_service.py`.
- **Área do aluno**: `GET /me/turmas` (turmas em que está matriculado) e
  `GET /me/turmas/{id}/progresso` (seu próprio progresso, 404 se não
  estiver matriculado) — um aluno nunca vê dados de turmas alheias nem o
  endpoint de gestão (`GET /turmas/{id}`, restrito a Professor+).

## Banco de problemas e execução de código (Parte 5)

- **Sandbox** (`app/sandbox/executor.py`): cada submissão roda num
  container Docker efêmero (`docker run --rm`), verificado manualmente
  antes de implementar:
  - `--network none` — sem acesso à rede (DNS/conexão falham de propósito);
  - `timeout {N}s` (coreutils, dentro do container) **+** timeout externo
    do `subprocess` (fora do container) como rede de segurança — loop
    infinito é interrompido, nunca trava a API;
  - `--memory`/`--memory-swap`/`--cpus`/`--pids-limit` — estouro de
    memória mata o processo (SIGKILL) sem derrubar o host;
  - `--read-only` + `--tmpfs /tmp` — sem escrita persistente;
  - `--user nobody` — nunca roda como root dentro do container.
  - O código do aluno **nunca** é executado com `exec()`/`subprocess`
    direto no processo da API — sempre por fora, via daemon Docker.
  - Só **Python** é suportado por enquanto (`linguagem` é texto livre no
    modelo, mas o executor só sabe rodar Python — decisão de escopo para
    não expandir a superfície de ataque do sandbox nesta parte).
  - Execução é **síncrona**: a requisição de submissão só retorna depois
    de rodar todos os casos de teste (sem fila/worker em background —
    decisão de escopo; ficaria para uma futura Parte de infraestrutura).
- **CRUD de Problema** (`POST/GET /problemas`, `GET /problemas/{id}`):
  enunciado, linguagem, nível de dificuldade, casos de teste **públicos**
  (mostrados ao aluno) e **ocultos** (só usados para corrigir).
- **Tags unificadas** (`GET /tags`, `app/models/problema.py:TagProblema`):
  um único vocabulário com campo `categoria` distingue tags de tema
  (`loops`, `recursao`...) dos metadados de dificuldade adaptativa exigidos
  pelo escopo (`logica_sequencial`, `abstracao`, `memoria_trabalho`...) que
  vão alimentar a IA da Parte 6.
- **Vínculo a turma** (`POST /problemas/{id}/turmas`): um problema só fica
  acessível a um aluno depois de vinculado a uma turma em que ele tem
  matrícula ativa (`app/api/deps.py:get_problema_acessivel`).
- **Descoberta pelo aluno** (`GET /turmas/{id}/problemas`, adicionado na
  Parte 7): lista os problemas vinculados a uma turma - Aluno matriculado
  ou Professor+ com acesso à turma (`app/api/deps.py:get_turma_acessivel_para_membro`).
  Sem este endpoint o aluno não tinha nenhuma forma de descobrir quais
  problemas resolver a partir do frontend.
- **Submissão** (`POST /problemas/{id}/submissoes`): roda o código contra
  cada caso de teste, grava um status geral (`aceito`, `reprovado`,
  `erro_execucao`, `tempo_excedido`, `erro_interno` — o pior status entre
  todos os casos) e o resultado por caso. **Nunca** expõe ao aluno, para um
  caso oculto: entrada, saída esperada, saída obtida ou mensagem de erro —
  só se passou ou não. Para casos públicos, a mensagem de erro é
  sanitizada (`_sanitizar_stderr`): nunca inclui caminhos internos do
  sandbox (`/sandbox/...`) nem a stack trace completa, só o tipo e a
  mensagem da exceção.
- Histórico: `GET /problemas/{id}/minhas-submissoes` (Aluno, só as
  próprias) e `GET /problemas/{id}/submissoes` (Professor+, todas).

## Motor de IA adaptativa (Parte 6)

> **Nota sobre o provedor:** o escopo original previa a API da Anthropic;
> por decisão explícita do time neste projeto, o provedor usado é a
> **[Groq](https://groq.com)** (SDK oficial `groq`, modelo
> `llama-3.3-70b-versatile` por padrão). A arquitetura (isolamento em
> `app/ai`, nunca exposta ao frontend; progressão de nível; guardrails;
> registro de eficácia) é a mesma independente do provedor.

- **Isolamento** (`app/ai/`): nenhum router chama o provedor de IA
  diretamente — só `app/services/dica_service.py` o faz. `app/ai/groq_client.py`
  é a única porta de saída para a rede (SDK `AsyncGroq`); `app/ai/prompts.py`
  é puro (sem I/O) e monta o *system prompt* a partir do nível da dica e do
  perfil do aluno.
- **Dicas progressivas** (`POST /problemas/{id}/dicas`): 4 níveis —
  1) pergunta socrática, 2) pista conceitual, 3) pseudocódigo,
  4) solução comentada. **O aluno nunca escolhe o nível**: o endpoint não
  aceita esse parâmetro, o servidor sempre calcula
  `nível_máximo_já_dado_ao_aluno_neste_problema + 1`. Isso torna o
  guardrail "nunca pular etapa" estrutural (não depende só de instrução
  no prompt) — pedir uma 5ª dica devolve `409 Conflict`.
- **Guardrails no system prompt** (`app/ai/prompts.py:_GUARDRAILS`),
  presentes em **toda** chamada, independente do perfil do aluno: (1) só
  entrega solução completa no nível 4, mesmo se o aluno pedir a resposta
  direta antes disso; (2) a IA nunca emite diagnóstico, avaliação clínica
  ou qualquer afirmação sobre a condição de saúde do aluno — adapta só a
  *comunicação*, nunca substitui avaliação profissional (ver
  `docs/lgpd.md`).
- **Prompt engineering condicionado a perfil**: condições de
  neurodivergência (`PerfilAluno`, Parte 3) e traços Big Five
  (`PerfilBigFive`, Parte 3) mudam o tom/estrutura da dica — ex: TDAH →
  frases curtas em passos numerados + reforço positivo; TEA → linguagem
  literal, sem metáfora, estrutura previsível; Dislexia → texto
  simplificado; Discalculia → reforço lógico/posicional em vez de
  numérico; Neuroticismo alto → tom tranquilizador, sem pressão de tempo;
  Conscienciosidade baixa → dica quebrada em microtarefas. Cada dica
  grava em `adaptacoes_aplicadas` **os códigos** das adaptações usadas
  (nunca a condição do aluno de novo) — um log auditável de *por que* o
  tom mudou, visível só a Professor+ (`GET /problemas/{id}/dicas/{aluno_id}`).
- **Eficácia** (`app/models/dica.py`): quando uma submissão é **aceita**
  para o mesmo problema, `app/services/submissao_service.py` aciona
  `dica_service.registrar_resultado_pos_dica`, que marca toda dica ainda
  sem resultado como `resolvida_apos=true` e calcula
  `tempo_ate_resolver_ms` — o dado usado para calibrar o sistema ao longo
  do tempo. Exposto só a Professor+, nunca ao próprio aluno (não
  queremos pressioná-lo com métrica de desempenho durante o aprendizado).
- Sem `GROQ_API_KEY` configurada, `POST /problemas/{id}/dicas` devolve
  `503 Service Unavailable` de forma controlada (nunca vaza o erro bruto
  do SDK) — verificado manualmente com o servidor rodando.
- Critério de aceite validado em `app/tests/test_dicas.py`: dois alunos
  com perfis diferentes recebendo o mesmo problema recebem dicas com
  conteúdo visivelmente distinto (`test_dois_alunos_perfis_diferentes_recebem_dicas_com_tom_distinto`),
  e o histórico visível a Professor+ demonstra a progressão de nível e a
  adaptação aplicada por aluno. `app/tests/test_ai_prompts.py` testa a
  engenharia de prompt em isolamento (pura, determinística, sem mock).
  Nos testes de integração, o provedor de IA é sempre mockado — chamar a
  API real custaria dinheiro e seria não-determinístico; o que se
  valida ali é a orquestração, não a qualidade do texto de um modelo de
  terceiros.

## Frontend (Parte 7)

SPA em `frontend/`: React 19 + TypeScript + Vite, TanStack Query (estado de
servidor/cache), React Router, React Hook Form + Zod (formulários), Radix
UI (primitivas acessíveis) + Tailwind CSS v4, CodeMirror 6 (editor de
código), Vitest + Testing Library.

> **Nota sobre o escopo:** o texto original da Parte 7 (frontend
> completo, meta de Lighthouse Accessibility Score > 90) não estava mais
> disponível nesta sessão além do fragmento de acessibilidade — a
> implementação seguiu diretamente o backend das Partes 1-6 como fonte de
> verdade para cada tela e regra de acesso.

- **Setup:**
  ```powershell
  cd frontend
  npm install
  copy .env.example .env      # ajuste VITE_API_BASE_URL se necessário
  npm run dev                 # http://localhost:5173
  ```
  O backend precisa estar rodando em paralelo (`.venv\Scripts\python.exe -m uvicorn app.main:app --reload`) - `CORS_ORIGINS` no `.env` do backend já inclui `http://localhost:5173`.
- **Cliente de API tipado** (`src/lib/api/`): tipos TypeScript espelhando
  1:1 os schemas Pydantic do backend, um axios `apiClient` com interceptor
  de refresh token (rotação automática, deduplicando chamadas concorrentes
  de `/auth/refresh`), e um módulo por recurso (auth/usuarios/perfis/turmas/problemas/dicas).
- **Autenticação e RBAC** (`src/lib/auth/`): `AuthProvider` guarda a
  sessão; `ProtectedRoute` bloqueia rotas por autenticação e por papel
  mínimo (`papelMinimo`, espelhando `app/api/deps.py:require_min_role`);
  `RoleGate` esconde elementos de UI por papel — sempre como reforço de
  UX, nunca como a autorização real (essa é sempre revalidada pelo
  backend).
- **Acessibilidade aplicada globalmente** (`src/lib/accessibility/`): lê
  `PreferenciasAcessibilidade` (Parte 3) do usuário logado e aplica
  classes no `<html>` — alto contraste, tamanho de fonte, fonte legível
  (mais espaçamento entre letras/linhas, ajuda leitura com dislexia),
  redução de estímulos (desliga toda animação/transição) e um botão
  "ouvir" (Web Speech API) em enunciados de problema e no conteúdo das
  dicas quando "leitura em voz alta" está ativada. Testado manualmente no
  Chrome: alternar alto contraste + fonte grande re-tema a aplicação
  inteira instantaneamente (otimista, antes da confirmação da API).
- **Telas:** login/cadastro (auto-registro de aluno, conta nasce
  inativa)/recuperação de senha; dashboard por papel; usuários
  (hierarquia RBAC de criação + aprovação de aluno pendente); perfil
  (identificação de neurodivergência + questionário Big Five/TIPI, com
  linguagem cuidadosa de LGPD — nunca fala em diagnóstico); turmas
  (gestão para Professor+, progresso pessoal para Aluno); banco de
  problemas (CRUD com casos de teste públicos/ocultos para Professor+;
  editor de código CodeMirror + submissão + resultado por caso para
  Aluno — nunca expõe detalhe de caso oculto, o backend já filtra isso);
  dicas progressivas (Parte 6) embutidas na tela do problema — o nível
  não é escolhido pelo cliente, só "pedir a próxima dica".
- **Endpoint novo no backend** (`GET /turmas/{id}/problemas`): ao montar
  a tela do aluno percebemos que não havia nenhuma forma de descobrir
  quais problemas foram atribuídos à turma dele — só existia
  `GET /problemas`, restrito a Professor+. Endpoint aditivo, sem alterar
  nenhum contrato existente; coberto por testes em `app/tests/test_problemas.py`
  (aluno matriculado lista, aluno de fora recebe 403).
- **Testes** (`npm run test`, Vitest + Testing Library): fluxo de login
  (validação, sucesso, erro do backend), `ProtectedRoute`/`RoleGate`
  (redirecionamento por autenticação e por papel), extração de mensagem
  de erro do envelope único da API, regras hierárquicas de RBAC
  (`papeisCriaveisPor`/`papelAtendeMinimo`).
- **Build de produção:** `npm run build` (`tsc -b && vite build`) —
  code-splitting por rota via `React.lazy`, então o chunk inicial (tela de
  login) não carrega CodeMirror nem as telas de gestão.

## Testes e lint

```powershell
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check app alembic scripts
```

Frontend (dentro de `frontend/`):

```powershell
npm run lint    # eslint, incluindo jsx-a11y
npm run test    # vitest
npm run build   # tsc --noEmit + vite build
```

Os testes escrevem no banco Postgres local de verdade, mas cada teste roda
dentro de uma transação revertida ao final (nada fica persistido). O
rate limiting usa Redis de verdade também; um fixture `autouse` zera o
Redis antes de cada teste para evitar que testes se atrapalhem entre si.
Os testes de `app/tests/test_problemas.py` executam containers Docker de
verdade (Parte 5) — mais lentos que o resto da suíte (~20s), mas é o único
jeito honesto de validar isolamento/timeout real. Exigem o Docker Desktop
rodando. Os testes de `app/tests/test_dicas.py` (Parte 6) mockam o
provedor de IA (nunca chamam a Groq de verdade); `app/tests/test_ai_prompts.py`
testa a montagem de prompt sem nenhum mock, banco ou rede.

## Logging

Logs estruturados em JSON (uma linha por evento), com `request_id` de
correlação propagado automaticamente em todo log emitido durante o
processamento de uma requisição. O header `X-Request-ID` é devolvido em
toda resposta.

## Padrão de erro

Toda resposta de erro da API segue o mesmo formato:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Um ou mais campos são inválidos.",
    "fields": { "campo": ["mensagem de erro"] }
  },
  "request_id": "..."
}
```

## Próximas partes

Observabilidade, testes de segurança, CI/CD e documentação (Parte 8) —
ver escopo completo do projeto.
