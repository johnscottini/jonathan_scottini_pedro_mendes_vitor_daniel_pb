from fastapi import FastAPI

from routes import auth, health, predict

app = FastAPI(
    title="Customer Support Intent API",
    description=(
        "API base do sistema de atendimento ao cliente. Nesta fase expõe "
        "autenticação JWT e um endpoint de predição de intenção com saída "
        "simulada (o modelo de ML real será integrado em um TP futuro)."
    ),
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(predict.router)
