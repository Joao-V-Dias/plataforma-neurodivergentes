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

### 6. Subir a API

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Swagger: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/v1/health

## Testes e lint

```powershell
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check app alembic
```

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

Autenticação/RBAC, modelagem de usuários e perfis de adaptação, gestão
acadêmica, banco de problemas, motor de IA adaptativa, frontend acessível e
observabilidade/CI-CD — ver escopo completo do projeto.
