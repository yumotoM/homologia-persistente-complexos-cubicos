"""Confere a matemática do bloco 4 (matriz de bordo e redução de G): cada número e afirmação da tela e das notas.

Uso (em cenas/, com o env ativo): python verifica_bloco4.py
"""
from __future__ import annotations


import numpy as np

import dados_bloco2 as d2
import dados_bloco3 as d3
import dados_bloco4 as d
from referencia import cubemap_V, persistence


def confere(condicao: bool, mensagem: str) -> None:
    assert condicao, mensagem
    print("ok:", mensagem)


confere(len(d.ORDEM) == 81, "81 células: a matriz é 81 x 81")
valores = [d3.valor(c) for c in d.ORDEM]
confere(valores == sorted(valores), "a ordem é por valor crescente")
faces_antes = all(d.INDICE[f] < d.INDICE[c] for c in d.ORDEM for f in d2.faces_primarias(c))
confere(faces_antes, "toda face vem antes da célula: a matriz é triangular superior")
nao_nulos = sum(len(col) for col in d.matriz())
confere(nao_nulos == 144 and 40 * 2 + 16 * 4 == 144, "144 entradas não nulas (2 por aresta, 4 por quadrado) de 6561")

quadrado = d2.QUADRADO
faces = sorted(d3.casa(f) for f in d2.faces_primarias(quadrado))
a, b = d3.casa(quadrado)
confere(faces == sorted([(a - 1, b), (a + 1, b), (a, b - 1), (a, b + 1)]),
        "as faces do quadrado [1,2] x [2,3] são ±1 nas suas coordenadas ímpares")

passos, total = d.reducao()
_, total_twist = d.reducao(twist=True)
confere(total == 89, "a redução padrão faz 89 somas de colunas")
confere(total_twist == 4, "com o twist, 4 somas")

fecha = d.aresta_que_fecha_o_anel()
k = d.INDICE[fecha]
somadas, final, low = passos[k]
anel = set(d3.anel())
confere(d3.valor(fecha) == 100, "a aresta que fecha o anel vale 100")
confere({d.ORDEM[j] for j in somadas} == anel - {fecha} and len(somadas) == 7,
        "a coluna dela soma as colunas das outras 7 arestas do anel")
confere(not final, "e zera: ela fecha um laço, nasce H1 em 100")

ultimo = d.ultimo_quadrado_do_miolo()
k2 = d.INDICE[ultimo]
somadas2, final2, low2 = passos[k2]
miolo = {c for c in d3.celulas() if d2.dimensao(c) == 2 and (2, 2) in d3.vertices_do_cubo(c)}
confere(k2 == 80, "o último quadrado do miolo é a última coluna da matriz")
confere({d.ORDEM[j] for j in somadas2} == miolo - {ultimo}, "a coluna dele soma as colunas dos outros 3 quadrados do miolo")
confere({d.ORDEM[r] for r in final2} == anel, "o que sobra é o anel de 8 arestas")
confere(d.ORDEM[low2] == fecha, "o low aponta para a aresta de 100: o par é (100, 139)")

somas_por_dim = {1: 0, 2: 0}
for col, (somadas_k, _, _) in passos.items():
    if somadas_k:
        somas_por_dim[d2.dimensao(d.ORDEM[col])] += len(somadas_k)
confere(somas_por_dim == {1: 86, 2: 3}, "86 somas em colunas de arestas e 3 em colunas de quadrados")
zeradas = [c for c, (_, f, _) in passos.items() if not f and d2.dimensao(d.ORDEM[c]) == 1]
confere(len(zeradas) == 16, "16 colunas de arestas zeram: 16 laços nascem")
confere(sum(len(passos[c][0]) for c in zeradas) == 85, "85 das 89 somas caem nessas 16 colunas, que acabam zeradas")
passos_twist, _ = d.reducao(twist=True)
limpas = sorted(c for c, (s, f, low) in passos_twist.items() if not f and d2.dimensao(d.ORDEM[c]) == 1)
confere(limpas == sorted(zeradas), "o twist zera essas mesmas 16 colunas sem somar nada")
confere(d.INDICE[d2.QUADRADO] == 77 and sorted(d.coluna(d2.QUADRADO)) == [5, 7, 73, 74],
        "o quadrado [1,2] x [2,3] é a coluna 77, com 1 nas linhas 5, 7, 73 e 74")

todos = d.pares()
duram = sorted((dim, b, m) for dim, b, m, _, _ in todos if m > b)
zero = [p for p in todos if p[2] == p[1]]
confere(duram == [(0, 94, np.inf), (1, 100, 139)], "pares que duram: (94, ∞) em H0 e (100, 139) em H1")
confere(len(zero) == 39 and len(todos) == 41, "39 pares de duração zero; 40 pares e uma coluna sem par")
referencia, _ = persistence(cubemap_V(d2.G))
confere(sorted((p[0], p[1], p[2]) for p in todos) == sorted((p[0], p[1], p[2]) for p in referencia),
        "os pares são os mesmos da implementação de referência")
essencial = [p for p in todos if p[2] == np.inf][0]
confere(d3.valor(d.ORDEM[essencial[3]]) == 94 and d2.dimensao(d.ORDEM[essencial[3]]) == 0,
        "a coluna sem par é a de um vértice 94")

confere(d.celulas_triangulacao() == 113, "triangulando G: 113 células (25 + 56 + 32)")
confere(81 * 81 == 6561 and 113 * 113 == 12769, "matriz 81 x 81 = 6561 entradas contra 113 x 113 = 12769")

# ------------------------------------------------------------------ a leitura passo a passo
guardada = d.ORDEM_GUARDADA
abaixo = sum(1 for c in guardada for f in d2.faces_primarias(c) if d.INDICE_GUARDADO[f] > d.INDICE_GUARDADO[c])
confere(abaixo > 0, f"na ordem guardada (linha a linha), {abaixo} pontos ficam abaixo da diagonal; ordenar põe todos acima")

k_aresta = d.primeira_aresta_que_junta()
col = sorted(d.coluna(d.ORDEM[k_aresta]))
confere(all(d3.valor(d.ORDEM[r]) == 94 for r in col) and passos[k_aresta][2] == col[-1],
        "a primeira aresta junta dois vértices 94; o low é o mais novo dos dois, que morre em 94")

estados = d.estados_da_coluna(k)
confere(all(len(e) == 2 for e in estados[:-1]) and estados[-1] == set(),
        "na aresta de 100, a coluna sempre tem as 2 pontas de um caminho, até zerar")
caminho_ok = True
caminho = [fecha]
for j, antes, depois in zip(somadas, estados[:-1], estados[1:]):
    aresta = d.ORDEM[j]
    pontas = {d.INDICE[v] for v in d2.faces_primarias(aresta)}
    if max(antes) not in pontas or passos[j][0]:
        caminho_ok = False
    caminho.append(aresta)
confere(caminho_ok, "cada soma acrescenta ao caminho uma aresta original que toca a ponta mais nova (o low)")

estados_q = d.estados_da_coluna(k2)
confere([len(e) for e in estados_q] == [4, 6, 8, 8], "no último quadrado, o contorno do conjunto tem 4, 6, 8 e 8 arestas")
confere(all(not passos[j][0] for j in somadas2), "os quadrados somados são colunas originais: cada soma junta mais um quadrado")
