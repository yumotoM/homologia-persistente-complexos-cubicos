"""Implementação de referência da persistência cúbica, independente das cenas.

As verificações usam estas funções para conferir, por um caminho separado, os números
que as cenas desenham. Construção V (Wagner et al., 2011): o pixel é o vértice, e cada
célula recebe o máximo dos seus vértices. A redução é a padrão, sobre Z2, da matriz de
bordo ordenada.
"""
from __future__ import annotations

import numpy as np

Celula = tuple[int, int]
Par = tuple[int, float, float, Celula, "Celula | None"]


def cubemap_V(img: np.ndarray) -> np.ndarray:
    """O CubeMap da construção V: o array (2h - 1) x (2w - 1) com o valor de cada célula."""
    h, w = img.shape
    val = np.full((2 * h - 1, 2 * w - 1), -np.inf)
    for i in range(2 * h - 1):
        for j in range(2 * w - 1):
            rows = [i // 2] if i % 2 == 0 else [i // 2, i // 2 + 1]
            cols = [j // 2] if j % 2 == 0 else [j // 2, j // 2 + 1]
            for r in rows:
                for c in cols:
                    val[i, j] = max(val[i, j], img[r, c])
    return val


def boundary(i: int, j: int) -> list[Celula]:
    """As faces da célula (i, j) no CubeMap."""
    # Coordenada ímpar = intervalo não degenerado; o bordo tira 1 de cada uma.
    faces = []
    if i % 2 == 1:
        faces += [(i - 1, j), (i + 1, j)]
    if j % 2 == 1:
        faces += [(i, j - 1), (i, j + 1)]
    return faces


def persistence(val: np.ndarray) -> tuple[list[Par], int]:
    """Pares (dim, nascimento, morte, célula que nasce, célula que mata) e o número de células."""
    H, W = val.shape
    cells = []
    for i in range(H):
        for j in range(W):
            cells.append((val[i, j], (i % 2) + (j % 2), i, j))
    cells.sort()  # valor, depois dimensão: faces entram antes das cofaces
    order = {(c[2], c[3]): k for k, c in enumerate(cells)}

    low_owner = {}
    paired = set()
    out = []
    for k, (_, _, i, j) in enumerate(cells):
        col = {order[f] for f in boundary(i, j)}
        while col and max(col) in low_owner:
            _, owner_col = low_owner[max(col)]
            col ^= owner_col
        if col:
            low = max(col)
            low_owner[low] = (k, col)
            paired.update([low, k])
            b, d = cells[low], cells[k]
            out.append((b[1], b[0], d[0], (b[2], b[3]), (d[2], d[3])))
    for k, c in enumerate(cells):
        if k not in paired:
            out.append((c[1], c[0], np.inf, (c[2], c[3]), None))
    return out, len(cells)
