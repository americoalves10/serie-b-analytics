
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "data" / "processed"

arquivos = [
    "partidas_serie_b_2022.csv",
    "partidas_serie_b_2023.csv",
    "partidas_serie_b_2024_completa.csv",
    "partidas_serie_b_2025_completa.csv",
]

for nome in arquivos:
    caminho = PASTA / nome

    print(f"\n{'=' * 55}")
    print(f"Arquivo: {nome}")

    if not caminho.exists():
        print("ERRO: arquivo não encontrado!")
        continue

    df = pd.read_csv(caminho)

    datas = pd.to_datetime(df["data"], errors="coerce")
    duplicadas = df.duplicated(
        subset=["temporada", "data", "mandante", "visitante"]
    ).sum()

    equipes = set(df["mandante"].dropna()) | set(
        df["visitante"].dropna()
    )

    print(f"Quantidade de partidas: {len(df)}")
    print(f"Temporadas registradas: {df['temporada'].unique().tolist()}")
    print(f"Quantidade de equipes: {len(equipes)}")
    print(f"Datas inválidas: {datas.isna().sum()}")
    print(
        "Placares ausentes:",
        df[["gols_mandante", "gols_visitante"]]
        .isna().any(axis=1).sum()
    )
    print(f"Partidas duplicadas: {duplicadas}")

    if len(df) == 380 and len(equipes) == 20:
        print("Quantidade de partidas e equipes: OK")
    else:
        print("ATENÇÃO: verificar quantidade de partidas ou equipes")
