"""Validadores Pydantic reutilizados por mais de um schema."""

import re


def validar_forca_senha(senha: str) -> str:
    if len(senha) < 8:
        raise ValueError("A senha deve ter pelo menos 8 caracteres.")
    if not re.search(r"[A-Za-z]", senha):
        raise ValueError("A senha deve conter pelo menos uma letra.")
    if not re.search(r"\d", senha):
        raise ValueError("A senha deve conter pelo menos um numero.")
    return senha
