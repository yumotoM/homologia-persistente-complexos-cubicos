# Homologia persistente em complexos cúbicos: teoria, exemplo e aplicação

Apresentação animada (ManimGL + manim-slides) que constrói, passo a passo e à mão, a homologia persistente de uma imagem em complexos cúbicos, e termina numa aplicação com imagens de satélite.

## Motivação

Esta apresentação foi feita para a disciplina SME0231 – Análise Topológica de Dados, do Instituto de Ciências Matemáticas e de Computação (ICMC-USP), no 2º semestre de 2026. A pergunta que a guia é como a homologia persistente é calculada quando o dado é uma imagem.

Em imagens e volumes, o complexo natural é o cúbico, não o simplicial. Cada pixel (ou voxel) já é uma célula de uma grade, e triangular a grade só para usar os algoritmos usuais aumenta o número de células, numa proporção que cresce com a dimensão. A apresentação segue o fluxo de Wagner, Chen e Vuçini (2012), que calcula a persistência direto na grade, e o percorre à mão numa imagem 5 × 5, o exemplo de Otter et al. (2017):

1. da imagem ao complexo cúbico;
2. do complexo à filtração;
3. da filtração à matriz de bordo ordenada;
4. da redução da matriz ao diagrama de persistência.

No fim, o mesmo fluxo aparece numa aplicação real, na área de pesquisa do autor, o sensoriamento remoto: a classificação de padrões de nuvens em imagens de satélite de Ver Hoef et al. (2023). Lá, a persistência funciona como extratora de atributos interpretáveis.

Os slides são animações em ManimGL com manim-slides, para mostrar passo a passo o que numa figura parada fica escondido, como a filtração e a redução da matriz.

O código também confere a matemática. Os scripts `verifica_bloco*.py` comparam cada número da tela e cada afirmação das notas com um cálculo independente: uma implementação de referência da redução (`referencia.py`), o GUDHI ou a própria definição. São 141 checagens.

## O que tem

São 80 slides em 7 seções, todos com notas para o apresentador.

| Seção | Cena | Arquivo |
| --- | --- | --- |
| Capa e sumário | `Abertura` | `cenas/bloco1.py` |
| 1. TDA e o fluxo da persistência; 2. O formato do dado | `FluxoEFormato` | `cenas/bloco1.py` |
| 3. Complexos cúbicos | `ConstrucaoDoComplexo` | `cenas/bloco2.py` |
| 4. Filtração | `ConstrucaoDaFiltracao` | `cenas/bloco3.py` |
| 5. Matriz de bordo e redução | `MatrizEReducao` | `cenas/bloco4.py` |
| 6. Leitura do diagrama | `LeituraDoDiagrama` | `cenas/bloco5.py` |
| 7. Aplicação: imagens de satélite | `AplicacaoSatelite` | `cenas/bloco6.py` |

## Ver a apresentação

