"""Bloco 5: leitura do diagrama de persistência.

Render: manim-slides render --GL bloco5.py LeituraDoDiagrama
O diagrama vem do GUDHI (dados_bloco5.py), conferido contra a nossa redução em verifica_bloco5.py.
Uma seta, um passo: cada fecha_passo fecha um passo, com a nota do que ele mostrou.

À esquerda, o barcode da imagem (como no fim da seção 4) e, no último passo, o código do GUDHI;
à direita, o diagrama: nascimento no eixo x, morte no eixo y, a diagonal e a linha do infinito.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from manimlib import *
from manim_slides import Slide

import dados_bloco5 as dados
from bloco2 import imagem_g
from bloco3 import entendimento, texto_a_esquerda
from estilo import *

if TYPE_CHECKING:
    from manimlib.typing import ManimColor

U = 0.085  # unidade do diagrama (por nível de cinza)
ORIGEM_D = np.array([1.3, -2.3, 0])  # o ponto (90, 90) do diagrama
INFINITO = 147  # altura da linha do infinito, em nível de cinza
X_ESQUERDA = -6.5  # borda esquerda dos textos do painel da esquerda


def pd(nasce: float, morre: float) -> np.ndarray:
    """Um ponto (nascimento, morte) no diagrama."""
    return ORIGEM_D + U * np.array([nasce - 90, morre - 90, 0])


def ponto(nasce: float, morre: float, cor: ManimColor, raio: float = 0.1) -> Dot:
    return Dot(pd(nasce, morre), radius=raio, fill_color=cor)


class LeituraDoDiagrama(Slide):
    """Do barcode ao diagrama de persistência, como lê-lo, e o mesmo resultado em três linhas de GUDHI."""

    def construct(self) -> None:
        self.entrada()
        self.barras_viram_pontos()
        self.a_diagonal()
        self.como_ler()
        self.na_pratica()

    def troca_linha(self, texto: str, run_time: float = 2) -> None:
        nova = entendimento(texto)
        if self.linha is None:
            self.play(Write(nova), run_time=run_time)
        else:
            self.play(FadeOut(self.linha), Write(nova), run_time=run_time)
        self.linha = nova

    def troca_texto(self, *linhas: str) -> None:
        novo = VGroup()
        for k, linha in enumerate(linhas):
            novo.add(texto_a_esquerda(linha, -1.55 - 0.4 * k, x=X_ESQUERDA))
        if self.texto is None:
            self.play(Write(novo), run_time=2)
        else:
            self.play(FadeOut(self.texto), Write(novo), run_time=2)
        self.texto = novo

    # ---------------------------------------------------------- entrada
    def entrada(self) -> None:
        mapa = fluxo_persistencia(icone_dados=imagem_g(0.2))
        self.indice = indice_secao(6)
        self.play(Write(self.indice))
        apresenta_fluxo(self, mapa)
        diagrama = mapa["objetos"][3]
        realce = SurroundingRectangle(diagrama, buff=0.1).set_stroke(YELLOW, width=3)
        resto = VGroup(mapa["moldura"], mapa["setas"], *mapa["sequencia"][:6])
        self.play(ShowCreation(realce), resto.animate.set_opacity(0.2), run_time=2)
        pausa(self, 1.5)
        self.cabecalho = titulo("Leitura do diagrama")
        self.play(FadeOut(VGroup(resto, diagrama, realce)), run_time=1.2)
        self.play(Write(self.cabecalho))
        self.texto = None
        self.linha = None

    # ---------------------------------------------------------- 6.1 (do barcode ao diagrama)
    def barras_viram_pontos(self) -> None:
        # À esquerda, o barcode da imagem, como no fim do processo de filtração da seção 4.
        eixo_t = EixoNumerado((90, 140, 10), unit_size=0.08, font_size=20)
        eixo_t.shift(np.array([-6.0, -0.7, 0]) - eixo_t.n2p(90))
        barra_h0 = Line(np.array([eixo_t.n2p(94)[0], 0.5, 0]), np.array([eixo_t.n2p(146)[0], 0.5, 0]),
                        stroke_color=COR_H0, stroke_width=10)
        barra_h1 = Line(np.array([eixo_t.n2p(100)[0], -0.1, 0]), np.array([eixo_t.n2p(139)[0], -0.1, 0]),
                        stroke_color=COR_H1, stroke_width=10)
        nomes = VGroup(
            Tex("H_0", font_size=28).set_color(COR_H0).move_to([-6.55, 0.5, 0]),
            Tex("H_1", font_size=28).set_color(COR_H1).move_to([-6.55, -0.1, 0]),
            Tex(R"\infty", font_size=26).set_color(COR_H0).next_to(barra_h0, RIGHT, buff=0.1),
        )
        titulo_barcode = TexText("o barcode da imagem (seção 4)", font_size=28).move_to([-4.0, 1.35, 0])
        self.barcode = VGroup(eixo_t, barra_h0, barra_h1, nomes, titulo_barcode)

        # À direita, os eixos do diagrama.
        eixo_x = EixoNumerado((90, 140, 10), unit_size=U, font_size=22)
        eixo_x.shift(ORIGEM_D - eixo_x.n2p(90))
        eixo_y = EixoNumerado((90, 140, 10), unit_size=U, font_size=22, direcao=UP)
        eixo_y.rotate(PI / 2, about_point=eixo_y.n2p(90))
        eixo_y.shift(ORIGEM_D - eixo_y.n2p(90))
        for numero in eixo_y.numeros:
            numero.rotate(-PI / 2)
        nome_x = TexText("nascimento", font_size=26).next_to(eixo_x.reta, RIGHT, buff=0.25)
        nome_y = TexText("morte", font_size=26).rotate(PI / 2).next_to(eixo_y.numeros, LEFT, buff=0.2)
        diagonal = DashedLine(pd(90, 90), pd(INFINITO - 1, INFINITO - 1), stroke_color=GREY_B, stroke_width=2)
        linha_inf = DashedLine(pd(90, INFINITO), pd(INFINITO - 1, INFINITO), stroke_color=GREY_C, stroke_width=1.5)
        nome_inf = Tex(R"\infty", font_size=30).next_to(linha_inf, LEFT, buff=0.12)
        self.eixos = VGroup(eixo_x, eixo_y, nome_x, nome_y, diagonal, linha_inf, nome_inf)
        self.diagonal = diagonal

        self.play(FadeIn(self.barcode), run_time=1.5)
        self.troca_texto("cada barra vira um ponto:", "x = nascimento, y = morte")
        cria_eixo(self, eixo_x, tempo=2)
        cria_eixo(self, eixo_y, tempo=2)
        self.play(Write(nome_x), Write(nome_y), ShowCreation(diagonal), ShowCreation(linha_inf), Write(nome_inf))

        # H1: a barra de 100 a 139 vira o ponto (100, 139), com as guias até os eixos.
        p_h1 = ponto(100, 139, COR_H1)
        guias = VGroup(
            DashedLine(eixo_x.n2p(100), pd(100, 139), stroke_color=COR_H1, stroke_width=1.5),
            DashedLine(eixo_y.n2p(139), pd(100, 139), stroke_color=COR_H1, stroke_width=1.5),
        )
        rotulo_h1 = Tex("(100, 139)", font_size=26).set_color(COR_H1).next_to(p_h1, RIGHT, buff=0.15)
        self.play(Transform(barra_h1.copy(), p_h1), run_time=1.5)
        self.add(p_h1)
        self.play(ShowCreation(guias), Write(rotulo_h1))
        # H0: a barra que nunca termina vira um ponto na linha do infinito.
        p_h0 = ponto(94, INFINITO, COR_H0)
        rotulo_h0 = Tex(R"(94, \infty)", font_size=26).set_color(COR_H0).next_to(p_h0, DOWN + RIGHT, buff=0.1)
        self.play(Transform(barra_h0.copy(), p_h0), run_time=1.5)
        self.add(p_h0)
        self.play(Write(rotulo_h0))
        self.troca_linha("O diagrama de persistência: cada barra vira o ponto (nascimento, morte).")
        fecha_passo(self, """
            - O fluxo termina no diagrama de persistência. Ele carrega a mesma informação do barcode, em outra forma.
            - Cada barra vira um ponto: o eixo x é quando a feição nasce, e o eixo y é quando ela morre. A barra rosa, de 100 a 139, vira o ponto (100, 139).
            - A componente nunca morre: o ponto dela vai para uma linha especial no topo, a do infinito. É o (94, ∞).
            - Como a morte vem sempre depois do nascimento, todo ponto fica acima da diagonal tracejada.
        """)
        self.pontos = VGroup(p_h1, p_h0)
        self.rotulos = VGroup(rotulo_h1, rotulo_h0)
        self.guias = guias

    # ---------------------------------------------------------- 6.2 (a diagonal)
    def a_diagonal(self) -> None:
        valores = sorted({valor for _, valor in dados.pares_de_duracao_zero()})
        zero = VGroup(*[ponto(v, v, GREY_A, raio=0.07) for v in valores])
        rotulo = TexText("39 pares de duração zero", font_size=24).set_color(GREY_A)
        rotulo.next_to(pd(117, 117), DOWN + RIGHT, buff=0.15)
        n_h0 = sum(1 for dim, _ in dados.pares_de_duracao_zero() if dim == 0)
        n_h1 = len(dados.pares_de_duracao_zero()) - n_h0
        self.troca_texto("duração zero: nasce e morre no mesmo valor",
                         f"$H_0$ ({n_h0}): um vértice e a aresta que o liga ao resto",
                         f"$H_1$ ({n_h1}): um laço e o quadrado que o tapa")
        self.play(LaggedStartMap(GrowFromCenter, zero, lag_ratio=0.15), run_time=2)
        self.play(Write(rotulo))
        self.troca_linha("Células de mesmo valor entram juntas: o que uma cria, a outra desfaz.")
        fecha_passo(self, f"""
            - Lembra dos 39 pares de duração zero da filtração e da redução? Nascem e morrem no mesmo valor: a coordenada x é igual à y, e o ponto cai em cima da diagonal.
            - **O que eles representam:** no complexo cúbico, muitas células têm o mesmo valor (cada uma recebe o máximo dos seus vértices). Elas entram juntas, com a face antes da célula. Assim, uma célula pode criar uma feição que outra, do mesmo valor, desfaz no mesmo instante.
                - **{n_h0} em H₀:** um vértice entra e, no mesmo valor, entra a aresta que o liga a uma componente mais velha. Por exemplo, em 94: os vértices 94 vizinhos nascem juntos, e as arestas 94 entre eles os juntam na hora.
                - **{n_h1} em H₁:** arestas fecham um laço e, no mesmo valor, entra o quadrado que o tapa.
            - Eles não são forma da imagem: em nenhum valor t o conjunto {{f ≤ t}} mostra essas componentes ou esses laços. São efeito de quebrar a imagem em células. Por isso o GUDHI os omite por padrão.
            - Eles se empilham em poucos lugares: 94, 99, 100, 114, 115, 117, 119 e 139, os valores em que algo entra.
            - No barcode seriam barras de comprimento zero, por isso nem aparecem. No diagrama, ficam colados na diagonal.
        """)
        self.zero = VGroup(zero, rotulo)

    # ---------------------------------------------------------- 6.3 (como ler)
    def como_ler(self) -> None:
        distancia = DashedLine(pd(100, 139), pd(100, 100), stroke_color=YELLOW, stroke_width=3)
        rotulo_dist = Tex("139 - 100 = 39", font_size=26).set_color(YELLOW).next_to(pd(100, 130), RIGHT, buff=0.12)
        faixa = Polygon(pd(90, 90), pd(INFINITO - 1, INFINITO - 1), pd(INFINITO - 1, INFINITO - 7), pd(96, 90))
        faixa.set_fill(GREY_B, opacity=0.18).set_stroke(width=0)
        nome_ruido = TexText("perto da diagonal: ruído", font_size=24).set_color(GREY_A)
        nome_ruido.move_to(pd(124, 104))
        nome_forma = TexText("longe: forma", font_size=24).set_color(COR_H1).next_to(self.rotulos[0], DOWN, buff=0.15)
        nome_inf = TexText("nunca morre: uma peça só", font_size=22).set_color(COR_H0)
        nome_inf.next_to(self.rotulos[1], RIGHT, buff=0.25)
        fonte = rodape("Cohen-Steiner, Edelsbrunner e Harer (2007)")
        self.troca_texto("distância até a diagonal = persistência:", "quanto a feição dura")
        self.play(FadeOut(self.zero[1]), FadeOut(self.guias))
        self.play(ShowCreation(distancia), Write(rotulo_dist), run_time=1.5)
        self.play(FadeIn(faixa), Write(nome_ruido), run_time=1.5)
        self.play(Write(nome_forma), Write(nome_inf), Write(fonte))
        self.troca_linha("Longe da diagonal, a feição dura: é forma. Perto, morre logo: é ruído.")
        fecha_passo(self, """
            - A leitura de qualquer diagrama: a distância de um ponto até a diagonal é quanto a feição dura (a persistência). O anel dura 139 − 100 = 39.
            - Longe da diagonal: feição que dura, é a forma do dado. Colado na diagonal: nasce e morre quase junto, é ruído. A faixa cinza é só ilustrativa; onde cortar depende do problema.
            - O ponto no infinito: a componente que nunca morre. Uma por pedaço da imagem; aqui, uma só.
            - Por que dá para confiar nessa leitura: o teorema de estabilidade (Cohen-Steiner, Edelsbrunner e Harer, 2007). Se a imagem muda pouco (cada pixel muda no máximo ε), cada ponto do diagrama se move no máximo ε em cada coordenada, e os pontos novos que surgem duram no máximo 2ε: ficam colados na diagonal. Ruído pequeno não cria forma.
            - Em imagens reais, aparece uma nuvem de pontos colada na diagonal e poucos pontos longe dela. São esses que se leem.
        """)
        self.leitura = VGroup(distancia, rotulo_dist, faixa, nome_ruido, nome_forma, nome_inf)
        self.fonte = fonte

    # ---------------------------------------------------------- 6.4 (na prática: GUDHI)
    def na_pratica(self) -> None:
        linhas = VGroup()
        for linha in dados.CODIGO:
            linhas.add(TexText(R"\texttt{" + linha + "}", font_size=26))
        linhas.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        saida = TexText(R"\texttt{" + dados.SAIDA + "}", font_size=24).set_color(GREY_A)
        saida.next_to(linhas, DOWN, buff=0.4).align_to(linhas, LEFT)
        bloco = VGroup(linhas, saida)
        fundo = RoundedRectangle(width=bloco.get_width() + 0.5, height=bloco.get_height() + 0.5, corner_radius=0.12)
        fundo.set_stroke(GREY_D, width=1.5).set_fill(GREY_E, opacity=0.6)
        codigo = VGroup(fundo, bloco)
        bloco.move_to(fundo)
        codigo.move_to([-3.6, 0.6, 0])
        legenda = TexText(R"\texttt{imagem}: a matriz 5 $\times$ 5; \texttt{vertices}: pixel = vértice", font_size=22)
        legenda.set_color(GREY_B).next_to(codigo, DOWN, buff=0.2).align_to(codigo, LEFT)
        fonte = rodape("GUDHI 3.13 (gudhi.inria.fr)")
        self.play(FadeOut(self.barcode), FadeOut(self.texto), FadeOut(self.fonte), Write(fonte))
        self.texto = None
        self.play(FadeIn(fundo), LaggedStartMap(Write, linhas, lag_ratio=0.5), run_time=3)
        self.play(Write(legenda))
        self.play(Write(saida), run_time=2)
        self.play(*[Indicate(p, color=YELLOW, scale_factor=1.6) for p in self.pontos],
                  *[Indicate(r, color=YELLOW) for r in self.rotulos], run_time=1.5)
        self.troca_linha("Na prática, três linhas de código dão o mesmo diagrama que construímos.")
        fecha_passo(self, """
            - Na prática, ninguém monta a matriz à mão: usa uma biblioteca. Aqui, o GUDHI (versão 3.13), com a mesma imagem 5×5.
            - **Como extraímos o resultado:** `gudhi.CubicalComplex(vertices=imagem)` monta o complexo cúbico com cada pixel como vértice e cada célula com o máximo dos seus vértices: a construção de Wagner et al., a mesma da apresentação. São as mesmas 81 células.
            - `complexo.persistence()` faz a redução e devolve os pares (dimensão, (nascimento, morte)): `[(1, (100.0, 139.0)), (0, (94.0, inf))]`. É o diagrama da direita.
            - Por padrão, ele só devolve pares com duração maior que zero. Com `persistence(min_persistence=-1)`, devolve todos: 41 pares, 39 de duração zero, exatamente os da nossa redução.
            - Por padrão, o GUDHI calcula com coeficientes em ℤ₁₁, e não em ℤ₂. Para imagens 2D e 3D isso não muda nada; conferimos que dá o mesmo diagrama.
            - A outra opção, `CubicalComplex(top_dimensional_cells=imagem)`, usa cada pixel como quadrado (a construção T de Dlotko e Wanner): 121 células e, nesta imagem, os mesmos pares que duram.
            - Tudo isso está conferido no script `verifica_bloco5.py`: o GUDHI contra a nossa redução, par a par.
            - Outras ferramentas para imagens e volumes: o Cubical Ripser (Kaji, Sudo e Ahara, 2020).
        """)
