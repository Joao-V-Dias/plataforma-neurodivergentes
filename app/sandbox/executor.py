"""Executor de codigo sandboxado via Docker.

Cada execucao roda em um container efemero (`docker run --rm`), sem
acesso a rede (`--network none`), com limites de CPU/memoria/numero de
processos e timeout (tanto interno via `timeout` do coreutils quanto
externo via subprocess). O codigo do aluno NUNCA e executado com
exec()/subprocess direto no processo da API - sempre por fora, via
daemon Docker.

Garantias verificadas manualmente antes de escrever este modulo:
- rede bloqueada (--network none): DNS/conexao falham dentro do container;
- timeout aplicado (`timeout {N}s` + timeout externo do subprocess): loop
  infinito e interrompido, retorna exit code 124;
- limite de memoria aplicado (--memory): estouro de memoria mata o
  processo com SIGKILL (exit code 137), nao derruba o host.

Erros do Docker em si (daemon fora do ar, imagem ausente etc.) sao
tratados como `erro_interno` e NUNCA tem seu detalhe exposto ao aluno -
apenas logados no servidor."""

import asyncio
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Exit codes de nivel Docker (nao do processo do aluno) - ver `man docker-run`.
_DOCKER_ERRO_EXIT_CODES = {125, 126, 127}
_TIMEOUT_EXIT_CODE = 124
_OOM_EXIT_CODE = 137

LINGUAGENS_SUPORTADAS = {"python"}


class StatusExecucao(StrEnum):
    SUCESSO = "sucesso"
    TEMPO_EXCEDIDO = "tempo_excedido"
    ERRO_EXECUCAO = "erro_execucao"
    ERRO_INTERNO = "erro_interno"


@dataclass(frozen=True)
class ResultadoExecucao:
    status: StatusExecucao
    stdout: str
    erro_sanitizado: str | None
    tempo_execucao_ms: int


def _sanitizar_stderr(stderr: str) -> str:
    """Nunca repassa caminhos internos do sandbox (/sandbox/..., paths da
    stdlib dentro do container) - so a ultima linha da excecao Python
    (tipo + mensagem), que e o que importa pedagogicamente para o aluno
    entender o erro sem aprender nada sobre a infraestrutura."""
    linhas = [linha for linha in stderr.strip().splitlines() if linha.strip()]
    if not linhas:
        return "Ocorreu um erro durante a execucao."
    return linhas[-1].strip()[:500]


def _montar_comando_docker(tmpdir: str, nome_container: str) -> list[str]:
    settings = get_settings()
    return [
        "docker",
        "run",
        "--rm",
        "-i",
        "--name",
        nome_container,
        "--network",
        "none",
        "--memory",
        f"{settings.sandbox_memoria_mb}m",
        "--memory-swap",
        f"{settings.sandbox_memoria_mb}m",
        "--cpus",
        settings.sandbox_cpus,
        "--pids-limit",
        str(settings.sandbox_pids_limit),
        "--read-only",
        "--tmpfs",
        "/tmp:rw,size=16m",
        "-v",
        f"{tmpdir}:/sandbox:ro",
        "--workdir",
        "/sandbox",
        "--user",
        "nobody",
        settings.sandbox_docker_image,
        "timeout",
        f"{settings.sandbox_timeout_segundos}s",
        "python",
        "solucao.py",
    ]


def _executar_sync(codigo_fonte: str, entrada: str, linguagem: str) -> ResultadoExecucao:
    settings = get_settings()

    if linguagem not in LINGUAGENS_SUPORTADAS:
        return ResultadoExecucao(
            status=StatusExecucao.ERRO_INTERNO,
            stdout="",
            erro_sanitizado=f"Linguagem '{linguagem}' nao e suportada.",
            tempo_execucao_ms=0,
        )

    with tempfile.TemporaryDirectory(prefix="teacher_sandbox_") as tmpdir:
        (Path(tmpdir) / "solucao.py").write_text(codigo_fonte, encoding="utf-8")

        nome_container = f"sandbox-{uuid.uuid4().hex[:12]}"
        comando = _montar_comando_docker(tmpdir, nome_container)
        inicio = time.monotonic()

        try:
            resultado = subprocess.run(
                comando,
                input=entrada,
                capture_output=True,
                text=True,
                timeout=settings.sandbox_timeout_segundos + 15,
            )
        except subprocess.TimeoutExpired:
            # O cliente docker nao retornou nem com a margem extra (container
            # travado). Mata explicitamente para nao deixar orfao.
            subprocess.run(["docker", "kill", nome_container], capture_output=True)
            return ResultadoExecucao(
                status=StatusExecucao.TEMPO_EXCEDIDO,
                stdout="",
                erro_sanitizado=None,
                tempo_execucao_ms=int((time.monotonic() - inicio) * 1000),
            )
        except FileNotFoundError:
            logger.error("sandbox_docker_cli_nao_encontrado")
            return ResultadoExecucao(
                status=StatusExecucao.ERRO_INTERNO,
                stdout="",
                erro_sanitizado="Sandbox de execucao indisponivel no momento.",
                tempo_execucao_ms=0,
            )

        tempo_ms = int((time.monotonic() - inicio) * 1000)

        if resultado.returncode in _DOCKER_ERRO_EXIT_CODES:
            logger.error(
                "sandbox_erro_docker",
                returncode=resultado.returncode,
                stderr=resultado.stderr[:2000],
            )
            return ResultadoExecucao(
                status=StatusExecucao.ERRO_INTERNO,
                stdout="",
                erro_sanitizado="Sandbox de execucao indisponivel no momento.",
                tempo_execucao_ms=tempo_ms,
            )

        if resultado.returncode == _TIMEOUT_EXIT_CODE:
            return ResultadoExecucao(
                status=StatusExecucao.TEMPO_EXCEDIDO,
                stdout="",
                erro_sanitizado=None,
                tempo_execucao_ms=tempo_ms,
            )

        if resultado.returncode == _OOM_EXIT_CODE:
            return ResultadoExecucao(
                status=StatusExecucao.ERRO_EXECUCAO,
                stdout="",
                erro_sanitizado="Limite de memoria excedido.",
                tempo_execucao_ms=tempo_ms,
            )

        if resultado.returncode != 0:
            return ResultadoExecucao(
                status=StatusExecucao.ERRO_EXECUCAO,
                stdout=resultado.stdout,
                erro_sanitizado=_sanitizar_stderr(resultado.stderr),
                tempo_execucao_ms=tempo_ms,
            )

        return ResultadoExecucao(
            status=StatusExecucao.SUCESSO,
            stdout=resultado.stdout,
            erro_sanitizado=None,
            tempo_execucao_ms=tempo_ms,
        )


async def executar(codigo_fonte: str, entrada: str, linguagem: str) -> ResultadoExecucao:
    """subprocess.run e bloqueante; roda em thread separada para nao
    travar o event loop do FastAPI enquanto o container executa."""
    return await asyncio.to_thread(_executar_sync, codigo_fonte, entrada, linguagem)
