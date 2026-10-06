"""Emissão e validação de JWT + dependência `OAuth2PasswordBearer`.

Validação do token em `get_current_user`, nesta ordem:

1. **Assinatura** (HS256 com a `SECRET_KEY`): detecta token forjado ou adulterado.
2. **Expiração**: `exp` é obrigatório (`require_exp`) e verificado; token vencido
   é recusado mesmo com assinatura válida.
3. **Autorização do `sub`**: assinatura válida não basta. O `sub` precisa
   corresponder ao usuário administrativo — o único autorizado a usar a API.
   Sem essa checagem, um token assinado para qualquer outro `sub` (por exemplo
   emitido por outro serviço que compartilhe a chave, ou por um endpoint futuro
   que emita tokens para outros perfis) passaria direto.
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from security.users import ADMIN_USERNAME

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Claims que o token DEVE trazer para ser aceito.
_DECODE_OPTIONS = {
    "verify_signature": True,
    "verify_exp": True,
    "require_exp": True,
    "require_sub": True,
}


def create_access_token(subject: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    issued_at = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # (1) assinatura e (2) expiração
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM], options=_DECODE_OPTIONS
        )
    except JWTError:
        raise credentials_exception

    # (3) o `sub` é o usuário autorizado?
    # TODO(TP2 / Pessoa 2): com a tabela `User`, esta checagem vira uma consulta
    # ao banco (`select(User).where(User.username == sub)`) e a função passa a
    # devolver o objeto `User`. O controle é o mesmo: `sub` precisa corresponder
    # a um usuário autorizado existente, não só a um token bem assinado.
    username = payload.get("sub")
    if username != ADMIN_USERNAME:
        raise credentials_exception

    return username
