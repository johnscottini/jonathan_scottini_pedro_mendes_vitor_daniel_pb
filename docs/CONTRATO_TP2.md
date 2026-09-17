# Contrato do TP2 — decisões da fase 0

Documento de referência do time. Tudo o que está aqui **já foi decidido e já está
no código** (`main`): ninguém precisa reinventar nada, e mudar qualquer item
abaixo exige avisar as outras duas pessoas, porque quebra o trabalho delas.

- **Repositório:** branch `main` já contém o esqueleto.
- **Python:** 3.11+ (o código roda em 3.9, mas padronizem a versão para evitar surpresa).

---

## 1. Divisão de responsabilidades

| Pessoa | Tarefas do enunciado | Arquivos que essa pessoa edita |
|---|---|---|
| **Pessoa 1 — EDA** | 1 e 7 | `eda/eda.ipynb`, `docs/relatorio_eda.md`, `eda/requirements.txt` |
| **Pessoa 2 — Dados e autorização** | 2 e 6 | `fastapi/db.py` (seed), `fastapi/models/*`, `fastapi/routes/tickets.py`, `fastapi/security/*`, `tests/*` |
| **Pessoa 3 — Hardening e auditoria** | 3, 4 e 5 | `fastapi/middleware/security_headers.py`, `fastapi/core/limiter.py`, `docs/zap_findings.md`, `docs/zap_report.html` |

**Arquivos congelados** (definidos na fase 0, ninguém altera sem combinar):
`fastapi/main.py`, `fastapi/core/config.py`, `fastapi/models/tables.py`,
`fastapi/models/ticket.py`, `fastapi/requirements*.txt`, `pytest.ini`,
`tests/conftest.py`.

> O `main.py` já chama `add_security_middlewares(app)` e `install_rate_limiting(app)`,
> e o `routes/auth.py` já está decorado com `@login_rate_limit` e recebe
> `request: Request`. Ou seja: **a Pessoa 3 implementa só os dois módulos dela** e
> não encosta em `main.py` nem em `routes/auth.py`. Era o principal ponto de
> conflito de merge.

---

## 2. Modelo de dados (já implementado em `fastapi/models/tables.py`)

```python
class User(SQLModel, table=True):
    id: int | None            # PK
    username: str             # único, indexado, máx. 50
    hashed_password: str      # bcrypt

class Ticket(SQLModel, table=True):
    id: int | None            # PK
    owner_id: int             # FK -> user.id, indexado  <-- base do controle de BOLA
    subject: str              # máx. 200
    description: str          # máx. 4000
    ticket_type: str          # máx. 50   (ex.: "Billing inquiry")
    priority: str = "Low"
    channel: str = "Email"
    status: str = "Open"
    created_at: datetime      # UTC
```

Os nomes dos campos espelham as colunas do dataset do Kaggle, para o TP do
modelo de classificação reaproveitar sem tradução.

- **Banco:** SQLite em `fastapi/app.db` (já está no `.gitignore`).
- **Usuários iniciais (seed):** `alice` e `bob`, senha em hash bcrypt, criados no
  `init_db()`. Manter também o `admin` do TP1, se quiserem, mas sem senha fraca.
- **SQL cru é proibido.** Só `select()`/`session.get()` do SQLModel, que já são
  queries parametrizadas (OWASP A03 — Injection).

---

## 3. Contrato de autenticação

- O `sub` do JWT guarda o **`username`**.
- `security/jwt.py::get_current_user` passa a devolver o objeto **`User`**
  (hoje devolve `str`) — precisa de `Depends(get_session)`.
- A `SECRET_KEY` sai do código e vem de `core.config` / variável de ambiente.
- Expiração do token: 30 minutos (`ACCESS_TOKEN_EXPIRE_MINUTES`).

---

## 4. Rotas e códigos de resposta

| Método | Rota | Body | Sucesso |
|---|---|---|---|
| POST | `/auth/token` | form OAuth2 | 200 `Token` |
| GET | `/health` | — | 200 |
| POST | `/predict` | `PredictRequest` | 200 `PredictResponse` |
| POST | `/tickets` | `TicketCreate` | 201 `TicketRead` |
| GET | `/tickets` | — | 200 `List[TicketRead]` (só do usuário logado) |
| GET | `/tickets/{id}` | — | 200 `TicketRead` |

**Tabela única de erros** — testes, ZAP e documentação usam estes números:

| Situação | Status |
|---|---|
| Sem token / token inválido ou expirado | **401** |
| Recurso existe mas é de outro usuário | **404** (não 403: 403 confirma que o ID existe) |
| Campo extra ou inválido no body | **422** |
| Estourou o rate limit do login | **429** |

