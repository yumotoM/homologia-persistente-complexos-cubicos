"""Confere o que as telas do bloco 1 afirmam sobre as imagens.

Uso (em cenas/, com o env ativo): python verifica_bloco1.py
"""
from __future__ import annotations

import numpy as np
from PIL import Image

import prepara_imagens as prep
from bloco1 import LADO_IMAGEM


def confere(condicao: bool, mensagem: str) -> None:
    assert condicao, mensagem
    print("ok:", mensagem)


rgb = np.load(prep.PASTA / "cachorro_rgb.npy")
cinza = np.load(prep.PASTA / "cachorro_cinza.npy")
prob = np.load(prep.PASTA / "cachorro_prob.npy")

confere(rgb.shape == (LADO_IMAGEM, LADO_IMAGEM, 3), f"I tem H x W x 3 = {LADO_IMAGEM} x {LADO_IMAGEM} x 3, como o slide diz")
confere(prep.PESOS_CINZA == (0.299, 0.587, 0.114), "os pesos do script são os da fórmula do slide")
confere(np.allclose(cinza, 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]),
        "o cinza é phi aplicada pixel a pixel")
png_cinza = np.asarray(Image.open(prep.PASTA / "cachorro_cinza.png")).astype(float) / 255
confere(np.abs(png_cinza - cinza).max() <= 0.5 / 255 + 1e-9, "o PNG exibido é o cinza calculado, a menos do arredondamento")
png_rgb = np.asarray(Image.open(prep.PASTA / "cachorro_rgb.png")).astype(float) / 255
confere(np.allclose(png_rgb, rgb), "o PNG RGB exibido é o array I")
for k, nome in enumerate("rgb"):
    canal = np.asarray(Image.open(prep.PASTA / f"cachorro_canal_{nome}.png")).astype(float) / 255
    outros = [c for c in range(3) if c != k]
    confere(np.allclose(canal[..., k], rgb[..., k]) and canal[..., outros].max() == 0,
            f"o canal {nome.upper()} exibido é a componente {nome.upper()} de I, sozinha")
confere(prob.shape == cinza.shape and prob.min() >= 0 and prob.max() <= 1,
        "o mapa de probabilidade tem um número em [0, 1] por pixel")
