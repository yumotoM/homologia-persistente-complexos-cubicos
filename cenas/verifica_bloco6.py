"""Confere o bloco 6 (aplicação em satélite): o que é calculado e cada número da tela e das notas.

Uso (em cenas/, com o env ativo): python verifica_bloco6.py
"""
from __future__ import annotations

import numpy as np
from PIL import Image

import dados_bloco6 as d
import prepara_nuvens as p


def confere(condicao: bool, mensagem: str) -> None:
    assert condicao, mensagem
    print("ok:", mensagem)


# A paisagem calculada à mão bate com a definição, ponto a ponto, numa barra qualquer.
rng = np.random.default_rng(7)
barras = np.sort(rng.uniform(0, 255, size=(40, 2)), axis=1)
calculada = p.paisagem(barras)
t = np.linspace(0, 255, d.N_AMOSTRAS)
certo = True
for i, tt in enumerate(t):
    alturas = sorted((max(0.0, min(tt - b, m - tt)) for b, m in barras), reverse=True)
    for k in range(d.N_FUNCOES):
        if abs(alturas[k] - calculada[k, i]) > 1e-9:
            certo = False
confere(certo, "a paisagem (λ1 a λ5 em 200 pontos) bate com a definição: k-ésima maior tenda em cada t")
confere(2 * d.N_FUNCOES * d.N_AMOSTRAS == 2000, "o vetor de cada recorte tem 2 x 5 x 200 = 2000 números")

dados = d.persistencia()
esc = d.escolhidas()
for nome in ("sugar", "flower"):
    info = dados["padroes"][nome]
    x0, y0, x1, y1 = info["regiao"]
    dentro = all(x0 <= j["x"] and j["x"] + d.JANELA <= x1 and y0 <= j["y"] and j["y"] + d.JANELA <= y1 for j in info["janelas"])
    confere(len(info["janelas"]) == d.N_JANELAS and dentro, f"{nome}: 6 janelas de 96 x 96 dentro da área de consenso")
    cinza = np.array(Image.open(d.PASTA / f"cena_{nome}.jpeg").convert("L"))
    j = info["janelas"][info["exibida"]]
    h0, h1 = p.barras(cinza[j["y"]:j["y"] + d.JANELA, j["x"]:j["x"] + d.JANELA])
    confere(np.allclose(h0, info["diagrama_h0"]) and np.allclose(h1, info["diagrama_h1"]),
            f"{nome}: o diagrama da janela exibida é o que o GUDHI devolve ({len(h0)} pontos em H0, {len(h1)} em H1)")

media_s = np.array(dados["padroes"]["sugar"]["paisagem_media"])
media_f = np.array(dados["padroes"]["flower"]["paisagem_media"])
confere(media_s[0].max() > media_f[0].max(),
        f"H0: o pico da paisagem média é mais alto no sugar ({media_s[0].max():.0f}) que no flowers ({media_f[0].max():.0f}), como no artigo")
confere(media_f[d.N_FUNCOES].max() > media_s[d.N_FUNCOES].max(),
        f"H1: mais forte no flowers ({media_f[d.N_FUNCOES].max():.0f}) que no sugar ({media_s[d.N_FUNCOES].max():.0f}), como no artigo")
picos_s = [media_s[k].max() for k in range(d.N_FUNCOES)]
picos_f = [media_f[k].max() for k in range(d.N_FUNCOES)]
confere(picos_s[0] - picos_s[-1] < 10 and picos_f[0] - picos_f[-1] > 15,
        f"H0: λ1 a λ5 quase iguais no sugar ({picos_s[0]:.0f} a {picos_s[-1]:.0f}) e espalhadas no flowers ({picos_f[0]:.0f} a {picos_f[-1]:.0f})")
area_h1_s, area_h1_f = media_s[d.N_FUNCOES:].sum(), media_f[d.N_FUNCOES:].sum()
confere(1.1 < area_h1_f / area_h1_s < 1.3,
        f"H1 aparece nos dois; no flowers tem {100 * (area_h1_f / area_h1_s - 1):.0f}% a mais de área (\"um pouco maior\", \"cerca de 20%\")")
exibida = np.array(dados["padroes"]["flower"]["paisagem_exibida"])
confere(exibida.shape == (2 * d.N_FUNCOES, d.N_AMOSTRAS) and exibida.max() < 100,
        f"o vetor da tela tem 10 linhas de 200 amostras, e a paisagem cabe no eixo de altura 100 (máximo {exibida.max():.0f})")

for nome, info in esc.items():
    confere(info["especialistas_no_padrao"] >= 4, f"{nome}: consenso de {info['especialistas_no_padrao']} especialistas no recorte")

# O tile da tela: em cor, é o recorte da cena; em cinza, é a conta φ da seção 2 (a conversão "L" do PIL).
info = dados["padroes"]["flower"]
j = info["janelas"][info["exibida"]]
cena = Image.open(d.PASTA / "cena_flower.jpeg")
rgb = np.array(cena.convert("RGB"))[j["y"]:j["y"] + d.JANELA, j["x"]:j["x"] + d.JANELA].astype(float)
tile_cor = np.array(Image.open(d.PASTA / "janela_flower_cor.png").convert("RGB"))
confere(np.array_equal(tile_cor[::5, ::5], rgb.astype(np.uint8)),
        "o tile colorido da tela é o recorte 96 x 96 da cena, ampliado 5 vezes sem suavizar")
phi = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114
cinza = np.array(cena.convert("L"))[j["y"]:j["y"] + d.JANELA, j["x"]:j["x"] + d.JANELA].astype(float)
confere(np.abs(phi - cinza).max() <= 1,
        "o cinza do PIL é φ(R, G, B) = 0,299R + 0,587G + 0,114B, a menos do arredondamento")

confere(round(d.km(d.JANELA)) == 107, f"a janela de 96 pixels tem cerca de {d.km(d.JANELA):.0f} km de lado (≈ 100 km)")
x0, _, x1, _ = dados["padroes"]["fish"]["regiao"]
confere(1500 < d.km(x1 - x0) < 2200, f"a faixa de fish mostrada tem cerca de {d.km(x1 - x0):.0f} km de comprimento")

acuracias = [a for _, _, a in d.ACURACIAS]
confere(acuracias == sorted(acuracias, reverse=True) and acuracias[0] == 89.25 and acuracias[-1] == 57.0,
        "acurácias da Fig. 10, da maior (sugar x flowers, 89,25%) à menor (fish x flowers, 57%)")
