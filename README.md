# TP1 — Definição do Domínio, EDA e API Base (Customer Support)

## Objetivo do projeto

Este repositório contém a primeira entrega (TP1) do Projeto de Bloco: um
sistema de atendimento ao cliente alimentado por inteligência artificial.
Nesta etapa o foco é **entender os dados** e **estruturar a API** que vai
servir o sistema ao longo do bloco.

Este TP entrega:
1. Documentação e **análise exploratória (EDA)** do
   [Customer Support Ticket Dataset](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset/data)
   (Kaggle), incluindo inspeção inicial, verificação de qualidade, limpeza,
   análise univariada e hipóteses sobre a intenção dos usuários.
2. A **estrutura base de uma API FastAPI** modular, com autenticação JWT
   (`OAuth2PasswordBearer`) protegendo o endpoint que futuramente servirá o
   modelo de classificação de intenção.
3. Um **DFD (Data Flow Diagram)** da API com entradas, saídas, trust
   boundaries e a tríade CIA (Confidencialidade / Integridade /
   Disponibilidade) aplicada a cada componente.

## Estrutura de pastas

```
.
├── README.md                # este arquivo
├── data/
│   └── customer_support_tickets.csv   # dataset bruto (Kaggle)
├── eda/
│   └── eda.ipynb             # notebook único com toda a EDA
├── fastapi/                  # código-fonte da API
│   ├── main.py                # ponto de entrada da aplicação (FastAPI app)
│   ├── requirements.txt
│   ├── routes/                # endpoints da API
│   │   ├── health.py           # GET /health
│   │   ├── auth.py             # POST /auth/token
│   │   └── predict.py          # POST /predict (protegido por JWT)
│   ├── models/                 # schemas Pydantic de entrada/saída
│   │   ├── auth.py
│   │   └── predict.py
│   └── security/               # autenticação e JWT
│       ├── users.py            # usuário admin in-code (hash bcrypt)
│       └── jwt.py               # geração/validação de token + OAuth2PasswordBearer
└── others/
    └── dfd.png                # DFD da API com trust boundaries e tríade CIA
```

## Dataset

- **Fonte:** [Customer Support Ticket Dataset](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset/data) (Kaggle, autor `suraj520`).
- **Características, motivo da escolha e EDA completa:** ver [`eda/eda.ipynb`](eda/eda.ipynb).
- O CSV usado nesta entrega está versionado em [`data/customer_support_tickets.csv`](data/customer_support_tickets.csv).

## Instalação

Pré-requisito: Python 3.11+ instalado.

```bash
# na raiz do repositório
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (Git Bash) / Linux / macOS
source .venv/Scripts/activate   # ou: source .venv/bin/activate

# dependências da API
pip install -r fastapi/requirements.txt

# dependências extras para rodar o notebook de EDA (opcional)
pip install pandas numpy matplotlib seaborn jupyter nbclient ipykernel
```

## Execução

### API FastAPI

```bash
cd fastapi
uvicorn main:app --reload
```

A API sobe em `http://127.0.0.1:8000`. Documentação interativa
em `http://127.0.0.1:8000/docs`.

**Usuário único autorizado (definido in-code, ver [`security/users.py`](fastapi/security/users.py)):**

```
usuário: admin
senha:   admin123
```

Fluxo de teste manual:

```bash
# 1. Health check (rota pública)
curl http://127.0.0.1:8000/health

# 2. Login -> obtém o token JWT
curl -X POST http://127.0.0.1:8000/auth/token \
  -d "username=admin&password=admin123"

# 3. Chama a rota protegida com o token retornado acima
curl -X POST http://127.0.0.1:8000/predict \
  -H "Authorization: Bearer <TOKEN_AQUI>" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"I need a refund for my order\"}"
```

`POST /predict` ainda **não** roda um modelo de ML: ela retorna uma
intenção pré-determinada (baseada em correspondência simples de palavras-
chave) apenas para simular o formato de resposta que terá em um TP futuro.

### Notebook de EDA

```bash
# com o venv já ativado (ver seção Instalação)
cd eda
jupyter notebook eda.ipynb
```

## Segurança e DFD

O diagrama de fluxo de dados da API (entidades externas, processos, data
stores, trust boundaries e a tríade CIA aplicada a cada componente) está em
[`others/dfd.png`](others/dfd.png).
