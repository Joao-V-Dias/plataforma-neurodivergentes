# Plataforma de Educação Adaptativa em Programação para Pessoas Neurodivergentes

Backend em Python 3.12+ / FastAPI / PostgreSQL / SQLAlchemy 2.0 (async) / Pydantic v2.

> **Nota sobre este setup:** por decisão do time, a Parte 1 está rodando
> **sem Docker** — API, PostgreSQL e Redis instalados e executados
> diretamente na máquina. O código já está pronto para ser containerizado
> mais tarde (Dockerfile/docker-compose podem ser adicionados sem
> retrabalho, já que toda config já vem de variáveis de ambiente).

## Estrutura do projeto

```
app/
  api/          # Routers FastAPI (versionados em api/v1)
  core/         # Config, logging, database, middlewares, error handlers
  models/       # Modelos SQLAlchemy (ORM)
  schemas/      # Schemas Pydantic (request/response)
  services/     # Regras de negócio
  repositories/ # Acesso a dados (queries)
  ai/           # Integração com LLM (Parte 6)
  tests/        # Testes pytest
alembic/        # Migrations de banco de dados
scripts/        # Scripts auxiliares de setup local (Postgres/Redis)
```

## Pré-requisitos

- Python 3.12+ (testado também em 3.14)
- PostgreSQL 16+ instalado localmente
- Redis (ou build compatível) instalado localmente

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
  também acessam (`app/api/deps.py:get_aluno_acessivel`). Escopo por turma
  específica (não a instituição inteira) fica para a Parte 4.

## Testes e lint

```powershell
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check app alembic scripts
```

Os testes escrevem no banco Postgres local de verdade, mas cada teste roda
dentro de uma transação revertida ao final (nada fica persistido). O
rate limiting usa Redis de verdade também; um fixture `autouse` zera o
Redis antes de cada teste para evitar que testes se atrapalhem entre si.

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

Gestão acadêmica (turmas, matrículas), banco de problemas, motor de IA
adaptativa, frontend acessível e observabilidade/CI-CD — ver escopo
completo do projeto.
