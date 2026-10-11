"""Dados do bloco 4 (matriz de bordo e redução de G). As cenas e verifica_bloco4.py leem daqui.

Mesmas coordenadas dos blocos 2 e 3. A ordem da filtração é por valor; no empate, a dimensão
menor primeiro (a face antes da célula); depois, a posição no CubeMap, linha a linha de cima
para baixo. É a mesma ordem do referencia.persistence, que deu o diagrama.
"""
from __future__ import annotations

import dados_bloco2 as d2
import dados_bloco3 as d3

Passo = tuple[list[int], set[int], int | None]  # as colunas somadas, a coluna final e o low


def ordem() -> list[d2.Cubo]:
    """As 81 células na ordem da filtração."""
    def chave(cubo: d2.Cubo) -> tuple[int, int, int, int]:
        a, b = d3.casa(cubo)
        return (d3.valor(cubo), d2.dimensao(cubo), 8 - b, a)

    return sorted(d3.celulas(), key=chave)


ORDEM = ordem()
INDICE = {cubo: k for k, cubo in enumerate(ORDEM)}


def coluna(cubo: d2.Cubo) -> set[int]:
    """A coluna da célula na matriz de bordo: os índices das suas faces (±1 nas coordenadas ímpares)."""
    linhas = set()
    for face in d2.faces_primarias(cubo):
        linhas.add(INDICE[face])
    return linhas


def matriz() -> list[set[int]]:
    """As 81 colunas da matriz de bordo ordenada, cada uma como um conjunto de linhas."""
    return [coluna(cubo) for cubo in ORDEM]


def reducao(twist: bool = False) -> tuple[dict[int, Passo], int]:
    """Redução padrão sobre Z2, da esquerda para a direita (com twist: quadrados antes, e a coluna
    do low de cada quadrado já sai zerada). Devolve, por coluna: as colunas somadas, a coluna final
    e o low; e o total de somas."""
    colunas = matriz()
    sequencia = list(range(len(ORDEM)))
    if twist:
        sequencia.sort(key=lambda k: (-d2.dimensao(ORDEM[k]), k))
    dono = {}
    limpas = set()
    passos = {}
    total = 0
    for k in sequencia:
        if k in limpas:
            colunas[k] = set()
            passos[k] = ([], set(), None)
            continue
        somadas = []
        while colunas[k] and max(colunas[k]) in dono:
            j = dono[max(colunas[k])]
            colunas[k] = colunas[k] ^ colunas[j]
            somadas.append(j)
            total += 1
        low = max(colunas[k]) if colunas[k] else None
        if low is not None:
            dono[low] = k
            if twist:
                limpas.add(low)
        passos[k] = (somadas, set(colunas[k]), low)
    return passos, total


def pares() -> list[tuple[int, int, float, int, int | None]]:
    """(dimensão, nascimento, morte, coluna que nasce, coluna que mata ou None)."""
    passos, _ = reducao()
    lows = {}
    for k, (_, _, low) in passos.items():
        if low is not None:
            lows[low] = k
    resultado = []
    for k in range(len(ORDEM)):
        if k in lows:
            j = lows[k]
            resultado.append((d2.dimensao(ORDEM[k]), d3.valor(ORDEM[k]), d3.valor(ORDEM[j]), k, j))
        elif passos[k][2] is None:
            resultado.append((d2.dimensao(ORDEM[k]), d3.valor(ORDEM[k]), float("inf"), k, None))
    return resultado


def aresta_que_fecha_o_anel() -> d2.Cubo:
    """A última aresta do anel na ordem: a de valor 100 cuja coluna zera."""
    anel = d3.anel()
    return max(anel, key=lambda c: INDICE[c])


def ultimo_quadrado_do_miolo() -> d2.Cubo:
    miolo = [c for c in d3.celulas() if d2.dimensao(c) == 2 and (2, 2) in d3.vertices_do_cubo(c)]
    return max(miolo, key=lambda c: INDICE[c])


def celulas_triangulacao() -> int:
    """Freudenthal: cada quadrado vira 2 triângulos e uma diagonal. 25 vértices, 40 + 16 arestas, 32 triângulos."""
    n = d2.N
    return n * n + (2 * n * (n - 1) + (n - 1) ** 2) + 2 * (n - 1) ** 2


# ------------------------------------------------------------------ para a explicação passo a passo
def ordem_guardada() -> list[d2.Cubo]:
    """A ordem em que as células estão guardadas no CubeMap, linha a linha de cima para baixo,
    antes de ordenar pela filtração."""
    def chave(cubo: d2.Cubo) -> tuple[int, int]:
        a, b = d3.casa(cubo)
        return (8 - b, a)

    return sorted(d3.celulas(), key=chave)


ORDEM_GUARDADA = ordem_guardada()
INDICE_GUARDADO = {cubo: k for k, cubo in enumerate(ORDEM_GUARDADA)}


def estados_da_coluna(k: int) -> list[set[int]]:
    """A coluna k antes de cada soma e depois da última, na redução padrão: [inicial, depois da 1ª, ...]."""
    passos, _ = reducao()
    coluna_atual = set(coluna(ORDEM[k]))
    estados = [set(coluna_atual)]
    for j in passos[k][0]:
        coluna_atual = coluna_atual ^ passos[j][1]
        estados.append(set(coluna_atual))
    return estados


def primeira_aresta_que_junta() -> int:
    """A primeira coluna de aresta da filtração: junta dois vértices 94."""
    for k, cubo in enumerate(ORDEM):
        if d2.dimensao(cubo) == 1:
            return k
