from fastapi import APIRouter, Depends

from models.predict import PredictRequest, PredictResponse
from security.jwt import get_current_user

router = APIRouter(tags=["predict"])

_KEYWORD_INTENTS = [
    ("refund", "refund_request"),
    ("reembolso", "refund_request"),
    ("cancel", "cancellation_request"),
    ("cancela", "cancellation_request"),
    ("bill", "billing_inquiry"),
    ("fatura", "billing_inquiry"),
    ("cobra", "billing_inquiry"),
    ("bug", "technical_issue"),
    ("error", "technical_issue"),
    ("erro", "technical_issue"),
    ("problem", "technical_issue"),
    ("problema", "technical_issue"),
]

_DEFAULT_INTENT = "product_inquiry"
_STUB_CONFIDENCE = 0.5


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, current_user: str = Depends(get_current_user)):
    """Endpoint protegido, ainda não roda um modelo de ML.

    Retorna uma intenção pre-determinada com base em uma correspondência simples de palavras-chave,
    apenas para simular a forma da resposta que o futuro classificador produzirá.
    """
    text_lower = payload.text.lower()
    intent = _DEFAULT_INTENT
    for keyword, mapped_intent in _KEYWORD_INTENTS:
        if keyword in text_lower:
            intent = mapped_intent
            break
    return PredictResponse(intent=intent, confidence=_STUB_CONFIDENCE)
