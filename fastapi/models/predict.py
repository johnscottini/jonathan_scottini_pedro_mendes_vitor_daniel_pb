from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Texto do ticket enviado pelo cliente")


class PredictResponse(BaseModel):
    intent: str
    confidence: float
