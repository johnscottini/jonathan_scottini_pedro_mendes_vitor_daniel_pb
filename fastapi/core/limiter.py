"""Rate limiting do endpoint de autenticação — TAREFA 4 (Pessoa 3).

Este módulo existe desde a fase 0 para que `routes/auth.py` e `main.py` já
importem os nomes certos. Hoje as três funções são NO-OP: a API funciona, mas
ainda não limita nada. A Pessoa 3 troca o corpo das funções por `slowapi`
SEM precisar alterar `routes/auth.py` nem `main.py`.

Como implementar (sugestão):

    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)

    def login_rate_limit(endpoint):
        return limiter.limit(RATE_LIMIT_LOGIN)(endpoint)

    def install_rate_limiting(app):
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    def set_rate_limiting_enabled(enabled):
        limiter.enabled = enabled

O `slowapi` exige que o endpoint decorado receba um parâmetro `request: Request`
— ele já está na assinatura de `routes/auth.py:login` desde a fase 0.

Não esquecer: documentar no README o limite escolhido e a justificativa técnica.
"""

from typing import Callable, TypeVar

from fastapi import FastAPI

from core.config import RATE_LIMIT_LOGIN  # noqa: F401  (usado pela implementação)

F = TypeVar("F", bound=Callable)


def login_rate_limit(endpoint: F) -> F:
    """Decorator aplicado ao POST /auth/token. TODO(Pessoa 3): limitar de verdade."""
    return endpoint


def install_rate_limiting(app: FastAPI) -> None:
    """Registra o limiter e o handler de 429 na aplicação. TODO(Pessoa 3)."""
    return None


def set_rate_limiting_enabled(enabled: bool) -> None:
    """Liga/desliga o limite. Usado por `tests/conftest.py` para não poluir os testes."""
    return None
