"""Validação do token JWT (correção do retorno do TP1, Q6).

Não basta a assinatura ser válida: o token precisa estar dentro da validade e o
`sub` precisa corresponder ao usuário autorizado.
"""

import pytest

from core.config import ALGORITHM, SECRET_KEY
from security.jwt import create_access_token
from security.users import ADMIN_USERNAME

ROTA_PROTEGIDA = "/predict"
CORPO = {"text": "minha fatura veio errada"}


def _get(client, token):
    return client.post(ROTA_PROTEGIDA, headers={"Authorization": "Bearer " + token}, json=CORPO)


def test_token_do_admin_e_aceito(client):
    response = _get(client, create_access_token(subject=ADMIN_USERNAME))
    assert response.status_code == 200
    assert set(response.json()) == {"intent", "confidence"}


def test_token_assinado_mas_de_outro_sub_e_recusado(client):
    """Assinatura válida + `sub` não autorizado = 401.

    Este é o caso que o TP1 deixava passar: o código só checava se o `sub`
    existia, não se ele era o usuário autorizado.
    """
    response = _get(client, create_access_token(subject="atacante"))
    assert response.status_code == 401
    assert response.json()["code"] == "unauthorized"


def test_token_expirado_e_recusado(client):
    expirado = create_access_token(subject=ADMIN_USERNAME, expires_minutes=-1)
    response = _get(client, expirado)
    assert response.status_code == 401


def test_token_com_assinatura_adulterada_e_recusado(client):
    token = create_access_token(subject=ADMIN_USERNAME)
    adulterado = token[:-3] + ("aaa" if not token.endswith("aaa") else "bbb")
    response = _get(client, adulterado)
    assert response.status_code == 401


def test_token_sem_claim_exp_e_recusado(client):
    """`exp` é obrigatório: um token sem expiração vale para sempre."""
    jose_jwt = pytest.importorskip("jose").jwt
    sem_exp = jose_jwt.encode({"sub": ADMIN_USERNAME}, SECRET_KEY, algorithm=ALGORITHM)
    response = _get(client, sem_exp)
    assert response.status_code == 401
