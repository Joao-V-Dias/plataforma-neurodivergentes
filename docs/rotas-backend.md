# Documentação de Rotas do Backend

API da **Plataforma de Educação Adaptativa em Programação para Pessoas Neurodivergentes**.

- **Base URL:** `http://127.0.0.1:8000`
- **Prefixo da API:** `/api/v1`
- **Versão:** 1.0.0
- **Swagger/OpenAPI interativo:** `GET /docs` · `GET /redoc` · Schema bruto em `/openapi.json`
- **Health check:** `GET /api/v1/health`

> Documentação gerada a partir do schema OpenAPI e dos routers (`app/api/v1/*.py`).

---

## Autenticação e RBAC

Todas as rotas protegidas exigem o header:

```
Authorization: Bearer <access_token>
```

O token é obtido via `POST /api/v1/auth/login`. Papéis (hierarquia **Diretor > Coordenador > Professor > Aluno**):

| Papel | Valor |
|-------|-------|
| Aluno | `aluno` |
| Professor | `professor` |
| Coordenador | `coordenador` |
| Diretor | `diretor` |

Convenções de permissão:

- `require_min_role(X)` → libera o papel **X** e todos os **acima** dele na hierarquia.
- `require_roles(ALUNO)` → libera **apenas** o papel `aluno`.
- Nenhuma resposta transborda dados de outra instituição (multi-tenant); recursos de outra instituição retornam `404`, nunca revelam existência.

Padrão de erro comum a todas as rotas:

```json
{
  "error": { "code": "...", "message": "...", "fields": { "campo": ["mensagem"] } },
  "request_id": "..."
}
```

---

## Índice de Rotas

