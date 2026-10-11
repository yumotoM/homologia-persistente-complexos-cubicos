"""Dados do bloco 2 (construção do complexo cúbico). As cenas e verifica_bloco2.py leem daqui.

Coordenadas de grade: o pixel (i, j) da imagem vira o ponto (j, 4 - i), com a linha 0 no topo.
"""
from __future__ import annotations

import itertools

import numpy as np

Intervalo = tuple[int, int]  # (k, k) ou (k, k + 1)
Cubo = tuple[Intervalo, ...]  # um intervalo por eixo
Ponto = tuple[float, float]
Retangulo = tuple[float, float, float, float]  # (x0, x1, y0, y1)
Segmento = tuple[Ponto, Ponto]

# Otter et al. (2017), Fig. 2(b). A construção deles é a de Wagner et al. (a referência [157]).
G = np.array([
    [115, 119, 119, 119, 119],
    [115, 94, 94, 94, 114],
    [115, 94, 139, 100, 114],
    [115, 94, 99, 99, 114],
    [115, 117, 117, 117, 117],
])
N = G.shape[0]


# ------------------------------------------------------------------ cubos
# Um intervalo elementar é (k, k) ou (k, k + 1); um cubo é uma tupla de intervalos.

def dimensao(cubo: Cubo) -> int:
    return sum(1 for a, b in cubo if a != b)


def faces_primarias(cubo: Cubo) -> list[Cubo]:
    """bdr Q = união de Q1 x ... x bdr Qi x ... x Qd: troca um fator não degenerado por uma ponta."""
    faces = []
    for i, (a, b) in enumerate(cubo):
        if a == b:
            continue
        for ponta in (a, b):
            faces.append(cubo[:i] + ((ponta, ponta),) + cubo[i + 1:])
    return faces


def complexo_da_grade(n: int) -> dict[int, list[Cubo]]:
    """Todos os cubos elementares de [0, n-1]^2, por dimensão."""
    intervalos = [(k, k) for k in range(n)] + [(k, k + 1) for k in range(n - 1)]
    por_dim = {0: [], 1: [], 2: []}
    for cubo in itertools.product(intervalos, repeat=2):
        por_dim[dimensao(cubo)].append(cubo)
    return por_dim


# Exemplos dos passos 7.3 a 7.5: células de verdade do complexo de G.
EXEMPLOS_PRODUTO = [
    ((1, 1), (2, 2)),
    ((1, 2), (2, 2)),
    ((1, 1), (2, 3)),
    ((1, 2), (2, 3)),
]
QUADRADO = ((1, 2), (2, 3))
VOXEL = ((1, 2), (2, 3), (0, 1))


# Nomes do passo de ∂ em Z2: arestas na ordem de faces_primarias(QUADRADO), vértices pelos cantos.
NOMES_VERTICES = {(1, 2): "v_1", (2, 2): "v_2", (1, 3): "v_3", (2, 3): "v_4"}
NOMES_ARESTAS = ["e_1", "e_2", "e_3", "e_4"]


def bordo_das_arestas() -> dict[str, tuple[str, ...]]:
    """∂e_i em nomes: {"e_1": ("v_1", "v_3"), ...}."""
    bordos = {}
    for nome, aresta in zip(NOMES_ARESTAS, faces_primarias(QUADRADO)):
        vertices = []
        for v in faces_primarias(aresta):
            vertices.append(NOMES_VERTICES[(v[0][0], v[1][0])])
        bordos[nome] = tuple(sorted(vertices))
    return bordos


def bordo_do_bordo(cubo: Cubo) -> dict[Cubo, int]:
    """Quantas vezes cada vértice aparece em ∂∂Q; em Z2 tudo deve ser par."""
    contagem = {}
    for aresta in faces_primarias(cubo):
        for vertice in faces_primarias(aresta):
            contagem[vertice] = contagem.get(vertice, 0) + 1
    return contagem


# ------------------------------------------------------------------ Dlotko e Wanner, Fig. 2
# Retângulos lidos da figura, num quadrado [0, 8]^2: (x0, x1, y0, y1).
RETANGULOS_DW = [
    (0, 2, 4, 8), (2, 4, 6, 8), (4, 8, 6, 8),
    (2, 3, 5, 6), (3, 4, 5, 6), (2, 3, 4, 5), (3, 4, 4, 5),
    (4, 6, 4, 6), (6, 8, 5, 6), (6, 7, 4.5, 5), (6, 7, 4, 4.5), (7, 8, 4, 5),
    (0, 4, 2, 4), (4, 6, 0, 4), (6, 8, 2, 4), (6, 7, 0, 2), (7, 8, 0, 2), (0, 2, 0, 2),
    (2, 2.5, 1.5, 2), (2.5, 3, 1.5, 2), (2, 2.5, 1, 1.5), (2.5, 3, 1, 1.5),
    (3, 4, 1, 2), (2, 3, 0, 1), (3, 4, 0, 1),
]
# O retângulo com um vértice no meio de um lado: o bordo dele tem 5 arestas.
RETANGULO_DESTAQUE = (6, 8, 5, 6)


def vertices_dw() -> set[Ponto]:
    vertices = set()
    for x0, x1, y0, y1 in RETANGULOS_DW:
        vertices.update({(x0, y0), (x1, y0), (x0, y1), (x1, y1)})
    return vertices


def lados(retangulo: Retangulo) -> list[Segmento]:
    x0, x1, y0, y1 = retangulo
    return [((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)), ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))]


def arestas_do_retangulo(retangulo: Retangulo, vertices: set[Ponto]) -> list[Segmento]:
    """Cada lado é partido nos vértices que caem sobre ele (os nós pendurados)."""
    arestas = []
    for (ax, ay), (bx, by) in lados(retangulo):
        if ay == by:
            xs = sorted(x for x, y in vertices if y == ay and ax <= x <= bx)
            for u, v in zip(xs[:-1], xs[1:]):
                arestas.append(((u, ay), (v, ay)))
        else:
            ys = sorted(y for x, y in vertices if x == ax and ay <= y <= by)
            for u, v in zip(ys[:-1], ys[1:]):
                arestas.append(((ax, u), (ax, v)))
    return arestas


def arestas_dw() -> set[Segmento]:
    vertices = vertices_dw()
    arestas = set()
    for retangulo in RETANGULOS_DW:
        arestas.update(arestas_do_retangulo(retangulo, vertices))
    return arestas
