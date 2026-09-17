from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.limiter import install_rate_limiting
from db import init_db
from middleware.security_headers import add_security_middlewares
from routes import auth, health, predict, tickets


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cria tabelas e usuários iniciais quando a aplicação sobe."""
    init_db()
    yield


app = FastAPI(
    title="Customer Support Intent API",
    description=(
        "API do sistema de atendimento ao cliente. Expõe autenticação JWT, "
        "gestão de tickets por usuário e um endpoint de predição de intenção "
        "com saída simulada (o modelo de ML real será integrado em um TP futuro)."
    ),
    version="0.2.0",
    lifespan=lifespan,
)

# Tarefa 3 (Pessoa 3) — headers de segurança + CORS: ver middleware/security_headers.py
add_security_middlewares(app)

# Tarefa 4 (Pessoa 3) — rate limiting do login: ver core/limiter.py
install_rate_limiting(app)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(tickets.router)
