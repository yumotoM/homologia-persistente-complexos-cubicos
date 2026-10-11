"""Convenções visuais de todos os blocos."""
from __future__ import annotations

import subprocess
from textwrap import dedent
from typing import TYPE_CHECKING

import manimpango
from manimlib import *

if TYPE_CHECKING:
    from manim_slides import Slide
    from manimlib.typing import ManimColor

# O Pango não acha a Latin Modern pelo fontconfig; registrada aqui, os números
# (DecimalNumber) e o Text saem na mesma Computer Modern das fórmulas. O arquivo
# vem com o LaTeX, e o kpsewhich (do próprio TeX) diz onde ele está em cada sistema.
FONTE_LM = subprocess.run(["kpsewhich", "lmroman10-regular.otf"], capture_output=True, text=True).stdout.strip()
if not FONTE_LM:
    raise RuntimeError("Fonte Latin Modern (lmroman10-regular.otf) não encontrada: instale o LaTeX (ver README).")
manimpango.register_font(FONTE_LM)

# Células, nas cores da Fig. 3 de Wagner et al.
COR_VERTICE = YELLOW
COR_ARESTA = BLUE
COR_QUADRADO = RED
COR_VOXEL = GREEN

# Classes de homologia, iguais do barcode ao diagrama.
COR_H0 = TEAL
COR_H1 = PINK


# A fonte única do sumário e do índice de seção no canto dos slides.
SUMARIO = [
    "TDA e o fluxo da persistência",
    "O formato do dado",
    "Complexos cúbicos",
    "Filtração",
    "Matriz de bordo e redução",
    "Leitura do diagrama",
    "Aplicação: imagens de satélite",
]


def titulo(texto: str) -> TexText:
    """Título do slide, centralizado, numa faixa abaixo do índice de seção."""
    return TexText(texto, font_size=46).move_to(UP * 3.1)


def indice_secao(numero: int) -> VGroup:
    """O item do sumário em que estamos, pequeno, no canto superior esquerdo."""
    indice = VGroup(
        Tex(str(numero), font_size=26).set_color(YELLOW),
        TexText(SUMARIO[numero - 1], font_size=24).set_color(GREY_B),
    ).arrange(RIGHT, buff=0.2)
    return indice.to_corner(UL, buff=0.28)


class EixoNumerado(VGroup):
    """Reta numérica com os números como objetos à parte, e não como submobjects da reta.

    No ManimGL 1.7, tirar ou pôr submobjects num NumberLine em volta de uma animação
    faz a reta deixar de ser desenhada. Com os números à parte, a reta é desenhada e os
    números são escritos em dois tempos, sem mexer na família dela. Responde a n2p
    como um NumberLine.
    """

    def __init__(self, x_range: tuple[float, float, float], unit_size: float, font_size: float, direcao: np.ndarray = DOWN) -> None:
        reta = NumberLine(x_range=x_range, unit_size=unit_size, include_numbers=False)
        numeros = VGroup()
        inicio, fim, passo = x_range
        valor = inicio
        while valor <= fim + 1e-9:
            numero = Integer(int(round(valor)), font_size=font_size)
            numero.next_to(reta.n2p(valor), direcao, buff=MED_SMALL_BUFF)
            numeros.add(numero)
            valor += passo
        super().__init__(reta, numeros)

    @property
    def reta(self) -> NumberLine:
        return self[0]

    @property
    def numeros(self) -> VGroup:
        return self[1]

    def n2p(self, x: float) -> np.ndarray:
        return self.reta.n2p(x)


def cria_eixo(cena: Scene, eixo: EixoNumerado, tempo: float = 2.5) -> None:
    """Desenha um EixoNumerado devagar: a reta com os ticks, depois os números um a um."""
    cena.play(ShowCreation(eixo.reta), run_time=tempo)
    cena.play(LaggedStartMap(Write, eixo.numeros, lag_ratio=0.25), run_time=1.5)


def rodape(texto: str) -> TexText:
    nota = TexText(texto, font_size=22).set_color(GREY_B)
    nota.to_corner(DR, buff=0.3)
    return nota


def cor_na_escala(cores: list[ManimColor], alpha: float) -> ManimColor:
    """Interpola linearmente em sRGB numa lista de cores, com alpha em [0, 1].

    O interpolate_color do ManimGL interpola no quadrado das componentes, o que
    clareia os escuros (0,08 vira 0,28). Num mapa de valores, o cinza tem de ser
    proporcional ao valor, como num visualizador de imagem.
    """
    alpha = float(np.clip(alpha, 0, 1))
    pos = alpha * (len(cores) - 1)
    i = min(int(pos), len(cores) - 2)
    frac = pos - i
    rgb = (1 - frac) * color_to_rgb(cores[i]) + frac * color_to_rgb(cores[i + 1])
    return rgb_to_color(rgb)


