"""Exporta as cenas para um HTML e confere que cada vídeo é o do render atual.

O manim-slides nomeia o vídeo de cada slide pelo hash dos NOMES dos vídeos parciais
(00000, 00001, ...), que se repetem entre renders, e o convert não sobrescreve um
asset que já existe. Sem apagar a pasta de assets, o HTML serve vídeos de versões
anteriores. Por isso: apaga, converte e compara byte a byte.

Uso: python exporta_html.py apresentacao.html Abertura FluxoEFormato ConstrucaoDoComplexo
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def md5(caminho: str | Path) -> str:
    return hashlib.md5(Path(caminho).read_bytes()).hexdigest()


def main() -> None:
    saida = Path(sys.argv[1])
    cenas = sys.argv[2:]
    assets = saida.with_name(f"{saida.stem}_assets")
    shutil.rmtree(assets, ignore_errors=True)
    saida.unlink(missing_ok=True)
    subprocess.run(["manim-slides", "convert", *cenas, str(saida)], check=True)

    originais = []
    for cena in cenas:
        for slide in json.loads(Path(f"slides/{cena}.json").read_text())["slides"]:
            originais.append(slide["file"])
    referenciados = re.findall(r'data-background-video="([^"]+)"', saida.read_text())
    assert len(referenciados) == len(originais), (len(referenciados), len(originais))
    diferentes = []
    for k, (ref, orig) in enumerate(zip(referenciados, originais)):
        if md5(saida.parent / ref) != md5(orig):
            diferentes.append(k)
    if diferentes:
        raise SystemExit(f"slides com vídeo diferente do render: {diferentes}")
    print(f"{saida}: {len(referenciados)} slides, todos idênticos aos vídeos do render atual")


if __name__ == "__main__":
    main()
