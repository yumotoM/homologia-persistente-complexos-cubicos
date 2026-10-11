"""Dados do bloco 6 (aplicação em satélite: Ver Hoef et al. 2023). As cenas e verifica_bloco6.py leem daqui.

Os números do artigo vêm do texto do primer (DOI 10.1175/AIES-D-22-0039.1): Fig. 10 (acurácias),
seções 2 e 4 (rótulos de Rasp et al. 2020, SVM, custo). Os números calculados vêm de prepara_nuvens.py.
"""
from __future__ import annotations

import json
from pathlib import Path

PASTA = Path(__file__).parent / "assets" / "nuvens"

# Fig. 10 do artigo: acurácia de teste da SVM linear em 3D (PCA), por par de padrões.
ACURACIAS = [
    ("sugar", "flowers", 89.25),
    ("fish", "sugar", 86.0),
    ("flowers", "gravel", 81.0),
    ("fish", "gravel", 79.5),
    ("sugar", "gravel", 71.25),
    ("fish", "flowers", 57.0),
]
SVM_TREINO, SVM_TESTE = 350, 200  # por classe (seção 4b)
CUSTO_AMOSTRAS, CUSTO_RECORTES, CUSTO_MINUTOS = 800, 4800, 45  # num notebook (seção 4e)
JANELA = 96
N_JANELAS = 6
N_FUNCOES = 5
N_AMOSTRAS = 200
KM_POR_GRAU = 111.0  # 1 grau de latitude
GRAUS_POR_PIXEL = 0.01  # as cenas do NASA Worldview têm 2100 x 1400 pixels para 21 x 14 graus

NOMES = {"sugar": "Sugar", "gravel": "Gravel", "flower": "Flowers", "fish": "Fish"}
DESCRICOES = {  # duas linhas por padrão, para caber embaixo de cada quadro
    "sugar": ("nuvens pequenas", "espalhadas por igual"),
    "gravel": ("um pouco maiores", "e mais organizadas"),
    "flower": ("aglomerados grandes", "com céu limpo entre eles"),
    "fish": ("faixas alongadas", "em espinha de peixe"),
}


def persistencia() -> dict:
    return json.loads((PASTA / "persistencia.json").read_text())


def escolhidas() -> dict:
    return json.loads((PASTA / "escolhidas.json").read_text())


def km(pixels: float) -> float:
    return pixels * GRAUS_POR_PIXEL * KM_POR_GRAU