| Método | Caminho | Função | Acesso |
|--------|---------|--------|--------|
| GET | `/api/v1/health` | Verifica se a API e o banco estão operacionais | Público |
| POST | `/api/v1/auth/register` | Auto-cadastro do aluno (conta nasce inativa) | Público |
| POST | `/api/v1/auth/login` | Autentica e emite tokens de acesso/refresh | Público |
| POST | `/api/v1/auth/refresh` | Renova o par de tokens (rotação de sessão) | Público |
| POST | `/api/v1/auth/logout` | Encerra a sessão e revoga o refresh token | Público |
| POST | `/api/v1/auth/forgot-password` | Gera token de redefinição de senha | Público |
| POST | `/api/v1/auth/reset-password` | Redefine a senha com o token de uso único | Público |
| GET | `/api/v1/auth/me` | Retorna os dados do usuário autenticado | Autenticado |
| GET | `/api/v1/usuarios` | Lista os usuários da instituição do requisitante | Professor+ |
| POST | `/api/v1/usuarios` | Cria conta de papel estritamente abaixo do criador | Professor+ |
| GET | `/api/v1/usuarios/{usuario_id}` | Obtém os dados de um usuário da instituição | Professor+ |
| POST | `/api/v1/usuarios/{usuario_id}/aprovar` | Ativa um aluno auto-cadastrado (aprovação) | Professor+ |
| GET | `/api/v1/condicoes-neurodivergencia` | Lista o vocabulário de condições de neurodivergência | Autenticado |
| GET | `/api/v1/big-five/questionario` | Retorna o questionário TIPI de 10 itens | Autenticado |
| POST | `/api/v1/me/big-five` | Registra as respostas do Big Five do próprio usuário | Autenticado |
| GET | `/api/v1/me/preferencias-acessibilidade` | Obtém as preferências de acessibilidade do usuário | Autenticado |
| PUT | `/api/v1/me/preferencias-acessibilidade` | Atualiza as preferências de acessibilidade do usuário | Autenticado |
| POST | `/api/v1/alunos/{aluno_id}/perfil` | Registra (versiona) o perfil de neurodivergência do aluno | Próprio aluno ou Professor+ |
| GET | `/api/v1/alunos/{aluno_id}/perfil` | Obtém o perfil de neurodivergência vigente do aluno | Próprio aluno ou Professor+ |
| GET | `/api/v1/alunos/{aluno_id}/perfil/historico` | Obtém todo o histórico versionado do perfil do aluno | Próprio aluno ou Professor+ |
| GET | `/api/v1/alunos/{aluno_id}/big-five` | Obtém o Big Five vigente do aluno | Próprio aluno ou Professor+ |
| GET | `/api/v1/me/turmas` | Lista as turmas em que o usuário está matriculado | Autenticado |
| GET | `/api/v1/me/turmas/{turma_id}/progresso` | Progresso do próprio aluno dentro de uma turma | Autenticado (matriculado) |
| POST | `/api/v1/turmas` | Cria turma vinculando o professor responsável | Professor+ |
| GET | `/api/v1/turmas` | Lista turmas visíveis (Professor: as dele; Coord./Dir.: todas) | Professor+ |
| GET | `/api/v1/turmas/{turma_id}` | Detalhe da turma com total de professores e alunos | Professor+ c/ acesso |
| POST | `/api/v1/turmas/{turma_id}/professores` | Vincula um professor à turma (co-docência) | Professor+ c/ acesso |
| POST | `/api/v1/turmas/{turma_id}/matriculas` | Matricula um aluno na turma | Professor+ c/ acesso |
| GET | `/api/v1/turmas/{turma_id}/matriculas` | Lista as matrículas da turma | Professor+ c/ acesso |
| DELETE | `/api/v1/turmas/{turma_id}/matriculas/{aluno_id}` | Desmatricula um aluno (histórico preservado) | Professor+ c/ acesso |
| GET | `/api/v1/turmas/{turma_id}/progresso` | Progresso agregado dos alunos da turma | Professor+ c/ acesso |
| GET | `/api/v1/tags` | Lista as tags de problemas (tema/raciocínio) | Autenticado |
| POST | `/api/v1/problemas` | Cria problema com casos de teste públicos/ocultos | Professor+ |
| GET | `/api/v1/problemas` | Lista os problemas da instituição | Professor+ |
| GET | `/api/v1/problemas/{problema_id}` | Detalhe do problema (Aluno vê só casos públicos) | Acesso ao problema |
| POST | `/api/v1/problemas/{problema_id}/turmas` | Vincula um problema a uma turma | Professor+ c/ acesso |
| POST | `/api/v1/problemas/{problema_id}/submissoes` | Executa o código do aluno no sandbox e corrige os casos | Aluno |
| GET | `/api/v1/problemas/{problema_id}/minhas-submissoes` | Histórico de submisssões do próprio usuário | Autenticado |
| GET | `/api/v1/problemas/{problema_id}/submissoes` | Lista todas as submisssões de um problema | Professor+ |
| GET | `/api/v1/submissoes/{submissao_id}` | Detalhe de uma submissão específica | Autenticado c/ acesso |
| GET | `/api/v1/turmas/{turma_id}/problemas` | Lista os problemas vinculados a uma turma | Membro (aluno matriculado/Professor+) |
| POST | `/api/v1/problemas/{problema_id}/dicas` | Gera a próxima dica progressiva (nível calculado pelo servidor) | Aluno c/ acesso |
| GET | `/api/v1/problemas/{problema_id}/minhas-dicas` | Histórico de dicas do próprio aluno no problema | Aluno c/ acesso |
| GET | `/api/v1/problemas/{problema_id}/dicas/{aluno_id}` | Histórico e eficácia das dicas de um aluno (Professor+) | Professor+ |

Legenda de acesso:

- **Público** — sem token.
- **Autenticado** — qualquer usuário logado (`get_current_user`).
- **Professor+** — professor, coordenador ou diretor (`require_min_role(PROFESSOR)`).
- **Próprio aluno ou Professor+** — o próprio aluno-alvo ou staff da mesma instituição (`get_aluno_acessivel`).
- **Professor+ c/ acesso** — staff com acesso à turma: Professor só em turmas em que está vinculado; Coordenador/Diretor em todas da instituição (`get_turma_acessivel`).
- **Membro** — Professor c/ vínculo, Coordenador/Diretor, **ou** Aluno com matrícula ativa (`get_turma_acessivel_para_membro`).
- **Acesso ao problema** — Professor+ da instituição ou Aluno com acesso (problema vinculado à turma em que está ativo) (`get_problema_acessivel`).

