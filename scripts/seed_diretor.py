"""Cria uma instituicao (se o codigo informado nao existir ainda) e o
primeiro usuario Diretor dela (bootstrap). Nao existe endpoint publico
para isso, de proposito - criar um diretor e um evento raro e sensivel,
nao uma rota de API.

So cria o Diretor se ainda nao existir nenhum para aquela instituicao
(idempotente).

Uso:
    .venv\\Scripts\\python.exe scripts\\seed_diretor.py \\
        --instituicao-nome "Escola Exemplo" --instituicao-codigo ESCOLA01 \\
        --nome "Nome Completo" --email diretor@escola.com --senha "SenhaForte123"
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.instituicao import Instituicao  # noqa: E402
from app.models.usuario import Papel  # noqa: E402
from app.repositories import instituicao_repository, usuario_repository  # noqa: E402


async def seed(
    instituicao_nome: str, instituicao_codigo: str, nome: str, email: str, senha: str
) -> None:
    async with AsyncSessionLocal() as db:
        instituicao = await instituicao_repository.get_by_codigo(db, instituicao_codigo)
        if instituicao is None:
            instituicao = Instituicao(
                nome=instituicao_nome, codigo=instituicao_codigo.upper(), ativo=True
            )
            db.add(instituicao)
            await db.flush()
            await db.refresh(instituicao)
            print(f"Instituicao criada: {instituicao.nome} (codigo={instituicao.codigo})")
        else:
            print(f"Instituicao ja existia: {instituicao.nome} (codigo={instituicao.codigo})")

        if await usuario_repository.existe_algum_diretor(db, instituicao.id):
            print("Ja existe um Diretor cadastrado para esta instituicao. Nada a fazer.")
            await db.commit()
            return

        if await usuario_repository.get_by_email(db, email) is not None:
            print(f"Ja existe um usuario com o e-mail {email!r}. Abortando.")
            await db.rollback()
            return

        usuario = await usuario_repository.create(
            db,
            nome=nome,
            email=email,
            senha_hash=hash_password(senha),
            papel=Papel.DIRETOR,
            instituicao_id=instituicao.id,
            is_active=True,
        )
        await db.commit()
        print(f"Diretor criado: {usuario.email} (id={usuario.id})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cria a instituicao (se preciso) e o primeiro Diretor."
    )
    parser.add_argument("--instituicao-nome", required=True)
    parser.add_argument("--instituicao-codigo", required=True)
    parser.add_argument("--nome", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--senha", required=True)
    args = parser.parse_args()

    asyncio.run(
        seed(
            args.instituicao_nome,
            args.instituicao_codigo,
            args.nome,
            args.email,
            args.senha,
        )
    )


if __name__ == "__main__":
    main()