def mapa_de_calor(valores: np.ndarray, cores: list[ManimColor], vmin: float, vmax: float, lado: float = 0.2) -> VGroup:
    """Uma grade de quadrados, linha 0 no topo, coloridos pelo valor."""
    n_lin, n_col = valores.shape
    grade = VGroup()
    for i in range(n_lin):
        for j in range(n_col):
            pixel = Square(side_length=lado, stroke_width=0, fill_opacity=1)
            pixel.set_fill(cor_na_escala(cores, (valores[i, j] - vmin) / (vmax - vmin)))
            pixel.move_to(np.array([j * lado, -i * lado, 0]))
            grade.add(pixel)
    grade.center()
    return grade


def pausa(cena: Scene, segundos: float) -> None:
    """Espera que o manim-slides conta. No modo GL ele só conta play(), mas o
    ManimGL grava um vídeo parcial também para wait(): cada wait() deslocaria
    as fronteiras de todos os slides seguintes. Nunca usar self.wait() num Slide."""
    cena.play(Animation(Mobject()), run_time=segundos)


def fecha_passo(cena: Slide, notas: str) -> None:
    """Fecha o passo com a nota do que ele acabou de mostrar. O next_slide(notes=...)
    anota o slide que COMEÇA depois da chamada: chamado no fim do passo, deslocaria
    cada nota um slide adiante e perderia a última da cena. Usa o atributo privado
    _base_slide_config (manim-slides 5.7.0), que o próprio next_slide altera. O dedent
    é o que o next_slide faria: sem ele, linhas recuadas viram bloco de código no Markdown."""
    cena._base_slide_config.notes = dedent(notas)
    cena.next_slide()


# ------------------------------------------------------------------ o mapa
# Fig. 2 de Wagner et al.: objetos (azul) e processos (verde); o miolo, do
# complexo à redução, fica numa moldura. Volta em cada bloco como mapa.

COR_OBJETO = BLUE_C
COR_PROCESSO = GREEN_C
COR_MOLDURA = YELLOW_E

Fluxo = dict[str, VGroup | list[VGroup]]  # as partes do fluxo, por nome


def _icone_dados(lado: float) -> VGroup:
    valores = [[0.2, 0.7, 0.4, 0.9], [0.6, 0.1, 0.8, 0.3], [0.9, 0.5, 0.2, 0.6], [0.3, 0.8, 0.7, 0.1]]
    grade = VGroup()
    passo = lado / 4
    for i in range(4):
        for j in range(4):
            pixel = Square(side_length=passo, stroke_width=0, fill_opacity=1)
            pixel.set_fill(interpolate_color(GREY_E, WHITE, valores[i][j]))
            pixel.move_to(np.array([j * passo, -i * passo, 0]))
            grade.add(pixel)
    return grade.center()


def _icone_complexo(lado: float) -> VGroup:
    passo = lado / 2
    pontos = []
    for i in range(3):
        for j in range(3):
            pontos.append(np.array([j * passo, i * passo, 0]))
    grupo = VGroup()
    for i in range(2):
        for j in range(2):
            k = 3 * i + j
            q = Polygon(pontos[k], pontos[k + 1], pontos[k + 4], pontos[k + 3])
            grupo.add(q.set_fill(COR_QUADRADO, opacity=0.45).set_stroke(width=0))
    for i in range(3):
        grupo.add(Line(pontos[3 * i], pontos[3 * i + 2], stroke_color=COR_ARESTA, stroke_width=2.5))
        grupo.add(Line(pontos[i], pontos[6 + i], stroke_color=COR_ARESTA, stroke_width=2.5))
    for p in pontos:
        grupo.add(Dot(p, radius=0.045, fill_color=COR_VERTICE))
    return grupo.center()


def _icone_matriz(lado: float) -> VGroup:
    n = 6
    passo = lado / n
    cheias = {(0, 2), (1, 2), (1, 3), (3, 4), (0, 4), (2, 5), (4, 5)}
    grupo = VGroup()
    for i in range(n):
        for j in range(n):
            cheia = (i, j) in cheias
            ponto = Dot(np.array([j * passo, -i * passo, 0]), radius=0.05 if cheia else 0.025)
            ponto.set_fill(WHITE if cheia else GREY_D)
            grupo.add(ponto)
    return grupo.center()