---

## Health

### `GET /api/v1/health` — Público
Verifica se a API e o banco estão operacionais.

```json
{ "status": "ok", "database": "ok" }
```

---

## Autenticação (`/auth`)

### `POST /api/v1/auth/register` — Público
Auto-cadastro de **aluno**. A conta nasce **inativa**, aguardando aprovação de Professor+ (`POST /api/v1/usuarios/{usuario_id}/aprovar`).

**Body:**
```json
{
  "nome": "Aluno Fulano",
  "email": "aluno@escola.com",
  "senha": "SenhaForte123",
  "instituicao_codigo": "ESCOLA01",
  "aceite_lgpd": true
}
```
- `senha`: mínimo 8 caracteres, com pelo menos uma letra e um número.
- `aceite_lgpd`: obrigatório `true`.

**Respostas:** `201` → `UsuarioPublico` · `400` (consentimento) · `404` (instituição não encontrada) · `409` (e-mail já cadastrado) · `422`

---

### `POST /api/v1/auth/login` — Público
Autentica e retorna os tokens. **Rate limit:** `5/minute` por IP.

**Body:** `{ "email": "...", "senha": "..." }`

**Respostas:**
- `200` → `TokenResponse`
  ```json
  {
    "access_token": "...",
    "access_token_expires_at": "2026-09-05T22:59:21Z",
    "refresh_token": "...",
    "refresh_token_expires_at": "2026-09-12T22:59:21Z",
    "token_type": "bearer"
  }
  ```
- `401` (credenciais inválidas) · `403` (conta inativa) · `429` (rate limit) · `422`

---

### `POST /api/v1/auth/refresh` — Público
Rotaciona o par de tokens (invalida o anterior e emite novo). Reuso de token já rotacionado revoga todas as sessões.

**Body:** `{ "refresh_token": "..." }`
**Respostas:** `200` → `TokenResponse` · `401` · `403` · `422`

---

### `POST /api/v1/auth/logout` — Público
Revoga a sessão (refresh token).

**Body:** `{ "refresh_token": "..." }`
**Respostas:** `204` (sem corpo) · `422`

---

### `POST /api/v1/auth/forgot-password` — Público
Solicita redefinição de senha. Resposta idêntica para e-mail existente/inexistente (anti-enumeration). **Rate limit:** `3/minute` por IP.

**Body:** `{ "email": "..." }`

**Respostas:** `200`
```json
{ "message": "Se este e-mail estiver cadastrado, um link de redefinicao de senha foi enviado.", "reset_token": "..." }
```
- `reset_token` só é preenchido fora do ambiente `production` (substituto temporário de envio de e-mail).

---

### `POST /api/v1/auth/reset-password` — Público
Redefine a senha com o token de uso único (expira em 30 min).

**Body:** `{ "token": "...", "nova_senha": "..." }`
**Respostas:** `204` · `400` (token inválido) · `422`

---

### `GET /api/v1/auth/me` — Autenticado
Retorna os dados do usuário logado.

**Respostas:** `200` → `UsuarioPublico`
```json
{ "id": "uuid", "nome": "...", "email": "...", "papel": "aluno", "is_active": true }
```

---

## Gestão de Usuários (`/usuarios`)

Regra de criação hierárquica: um papel só cria contas de papel **estritamente abaixo** do seu. Professor+.

### `GET /api/v1/usuarios` — Professor+
**Função:** listar todos os usuários da escola do requisitante. É a base da tela de gestão de usuários do frontend. O escopo é sempre a instituição do chamador (isolamento multi-tenant): ninguém enxerga usuários de outra escola.

### `POST /api/v1/usuarios` — Professor+
**Função:** criar a conta de um novo usuário (coordenador, professor ou aluno) sem precisar de auto-cadastro. Só pode criar papéis **estritamente abaixo** do criador na hierarquia (ex.: Diretor cria Coordenador/Professor/Aluno; Professor só cria Aluno). Contas criadas por staff nascem **ativas** (podem logar imediatamente), ao contrário do auto-cadastro.

**Body:**
```json
{ "nome": "...", "email": "...", "senha": "...", "papel": "coordenador" }
```
`papel` ∈ `aluno | professor | coordenador | diretor`.

