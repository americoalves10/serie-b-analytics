
from pathlib import Path
import pandas as pd

arquivos = {
    2022: "data/processed/partidas_serie_b_2022.csv",
    2023: "data/processed/partidas_serie_b_2023.csv",
    2024: "data/processed/partidas_serie_b_2024_completa.csv",
    2025: "data/processed/partidas_serie_b_2025_completa.csv",
}

colunas_obrigatorias = [
    "temporada",
    "data",
    "mandante",
    "visitante",
    "gols_mandante",
    "gols_visitante",
]

for temporada, caminho in arquivos.items():
    print("\n" + "=" * 55)
    print(f"AUDITORIA DA TEMPORADA {temporada}")
    print("=" * 55)

    arquivo = Path(caminho)

    if not arquivo.exists():
        print(f"ERRO: arquivo não encontrado: {caminho}")
        continue

    df = pd.read_csv(arquivo)

    faltantes = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    if faltantes:
        print("Colunas ausentes:", faltantes)
        continue

    datas = pd.to_datetime(df["data"], errors="coerce")
    gols_mandante = pd.to_numeric(
        df["gols_mandante"], errors="coerce"
    )
    gols_visitante = pd.to_numeric(
        df["gols_visitante"], errors="coerce"
    )

    print(f"Partidas: {len(df)}")
    print(f"Equipes: {pd.unique(
        pd.concat([df['mandante'], df['visitante']])
    ).size}")
    print(f"Datas inválidas: {datas.isna().sum()}")
    print(
        "Partidas sem placar:",
        (gols_mandante.isna() | gols_visitante.isna()).sum()
    )

    duplicadas = df.duplicated(
        subset=[
            "data", "mandante", "visitante",
            "gols_mandante", "gols_visitante"
        ]
    ).sum()
    print(f"Linhas duplicadas: {duplicadas}")

    jogos = pd.concat([
        df["mandante"].value_counts(),
        df["visitante"].value_counts()
    ], axis=1).fillna(0)

    jogos["total_jogos"] = jogos.sum(axis=1)

    fora_do_esperado = jogos[
        jogos["total_jogos"] != 38
    ]

    print("Equipes com quantidade diferente de 38 jogos:")
    if fora_do_esperado.empty:
        print("Nenhuma")
    else:
        print(fora_do_esperado[["total_jogos"]].to_string())

    if len(df) == 380 and jogos.shape[0] == 20:
        print("Quantidade de partidas e equipes: OK")
    else:
        print("ATENÇÃO: verificar quantidade de partidas ou equipes")
