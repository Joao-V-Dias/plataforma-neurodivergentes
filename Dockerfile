# Imagem da API (Parte 8) - usada pelo pipeline de CI para validar que a
# aplicacao continua "buildable" e pronta para deploy, mesmo que o
# ambiente de desenvolvimento local rode sem Docker (decisao da Parte 1).
# Nao inclui Postgres/Redis: aponte DATABASE_URL/REDIS_URL para servicos
# externos (gerenciados ou outros containers) ao rodar esta imagem.

# --- Stage 1: build das dependencias -----------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

# Compiladores para dependencias com extensao C (ex: argon2-cffi).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY app ./app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# --- Stage 2: imagem final, enxuta --------------------------------------
FROM python:3.12-slim AS runtime

RUN groupadd --system app && useradd --system --gid app --home /app app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

RUN chown -R app:app /app
USER app

EXPOSE 8000

# Sem CMD de migration automatica de proposito: rodar `alembic upgrade
# head` antes de subir a API e responsabilidade explicita do processo de
# deploy (evita corrida entre multiplas replicas migrando ao mesmo tempo).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