def _icone_diagrama(lado: float) -> VGroup:
    origem = np.array([-lado / 2, -lado / 2, 0])
    eixos = VGroup(
        Line(origem, origem + lado * RIGHT, stroke_color=GREY_B, stroke_width=2),
        Line(origem, origem + lado * UP, stroke_color=GREY_B, stroke_width=2),
        DashedLine(origem, origem + lado * (RIGHT + UP), stroke_color=GREY_C, stroke_width=1.5),
    )
    pontos = VGroup(
        Dot(origem + lado * np.array([0.12, 0.25, 0]), radius=0.045, fill_color=COR_H0),
        Dot(origem + lado * np.array([0.35, 0.45, 0]), radius=0.045, fill_color=COR_H0),
        Dot(origem + lado * np.array([0.25, 0.85, 0]), radius=0.05, fill_color=COR_H1),
    )
    return VGroup(eixos, pontos)


def fluxo_persistencia(icone_dados: Mobject | None = None) -> Fluxo:
    """O fluxo da Fig. 2 estilizado. Devolve um dict com as partes, para destacar.

    icone_dados troca o ícone da caixa "dados" (por exemplo, pela imagem do bloco).
    """
    lado = 1.0
    objetos = []
    nomes_objetos = [("dados",), ("complexo",), ("matriz de bordo", "ordenada"), ("diagrama de", "persistência")]
    if icone_dados is None:
        icone_dados = _icone_dados(lado)
    icones = [icone_dados, _icone_complexo(lado), _icone_matriz(lado), _icone_diagrama(lado)]
    for icone, nome in zip(icones, nomes_objetos):
        caixa = RoundedRectangle(width=1.4, height=1.4, corner_radius=0.08)
        caixa.set_stroke(COR_OBJETO, width=2).set_fill(BLUE_E, opacity=0.25)
        icone.move_to(caixa)
        rotulo = VGroup()
        for linha in nome:
            rotulo.add(TexText(linha, font_size=22))
        rotulo.arrange(DOWN, buff=0.06).next_to(caixa, DOWN, buff=0.15)
        objetos.append(VGroup(caixa, icone, rotulo))

    processos = []
    nomes_processos = [("construir", "o complexo"), ("filtração e", "matriz de bordo"), ("redução", "da matriz")]
    for nome in nomes_processos:
        texto = VGroup()
        for linha in nome:
            texto.add(TexText(linha, font_size=22))
        texto.arrange(DOWN, buff=0.06)
        caixa = RoundedRectangle(width=1.75, height=0.95, corner_radius=0.3)
        caixa.set_stroke(COR_PROCESSO, width=2).set_fill(GREEN_E, opacity=0.25)
        processos.append(VGroup(caixa, texto.move_to(caixa)))

    sequencia = [objetos[0], processos[0], objetos[1], processos[1], objetos[2], processos[2], objetos[3]]
    caixas = VGroup()
    for item in sequencia:
        caixas.add(item[0])
    caixas.arrange(RIGHT, buff=0.42)  # move as próprias caixas; o conteúdo vem atrás
    for processo in processos:
        processo[1].move_to(processo[0])
    for objeto in objetos:
        objeto[1].move_to(objeto[0])
        objeto[2].next_to(objeto[0], DOWN, buff=0.15)

    setas = VGroup()
    for a, b in zip(sequencia[:-1], sequencia[1:]):
        setas.add(Arrow(a[0].get_right(), b[0].get_left(), buff=0.05, thickness=2.5, fill_color=GREY_B))

    miolo = VGroup(processos[0][0], objetos[1], processos[2][0])
    moldura = RoundedRectangle(width=miolo.get_width() + 0.5, height=2.75, corner_radius=0.25)
    moldura.move_to(miolo).shift(0.05 * DOWN)
    moldura.set_stroke(COR_MOLDURA, width=1.5).set_fill(COR_MOLDURA, opacity=0.06)
    rotulo_moldura = TexText("o fluxo da homologia persistente", font_size=22).set_color(COR_MOLDURA)
    rotulo_moldura.next_to(moldura.get_top(), DOWN, buff=0.12)

    tudo = VGroup(moldura, rotulo_moldura, setas, *sequencia)
    return {
        "tudo": tudo, "objetos": objetos, "processos": processos,
        "setas": setas, "moldura": VGroup(moldura, rotulo_moldura), "sequencia": sequencia,
    }


def apresenta_fluxo(cena: Scene, mapa: Fluxo) -> None:
    """A entrada do fluxo, igual em todas as aparições: tudo de uma vez, num fade.

    É a exceção à regra do texto escrito, por pedido: o fluxo é um mapa já conhecido.
    """
    cena.play(FadeIn(mapa["tudo"]), run_time=1.5)
