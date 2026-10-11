"""Dados do bloco 5 (leitura do diagrama). O diagrama vem do GUDHI; verifica_bloco5.py confere
que ele é o mesmo da nossa redução (dados_bloco4) e o que cada opção do GUDHI faz.
"""
from __future__ import annotations

import gudhi

import dados_bloco2 as d2


def persistencia(construcao: str = "vertices", min_persistence: float = 0, coeficientes: int = 11) -> tuple[list[tuple[int, tuple[float, float]]], int]:
    """Os pares do GUDHI para a imagem do exemplo: [(dimensão, (nascimento, morte)), ...] e o número de células.

    construcao="vertices": pixel = vértice, célula com o máximo dos vértices (Wagner et al.).
    construcao="top_dimensional_cells": pixel = quadrado (a construção T).
    """
    complexo = gudhi.CubicalComplex(**{construcao: d2.G.astype(float)})
    pares = complexo.persistence(homology_coeff_field=coeficientes, min_persistence=min_persistence)
    return pares, complexo.num_simplices()


def pares_que_duram() -> list[tuple[int, float, float]]:
    """(dimensão, nascimento, morte) dos pares com duração maior que zero, como o GUDHI devolve por padrão."""
    pares, _ = persistencia()
    resultado = []
    for dim, (nasce, morre) in pares:
        resultado.append((dim, nasce, morre))
    return sorted(resultado)


def pares_de_duracao_zero() -> list[tuple[int, float]]:
    """(dimensão, valor) dos pares que nascem e morrem no mesmo valor (min_persistence=-1)."""
    pares, _ = persistencia(min_persistence=-1)
    resultado = []
    for dim, (nasce, morre) in pares:
        if nasce == morre:
            resultado.append((dim, nasce))
    return sorted(resultado)


# O código mostrado na tela e a saída que ele imprime (conferida em verifica_bloco5.py).
CODIGO = [
    "import gudhi",
    "complexo = gudhi.CubicalComplex(vertices=imagem)",
    "complexo.persistence()",
]
SAIDA = "[(1, (100.0, 139.0)), (0, (94.0, inf))]"