Baixe o `apresentacao_completa.html` na página [Releases](https://github.com/yumotoM/homologia-persistente-complexos-cubicos/releases) e abra no navegador. É um arquivo único (os vídeos vão embutidos), funciona sem internet e não precisa instalar nada.

| Tecla | O que faz |
| --- | --- |
| setas | avançar e voltar |
| `S` | modo apresentador, com as notas de cada slide |
| `F` | tela cheia |

## Regenerar a apresentação

Testado no Ubuntu 22.04.

### 1. Instalar o LaTeX, pelo sistema

As fórmulas são compiladas pelo LaTeX, e a fonte dos números (Latin Modern) vem junto com ele:

```bash
sudo apt install texlive-latex-extra texlive-fonts-extra texlive-science
```

### 2. Criar o ambiente, com conda

O resto (Python 3.11, ManimGL, manim-slides, GUDHI, Qt e ffmpeg) vem do `environment.yml`, com as versões em que a apresentação foi renderizada:

```bash
conda env create -f environment.yml
conda activate complexos-cubicos
```

### 3. Preparar os assets e conferir os números

Todos os comandos daqui em diante rodam dentro de `cenas/`, onde fica o `custom_config.yml` (1080p, fundo preto).

```bash
cd cenas
python prepara_imagens.py
python prepara_nuvens.py
for n in 1 2 3 4 5 6; do python verifica_bloco$n.py; done
```

- `prepara_imagens.py` gera, a partir da foto original, as imagens do cachorro da seção 2.
- `prepara_nuvens.py` gera, a partir das cenas MODIS, os recortes, o tile e a persistência das nuvens da seção 7.
- Cada verificação imprime `ok:` seguido do que conferiu e para no primeiro erro.

### 4. Renderizar os slides

```bash
manim-slides render --GL bloco1.py Abertura FluxoEFormato
manim-slides render --GL bloco2.py ConstrucaoDoComplexo
manim-slides render --GL bloco3.py ConstrucaoDaFiltracao
manim-slides render --GL bloco4.py MatrizEReducao
manim-slides render --GL bloco5.py LeituraDoDiagrama
manim-slides render --GL bloco6.py AplicacaoSatelite
```

Os vídeos vão para `slides/`. Ao renderizar de novo uma cena, apague antes a pasta `videos/<Cena>/`. O ManimGL não remove os vídeos parciais de renders anteriores, e o `folha_contato.py` os somaria na conferência de cobertura.

### 5. Conferir as transições

```bash
python folha_contato.py Abertura FluxoEFormato ConstrucaoDoComplexo ConstrucaoDaFiltracao MatrizEReducao LeituraDoDiagrama AplicacaoSatelite
```

O script gera `revisao/<Cena>.png`, com o início, o meio e o fim de cada slide. Ele também acusa saltos entre slides e tempo de vídeo que não ficou em nenhum slide.

### 6. Exportar os HTMLs

```bash
CENAS="Abertura FluxoEFormato ConstrucaoDoComplexo ConstrucaoDaFiltracao MatrizEReducao LeituraDoDiagrama AplicacaoSatelite"
python exporta_html.py apresentacao.html $CENAS
manim-slides convert --one-file --offline $CENAS apresentacao_completa.html
```

- **`apresentacao.html`:** os vídeos ficam ao lado, em `apresentacao_assets/`. O `exporta_html.py` apaga essa pasta antes de converter e confere, byte a byte, cada vídeo contra o render atual. Sem isso, o `manim-slides convert` reaproveita vídeos de renders anteriores.
- **`apresentacao_completa.html`:** um arquivo só, com os vídeos embutidos. É o da release.

## Estrutura

```
environment.yml          ambiente conda
ruff.toml                lint: type hints obrigatórias (ANN), pathlib (PTH), imports sem uso (F401)
cenas/
  custom_config.yml      configuração do ManimGL
  estilo.py              cores, sumário, fluxo da persistência, fecha_passo (nota de cada slide)
  bloco1.py … bloco6.py  as cenas
  dados_bloco2.py …      os números que cada cena desenha
  referencia.py          implementação independente da persistência cúbica, usada pelas verificações
  verifica_bloco1.py …   as verificações
  prepara_imagens.py     imagens da seção 2
  prepara_nuvens.py      imagens e persistência da seção 7
  folha_contato.py       conferência das transições
  exporta_html.py        exportação do HTML com os vídeos conferidos
  assets/                entradas: a foto do cachorro, as cenas MODIS e as caixas de consenso
```

## Referências

Só as que aparecem nos slides.

- Wagner, H., Chen, C. e Vuçini, E. (2012). Efficient computation of persistent homology for cubical data. Em *Topological Methods in Data Analysis and Visualization II* (TopoInVis 2011), Mathematics and Visualization, Springer, p. 91–106. https://doi.org/10.1007/978-3-642-23175-9_7
- Otter, N., Porter, M. A., Tillmann, U., Grindrod, P. e Harrington, H. A. (2017). A roadmap for the computation of persistent homology. *EPJ Data Science*, 6, 17. https://doi.org/10.1140/epjds/s13688-017-0109-5
- Dłotko, P. e Wanner, T. (2018). Rigorous cubical approximation and persistent homology of continuous functions. *Computers & Mathematics with Applications*, 75(5), 1648–1666. https://doi.org/10.1016/j.camwa.2017.11.027 (pré-print de 2016: arXiv:1610.03833)
- Edelsbrunner, H., Letscher, D. e Zomorodian, A. (2002). Topological persistence and simplification. *Discrete & Computational Geometry*, 28(4), 511–533. https://doi.org/10.1007/s00454-002-2885-2
- Cohen-Steiner, D., Edelsbrunner, H. e Harer, J. (2007). Stability of persistence diagrams. *Discrete & Computational Geometry*, 37(1), 103–120. https://doi.org/10.1007/s00454-006-1276-5
- The GUDHI Project. *GUDHI User and Reference Manual*, versão 3.13. https://gudhi.inria.fr/doc/3.13.0/
- Ver Hoef, L., Adams, H., King, E. J. e Ebert-Uphoff, I. (2023). A primer on topological data analysis to support image analysis tasks in environmental science. *Artificial Intelligence for the Earth Systems*, 2(1). https://doi.org/10.1175/AIES-D-22-0039.1
- Rasp, S., Schulz, H., Bony, S. e Stevens, B. (2020). Combining crowdsourcing and deep learning to explore the mesoscale organization of shallow convection. *Bulletin of the American Meteorological Society*, 101(11), E1980–E1995. https://doi.org/10.1175/BAMS-D-19-0324.1

## Créditos

- **Foto do cachorro:** "White Swiss Shepherd portrait", de Joselodos, CC0, [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:White_Swiss_Shepherd_portrait.jpg).
- **Imagens de satélite:** MODIS (Terra e Aqua), pelo NASA Worldview. We acknowledge the use of imagery from the NASA Worldview application (https://worldview.earthdata.nasa.gov), part of the NASA Earth Science Data and Information System (ESDIS). As URLs de cada cena estão em `cenas/assets/nuvens/escolhidas.json`.
- **Rótulos das nuvens:** as caixas de consenso em `escolhidas.json` (a área em que 4 ou mais especialistas concordaram) derivam dos rótulos públicos de Rasp et al. (2020), em [github.com/raspstephan/sugar-flower-fish-or-gravel](https://github.com/raspstephan/sugar-flower-fish-or-gravel). Esse repositório não declara licença; o uso aqui é acadêmico e com citação.
- **Exemplos redesenhados:** a imagem do exemplo (Otter et al., 2017, Fig. 2), a subdivisão retangular (Dłotko e Wanner, Fig. 2) e o fluxo e as cores das células (Wagner et al., Figs. 2 e 3) foram redesenhados a partir dos artigos, citados nos rodapés dos slides.

## Licença

- **Código** (os `.py`, `environment.yml`, `ruff.toml` e `custom_config.yml`): [MIT](LICENSE).
- **Conteúdo** (o texto dos slides e das notas, as animações, os HTMLs e este README): [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.pt_BR).
- **Material de terceiros:** fica com os termos de origem, listados em Créditos.

© 2026 Murillo Yumoto.
