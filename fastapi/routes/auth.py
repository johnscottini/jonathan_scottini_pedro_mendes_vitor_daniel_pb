from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from core.limiter import login_rate_limit
from models.auth import Token
from security.jwt import create_access_token
from security.users import authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
@login_rate_limit
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """Autentica o usuário e emite um JWT.

    O parâmetro `request` existe porque o rate limiter (slowapi) precisa dele
    para identificar o IP de origem — não remover.

    TODO(Pessoa 2): `authenticate_user` passa a consultar a tabela `User` via
    sessão do SQLModel (`Depends(get_session)`) em vez do usuário fixo no código.
    """
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=form_data.username)
    return Token(access_token=access_token)
