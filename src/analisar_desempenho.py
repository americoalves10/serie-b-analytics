
from pathlib import Path
import pandas as pd

arquivo_jogos = Path(
    "data/processed/partidas_serie_b_2022_2025.csv"
)
arquivo_acessos = Path(
    "data/processed/clubes_promovidos.csv"
)

jogos = pd.read_csv(arquivo_jogos)
promovidos = pd.read_csv(arquivo_acessos)

# Padronizar tipos
jogos["temporada"] = pd.to_numeric(
    jogos["temporada"], errors="raise"
)
promovidos["temporada"] = pd.to_numeric(
    promovidos["temporada"], errors="raise"
)

jogos["gols_mandante"] = pd.to_numeric(
    jogos["gols_mandante"], errors="raise"
)
jogos["gols_visitante"] = pd.to_numeric(
    jogos["gols_visitante"], errors="raise"
)

registros = []

for _, jogo in jogos.iterrows():
    temporada = jogo["temporada"]
    mandante = jogo["mandante"]
    visitante = jogo["visitante"]
    gm = int(jogo["gols_mandante"])
    gv = int(jogo["gols_visitante"])

    if gm > gv:
        resultado_mandante = (1, 0, 0)
        resultado_visitante = (0, 0, 1)
    elif gm < gv:
        resultado_mandante = (0, 0, 1)
        resultado_visitante = (1, 0, 0)
    else:
        resultado_mandante = (0, 1, 0)
        resultado_visitante = (0, 1, 0)

    registros.append({
        "temporada": temporada,
        "clube": mandante,
        "vitorias": resultado_mandante[0],
        "empates": resultado_mandante[1],
        "derrotas": resultado_mandante[2],
        "gols_marcados": gm,
        "gols_sofridos": gv,
    })

    registros.append({
        "temporada": temporada,
        "clube": visitante,
        "vitorias": resultado_visitante[0],
        "empates": resultado_visitante[1],
        "derrotas": resultado_visitante[2],
        "gols_marcados": gv,
        "gols_sofridos": gm,
    })

desempenho = (
    pd.DataFrame(registros)
    .groupby(["temporada", "clube"], as_index=False)
    .agg(
        partidas=("vitorias", "size"),
        vitorias=("vitorias", "sum"),
        empates=("empates", "sum"),
        derrotas=("derrotas", "sum"),
        gols_marcados=("gols_marcados", "sum"),
        gols_sofridos=("gols_sofridos", "sum"),
    )
)

desempenho["pontos"] = (
    desempenho["vitorias"] * 3 + desempenho["empates"]
)
desempenho["saldo_gols"] = (
    desempenho["gols_marcados"] - desempenho["gols_sofridos"]
)
desempenho["aproveitamento_pct"] = (
    desempenho["pontos"] / (desempenho["partidas"] * 3) * 100
)

# Marcar clubes promovidos usando temporada e nome
chaves_promovidos = set(
    zip(promovidos["temporada"], promovidos["clube"])
)

desempenho["promovido"] = [
    (temporada, clube) in chaves_promovidos
    for temporada, clube in zip(
        desempenho["temporada"], desempenho["clube"]
    )
]

desempenho = desempenho.sort_values(
    ["temporada", "pontos", "saldo_gols"],
    ascending=[True, False, False]
)

saida = Path(
    "data/processed/desempenho_equipes_2022_2025.csv"
)
desempenho.to_csv(saida, index=False, encoding="utf-8-sig")

print("Análise concluída!")
print(f"Equipes-temporada analisadas: {len(desempenho)}")
print(f"Arquivo salvo: {saida}")

print("\nClubes promovidos:")
print(
    desempenho[desempenho["promovido"]][
        ["temporada", "clube", "partidas", "vitorias",
         "empates", "derrotas", "pontos", "saldo_gols",
         "aproveitamento_pct"]
    ].to_string(index=False)
)

print("\nMédias por grupo:")
print(
    desempenho.groupby("promovido")[
        ["pontos", "vitorias", "gols_marcados",
         "gols_sofridos", "saldo_gols", "aproveitamento_pct"]
    ].mean().round(2).to_string()
)
