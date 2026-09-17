"""Headers de segurança HTTP e CORS — TAREFA 3 (Pessoa 3).

`main.py` já chama `add_security_middlewares(app)` desde a fase 0, então a
Pessoa 3 só precisa implementar esta função — sem tocar em `main.py`.

O que precisa ser entregue aqui:

1. Middleware que adiciona em TODA resposta:
   - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
   - `X-Frame-Options: DENY`
   - `X-Content-Type-Options: nosniff`
   - `Content-Security-Policy: default-src 'none'; frame-ancestors 'none'`
     (a API só devolve JSON; atenção que uma CSP muito restritiva quebra a
     página /docs do Swagger — decidam se liberam o /docs ou se aceitam isso
     e documentem a escolha no relatório do ZAP)
   - opcional, mas o ZAP costuma pedir: `Referrer-Policy: no-referrer`,
     `Permissions-Policy`, e remover o header `server`.

2. CORS com allowlist explícita, usando `CORS_ORIGINS` de `core.config`.
   Nunca `allow_origins=["*"]` junto com `allow_credentials=True`.
   Restringir também métodos e headers ao que a API realmente usa.

Esboço:

    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware

    from core.config import CORS_ORIGINS

    def add_security_middlewares(app: FastAPI) -> None:
        @app.middleware("http")
        async def security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Frame-Options"] = "DENY"
            ...
            return response

        app.add_middleware(
            CORSMiddleware,
            allow_origins=CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type"],
        )
"""

from fastapi import FastAPI


def add_security_middlewares(app: FastAPI) -> None:
    """TODO(Pessoa 3): headers de segurança + CORS com allowlist."""
    return None
