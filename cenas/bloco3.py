"""Bloco 3: a filtração de G.

Render: manim-slides render --GL bloco3.py ConstrucaoDaFiltracao
Os números vêm de dados_bloco3.py e são conferidos por verifica_bloco3.py.
Uma seta, um passo: cada fecha_passo fecha um passo, com a nota do que ele mostrou.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from manimlib import *
from manim_slides import Slide

import dados_bloco2 as d2
import dados_bloco3 as dados
from bloco2 import CINZA_G, X_PAINEL, coluna, complexo_de_g, cor_da_dimensao, imagem_g, p
from estilo import *

if TYPE_CHECKING:
    from manimlib.typing import ManimColor

X_TEXTO = 0.9  # borda esquerda dos textos do painel da direita
CENTRO_MAX = np.array([1.9, -1.4, 0])  # os dois blocos ampliados da tela 4.1
CENTRO_MIN = np.array([5.3, -1.4, 0])
LADO_BLOCO = 1.3
LADO_CASA = 0.5  # o CubeMap da tela 4.2
CENTRO_CUBEMAP = np.array([-3.4, -0.35, 0])
Y_BARRA = {0: -0.5, 1: -1.1}  # o barcode da tela 4.3
Y_EIXO_T = -1.9
CENTRO = ((2, 2), (2, 2))  # o vértice 139
COR_NUMERO = {0: WHITE, 2: RED_A}  # no processo de filtração: valor do vértice e do quadrado
# A linha de entendimento sobe em relação à do bloco 2: as desta seção são longas e
# cruzariam o rodapé, que começa em y = -3,48.
Y_LINHA = -3.15


def cinza(valor: float) -> ManimColor:
    return cor_na_escala([BLACK, WHITE], (valor - CINZA_G[0]) / (CINZA_G[1] - CINZA_G[0]))


def claro(valor: float) -> bool:
    return (valor - CINZA_G[0]) / (CINZA_G[1] - CINZA_G[0]) >= 0.5  # o 115 fica no meio: preto lê melhor


def acende(mob: Mobject, dim: int, forca: float = 1.0) -> Mobject:
    """A célula no estilo da convenção, com a força dada: 1 acesa, perto de 0 apagada.
    Aceita também mob.animate."""
    if dim == 0:
        return mob.set_fill(opacity=forca)
    if dim == 1:
        return mob.set_stroke(opacity=forca)
    return mob.set_fill(opacity=0.45 * forca)


VERTICES = d2.complexo_da_grade(d2.N)[0]  # a ordem dos rótulos dos vértices


def novo_complexo() -> VGroup:
    """O complexo de G num grupo só: quadrados, arestas e vértices, nessa ordem de camadas."""
    camadas = complexo_de_g()
    return VGroup(camadas[2], camadas[1], camadas[0])


def por_cubo(complexo: VGroup) -> dict[d2.Cubo, VMobject]:
    """cubo -> mobject, num grupo feito por novo_complexo() ou numa cópia dele."""
    por_dim = d2.complexo_da_grade(d2.N)
    mobs = {}
    for dim in (0, 1, 2):
        for cubo, mob in zip(por_dim[dim], complexo[2 - dim]):
            mobs[cubo] = mob
    return mobs


def lugar_do_rotulo(cubo: d2.Cubo) -> np.ndarray:
    """Onde fica o valor de uma célula no complexo: acima e à direita do vértice; no centro do quadrado."""
    (x0, x1), (y0, y1) = cubo
    if d2.dimensao(cubo) == 0:
        return p(x0, y0) + np.array([0.22, 0.18, 0])
    return p((x0 + x1) / 2, (y0 + y1) / 2)


def celula_apagada(cubo: d2.Cubo) -> Mobject:
    """A célula do bloco 2 no lugar dela, quase apagada (o subnível ainda não chegou)."""
    (x0, x1), (y0, y1) = cubo
    dim = d2.dimensao(cubo)
    if dim == 0:
        mob = Dot(p(x0, y0), radius=0.09, fill_color=COR_VERTICE)
    elif dim == 1:
        mob = Line(p(x0, y0), p(x1, y1), stroke_color=COR_ARESTA, stroke_width=6)
    else:
        mob = Polygon(p(x0, y0), p(x1, y0), p(x1, y1), p(x0, y1)).set_fill(COR_QUADRADO).set_stroke(width=0)
    return acende(mob, dim, 0.12)


def bloco_ampliado(centro: np.ndarray, regra: Callable[[d2.Cubo], int]) -> tuple[VGroup, VGroup]:
    """O quadrado [1,2] x [2,3] ampliado, com o valor de cada célula pela regra dada.
    Ordem de dados.faces_do_bloco(): o quadrado, e1 a e4 e os quatro vértices."""
    def q(x: float, y: float) -> np.ndarray:
        return centro + LADO_BLOCO * np.array([x - 1.5, y - 2.5, 0])

    celulas = VGroup()
    rotulos = VGroup()
    for cubo in dados.faces_do_bloco():
        dim = d2.dimensao(cubo)
        cantos = [q(x, y) for x, y in dados.vertices_do_cubo(cubo)]
        meio = sum(cantos) / len(cantos)
        if dim == 0:
            mob = Dot(meio, radius=0.11, fill_color=COR_VERTICE)
        elif dim == 1:
            mob = Line(cantos[0], cantos[1], stroke_color=COR_ARESTA, stroke_width=7)
        else:
            (x0, x1), (y0, y1) = cubo
            mob = Polygon(q(x0, y0), q(x1, y0), q(x1, y1), q(x0, y1))
            mob.set_fill(COR_QUADRADO, opacity=0.45).set_stroke(width=0)
        rotulo = Tex(str(regra(cubo)), font_size=26)
        if dim < 2:
            fora = meio - centro
            rotulo.move_to(meio + 0.36 * fora / np.linalg.norm(fora))
        else:
            rotulo.move_to(meio)
        celulas.add(mob)
        rotulos.add(rotulo)
    return celulas, rotulos


def posicao_da_casa(casa: tuple[int, int]) -> np.ndarray:
    a, b = casa
    return CENTRO_CUBEMAP + LADO_CASA * np.array([a - 4, b - 4, 0])


def ladrilho(cubo: d2.Cubo) -> Square:
    forma = Square(side_length=0.88 * LADO_CASA).set_stroke(width=0)
    forma.set_fill(cor_da_dimensao(d2.dimensao(cubo)), opacity=0.9)
    return forma.move_to(posicao_da_casa(dados.casa(cubo)))


def texto_a_esquerda(texto: str, y: float, tamanho: float = 28, x: float = X_TEXTO) -> TexText:
    linha = TexText(texto, font_size=tamanho)
    return linha.move_to([x + linha.get_width() / 2, y, 0])


def linha_com_icone(icone: VMobject, texto: str, y: float, cor: ManimColor = WHITE, tamanho: float = 28) -> VGroup:
    icone.move_to([X_TEXTO + 0.2, y, 0])
    rotulo = TexText(texto, font_size=tamanho).set_color(cor)
    rotulo.move_to([X_TEXTO + 0.6 + rotulo.get_width() / 2, y, 0])
    return VGroup(icone, rotulo)


def entendimento(texto: str) -> TexText:
    return TexText(texto, font_size=30).move_to(np.array([0, Y_LINHA, 0]))


class ConstrucaoDaFiltracao(Slide):
    """Da extensão de f às células ao processo de filtração de G, com o barcode."""

    def construct(self) -> None:
        self.entrada()
        self.valor_por_celula()
        self.no_cubemap()
        self.processo()

    def transforma_celulas(self, muda: Callable[[d2.Cubo, VMobject], object], **kwargs: float) -> Transform:
        """Muda células com um Transform no complexo inteiro; muda(cubo, mob) altera a cópia.

        Um LaggedStart ou AnimationGroup sobre células soltas cria um grupo novo, e o ManimGL
        põe esse grupo por cima de tudo: os números somem embaixo das células. O complexo já
        está na cena, então o Transform nele mantém a ordem das camadas."""
        alvo = self.complexo.copy()
        for cubo, mob in por_cubo(alvo).items():
            muda(cubo, mob)
        return Transform(self.complexo, alvo, **kwargs)

    # ---------------------------------------------------------- entrada
    def entrada(self) -> None:
        mapa = fluxo_persistencia(icone_dados=imagem_g(0.2))
        self.indice = indice_secao(4)
        self.play(Write(self.indice))
        apresenta_fluxo(self, mapa)
        processo = mapa["processos"][1]
        objeto = mapa["objetos"][1]
        icone = objeto[1]
        destaque = SurroundingRectangle(processo[0], buff=0.08).set_stroke(YELLOW, width=3)
        resto = VGroup(mapa["moldura"], mapa["setas"], *mapa["sequencia"][:2], objeto[0], objeto[2],
                       *mapa["sequencia"][4:])
        self.play(ShowCreation(destaque), resto.animate.set_opacity(0.2))
        self.play(icone.animate.move_to(processo[0]).scale(0.8), run_time=1.2)

        # A imagem G volta, com o valor de cada pixel. Os pixels ficam numa camada própria, por baixo
        # do complexo, que entra invisível: no clique 1 eles encolhem até sumir sob os vértices.
        self.imagem = VGroup()
        for cubo in VERTICES:
            (x, _), (y, _) = cubo
            pixel = Square(side_length=1.0).set_stroke(width=0).set_fill(cinza(dados.valor(cubo)), opacity=1)
            self.imagem.add(pixel.move_to(p(x, y)))
        self.complexo = novo_complexo()
        self.mobs = por_cubo(self.complexo)
        self.complexo.set_opacity(0)
        self.grupo_rotulos = VGroup()
        self.rotulos = {}
        for cubo in VERTICES:
            valor = dados.valor(cubo)
            numero = Tex(str(valor), font_size=24).set_color(BLACK if claro(valor) else WHITE)
            numero.set_stroke(width=0, behind=True).move_to(self.mobs[cubo])
            self.grupo_rotulos.add(numero)
            self.rotulos[cubo] = numero
        self.cabecalho = titulo("Construção da filtração")
        self.play(FadeOut(VGroup(resto, processo, destaque, icone)), run_time=1.2)
        self.play(FadeIn(self.imagem), Write(self.cabecalho), run_time=1.5)
        self.add(self.complexo)
        self.play(LaggedStartMap(Write, self.grupo_rotulos, lag_ratio=0.04), run_time=2)

    # ---------------------------------------------------------- 4.1 (um valor para cada célula)
    def valor_por_celula(self) -> None:
        # Clique 1: cada pixel vira um vértice e leva o seu valor; f só conhece os vértices.
        texto = coluna("Um valor para cada célula", ["$f$ só dá valor aos 25 vértices;", "faltam 40 arestas e 16 quadrados"],
                       R"f(\sigma) = \max_{v \in \sigma} f(v)")
        sem_valor = Square(side_length=0.3).set_fill(COR_QUADRADO, opacity=0.11).set_stroke(COR_ARESTA, width=4, opacity=0.25)
        legenda = VGroup(
            VGroup(Dot(radius=0.1, fill_color=COR_VERTICE), TexText("vértice: o valor do pixel", font_size=24)).arrange(RIGHT, buff=0.25),
            VGroup(sem_valor, TexText("aresta e quadrado: ainda sem valor", font_size=24)).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        legenda.move_to(np.array([-3.3, -2.55, 0]))
        fonte = rodape("Wagner et al. (2011), seção 3")

        forma_final = por_cubo(novo_complexo())

        def vira_complexo(cubo: d2.Cubo, mob: VMobject) -> None:
            alvo = forma_final[cubo]
            if d2.dimensao(cubo) > 0:
                acende(alvo, d2.dimensao(cubo), 0.25)
            mob.become(alvo)

        no_vertice = self.grupo_rotulos.copy()
        for k, cubo in enumerate(VERTICES):
            no_vertice[k].set_fill(WHITE).scale(20 / 24).move_to(lugar_do_rotulo(cubo)).set_stroke(BLACK, width=3)
        pontos = self.imagem.copy()
        for pixel in pontos:
            pixel.set_width(0.1).set_fill(COR_VERTICE)  # menor que o vértice: some embaixo dele
        self.play(self.transforma_celulas(vira_complexo), Transform(self.imagem, pontos),
                  Transform(self.grupo_rotulos, no_vertice), run_time=2.5)
        self.remove(self.imagem)
        self.play(Write(legenda[0]))
        self.play(Write(legenda[1]))
        self.play(Write(texto[0]))
        self.play(Write(texto[1]), run_time=2.4)
        self.play(Write(fonte))
        fecha_passo(self, """
            - Voltamos ao fluxo: o complexo está pronto, e a próxima caixa é "filtração e matriz de bordo". Nesta seção, a filtração; a matriz fica para a próxima.
            - Primeiro, a imagem G com o valor de cada pixel. Cada pixel vira um vértice e leva o seu valor junto (construção V: pixel = vértice).
            - Filtrar é acrescentar as células em ordem crescente de valor, uma de cada vez (Wagner et al., seção 3). Para isso, toda célula precisa de um valor.
            - O problema: f só dá valor aos pixels, que viraram os 25 vértices. As 40 arestas e os 16 quadrados ainda não têm valor.
        """)

        # Clique 2: a regra do máximo, no quadrado [1,2] x [2,3] da seção 3.
        faces = dados.faces_do_bloco()
        destaque = Square(side_length=1.25).move_to(p(1.5, 2.5)).set_stroke(YELLOW, width=4)
        cel_max, rot_max = bloco_ampliado(CENTRO_MAX, dados.valor)
        leg_max = TexText("regra do máximo", font_size=28).move_to(CENTRO_MAX + 1.35 * DOWN)
        origem = VGroup(*[self.mobs[c] for c in faces])
        rotulos_origem = VGroup(*[self.rotulos[c] for c in faces[5:]])
        self.play(ShowCreation(destaque))
        self.play(TransformFromCopy(origem, cel_max), run_time=1.5)
        self.play(TransformFromCopy(rotulos_origem, rot_max[5:]), run_time=1.2)
        self.play(Write(texto[2]), run_time=1.5)
        self.play(LaggedStart(*[Write(r) for r in rot_max[1:5]], lag_ratio=0.3),
                  *[Indicate(c, color=WHITE) for c in cel_max[1:5]], run_time=2)
        self.play(Write(rot_max[0]), Indicate(cel_max[0], color=WHITE))
        self.play(Write(leg_max))
        fecha_passo(self, """
            - A regra de Wagner et al.: cada célula recebe o **maior** valor entre os seus vértices.
            - No quadrado [1,2]×[2,3], o mesmo da seção 3: três vértices 94 e o 139 do centro. As arestas e₁ e e₄ só têm 94: ficam com 94. As arestas e₂ e e₃ tocam o 139: ficam com 139. O quadrado também fica com 139.
            - Intuição: a célula espera o último dos seus vértices chegar para entrar.
        """)

        # Clique 3: e se fosse o mínimo?
        cel_min, rot_min = bloco_ampliado(CENTRO_MIN, dados.valor_minimo)
        leg_min = TexText("regra do mínimo", font_size=28).move_to(CENTRO_MIN + 1.35 * DOWN)
        self.play(TransformFromCopy(cel_max, cel_min), TransformFromCopy(rot_max[5:], rot_min[5:]), run_time=1.5)
        self.play(LaggedStart(*[Write(r) for r in rot_min[:5]], lag_ratio=0.2), run_time=1.5)
        self.play(Write(leg_min))
        fecha_passo(self, """
            - E se cada célula recebesse o **menor** valor dos seus vértices? Todo o bloco ficaria com 94.
            - Parece uma escolha tão boa quanto a outra. O próximo passo mostra onde ela quebra.
        """)

        # Clique 4: o subnível t = 94 nas duas regras.
        k_centro = faces.index(CENTRO)
        # Acima dos dois blocos, entre a fórmula da coluna e os rótulos de cima: entre os
        # blocos ele encostaria nos rótulos das arestas.
        rotulo_t = Tex("t = 94", font_size=32).set_color(YELLOW).move_to([X_PAINEL, -0.06, 0])
        self.play(Write(rotulo_t))
        apagam = []
        for k, cubo in enumerate(faces):
            if dados.valor(cubo) > dados.T_CONTRAEXEMPLO:
                apagam.append(acende(cel_max[k].animate, d2.dimensao(cubo), 0.15))
                apagam.append(rot_max[k].animate.set_opacity(0.25))
        marca_ok = Tex(R"\checkmark", font_size=40).set_color(GREEN).next_to(leg_max, RIGHT, buff=0.2)
        self.play(*apagam, run_time=1.5)
        self.play(Write(marca_ok))
        circulo = Circle(radius=0.2, stroke_color=RED, stroke_width=5).move_to(cel_min[k_centro])
        marca_x = Tex(R"\times", font_size=40).set_color(RED).next_to(leg_min, RIGHT, buff=0.2)
        self.play(acende(cel_min[k_centro].animate, 0, 0.15), rot_min[k_centro].animate.set_opacity(0.25), run_time=1.2)
        self.play(ShowCreation(circulo), Write(marca_x))
        linha = entendimento(R"Com o máximo, $f(\tau) \le f(\sigma)$ se $\tau$ é face de $\sigma$: todo subnível é um subcomplexo.")
        self.play(Write(linha), run_time=2.5)
        fecha_passo(self, """
            - Em t = 94, com o máximo, sobram os três vértices 94 e as arestas e₁ e e₄: um caminho, que é um complexo.
            - Com o mínimo, o quadrado e as quatro arestas já estão lá, mas o vértice 139 não: falta uma face, e não é complexo (o ✗ da seção 3). Nem dá para falar em homologia.
            - Por que o máximo funciona: uma face tem só parte dos vértices da célula, então o máximo dela é menor ou igual. Logo, cada subnível {f ≤ t} é um subcomplexo, e eles crescem com t: é uma filtração.
            - O nome: filtração por **estrela inferior** (*lower-star*). A estrela inferior de um vértice são as células em que ele é o maior vértice.
            - Se perguntarem: a construção T (pixel = quadrado, face com o mínimo das cofaces) é a outra convenção, de Dlotko e Wanner. Em G, as duas dão o mesmo diagrama.
        """)
        self.limpar_41 = VGroup(texto, legenda, destaque, cel_max, rot_max, leg_max, cel_min, rot_min, leg_min,
                                rotulo_t, marca_ok, marca_x, circulo, linha, fonte)

    # ---------------------------------------------------------- 4.2 (a filtração no CubeMap)
    def no_cubemap(self) -> None:
        celulas = dados.celulas()
        # Clique 1: de volta ao CubeMap; paridade = dimensão.
        casas = VGroup()
        for a in range(9):
            for b in range(9):
                casa = Square(side_length=LADO_CASA).set_stroke(GREY_D, width=1).set_fill(opacity=0)
                casas.add(casa.move_to(posicao_da_casa((a, b))))
        nas_casas = self.grupo_rotulos.copy()
        for k, cubo in enumerate(VERTICES):
            nas_casas[k].scale(0.85).move_to(posicao_da_casa(dados.casa(cubo))).set_fill(BLACK).set_stroke(width=0)
        self.play(FadeOut(self.limpar_41))
        self.play(self.transforma_celulas(lambda cubo, mob: mob.become(ladrilho(cubo)), lag_ratio=0.01),
                  Transform(self.grupo_rotulos, nas_casas), FadeIn(casas), run_time=3)

        coordenadas = VGroup()
        for k in range(9):
            coordenadas.add(Tex(str(k), font_size=18).set_color(GREY_B).move_to(posicao_da_casa((k, 0)) + 0.42 * DOWN))
            coordenadas.add(Tex(str(k), font_size=18).set_color(GREY_B).move_to(posicao_da_casa((0, k)) + 0.42 * LEFT))
        cabeca = TexText("Paridade = dimensão", font_size=40).move_to([X_PAINEL, 2.3, 0])
        nomes = ["(par, par): vértice", "(par, ímpar): aresta", "(ímpar, ímpar): quadrado"]
        linhas_par = VGroup()
        for dim, nome in enumerate(nomes):
            icone = Square(side_length=0.3).set_stroke(width=0).set_fill(cor_da_dimensao(dim), opacity=0.9)
            linhas_par.add(linha_com_icone(icone, nome, 1.6 - 0.5 * dim, cor_da_dimensao(dim)))
        fonte = rodape("Wagner et al. (2011), seção 4, Algoritmo 1")
        self.play(LaggedStartMap(Write, coordenadas, lag_ratio=0.03), Write(fonte), run_time=1.5)
        self.play(Write(cabeca))
        for dim, linha in enumerate(linhas_par):
            # Contornos por cima, e não Indicate nas casas: ver transforma_celulas.
            contornos = VGroup()
            for cubo in celulas:
                if d2.dimensao(cubo) == dim:
                    contorno = Square(side_length=LADO_CASA).set_stroke(WHITE, width=3)
                    contornos.add(contorno.move_to(posicao_da_casa(dados.casa(cubo))))
            self.play(Write(linha), ShowCreation(contornos, lag_ratio=0.02), run_time=1.5)
            self.play(FadeOut(contornos), run_time=0.5)
        fecha_passo(self, """
            - O CubeMap do fim da seção 3: um array 9×9, uma casa por célula.
            - A paridade das coordenadas diz a dimensão: par-par é vértice, par-ímpar é aresta, ímpar-ímpar é quadrado. Não é preciso guardar quem é quem.
            - É a única propriedade do CubeMap que a filtração usa, além da vizinhança do próximo passo.
        """)

        # Clique 2: os vértices recebem o valor do pixel; as outras casas, vazias.
        def vertices_com_valor(cubo: d2.Cubo, mob: VMobject) -> None:
            if d2.dimensao(cubo) == 0:
                mob.set_fill(cinza(dados.valor(cubo)), opacity=1)
            else:
                mob.set_fill(opacity=0.15)

        cores = []
        for cubo in VERTICES:
            cores.append(self.rotulos[cubo].animate.set_fill(BLACK if claro(dados.valor(cubo)) else WHITE))
        linhas_valor = VGroup(
            texto_a_esquerda("os vértices recebem o valor do pixel;", 0.0),
            texto_a_esquerda("as outras 56 casas estão vazias", -0.4),
        )
        self.play(self.transforma_celulas(vertices_com_valor), *cores, run_time=2)
        self.play(Write(linhas_valor), run_time=2.4)
        fecha_passo(self, """
            - As casas par-par recebem o valor do pixel, em cinza como a imagem.
            - As outras 56 casas (40 arestas e 16 quadrados) estão vazias, esperando a regra do máximo.
        """)

        # Clique 3: as 8 vizinhas de um vértice são as suas cofaces.
        moldura = Square(side_length=3 * LADO_CASA + 0.06).move_to(posicao_da_casa((4, 4))).set_stroke(YELLOW, width=4)
        vizinhas = []
        for cubo in celulas:
            if cubo != CENTRO and (2, 2) in dados.vertices_do_cubo(cubo):
                vizinhas.append(cubo)
        linhas_viz = VGroup(
            texto_a_esquerda("as 8 vizinhas de um vértice", -1.1),
            texto_a_esquerda("são as suas cofaces:", -1.5),
            texto_a_esquerda(R"$3^d - 1$ casas (8 em 2D, 26 em 3D)", -1.9),
        )
        self.play(ShowCreation(moldura))
        self.play(self.transforma_celulas(lambda cubo, mob: mob.set_fill(opacity=0.75) if cubo in vizinhas else None),
                  run_time=1.2)
        self.play(Write(linhas_viz), run_time=3)
        fecha_passo(self, """
            - Em volta de um vértice, as 8 casas vizinhas são exatamente as arestas e os quadrados que o contêm: as cofaces dele. Aqui, as do centro: 4 arestas e 4 quadrados.
            - Em d dimensões são 3^d − 1 vizinhas: 26 em 3D, 80 em 4D. Achar uma coface vira conta de índice, ±1 nas coordenadas.
            - Sem lista de incidência guardada: é isso que deixa a filtração barata em memória.
        """)

        # Clique 4: o Algoritmo 1; o 139 vem primeiro e toma a sua estrela inferior.
        cabeca_alg = TexText("Algoritmo 1", font_size=40).move_to([X_PAINEL, 2.3, 0])
        linhas_alg = VGroup(
            texto_a_esquerda("os pixels, do maior para o menor;", 1.6),
            texto_a_esquerda("cada um toma as casas vizinhas", 1.2),
            texto_a_esquerda("que ainda estão vazias", 0.8),
        )
        ordem = VGroup()
        for valor in dados.ordem_dos_valores():
            ordem.add(Tex(str(valor), font_size=30))
        ordem.arrange(RIGHT, buff=0.3).move_to([X_PAINEL, 0.1, 0])
        ponteiro = SurroundingRectangle(ordem[0], buff=0.08).set_stroke(YELLOW, width=3)
        self.play(FadeOut(VGroup(cabeca, linhas_par, linhas_valor, linhas_viz)))
        self.play(Write(cabeca_alg))
        self.play(Write(linhas_alg), run_time=2.5)
        self.play(LaggedStartMap(Write, ordem, lag_ratio=0.15), run_time=1.5)
        self.play(ShowCreation(ponteiro))
        self.preenche(vizinhas, run_time=1.8)
        linhas_estrela = VGroup(
            texto_a_esquerda("o 139 toma 9 casas:", -0.7),
            texto_a_esquerda("a sua estrela inferior", -1.1),
        )
        self.play(Write(linhas_estrela), run_time=2)
        fecha_passo(self, """
            - O Algoritmo 1 de Wagner et al. ordena só os pixels, do maior para o menor. Cada um toma as casas vizinhas que ainda estão vazias e dá a elas o seu valor.
            - O que ele preenche aqui é o **CubeMap** (o array 9×9 de valores), não a matriz de bordo. A matriz vem numa segunda passada, que usa a ordem montada aqui: é a próxima seção.
            - O 139 vem primeiro e toma 9 casas: ele, 4 arestas e 4 quadrados.
            - **Estrela inferior** de um vértice: as células em que ele é o maior vértice. São exatamente as casas que ele toma, e todas recebem o valor dele, então entram na filtração junto com ele. O 139 fica com as 9 porque todo vizinho é menor.
            - Por que isso dá o máximo: se a casa ainda está vazia quando um vértice chega, nenhum vértice maior a tocou antes. Então ele é o maior vértice dela.
        """)

        # Clique 5: os outros pixels, valor a valor, até as 81 casas.
        self.play(FadeOut(moldura))
        for k, valor in enumerate(dados.ordem_dos_valores()[1:], start=1):
            donos = []
            tomadas = []
            for cubo in celulas:
                if dados.valor(cubo) == valor:
                    if d2.dimensao(cubo) == 0:
                        donos.append(Indicate(self.rotulos[cubo], color=YELLOW, scale_factor=1.5))
                    else:
                        tomadas.append(cubo)
            self.play(ponteiro.animate.move_to(ordem[k]), *donos, run_time=0.7)
            self.preenche(tomadas, run_time=1.0)
        linha = entendimento("Quem chega primeiro numa casa é o seu maior vértice: o máximo sai de graça.")
        self.play(Write(linha), run_time=2.5)
        fecha_passo(self, """
            - Os outros pixels na ordem 119, 117, 115, 114, 100, 99, 94. Empates não mudam nada: os empatados têm o mesmo valor.
            - As estrelas inferiores encolhem no fim: um 94 do anel fica com 1 ou 2 casas, porque os vizinhos maiores já tomaram as cofaces que dividem com ele.
            - No fim, as 81 casas têm valor: é f estendida ao complexo, e o array parece G ampliada.
            - Só os 25 pixels foram ordenados. O artigo também dá o índice da filtração na mesma passada, do maior para o menor, e monta a matriz de bordo numa segunda passada (linhas 7 a 11 do Algoritmo 1): é a ponte para a próxima seção. O custo é linear no número de pixels (seção 6).
            - **Hoje as bibliotecas não fazem assim.** O Cubical Ripser (Kaji, Sudo e Ahara, 2020) comenta exatamente esta ideia, ordenar só os voxels e enumerar as células de cada um, e não a usou: o ganho medido foi de menos de 1%. Ele ordena as células de cada dimensão direto, calcula H₀ por union-find e H₁, H₂ reduzindo a matriz de **cobordo**, com cada coluna calculada na hora a partir das cofaces, sem guardar a matriz.
        """)
        self.limpar_42 = VGroup(casas, coordenadas, cabeca_alg, linhas_alg, ordem, ponteiro, linhas_estrela, linha, fonte)

    def preenche(self, cubos: list[d2.Cubo], run_time: float) -> None:
        """As casas tomadas recebem o valor do dono: o cinza e o número."""
        numeros = VGroup()
        for cubo in cubos:
            valor = dados.valor(cubo)
            numero = Tex(str(valor), font_size=17).move_to(posicao_da_casa(dados.casa(cubo)))
            numero.set_color(BLACK if claro(valor) else WHITE)
            self.rotulos[cubo] = numero
            numeros.add(numero)

        def cinza_do_valor(cubo: d2.Cubo, mob: VMobject) -> None:
            if cubo in cubos:
                mob.set_fill(cinza(dados.valor(cubo)), opacity=1)

        self.play(self.transforma_celulas(cinza_do_valor), LaggedStartMap(Write, numeros, lag_ratio=0.08), run_time=run_time)

    # ---------------------------------------------------------- 4.3 (o processo de filtração)
    def processo(self) -> None:
        celulas = dados.celulas()
        # Clique 1: o complexo apagado, com os valores trazidos do CubeMap, o barcode vazio e a régua de t.
        # Ficam os números dos vértices e dos quadrados; os das arestas saem, para não poluir.
        self.play(FadeOut(self.limpar_42))
        self.numeros = {}
        movem = []
        for cubo in celulas:
            rotulo = self.rotulos[cubo]
            if d2.dimensao(cubo) == 1:
                movem.append(FadeOut(rotulo))
                continue
            dim = d2.dimensao(cubo)
            rotulo.set_stroke(width=0, behind=True)
            tamanho = 1 / 0.85 if dim == 0 else 18 / 17
            movem.append(rotulo.animate.scale(tamanho).move_to(lugar_do_rotulo(cubo))
                         .set_fill(COR_NUMERO[dim], opacity=0.35).set_stroke(BLACK, width=3, opacity=0.35))
            self.numeros[cubo] = rotulo
        self.play(self.transforma_celulas(lambda cubo, mob: mob.become(celula_apagada(cubo)), lag_ratio=0.01),
                  *movem, run_time=3)

        cabeca = TexText("O processo de filtração", font_size=40).move_to([X_PAINEL, 2.4, 0])
        acesa = Square(side_length=0.3).set_fill(COR_QUADRADO, opacity=0.45).set_stroke(COR_ARESTA, width=4)
        legenda = VGroup(
            linha_com_icone(Line(LEFT * 0.22, RIGHT * 0.22, stroke_color=COR_H0, stroke_width=10), "componente ($H_0$)", 1.85, COR_H0),
            linha_com_icone(Line(LEFT * 0.22, RIGHT * 0.22, stroke_color=COR_H1, stroke_width=10), "buraco ($H_1$)", 1.45, COR_H1),
            linha_com_icone(acesa, R"célula acesa: $f \le t$", 1.05),
        )
        # A última linha tem cores por palavra: o número do quadrado é vermelho; o que acabou de entrar, amarelo.
        linha_valores = TexText(R"valor: vértice, quadrado; amarelo: $f = t$", font_size=28,
                          t2c={"quadrado": COR_NUMERO[2], "amarelo": YELLOW})
        linha_valores.move_to([X_TEXTO + 0.6 + linha_valores.get_width() / 2, 0.65, 0])
        legenda.add(VGroup(Tex("94", font_size=24).set_color(YELLOW).move_to([X_TEXTO + 0.2, 0.65, 0]), linha_valores))
        eixo = EixoNumerado((90, 140, 10), unit_size=0.1, font_size=22)
        eixo.shift(np.array([1.0, Y_EIXO_T, 0]) - eixo.n2p(90))
        nome_eixo = Tex("t", font_size=28).next_to(eixo.reta, RIGHT, buff=0.55)
        rotulos_h = VGroup(
            Tex("H_0", font_size=30).set_color(COR_H0).move_to([0.45, Y_BARRA[0], 0]),
            Tex("H_1", font_size=30).set_color(COR_H1).move_to([0.45, Y_BARRA[1], 0]),
        )
        betti = VGroup(Tex(R"\beta_0 =", font_size=34).set_color(COR_H0), Integer(0, font_size=34),
                       Tex(R"\beta_1 =", font_size=34).set_color(COR_H1), Integer(0, font_size=34))
        betti.arrange(RIGHT, buff=0.15)
        betti[2].shift(0.5 * RIGHT)
        betti[3].shift(0.5 * RIGHT)
        betti.move_to(np.array([-3.3, -2.5, 0]))
        fonte = rodape("Otter et al. (2017), Fig. 2")

        self.t = ValueTracker(90)

        def x_de(valor: float) -> float:
            return eixo.n2p(valor)[0]

        marcador = DashedLine(np.array([x_de(90), Y_EIXO_T, 0]), np.array([x_de(90), -0.15, 0]),
                              stroke_color=YELLOW, stroke_width=2)
        rotulo_t = VGroup(Tex("t =", font_size=28), Integer(90, font_size=28)).arrange(RIGHT, buff=0.12).set_color(YELLOW)
        rotulo_t.next_to(marcador, UP, buff=0.08)

        self.play(Write(cabeca))
        self.play(LaggedStartMap(Write, legenda, lag_ratio=0.3), run_time=3)
        cria_eixo(self, eixo)
        self.play(Write(nome_eixo), Write(rotulos_h), Write(betti), Write(fonte))
        self.play(ShowCreation(marcador), Write(rotulo_t))

        def segue_t(mob: Mobject) -> None:
            mob.set_x(x_de(self.t.get_value()))

        def atualiza_rotulo(mob: VGroup) -> None:
            mob[1].set_value(int(round(self.t.get_value())))
            mob.arrange(RIGHT, buff=0.12)
            mob.next_to(marcador, UP, buff=0.08)

        marcador.add_updater(segue_t)
        rotulo_t.add_updater(atualiza_rotulo)
        fecha_passo(self, """
            - Agora o processo de filtração: t sobe, e cada célula com f ≤ t acende. Cada etapa é um subcomplexo, pelo que vimos no começo da seção.
            - Os números vieram do CubeMap: o valor de cada vértice (o pixel) e, no centro de cada quadrado, o valor dele (o maior dos quatro cantos). As arestas ficaram sem número para não poluir: valem o maior das duas pontas. Em amarelo, os valores que acabaram de entrar.
            - À direita, o barcode: uma barra por feição, de quando nasce até quando morre. Teal para componentes (H₀), rosa para buracos (H₁).
            - Embaixo do complexo, os contadores β₀ e β₁ do quadro atual.
            - As etapas da Fig. 2(c) de Otter et al. são t = 100, 115, 130 e 140; aqui o processo para nos valores em que algo entra.
        """)

        def barra(dim: int, nasce: float, morre: float) -> Line:
            """A barra cresce com t até a morte; nasce com comprimento quase zero."""
            y = Y_BARRA[dim]
            cor = COR_H0 if dim == 0 else COR_H1
            linha = Line(np.array([x_de(nasce), y, 0]), np.array([x_de(nasce) + 0.01, y, 0]),
                         stroke_color=cor, stroke_width=10)

            def cresce(mob: Line) -> None:
                fim = max(min(self.t.get_value(), morre), nasce + 0.1)
                mob.put_start_and_end_on(np.array([x_de(nasce), y, 0]), np.array([x_de(fim), y, 0]))

            linha.add_updater(cresce)
            return linha

        def marca(dim: int, valor: float) -> tuple[Dot, Tex]:
            cor = COR_H0 if dim == 0 else COR_H1
            ponto = Dot(np.array([x_de(valor), Y_BARRA[dim], 0]), radius=0.08, fill_color=cor)
            numero = Tex(str(valor), font_size=22).set_color(cor).next_to(ponto, UP, buff=0.12)
            return ponto, numero

        notas = [
            """
            - t = 94: entram os cinco pixels 94 e as 4 arestas entre eles, um "gancho". É uma componente: nasce a barra de H₀ em 94.
            - Os cinco vértices 94 não são cinco componentes? Cada aresta 94 junta dois deles no mesmo instante: são pares (94, 94), de duração zero, que não aparecem no barcode.
            """,
            """
            - Em 99 o gancho cresce, sem nada novo.
            - Em t = 100, o vértice 100 e as suas duas arestas fecham o anel em volta do centro: 8 vértices e 8 arestas, em rosa. Nasce H₁ em 100.
            - **Por que só vértices e arestas:** um quadrado só entra quando os seus quatro cantos já entraram. Todo quadrado tem um canto na borda (114 ou mais) ou no centro (139): os números nos centros dos quadrados mostram 114 ou mais. Então, em 100, o anel é um laço de arestas sem nada por dentro. É o buraco.
            - Conferência: χ = 8 − 8 = 0 = β₀ − β₁ = 1 − 1.
            - O buraco é o centro claro, o 139, que ainda não entrou.
            - **Se perguntarem "como é uma componente, se não tem quadrado?":**
                - Um complexo cúbico não precisa de quadrados: vértices e arestas sozinhos já são um complexo (de dimensão 1, como uma armação de arame).
                - Componente conexa = vértices ligados por um caminho de **arestas** (vizinhança de 4 pixels; é a definição usada no artigo do Cubical Ripser).
                - O quadrado não muda a conexão: se ele está lá, as 4 arestas dele também estão, e os vértices já estavam ligados. Ele só faz uma coisa: tapar o laço das suas arestas, matando uma classe de H₁.
                - Por isso t = 100 é o exemplo mais limpo de buraco: o anel é uma peça só (arestas ligando os 8 vértices) e oco (nenhum quadrado). Se a conexão exigisse quadrados, nunca haveria buraco.
                - A seção 3 já mostrou isso no passo 7.7: com 25 vértices e 40 arestas, a grade é uma componente com 16 buracos (χ = 25 − 40 = −15 = 1 − 16), e os 16 quadrados tapam esses buracos.
                - Até 119 nada muda: a borda só engrossa o anel e vira uma moldura (24 vértices, 36 arestas, 12 quadrados, χ = 0). Continua sendo uma peça com um buraco, e a barra rosa segue até 139.
            """,
            """
            - Entram as bordas da imagem: 114 à direita, 115 à esquerda, 117 embaixo e 119 em cima. São 16 vértices, 28 arestas e 12 quadrados.
            - β₀ e β₁ não mudam. O que nasce aqui morre no mesmo valor: o vértice 114, por exemplo, entra junto da aresta que o liga ao gancho.
            - Em t = 119 está tudo, menos o centro: o anel continua. É o quadro t = 130 do Otter.
            """,
            """
            - Em t = 139 entra o centro com a sua estrela inferior, as mesmas 9 casas que o 139 tomou no CubeMap: o vértice, 4 arestas e 4 quadrados.
            - Os quadrados tapam o buraco: H₁ morre em 139. A barra rosa vai de 100 a 139, uma persistência de 39.
            - Na imagem: o anel escuro em volta do centro claro dura de 100 a 139.
            """,
        ]
        atual = 90
        evento = None
        anel = VGroup()
        amarelos = []
        for (valores, texto_evento), nota in zip(dados.PARADAS, notas):
            for valor in valores:
                self.play(self.t.animate.set_value(valor), run_time=max(0.8, 0.12 * (valor - atual)), rate_func=linear)
                atual = valor
                # As células de valor t acendem, e os seus números ficam amarelos (os anteriores voltam ao branco).
                entram = [self.transforma_celulas(
                    lambda cubo, mob: acende(mob, d2.dimensao(cubo)) if dados.valor(cubo) == valor else None)]
                for cubo in amarelos:
                    entram.append(self.numeros[cubo].animate.set_fill(COR_NUMERO[d2.dimensao(cubo)]))
                amarelos = [cubo for cubo in self.numeros if dados.valor(cubo) == valor]
                for cubo in amarelos:
                    entram.append(self.numeros[cubo].animate.set_fill(YELLOW, opacity=1).set_stroke(opacity=1))
                if valor == dados.MORTE_H1:
                    estrela = Square(side_length=2.0).move_to(p(2, 2)).set_stroke(YELLOW, width=4)
                    self.play(ShowCreation(estrela))
                    self.play(*entram, run_time=1.5)
                    ponto, numero = marca(1, valor)
                    self.play(GrowFromCenter(ponto), Write(numero), betti[3].animate.set_value(0), FadeOut(anel))
                    self.play(FadeOut(estrela))
                    continue
                self.play(*entram, run_time=1.0)
                if valor == dados.NASCIMENTO_H0:
                    self.barra_h0 = barra(0, valor, np.inf)
                    ponto, numero = marca(0, valor)
                    self.add(self.barra_h0)
                    self.play(GrowFromCenter(ponto), Write(numero), betti[1].animate.set_value(1))
                if valor == dados.NASCIMENTO_H1:
                    for cubo in dados.anel():
                        (x0, x1), (y0, y1) = cubo
                        anel.add(Line(p(x0, y0), p(x1, y1), stroke_color=COR_H1, stroke_width=8))
                    self.play(LaggedStartMap(ShowCreation, anel, lag_ratio=0.1), run_time=1.5)
                    self.add(barra(1, valor, dados.MORTE_H1))
                    ponto, numero = marca(1, valor)
                    self.play(GrowFromCenter(ponto), Write(numero), betti[3].animate.set_value(1))
            novo = entendimento(texto_evento)
            if evento is None:
                self.play(Write(novo))
            else:
                self.play(FadeOut(evento), Write(novo))
            evento = novo
            fecha_passo(self, nota)

        # Último clique: a componente nunca morre; o barcode de G.
        marcador.clear_updaters()
        rotulo_t.clear_updaters()
        self.barra_h0.clear_updaters()
        fim = np.array([x_de(146), Y_BARRA[0], 0])
        infinito = Tex(R"\infty", font_size=30).set_color(COR_H0).next_to(fim, RIGHT, buff=0.12)
        self.play(FadeOut(VGroup(marcador, rotulo_t)), *[self.numeros[cubo].animate.set_fill(COR_NUMERO[d2.dimensao(cubo)]) for cubo in amarelos])
        self.play(self.barra_h0.animate.put_start_and_end_on(self.barra_h0.get_start(), fim), run_time=1.2)
        self.play(Write(infinito))
        final = entendimento(R"O barcode da imagem: $H_0 = (94, \infty)$ e $H_1 = (100, 139)$.")
        self.play(FadeOut(evento), Write(final))
        fecha_passo(self, """
            - A componente nunca morre: (94, ∞), a classe essencial. A imagem inteira é conexa.
            - O barcode de G: H₀ = (94, ∞) e H₁ = (100, 139), o mesmo do barcode (d) de Otter et al.
            - Além desses, a filtração tem 39 pares de duração zero: nascem e morrem no mesmo valor e não aparecem.
            - Até aqui lemos os pares olhando a figura. Na próxima seção, a matriz de bordo, ordenada por esta filtração, e a redução que acha exatamente esses pares sem olhar a figura.
        """)
