# battle-service

Servico standalone de WebSocket para partidas (batalhas) online: quando
dois usuarios autenticados da mesma turma estao conectados e livres, o
servico sugere automaticamente uma batalha entre os dois
(docs/prompt-redesign-frontend.md #3.6).

Roda separado da API principal (`app/`) - processo, porta e deploy
proprios. So compartilha o `SECRET_KEY`/`JWT_ALGORITHM` do login para
validar o access token; nao chama a API principal nem acessa o banco.
Estado (fila de disponiveis, convites pendentes) fica em memoria, em um
unico processo - reiniciar o servico limpa tudo.

## Rodando localmente

```bash
cd battle-service
python -m venv .venv
.venv/Scripts/activate   # Windows; em Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edite .env: SECRET_KEY e JWT_ALGORITHM devem ser IGUAIS aos do .env da
# API principal (raiz do projeto) - e o segredo que assina o access token.
# Lido automaticamente por config.py (pydantic-settings) ao subir o processo.

uvicorn main:app --reload --port 8001
```

Health check: `GET http://localhost:8001/health` -> `{"status": "ok"}`.

## Protocolo

Conecte via WebSocket enviando o access token JWT (o mesmo emitido por
`POST /api/v1/auth/login` da API principal), um nome de exibicao e o id da
turma (`GET /api/v1/me/turmas` na API principal) como query params:

```
ws://localhost:8001/ws/batalha?token=<access_token>&nome=<nome_do_usuario>&turma_id=<turma_id>
```

Se o token for invalido/expirado, a conexao e fechada com o codigo `4401`.
O pareamento so acontece entre usuarios com o mesmo `turma_id`.

### Mensagens do servidor para o cliente

Quando ha 2+ usuarios conectados e sem batalha em andamento, ambos recebem:

```json
{
  "tipo": "batalha_sugerida",
  "batalha_id": "uuid",
  "oponente": { "id": "uuid", "nome": "Nome do oponente" }
}
```

Se algum lado recusar, ou desconectar antes de os dois aceitarem, o outro
recebe (e volta para a fila de disponiveis, podendo ser pareado de novo):

```json
{ "tipo": "batalha_cancelada", "motivo": "oponente_recusou" }
```

`motivo` tambem pode ser `"oponente_desconectou"`.

Quando ambos aceitam, os dois recebem:

```json
{ "tipo": "batalha_iniciada", "batalha_id": "uuid", "oponente_id": "uuid" }
```

### Mensagem do cliente para o servidor

Em resposta a um `batalha_sugerida`, o cliente envia:

```json
{ "tipo": "responder_batalha", "batalha_id": "uuid", "aceitar": true }
```

(`aceitar: false` recusa o convite.)

## Fora de escopo (de proposito)

Este servico so faz o pareamento e o convite/aceite da batalha - a logica
do jogo em si (problema sorteado, submissao de codigo, pontuacao) continua
na API principal (`app/`). O front-end deve usar o `batalha_id` recebido
em `batalha_iniciada` para iniciar o fluxo real da partida contra a API
principal.
