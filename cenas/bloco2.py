"""Bloco 2: construção do complexo cúbico.

Render: manim-slides render --GL bloco2.py ConstrucaoDoComplexo
Os números vêm de dados_bloco2.py e são conferidos por verifica_bloco2.py.
Uma seta, um passo: cada fecha_passo fecha um passo, com a nota do que ele mostrou.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from manimlib import *
from manim_slides import Slide

import dados_bloco2 as dados
from estilo import *

if TYPE_CHECKING:
    from manimlib.typing import ManimColor

UNIDADE = 1.0
ORIGEM = np.array([-5.3, -1.8, 0])  # o ponto (0, 0) da grade de G na tela
X_PAINEL = 3.6  # centro da coluna de explicação, à direita
X_TABELA = 0.7  # borda esquerda das linhas de tabela da coluna
Y_ENTENDIMENTO = -3.45  # a linha de entendimento, embaixo
CINZA_G = (90, 140)  # faixa de cinza para G: 94 quase preto e 139 branco, como em Otter et al.


def p(x: float, y: float, z: float = 0.0) -> np.ndarray:
    return ORIGEM + UNIDADE * np.array([x, y, z], dtype=float)


def celula(cubo: dados.Cubo) -> VMobject:
    """Desenha um cubo elementar do plano, na cor da sua dimensão."""
    (x0, x1), (y0, y1) = cubo
    dim = dados.dimensao(cubo)
    if dim == 0:
        return Dot(p(x0, y0), radius=0.09, fill_color=COR_VERTICE)
    if dim == 1:
        return Line(p(x0, y0), p(x1, y1), stroke_color=COR_ARESTA, stroke_width=6)
    quadrado = Polygon(p(x0, y0), p(x1, y0), p(x1, y1), p(x0, y1))
    return quadrado.set_fill(COR_QUADRADO, opacity=0.45).set_stroke(width=0)


def imagem_g(lado: float) -> VGroup:
    return mapa_de_calor(dados.G, [BLACK, WHITE], *CINZA_G, lado=lado)


def complexo_de_g() -> dict[int, VGroup]:
    """Quadrados, arestas e vértices de G, nessa ordem de camadas."""
    por_dim = dados.complexo_da_grade(dados.N)
    camadas = {}
    for dim in (2, 1, 0):
        grupo = VGroup()
        for cubo in por_dim[dim]:
            grupo.add(celula(cubo))
        camadas[dim] = grupo
    return camadas


def valores_nos_pixels(imagem: VGroup) -> VGroup:
    """O valor de cinza escrito em cada pixel, em preto nos claros e em branco nos escuros."""
    numeros = VGroup()
    for k, pixel in enumerate(imagem):
        valor = int(dados.G.flat[k])
        claro = (valor - CINZA_G[0]) / (CINZA_G[1] - CINZA_G[0]) > 0.5
        numero = Tex(str(valor), font_size=20).set_color(BLACK if claro else WHITE).move_to(pixel)
        numeros.add(numero)
    return numeros


def celulas_explodidas(cubos: list[dados.Cubo], centro: np.ndarray, t: float) -> VGroup:
    """Cada cubo encolhido no próprio centro, como na Fig. 3(b) de Wagner et al.

    Vértice: quadradinho; aresta: barra na direção dela; quadrado: quadrado menor.
    O centro de cada um é a sua casa (x0 + x1, y0 + y1) do array de lado t.
    """
    grupo = VGroup()
    for cubo in cubos:
        (x0, x1), (y0, y1) = cubo
        dim = dados.dimensao(cubo)
        largura = 1.3 * t if x0 != x1 else 0.45 * t
        altura = 1.3 * t if y0 != y1 else 0.45 * t
        forma = Rectangle(width=largura, height=altura).set_stroke(width=0)
        forma.set_fill(cor_da_dimensao(dim), opacity=0.9)
        forma.move_to(centro + t * np.array([x0 + x1 - 4, y0 + y1 - 4, 0]))
        grupo.add(forma)
    return grupo


def ladrilhos_cubemap(cubos: list[dados.Cubo], centro: np.ndarray, lado_ladrilho: float) -> VGroup:
    """Um ladrilho por cubo, na posição (x0 + x1, y0 + y1) do array: [k,k] vira 2k e [k,k+1] vira 2k+1."""
    ladrilhos = VGroup()
    for cubo in cubos:
        (x0, x1), (y0, y1) = cubo
        i, j = x0 + x1, y0 + y1
        ladrilho = Square(side_length=0.88 * lado_ladrilho).set_stroke(width=0)
        ladrilho.set_fill(cor_da_dimensao(dados.dimensao(cubo)), opacity=0.9)
        ladrilho.move_to(centro + lado_ladrilho * np.array([i - 4, j - 4, 0]))
        ladrilhos.add(ladrilho)
    return ladrilhos


def coluna(cabeca: str, linhas: list[str], formula: str | None = None, tamanho_formula: float = 36) -> VGroup:
    """A coluna de explicação, à direita: cabeçalho, o sentido em poucas linhas e a fórmula."""
    grupo = VGroup(TexText(cabeca, font_size=40))
    sentido = VGroup()
    for linha in linhas:
        sentido.add(TexText(linha, font_size=30))
    grupo.add(sentido.arrange(DOWN, buff=0.12))
    if formula is not None:
        grupo.add(Tex(formula, font_size=tamanho_formula))
    grupo.arrange(DOWN, buff=0.35)
    grupo.move_to([X_PAINEL, 2.4 - grupo.get_height() / 2, 0])
    return grupo


def escreve(cena: Scene, grupo: VGroup) -> None:
    """Escreve a coluna aos poucos: cabeçalho, sentido, fórmula."""
    cena.play(Write(grupo[0]))
    cena.play(Write(grupo[1]), run_time=1.2 + 0.6 * len(grupo[1]))
    if len(grupo) > 2:
        cena.play(Write(grupo[2]), run_time=1.5)


def icone_dimensao(dim: int) -> VMobject:
    if dim == 0:
        return Dot(radius=0.1, fill_color=COR_VERTICE)
    if dim == 1:
        return Line(LEFT * 0.22, RIGHT * 0.22, stroke_color=COR_ARESTA, stroke_width=6)
    return Square(side_length=0.34).set_fill(cor_da_dimensao(dim), opacity=0.6).set_stroke(width=0)


def linha_tabela(icone: VMobject, tex_esquerda: str, texto_direita: str, cor: ManimColor, y: float, x_direita: float | None = None) -> VGroup:
    """Uma linha da coluna: ícone, expressão em Tex e descrição na cor da dimensão, em colunas fixas.

    x_direita fixa onde começa a descrição; sem ele, a descrição fica numa coluna larga, para produtos.
    """
    icone.move_to([X_TABELA + 0.2, y, 0])
    esquerda = Tex(tex_esquerda, font_size=32)
    esquerda.move_to([X_TABELA + 0.6 + esquerda.get_width() / 2, y, 0])
    linha = VGroup(icone, esquerda)
    if texto_direita:
        direita = TexText(texto_direita, font_size=28).set_color(cor)
        if x_direita is None:
            x_direita = max(X_TABELA + 3.5, esquerda.get_right()[0] + 0.4)
        direita.move_to([x_direita + direita.get_width() / 2, y, 0])
        linha.add(direita)
    return linha


def tex_produto(cubo: dados.Cubo) -> str:
    return R" \times ".join(tex_intervalo(a, b) for a, b in cubo)


def aparece(mob: VMobject) -> Animation:
    """A animação de entrada de uma célula, conforme o tipo."""
    if isinstance(mob, Dot):
        return GrowFromCenter(mob)
    if isinstance(mob, Line):
        return ShowCreation(mob)
    return FadeIn(mob)


def mini_quadrado(centro: np.ndarray, lado: float, falta: str | None = None) -> VGroup:
    """Um quadrado com as faces; falta = "aresta" tira a de cima, "vertice" tira o canto superior direito."""
    meio = lado / 2
    cantos = [centro + np.array([sx * meio, sy * meio, 0]) for sx, sy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
    preenchimento = Polygon(*cantos).set_fill(COR_QUADRADO, opacity=0.45).set_stroke(width=0)
    arestas = VGroup()
    for k in range(4):
        a, b = cantos[k], cantos[(k + 1) % 4]
        if falta == "aresta" and k == 2:
            continue
        arestas.add(Line(a, b, stroke_color=COR_ARESTA, stroke_width=6))
    vertices = VGroup()
    for k, c in enumerate(cantos):
        if falta == "vertice" and k == 2:
            continue
        vertices.add(Dot(c, radius=0.1, fill_color=COR_VERTICE))
    figura = VGroup(preenchimento, arestas, vertices)
    if falta == "aresta":
        figura.add(DashedLine(cantos[2], cantos[3], stroke_color=RED, stroke_width=6, dash_length=0.1))
    if falta == "vertice":
        figura.add(Circle(radius=0.17, stroke_color=RED, stroke_width=5).move_to(cantos[2]))
    return figura


def legenda_celulas() -> VGroup:
    """Chave de leitura das cores: o tipo de cada célula, numa linha."""
    itens = [
        (Dot(radius=0.1, fill_color=COR_VERTICE), "vértice"),
        (Line(LEFT * 0.22, RIGHT * 0.22, stroke_color=COR_ARESTA, stroke_width=6), "aresta"),
        (Square(side_length=0.34).set_fill(COR_QUADRADO, opacity=0.6).set_stroke(width=0), "quadrado"),
    ]
    legenda = VGroup()
    for icone, texto in itens:
        legenda.add(VGroup(icone, TexText(texto, font_size=28)).arrange(RIGHT, buff=0.2))
    return legenda.arrange(RIGHT, buff=0.8)


def intervalo_na_reta(reta: EixoNumerado, a: int, b: int, deslocamento: float = 0.0) -> VMobject:
    """[a, b] na reta numérica: ponto amarelo se degenerado, segmento azul se não."""
    if a == b:
        return Dot(reta.n2p(a) + deslocamento * UP, radius=0.1, fill_color=COR_VERTICE)
    return Line(reta.n2p(a) + deslocamento * UP, reta.n2p(b) + deslocamento * UP,
                stroke_color=COR_ARESTA, stroke_width=8)


def tex_intervalo(a: int, b: int) -> str:
    return f"[{a},{b}]" if a != b else f"[{a}]"


class ConstrucaoDoComplexo(Slide):
    """Do fluxo à construção do complexo de G, e a matemática que a justifica."""

    def construct(self) -> None:
        self.entrada()
        reta = self.intervalos()
        eixo_x, eixo_y, rede = self.produtos(reta)
        self.voxel()
        self.faces(eixo_x, eixo_y)
        self.bordo_em_z2()
        self.fechado_por_faces(eixo_x, eixo_y, rede)
        self.construcao_por_dimensao()
        self.generalizacao()

    # ---------------------------------------------------------- tela 5
    def entrada(self) -> None:
        mapa = fluxo_persistencia(icone_dados=imagem_g(0.2))
        self.indice = indice_secao(3)
        self.play(Write(self.indice))
        apresenta_fluxo(self, mapa)
        processo = mapa["processos"][0]
        icone = mapa["objetos"][0][1]
        destaque = SurroundingRectangle(processo[0], buff=0.08).set_stroke(YELLOW, width=3)
        resto = VGroup(mapa["moldura"], mapa["setas"], mapa["objetos"][0][0], mapa["objetos"][0][2],
                       *mapa["sequencia"][2:])
        self.play(ShowCreation(destaque), resto.animate.set_opacity(0.2))
        self.play(icone.animate.move_to(processo[0]).scale(0.8), run_time=1.2)

        cabecalho = titulo("Construção do complexo cúbico")
        lado = 0.66
        centros = [np.array([-4.6, 0.45, 0]), np.array([0.0, 0.45, 0]), np.array([4.6, 0.45, 0])]
        imagem = imagem_g(lado).move_to(centros[0])
        self.play(
            FadeOut(VGroup(resto, processo, destaque)),
            ReplacementTransform(icone, imagem),
            run_time=1.5,
        )
        self.play(Write(cabecalho))
        self.cabecalho = cabecalho

        # Clique 1: a imagem com o valor de cada pixel.
        valores = valores_nos_pixels(imagem)
        legendas = [
            Tex(R"\text{imagem } 5 \times 5", font_size=32),
            TexText("complexo cúbico", font_size=32),
            Tex(R"\text{CubeMap } 9 \times 9", font_size=32),
        ]
        for legenda, centro in zip(legendas, centros):
            legenda.move_to(centro + DOWN * 2.15)
        fonte = rodape("Otter et al. (2017), Fig. 2; Wagner et al. (2011), Fig. 3")
        self.play(LaggedStartMap(Write, valores, lag_ratio=0.03), run_time=2)
        self.play(Write(legendas[0]), Write(fonte))
        fecha_passo(self, """
            Nesta seção, trataremos da matemática topológica fundamental para entender o que é um CubeMap.

            A imagem 5x5 de Otter et al., com o valor de cinza de cada pixel. Escolhida porque a homologia é fácil de ver: um anel escuro em volta de um centro claro.
        """)

        # Clique 2: a mesma imagem com o complexo cúbico por cima; cada tipo entra com a sua legenda.
        seta1 = Arrow(centros[0] + 1.85 * RIGHT, centros[1] + 1.85 * LEFT, buff=0.1, thickness=3, fill_color=GREY_B)
        imagem2 = imagem_g(lado).move_to(centros[1]).set_opacity(0.6)
        camadas = complexo_de_g()
        complexo = VGroup(camadas[2], camadas[1], camadas[0])
        complexo.scale(lado / UNIDADE).move_to(centros[1])
        camadas[1].set_stroke(width=4)
        chave = legenda_celulas().move_to(DOWN * 2.35)
        self.play(GrowArrow(seta1), TransformFromCopy(imagem, imagem2), run_time=1.2)
        self.play(LaggedStartMap(GrowFromCenter, camadas[0], lag_ratio=0.03), Write(chave[0]))
        self.play(LaggedStartMap(ShowCreation, camadas[1], lag_ratio=0.03), Write(chave[1]), run_time=1.5)
        self.play(LaggedStartMap(FadeIn, camadas[2], lag_ratio=0.05), Write(chave[2]), run_time=1.5)
        self.play(Write(legendas[1]))
        fecha_passo(self, "Cada pixel vira um vértice; pixels vizinhos, uma aresta; blocos 2x2, um quadrado. É o complexo cúbico de G.")

        # Clique 3: o complexo "explode" sobre as casas do array (Wagner et al., Fig. 3b).
        # Na escala em que dois vértices vizinhos ficam a duas casas, cada célula já está
        # centrada na sua casa: só encolhe no lugar.
        seta2 = Arrow(centros[1] + 1.85 * RIGHT, centros[2] + 1.85 * LEFT, buff=0.1, thickness=3, fill_color=GREY_B)
        t = 3.3 / 9  # lado de uma casa do CubeMap
        casas = VGroup()
        for i in range(9):
            for j in range(9):
                casa = Square(side_length=t).set_stroke(GREY_D, width=1).set_fill(opacity=0)
                casas.add(casa.move_to(centros[2] + t * np.array([i - 4, j - 4, 0])))
        copia = complexo.copy()
        self.play(GrowArrow(seta2))
        self.play(copia.animate.scale(2 * t / lado).move_to(centros[2]), FadeIn(casas), run_time=2)
        por_dim = dados.complexo_da_grade(dados.N)
        explodido = {}
        for dim in (2, 1, 0):
            explodido[dim] = celulas_explodidas(por_dim[dim], centros[2], t)
        for dim in (2, 1, 0):  # quadrados, arestas, vértices: um tipo de cada vez
            camada = copia[2 - dim]
            self.play(LaggedStart(*[Transform(c, e) for c, e in zip(camada, explodido[dim])], lag_ratio=0.02),
                      run_time=1.6)
        fecha_passo(self, "Cada célula fica no seu próprio centro: vértices nas casas par-par, arestas nas mistas, quadrados nas ímpar-ímpar.")

        # Clique 4: todas viram casas iguais do array: o CubeMap (Fig. 3c).
        ladrilhos = VGroup()
        for dim in (2, 1, 0):
            ladrilhos.add(*ladrilhos_cubemap(por_dim[dim], centros[2], lado_ladrilho=t))
        explodidas = VGroup(*copia[0], *copia[1], *copia[2])
        entendimento = TexText("É sobre o CubeMap que a filtração será construída.", font_size=32)
        entendimento.move_to(DOWN * 3.0)
        self.play(LaggedStart(*[Transform(c, l) for c, l in zip(explodidas, ladrilhos)], lag_ratio=0.008),
                  FadeOut(casas), run_time=2.5)
        self.play(Write(legendas[2]))
        self.play(Write(entendimento))
        fecha_passo(self, "O mesmo complexo guardado num array 9x9: o CubeMap. É o resultado desta etapa, e é sobre ele que a filtração será construída.")
        self.play(FadeOut(VGroup(imagem, valores, imagem2, complexo, copia, seta1, seta2,
                                 *legendas, chave, entendimento, fonte)))

    # ---------------------------------------------------------- 7.1 (intervalos e bordo)
    def intervalos(self) -> EixoNumerado:
        reta = EixoNumerado((0, 4, 1), unit_size=1.25, font_size=30)
        reta.move_to(np.array([-3.7, 1.5, 0]))
        cria_eixo(self, reta)
        fecha_passo(self, "O eixo x da grade de G.")

        ponto = intervalo_na_reta(reta, 3, 3)
        r_ponto = Tex("[3,3]", font_size=38).set_color(COR_VERTICE).next_to(ponto, UP, buff=0.25)
        leg_ponto = VGroup(Dot(radius=0.1, fill_color=COR_VERTICE),
                           TexText("$[k,k]$: intervalo degenerado (um ponto)", font_size=28))
        leg_ponto.arrange(RIGHT, buff=0.3)
        leg_ponto.move_to(np.array([-3.7, 0.2, 0]))
        self.play(GrowFromCenter(ponto), Write(r_ponto))
        self.play(Write(leg_ponto))
        fecha_passo(self, "Um intervalo degenerado: um ponto inteiro.")

        segmento = intervalo_na_reta(reta, 1, 2)
        r_seg = Tex("[1,2]", font_size=38).set_color(COR_ARESTA).next_to(segmento, UP, buff=0.25)
        leg_seg = VGroup(Line(LEFT * 0.25, RIGHT * 0.25, stroke_color=COR_ARESTA, stroke_width=8),
                         TexText("$[k,k+1]$: intervalo não degenerado (um segmento)", font_size=28))
        leg_seg.arrange(RIGHT, buff=0.3)
        legendas = VGroup(leg_ponto, leg_seg)
        leg_seg.next_to(leg_ponto, DOWN, buff=0.3).align_to(leg_ponto, LEFT)
        self.play(ShowCreation(segmento), Write(r_seg))
        self.play(Write(leg_seg))
        fecha_passo(self, "Um intervalo não degenerado: um segmento de comprimento 1. Os dois são intervalos elementares.")

        cabeca = TexText("O bordo", font_size=40).move_to(np.array([3.6, 2.2, 0]))
        sentido = VGroup(
            TexText("o que delimita uma célula:", font_size=30),
            TexText("as células de uma dimensão abaixo", font_size=30),
            TexText("que a fecham", font_size=30),
        ).arrange(DOWN, buff=0.12).next_to(cabeca, DOWN, buff=0.35)
        definicao = VGroup(
            Tex(R"\operatorname{bdr}[a, a+1] = \{[a],\ [a+1]\}", font_size=36),
            Tex(R"\operatorname{bdr}[a, a] = \emptyset", font_size=36),
        ).arrange(DOWN, buff=0.25).next_to(sentido, DOWN, buff=0.45)
        self.play(Write(cabeca))
        self.play(Write(sentido), run_time=2)
        self.play(Write(definicao))
        fecha_passo(self, "O bordo é o que delimita a célula. Para um segmento, as duas pontas; um ponto não tem bordo.")

        pontas = VGroup(
            Dot(reta.n2p(1), radius=0.12, fill_color=COR_VERTICE),
            Dot(reta.n2p(2), radius=0.12, fill_color=COR_VERTICE),
        )
        exemplo_seg = Tex(R"\operatorname{bdr}[1,2] = \{[1],\ [2]\}", font_size=38)
        exemplo_ponto = VGroup(Tex(R"\operatorname{bdr}[3,3] = \emptyset", font_size=38),
                               TexText("caso degenerado", font_size=28).set_color(GREY_B)).arrange(RIGHT, buff=0.35)
        exemplos = VGroup(exemplo_seg, exemplo_ponto).arrange(RIGHT, buff=1.4).move_to(DOWN * 2.4)
        self.play(LaggedStartMap(GrowFromCenter, pontas, lag_ratio=0.4), Write(exemplo_seg))
        self.play(Indicate(ponto, color=WHITE), Write(exemplo_ponto))
        fecha_passo(self, "No exemplo: as faces de [1,2] são [1] e [2]; [3,3] é o caso degenerado, sem bordo.")
        self.play(FadeOut(VGroup(ponto, segmento, r_ponto, r_seg, legendas, cabeca, sentido, definicao,
                                 pontas, exemplos)))
        return reta

    # ---------------------------------------------------------- 7.3 (cubo elementar)
    def produtos(self, reta: EixoNumerado) -> tuple[EixoNumerado, EixoNumerado, VGroup]:
        eixo_x = EixoNumerado((0, 4, 1), unit_size=UNIDADE, font_size=26)
        eixo_x.shift(p(0, -0.7) - eixo_x.n2p(0))
        eixo_y = EixoNumerado((0, 4, 1), unit_size=UNIDADE, font_size=26, direcao=UP)
        eixo_y.rotate(PI / 2, about_point=eixo_y.n2p(0))
        eixo_y.shift(p(-0.7, 0) - eixo_y.n2p(0))
        for numero in eixo_y.numeros:
            numero.rotate(-PI / 2)
        rede = VGroup()
        for x in range(dados.N):
            for y in range(dados.N):
                rede.add(Dot(p(x, y), radius=0.035, fill_color=GREY_C))
        texto = coluna("Cubo elementar", ["um intervalo elementar em cada eixo,", "multiplicados"],
                       R"Q = I_1 \times I_2")
        self.play(ReplacementTransform(reta, eixo_x), run_time=2.5)
        cria_eixo(self, eixo_y)
        self.play(FadeIn(rede), run_time=1.5)
        escreve(self, texto)
        fecha_passo(self, "Cubo elementar: um intervalo elementar em cada eixo, multiplicados. A grade é a de G.")

        nomes = ["vértice", "aresta", "aresta", "quadrado"]
        notas = [
            "[1] x [2]: dois pontos dão um ponto, um vértice. Dimensão 0.",
            "[1,2] x [2]: um segmento e um ponto dão uma aresta horizontal. Dimensão 1.",
            "[1] x [2,3]: um ponto e um segmento dão uma aresta vertical. Dimensão 1.",
            "[1,2] x [2,3]: dois segmentos dão um quadrado. Dimensão 2: conta os fatores que são segmentos.",
        ]
        linhas = VGroup()
        celulas = VGroup()
        anterior = None
        y = texto.get_bottom()[1] - 0.55
        for cubo, nome, nota in zip(dados.EXEMPLOS_PRODUTO, nomes, notas):
            dim = dados.dimensao(cubo)
            grupo = self.produto_no_plano(eixo_x, eixo_y, cubo)
            linha = linha_tabela(icone_dimensao(dim), tex_produto(cubo), f"dim {dim}: {nome}", cor_da_dimensao(dim), y)
            y -= 0.55
            saem = []
            if anterior is not None:
                saem.append(FadeOut(VGroup(anterior[0], anterior[1], anterior[2])))
                saem.append(anterior[3].animate.set_opacity(0.3))
            self.play(*saem, ShowCreation(grupo[0]), FadeIn(grupo[1]), FadeIn(grupo[2]))
            self.play(aparece(grupo[3]), Write(linha))
            linhas.add(linha)
            celulas.add(grupo[3])
            anterior = grupo
            if dim == 2:
                regra = TexText("A dimensão de um cubo é o número de fatores que são segmentos.", font_size=30)
                regra.move_to(np.array([0, Y_ENTENDIMENTO, 0]))
                self.play(Write(regra))
            fecha_passo(self, nota)
        self.produto_atual = anterior
        self.celulas_produto = celulas
        self.coluna_produto = VGroup(texto, linhas)
        self.regra_dim = regra
        return eixo_x, eixo_y, rede

    def produto_no_plano(self, eixo_x: EixoNumerado, eixo_y: EixoNumerado, cubo: dados.Cubo) -> VGroup:
        """Guias, os dois fatores nas réguas (na cor da dimensão de cada um) e a célula."""
        (x0, x1), (y0, y1) = cubo
        guias = VGroup()
        for x in sorted({x0, x1}):
            guias.add(DashedLine(eixo_x.n2p(x), p(x, y1), stroke_color=GREY_B, stroke_width=1.5))
        for yy in sorted({y0, y1}):
            guias.add(DashedLine(eixo_y.n2p(yy), p(x1, yy), stroke_color=GREY_B, stroke_width=1.5))
        return VGroup(guias, intervalo_na_reta(eixo_x, x0, x1), intervalo_na_reta(eixo_y, y0, y1), celula(cubo))

    # ---------------------------------------------------------- 7.4 (voxel)
    def voxel(self) -> None:
        fixos = [self.indice, self.cabecalho, self.coluna_produto, self.regra_dim]
        for mob in fixos:
            mob.fix_in_frame()
        (x0, x1), (y0, y1), (z0, z1) = dados.VOXEL
        cubo = VCube(side_length=UNIDADE, fill_color=COR_VOXEL, fill_opacity=0.35)
        cubo.set_stroke(COR_VOXEL, width=2).move_to(p((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
        y = self.coluna_produto[1][-1].get_y() - 0.55
        linha = linha_tabela(icone_dimensao(3), R"[1,2] \times [2,3] \times [0,1]", "dim 3: voxel", COR_VOXEL, y)
        linha.fix_in_frame()
        geral = TexText(R"Em $d$ dimensões: $Q = I_1 \times \cdots \times I_d$", font_size=30)
        geral.move_to(np.array([0, Y_ENTENDIMENTO, 0])).fix_in_frame()
        centro = p(2, 2)
        self.play(self.frame.animate.reorient(-25, 55, 0, centro + 2.6 * RIGHT, 9.5), run_time=2.5)
        self.play(FadeIn(cubo), Write(linha))
        self.play(self.frame.animate.reorient(25, 60, 0, centro + 2.6 * RIGHT, 9.5), run_time=3)
        self.play(FadeOut(self.regra_dim))
        self.play(Write(geral))
        fecha_passo(self, "Em três dimensões, três intervalos: o voxel é o 3-cubo. A construção vale em qualquer dimensão.")
        self.voxel_cubo = cubo
        self.voxel_linha = linha
        self.voxel_geral = geral

    # ---------------------------------------------------------- 7.5 (bordo de um cubo)
    def faces(self, eixo_x: EixoNumerado, eixo_y: EixoNumerado) -> None:
        guias, fator_x, fator_y, quadrado = self.produto_atual
        self.play(
            self.frame.animate.reorient(0, 0, 0, ORIGIN, FRAME_HEIGHT),
            FadeOut(self.voxel_cubo),
            FadeOut(VGroup(self.coluna_produto, self.voxel_linha, self.voxel_geral, self.celulas_produto[:3])),
            run_time=2,
        )
        texto = coluna("Bordo de um cubo", ["troque um fator que é segmento", "por uma das suas pontas"],
                       R"\operatorname{bdr} Q = \bigcup_{i} Q_1 \times \cdots \times \operatorname{bdr} Q_i \times \cdots \times Q_d",
                       tamanho_formula=30)
        escreve(self, texto)
        fecha_passo(self, "O bordo de um cubo: troca-se um fator que é segmento por uma das suas pontas.")

        faces = dados.faces_primarias(dados.QUADRADO)
        direcoes = [LEFT, RIGHT, DOWN, UP]
        arestas = VGroup()
        rotulos = VGroup()
        linhas = VGroup()
        y = texto.get_bottom()[1] - 0.5
        for k, face in enumerate(faces):
            aresta = celula(face)
            arestas.add(aresta)
            rotulos.add(Tex(dados.NOMES_ARESTAS[k], font_size=32).set_color(COR_ARESTA)
                        .next_to(aresta, direcoes[k], buff=0.12))
            linhas.add(linha_tabela(icone_dimensao(1), rf"{dados.NOMES_ARESTAS[k]} = {tex_produto(face)}", "",
                                    COR_ARESTA, y))
            y -= 0.5
        notas = [
            "Trocando o fator x, o segmento [1,2] vira a ponta [1] ou a ponta [2]: as arestas verticais e1 e e2.",
            "Trocando o fator y, [2,3] vira [2] ou [3]: as arestas horizontais e3 e e4. São as quatro faces do quadrado.",
        ]
        for grupo_faces, fator, regua, nota in (((0, 1), fator_x, eixo_x, notas[0]), ((2, 3), fator_y, eixo_y, notas[1])):
            for k in grupo_faces:
                indice = 0 if k < 2 else 1
                ponta = faces[k][indice][0]
                encolhe = fator.copy()
                self.add(encolhe)
                self.play(Transform(encolhe, Dot(regua.n2p(ponta), radius=0.13, fill_color=COR_VERTICE)), run_time=1.2)
                self.play(ShowCreation(arestas[k]), Write(rotulos[k]), Write(linhas[k]), run_time=1.4)
                self.play(FadeOut(encolhe), run_time=0.4)
            fecha_passo(self, nota)

        vertices = VGroup()
        for v in dados.faces_primarias(faces[2]):
            vertices.add(celula(v).scale(1.3))
        linha_v = linha_tabela(icone_dimensao(0), R"\operatorname{bdr}\, e_3 = \{[1]\times[2],\ [2]\times[2]\}", "",
                               COR_VERTICE, y - 0.1)
        entendimento = TexText("Faces de faces também são faces: o bordo desce uma dimensão por vez.", font_size=30)
        entendimento.move_to(np.array([0, Y_ENTENDIMENTO, 0]))
        self.play(Indicate(arestas[2], color=WHITE), Write(linha_v))
        self.play(LaggedStartMap(GrowFromCenter, vertices, lag_ratio=0.4))
        self.play(Write(entendimento))
        fecha_passo(self, "A aresta e3 tem como faces os vértices [1]x[2] e [2]x[2]: faces de faces também são faces.")
        self.quadrado = quadrado
        self.quadrado_arestas = arestas
        self.quadrado_rotulos = rotulos
        self.quadrado_vertices = vertices
        self.coluna_faces = VGroup(texto, linhas, linha_v, entendimento, guias, fator_x, fator_y)

    # ---------------------------------------------------------- ∂ em Z2
    def bordo_em_z2(self) -> None:
        self.play(FadeOut(self.coluna_faces))
        vertices_topo = VGroup()
        for (x, y) in [(1, 3), (2, 3)]:
            vertices_topo.add(Dot(p(x, y), radius=0.117, fill_color=COR_VERTICE))
        nomes = VGroup()
        cantos = {}
        for (x, y), nome in dados.NOMES_VERTICES.items():
            direcao = normalize(np.array([x - 1.5, y - 2.5, 0]))
            nomes.add(Tex(nome, font_size=30).set_color(COR_VERTICE).move_to(p(x, y) + 0.4 * direcao))
            cantos[nome] = p(x, y) + 0.85 * direcao
        texto = coluna("O bordo como soma", [R"em $\mathbb{Z}_2$, cada face entra uma vez", R"e $1 + 1 = 0$"],
                       R"\partial Q = e_1 + e_2 + e_3 + e_4")
        self.play(FadeIn(vertices_topo))
        self.play(Write(nomes))
        escreve(self, texto)
        self.play(LaggedStart(*[Indicate(a, color=WHITE) for a in self.quadrado_arestas], lag_ratio=0.3))
        fecha_passo(self, "Em Z2, o bordo do quadrado é a soma das quatro arestas: é a coluna dele na matriz de bordo.")

        contadores = {}
        for nome, ponto in cantos.items():
            contadores[nome] = Integer(0, font_size=30).set_color(YELLOW).move_to(ponto)
        legenda = VGroup(Integer(2, font_size=28).set_color(YELLOW),
                         TexText("no canto: quantas vezes o vértice aparece", font_size=26).set_color(GREY_B))
        legenda.arrange(RIGHT, buff=0.25)
        legenda.next_to(texto, DOWN, buff=0.35).set_x(X_PAINEL)
        self.play(*[Write(n) for n in contadores.values()], Write(legenda))
        bordos = dados.bordo_das_arestas()
        y = legenda.get_bottom()[1] - 0.45
        vezes = {}
        linhas = VGroup()
        for k, (aresta, (a, b)) in enumerate(bordos.items()):
            linha = Tex(rf"\partial {aresta} = {a} + {b}", font_size=32).move_to([X_PAINEL, y, 0])
            y -= 0.45
            linhas.add(linha)
            atualiza = []
            for nome in (a, b):
                vezes[nome] = vezes.get(nome, 0) + 1
                atualiza.append(contadores[nome].animate.set_value(vezes[nome]))
            self.play(Indicate(self.quadrado_arestas[k], color=WHITE), Write(linha), *atualiza, run_time=1.2)
        final = Tex(R"\partial \partial Q = 2\,(v_1 + v_2 + v_3 + v_4) = 0", font_size=34).move_to([X_PAINEL, y - 0.1, 0])
        entendimento = TexText("Cada vértice aparece duas vezes: o bordo de um bordo é zero.", font_size=30)
        entendimento.move_to(np.array([0, Y_ENTENDIMENTO, 0]))
        self.play(Write(final))
        self.play(Write(entendimento))
        fecha_passo(self, """
            - Cada vértice aparece duas vezes em ∂∂Q; em ℤ₂, 2 = 0. É o ∂∂ = 0 que a turma conhece.
            - **O que é o bordo do bordo aqui:** o bordo do quadrado são as 4 arestas, que formam um laço fechado. O bordo desse laço são as pontas das arestas, e cada vértice é ponta de duas delas: aparece duas vezes e some (1 + 1 = 0). O laço não tem pontas soltas.
            - **A regra geral:** o bordo de qualquer coisa é sempre fechado. Todo bordo é um ciclo.
            - **Por que importa:** é o que torna a homologia possível. Como todo bordo é um ciclo, faz sentido perguntar quais ciclos não são bordo de nada, e esses são os buracos. H₁ é "ciclos, a menos dos que são bordo". Sem ∂∂ = 0, essa conta não fecha.
            - **Na imagem do exemplo:** em t = 100, o anel é um ciclo (cada vértice dele é ponta de duas arestas do anel) e não é bordo de nada que já entrou, porque não há quadrado dentro: é um buraco. Em t = 139, os 4 quadrados do miolo entram, e o anel passa a ser o bordo da soma deles: deixou de ser buraco, H₁ morre. A seção 5 mostra isso: somando as colunas dos 4 quadrados do miolo, sobra o anel.
        """)
        self.limpar_z2 = VGroup(texto, legenda, linhas, final, entendimento, nomes, vertices_topo,
                                *contadores.values(), self.quadrado, self.quadrado_arestas,
                                self.quadrado_rotulos, self.quadrado_vertices)

    # ---------------------------------------------------------- 7.6 (complexo cúbico)
    def fechado_por_faces(self, eixo_x: EixoNumerado, eixo_y: EixoNumerado, rede: VGroup) -> None:
        self.play(FadeOut(VGroup(self.limpar_z2, eixo_x, eixo_y, rede)))
        texto = coluna("Complexo cúbico", ["uma coleção de cubos que,", "com cada cubo, contém", "todas as suas faces"],
                       R"\tau \subseteq \sigma \in K \quad \Rightarrow \quad \tau \in K")
        variaveis = VGroup(
            TexText(R"$K$: o complexo, a coleção de cubos", font_size=26),
            TexText(R"$\sigma \in K$: um cubo que está em $K$", font_size=26),
            TexText(R"$\tau \subseteq \sigma$: $\tau$ é uma face de $\sigma$", font_size=26),
            TexText(R"$\Rightarrow$: então", font_size=26),
        ).set_color(GREY_A).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        variaveis.next_to(texto, DOWN, buff=0.4).set_x(X_PAINEL)
        escreve(self, texto)
        self.play(LaggedStartMap(Write, variaveis, lag_ratio=0.4), run_time=3)
        texto.add(variaveis)
        fecha_passo(self, """
            - Complexo cúbico: uma coleção de cubos que, junto com cada cubo, contém todas as suas faces.
            - Lendo a fórmula: se τ é face de algum cubo σ de K, então τ também está em K. "τ ⊆ σ ∈ K" abrevia "τ ⊆ σ e σ ∈ K".
            - Aqui ⊆ quer dizer "é face de": τ é um cubo da grade (vértice, aresta, quadrado), não um pedaço qualquer de σ.
            - Por que exigir: o bordo de σ é a soma das faces dele; se uma face falta, o bordo aponta para uma célula que não está no complexo.
        """)

        casos = [
            (None, R"\checkmark", GREEN, "todas as faces", "Com todas as faces: é um complexo."),
            ("aresta", R"\times", RED, "falta uma aresta", "Falta a aresta de cima, que é face do quadrado: não é complexo."),
            ("vertice", R"\times", RED, "falta um vértice", "Falta um vértice, face de duas arestas e do quadrado: não é complexo."),
        ]
        figuras = VGroup()
        for k, (falta, marca_tex, cor, legenda, nota) in enumerate(casos):
            centro = np.array([-5.55 + 2.3 * k, 0.2, 0])
            figura = mini_quadrado(centro, 1.5, falta)
            marca = Tex(marca_tex, font_size=60).set_color(cor).next_to(figura, UP, buff=0.35)
            rotulo = TexText(legenda, font_size=26).next_to(figura, DOWN, buff=0.4)
            self.play(FadeIn(figura[0]), ShowCreation(figura[1]), GrowFromCenter(figura[2]), run_time=1.2)
            if len(figura) > 3:
                self.play(ShowCreation(figura[3]))
            self.play(Write(marca), Write(rotulo))
            figuras.add(VGroup(figura, marca, rotulo))
            if falta == "vertice":
                entendimento = TexText("Sem uma face, a coleção não é um complexo.", font_size=30)
                entendimento.move_to(np.array([0, Y_ENTENDIMENTO, 0]))
                self.play(Write(entendimento))
            fecha_passo(self, nota)
        self.limpar_complexo = VGroup(texto, figuras, entendimento)

    # ---------------------------------------------------------- 7.7 (o complexo de G)
    def construcao_por_dimensao(self) -> None:
        self.play(FadeOut(self.limpar_complexo))
        camadas = complexo_de_g()
        texto = coluna("O complexo da imagem", ["montado dimensão a dimensão"])
        itens = [
            (0, "vértices: um por pixel", "Primeiro os 25 vértices, um por pixel."),
            (1, "arestas: pixels vizinhos", "Depois as 40 arestas, uma por par de pixels vizinhos."),
            (2, R"quadrados: blocos $2 \times 2$", "Por fim os 16 quadrados, um por bloco 2x2: tapam os buracos entre as arestas."),
        ]
        y = texto.get_bottom()[1] - 0.6
        linhas = VGroup()
        for dim, descricao, nota in itens:
            linha = linha_tabela(icone_dimensao(dim), str(len(camadas[dim])), descricao, cor_da_dimensao(dim), y,
                                 x_direita=X_TABELA + 1.5)
            y -= 0.6
            if dim == 0:
                escreve(self, texto)
                self.play(LaggedStartMap(GrowFromCenter, camadas[0], lag_ratio=0.04), Write(linha), run_time=2)
            elif dim == 1:
                self.play(LaggedStartMap(ShowCreation, camadas[1], lag_ratio=0.03), Write(linha), run_time=2.5)
            else:
                self.play(LaggedStartMap(FadeIn, camadas[2], lag_ratio=0.05), Write(linha), run_time=2.5)
            linhas.add(linha)
            fecha_passo(self, nota)
        euler = Tex(R"\chi = 25 - 40 + 16 = 1", font_size=38).move_to([X_PAINEL, y - 0.2, 0])
        betti = TexText(R"uma componente e nenhum buraco: $\beta_0 = 1$, $\beta_1 = 0$", font_size=28)
        betti.next_to(euler, DOWN, buff=0.25).set_x(X_PAINEL)
        entendimento = TexText("81 células: o complexo cúbico do início da seção.", font_size=30)
        entendimento.move_to(np.array([0, Y_ENTENDIMENTO, 0]))
        self.play(Write(euler))
        self.play(Write(betti))
        self.play(Write(entendimento))
        fecha_passo(self, """
            - Conferência: χ = 25 − 40 + 16 = 1, uma componente e nenhum buraco. É o complexo do primeiro slide.
            - **O que é essa conta:** χ é a característica de Euler, as células contadas com sinal alternado (vértices − arestas + quadrados; em 3D, ainda − cubos). Vale para qualquer complexo de células, cúbico ou simplicial.
            - É um invariante: não depende de como o espaço foi dividido em células. Por isso serve de conferência.
            - Ela liga a contagem à homologia (Euler–Poincaré): χ = β₀ − β₁ + β₂. Aqui 1 = 1 − 0 + 0: uma componente, nenhum buraco, como um quadrado cheio.
            - A mesma conta aparece na filtração (seção 4): em t = 100, o anel tem 8 vértices e 8 arestas, χ = 0 = 1 − 1, uma componente e um buraco.
        """)
        self.limpar_g = VGroup(camadas[2], camadas[1], camadas[0], texto, linhas, euler, betti, entendimento)

    # ---------------------------------------------------------- generalização
    def generalizacao(self) -> None:
        self.play(FadeOut(self.limpar_g))
        escala = 4.4 / 8
        origem = np.array([-6.3, -2.2, 0])

        def q(x: float, y: float) -> np.ndarray:
            return origem + escala * np.array([x, y, 0])

        retangulos = VGroup()
        for x0, x1, y0, y1 in dados.RETANGULOS_DW:
            r = Polygon(q(x0, y0), q(x1, y0), q(x1, y1), q(x0, y1))
            retangulos.add(r.set_fill(COR_QUADRADO, opacity=0.45).set_stroke(width=0))
        arestas = VGroup()
        for a, b in sorted(dados.arestas_dw()):
            arestas.add(Line(q(*a), q(*b), stroke_color=COR_ARESTA, stroke_width=3))
        vertices = VGroup()
        for v in sorted(dados.vertices_dw()):
            vertices.add(Dot(q(*v), radius=0.06, fill_color=COR_VERTICE))

        texto = coluna("Complexo CW retangular", ["qualquer subdivisão em retângulos,", "não só a grade unitária"])
        fonte = rodape("Dlotko e Wanner (2016), Fig. 2")
        y = texto.get_bottom()[1] - 0.6
        passos = [
            (0, vertices, "vértices", "Os 46 vértices da subdivisão de Dlotko e Wanner."),
            (1, arestas, "arestas", "As 70 arestas ligam vértices vizinhos ao longo das linhas da subdivisão."),
            (2, retangulos, "retângulos", """
                - Os 25 retângulos, de tamanhos diferentes, preenchem o quadrado: os cubos não precisam ser unitários.
                - O χ = 46 − 70 + 25 = 1 é a mesma conferência do complexo da imagem: o quadrado subdividido continua sendo uma peça só, sem buracos.
                - **Por que o CubeMap só vale na grade regular:** lá, todo quadrado tem 4 arestas e quem é face de quem sai de uma conta (±1 nas coordenadas). Numa subdivisão qualquer, o número de faces varia: quando o canto de dois retângulos vizinhos cai no meio do lado de um terceiro, esse lado se parte em duas arestas, e o retângulo fica com 5. Aí a incidência precisa ser guardada explicitamente (Dlotko e Wanner).
                - Para que serve: refinar a malha só onde a função varia muito, como em simulações numéricas; em sensoriamento remoto, o parente é o raster multirresolução (quadtree).
            """),
        ]
        linhas = VGroup()
        for dim, grupo, nome, nota in passos:
            linha = linha_tabela(icone_dimensao(dim), str(len(grupo)), nome, cor_da_dimensao(dim), y,
                                 x_direita=X_TABELA + 1.5)
            y -= 0.6
            if dim == 0:
                escreve(self, texto)
                self.play(LaggedStartMap(GrowFromCenter, vertices, lag_ratio=0.02), Write(linha), Write(fonte), run_time=2)
            elif dim == 1:
                self.play(LaggedStartMap(ShowCreation, arestas, lag_ratio=0.02), Write(linha), run_time=2.5)
            else:
                self.play(LaggedStartMap(FadeIn, retangulos, lag_ratio=0.04), Write(linha), run_time=2)
                self.bring_to_front(arestas, vertices)
                euler = Tex(R"\chi = 46 - 70 + 25 = 1", font_size=36).move_to([X_PAINEL, y - 0.1, 0])
                entendimento = TexText("Na grade regular, tudo isso cabe num CubeMap.", font_size=30)
                entendimento.move_to(np.array([0, Y_ENTENDIMENTO, 0]))
                self.play(Write(euler))
                self.play(Write(entendimento))
            linhas.add(linha)
            fecha_passo(self, nota)


def cor_da_dimensao(dim: int) -> ManimColor:
    return [COR_VERTICE, COR_ARESTA, COR_QUADRADO, COR_VOXEL][dim]
