"""Endpoint de health-check. Alem de confirmar que o processo da API esta
de pe, verifica conectividade real com o PostgreSQL - um /health que so
responde 200 sem checar dependencias criticas costuma mascarar problemas em
producao."""

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    database: Literal["ok", "unavailable"]


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    try:
        await db.execute(text("SELECT 1"))
        database_status: Literal["ok", "unavailable"] = "ok"
    except Exception:
        database_status = "unavailable"

    overall_status: Literal["ok", "degraded"] = "ok" if database_status == "ok" else "degraded"
    return HealthResponse(status=overall_status, database=database_status)
