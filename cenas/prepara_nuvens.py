"""Prepara as imagens e a persistência da aplicação em satélite (Ver Hoef et al. 2023).

Entradas, em assets/nuvens/ (ver escolhidas.json):
- cena_<padrão>.jpeg: cenas MODIS (NASA Worldview Snapshots, 2100 x 1400, 0,01 grau por pixel),
  baixadas pela data e região dos rótulos de Rasp et al. (2020);
- escolhidas.json: a caixa de consenso de cada padrão (interseção dos retângulos de 4+ especialistas)
  e a URL da cena no NASA Worldview.

A persistência segue o código dos autores (github.com/zyjux/sffg_tda): imagem em tons de cinza (PIL "L"),
janelas de 96 x 96, gudhi.CubicalComplex(top_dimensional_cells=255 - janela) com coeficientes em Z2,
H0 sem a barra infinita, paisagens com 5 funções amostradas em 200 pontos de [0, 255], média de 6 janelas.

Saídas em assets/nuvens/: os PNGs de exibição e persistencia.json.
Uso (em cenas/, com o env ativo): python prepara_nuvens.py
"""
from __future__ import annotations

import json
from pathlib import Path

import gudhi
import numpy as np
from PIL import Image

PASTA = Path(__file__).parent / "assets" / "nuvens"
JANELA = 96
N_JANELAS = 6
N_FUNCOES = 5
N_AMOSTRAS = 200
LIMIARES = [250, 225, 200, 175, 150, 125, 100, 75, 50]  # brilho; a filtração desce do claro ao escuro
TILE_DA_TELA = "flower"  # o padrão cujo tile a seção 7 acompanha, da cor ao diagrama


