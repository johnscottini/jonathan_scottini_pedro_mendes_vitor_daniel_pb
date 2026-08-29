from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """Endpoint público, sem autenticação necessária."""
    return {"status": "ok"}
