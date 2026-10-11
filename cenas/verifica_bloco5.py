"""Confere a matemática do bloco 5 (leitura do diagrama): o GUDHI contra a nossa redução, e cada
afirmação da tela e das notas sobre as opções do GUDHI.

Uso (em cenas/, com o env ativo): python verifica_bloco5.py
"""
from __future__ import annotations

import numpy as np

import dados_bloco4 as d4
import dados_bloco5 as d


def confere(condicao: bool, mensagem: str) -> None:
    assert condicao, mensagem
    print("ok:", mensagem)


padrao, celulas = d.persistencia()
confere(celulas == 81, "com vertices=, o GUDHI monta as mesmas 81 células (pixel = vértice)")
confere(repr(padrao) == d.SAIDA, f"a saída na tela é a do GUDHI: {d.SAIDA}")
confere(d.pares_que_duram() == [(0, 94.0, np.inf), (1, 100.0, 139.0)], "pares que duram: (94, ∞) em H0 e (100, 139) em H1")

todos, _ = d.persistencia(min_persistence=-1)
do_gudhi = sorted((dim, nasce, morre) for dim, (nasce, morre) in todos)
nossos = sorted((dim, float(b), float(m)) for dim, b, m, _, _ in d4.pares())
confere(do_gudhi == nossos, "com min_persistence=-1, os 41 pares do GUDHI são exatamente os da nossa redução")
confere(len(d.pares_de_duracao_zero()) == 39, "39 pares de duração zero, que o padrão do GUDHI omite")

em_z2, _ = d.persistencia(coeficientes=2)
confere(em_z2 == padrao, "coeficientes em Z2 e em Z11 (o padrão do GUDHI) dão o mesmo diagrama")

top, celulas_t = d.persistencia("top_dimensional_cells")
confere(celulas_t == 121, "com top_dimensional_cells= (pixel = quadrado), são 121 células")
confere(sorted((dim, b, m) for dim, (b, m) in top) == d.pares_que_duram(), "e os mesmos pares que duram, nesta imagem")

valores_zero = sorted({v for _, v in d.pares_de_duracao_zero()})
confere(valores_zero == [94.0, 99.0, 100.0, 114.0, 115.0, 117.0, 119.0, 139.0],
        "os pares de duração zero caem nos valores 94, 99, 100, 114, 115, 117, 119 e 139 da diagonal")
confere(139 - 100 == 39, "persistência do anel: 139 - 100 = 39")

zero_h0 = [v for dim, v in d.pares_de_duracao_zero() if dim == 0]
zero_h1 = [v for dim, v in d.pares_de_duracao_zero() if dim == 1]
confere(len(zero_h0) == 24 and len(zero_h1) == 15, "duração zero: 24 em H0 (vértice e aresta) e 15 em H1 (laço e quadrado)")
import dados_bloco2 as d2
import dados_bloco3 as d3
vertices_94 = [c for c in d3.celulas() if d2.dimensao(c) == 0 and d3.valor(c) == 94]
arestas_94 = [c for c in d3.celulas() if d2.dimensao(c) == 1 and d3.valor(c) == 94]
confere(len(vertices_94) == 5 and len(arestas_94) == 4 and zero_h0.count(94.0) == 4,
        "em 94: 5 vértices ligados por 4 arestas de 94; 4 componentes morrem na hora e uma segue, o (94, inf)")
