"""Gera as imagens da tela "O formato do dado em complexos cúbicos".

Foto: "White Swiss Shepherd portrait", de Joselodos, CC0, Wikimedia Commons
https://commons.wikimedia.org/wiki/File:White_Swiss_Shepherd_portrait.jpg

Saídas em assets/: cachorro_rgb.png, os três canais (cachorro_canal_r/g/b.png),
cachorro_cinza.png, cachorro_prob.png e os arrays .npy que verifica_bloco1.py confere.

O mapa de probabilidade é ILUSTRATIVO: não vem de um modelo. É a silhueta do
cachorro (separada da grama pela cor) suavizada, imitando a saída de uma rede
de segmentação.

Uso: python prepara_imagens.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

PASTA = Path(__file__).parent / "assets"
ORIGINAL = PASTA / "original_white_swiss_shepherd_1600.jpg"

LADO = 512
RECORTE = (330, 0, 1610, 1280)  # x0, y0, x1, y1 no original de 1920 x 1280
PESOS_CINZA = (0.299, 0.587, 0.114)  # ITU-R BT.601, a mesma fórmula do slide

# Escala da probabilidade, igual a CORES_PROB do bloco1 (preto -> azuis do ManimGL).
ESCALA_PROB = ["#000000", "#1C758A", "#58C4DD", "#C7E9F1"]


def silhueta(rgb: np.ndarray) -> np.ndarray:
    """Cachorro = tudo que não é grama; grama tem o verde dominante."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    grama = (g > r * 1.08) & (g > b * 1.15)
    cao = ndimage.binary_opening(~grama, iterations=3)
    rotulos, n = ndimage.label(cao)
    tamanhos = ndimage.sum(cao, rotulos, range(1, n + 1))
    maior = 1 + int(np.argmax(tamanhos))
    return ndimage.binary_fill_holes(rotulos == maior)


def probabilidade_ilustrativa(mascara: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng(11)
    suave = ndimage.gaussian_filter(mascara.astype(float), sigma=10)
    ruido = ndimage.gaussian_filter(rng.normal(0, 1, mascara.shape), sigma=24)
    ruido = 0.06 * ruido / np.abs(ruido).max()
    return np.clip(0.03 + 0.94 * suave + ruido, 0, 1)


def colorir(valores: np.ndarray, escala: list[str]) -> np.ndarray:
    cores = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in escala], dtype=float)
    pos = np.clip(valores, 0, 1) * (len(escala) - 1)
    i = np.minimum(pos.astype(int), len(escala) - 2)
    frac = (pos - i)[..., None]
    return (cores[i] * (1 - frac) + cores[i + 1] * frac).astype(np.uint8)


def main() -> None:
    foto = Image.open(ORIGINAL).convert("RGB").crop(RECORTE).resize((LADO, LADO), Image.LANCZOS)
    rgb = np.asarray(foto).astype(float) / 255
    cinza = rgb @ np.array(PESOS_CINZA)
    prob = probabilidade_ilustrativa(silhueta(rgb))

    foto.save(PASTA / "cachorro_rgb.png")
    for k, nome in enumerate("rgb"):
        canal = np.zeros_like(rgb)
        canal[..., k] = rgb[..., k]  # cada canal na sua cor, para mostrar o "x 3"
        Image.fromarray(np.round(canal * 255).astype(np.uint8)).save(PASTA / f"cachorro_canal_{nome}.png")
    Image.fromarray(np.round(cinza * 255).astype(np.uint8)).save(PASTA / "cachorro_cinza.png")
    Image.fromarray(colorir(prob, ESCALA_PROB)).save(PASTA / "cachorro_prob.png")
    np.save(PASTA / "cachorro_rgb.npy", rgb)
    np.save(PASTA / "cachorro_cinza.npy", cinza)
    np.save(PASTA / "cachorro_prob.npy", prob)
    print(f"{LADO} x {LADO} x 3 -> cinza e prob em [{prob.min():.2f}, {prob.max():.2f}]")


if __name__ == "__main__":
    main()
