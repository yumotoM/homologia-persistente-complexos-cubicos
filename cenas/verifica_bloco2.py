"""Confere a matemática do bloco 2 (construção do complexo cúbico).

Uso (em cenas/, com o env ativo): python verifica_bloco2.py
"""
from __future__ import annotations


import numpy as np

import dados_bloco2 as d
from referencia import cubemap_V, persistence


def confere(condicao: bool, mensagem: str) -> None:
    assert condicao, mensagem
    print("ok:", mensagem)


# O exemplo de Otter et al. tem o diagrama do barcode (d) deles.
pares, n_celulas = persistence(cubemap_V(d.G))
finitos = sorted((dim, b, m) for dim, b, m, _, _ in pares if m > b)
confere(finitos == [(0, 94, np.inf), (1, 100, 139)], "G dá H0 = (94, ∞) e H1 = (100, 139), como o barcode de Otter et al.")
confere(n_celulas == 81, "G tem 81 células, um CubeMap 9 x 9 como o da Fig. 3 de Wagner et al.")

complexo = d.complexo_da_grade(d.N)
contagem = {k: len(v) for k, v in complexo.items()}
confere(contagem == {0: 25, 1: 40, 2: 16}, "o complexo de G tem 25 vértices, 40 arestas e 16 quadrados")
confere(25 - 40 + 16 == 1, "χ = 25 - 40 + 16 = 1, o de um quadrado (contrátil)")

dims = [d.dimensao(c) for c in d.EXEMPLOS_PRODUTO]
confere(dims == [0, 1, 1, 2], "os quatro produtos do passo 7.3 têm dimensões 0, 1, 1 e 2")
for cubo in d.EXEMPLOS_PRODUTO:
    confere(cubo in complexo[d.dimensao(cubo)], f"{cubo} é uma célula do complexo de G")
confere(d.dimensao(d.VOXEL) == 3, "o voxel [1,2] x [2,3] x [0,1] tem dimensão 3")

faces = d.faces_primarias(d.QUADRADO)
esperado = [((1, 1), (2, 3)), ((2, 2), (2, 3)), ((1, 2), (2, 2)), ((1, 2), (3, 3))]
confere(faces == esperado, "bdr([1,2] x [2,3]) = [1]x[2,3], [2]x[2,3], [1,2]x[2], [1,2]x[3]")
confere(d.faces_primarias(((1, 2), (2, 2))) == [((1, 1), (2, 2)), ((2, 2), (2, 2))],
        "bdr([1,2] x [2]) = os vértices (1, 2) e (2, 2)")
contagem_bb = d.bordo_do_bordo(d.QUADRADO)
confere(len(contagem_bb) == 4 and set(contagem_bb.values()) == {2}, "em ∂∂Q cada um dos 4 vértices aparece 2 vezes: ∂∂Q = 0 em Z2")

bordos = d.bordo_das_arestas()
confere(bordos == {"e_1": ("v_1", "v_3"), "e_2": ("v_2", "v_4"), "e_3": ("v_1", "v_2"), "e_4": ("v_3", "v_4")},
        "∂e1 = v1 + v3, ∂e2 = v2 + v4, ∂e3 = v1 + v2, ∂e4 = v3 + v4, como o slide escreve")
vezes = {}
for par in bordos.values():
    for nome in par:
        vezes[nome] = vezes.get(nome, 0) + 1
confere(vezes == {"v_1": 2, "v_2": 2, "v_3": 2, "v_4": 2}, "∂∂Q = 2(v1 + v2 + v3 + v4) = 0 em Z2")

vertices = d.vertices_dw()
arestas = d.arestas_dw()
confere(len(vertices) == 46, "a reconstrução da Fig. 2 de Dlotko e Wanner tem 46 vértices, como a legenda")
confere(len(arestas) == 70, "e 70 arestas, como a legenda")
confere(len(d.RETANGULOS_DW) == 25 and len(vertices) - len(arestas) + 25 == 1, "e 25 retângulos, com χ = 1")
area = sum((x1 - x0) * (y1 - y0) for x0, x1, y0, y1 in d.RETANGULOS_DW)
confere(area == 64, "os 25 retângulos cobrem o quadrado [0, 8]^2 sem sobra")
bordo_destaque = d.arestas_do_retangulo(d.RETANGULO_DESTAQUE, vertices)
confere(len(bordo_destaque) == 5 and ((6, 5), (7, 5)) in bordo_destaque,
        "o retângulo [6,8] x [5,6] tem 5 arestas no bordo: o lado de baixo é partido no vértice (7, 5)")
