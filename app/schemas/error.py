"""Schema de erro unico usado em toda a API. Qualquer excecao tratada pela
aplicacao (HTTPException, erro de validacao, erro nao tratado) e serializada
neste formato, garantindo que o consumidor da API nunca precise lidar com
formatos de erro diferentes dependendo do endpoint."""

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Codigo estavel do erro, ex: 'validation_error'")
    message: str = Field(..., description="Mensagem legivel para humanos")
    fields: dict[str, list[str]] | None = Field(
        default=None, description="Erros de validacao por campo, quando aplicavel"
    )


class ErrorResponse(BaseModel):
    error: ErrorDetail
    request_id: str | None = Field(default=None, description="ID de correlacao da requisicao")
