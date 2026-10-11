"""Bloco 6: aplicação em satélite, a classificação de padrões de nuvens de Ver Hoef et al. (2023).

Render: manim-slides render --GL bloco6.py AplicacaoSatelite
Imagens e persistência preparadas por prepara_nuvens.py; números conferidos por verifica_bloco6.py.
Uma seta, um passo: cada fecha_passo fecha um passo, com a nota do que ele mostrou.

Seis telas: o dado, as classes e a motivação; os quatro padrões; um tile de flowers, da cor ao
diagrama; do diagrama à paisagem e ao vetor; sugar contra flowers; e a volta à primeira tela, para
a conclusão na fala. As nuvens são cenas MODIS reais (NASA Worldview), escolhidas pelo consenso de
4 ou mais especialistas nos rótulos de Rasp et al. (2020).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from manimlib import *
from manim_slides import Slide

import dados_bloco6 as dados
from bloco1 import surge_de
from bloco3 import entendimento
from estilo import *

if TYPE_CHECKING:
    from manimlib.typing import ManimColor

COR_PADRAO = {"sugar": YELLOW_C, "gravel": GREEN_C, "flower": RED_C, "fish": BLUE_C}  # como na Fig. 10 do artigo
ORDEM = ["sugar", "gravel", "flower", "fish"]
FONTE = "Ver Hoef et al. (2023); imagens: NASA Worldview; rótulos: Rasp et al. (2020)"
X_DIREITA = 0.3  # borda esquerda da coluna de texto da primeira tela
PERGUNTA = "Pergunta: dá para separar os quatro padrões pela forma das nuvens?"


def imagem(nome: str, altura: float) -> ImageMobject:
    return ImageMobject(str(dados.PASTA / nome), height=altura)


def arquivo_do_padrao(nome: str) -> str:
    return "padrao_fish_quadrado.png" if nome == "fish" else f"padrao_{nome}.png"


def ponto_na_imagem(img: ImageMobject, tamanho_px: tuple[int, int], px: float, py: float) -> np.ndarray:
    """O ponto da tela que corresponde ao pixel (px, py) de uma imagem de tamanho_px mostrada em img."""
    largura, altura = tamanho_px
    canto = img.get_corner(UL)
    return canto + np.array([px / largura * img.get_width(), -py / altura * img.get_height(), 0])


def caixa_na_imagem(img: ImageMobject, tamanho_px: tuple[int, int], caixa: tuple[float, float, float, float], cor: ManimColor, largura: float = 3) -> Rectangle:
    x0, y0, x1, y1 = caixa
    a = ponto_na_imagem(img, tamanho_px, x0, y0)
    b = ponto_na_imagem(img, tamanho_px, x1, y1)
    return Rectangle(width=b[0] - a[0], height=a[1] - b[1]).set_stroke(cor, width=largura).move_to((a + b) / 2)


def linha_de_texto(texto: str, y: float, tamanho: float = 26, cor: ManimColor = WHITE, x: float | None = None, alinha_esquerda: float | None = None) -> TexText:
    t = TexText(texto, font_size=tamanho).set_color(cor)
    if alinha_esquerda is not None:
        t.move_to([alinha_esquerda + t.get_width() / 2, y, 0])
    else:
        t.move_to([x if x is not None else 0, y, 0])
    return t


def polilinha(pontos: list[np.ndarray], cor: ManimColor, largura: float = 2.5, opacidade: float = 1.0) -> VMobject:
    linha = VMobject().set_points_as_corners(pontos)
    return linha.set_stroke(cor, width=largura, opacity=opacidade)


def primeira_tela() -> dict[str, Mobject]:
    """A tela de abertura da seção, em três blocos: o dado, as classes e por que classificar.
    Montada por função porque volta, idêntica, no último slide."""
    cena = imagem("cena_flower_tela.png", 3.9).move_to([-3.7, 0.5, 0])
    legenda = linha_de_texto("MODIS (Terra), 28/01/2008, a leste de Barbados", -1.75, 22, GREY_A, x=-3.7)
    dado = VGroup(
        linha_de_texto("O dado", 2.35, 30, alinha_esquerda=X_DIREITA),
        linha_de_texto(R"imagens de satélite (MODIS), no visível, 1 pixel $\approx$ 1 km", 1.95, 24, GREY_A, alinha_esquerda=X_DIREITA),
        linha_de_texto("nuvens rasas sobre o Atlântico tropical", 1.63, 24, GREY_A, alinha_esquerda=X_DIREITA),
        linha_de_texto("cenas rotuladas à mão por especialistas", 1.31, 24, GREY_A, alinha_esquerda=X_DIREITA),
    )
    cabeca_classes = linha_de_texto("As classes", 0.8, 30, alinha_esquerda=X_DIREITA)
    miniaturas = Group()
    nomes = VGroup()
    for k, nome in enumerate(ORDEM):
        x = X_DIREITA + 0.6 + 1.5 * k
        miniaturas.add(imagem(arquivo_do_padrao(nome), 1.2).move_to([x, -0.05, 0]))
        nomes.add(linha_de_texto(dados.NOMES[nome], -0.9, 24, COR_PADRAO[nome], x=x))
    motivacao = VGroup(
        linha_de_texto("Por que classificar", -1.4, 30, alinha_esquerda=X_DIREITA),
        linha_de_texto("cada padrão indica um ambiente climatológico", -1.8, 24, GREY_A, alinha_esquerda=X_DIREITA),
        linha_de_texto("nuvens rasas: grande incerteza nos modelos de clima", -2.12, 24, GREY_A, alinha_esquerda=X_DIREITA),
        linha_de_texto("meta: contar os padrões em décadas de imagens", -2.44, 24, GREY_A, alinha_esquerda=X_DIREITA),
    )
    return {"cena": cena, "legenda": legenda, "dado": dado, "cabeca_classes": cabeca_classes,
            "miniaturas": miniaturas, "nomes": nomes, "motivacao": motivacao}


class AplicacaoSatelite(Slide):
    """Padrões de nuvens rasas no MODIS: o dado, a pergunta, e como a persistência descreve cada padrão."""

    def construct(self) -> None:
        self.pers = dados.persistencia()
        self.o_dado()
        self.quatro_padroes()
        self.um_tile()
        self.do_diagrama_ao_vetor()
        self.sugar_contra_flowers()
        self.volta_ao_comeco()

    def troca_linha(self, texto: str, run_time: float = 2) -> None:
        nova = entendimento(texto)
        if getattr(self, "linha", None) is None:
            self.play(Write(nova), run_time=run_time)
        else:
            self.play(FadeOut(self.linha), Write(nova), run_time=run_time)
        self.linha = nova

    # ---------------------------------------------------------- 7.1: o dado, as classes, a motivação
    def o_dado(self) -> None:
        self.indice = indice_secao(7)
        self.cabecalho = titulo("Nuvens vistas do satélite")
        self.fonte = rodape(FONTE)
        self.play(Write(self.indice))
        self.play(Write(self.cabecalho), Write(self.fonte))

        tela = primeira_tela()
        self.play(FadeIn(tela["cena"]), run_time=1.5)
        self.play(Write(tela["legenda"]), LaggedStartMap(Write, tela["dado"], lag_ratio=0.3), run_time=3)
        fecha_passo(self, """
            - A aplicação é de Ver Hoef, Adams, King e Ebert-Uphoff (2023), um primer sobre TDA para ciências atmosféricas na revista AIES, com código no GitHub.
            - **O dado:** imagens do MODIS (satélites Terra e Aqua, da NASA) no visível, em cor verdadeira, com cerca de 1 km por pixel. A região fica a leste de Barbados (10–24° N, 61–40° O), no inverno do hemisfério norte, onde dominam as nuvens rasas dos ventos alísios.
            - Esta cena é do Terra, de 28/01/2008, baixada do NASA Worldview pela data e pela região de um rótulo.
            - **Os rótulos** vêm de Rasp et al. (2020): uma campanha de crowdsourcing com especialistas recrutados, que desenharam retângulos sobre as imagens e disseram o padrão de cada um. Foram cerca de 10 mil imagens e 50 mil retângulos. Rotular é caro: é a motivação para um método que precise de poucos rótulos.
        """)

        self.play(Write(tela["cabeca_classes"]))
        self.play(LaggedStartMap(FadeIn, tela["miniaturas"], lag_ratio=0.25), LaggedStartMap(Write, tela["nomes"], lag_ratio=0.25),
                  run_time=2.5)
        fecha_passo(self, """
            - **As classes:** quatro padrões de organização de nuvens rasas, em escalas de 20 a 1000 km: sugar, gravel, flowers e fish.
            - Foram identificados em 2020 por uma equipe internacional de cientistas (ISSI), por inspeção visual de imagens MODIS (Stevens et al., 2020).
            - Humanos reconhecem os quatro com algum treino, mas é difícil descrevê-los objetivamente para uma máquina.
            - Cada miniatura é um recorte em que 4 ou mais especialistas concordaram sobre o padrão.
        """)

        self.play(LaggedStartMap(Write, tela["motivacao"], lag_ratio=0.3), run_time=3)
        self.troca_linha(PERGUNTA)
        fecha_passo(self, """
            - **Por que classificar (seção 2 do artigo):**
                - as nuvens têm papel central no balanço de radiação da Terra (L'Ecuyer et al., 2015);
                - os modelos de clima têm resolução baixa demais para representar as nuvens na escala delas, e isso gera grande incerteza nas previsões de clima (Gentine et al., 2018);
                - estudos de radar (Stevens et al., 2020) e de perfis verticais de temperatura, umidade e movimento vertical (Rasp et al., 2020) mostraram que cada padrão ocorre num ambiente climatológico distinto: o padrão é um indicador do ambiente;
                - **a meta de longo prazo:** contar com que frequência cada padrão aparece pelo globo, ao longo de décadas de registro de satélite, para entender mudanças nas condições meteorológicas. Isso exige classificar milhares de cenas automaticamente.
            - A pergunta da seção: dá para separar os padrões pela forma das nuvens? É aqui que entra a homologia persistente.
        """)
        self.tela = tela

    # ---------------------------------------------------------- 7.2: os quatro padrões
    def quatro_padroes(self) -> None:
        tela = self.tela
        lado = 2.85
        xs = [-4.95, -1.65, 1.65, 4.95]
        self.quadros = {}
        nomes = VGroup()
        descricoes = VGroup()
        for x, nome in zip(xs, ORDEM):
            self.quadros[nome] = imagem(arquivo_do_padrao(nome), lado).move_to([x, 0.25, 0])
            nomes.add(linha_de_texto(dados.NOMES[nome], 2.05, 34, COR_PADRAO[nome], x=x))
            bloco = VGroup(*[TexText(p_, font_size=22).set_color(GREY_A) for p_ in dados.DESCRICOES[nome]]).arrange(DOWN, buff=0.08)
            descricoes.add(bloco.move_to([x, -1.55, 0]))
        molduras = VGroup(*[SurroundingRectangle(self.quadros[n], buff=0.02).set_stroke(COR_PADRAO[n], width=3) for n in ORDEM])
        sai = Group(tela["cena"], tela["legenda"], tela["dado"], tela["cabeca_classes"], tela["nomes"], tela["motivacao"], self.linha)
        self.linha = None
        cresce = [surge_de(self.quadros[n], miniatura) for n, miniatura in zip(ORDEM, tela["miniaturas"])]
        self.play(FadeOut(sai), FadeOut(tela["miniaturas"]), *cresce, run_time=2)
        self.play(LaggedStartMap(ShowCreation, molduras, lag_ratio=0.2), LaggedStartMap(Write, nomes, lag_ratio=0.2), run_time=2)
        self.play(LaggedStartMap(Write, descricoes, lag_ratio=0.25), run_time=3)
        fecha_passo(self, """
            - Os quatro padrões de perto:
                - **Sugar:** nuvens pequenas, espalhadas por igual.
                - **Gravel:** um pouco maiores e mais organizadas.
                - **Flowers:** aglomerados grandes, com céu limpo entre eles.
                - **Fish:** estruturas em espinha, de mesoescala.
            - Cada recorte é a área em que 4 ou mais especialistas concordaram (a interseção dos retângulos deles, nos rótulos de Rasp et al., 2020). As imagens foram baixadas do NASA Worldview pela data e pela região dos rótulos.
        """)

        self.troca_linha("Premissa: formas diferentes, topologias diferentes; a persistência mede forma.")
        fecha_passo(self, """
            - **A premissa do artigo:** se os padrões têm formas diferentes, a topologia deles deve ser diferente, e a homologia persistente é uma medida de forma.
            - Vamos seguir um exemplo de flowers, do pixel ao resumo topológico.
        """)
        self.limpar = Group(molduras, nomes, descricoes)

    # ---------------------------------------------------------- 7.3: um tile, da cor ao diagrama
    def um_tile(self) -> None:
        info = self.pers["padroes"]["flower"]
        rx0, ry0, rx1, ry1 = info["regiao"]
        j = info["janelas"][info["exibida"]]
        caixa = (j["x"] - rx0, j["y"] - ry0, j["x"] - rx0 + dados.JANELA, j["y"] - ry0 + dados.JANELA)
        flower = self.quadros["flower"]
        marca = caixa_na_imagem(flower, (rx1 - rx0, ry1 - ry0), caixa, YELLOW, 4)
        self.play(ShowCreation(marca), run_time=1.2)
        outros = Group(*[self.quadros[n] for n in ORDEM if n != "flower"], self.limpar, self.linha)
        self.linha = None
        # O tile entra no centro; quando a filtração começa, desliza para a esquerda.
        centro = np.array([0, 0.35, 0])
        tile_cor = imagem("janela_flower_cor.png", 3.0).move_to(centro)
        nome_tile = linha_de_texto("um tile de flowers", 2.2, 28, x=centro[0])
        tamanho_tile = linha_de_texto(R"96 $\times$ 96 pixels ($\approx$ 100 km)", -1.45, 24, GREY_A, x=centro[0])
        self.play(FadeOut(outros), run_time=1.2)
        self.play(surge_de(tile_cor, marca), FadeOut(flower), FadeOut(marca), run_time=2)
        self.play(Write(nome_tile), Write(tamanho_tile))
        fecha_passo(self, """
            - Como os autores fazem (o código deles está no GitHub): de cada retângulo rotulado, sorteiam 6 tiles de 96 × 96 pixels, cerca de 100 km de lado.
            - Aqui, um deles, de um retângulo de flowers: o de maior contraste entre os 6 (um tile só de céu limpo não mostraria nada).
            - Mais adiante, os 6 tiles de cada retângulo são resumidos numa média.
        """)

        # Escala de cinza: a mesma conta da seção 2.
        tile_cinza = imagem("janela_flower.png", 3.0).move_to(centro)
        formulas = VGroup(
            Tex(R"f = \varphi \circ I", font_size=32),
            Tex(R"\varphi(R, G, B) = 0.299R + 0.587G + 0.114B", font_size=26),
        ).arrange(DOWN, buff=0.2).move_to([centro[0], -2.25, 0])
        self.play(FadeIn(tile_cinza), run_time=2)
        self.remove(tile_cor)
        self.play(Write(formulas), run_time=2)
        fecha_passo(self, """
            - O tile vai para tons de cinza com a mesma conta da seção 2: φ(R, G, B) = 0,299R + 0,587G + 0,114B, pixel a pixel. É o que faz a conversão "L" da biblioteca PIL, usada no código dos autores.
            - Cada pixel vira um número de 0 (preto, o mar) a 255 (branco, a nuvem). O tile virou uma função f na grade, como a imagem do exemplo.
        """)

        # O limiar desce do claro para o escuro, numa barra de brilho.
        x_barra = -2.35

        def y_do_limiar(brilho: float) -> float:
            return centro[1] + 1.5 - (255 - brilho) / 255 * 3.0

        barra = VGroup()
        for i in range(40):
            barra.add(Rectangle(width=0.28, height=3.0 / 40).set_stroke(width=0)
                      .set_fill(cor_na_escala([WHITE, BLACK], i / 39), 1).move_to([x_barra, centro[1] + 1.5 - (i + 0.5) * 3.0 / 40, 0]))
        nome_claro = linha_de_texto("claro", centro[1] + 1.75, 22, x=x_barra)
        nome_escuro = linha_de_texto("escuro", centro[1] - 1.75, 22, x=x_barra)
        marcador = VGroup(Triangle(fill_color=YELLOW, fill_opacity=1).set_stroke(width=0).scale(0.09).rotate(-PI / 2),
                          Line(LEFT * 0.2, RIGHT * 0.2, stroke_color=YELLOW, stroke_width=3))
        marcador.arrange(RIGHT, buff=0.02).move_to([x_barra - 0.23, y_do_limiar(255), 0])
        self.play(Group(tile_cinza, nome_tile, tamanho_tile, formulas).animate.shift(LEFT * 4.5), run_time=1.5)
        self.play(FadeIn(barra), Write(nome_claro), Write(nome_escuro), FadeIn(marcador))
        quadros = [imagem(f"janela_flower_limiar_{k}.png", 3.0).move_to(tile_cinza) for k in range(len(self.pers["limiares"]))]
        anterior = tile_cinza
        for quadro, brilho in zip(quadros, self.pers["limiares"]):
            self.play(FadeIn(quadro), marcador.animate.set_y(y_do_limiar(brilho)), run_time=0.7)
            self.remove(anterior)
            anterior = quadro
        self.play(FadeIn(tile_cinza), marcador.animate.set_y(y_do_limiar(0)), run_time=0.7)
        self.remove(anterior)
        self.troca_linha("Superníveis: o limiar desce, e o mais claro entra primeiro.")
        fecha_passo(self, """
            - A filtração aqui é por superníveis: o limiar desce do claro para o escuro. Os núcleos mais claros das nuvens entram primeiro, o aglomerado cresce, e por último entra o mar escuro.
            - É o processo de filtração da seção 4, ao contrário. No GUDHI, os autores escrevem `CubicalComplex(top_dimensional_cells=255 - tile)`: inverter os valores troca superníveis por subníveis. O pixel é o quadrado, e os coeficientes são em ℤ₂.
            - Repare nos buracos escuros que aparecem dentro do aglomerado e depois são preenchidos: são as classes de H₁.
        """)

        # O diagrama do tile, calculado pelo GUDHI.
        origem = np.array([0.5, -1.35, 0])
        tamanho = 3.4
        escala = tamanho / 255

        def pd(nasce: float, morre: float) -> np.ndarray:
            return origem + escala * np.array([nasce, morre, 0])

        eixos = VGroup(
            Line(pd(0, 0), pd(255, 0), stroke_color=GREY_B, stroke_width=2),
            Line(pd(0, 0), pd(0, 255), stroke_color=GREY_B, stroke_width=2),
            DashedLine(pd(0, 0), pd(255, 255), stroke_color=GREY_C, stroke_width=1.5),
        )
        nomes_eixos = VGroup(
            linha_de_texto("nascimento", -1.7, 22, x=origem[0] + tamanho / 2),
            TexText("morte", font_size=22).rotate(PI / 2).move_to(origem + np.array([-0.25, tamanho / 2, 0])),
        )
        pontos_h0 = VGroup(*[Dot(pd(b, m), radius=0.018, fill_color=COR_H0) for b, m in info["diagrama_h0"]])
        pontos_h1 = VGroup(*[Dot(pd(b, m), radius=0.018, fill_color=COR_H1) for b, m in info["diagrama_h1"]])
        legenda_d = VGroup(
            VGroup(Dot(radius=0.06, fill_color=COR_H0), TexText(f"{len(pontos_h0)} componentes ($H_0$)", font_size=22)).arrange(RIGHT, buff=0.12),
            VGroup(Dot(radius=0.06, fill_color=COR_H1), TexText(f"{len(pontos_h1)} buracos ($H_1$)", font_size=22)).arrange(RIGHT, buff=0.12),
            TexText(R"eixos em $255 - f$", font_size=22).set_color(GREY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        legenda_d.move_to([origem[0] + tamanho + 0.4 + legenda_d.get_width() / 2, 0.8, 0])
        self.play(ShowCreation(eixos), Write(nomes_eixos), run_time=1.5)
        self.play(FadeIn(pontos_h0), FadeIn(pontos_h1), Write(legenda_d), run_time=2)
        self.troca_linha("Um tile vira um diagrama: milhares de pontos, a maioria junto à diagonal.")
        fecha_passo(self, f"""
            - O diagrama deste tile, calculado com o GUDHI exatamente na configuração dos autores: {len(pontos_h0)} pontos em H₀ e {len(pontos_h1)} em H₁.
            - Os eixos estão em 255 − f (a "escuridão"): 0 é o mais claro. Um ponto de H₀ nasce quando uma região clara aparece e morre quando ela se junta a outra. Um de H₁ nasce quando um anel claro fecha em volta de um trecho escuro e morre quando esse trecho é preenchido.
            - É a leitura da seção 6 numa imagem real: uma nuvem de pontos colada na diagonal (textura, ruído) e poucos pontos longe dela (as estruturas que duram).
            - Um diagrama tem um número variável de pontos; para aprendizado de máquina é preciso um vetor de tamanho fixo. É o próximo passo.
        """)
        self.diagrama = VGroup(eixos, nomes_eixos, pontos_h0, pontos_h1)
        self.legenda_d = legenda_d
        self.pontos_h0 = pontos_h0
        self.limpar = Group(tile_cinza, nome_tile, tamanho_tile, formulas, barra, nome_claro, nome_escuro, marcador)

    # ---------------------------------------------------------- 7.4: do diagrama ao vetor
    def do_diagrama_ao_vetor(self) -> None:
        info = self.pers["padroes"]["flower"]
        alvo = self.diagrama.copy().scale(0.8).move_to([-4.6, 0.1, 0])
        self.play(FadeOut(self.limpar), FadeOut(self.linha),
                  self.diagrama.animate.scale(0.8).move_to([-4.6, 0.1, 0]),
                  self.legenda_d.animate.scale(0.8).next_to(alvo, UP, buff=0.15), run_time=1.8)
        self.linha = None

        # Os eixos da paisagem: t (escuridão) na horizontal, altura da tenda na vertical.
        origem = np.array([-1.6, -1.0, 0])
        largura, altura, h_max = 7.6, 2.4, 100.0
        t = np.linspace(0, 255, dados.N_AMOSTRAS)

        def pl(tt: float, h: float) -> np.ndarray:
            return origem + np.array([tt / 255 * largura, h / h_max * altura, 0])

        eixos = VGroup(Line(pl(0, 0), pl(255, 0), stroke_color=GREY_B, stroke_width=2),
                       Line(pl(0, 0), pl(0, h_max), stroke_color=GREY_B, stroke_width=2))
        nome_t = linha_de_texto(R"limiar ($255 - f$)", -1.35, 22, x=origem[0] + largura / 2)
        titulo_p = linha_de_texto("paisagem de persistência", 2.5, 30, x=origem[0] + largura / 2)
        self.play(ShowCreation(eixos), Write(nome_t), Write(titulo_p), run_time=1.5)

        # As 5 barras de H0 que mais duram viram tendas; o contorno de cima é λ1.
        h0 = np.array(info["diagrama_h0"])
        maiores = np.argsort(-(h0[:, 1] - h0[:, 0]))[:5]
        tendas = VGroup()
        for i in maiores:
            b, m = h0[i]
            tendas.add(polilinha([pl(b, 0), pl((b + m) / 2, (m - b) / 2), pl(m, 0)], COR_H0, 2, 0.6))
        destaque = VGroup(*[self.pontos_h0[i].copy().set_fill(YELLOW).scale(2.5) for i in maiores])
        self.play(FadeIn(destaque), run_time=0.8)
        self.play(*[ShowCreation(te) for te in tendas], run_time=2)
        paisagem = np.array(info["paisagem_exibida"])
        curvas_h0 = VGroup()
        curvas_h1 = VGroup()
        for k in range(dados.N_FUNCOES):
            curvas_h0.add(polilinha([pl(tt, h) for tt, h in zip(t, paisagem[k])], COR_H0, 3.5 - 0.5 * k, 1 - 0.15 * k))
            curvas_h1.add(polilinha([pl(tt, h) for tt, h in zip(t, paisagem[dados.N_FUNCOES + k])], COR_H1, 3.5 - 0.5 * k, 1 - 0.15 * k))
        explica = VGroup(
            linha_de_texto(R"cada ponto vira uma tenda; $\lambda_1$ é o contorno de cima,", 2.0, 22, GREY_A, alinha_esquerda=origem[0]),
            linha_de_texto(R"$\lambda_2$ o segundo, \dots, até $\lambda_5$; o mesmo para $H_1$", 1.65, 22, GREY_A, alinha_esquerda=origem[0]),
        )
        self.play(FadeOut(tendas), ShowCreation(curvas_h0), Write(explica), run_time=2.5)
        self.play(ShowCreation(curvas_h1), FadeOut(destaque), run_time=2)
        fecha_passo(self, """
            - A paisagem de persistência transforma o diagrama em funções. Sobre cada barra (b, m) levanta-se uma "tenda", um triângulo com pico no meio da barra e altura proporcional ao comprimento dela.
            - λ₁ é o contorno de cima de todas as tendas, λ₂ o segundo contorno, e assim por diante. Os autores guardam 5 funções para H₀ e 5 para H₁.
            - Aqui, as tendas das 5 barras de H₀ que mais duram (os pontos em amarelo no diagrama) e as paisagens completas do tile.
            - Leitura: montanha alta é uma estrutura que dura (nuvem grande e contrastada); muitas montanhas baixas são textura. A posição no eixo diz em que nível de brilho isso acontece.
            - A paisagem é estável (Bubenik, 2015): mudar pouco a imagem muda pouco a paisagem.
        """)

        # O vetor: 10 linhas (λ1 a λ5 de H0, λ1 a λ5 de H1) de 200 amostras; mais claro, mais alto.
        vetor = VGroup()
        maximo = paisagem.max()
        lado_x, lado_y = largura / dados.N_AMOSTRAS, 0.07
        for linha in range(2 * dados.N_FUNCOES):
            cor = COR_H0 if linha < dados.N_FUNCOES else COR_H1
            y = -1.55 - linha * (lado_y + 0.012) - (0.06 if linha >= dados.N_FUNCOES else 0)
            for k, valor in enumerate(paisagem[linha]):
                celula = Rectangle(width=lado_x, height=lado_y).set_stroke(width=0)
                celula.set_fill(cor_na_escala([BLACK, cor], valor / maximo), 1)
                vetor.add(celula.move_to([origem[0] + (k + 0.5) * lado_x, y, 0]))
        nomes_v = VGroup(
            Tex("H_0", font_size=24).set_color(COR_H0).move_to([origem[0] - 0.3, vetor[0].get_y() - 2 * (lado_y + 0.012), 0]),
            Tex("H_1", font_size=24).set_color(COR_H1).move_to([origem[0] - 0.3, vetor[-1].get_y() + 2 * (lado_y + 0.012), 0]),
        )
        rotulo_v = linha_de_texto(R"10 funções $\times$ 200 amostras $=$ 2000 números", -2.75, 22, x=origem[0] + largura / 2)
        self.play(FadeOut(nome_t), FadeIn(vetor, lag_ratio=0.002), Write(nomes_v), Write(rotulo_v), run_time=2.5)
        fecha_passo(self, """
            - Cada uma das 10 funções é amostrada em 200 níveis igualmente espaçados do limiar: 10 × 200 = 2000 números por tile.
            - A faixa é esse vetor: cada linha é uma função (de cima para baixo, λ₁ a λ₅ de H₀, depois λ₁ a λ₅ de H₁), cada coluna um nível do limiar, e quanto mais clara a célula, mais alta a função ali.
            - O vetor do retângulo é a média dos vetores dos seus 6 tiles: um ponto em ℝ²⁰⁰⁰.
            - **Nenhum treino até aqui:** é só a persistência. É isto que os autores chamam de feature engineering.
        """)
        self.limpar = Group(self.diagrama, self.legenda_d, eixos, titulo_p, curvas_h0, curvas_h1, explica, vetor, nomes_v, rotulo_v)

    # ---------------------------------------------------------- 7.5: sugar contra flowers
    def sugar_contra_flowers(self) -> None:
        self.play(FadeOut(self.limpar), run_time=1.2)
        t = np.linspace(0, 255, dados.N_AMOSTRAS)
        titulo_m = VGroup(
            TexText("paisagens médias dos 6 tiles:", font_size=26),
            TexText(R"$H_0$", font_size=26).set_color(COR_H0),
            TexText(R"e", font_size=26),
            TexText(R"$H_1$", font_size=26).set_color(COR_H1),
        ).arrange(RIGHT, buff=0.15).move_to([0, 2.5, 0])
        lambda_k = linha_de_texto(R"$\lambda_k(t)$: altura da $k$-ésima tenda mais alta no limiar $t$ (alta: a feição dura muito)",
                                  2.08, 22, GREY_A)
        paineis = Group()
        for x, nome in ((-3.4, "sugar"), (3.4, "flower")):
            media = np.array(self.pers["padroes"][nome]["paisagem_media"])
            o = np.array([x - 2.6, -2.0, 0])

            def pm(tt: float, h: float, o: np.ndarray = o) -> np.ndarray:
                return o + np.array([tt / 255 * 5.2, h / 90 * 2.3, 0])

            painel = VGroup(Line(pm(0, 0), pm(255, 0), stroke_color=GREY_B, stroke_width=2),
                            Line(pm(0, 0), pm(0, 90), stroke_color=GREY_B, stroke_width=2))
            for k in range(dados.N_FUNCOES):
                painel.add(polilinha([pm(tt, h) for tt, h in zip(t, media[k])], COR_H0, 3.5 - 0.5 * k, 1 - 0.15 * k))
                painel.add(polilinha([pm(tt, h) for tt, h in zip(t, media[dados.N_FUNCOES + k])], COR_H1, 3.5 - 0.5 * k, 1 - 0.15 * k))
            mini = imagem(f"padrao_{nome}.png", 1.2).move_to([x + 0.9, 1.0, 0])
            nome_t2 = linha_de_texto(dados.NOMES[nome], 1.0, 32, COR_PADRAO[nome], x=x - 1.1)
            paineis.add(Group(mini, nome_t2, painel))
        notas_p = VGroup(
            linha_de_texto(R"$H_0$: $\lambda_1$ a $\lambda_5$ altas e quase iguais", -2.4, 22, GREY_A, x=-3.4),
            linha_de_texto(R"$H_0$: mais baixas e espalhadas; $H_1$ um pouco maior", -2.4, 22, GREY_A, x=3.4),
        )
        self.play(Write(titulo_m), run_time=1.2)
        self.play(Write(lambda_k), run_time=2)
        self.play(FadeIn(paineis[0][0]), Write(paineis[0][1]), FadeIn(paineis[1][0]), Write(paineis[1][1]), run_time=1.5)
        self.play(*[ShowCreation(p[2]) for p in paineis], run_time=2.5)
        self.play(Write(notas_p), run_time=1.5)
        self.troca_linha("Sugar: muitas nuvens iguais. Flowers: aglomerados que se fundem aos poucos.")
        fecha_passo(self, """
            - **O que é o λ, rapidamente:** em cada nível t do limiar, cada ponto do diagrama levanta uma tenda. λ₁(t) é a altura da tenda mais alta ali, λ₂(t) a da segunda, até λ₅(t). Altura grande quer dizer feição que dura muito; várias λ juntas e altas querem dizer várias feições que duram parecido.
            - As paisagens médias dos 6 tiles de um retângulo de sugar e de um de flowers, calculadas por nós nos recortes reais, na configuração dos autores. O padrão é o que o artigo descreve (seção 4d): no sugar, um pico de H₀ alto e agudo; no flowers, um H₀ mais baixo e um H₁ mais forte.
            - **Sugar:** λ₁ a λ₅ de H₀ quase se sobrepõem (picos de 82 a 75). Há muitas componentes com praticamente a mesma vida longa: nuvens pequenas, de brilho parecido (nascem em níveis parecidos), sobre um mar escuro uniforme (morrem quase juntas, quando o limiar chega ao brilho do mar entre elas e as funde).
            - **Flowers:** as λₖ de H₀ são mais baixas e se separam (picos de 60 a 39). Os aglomerados têm brilhos variados e se fundem em níveis diferentes do limiar.
            - **H₁ aparece nos dois.** No flowers é um pouco mais forte (pico de 45 contra 39 no sugar, e cerca de 20% a mais de área): buracos e textura dentro dos aglomerados. A diferença mais visível está em H₀.
            - Esta é a premissa virando número: formas diferentes, paisagens diferentes.
        """)
        self.limpar = Group(titulo_m, lambda_k, paineis, notas_p)

    # ---------------------------------------------------------- 7.6: de volta à primeira tela
    def volta_ao_comeco(self) -> None:
        tela = primeira_tela()
        tudo = Group(tela["cena"], tela["legenda"], tela["dado"], tela["cabeca_classes"], tela["miniaturas"],
                     tela["nomes"], tela["motivacao"])
        pergunta = entendimento(PERGUNTA)
        self.play(FadeOut(self.limpar), FadeOut(self.linha), run_time=1.2)
        self.linha = None
        self.play(FadeIn(tudo), FadeIn(pergunta), run_time=2)
        fecha_passo(self, f"""
            - De volta à pergunta do começo. A resposta do artigo: sim, em boa parte.
            - **A classificação:** cada retângulo vira um ponto em ℝ²⁰⁰⁰. A PCA, sem olhar rótulos, projeta nos 3 primeiros componentes principais (mais de 90% da variação), e uma SVM linear separa cada par de padrões, treinada com {dados.SVM_TREINO} retângulos por classe e testada com {dados.SVM_TESTE}.
            - **As acurácias (Fig. 10):** sugar × flowers 89,25%; fish × sugar 86%; flowers × gravel 81%; fish × gravel 79,5%; sugar × gravel 71,25%; fish × flowers 57%, perto do acaso.
            - **Por que o fish falha:** a estrutura dele é de mesoescala (a faixa de fish da cena que baixamos tem quase 1.900 km), e o tile tem cerca de 100 km: dentro dele, um pedaço de fish parece flowers. Os autores sugerem tiles maiores. O fish foi também o padrão mais disputado entre os próprios especialistas em Rasp et al. (2020).
            - **Contra o deep learning de Rasp et al.:** as redes aprendem com dezenas de milhares de rótulos e acertam mais, mas são caixa-preta. A rota do artigo calcula os atributos da forma ("um feature engineering sofisticado", nas palavras dos autores), precisa de poucas centenas de rótulos, usa um modelo linear interpretável (o plano da SVM volta ao espaço das paisagens e pode ser lido como nuvens, Fig. 11) e custa pouco: cerca de {dados.CUSTO_MINUTOS} min para {dados.CUSTO_AMOSTRAS} retângulos ({dados.CUSTO_RECORTES} tiles) num notebook.
            - **Na medicina, a mesma ideia (só citar):** Tanabe, Kaji et al. (2021), tomografia 3D de pulmão. É a mesma filtração por limiar, agora em voxels: a fibrose aparece como "cavidades densas e duradouras" e o enfisema como "componentes densos com nascimento baixo". Kaji é coautor do Cubical Ripser.
            - **Crédito das imagens:** "We acknowledge the use of imagery from the NASA Worldview application (https://worldview.earthdata.nasa.gov), part of the NASA Earth Science Data and Information System (ESDIS)."
        """)
