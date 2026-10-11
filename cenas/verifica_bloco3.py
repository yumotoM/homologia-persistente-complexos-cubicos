"""Confere a matemática do bloco 3 (a filtração de G): cada número e afirmação da tela e das notas.

Uso (em cenas/, com o env ativo): python verifica_bloco3.py
"""
from __future__ import annotations


import numpy as np

import dados_bloco2 as d2
import dados_bloco3 as d
from referencia import cubemap_V, persistence


def confere(condicao: bool, mensagem: str) -> None:
    assert condicao, mensagem
    print("ok:", mensagem)


celulas = d.celulas()
confere(len(celulas) == 81, "81 células: 25 vértices com valor de pixel, faltam 40 arestas e 16 quadrados")

# A extensão pelo máximo é a mesma da implementação de referência (que deu o diagrama), casa a casa.
cubemap = cubemap_V(d.G)
iguais = True
for cubo in celulas:
    a, b = d.casa(cubo)
    if cubemap[8 - b, a] != d.valor(cubo):
        iguais = False
confere(iguais, "o valor de cada célula (máximo dos vértices) bate com o CubeMap da implementação de referência")

# ------------------------------------------------------------------ 4.1
quadrado, e1, e2, e3, e4, *vertices = d.faces_do_bloco()
valores_vertices = {v: d.valor(v) for v in vertices}
confere(sorted(valores_vertices.values()) == [94, 94, 94, 139], "o bloco [1,2] x [2,3] tem três vértices 94 e o 139")
confere(valores_vertices[((2, 2), (2, 2))] == 139, "o 139 é o canto (2, 2), o centro de G")
confere([d.valor(e) for e in (e1, e2, e3, e4)] == [94, 139, 139, 94], "pelo máximo, e1 = 94, e2 = 139, e3 = 139, e4 = 94")
confere(d.valor(quadrado) == 139, "pelo máximo, o quadrado recebe 139")
confere(all(d.valor_minimo(c) == 94 for c in [quadrado, e1, e2, e3, e4]), "pelo mínimo, o quadrado e as quatro arestas recebem 94")

t = d.T_CONTRAEXEMPLO
com_maximo = [c for c in d.faces_do_bloco() if d.valor(c) <= t]
confere(sorted(com_maximo) == sorted([e1, e4] + [v for v in vertices if valores_vertices[v] == 94]),
        "em t = 94, com o máximo, sobram os três vértices 94 e as arestas e1 e e4")
for cubo in com_maximo:
    for face in d2.faces_primarias(cubo):
        assert face in com_maximo
confere(True, "com o máximo, o que sobra em t = 94 é fechado por faces (um complexo)")
com_minimo = [c for c in d.faces_do_bloco() if d.valor_minimo(c) <= t]
faltando = set()
for cubo in com_minimo:
    for face in d2.faces_primarias(cubo):
        if face not in com_minimo:
            faltando.add(face)
confere(faltando == {((2, 2), (2, 2))}, "com o mínimo, em t = 94 falta só o vértice 139, face de e2, e3 e do quadrado")

monotona = True
for cubo in celulas:
    for face in d2.faces_primarias(cubo):
        if d.valor(face) > d.valor(cubo):
            monotona = False
confere(monotona, "com o máximo, f(face) <= f(célula) em todo o complexo: cada subnível é subcomplexo")

# ------------------------------------------------------------------ 4.2
paridade = True
for cubo in celulas:
    a, b = d.casa(cubo)
    if a % 2 + b % 2 != d2.dimensao(cubo):
        paridade = False
confere(paridade, "paridade = dimensão: par-par vértice, par-ímpar aresta, ímpar-ímpar quadrado")

centro = ((2, 2), (2, 2))
cofaces = [c for c in celulas if c != centro and (2, 2) in d.vertices_do_cubo(c)]
casas_vizinhas = sorted((4 + da, 4 + db) for da in (-1, 0, 1) for db in (-1, 0, 1) if (da, db) != (0, 0))
confere(sorted(d.casa(c) for c in cofaces) == casas_vizinhas, "as 8 casas vizinhas do centro são as suas cofaces (3^2 - 1 = 8)")

