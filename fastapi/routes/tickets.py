"""Rotas de tickets — TAREFA 2 (Pessoa 2): ownership / BOLA.

O router já está registrado em `main.py`, então basta implementar os endpoints
abaixo. Contrato combinado na fase 0 (não mudar sem avisar o time):

    POST /tickets        body TicketCreate  -> 201 TicketRead
    GET  /tickets                           -> 200 List[TicketRead]  (só os do usuário logado)
    GET  /tickets/{ticket_id}               -> 200 TicketRead

Regras de segurança:

- `owner_id` SEMPRE vem de `current_user.id`, nunca do corpo da requisição.
- `GET /tickets` filtra por `Ticket.owner_id == current_user.id`.
- `GET /tickets/{id}` de um ticket de outro usuário devolve **404**, não 403:
  o 403 confirmaria para o atacante que aquele ID existe (enumeração).
- Nada de SQL cru: só `select()` do SQLModel, que já é parametrizado.

Esboço:

    from typing import List

    from fastapi import APIRouter, Depends, HTTPException, status
    from sqlmodel import Session, select

    from db import get_session
    from models.tables import Ticket, User
    from models.ticket import TicketCreate, TicketRead
    from security.jwt import get_current_user

    @router.get("/{ticket_id}", response_model=TicketRead)
    def obter_ticket(
        ticket_id: int,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
    ):
        ticket = session.get(Ticket, ticket_id)
        if ticket is None or ticket.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket não encontrado")
        return ticket
"""

from fastapi import APIRouter

router = APIRouter(prefix="/tickets", tags=["tickets"])

# TODO(Pessoa 2): implementar POST /tickets, GET /tickets e GET /tickets/{ticket_id}.