Regras invioláveis:
- `owner_id` nunca vem do body; sempre de `current_user.id`.
- Todo schema de **entrada** herda de `models/base.py::StrictModel`
  (`extra="forbid"`). Falta aplicar em `PredictRequest` — tarefa da Pessoa 2.

---

## 5. Configuração (`fastapi/core/config.py` + `.env.example`)

| Variável | Default | Dono |
|---|---|---|
| `SECRET_KEY` | valor de dev | Pessoa 2 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Pessoa 2 |
| `DATABASE_URL` | `sqlite:///fastapi/app.db` | Pessoa 2 |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Pessoa 3 |
| `RATE_LIMIT_LOGIN` | `5/minute` | Pessoa 3 |

**Rate limit — decisão e justificativa (documentar no README):** 5 tentativas por
minuto por IP no `POST /auth/token`. Um usuário legítimo erra a senha 2 ou 3
vezes, no máximo; um ataque de força bruta com 5 tentativas/minuto levaria anos
para varrer um dicionário pequeno. O limite é por IP porque limitar por usuário
permitiria que o atacante travasse a conta de um terceiro (negação de serviço).

---

## 6. Testes

- Rodar **da raiz do repositório**: `pytest tests/`.
- `pytest.ini` coloca `fastapi/` no `pythonpath` — a pasta tem o mesmo nome da
  biblioteca, e sem isso o `import fastapi` pega a pasta errada. Já validado.
- Cada teste usa SQLite **em memória**; o `app.db` real nunca é tocado.
- Fixtures já prontas em `tests/conftest.py` (nomes fazem parte do contrato):
  `session`, `client`, `alice`, `bob`, `token_alice`, `token_bob`, `ticket_de_bob`,
  além dos helpers `criar_usuario`, `obter_token` e `auth_header`.
- O rate limit é desligado automaticamente durante os testes
  (`core/limiter.py::set_rate_limiting_enabled`), senão o login em série
  derrubaria a suíte com 429.
- Os 3 testes obrigatórios já estão escritos em `tests/test_seguranca.py`, com
  `skip`. A Pessoa 2 remove o `pytestmark` conforme implementa as rotas.

---

## 7. EDA — o que precisa ser decidido pela Pessoa 1

Nenhuma das 4 hipóteses do TP1 é testável direto com t-test ou Mann-Whitney
(a H1 pediria qui-quadrado; H3 e H4 não comparam grandezas numéricas).

**Decisão:** adaptar a **H2** ("as intenções se dividem em um eixo técnico e um
eixo comercial") para uma comparação numérica e testar com **Mann-Whitney**:

> Entre os tickets `Closed`, a satisfação do cliente (`Customer Satisfaction
> Rating`) difere entre tickets de intenção **técnica** e de intenção
> **comercial**?

Mann-Whitney em vez de t-test porque a nota de satisfação é ordinal de 1 a 5 e
não tem distribuição normal. Interpretar o p-valor em linguagem acessível e —
importante — comentar que, sendo um dataset sintético, um resultado não
significativo é um achado esperado e igualmente válido de reportar.

Entregáveis da Pessoa 1: heatmap de correlação, pelo menos 2 scatter plots, o
teste de hipótese com p-valor interpretado, e o `docs/relatorio_eda.md` com as
seções problema / dados / análise / insights / limitações / próximos passos.

---

## 8. Organização do trabalho

**Branches:** `feat/eda` (Pessoa 1), `feat/bola-sqlmodel` (Pessoa 2),
`feat/hardening` (Pessoa 3). PR para `main` com `pytest tests/` passando e
revisão de pelo menos uma outra pessoa.

**Ordem obrigatória:** o scan do ZAP (tarefa 5) só pode rodar depois que as
partes das Pessoas 2 e 3 estiverem juntas na `main`. Combinem uma data-limite
para esse merge — é o gargalo da entrega.

**Revisão cruzada no final:** Pessoa 1 revisa o hardening, Pessoa 2 revisa a EDA,
Pessoa 3 revisa as rotas e os testes.

**Entregáveis (checklist do enunciado):**

- [ ] `eda/eda.ipynb` com heatmap, scatter plots e teste de hipótese interpretado
- [ ] API com `extra="forbid"`, SQLModel, ownership, headers, CORS e rate limit
- [ ] `docs/zap_report.html` + `docs/zap_findings.md` (todo Medium/High documentado)
- [ ] `pytest tests/` passando com pelo menos 3 testes de segurança
- [ ] `docs/relatorio_eda.md` com as 6 seções
- [ ] README atualizado para o TP2 (estrutura, como rodar, limite de rate e justificativa)

---

## 9. Como rodar (para todos)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r fastapi/requirements-dev.txt   # API + pytest
pip install -r eda/requirements.txt           # só quem for mexer no notebook
pytest tests/                                 # da raiz do repositório
cd fastapi && uvicorn main:app --reload       # API em http://127.0.0.1:8000
```
