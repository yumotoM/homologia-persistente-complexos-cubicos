"""Bloco 1: abertura, a TDA numa frase e o formato do dado.

Render: manim-slides render --GL bloco1.py Abertura FluxoEFormato
Imagens: prepara_imagens.py. Conferência: verifica_bloco1.py.
"""
from __future__ import annotations

from pathlib import Path

from manimlib import *
from manim_slides import Slide

from estilo import *

ASSETS = Path(__file__).parent / "assets"
CREDITO_FOTO = "Foto: Joselodos, CC0, Wikimedia Commons"
LADO_IMAGEM = 512  # o mesmo LADO de prepara_imagens.py



def imagem(nome: str, altura: float) -> ImageMobject:
    return ImageMobject(str(ASSETS / nome), height=altura)


def surge_de(img: ImageMobject, origem: Mobject) -> Restore:
    """Animação de img nascendo da posição e do tamanho de origem.

    FadeTransform monta um VGroup por dentro e não aceita ImageMobject.
    """
    img.save_state()
    img.replace(origem)
    img.set_opacity(0)
    return Restore(img)


def moldura(img: Mobject) -> SurroundingRectangle:
    return SurroundingRectangle(img, buff=0).set_stroke(GREY_B, width=1.5)


class Abertura(Slide):
    """Telas 1 e 2: capa e sumário."""

    def construct(self) -> None:
        capa = TexText("Complexos Cúbicos", font_size=96)
        disciplina = TexText("SME0231 - Análise Topológica de Dados", font_size=40).set_color(GREY_A)
        VGroup(capa, disciplina).arrange(DOWN, buff=0.5).move_to(ORIGIN)
        self.play(Write(capa), run_time=2)
        self.play(Write(disciplina), run_time=1.5)
        fecha_passo(self, "Capa.")

        cabecalho = titulo("Sumário")
        itens = VGroup()
        for k, item in enumerate(SUMARIO, start=1):
            itens.add(TexText(f"{k}.\\quad {item}", font_size=44))
        itens.arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        itens.move_to(DOWN * 0.35)
        self.play(FadeOut(VGroup(capa, disciplina), shift=0.5 * UP))
        self.play(Write(cabecalho))
        self.play(LaggedStartMap(Write, itens, lag_ratio=0.3, run_time=4))
        fecha_passo(self, "Sumário.")


