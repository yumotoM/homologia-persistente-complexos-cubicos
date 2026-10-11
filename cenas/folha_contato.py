"""Folha de contato dos slides renderizados, para revisar as transições.

Cada linha é um slide, e as colunas são o início, o meio e o fim do vídeo dele.
O início de um slide deve repetir o fim do anterior; se não repetir, há salto.

Uso: python folha_contato.py <Cena> [<Cena> ...]   (depois de manim-slides render)
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

FRACOES = (0.0, 0.5, 1.0)
LARGURA = 480
# Diferença média (0 a 255) aceitável entre o fim de um slide e o início do
# seguinte; acima disso a transição tem um salto visível.
LIMITE_SALTO = 3.0


def duracao(arquivo: str) -> float:
    saida = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", arquivo,
    ])
    return float(saida)


def quadro(arquivo: str, t: float) -> Image.Image:
    png = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", arquivo,
         "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
        capture_output=True, check=True,
    ).stdout
    imagem = Image.open(io.BytesIO(png)).convert("RGB")
    altura = round(imagem.height * LARGURA / imagem.width)
    return imagem.resize((LARGURA, altura))


def folha(cena: str) -> None:
    slides = json.loads(Path(f"slides/{cena}.json").read_text())["slides"]
    linhas = []
    for slide in slides:
        dur = duracao(slide["file"])
        imagens = []
        for f in FRACOES:
            imagens.append(quadro(slide["file"], min(dur * f, dur - 0.04)))
        linhas.append(imagens)
    alt = linhas[0][0].height
    tela = Image.new("RGB", (LARGURA * len(FRACOES), (alt + 22) * len(linhas)), "white")
    desenho = ImageDraw.Draw(tela)
    for k, imagens in enumerate(linhas):
        y = k * (alt + 22)
        desenho.text((4, y + 4), f"slide {k}   (início | meio | fim)", fill="black")
        for c, imagem in enumerate(imagens):
            tela.paste(imagem, (c * LARGURA, y + 22))
    saltos = []
    for k in range(len(linhas) - 1):
        fim = np.asarray(linhas[k][-1], dtype=float)
        inicio = np.asarray(linhas[k + 1][0], dtype=float)
        diferenca = np.abs(fim - inicio).mean()
        if diferenca > LIMITE_SALTO:
            saltos.append(f"{k}->{k + 1}: {diferenca:.1f}")
    print(cena, "transições:", "sem saltos" if not saltos else "SALTO em " + ", ".join(saltos))

    # Os slides devem cobrir todos os vídeos parciais. Se um wait() não for
    # contado pelo manim-slides, as fronteiras andam e o fim da cena se perde.
    total_slides = sum(duracao(slide["file"]) for slide in slides)
    total_parciais = sum(duracao(str(p)) for p in sorted(Path(f"videos/{cena}").glob("*.mp4")))
    perdido = total_parciais - total_slides
    situacao = "completa" if abs(perdido) < 0.2 else f"FALTAM {perdido:.1f} s"
    print(cena, f"cobertura: {total_slides:.1f} s de {total_parciais:.1f} s, {situacao}")
    Path("revisao").mkdir(exist_ok=True)
    destino = Path("revisao") / f"{cena}.png"
    tela.save(destino)
    print(destino, f"{len(linhas)} slides")


if __name__ == "__main__":
    for nome in sys.argv[1:]:
        folha(nome)
