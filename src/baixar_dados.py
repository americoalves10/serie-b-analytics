
import json
from pathlib import Path

import pandas as pd
import requests

# 1. Definir as pastas do projeto
RAIZ = Path(__file__).resolve().parent.parent
PASTA_RAW = RAIZ / "data" / "raw"
PASTA_PROCESSED = RAIZ / "data" / "processed"

PASTA_RAW.mkdir(parents=True, exist_ok=True)
PASTA_PROCESSED.mkdir(parents=True, exist_ok=True)

# 2. Começar pela temporada disponível
TEMPORADAS = [2025]

URL_BASE = (
    "https://raw.githubusercontent.com/"
    "openfootball/football.json/master"
)

partidas = []

# 3. Baixar e processar cada temporada
for temporada in TEMPORADAS:
    url = f"{URL_BASE}/{temporada}/br.2.json"

    print(f"\nBaixando a temporada {temporada}...")

    try:
        resposta = requests.get(url, timeout=30)
        resposta.raise_for_status()

        dados = resposta.json()

        # Salvar o JSON original
        arquivo_json = PASTA_RAW / f"serie_b_{temporada}.json"

        with open(arquivo_json, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=2)

        jogos = dados.get("matches", [])
        print(f"Partidas encontradas: {len(jogos)}")

        for jogo in jogos:
            placar = jogo.get("score")
            gols = None

            # Tratar os dois formatos de placar
            if isinstance(placar, list):
                gols = placar

            elif isinstance(placar, dict):
                gols = placar.get("ft")

            # Validar se existem dois gols numéricos
            placar_valido = (
                isinstance(gols, list)
                and len(gols) == 2
                and all(
                    isinstance(g, (int, float))
                    and not isinstance(g, bool)
                    for g in gols
                )
            )

            if not placar_valido:
                gols_mandante = None
                gols_visitante = None
            else:
                gols_mandante = gols[0]
                gols_visitante = gols[1]

            partidas.append({
                "temporada": temporada,
                "rodada": jogo.get("round"),
                "data": jogo.get("date"),
                "mandante": jogo.get("team1"),
                "visitante": jogo.get("team2"),
                "gols_mandante": gols_mandante,
                "gols_visitante": gols_visitante,
            })

    except requests.RequestException as erro:
        print(f"Erro ao baixar {temporada}: {erro}")

    except (ValueError, TypeError) as erro:
        print(f"Erro ao processar {temporada}: {erro}")

# 4. Criar e salvar a tabela consolidada
df = pd.DataFrame(partidas)

if not df.empty:
    df["data"] = pd.to_datetime(df["data"], errors="coerce")

    arquivo_csv = PASTA_PROCESSED / "partidas_serie_b.csv"

    df.to_csv(
        arquivo_csv,
        index=False,
        encoding="utf-8-sig",
        date_format="%Y-%m-%d"
    )

    print("\nResumo da coleta:")
    print("Total de partidas:", len(df))
    print("Partidas com placar:",
          df["gols_mandante"].notna().sum())
    print("Partidas sem placar:",
          df["gols_mandante"].isna().sum())
    print("\nArquivo criado:", arquivo_csv)

else:
    print("\nNenhuma partida foi carregada.")
