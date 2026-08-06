"""Motor de dicas progressivas (Parte 6): o aluno pede a proxima dica para
um problema (o nivel e sempre calculado pelo servidor, nunca escolhido
pelo cliente - ver app/services/dica_service.py) e pode consultar o
proprio historico; Professor+ pode revisar o historico de um aluno
especifico, com o dado de eficacia, para acompanhamento pedagogico."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_aluno_acessivel,
    get_client_ip,
    get_problema_acessivel,
    require_min_role,
    require_roles,
)
from app.core.database import get_db
from app.models.problema import Problema
from app.models.usuario import Papel, Usuario
from app.schemas.dicas import DicaComEficaciaResponse, DicaResponse
from app.services import dica_service
from app.services.exceptions import (
    GeracaoDicaFalhouError,
    MotorIaIndisponivelError,
    NivelMaximoDeDicasAtingidoError,
)

router = APIRouter(tags=["dicas"])


@router.post(
    "/problemas/{problema_id}/dicas",
    response_model=DicaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def solicitar_dica(
    request: Request,
    db: AsyncSession = Depends(get_db),
    problema: Problema = Depends(get_problema_acessivel),
    aluno: Usuario = Depends(require_roles(Papel.ALUNO)),
) -> DicaResponse:
    try:
        gerada = await dica_service.solicitar_proxima_dica(
            db, aluno=aluno, problema=problema, ip_address=get_client_ip(request)
        )
    except NivelMaximoDeDicasAtingidoError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except MotorIaIndisponivelError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
    except GeracaoDicaFalhouError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc

    return DicaResponse.model_validate(gerada.dica)


@router.get("/problemas/{problema_id}/minhas-dicas", response_model=list[DicaResponse])
async def listar_minhas_dicas(
    db: AsyncSession = Depends(get_db),
    problema: Problema = Depends(get_problema_acessivel),
    aluno: Usuario = Depends(require_roles(Papel.ALUNO)),
) -> list[DicaResponse]:
    dicas = await dica_service.listar_historico(db, problema_id=problema.id, aluno_id=aluno.id)
    return [DicaResponse.model_validate(d) for d in dicas]


@router.get(
    "/problemas/{problema_id}/dicas/{aluno_id}",
    response_model=list[DicaComEficaciaResponse],
)
async def listar_dicas_de_aluno(
    db: AsyncSession = Depends(get_db),
    problema: Problema = Depends(get_problema_acessivel),
    aluno: Usuario = Depends(get_aluno_acessivel),
    _ator: Usuario = Depends(require_min_role(Papel.PROFESSOR)),
) -> list[DicaComEficaciaResponse]:
    dicas = await dica_service.listar_historico(db, problema_id=problema.id, aluno_id=aluno.id)
    return [DicaComEficaciaResponse.model_validate(d) for d in dicas]