confere(d.ordem_dos_valores() == [139, 119, 117, 115, 114, 100, 99, 94], "ordem: 139, 119, 117, 115, 114, 100, 99, 94")
dono = d.reivindicacao()
confere(len(dono) == 81, "o Algoritmo 1 dá valor às 81 casas")
certo = True
for cubo in celulas:
    vertice, _ = dono[d.casa(cubo)]
    if d.valor_do_vertice(vertice[0] // 2, vertice[1] // 2) != d.valor(cubo):
        certo = False
confere(certo, "quem toma primeiro cada casa é o maior vértice dela: o Algoritmo 1 dá o máximo")
estrela_casas = sorted(c for c, (v, _) in dono.items() if v == (4, 4))
confere(estrela_casas == sorted([(4, 4)] + casas_vizinhas), "o 139 toma 9 casas: ele e as suas 8 vizinhas")
confere(sorted(d.casa(c) for c in d.estrela_do_centro()) == estrela_casas, "as 9 casas do 139 são a sua estrela inferior")
dims = sorted(d2.dimensao(c) for c in d.estrela_do_centro())
confere(dims == [0, 1, 1, 1, 1, 2, 2, 2, 2], "estrela do 139: 1 vértice, 4 arestas e 4 quadrados")

indice = d.indices_da_filtracao()
valida = True
for cubo in celulas:
    for face in d2.faces_primarias(cubo):
        if indice[d.casa(face)] >= indice[d.casa(cubo)]:
            valida = False
crescente = True
por_indice = sorted(celulas, key=lambda c: indice[d.casa(c)])
for a, b in zip(por_indice[:-1], por_indice[1:]):
    if d.valor(a) > d.valor(b):
        crescente = False
confere(valida and crescente, "os índices do Algoritmo 1 já são uma filtração: faces antes, valores crescentes")

# ------------------------------------------------------------------ 4.3
esperado = {94: (1, 0), 99: (1, 0), 100: (1, 1), 114: (1, 1), 115: (1, 1), 117: (1, 1), 119: (1, 1), 139: (1, 0)}
for valor_t, betas in esperado.items():
    confere(d.betti(d.subnivel(valor_t)) == betas, f"em t = {valor_t}: (β0, β1) = {betas}")
confere(d.betti(d.subnivel(93)) == (0, 0), "antes de 94 o subnível é vazio")

paradas = [v for valores, _ in d.PARADAS for v in valores]
confere(paradas == sorted({d.valor(c) for c in celulas}), "as paradas do processo de filtração cobrem todos os valores das células")

entram = {}
for cubo in celulas:
    chave = d.valor(cubo)
    entram.setdefault(chave, [0, 0, 0])[d2.dimensao(cubo)] += 1
confere(entram[94] == [5, 4, 0], "t = 94: entram 5 vértices e 4 arestas")
borda = [0, 0, 0]
for v in (114, 115, 117, 119):
    for k in range(3):
        borda[k] += entram[v][k]
confere(borda == [16, 28, 12], "de 114 a 119: 16 vértices, 28 arestas e 12 quadrados")
confere(entram[139] == [1, 4, 4], "t = 139: o centro, 4 arestas e 4 quadrados")

anel = d.anel()
no_anel = sorted({v for a in anel for v in d.vertices_do_cubo(a)})
confere(len(anel) == 8 and len(no_anel) == 8, "em t = 100 o subnível é o anel: 8 vértices e 8 arestas")
confere(len(d.subnivel(100)) == 16, "em t = 100 não há quadrados: o subnível é só o anel")
grade_1d = [c for c in celulas if d2.dimensao(c) < 2]
confere(d.betti(grade_1d) == (1, 16), "só vértices e arestas: uma componente e 16 buracos (χ = 25 - 40 = 1 - 16)")
confere([sum(1 for c in d.subnivel(119) if d2.dimensao(c) == k) for k in range(3)] == [24, 36, 12],
        "em t = 119, a moldura: 24 vértices, 36 arestas e 12 quadrados (χ = 0)")
confere(all(max(abs(x - 2), abs(y - 2)) == 1 for x, y in no_anel), "o anel cerca o centro (2, 2)")
quadrados = [c for c in celulas if d2.dimensao(c) == 2]
confere(min(d.valor(q) for q in quadrados) == 114, "nenhum quadrado vale menos de 114: em t = 100 não há quadrado, só o laço")
internos = [q for q in quadrados if (2, 2) in d.vertices_do_cubo(q)]
confere(len(internos) == 4 and all(d.valor(q) == 139 for q in internos), "os 4 quadrados em volta do centro valem 139")
tamanho = {}
for casa_, (vertice, _) in dono.items():
    tamanho[vertice] = tamanho.get(vertice, 0) + 1
noventa_e_quatro = [tamanho[(2 * x, 2 * y)] for x in range(5) for y in range(5) if d.valor_do_vertice(x, y) == 94]
confere(sorted(noventa_e_quatro) == [1, 2, 2, 2, 2], "as estrelas inferiores dos 94 têm 1 ou 2 casas")

pares, _ = persistence(cubemap)
duradouros = sorted((dim, b, m) for dim, b, m, _, _ in pares if m > b)
zero = [p for p in pares if p[2] == p[1]]
confere(duradouros == [(0, d.NASCIMENTO_H0, np.inf), (1, d.NASCIMENTO_H1, d.MORTE_H1)],
        "barcode: H0 = (94, ∞) e H1 = (100, 139)")
confere(len(zero) == 39, "além deles, 39 pares de duração zero, que não aparecem no barcode")
zero_94 = [p for p in zero if p[0] == 0 and p[1] == 94]
confere(len(zero_94) == 4, "em t = 94, quatro pares (94, 94) de H0: cada aresta junta dois 94")

otter = {100: (1, 1), 115: (1, 1), 130: (1, 1), 140: (1, 0)}
for valor_t, betas in otter.items():
    confere(d.betti(d.subnivel(valor_t)) == betas, f"quadro do Otter t = {valor_t}: (β0, β1) = {betas}")
confere(sorted(d.subnivel(130)) == sorted(d.subnivel(119)), "o quadro t = 130 do Otter é o subnível de 119: tudo menos o centro")
