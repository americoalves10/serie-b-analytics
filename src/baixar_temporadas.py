
import json
import re
import urllib.request
from pathlib import Path

import pandas as pd


RAIZ = Path(__file__).resolve().parent.parent
PASTA_RAW = RAIZ / "data" / "raw"
PASTA_PROCESSED = RAIZ / "data" / "processed"

PASTA_RAW.mkdir(parents=True, exist_ok=True)
PASTA_PROCESSED.mkdir(parents=True, exist_ok=True)

URL_BASE = (
    "https://raw.githubusercontent.com/BrazilianFootball/"
    "Data/main/results/processed/Serie_B_{ano}_games.json"
)


def baixar_json(ano):
    url = URL_BASE.format(ano=ano)

    requisicao = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    with urllib.request.urlopen(requisicao, timeout=60) as resposta:
        conteudo = resposta.read()

    arquivo_raw = PASTA_RAW / f"serie_b_{ano}_brazilianfootball.json"
    arquivo_raw.write_bytes(conteudo)

    return json.loads(conteudo.decode("utf-8"))


def converter_partidas(dados, ano):
    registros = []

    partidas = dados.values() if isinstance(dados, dict) else dados

    for partida in partidas:
        resultado = str(partida.get("Result", "")).strip()

        placar = re.search(
            r"(\d+)\s*[xX]\s*(\d+)",
            resultado,
        )

        gols_mandante = None
        gols_visitante = None

        if placar:
            gols_mandante = int(placar.group(1))
            gols_visitante = int(placar.group(2))

        data_original = partida.get("Date")

        data = pd.to_datetime(
            data_original,
            format="%d/%m/%Y",
            errors="coerce",
        )

        registros.append({
            "temporada": ano,
            "data": data,
            "mandante": partida.get("Home"),
            "visitante": partida.get("Away"),
            "gols_mandante": gols_mandante,
            "gols_visitante": gols_visitante,
        })

    return pd.DataFrame(registros)


def auditar(df, ano):
    placar_valido = (
        df["gols_mandante"].notna()
        & df["gols_visitante"].notna()
    )

    equipes = pd.concat(
        [df["mandante"], df["visitante"]],
        ignore_index=True,
    ).dropna().nunique()

    jogos_por_equipe = pd.concat(
        [df["mandante"], df["visitante"]],
        ignore_index=True,
    ).value_counts()

    duplicadas = df.duplicated(
        subset=["data", "mandante", "visitante"]
    ).sum()

    print(f"\n{'=' * 45}")
    print(f"AUDITORIA DA TEMPORADA {ano}")
    print(f"{'=' * 45}")
    print("Total de partidas:", len(df))
    print("Partidas com placar:", int(placar_valido.sum()))
    print("Partidas sem placar:", int((~placar_valido).sum()))
    print("Datas inválidas:", int(df["data"].isna().sum()))
    print("Equipes identificadas:", equipes)
    print("Confrontos duplicados:", int(duplicadas))

    print("\nEquipes com número de jogos diferente de 38:")
    diferentes = jogos_por_equipe[jogos_por_equipe != 38]

    if diferentes.empty:
        print("Nenhuma")
    else:
        print(diferentes.to_string())

    # Salvar mesmo quando a auditoria detectar problemas,
    # para que possamos investigar os registros.
    arquivo_saida = (
        PASTA_PROCESSED / f"partidas_serie_b_{ano}.csv"
    )

    df_exportar = df.copy()
    df_exportar["data"] = df_exportar["data"].dt.strftime("%Y-%m-%d")

    df_exportar.to_csv(
        arquivo_saida,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nArquivo salvo em:")
    print(arquivo_saida)


def main():
    for ano in [2022, 2023, 2024]:
        print(f"\nBaixando Série B de {ano}...")

        try:
            dados = baixar_json(ano)
            df = converter_partidas(dados, ano)
            auditar(df, ano)

        except Exception as erro:
            print(f"\nErro ao processar {ano}: {erro}")
            print("A temporada será investigada separadamente.")


if __name__ == "__main__":
    main()