**Respostas:** `201` → `UsuarioPublico` · `403` (hierarquia inválida) · `409` (e-mail duplicado) · `422`

### `GET /api/v1/usuarios/{usuario_id}` — Professor+
**Função:** consultar os dados de um usuário específico da própria instituição. Usado para exibir detalhes de um usuário no frontend. Retorna `404` se o registro não existir ou for de outra instituição.

### `POST /api/v1/usuarios/{usuario_id}/aprovar` — Professor+
**Função:** ativar um aluno que se auto-cadastrou (`POST /auth/register`). Fecha o fluxo "aluno se autocadastra → professor aprova". A conta só passa a funcionar (login) depois desta aprovação.

**Respostas:** `200` → `UsuarioPublico` · `403` · `404`

---

## Perfis e Acessibilidade (`/perfis`)

Regra de visibilidade de dado sensível (LGPD): o próprio aluno sempre acessa seu perfil; Professor/Coordenador/Diretor da mesma instituição também acessam.

### `GET /api/v1/condicoes-neurodivergencia` — Autenticado
**Função:** listar o vocabulário (extensível) de condições de neurodivergência que podem ser selecionadas ao montar um perfil de aluno.

### `GET /api/v1/big-five/questionario` — Autenticado
**Função:** fornecer as 10 questões do instrumento TIPI para o aluno responder (o frontend monta o formulário a partir desta rota).

### `POST /api/v1/me/big-five` — Autenticado
**Função:** salvar as respostas do próprio usuário ao questionário Big Five. A partir dele o motor de IA calcula os traços de personalidade (abertura, conscienciosidade, extroversão, amabilidade, neuroticismo) usados para adaptar o tom das dicas.

**Body:** `{ "respostas": [1, 5, 2, 4, 3, ...] }` (10 itens)

**Respostas:** `201` → `PerfilBigFiveResponse` (com `scores` de abertura, conscienciosidade, extroversão, amabilidade, neuroticismo) · `400` · `422`

### `GET /api/v1/me/preferencias-acessibilidade` — Autenticado
**Função:** ler as preferências de acessibilidade do usuário logado (fonte, contraste, tempo extra, leitura em voz alta, redução de estímulos) para o frontend aplicar o tema/ajustes de acessibilidade.

**Respostas:** `200` → `PreferenciasAcessibilidadeResponse`

### `PUT /api/v1/me/preferencias-acessibilidade` — Autenticado
**Função:** atualizar as preferências de acessibilidade do próprio usuário (mutável in-place, sem versionamento). Persiste os ajustes que o frontend aplica globalmente.

**Body:**
```json
{
  "fonte_legivel": false,
  "alto_contraste": false,
  "tempo_extra_percentual": 0,
  "leitura_voz_alta": false,
  "reducao_estimulos": false,
  "tamanho_fonte": 100
}
```
**Respostas:** `200` → `PreferenciasAcessibilidadeResponse` · `422`

### `POST /api/v1/alunos/{aluno_id}/perfil` — Próprio aluno ou Professor+
**Função:** registrar (**append-only** — nunca sobrescreve, soma uma nova versão) o perfil de neurodivergência do aluno, exigindo consentimento específico (separado do consentimento geral de cadastro). Dado sensível de saúde (LGPD).

**Body:**
```json
{
  "condicoes_codigos": ["tdah", "tea"],
  "observacoes": "opcional",
  "aceite_consentimento": true
}
```
**Respostas:** `201` → `PerfilAlunoResponse` · `400` · `404` · `422`

### `GET /api/v1/alunos/{aluno_id}/perfil` — Próprio aluno ou Professor+
**Função:** consultar o perfil de neurodivergência **vigente** do aluno (dado usado pelo motor de IA para adaptar as dicas). `404` se ainda não registrado.

### `GET /api/v1/alunos/{aluno_id}/perfil/historico` — Próprio aluno ou Professor+
**Função:** obter todas as versões já registradas do perfil do aluno (trilha de evolução, append-only).

