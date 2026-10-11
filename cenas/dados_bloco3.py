"""Dados do bloco 3 (a filtração de G). As cenas e verifica_bloco3.py leem daqui.

Mesmas coordenadas do bloco 2: um cubo é ((x0, x1), (y0, y1)) na grade de G, com o pixel
(i, j) no ponto (j, 4 - i). A casa do cubo no CubeMap é (x0 + x1, y0 + y1), com a primeira
coordenada na horizontal e a segunda para cima, como no fim da seção 3.
"""
from __future__ import annotations

import itertools
from collections.abc import Callable

import numpy as np

import dados_bloco2 as d

G = d.G
N = d.N


def vertices_do_cubo(cubo: d.Cubo) -> list[tuple[int, int]]:
    (x0, x1), (y0, y1) = cubo
    return sorted(set(itertools.product((x0, x1), (y0, y1))))


def valor_do_vertice(x: int, y: int) -> int:
    return int(G[N - 1 - y, x])


def valor(cubo: d.Cubo) -> int:
    """Construção V de Wagner et al.: a célula recebe o máximo dos seus vértices."""
    return max(valor_do_vertice(x, y) for x, y in vertices_do_cubo(cubo))


def valor_minimo(cubo: d.Cubo) -> int:
    """A regra errada, só para o contraexemplo."""
    return min(valor_do_vertice(x, y) for x, y in vertices_do_cubo(cubo))


def casa(cubo: d.Cubo) -> tuple[int, int]:
    (x0, x1), (y0, y1) = cubo
    return (x0 + x1, y0 + y1)


def celulas() -> list[d.Cubo]:
    """As 81 células de G, por dimensão crescente."""
    por_dim = d.complexo_da_grade(N)
    return por_dim[0] + por_dim[1] + por_dim[2]


# ------------------------------------------------------------------ 4.1: o bloco ao lado do buraco
# O quadrado [1,2] x [2,3] da seção 3, com três vértices 94 e o 139 do centro.
BLOCO = d.QUADRADO
T_CONTRAEXEMPLO = 94


def faces_do_bloco() -> list[d.Cubo]:
    """O quadrado, as arestas e1..e4 (na ordem do bloco 2) e os quatro vértices."""
    return [BLOCO] + d.faces_primarias(BLOCO) + [((x, x), (y, y)) for x, y in vertices_do_cubo(BLOCO)]


# ------------------------------------------------------------------ 4.2: o Algoritmo 1 no CubeMap
def ordem_dos_valores() -> list[int]:
    """Os valores distintos dos pixels, do maior para o menor."""
    return sorted({int(v) for v in G.flatten()}, reverse=True)


def reivindicacao() -> dict[tuple[int, int], tuple[tuple[int, int], int]]:
    """Algoritmo 1 de Wagner et al.: os pixels em ordem decrescente; cada um toma as casas
    vizinhas (ele e as suas cofaces) ainda livres. Devolve {casa: (casa do vértice dono, ordem)}."""
    pixels = []
    for x in range(N):
        for y in range(N):
            pixels.append((valor_do_vertice(x, y), x, y))
    pixels.sort(reverse=True)
    dono = {}
    for ordem, (_, x, y) in enumerate(pixels):
        for da in (-1, 0, 1):
            for db in (-1, 0, 1):
                a, b = 2 * x + da, 2 * y + db
                if 0 <= a <= 2 * (N - 1) and 0 <= b <= 2 * (N - 1) and (a, b) not in dono:
                    dono[(a, b)] = ((2 * x, 2 * y), ordem)
    return dono


def indices_da_filtracao() -> dict[tuple[int, int], int]:
    """Os índices do Algoritmo 1 (linha 5): atribuídos do maior para o menor, na ordem em que
    as casas são tomadas. Dentro da estrela de um vértice, as células de dimensão maior recebem
    índice antes (maior), para que cada face fique antes das suas cofaces."""
    dono = reivindicacao()
    por_vertice = {}
    for casa_, (vertice, ordem) in dono.items():
        por_vertice.setdefault(ordem, []).append(casa_)
    indice = {}
    proximo = len(dono) - 1
    for ordem in sorted(por_vertice):
        casas = sorted(por_vertice[ordem], key=lambda c: -(c[0] % 2 + c[1] % 2))
        for c in casas:
            indice[c] = proximo
            proximo -= 1
    return indice


# ------------------------------------------------------------------ 4.3: o processo de filtração
def subnivel(t: float, f: Callable[[d.Cubo], int] = valor) -> list[d.Cubo]:
    selecionadas = []
    for cubo in celulas():
        if f(cubo) <= t:
            selecionadas.append(cubo)
    return selecionadas


def _posto_z2(matriz: np.ndarray) -> int:
    m = matriz.copy() % 2
    posto = 0
    linhas, colunas = m.shape
    for c in range(colunas):
        pivo = None
        for k in range(posto, linhas):
            if m[k, c]:
                pivo = k
                break
        if pivo is None:
            continue
        m[[posto, pivo]] = m[[pivo, posto]]
        for k in range(linhas):
            if k != posto and m[k, c]:
                m[k] ^= m[posto]
        posto += 1
    return posto


def betti(cubos: list[d.Cubo]) -> tuple[int, int]:
    """(β0, β1) de um subcomplexo dado pela lista dos seus cubos, sobre Z2."""
    por_dim = {0: [], 1: [], 2: []}
    for cubo in cubos:
        por_dim[d.dimensao(cubo)].append(cubo)
    postos = {}
    for k in (1, 2):
        indice = {c: i for i, c in enumerate(por_dim[k - 1])}
        matriz = np.zeros((len(por_dim[k - 1]), len(por_dim[k])), dtype=np.uint8)
        for j, cubo in enumerate(por_dim[k]):
            for face in d.faces_primarias(cubo):
                matriz[indice[face], j] = 1
        postos[k] = _posto_z2(matriz) if matriz.size else 0
    return len(por_dim[0]) - postos[1], len(por_dim[1]) - postos[1] - postos[2]


# As paradas do processo de filtração, uma por clique: (valores que entram, texto do evento).
PARADAS = [
    ([94], R"$t = 94$: nasce uma componente ($H_0$)"),
    ([99, 100], R"$t = 100$: o anel fecha sem nenhum quadrado dentro: nasce um buraco ($H_1$)"),
    ([114, 115, 117, 119], R"de 114 a 119 entra a borda: $\beta_0$ e $\beta_1$ não mudam"),
    ([139], R"$t = 139$: o centro tapa o buraco e $H_1$ morre"),
]
NASCIMENTO_H0 = 94
NASCIMENTO_H1, MORTE_H1 = 100, 139


def anel() -> list[d.Cubo]:
    """As arestas presentes em t = 100: o ciclo de H1."""
    arestas = []
    for cubo in subnivel(NASCIMENTO_H1):
        if d.dimensao(cubo) == 1:
            arestas.append(cubo)
    return arestas


def estrela_do_centro() -> list[d.Cubo]:
    """As células cujo maior vértice é o centro (2, 2), o pixel 139."""
    estrela = []
    for cubo in celulas():
        if (2, 2) in vertices_do_cubo(cubo) and valor(cubo) == valor_do_vertice(2, 2):
            estrela.append(cubo)
    return estrela
