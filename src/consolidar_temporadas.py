
from pathlib import Path
import pandas as pd

arquivos = [
    "data/processed/partidas_serie_b_2022.csv",
    "data/processed/partidas_serie_b_2023.csv",
    "data/processed/partidas_serie_b_2024_completa.csv",
    "data/processed/partidas_serie_b_2025_completa.csv",
]

bases = []

for caminho in arquivos:
    arquivo = Path(caminho)

    if not arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho}"
        )

    df = pd.read_csv(arquivo)
    bases.append(df)

# Unir as temporadas
consolidado = pd.concat(bases, ignore_index=True)

# Ordenar cronologicamente
consolidado["data"] = pd.to_datetime(
    consolidado["data"], errors="raise"
)

consolidado = consolidado.sort_values(
    ["temporada", "data"]
).reset_index(drop=True)

# Salvar a base consolidada
saida = Path(
    "data/processed/partidas_serie_b_2022_2025.csv"
)

consolidado.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig",
    date_format="%Y-%m-%d"
)

print("Consolidação concluída!")
print(f"Arquivo: {saida}")
print(f"Total de partidas: {len(consolidado)}")

print("\nPartidas por temporada:")
print(consolidado.groupby("temporada").size().to_string())

print("\nEquipes por temporada:")
for temporada, grupo in consolidado.groupby("temporada"):
    equipes = pd.unique(
        pd.concat([
            grupo["mandante"],
            grupo["visitante"]
        ])
    )
    print(f"{temporada}: {len(equipes)} equipes")

print("\nPrimeiras linhas:")
print(consolidado.head().to_string(index=False))
