"""Handlers que padronizam TODAS as respostas de erro no formato `ErrorResponse`.

Registrados em `main.py` por `register_exception_handlers(app)`.

Três motivos para padronizar:

1. Contrato: o cliente trata um único formato de erro, qualquer que seja o status.
2. Documentação: o formato aparece no OpenAPI (as rotas declaram `responses=`).
3. Segurança: o handler genérico de `Exception` devolve uma mensagem neutra em
   vez do traceback. Stack trace em resposta HTTP entrega estrutura interna,
   versões e caminhos de arquivo para quem estiver sondando a API
   (OWASP A05 — Security Misconfiguration).
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from models.errors import ErrorResponse

# Código estável por status HTTP. O cliente deve ramificar por `code`, não pela
# mensagem (que é texto livre e pode mudar).
_CODE_BY_STATUS = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "method_not_allowed",
    409: "conflict",
    422: "validation_error",
    429: "rate_limited",
    500: "internal_error",
}


def _code_for(status_code: int) -> str:
    return _CODE_BY_STATUS.get(status_code, "error")


def _json(status_code: int, payload: ErrorResponse, headers=None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(exclude_none=True),
        headers=headers,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """401, 403, 404, 429... — tudo que é levantado como HTTPException."""
    return _json(
        exc.status_code,
        ErrorResponse(
            code=_code_for(exc.status_code),
            message=str(exc.detail),
            path=request.url.path,
        ),
        # Preserva headers da exceção, em especial o `WWW-Authenticate: Bearer`
        # exigido pelo fluxo OAuth2 nas respostas 401.
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """422 — corpo inválido, campo faltando ou campo extra (`extra="forbid"`)."""
    fields = [
        {
            "field": ".".join(str(part) for part in error.get("loc", [])),
            "message": error.get("msg", "campo inválido"),
        }
        for error in exc.errors()
    ]
    return _json(
        422,
        ErrorResponse(
            code="validation_error",
            message="Corpo da requisição inválido",
            path=request.url.path,
            fields=fields,
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """500 — qualquer erro não previsto, sem vazar detalhes internos."""
    return _json(
        500,
        ErrorResponse(
            code="internal_error",
            message="Erro interno do servidor",
            path=request.url.path,
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