class FluxoEFormato(Slide):
    """Telas 3 e 4: a TDA numa frase com o fluxo da persistência, e o formato do dado."""

    def construct(self) -> None:
        # Tela 3: a frase.
        frase = VGroup(
            TexText("Dados têm forma.", font_size=52),
            TexText("A TDA é a matemática que mede essa forma, de modo quantitativo e robusto.", font_size=34),
        )
        frase.arrange(DOWN, buff=0.35).move_to(UP * 2.0)
        indice = indice_secao(1)
        self.play(Write(indice))
        self.play(Write(frase[0]))
        self.play(Write(frase[1]), run_time=2.5)
        fecha_passo(self, "TDA numa frase.")

        # Tela 3: o fluxo da Fig. 2, montado da esquerda para a direita.
        mapa = fluxo_persistencia()
        mapa["tudo"].move_to(DOWN * 1.0)
        apresenta_fluxo(self, mapa)
        fonte_fluxo = rodape("Wagner, Chen e Vuçini (2011), Fig. 2")
        self.play(Write(fonte_fluxo))
        fecha_passo(self, "O fluxo do artigo: dos dados ao diagrama. Objetos em azul, processos em verde.")

        # Transição: o fluxo começa nos dados, e é por eles que entramos.
        dados = mapa["objetos"][0]
        destaque = SurroundingRectangle(dados[0], buff=0.08).set_stroke(YELLOW, width=3)
        outros = VGroup(mapa["moldura"], mapa["setas"], *mapa["sequencia"][1:])
        self.play(ShowCreation(destaque), outros.animate.set_opacity(0.2), frase.animate.set_opacity(0.2))

        foto = imagem("cachorro_rgb.png", 3.3).move_to(np.array([-4.55, 0.25, 0]))
        cabecalho = titulo("O formato do dado em complexos cúbicos")
        nasce_foto = surge_de(foto, dados[1])
        self.play(
            FadeOut(VGroup(frase, outros, destaque, dados[0], dados[2], fonte_fluxo, indice)),
            dados[1].animate.replace(foto.saved_state).set_opacity(0),
            nasce_foto,
            run_time=1.5,
        )
        self.remove(dados[1])
        borda_foto = moldura(foto)
        credito = TexText(CREDITO_FOTO, font_size=20).set_color(GREY_B)
        credito.next_to(borda_foto, DOWN, buff=0.08).align_to(borda_foto, LEFT)
        self.play(Write(indice_secao(2)), Write(cabecalho), ShowCreation(borda_foto), Write(credito))

        # Tela 4, passo 1: a imagem são três números por pixel.
        canais = Group()
        for nome in "bgr":  # B atrás, R na frente
            canais.add(imagem(f"cachorro_canal_{nome}.png", 3.3).move_to(foto))
        deslocamentos = [0.9 * RIGHT + 0.7 * UP, 0.45 * RIGHT + 0.35 * UP, ORIGIN]
        rotulos_canais = VGroup()
        for canal, letra, desl in zip(canais, "BGR", deslocamentos):
            rotulo = Tex(letra, font_size=30).move_to(canal.get_corner(UR) + desl + 0.2 * (UP + RIGHT))
            rotulos_canais.add(rotulo)
        self.add(canais)
        self.bring_to_front(foto, borda_foto)
        deslocar = []
        for canal, desl in zip(canais, deslocamentos):
            deslocar.append(canal.animate.shift(desl))
        self.play(FadeOut(foto), FadeOut(borda_foto), *deslocar, run_time=1.5)
        self.play(Write(rotulos_canais))
        rotulo_i = Tex(R"I : \text{pixels} \to \mathbb{R}^3", font_size=40)
        dimensao = Tex(Rf"H \times W \times 3 = {LADO_IMAGEM} \times {LADO_IMAGEM} \times 3", font_size=30)
        dimensao.set_color(GREY_B)
        VGroup(rotulo_i, dimensao).arrange(DOWN, buff=0.18).next_to(credito, DOWN, buff=0.3)
        VGroup(rotulo_i, dimensao).set_x(borda_foto.get_x())
        self.play(Write(rotulo_i))
        self.play(Write(dimensao))
        voltar = []
        for canal, desl in zip(canais, deslocamentos):
            voltar.append(canal.animate.shift(-desl))
        self.play(FadeOut(rotulos_canais), *voltar, run_time=1.2)
        self.play(FadeIn(foto), FadeIn(borda_foto))
        self.remove(canais)
        fecha_passo(self, "Uma foto RGB é uma função dos pixels em R^3: três números por pixel.")

        # Passo 2: escala de cinza, uma conta pixel a pixel.
        cinza = imagem("cachorro_cinza.png", 2.15).move_to(np.array([0.1, 1.3, 0]))
        borda_cinza = moldura(cinza)
        rotulo_cinza = TexText("escala de cinza", font_size=30).next_to(cinza, UP, buff=0.15)
        seta_cinza = Arrow(borda_foto.get_right() + 0.4 * UP, borda_cinza.get_left(), buff=0.15,
                           thickness=3, fill_color=GREY_B)
        formulas_cinza = VGroup(
            Tex(R"f = \varphi \circ I", font_size=40),
            Tex(R"\varphi(R, G, B) = 0.299R + 0.587G + 0.114B", font_size=26),
            TexText("pontual: pixel a pixel", font_size=26).set_color(GREY_B),
        )
        formulas_cinza.arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(borda_cinza, RIGHT, buff=0.45)
        self.play(GrowArrow(seta_cinza), surge_de(cinza, foto), run_time=1.5)
        self.play(ShowCreation(borda_cinza), Write(rotulo_cinza))
        self.play(Write(formulas_cinza[0]))
        self.play(Write(formulas_cinza[1:]), run_time=2)
        fecha_passo(self, "Escala de cinza: a mesma conta em cada pixel, de R^3 em R.")

        # Passo 3: probabilidade, que olha a vizinhança.
        prob = imagem("cachorro_prob.png", 2.15).move_to(np.array([0.1, -1.75, 0]))
        borda_prob = moldura(prob)
        rotulo_prob = TexText("probabilidade de ``cachorro''", font_size=30).next_to(prob, UP, buff=0.15)
        seta_prob = Arrow(borda_foto.get_right() + 0.4 * DOWN, borda_prob.get_left(), buff=0.15,
                          thickness=3, fill_color=GREY_B)
        formulas_prob = VGroup(
            Tex(R"f = F(I)", font_size=40),
            Tex(R"F : \mathbb{R}^{H \times W \times 3} \to [0, 1]^{H \times W}", font_size=26),
            TexText("cada pixel depende da vizinhança", font_size=26).set_color(GREY_B),
            TexText("(mapa ilustrativo)", font_size=22).set_color(GREY_C),
        )
        formulas_prob.arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(borda_prob, RIGHT, buff=0.45)
        self.play(GrowArrow(seta_prob), surge_de(prob, foto), run_time=1.5)
        self.play(ShowCreation(borda_prob), Write(rotulo_prob))
        self.play(Write(formulas_prob[0]))
        self.play(Write(formulas_prob[1:]), run_time=2)
        fecha_passo(self, "Probabilidade de um modelo: a imagem inteira entra, sai um número por pixel. Mapa ilustrativo.")

        # Passo 4: o que a persistência precisa.
        conclusao = TexText(R"Nos dois casos, $f : \text{pixels} \to \mathbb{R}$: um número por pixel.", font_size=34)
        conclusao.set_color(YELLOW).to_edge(DOWN, buff=0.3)
        self.play(Write(conclusao))
        fecha_passo(self, """
            É esse número por pixel que a filtração usa. A escolha de f define a pergunta topológica.

            Exemplos com índices espectrais, que resultam em uma única saída por pixel, são especialmente interessantes:

            - índices espectrais referentes aos comprimentos de onda da luz visível, no caso de imagens RGB (extrapolação do verde, corpos de água);
            - aplicações para imagens multiespectrais.
        """)