def barras(janela: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """H0 (finitas) e H1 da janela, na convenção dos autores: subnível de 255 - cinza."""
    complexo = gudhi.CubicalComplex(top_dimensional_cells=255 - janela.astype(float))
    complexo.compute_persistence(homology_coeff_field=2)
    h0 = complexo.persistence_intervals_in_dimension(0)
    h0 = h0[np.isfinite(h0[:, 1])]
    h1 = complexo.persistence_intervals_in_dimension(1)
    return h0, h1


def paisagem(intervalos: np.ndarray) -> np.ndarray:
    """As N_FUNCOES primeiras funções da paisagem, amostradas em N_AMOSTRAS pontos de [0, 255].
    λ_k(t) é o k-ésimo maior valor de max(0, min(t - b, d - t)) entre as barras (b, d)."""
    t = np.linspace(0, 255, N_AMOSTRAS)
    saida = np.zeros((N_FUNCOES, N_AMOSTRAS))
    if len(intervalos) == 0:
        return saida
    tendas = np.maximum(0, np.minimum(t[None, :] - intervalos[:, :1], intervalos[:, 1:] - t[None, :]))
    tendas = -np.sort(-tendas, axis=0)
    m = min(N_FUNCOES, len(intervalos))
    saida[:m] = tendas[:m]
    return saida


def regiao_de_exibicao(nome: str, consenso: list[float]) -> tuple[int, int, int, int]:
    """A parte da caixa de consenso que vai para a tela (sem as faixas pretas entre passagens do MODIS)."""
    x0, y0, x1, y1 = (int(v) for v in consenso)
    if nome == "flower":
        return (x0, y0, x0 + 600, y0 + 600)  # o quadrante de cima à esquerda; a faixa preta fica à direita
    if nome in ("sugar", "gravel"):
        lado = min(x1 - x0, y1 - y0)
        cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
        return (cx - lado // 2, cy - lado // 2, cx + lado // 2, cy + lado // 2)
    return (x0, y0, x1 - 150, y1)  # fish: a faixa alongada, sem a ponta da faixa preta à direita


def ampliado(arr: np.ndarray, lado: int) -> Image.Image:
    """A janela ampliada sem suavizar, para os pixels ficarem visíveis."""
    return Image.fromarray(arr.astype(np.uint8)).resize((lado, lado), Image.NEAREST)


def main() -> None:
    escolhidas = json.loads((PASTA / "escolhidas.json").read_text())
    rng = np.random.default_rng(2023)
    saida = {"janela": JANELA, "limiares": LIMIARES, "padroes": {}}

    for nome, info in escolhidas.items():
        cena = Image.open(PASTA / f"cena_{nome}.jpeg")
        regiao = regiao_de_exibicao(nome, info["consenso"])
        if nome == "fish":
            # A faixa de fish é alongada; na tela vai um quadrado do meio dela.
            x0, y0, x1, y1 = regiao
            lado = y1 - y0
            meio = (x0 + x1) // 2
            cena.convert("RGB").crop((meio - lado // 2, y0, meio + lado // 2, y1)).save(PASTA / "padrao_fish_quadrado.png")
        else:
            cena.convert("RGB").crop(regiao).save(PASTA / f"padrao_{nome}.png")
        saida["padroes"][nome] = {"regiao": regiao, "tamanho_cena": list(cena.size)}

        if nome not in ("sugar", "flower"):
            continue
        cinza = np.array(cena.convert("L"))
        x0, y0, x1, y1 = regiao
        janelas = []
        paisagens = []
        for _ in range(N_JANELAS):
            x = int(rng.integers(x0, x1 - JANELA))
            y = int(rng.integers(y0, y1 - JANELA))
            h0, h1 = barras(cinza[y:y + JANELA, x:x + JANELA])
            janelas.append({"x": x, "y": y, "n_h0": len(h0), "n_h1": len(h1)})
            paisagens.append(np.concatenate([paisagem(h0), paisagem(h1)]))
        media = np.mean(paisagens, axis=0)
        # Na tela vai a janela de maior contraste entre as 6 (uma janela só de céu limpo não mostra nada);
        # a média continua sendo das 6, como no método.
        contrastes = []
        for j in janelas:
            contrastes.append(float(np.std(cinza[j["y"]:j["y"] + JANELA, j["x"]:j["x"] + JANELA])))
        exibida = int(np.argmax(contrastes))
        primeira = cinza[janelas[exibida]["y"]:janelas[exibida]["y"] + JANELA, janelas[exibida]["x"]:janelas[exibida]["x"] + JANELA]
        h0, h1 = barras(primeira)
        if nome == TILE_DA_TELA:
            ampliado(primeira, 480).save(PASTA / f"janela_{nome}.png")
            # O mesmo tile em cor, para a tela mostrar a passagem para tons de cinza.
            j = janelas[exibida]
            cor = np.array(cena.convert("RGB"))[j["y"]:j["y"] + JANELA, j["x"]:j["x"] + JANELA]
            ampliado(cor, 480).save(PASTA / f"janela_{nome}_cor.png")
            for k, limiar in enumerate(LIMIARES):
                # Superlevel: entra o que tem brilho >= limiar; o resto fica escuro.
                mascara = np.where(primeira >= limiar, primeira, 0.15 * primeira)
                ampliado(mascara, 480).save(PASTA / f"janela_{nome}_limiar_{k}.png")
        saida["padroes"][nome].update({
            "janelas": janelas, "exibida": exibida,
            "diagrama_h0": h0.tolist(), "diagrama_h1": h1.tolist(),
            "paisagem_exibida": paisagens[exibida].tolist(),
            "paisagem_media": media.tolist(),
        })
        print(f"{nome}: janela exibida {exibida + 1} com {len(h0)} pontos em H0 e {len(h1)} em H1; "
              f"pico da paisagem média: H0 {media[0].max():.1f}, H1 {media[N_FUNCOES].max():.1f}")

    (PASTA / "persistencia.json").write_text(json.dumps(saida))
    cena = Image.open(PASTA / "cena_flower.jpeg").convert("RGB")
    cena.resize((1050, 700), Image.LANCZOS).save(PASTA / "cena_flower_tela.png")
    print("ok")


if __name__ == "__main__":
    main()
