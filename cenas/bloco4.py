"""Bloco 4: matriz de bordo e redução de G.

Render: manim-slides render --GL bloco4.py MatrizEReducao
Os números vêm de dados_bloco4.py e são conferidos por verifica_bloco4.py.
Uma seta, um passo: cada fecha_passo fecha um passo, com a nota do que ele mostrou.

À esquerda fica o complexo de G com os valores (como no fim do processo de filtração da seção 4); à direita, a
matriz 81 x 81 como padrão de pontos. Os destaques no complexo são camadas por cima, nunca
animações nas células (ver transforma_celulas no bloco3.py).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from manimlib import *
from manim_slides import Slide

import dados_bloco2 as d2
import dados_bloco3 as d3
import dados_bloco4 as dados
from bloco2 import imagem_g, p
from bloco3 import COR_NUMERO, cinza, entendimento, lugar_do_rotulo, novo_complexo, texto_a_esquerda
from estilo import *

if TYPE_CHECKING:
    from manimlib.typing import ManimColor

N_CEL = len(dados.ORDEM)
MATRIZ_X0 = 1.15  # borda esquerda da matriz
MATRIZ_TOPO = 1.35
MATRIZ_LADO = 4.25
PASSO = MATRIZ_LADO / N_CEL
Y_TEXTO = (2.45, 2.08)  # as duas linhas de texto acima da matriz
Y_LEGENDA = 1.72
COR_LOW = YELLOW
FONTE_MATRIZ = "Wagner et al. (2011), seção 4, Algoritmo 1"
FONTE_REDUCAO = "Edelsbrunner, Letscher e Zomorodian (2002)"


def ponto_da_matriz(linha: int, coluna: int) -> np.ndarray:
    return np.array([MATRIZ_X0 + (coluna + 0.5) * PASSO, MATRIZ_TOPO - (linha + 0.5) * PASSO, 0])


def pontos_da_coluna(coluna: int, linhas: set[int], cor_low: ManimColor | None = None) -> VGroup:
    """Os pontos de uma coluna (ordem da filtração); o low (o último, o mais baixo) na cor dada."""
    grupo = VGroup()
    ordenadas = sorted(linhas)
    for linha in ordenadas:
        cor = cor_low if (cor_low is not None and linha == ordenadas[-1]) else WHITE
        grupo.add(Dot(ponto_da_matriz(linha, coluna), radius=0.026, fill_color=cor))
    return grupo


def faixa_da_coluna(coluna: int, cor: ManimColor = YELLOW, opacidade: float = 0.15) -> Rectangle:
    faixa = Rectangle(width=PASSO, height=MATRIZ_LADO).set_stroke(cor, width=2).set_fill(cor, opacity=opacidade)
    return faixa.move_to([MATRIZ_X0 + (coluna + 0.5) * PASSO, MATRIZ_TOPO - MATRIZ_LADO / 2, 0])


def faixa_da_linha(linha: int, cor: ManimColor = COR_ARESTA, opacidade: float = 0.2) -> Rectangle:
    faixa = Rectangle(width=MATRIZ_LADO, height=PASSO).set_stroke(cor, width=1).set_fill(cor, opacity=opacidade)
    return faixa.move_to([MATRIZ_X0 + MATRIZ_LADO / 2, MATRIZ_TOPO - (linha + 0.5) * PASSO, 0])


def barras_de_valor(indice: dict[d2.Cubo, int]) -> VGroup:
    """O valor de cada célula, em cinza, acima das colunas e à esquerda das linhas, na ordem dada."""
    topo = VGroup()
    lado = VGroup()
    for cubo in dados.ORDEM:
        k = indice[cubo]
        cor = cinza(d3.valor(cubo))
        marca = Rectangle(width=PASSO, height=0.1).set_stroke(width=0).set_fill(cor, opacity=1)
        topo.add(marca.move_to([MATRIZ_X0 + (k + 0.5) * PASSO, MATRIZ_TOPO + 0.08, 0]))
        marca = Rectangle(width=0.1, height=PASSO).set_stroke(width=0).set_fill(cor, opacity=1)
        lado.add(marca.move_to([MATRIZ_X0 - 0.08, MATRIZ_TOPO - (k + 0.5) * PASSO, 0]))
    return VGroup(topo, lado)


def destaque(cubo: d2.Cubo, cor: ManimColor, largura: float = 10) -> VMobject:
    """Uma camada por cima da célula no complexo de G: anel no vértice, traço na aresta, cor no quadrado."""
    (x0, x1), (y0, y1) = cubo
    dim = d2.dimensao(cubo)
    if dim == 0:
        return Circle(radius=0.2, stroke_color=cor, stroke_width=5).move_to(p(x0, y0))
    if dim == 1:
        return Line(p(x0, y0), p(x1, y1), stroke_color=cor, stroke_width=largura)
    return Polygon(p(x0, y0), p(x1, y0), p(x1, y1), p(x0, y1)).set_fill(cor, opacity=0.55).set_stroke(width=0)


def destaques(cubos: list[d2.Cubo], cor: ManimColor, largura: float = 10) -> VGroup:
    return VGroup(*[destaque(c, cor, largura) for c in cubos])


def linhas_de_texto(*textos: str) -> VGroup:
    grupo = VGroup()
    for texto, y in zip(textos, Y_TEXTO):
        grupo.add(texto_a_esquerda(texto, y))
    return grupo


class MatrizEReducao(Slide):
    """A matriz de bordo de G: o que é, como se ordena, como se reduz e o que os pares dizem."""

    def construct(self) -> None:
        self.entrada()
        self.o_que_e()
        self.todas_as_colunas()
        self.ordenacao()
        self.o_low()
        self.o_anel()
        self.o_miolo()
        self.pares()
        self.fecho()

    def troca_texto(self, novo: VGroup, run_time: float = 2) -> None:
        self.play(FadeOut(self.texto), Write(novo), run_time=run_time)
        self.texto = novo

    def troca_linha(self, texto: str, run_time: float = 2) -> None:
        """Escreve a linha de entendimento, tirando a anterior."""
        nova = entendimento(texto)
        if self.linha is None:
            self.play(Write(nova), run_time=run_time)
        else:
            self.play(FadeOut(self.linha), Write(nova), run_time=run_time)
        self.linha = nova

    # ---------------------------------------------------------- entrada
    def entrada(self) -> None:
        mapa = fluxo_persistencia(icone_dados=imagem_g(0.2))
        self.indice = indice_secao(5)
        self.play(Write(self.indice))
        apresenta_fluxo(self, mapa)
        etapa = VGroup(*mapa["sequencia"][3:6])  # filtração e matriz, a matriz ordenada, a redução
        realce = SurroundingRectangle(etapa, buff=0.12).set_stroke(YELLOW, width=3)
        resto = VGroup(mapa["moldura"], mapa["setas"], *mapa["sequencia"][:3], mapa["sequencia"][6])
        # O realce cobre três caixas: desenhado devagar e seguro na tela antes de o fluxo sair.
        self.play(ShowCreation(realce), resto.animate.set_opacity(0.2), run_time=2)
        pausa(self, 1.5)

        # O complexo de G aceso, com os valores, como no fim do processo de filtração da seção 4.
        self.complexo = novo_complexo()
        self.numeros = VGroup()
        for cubo in d3.celulas():
            dim = d2.dimensao(cubo)
            if dim == 1:
                continue
            numero = Tex(str(d3.valor(cubo)), font_size=20 if dim == 0 else 18).set_color(COR_NUMERO[dim])
            self.numeros.add(numero.set_backstroke(BLACK, 3).move_to(lugar_do_rotulo(cubo)))
        self.cabecalho = titulo("Matriz de bordo e redução")
        self.play(FadeOut(VGroup(resto, etapa, realce)), run_time=1.2)
        self.play(FadeIn(self.complexo), FadeIn(self.numeros), Write(self.cabecalho), run_time=1.5)

    # ---------------------------------------------------------- 5.1 (o que é a matriz de bordo)
    def o_que_e(self) -> None:
        self.borda = Rectangle(width=MATRIZ_LADO, height=MATRIZ_LADO).set_stroke(GREY_B, width=1.5)
        self.borda.move_to([MATRIZ_X0 + MATRIZ_LADO / 2, MATRIZ_TOPO - MATRIZ_LADO / 2, 0])
        # Todos os 144 pontos, na ordem em que as casas estão guardadas; o mesmo ponto depois se move
        # para a ordem da filtração.
        self.pontos = VGroup()
        self.pontos_de = {}
        for cubo in dados.ORDEM:
            for face in d2.faces_primarias(cubo):
                ponto = Dot(ponto_da_matriz(dados.INDICE_GUARDADO[face], dados.INDICE_GUARDADO[cubo]),
                            radius=0.026, fill_color=WHITE)
                self.pontos.add(ponto)
                self.pontos_de.setdefault(cubo, VGroup()).add(ponto)
        self.texto = linhas_de_texto("uma coluna para cada célula;", "na coluna, um ponto em cada face dela")
        self.fonte = rodape(FONTE_MATRIZ)
        self.linha = None
        self.play(ShowCreation(self.borda), Write(self.texto), Write(self.fonte), run_time=2)

        aresta = d2.faces_primarias(d2.QUADRADO)[0]
        exemplos = [CENTRO_V, aresta, d2.QUADRADO]
        rotulos = ["vazia", "2 pontos", "4 pontos"]
        self.exemplos = VGroup()
        x_rotulos = MATRIZ_X0 + (max(dados.INDICE_GUARDADO[c] for c in exemplos) + 3) * PASSO
        for n, (cubo, rotulo) in enumerate(zip(exemplos, rotulos)):
            j = dados.INDICE_GUARDADO[cubo]
            faixa = faixa_da_coluna(j)
            # Dentro da matriz, à direita das três colunas (vizinhas demais para rótulos em cima),
            # com um traço até a coluna. Nesta hora a matriz ainda está vazia ali.
            y = MATRIZ_TOPO - 0.35 - 0.35 * n
            texto_rotulo = TexText(rotulo, font_size=20).set_color(YELLOW)
            texto_rotulo.move_to([x_rotulos + 0.15 + texto_rotulo.get_width() / 2, y, 0])
            traco = Line([MATRIZ_X0 + (j + 0.5) * PASSO, y, 0], [x_rotulos + 0.08, y, 0], stroke_color=YELLOW, stroke_width=1.5)
            nome = VGroup(traco, texto_rotulo)
            faces = d2.faces_primarias(cubo)
            linhas = VGroup(*[faixa_da_linha(dados.INDICE_GUARDADO[f]) for f in faces])
            celula = destaque(cubo, YELLOW, 12)
            de_faces = destaques(faces, COR_ARESTA if d2.dimensao(cubo) == 2 else COR_VERTICE, 12)
            self.play(FadeIn(celula), FadeIn(faixa), Write(nome), run_time=1)
            if len(faces) > 0:
                self.play(LaggedStartMap(FadeIn, de_faces, lag_ratio=0.2), FadeIn(linhas),
                          LaggedStartMap(GrowFromCenter, self.pontos_de[cubo], lag_ratio=0.2), run_time=1.5)
            else:
                pausa(self, 1.5)
            self.play(FadeOut(VGroup(celula, de_faces, linhas)), faixa.animate.set_fill(opacity=0.06), run_time=0.8)
            self.exemplos.add(VGroup(faixa, nome))
        self.troca_linha("Vértice: coluna vazia. Aresta: os seus 2 vértices. Quadrado: as suas 4 arestas.")
        fecha_passo(self, """
            - Voltamos ao fluxo: falta a matriz de bordo ordenada e a redução, a última etapa antes do diagrama.
            - A matriz de bordo tem uma coluna para cada célula e uma linha para cada célula. Na coluna de uma célula há um ponto (um 1) em cada face dela; o resto é 0.
            - Três colunas de G, do bloco que já conhecemos: o vértice 139 do centro não tem bordo, a coluna é vazia. A aresta e₁ tem dois vértices: dois pontos. O quadrado [1,2]×[2,3] tem as quatro arestas: quatro pontos. É o ∂Q = e₁ + e₂ + e₃ + e₄ da seção 3, escrito como coluna.
        """)

    def todas_as_colunas(self) -> None:
        resto = VGroup()
        for cubo in dados.ORDEM:
            if cubo not in (CENTRO_V, d2.faces_primarias(d2.QUADRADO)[0], d2.QUADRADO):
                resto.add(*self.pontos_de.get(cubo, VGroup()))
        texto = linhas_de_texto("as 81 colunas: o complexo inteiro;", "na ordem em que as casas estão guardadas")
        self.troca_texto(texto)
        self.play(FadeOut(self.exemplos), LaggedStartMap(FadeIn, resto, lag_ratio=0.02), run_time=3)
        self.add(self.pontos)  # o grupo inteiro na cena, para ordenar de uma vez
        self.troca_linha("A matriz de bordo é o complexo em forma de tabela: quem é face de quem.")
        fecha_passo(self, """
            - Todas as 81 colunas. A matriz guarda o complexo inteiro: com ela, um programa sabe quem é face de quem sem desenhar nada.
            - São só 144 pontos em 6561 casas: duas por aresta e quatro por quadrado. A matriz é esparsa.
            - Por enquanto as colunas estão na ordem em que as casas estão guardadas no CubeMap, linha a linha. Repare que há pontos dos dois lados da diagonal.
        """)

    # ---------------------------------------------------------- 5.2 (a ordenação)
    def ordenacao(self) -> None:
        barras = barras_de_valor(dados.INDICE_GUARDADO)
        ordenadas = barras_de_valor(dados.INDICE)
        destino = self.pontos.copy()
        k = 0
        for cubo in dados.ORDEM:
            for face in d2.faces_primarias(cubo):
                destino[k].move_to(ponto_da_matriz(dados.INDICE[face], dados.INDICE[cubo]))
                k += 1
        diagonal = DashedLine(self.borda.get_corner(UL), self.borda.get_corner(DR), stroke_color=GREY_C, stroke_width=1.5)
        degrade = VGroup()
        for i in range(10):
            degrade.add(Rectangle(width=0.06, height=0.12).set_stroke(width=0).set_fill(cinza(94 + 45 * i / 9), opacity=1))
        legenda = VGroup(degrade.arrange(RIGHT, buff=0), TexText("valor: de 94 a 139", font_size=24))
        legenda.arrange(RIGHT, buff=0.15)
        legenda.move_to([MATRIZ_X0 + legenda.get_width() / 2, Y_LEGENDA, 0])
        texto = linhas_de_texto("na ordem da filtração: valor crescente;", "no empate, a face antes da célula")
        self.play(FadeIn(barras), Write(legenda), run_time=1.5)
        self.troca_texto(texto)
        self.play(Transform(self.pontos, destino), Transform(barras, ordenadas), run_time=4)
        self.play(ShowCreation(diagonal), run_time=1.5)
        # Os mesmos pontos, agrupados por coluna para a redução (troca invisível).
        self.colunas = {}
        for j, cubo in enumerate(dados.ORDEM):
            self.colunas[j] = pontos_da_coluna(j, dados.coluna(cubo))
        self.remove(self.pontos)
        self.add(*self.colunas.values())
        self.troca_linha("Na ordem da filtração, toda face vem antes: os pontos ficam acima da diagonal.")
        fecha_passo(self, """
            - Agora a ordem da filtração: as colunas (e as linhas) na ordem em que as células entram na filtração. A faixa de cinza em cima mostra o valor de cada coluna: escuro (94) à esquerda, claro (139) à direita.
            - No empate, a face antes da célula: o vértice antes das arestas dele, a aresta antes do quadrado.
            - Os pontos se rearranjam e todos ficam acima da diagonal: a face de uma célula sempre entrou antes dela. A matriz é triangular superior.
            - Ler a matriz da esquerda para a direita é refazer o processo de filtração da seção 4, célula por célula.
        """)
        self.barras = barras
        self.legenda_valor = legenda
        self.diagonal = diagonal

    # ---------------------------------------------------------- 5.3 (a redução)
    def coluna_vira(self, j: int, linhas: set[int], cor_low: ManimColor = COR_LOW) -> AnimationGroup:
        """Troca os pontos da coluna j pelos da coluna nova."""
        novo = pontos_da_coluna(j, linhas, cor_low)
        antigo = self.colunas[j]
        self.colunas[j] = novo
        anima = []
        if len(antigo) > 0:
            anima.append(FadeOut(antigo))
        if len(novo) > 0:
            anima.append(FadeIn(novo))
        return AnimationGroup(*anima)

    def varre(self, inicio: int, fim: int, run_time: float) -> None:
        """As colunas de inicio a fim - 1 já na forma reduzida, com o low marcado; o cursor anda junto."""
        passos, _ = dados.reducao()
        anima = []
        for j in range(inicio, fim):
            final = passos[j][1]
            if final or len(self.colunas[j]) > 0:
                anima.append(self.coluna_vira(j, final))
        juntas = [self.cursor.animate.move_to(faixa_da_coluna(fim - 1))]
        if anima:
            juntas.append(LaggedStart(*anima, lag_ratio=0.1))
        self.play(*juntas, run_time=run_time, rate_func=linear)

    def o_low(self) -> None:
        k = dados.primeira_aresta_que_junta()
        aresta = dados.ORDEM[k]
        pontas = sorted(dados.coluna(aresta))
        mais_nova = dados.ORDEM[pontas[-1]]
        mais_velha = dados.ORDEM[pontas[0]]
        texto = linhas_de_texto("low: a face mais nova da coluna", "(o último ponto, o mais baixo)")
        legenda_low = VGroup(Dot(radius=0.05, fill_color=COR_LOW), TexText("low", font_size=24)).arrange(RIGHT, buff=0.12)
        legenda_low.move_to([MATRIZ_X0 + MATRIZ_LADO - legenda_low.get_width() / 2, Y_LEGENDA, 0])
        fonte = rodape(FONTE_REDUCAO)
        self.cursor = faixa_da_coluna(k, YELLOW, 0.1)
        marca_velha = destaque(mais_velha, WHITE)
        marca_nova = destaque(mais_nova, COR_LOW)
        self.troca_texto(texto)
        self.play(FadeOut(self.fonte), Write(fonte), Write(legenda_low), FadeIn(self.cursor))
        self.fonte = fonte
        realce_aresta = destaque(aresta, YELLOW, 12)
        self.play(FadeIn(realce_aresta), FadeIn(marca_velha), FadeIn(marca_nova), run_time=1.2)
        self.play(self.coluna_vira(k, pontas))
        self.troca_linha("Aresta com low novo: juntou duas componentes, e a mais nova morre.")
        fecha_passo(self, """
            - Agora a redução: ler as colunas da esquerda para a direita, na ordem da filtração, e perguntar o que cada célula faz.
            - O low de uma coluna é a face mais nova dela: o último ponto, o mais baixo na matriz.
            - **A regra da redução** (aparece em ação no próximo passo): se uma coluna anterior já tem o mesmo low, some aquela coluna a esta. Em ℤ₂ o low comum se cancela e o low sobe para uma face mais velha; somar nunca o faz descer. Repita até o low ser inédito ou a coluna zerar.
            - A primeira aresta de G liga dois vértices 94. O low é o vértice mais novo dos dois (o que entrou por último). Nenhuma coluna antes dela tem esse low, então ele fica com ela.
            - O que isso quer dizer: a aresta juntou duas componentes, e a mais nova morre. É a regra do mais velho. Aqui as duas nasceram em 94 e a aresta é de 94: um par de duração zero.
            - **Por que o low importa:** no fim da redução, cada low é um par do diagrama. A feição nasce na célula da linha do low e morre na célula da coluna. Uma coluna que zera é uma célula que cria (componente ou buraco). O diagrama é a lista de lows.
        """)
        self.legenda_low = legenda_low
        self.marcas = VGroup(realce_aresta, marca_velha, marca_nova)
        self.k_aresta = k

    def o_anel(self) -> None:
        passos, _ = dados.reducao()
        fecha = dados.aresta_que_fecha_o_anel()
        k = dados.INDICE[fecha]
        somadas = passos[k][0]
        estados = dados.estados_da_coluna(k)
        texto = linhas_de_texto("low repetido: some a coluna dona dele", R"(em $\mathbb{Z}_2$, ponto repetido some)")
        self.troca_texto(texto)
        self.play(FadeOut(self.marcas), FadeOut(self.linha))
        self.linha = None
        self.varre(self.k_aresta + 1, k, run_time=2.5)
        self.play(self.cursor.animate.move_to(faixa_da_coluna(k)))
        caminho = VGroup(destaque(fecha, COR_H1))
        pontas = VGroup(*[destaque(dados.ORDEM[r], COR_LOW) for r in sorted(estados[0])])
        self.play(ShowCreation(caminho[0]), FadeIn(pontas), self.coluna_vira(k, estados[0]), run_time=1.5)
        for j, depois in zip(somadas, estados[1:]):
            faixa = faixa_da_coluna(j, COR_H1, 0.3)
            nova_aresta = destaque(dados.ORDEM[j], COR_H1)
            caminho.add(nova_aresta)
            novas_pontas = VGroup(*[destaque(dados.ORDEM[r], COR_LOW) for r in sorted(depois)])
            self.play(FadeIn(faixa), ShowCreation(nova_aresta), run_time=0.6)
            self.play(self.coluna_vira(k, depois), FadeOut(pontas), FadeIn(novas_pontas), FadeOut(faixa), run_time=0.8)
            pontas = novas_pontas
        zera = faixa_da_coluna(k, COR_H1, 0.25)
        self.play(FadeIn(zera), Indicate(caminho, color=COR_H1, scale_factor=1.03))
        self.troca_linha("Cada soma anda uma aresta; o anel fechou e a coluna zerou: nasce o buraco.")
        fecha_passo(self, f"""
            - O cursor passa pelas arestas do gancho: todas têm low novo (juntam componentes).
            - Na coluna {k}, a aresta de valor 100 que fecha o anel. A coluna dela tem as duas pontas. O low (a ponta mais nova) já é de outra coluna: a de uma aresta do anel. A regra manda somar essa coluna.
            - Em ℤ₂, ponto repetido some: a ponta comum cancela e sobra a outra ponta da aresta somada. No complexo, o caminho rosa ganhou uma aresta, e a coluna guarda as duas pontas do caminho.
            - Cada soma anda uma aresta pelo anel. Depois de 7 somas, o caminho volta ao começo: as pontas se encontram, cancelam, e a coluna zera.
            - Coluna que zera: a célula criou algo. Esta aresta fechou um laço: nasce o buraco (H₁) em 100. Ninguém olhou a figura: foram 7 somas de colunas.
        """)
        self.caminho = caminho
        self.zera = zera
        self.k_fecha = k
        self.extras = VGroup(pontas)

    def o_miolo(self) -> None:
        passos, _ = dados.reducao()
        ultimo = dados.ultimo_quadrado_do_miolo()
        k = dados.INDICE[ultimo]
        somadas = passos[k][0]
        estados = dados.estados_da_coluna(k)
        texto = linhas_de_texto("o último quadrado do miolo: low repetido,", "soma os outros 3 quadrados do miolo")
        self.troca_texto(texto)
        self.play(FadeOut(self.extras), FadeOut(self.linha))
        self.linha = None
        self.varre(self.k_fecha + 1, k, run_time=4)
        self.play(self.cursor.animate.move_to(faixa_da_coluna(k)))
        quadrados = VGroup(destaque(ultimo, COR_QUADRADO))
        contorno = destaques([dados.ORDEM[r] for r in estados[0]], COR_H1)
        self.play(FadeOut(self.caminho), FadeIn(quadrados[0]), ShowCreation(contorno), self.coluna_vira(k, estados[0]), run_time=1.5)
        for j, depois in zip(somadas, estados[1:]):
            faixa = faixa_da_coluna(j, COR_QUADRADO, 0.3)
            novo = destaque(dados.ORDEM[j], COR_QUADRADO)
            quadrados.add(novo)
            novo_contorno = destaques([dados.ORDEM[r] for r in depois], COR_H1)
            self.play(FadeIn(faixa), FadeIn(novo), run_time=0.6)
            self.play(self.coluna_vira(k, depois, COR_H1 if j == somadas[-1] else None), FadeOut(contorno),
                      FadeIn(novo_contorno), FadeOut(faixa), run_time=0.9)
            contorno = novo_contorno
        aresta_100 = destaque(dados.aresta_que_fecha_o_anel(), COR_LOW, 14)
        par = DashedLine(ponto_da_matriz(self.k_fecha, k), ponto_da_matriz(self.k_fecha, self.k_fecha),
                         stroke_color=COR_H1, stroke_width=2)
        self.play(ShowCreation(aresta_100), ShowCreation(par), Indicate(self.zera, color=COR_H1))
        self.troca_linha(R"Sobra o anel; o low é a aresta de 100: o buraco dela morre aqui. Par $(100, 139)$.")
        fecha_passo(self, f"""
            - O cursor passa rápido pela borda (114 a 119) e pelo centro. Ali estão os outros laços pequenos, que nascem e são tapados no mesmo valor.
            - A última coluna é o último quadrado do miolo (139). A coluna dele tem as 4 arestas. O low já tem dono: outro quadrado do miolo. Soma.
            - Somar quadrados é juntá-los: as arestas que os dois dividem aparecem duas vezes e somem (1 + 1 = 0). A coluna guarda o contorno do conjunto: 4, 6, 8 arestas.
            - Depois de juntar os 4 quadrados do miolo, o contorno é o anel inteiro. O low agora é a aresta mais nova do anel: a de 100, cuja coluna zerou. Ninguém ficou com esse low: ele é desta coluna.
            - Coluna que não zera: a célula matou a feição que nasceu no low. Este quadrado tapou o buraco que a aresta de 100 abriu. Par (100, 139).
        """)
        self.extras = VGroup(quadrados, contorno, aresta_100, par, self.zera)

    # ---------------------------------------------------------- 5.4 (os pares)
    def pares(self) -> None:
        passos, _ = dados.reducao()
        recolore = []
        n_h0 = 0
        n_h1 = 0
        for j in range(N_CEL):
            _, final, low = passos[j]
            if low is None:
                continue
            dim = d2.dimensao(dados.ORDEM[j])
            if dim == 1:
                n_h0 += 1
            else:
                n_h1 += 1
            recolore.append(self.coluna_vira(j, final, COR_H0 if dim == 1 else COR_H1))
        essencial = [par for par in dados.pares() if par[2] == float("inf")][0][3]
        faixa_inf = faixa_da_coluna(essencial, COR_H0, 0.2)
        infinito = Tex(R"\infty", font_size=28).set_color(COR_H0).next_to(faixa_inf, UP, buff=0.2)

        # À esquerda, no lugar do complexo, o barcode da filtração da seção 4.
        eixo = EixoNumerado((90, 140, 10), unit_size=0.08, font_size=20)
        eixo.shift(np.array([-5.8, -1.2, 0]) - eixo.n2p(90))
        barra_h0 = Line(np.array([eixo.n2p(94)[0], 0.2, 0]), np.array([eixo.n2p(146)[0], 0.2, 0]),
                        stroke_color=COR_H0, stroke_width=10)
        barra_h1 = Line(np.array([eixo.n2p(100)[0], -0.4, 0]), np.array([eixo.n2p(139)[0], -0.4, 0]),
                        stroke_color=COR_H1, stroke_width=10)
        rotulos = VGroup(
            Tex(R"(94, \infty)", font_size=26).set_color(COR_H0).next_to(barra_h0, UP, buff=0.12),
            Tex(R"(100, 139)", font_size=26).set_color(COR_H1).next_to(barra_h1, UP, buff=0.12),
        )
        titulo_barcode = TexText("o barcode da filtração (seção 4)", font_size=28).move_to([-3.6, 1.2, 0])
        texto = linhas_de_texto("cada low é um par: nasce no low, morre na coluna", f"{n_h0} em $H_0$ (teal) e {n_h1} em $H_1$ (rosa)")
        self.play(FadeOut(self.extras), FadeOut(self.complexo), FadeOut(self.numeros), FadeOut(self.cursor),
                  FadeOut(self.legenda_low), FadeOut(self.legenda_valor), FadeOut(self.linha), run_time=1.5)
        self.linha = None
        self.troca_texto(texto)
        self.play(LaggedStart(*recolore, lag_ratio=0.05), run_time=3)
        self.play(FadeIn(faixa_inf), Write(infinito))
        self.play(Write(titulo_barcode))
        cria_eixo(self, eixo, tempo=1.5)
        self.play(ShowCreation(barra_h0), ShowCreation(barra_h1), Write(rotulos), run_time=2)
        self.troca_linha(R"A matriz acha, sem olhar a figura, os pares da filtração: $(94, \infty)$ e $(100, 139)$.")
        fecha_passo(self, f"""
            - Cada low é um par: a feição nasce na célula da linha do low e morre na célula da coluna. O par é (valor da linha, valor da coluna).
            - Lows em colunas de arestas são mortes de componentes (H₀, teal): {n_h0}. Lows em colunas de quadrados são mortes de buracos (H₁, rosa): {n_h1}.
            - Dos 40 pares, 39 nascem e morrem no mesmo valor: duração zero, não aparecem no barcode. Sobra o (100, 139).
            - A coluna {essencial} (um vértice 94) é vazia e a linha dela nunca é low: essa componente nunca morre, (94, ∞).
            - À esquerda, o barcode da filtração da seção 4: é o mesmo. A matriz achou, só somando colunas, o que vimos olhando.
        """)
        self.extras = VGroup(titulo_barcode, eixo, barra_h0, barra_h1, rotulos, faixa_inf, infinito,
                             self.texto, self.borda, self.diagonal, self.barras, *self.colunas.values())

    # ---------------------------------------------------------- fecho: o fim do fluxo
    def fecho(self) -> None:
        mapa = fluxo_persistencia(icone_dados=imagem_g(0.2))
        diagrama = mapa["objetos"][3]
        realce = SurroundingRectangle(diagrama[0], buff=0.08).set_stroke(YELLOW, width=3)
        self.play(FadeOut(self.extras), FadeOut(self.fonte), FadeOut(self.cabecalho), FadeOut(self.linha), run_time=1.5)
        apresenta_fluxo(self, mapa)
        self.play(ShowCreation(realce))
        linha = entendimento(R"O fluxo chega ao diagrama: na imagem, $H_0 = (94, \infty)$ e $H_1 = (100, 139)$.")
        linha.set_y(-2.4)
        self.play(Write(linha), run_time=2)
        fecha_passo(self, """
            - Fim do fluxo da homologia persistente: dos dados (G) ao complexo cúbico, à filtração no CubeMap, à matriz de bordo ordenada, à redução e ao diagrama.
            - A sacada do artigo apareceu em todas as etapas: tudo foi feito direto na grade, sem triangular.
        """)


CENTRO_V = ((2, 2), (2, 2))  # o vértice 139
