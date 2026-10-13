
from pathlib import Path
import pandas as pd

# Arquivo original
arquivo = Path("data/processed/partidas_serie_b_2024.csv")

# Novo arquivo, sem sobrescrever o original
saida = Path("data/processed/partidas_serie_b_2024_completa.csv")

df = pd.read_csv(arquivo)

# Partida confirmada na CBF:
# 22/08/2024 — Sport 0 x 1 Coritiba
data = "2024-08-22"
mandante = "Sport / PE"
visitante = "Coritiba / PR"

# Verifica se a partida já existe
duplicada = (
    (df["data"].astype(str) == data)
    & (df["mandante"] == mandante)
    & (df["visitante"] == visitante)
)

if duplicada.any():
    print("A partida já existe. Nenhuma alteração realizada.")
else:
    nova_partida = pd.DataFrame([{
        "temporada": 2024,
        "data": data,
        "mandante": mandante,
        "visitante": visitante,
        "gols_mandante": 0,
        "gols_visitante": 1
    }])

    df = pd.concat([df, nova_partida], ignore_index=True)

df = df.sort_values("data").reset_index(drop=True)
df.to_csv(saida, index=False, encoding="utf-8-sig")

print(f"Arquivo salvo: {saida}")
print(f"Total de partidas: {len(df)}")
print("\nJogos por equipe:")

equipes = pd.concat([
    df["mandante"].value_counts(),
    df["visitante"].value_counts()
], axis=1).fillna(0)

equipes["jogos"] = equipes.sum(axis=1)
print(equipes[["jogos"]].sort_values("jogos").to_string())
