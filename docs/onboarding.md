# Guia de onboarding para novos devs

Bem-vindo(a). Este guia assume que você já leu o `README.md` (setup passo
a passo) e quer entender como o projeto é organizado e como contribuir
sem quebrar as convenções já estabelecidas.

## 1. Antes de tudo: rode o projeto

Siga o `README.md` da raiz até conseguir:

1. A API respondendo em `http://127.0.0.1:8000/api/v1/health`
2. `pytest` passando (backend)
3. O frontend em `http://localhost:5173` conversando com a API

Se algo travar no setup, é bug de documentação — abra uma issue/avise o
time em vez de gastar horas adivinhando.

## 2. Como o projeto foi construído

O projeto inteiro foi implementado em partes sequenciais, cada uma
entregue de ponta a ponta (modelo → migration → repositório → serviço →
schema → router → testes → validação manual → documentação → commit)
antes de começar a próxima. Isso significa que o histórico de commits
**é** uma cronologia legível da arquitetura:

| Parte | Tema | O que olhar primeiro |
|---|---|---|
| 1 | Setup base | `app/core/config.py`, `app/core/database.py` |
| 2 | Autenticação/RBAC | `app/core/security.py`, `app/api/deps.py`, `app/core/rbac.py` |
| 3 | Perfis sensíveis | `app/models/perfil_aluno.py`, `docs/lgpd.md` |
| 4 | Turmas/matrículas | `app/services/turma_service.py`, `app/services/matricula_service.py` |
| 5 | Sandbox de código | `app/sandbox/executor.py`, `docs/adr/0004-*.md` |
| 6 | Motor de IA | `app/ai/`, `app/services/dica_service.py`, `docs/adr/0005-*.md` |
| 7 | Frontend | `frontend/src/`, `docs/adr/0006-*.md` |
| 8 | Observabilidade/CI | `.github/workflows/ci.yml`, `app/core/monitoring.py` |

Leia os [ADRs em `docs/adr/`](adr/README.md) antes de mudar algo que
parece estranho à primeira vista — é provável que exista uma razão
documentada.

## 3. Convenções que valem para o repositório inteiro

- **Português em nomes de domínio, inglês em termos técnicos genéricos.**
  `criar_usuario`, `PerfilAluno`, `matricula_repository` — mas `client`,
  `Request`, `async def`. Siga o que já existe no arquivo que você está
  editando.
- **Camadas não pulam etapas.** Router → Service → Repository → Model.
  Um router nunca importa um repositório diretamente; um serviço nunca
  monta uma resposta HTTP. Se você se pegar fazendo isso, é sinal de que
  a lógica está na camada errada.
- **Exceções de domínio, não `HTTPException` direto no serviço.**
  `app/services/exceptions.py` define os erros de negócio; o router é
  quem sabe traduzir `RecursoNaoEncontradoError` para 404. Serviços não
  conhecem HTTP.
- **Todo dado sensível de saúde é versionado append-only** (ver
  [ADR 0003](adr/0003-dados-sensiveis-versionados-append-only.md)) —
  nunca faça `UPDATE` em `PerfilAluno`/`PerfilBigFive`.
- **Multi-tenant sempre explícito.** Toda query que retorna um recurso
  específico por ID deve confirmar `instituicao_id` antes de devolver
  algo — nunca confie que o ID sozinho é suficiente.
- **Sem comentários explicando o óbvio.** Comentários existem para
  registrar *por que*, não *o que* — se remover o comentário não deixaria
  ninguém confuso, ele não deveria existir.

## 4. Rodando os testes

```powershell
.venv\Scripts\python.exe -m pytest                          # suite completa
.venv\Scripts\python.exe -m pytest --cov --cov-report=html   # com cobertura (abre htmlcov/index.html)
.venv\Scripts\python.exe -m pytest app/tests/test_security.py -q  # um arquivo
```

Os testes escrevem no Postgres local de verdade (transação revertida ao
final de cada teste — nada fica persistido). `app/tests/test_problemas.py`
precisa do Docker Desktop rodando (sandbox real). `app/tests/test_dicas.py`
mocka o provedor de IA por padrão.

Frontend: `cd frontend && npm run test`.

## 5. Onde encontrar as coisas

- **"Como uma requisição é autenticada?"** → `app/api/deps.py:get_current_user`
- **"Quem pode fazer o quê?"** → `app/core/rbac.py` + os `require_*` em `app/api/deps.py`
- **"Como um erro vira resposta HTTP?"** → `app/core/errors.py`
- **"Como a IA decide o tom da dica?"** → `app/ai/prompts.py`
- **"Como o frontend sabe que preferência de acessibilidade aplicar?"** → `frontend/src/lib/accessibility/AccessibilityContext.tsx`
- **"Como criar os primeiros usuários?"** → `docs/manuais/` (um manual por papel) + a seção "Hierarquia de criação de usuários" do `README.md`

## 6. Antes de abrir um PR

1. `ruff check app alembic scripts` e `mypy app` sem erros
2. `pytest` verde, cobertura não caiu abaixo de 80%
3. Se mexeu no frontend: `npm run lint`, `npm run test`, `npm run build`
4. Se a mudança for uma decisão de arquitetura não-trivial, considere
   escrever um ADR (`docs/adr/`, copie o formato dos existentes)
5. O CI (`.github/workflows/ci.yml`) roda tudo isso automaticamente em
   todo push/PR — mas rodar local primeiro é mais rápido que esperar o
   CI te avisar.