### `GET /api/v1/alunos/{aluno_id}/big-five` — Próprio aluno ou Professor+
**Função:** consultar o Big Five **vigente** do aluno (traços de personalidade que complementam o perfil para a IA). `404` se ainda não respondeu.

---

## Turmas e Matrículas (`/turmas`)

### `POST /api/v1/turmas` — Professor+
**Função:** criar uma turma (nome + período) e marcar o professor responsável (titular), que é vinculado automaticamente a ela.

**Body:**
```json
{ "nome": "Turma 1A", "periodo": "2026.1", "professor_responsavel_id": "uuid" }
```
**Respostas:** `201` → `TurmaResponse` · `400` · `403` · `404` · `422`

### `GET /api/v1/turmas` — Professor+
**Função:** listar turmas. Um Professor vê **somente** as turmas em que está vinculado; Coordenador/Diretor vêem **todas** as turmas da instituição.

### `GET /api/v1/turmas/{turma_id}` — Professor+ c/ acesso
**Função:** exibir o detalhe de uma turma, incluindo contagem de professores (`total_professores`) e de alunos ativos (`total_alunos_ativos`).

### `POST /api/v1/turmas/{turma_id}/professores` — Professor+ c/ acesso
**Função:** adicionar outro professor à turma (co-docência), além do titular. Professor só pode adicionar em turmas em que está vinculado.

**Body:** `{ "professor_id": "uuid" }`
**Respostas:** `204` · `400` · `403` · `404`

### `POST /api/v1/turmas/{turma_id}/matriculas` — Professor+ c/ acesso
**Função:** matricular um aluno (da mesma instituição) na turma. É o vínculo que dá ao aluno acesso às turmas e aos problemas dela.

**Body:** `{ "aluno_id": "uuid" }`
**Respostas:** `201` → `MatriculaResponse` · `400` · `403` · `404` · `409` (já matriculado)

### `GET /api/v1/turmas/{turma_id}/matriculas` — Professor+ c/ acesso
**Função:** listar as matrículas de uma turma (alunos ativos e histórico).

### `DELETE /api/v1/turmas/{turma_id}/matriculas/{aluno_id}` — Professor+ c/ acesso
**Função:** desmatricular um aluno. O registro não é apagado: vira `ativo=false` (histórico preservado) e o aluno pode ser rematriculado depois.

**Respostas:** `204` · `404`

### `GET /api/v1/turmas/{turma_id}/progresso` — Professor+ c/ acesso
**Função:** visão agregada do professor sobre o desempenho da turma — para cada aluno, mostra problemas resolvidos, número de tentativas e tempo gasto (calculados a partir das submisssões).

**Respostas:** `200` → `list[ProgressoAlunoResponse]`

### `GET /api/v1/me/turmas` — Autenticado
**Função:** listar para o usuário logado as turmas em que ele tem matrícula **ativa** (útil para o Aluno ver sua área e escolher uma turma).

### `GET /api/v1/me/turmas/{turma_id}/progresso` — Autenticado (matriculado)
**Função:** mostrar ao **próprio aluno** seu progresso dentro de uma turma específica (problemas resolvidos, tentativas, tempo). `404` se não estiver matriculado — o aluno nunca vê dados de turmas alheias.

---

## Banco de Problemas (`/problemas`)

### `GET /api/v1/tags` — Autenticado
**Função:** listar as tags do banco de problemas (vocabulário único). Tags de `categoria=tema` (ex.: `loops`, `recursao`) e `categoria=raciocinio` (ex.: `logica_sequencial`, `abstracao`, `memoria_trabalho`). Parâmetro opcional de query: `?categoria=tema|raciocinio`.

### `POST /api/v1/problemas` — Professor+
**Função:** criar um problema de programação no banco, com enunciado e casos de teste **públicos** (visíveis ao aluno) e **ocultos** (usados só para corrigir, nunca exibidos).

**Body:**
```json
{
  "titulo": "Soma simples",
  "enunciado": "Leia dois inteiros a e b e imprima a soma.",
  "linguagem": "python",
  "nivel_dificuldade": "facil",
  "tags_codigos": ["loops"],
  "casos": [
    { "entrada": "2 3", "saida_esperada": "5", "publico": true },
    { "entrada": "10 20", "saida_esperada": "30", "publico": false }
  ]
}
```
- `linguagem`: por enquanto apenas **python** é suportada (executor).
- `nivel_dificuldade` ∈ `facil | medio | dificil`.
- **Respostas:** `201` → `ProblemaResponse` · `400` (linguagem não suportada) · `422`

