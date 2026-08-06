"""Cria o primeiro usuario Diretor (bootstrap), unica forma de originar uma
conta com privilegio administrativo nesta fase do projeto - nao existe
endpoint publico para isso, de proposito (criar um diretor e um evento raro
e sensivel, nao uma rota de API).

So cria se ainda nao existir nenhum Diretor no banco (idempotente).

Uso:
    .venv\\Scripts\\python.exe scripts\\seed_diretor.py \\
        --nome "Nome Completo" --email diretor@escola.com --senha "SenhaForte123"
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.usuario import Papel  # noqa: E402
from app.repositories import usuario_repository  # noqa: E402


async def seed(nome: str, email: str, senha: str) -> None:
    async with AsyncSessionLocal() as db:
        if await usuario_repository.existe_algum_diretor(db):
            print("Ja existe um Diretor cadastrado. Nada a fazer.")
            return

        if await usuario_repository.get_by_email(db, email) is not None:
            print(f"Ja existe um usuario com o e-mail {email!r}, mas nao e Diretor. Abortando.")
            return

        usuario = await usuario_repository.create(
            db,
            nome=nome,
            email=email,
            senha_hash=hash_password(senha),
            papel=Papel.DIRETOR,
            is_active=True,
        )
        await db.commit()
        print(f"Diretor criado: {usuario.email} (id={usuario.id})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria o primeiro usuario Diretor.")
    parser.add_argument("--nome", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--senha", required=True)
    args = parser.parse_args()

    asyncio.run(seed(args.nome, args.email, args.senha))


if __name__ == "__main__":
    main()
