"""Gera o DFD (nível 1) da Customer Support Intent API.

Uso (com o venv ativado, a partir da raiz do repositório):

    python others/dfd.py

Gera `others/dfd.png`. Esta é a fonte versionada do diagrama: qualquer ajuste
deve ser feito aqui e o PNG regerado, para que desenho e documentação não
divirjam.

Decisões de desenho (a versão anterior foi devolvida por baixa legibilidade):

* Os fluxos não têm mais rótulos de texto sobre as setas, que se sobrepunham.
  Cada seta leva um número, e a legenda abaixo descreve origem, destino, dados
  trafegados e direção.
* A trust boundary entre a rede pública e o processo da API é uma linha
  vertical única. Todo fluxo que a cruza é marcado com um losango numerado
  exatamente no ponto de travessia.
* Os segredos embutidos no código (hash da senha do admin e SECRET_KEY) estão
  em uma segunda trust boundary, também com os pontos de travessia marcados.
* Nenhuma seta passa por cima de um nó: processos e data stores foram
  posicionados para que os caminhos fiquem livres.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch, Rectangle

SAIDA = Path(__file__).resolve().parent / "dfd.png"

# Paleta
AZUL, VERDE, LARANJA = "#1f4e79", "#1b6b3a", "#9c6500"
VERMELHO, CINZA = "#b00020", "#444444"

# Posição da trust boundary 1 (rede pública | processo da API)
TB1_X = 34.0

fig, (ax, ax_legenda) = plt.subplots(
    2, 1, figsize=(17, 14), dpi=140, gridspec_kw={"height_ratios": [1.25, 1]}
)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")
ax_legenda.axis("off")

fig.suptitle(
    "DFD (nível 1) — Customer Support Intent API\n"
    "Entidades externas, processos, data stores, trust boundaries e tríade CIA",
    fontsize=15,
    fontweight="bold",
    y=0.985,
)

# --------------------------------------------------------------- zonas ----
ax.add_patch(Rectangle((0, 6), TB1_X, 88, facecolor="#fdeaea", edgecolor="none", zorder=0))
ax.add_patch(Rectangle((TB1_X, 6), 100 - TB1_X, 88, facecolor="#eaf5ee", edgecolor="none", zorder=0))

ax.plot([TB1_X, TB1_X], [6, 94], linestyle=(0, (7, 4)), color=VERMELHO, linewidth=2.6, zorder=2)
ax.text(
    TB1_X, 95.5,
    "TRUST BOUNDARY 1 — rede pública (não confiável)  |  processo da API (confiável)",
    ha="center", va="bottom", fontsize=10.5, fontweight="bold", color=VERMELHO,
)
ax.text(1.5, 89, "ZONA NÃO CONFIÁVEL\nentrada via HTTPS", fontsize=9.5, color=VERMELHO,
        fontweight="bold", va="top")
ax.text(98.5, 89, "PROCESSO DA API\n(uvicorn + FastAPI)", fontsize=9.5, color=VERDE,
        fontweight="bold", ha="right", va="top")

# Trust boundary 2: segredos embutidos no código
ax.add_patch(Rectangle((56, 8), 42, 20, fill=False, linestyle=(0, (6, 4)),
                       edgecolor=LARANJA, linewidth=2.2, zorder=2))
# rótulo dentro da caixa, abaixo dos data stores: fora do caminho das setas
ax.text(77, 10.0, "TRUST BOUNDARY 2 — segredos embutidos no código",
        ha="center", fontsize=9.5, fontweight="bold", color=LARANJA)


def entidade(x, y, titulo, subtitulo, cor=AZUL):
    """Entidade externa: retângulo."""
    ax.add_patch(FancyBboxPatch((x - 13, y - 7), 26, 14, boxstyle="round,pad=0.4",
                                facecolor="#dce6f1", edgecolor=cor, linewidth=2, zorder=3))
    ax.text(x, y + 2.4, titulo, ha="center", fontsize=11, fontweight="bold", color=cor, zorder=4)
    ax.text(x, y - 3.4, subtitulo, ha="center", fontsize=8.8, color=CINZA, zorder=4)


def processo(x, y, titulo, subtitulo="", rx=11, ry=7.5):
    """Processo: elipse."""
    ax.add_patch(Ellipse((x, y), rx * 2, ry * 2, facecolor="#e2f0e6",
                         edgecolor=VERDE, linewidth=2, zorder=3))
    ax.text(x, y + (1.6 if subtitulo else 0), titulo, ha="center", va="center",
            fontsize=10, fontweight="bold", color=VERDE, zorder=4)
    if subtitulo:
        ax.text(x, y - 2.8, subtitulo, ha="center", va="center", fontsize=8.3,
                color=CINZA, zorder=4)


def data_store(x, y, titulo, subtitulo, largura):
    """Data store: duas linhas paralelas, abertas nas laterais."""
    ax.add_patch(Rectangle((x - largura / 2, y - 3.4), largura, 6.8,
                           facecolor="#fdf3e0", edgecolor="none", zorder=3))
    for dy in (-3.4, 3.4):
        ax.plot([x - largura / 2, x + largura / 2], [y + dy, y + dy],
                color=LARANJA, linewidth=2, zorder=4)
    ax.text(x, y + 1.1, titulo, ha="center", fontsize=9.2, fontweight="bold",
            color=LARANJA, zorder=4)
    ax.text(x, y - 2.4, subtitulo, ha="center", fontsize=8.0, color=CINZA, zorder=4)


# ---------------------------------------------------- nós do diagrama -----
entidade(16, 72, "Usuário / Admin", "único usuário autorizado")
entidade(16, 30, "Atacante", "sem token ou com token forjado", cor=VERMELHO)

processo(50, 86, "GET /health", "público")
processo(50, 64, "POST /auth/token", "autenticação")
processo(50, 40, "POST /predict", "protegido por JWT")
processo(84, 64, "Validação JWT", "OAuth2PasswordBearer", rx=13, ry=8)

data_store(69, 18, "DS1 — usuário admin", "hash bcrypt da senha (in-code)", largura=22)
data_store(90, 18, "DS2 — SECRET_KEY", "assinatura HS256 (in-code)", largura=14)

# ------------------------------------------------------------- fluxos -----
# (nº, origem, destino, cor, curvatura, cruza_TB1, posição do número)
FLUXOS = [
    (1,  (29, 78),   (40, 88),   VERDE,    0.0,   True,  None),
    (2,  (40, 82),   (29, 72),   VERDE,    0.0,   True,  None),
    (3,  (29, 70),   (39.5, 66), AZUL,     0.0,   True,  None),
    # saem pela direita de /auth/token para não passar por cima de /predict
    (4,  (58, 57),   (66, 23),   LARANJA, -0.10,  False, (64, 41)),
    (5,  (60, 55),   (84, 23),   LARANJA, -0.10,  False, (73, 35)),
    (6,  (39.5, 61), (29, 67),   VERDE,    0.0,   True,  None),
    (7,  (29, 64),   (39.5, 43), AZUL,     0.0,   True,  None),
    (8,  (60, 44),   (72, 58),   AZUL,    -0.15,  False, (65, 52)),
    (9,  (88, 56),   (91, 22),   LARANJA,  0.10,  False, (91, 40)),
    (10, (79, 56),   (72, 23),   LARANJA,  0.10,  False, (78, 45)),
    (11, (39.5, 37), (29, 59),   VERDE,    0.0,   True,  None),
    (12, (29, 33),   (41, 36.5), VERMELHO, 0.0,   True,  None),
    (13, (43, 33),   (29, 27),   VERMELHO, 0.0,   True,  None),
]


def numero(x, y, texto, cor, forma="o"):
    ax.plot(x, y, marker=forma, markersize=15 if forma == "D" else 13,
            markerfacecolor="white", markeredgecolor=cor, markeredgewidth=1.7, zorder=6)
    ax.text(x, y, texto, ha="center", va="center", fontsize=8.5,
            fontweight="bold", color=cor, zorder=7)


for num, inicio, fim, cor, curva, cruza_tb1, pos_num in FLUXOS:
    ax.add_patch(FancyArrowPatch(
        inicio, fim, arrowstyle="-|>", mutation_scale=17, linewidth=1.9,
        color=cor, connectionstyle=f"arc3,rad={curva}", zorder=5,
        shrinkA=2, shrinkB=2,
    ))
    if cruza_tb1:
        # losango exatamente no ponto em que a seta atravessa a trust boundary
        (x1, y1), (x2, y2) = inicio, fim
        t = (TB1_X - x1) / (x2 - x1)
        numero(TB1_X, y1 + t * (y2 - y1), str(num), cor, forma="D")
    else:
        numero(*pos_num, str(num), cor)

ax.text(1.5, 2.5,
        "retângulo = entidade externa      elipse = processo      "
        "linhas paralelas = data store      ◇ = ponto de travessia de trust boundary      "
        "○ = fluxo interno",
        fontsize=9, color=CINZA)

# ------------------------------------------------------------ legenda -----
FLUXOS_TXT = [
    ("1", "Usuário → GET /health", "requisição sem credenciais", "cruza TB1"),
    ("2", "GET /health → Usuário", "200 {status, version}", "cruza TB1"),
    ("3", "Usuário → POST /auth/token", "username + senha (form)", "cruza TB1 · CONFIDENCIAL"),
    ("4", "POST /auth/token → DS1", "lê o hash bcrypt e compara a senha", "cruza TB2"),
    ("5", "POST /auth/token → DS2", "lê a SECRET_KEY e assina o JWT", "cruza TB2"),
    ("6", "POST /auth/token → Usuário", "200 {access_token, token_type}", "cruza TB1 · CONFIDENCIAL"),
    ("7", "Usuário → POST /predict", "Bearer token + texto do ticket", "cruza TB1"),
    ("8", "POST /predict → Validação JWT", "token recebido no header", "interno"),
    ("9", "Validação JWT → DS2", "lê a SECRET_KEY: assinatura + exp", "cruza TB2"),
    ("10", "Validação JWT → DS1", "confere se o sub é o admin autorizado", "cruza TB2"),
    ("11", "POST /predict → Usuário", "200 {intent, confidence}", "cruza TB1"),
    ("12", "Atacante → POST /predict", "sem token, token forjado ou expirado", "cruza TB1 · BLOQUEADO"),
    ("13", "POST /predict → Atacante", "401 {code, message, path}", "cruza TB1"),
]

CIA_TXT = [
    ("GET /health", [
        "C: baixa — não expõe dado sensível",
        "I: média — não pode mentir sobre o estado da API",
        "D: ALTA — é o endpoint consumido pelo monitoramento",
    ]),
    ("POST /auth/token", [
        "C: ALTA — senha trafega aqui; exige HTTPS",
        "I: ALTA — o token emitido não pode ser forjado nem alterado",
        "D: média — rate limit (negar excesso de tentativas) é desejável",
    ]),
    ("POST /predict", [
        "C: ALTA — o texto do ticket pode conter dados pessoais do cliente",
        "I: ALTA — a resposta não pode ser adulterada em trânsito",
        "D: média — é o endpoint principal do produto",
    ]),
    ("Validação JWT", [
        "C: média — manipula o token, não o segredo do usuário",
        "I: ALTA — é o controle de acesso da API; falha aqui libera tudo",
        "D: ALTA — se cair, toda rota protegida fica inacessível",
    ]),
    ("DS1 — usuário admin (hash bcrypt)", [
        "C: MÁXIMA — o hash nunca pode ser exposto em resposta ou log",
        "I: ALTA — alteração indevida concede acesso a terceiros",
        "D: baixa — constante em código, sempre disponível com o processo",
    ]),
    ("DS2 — SECRET_KEY", [
        "C: MÁXIMA — vazou, qualquer um forja um token de admin válido",
        "I: ALTA — trocar a chave invalida todos os tokens em circulação",
        "D: baixa — constante em código, sempre disponível com o processo",
    ]),
]

ax_legenda.text(0.0, 1.0, "FLUXOS DE DADOS", fontsize=11, fontweight="bold",
                color=CINZA, transform=ax_legenda.transAxes)
y = 0.93
for num, caminho, dados, obs in FLUXOS_TXT:
    cor = VERMELHO if "BLOQUEADO" in obs else (AZUL if "CONFIDENCIAL" in obs else CINZA)
    ax_legenda.text(0.0, y, f"{num:>3}", fontsize=8.8, fontweight="bold", color=cor,
                    transform=ax_legenda.transAxes)
    ax_legenda.text(0.03, y, caminho, fontsize=8.8, transform=ax_legenda.transAxes)
    ax_legenda.text(0.215, y, dados, fontsize=8.8, color=CINZA, transform=ax_legenda.transAxes)
    ax_legenda.text(0.40, y, obs, fontsize=8.8, color=cor, transform=ax_legenda.transAxes)
    y -= 0.056

ax_legenda.text(0.57, 1.0, "TRÍADE CIA POR COMPONENTE", fontsize=11, fontweight="bold",
                color=CINZA, transform=ax_legenda.transAxes)
y = 0.93
for componente, linhas in CIA_TXT:
    ax_legenda.text(0.57, y, componente, fontsize=8.8, fontweight="bold",
                    transform=ax_legenda.transAxes)
    for linha in linhas:
        y -= 0.033
        ax_legenda.text(0.585, y, linha, fontsize=8.2, color=CINZA,
                        transform=ax_legenda.transAxes)
    y -= 0.045

fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig(SAIDA, bbox_inches="tight", facecolor="white")
print(f"DFD gerado em {SAIDA}")
