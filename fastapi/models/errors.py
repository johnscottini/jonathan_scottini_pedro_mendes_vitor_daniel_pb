"""Modelo único de resposta de erro da API.

Antes, cada erro saía no formato padrão do FastAPI (`{"detail": ...}`), que muda
de forma conforme o tipo do erro: uma string nos `HTTPException` e uma lista de
objetos nos erros de validação. Isso obriga o cliente a tratar dois formatos.

Aqui todo erro — 401, 404, 422, 429, 500 — sai no MESMO formato, declarado no
OpenAPI. Os handlers que produzem essa resposta estão em
`core/exception_handlers.py`.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class FieldError(BaseModel):
    """Erro em um campo específico do corpo da requisição."""

    field: str = Field(..., description="Caminho do campo", examples=["body.text"])
    message: str = Field(..., description="O que há de errado com o campo")


class ErrorResponse(BaseModel):
    code: str = Field(
        ...,
        description="Identificador estável do erro, para o cliente tratar programaticamente",
        examples=["unauthorized"],
    )
    message: str = Field(..., description="Descrição legível do erro")
    path: str = Field(..., description="Rota em que o erro ocorreu", examples=["/predict"])
    fields: Optional[List[FieldError]] = Field(
        default=None,
        description="Preenchido apenas em erros de validação (422)",
    )