### `GET /api/v1/problemas` — Professor+
**Função:** listar todos os problemas criados pela instituição (gestão do banco de problemas).

### `GET /api/v1/problemas/{problema_id}` — Acesso ao problema
**Função:** exibir o enunciado e os casos de teste de um problema. Para **Aluno**, somente os casos **públicos** são retornados; os ocultos nunca vazam entrada/saída esperada.

### `POST /api/v1/problemas/{problema_id}/turmas` — Professor+ c/ acesso
**Função:** vincular o problema a uma turma. É o passo que torna o problema disponível aos alunos — sem esse vínculo, nenhum aluno consegue acessá-lo. Professor só vincula a turmas em que está vinculado.

**Body:** `{ "turma_id": "uuid" }`
**Respostas:** `204` · `403` · `404`

### `POST /api/v1/problemas/{problema_id}/submissoes` — Aluno (com acesso)
**Função:** enviar o código-fonte do aluno para ser **executado** e corrigido contra todos os casos de teste. Executa em sandbox Docker isolado (`--network none`, limite de CPU/memória/tempo). É **síncrono** — a resposta só volta após rodar todos os casos.

**Body:** `{ "codigo_fonte": "print(sum(map(int, input().split())))" }`

**Respostas:** `201` → `SubmissaoResponse` com `status` e `resultados` por caso (ocultos expõem apenas `passou`).

Valores de `status`: `aceito | reprovado | erro_execucao | tempo_excedido | erro_interno`.

> Sem o daemon Docker ativo, submissões falham com `status: erro_interno`.

### `GET /api/v1/problemas/{problema_id}/minhas-submissoes` — Autenticado
**Função:** mostrar ao usuário seu próprio histórico de submissões naquele problema (vitórias e tentativas), para acompanhar o progresso pessoal.

### `GET /api/v1/problemas/{problema_id}/submissoes` — Professor+
**Função:** listar todas as submisssões de um problema, de todos os alunos (visão de acompanhamento do professor).

### `GET /api/v1/submissoes/{submissao_id}` — Autenticado c/ acesso
**Função:** exibir o detalhe completo de uma submissão específica. Acesso restrito ao próprio aluno autor ou ao staff da instituição (casos ocultos mostram apenas `passou`).

### `GET /api/v1/turmas/{turma_id}/problemas` — Membro
**Função:** listar os problemas vinculados a uma turma. Permite ao **Aluno matriculado** descobrir quais problemas resolver (Professor+ também acessa). `403` para aluno não matriculado.

---

## Dicas Progressivas IA (`/dicas`, Parte 6)

Requere `GROQ_API_KEY` configurada no backend; sem ela, rotas de solicitação retornam `503`.

### `POST /api/v1/problemas/{problema_id}/dicas` — Aluno (com acesso)
**Função:** gerar a **próxima** dica para o aluno resolver o problema, adaptada ao perfil dele (neurodivergência + Big Five). O nível é sempre calculado pelo servidor (`nível já dado + 1`), nunca escolhido pelo cliente — impede pular etapas.

**Respostas:**
- `201` → `DicaResponse` (níveis 1–4: pergunta socrática, pista conceitual, pseudocódigo, solução comentada)
- `409` (nível máximo atingido — 4 dicas) · `503` (IA indisponível)

### `GET /api/v1/problemas/{problema_id}/minhas-dicas` — Aluno (com acesso)
**Função:** exibir ao aluno o histórico das dicas que já recebeu naquele problema (para releitura/consulta durante o estudo).

### `GET /api/v1/problemas/{problema_id}/dicas/{aluno_id}` — Professor+
**Função:** revisar o histórico de dicas de um aluno, incluindo as **adaptações aplicadas** (por que o tom mudou) e o dado de **eficácia** (tempo até resolver após a dica). Acompanhamento pedagógico do professor; nunca exposto ao próprio aluno.
