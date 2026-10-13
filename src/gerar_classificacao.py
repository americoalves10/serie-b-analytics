
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent

ARQUIVO_ENTRADA = (
    RAIZ / "data" / "processed"
    / "partidas_serie_b_2025_completa.csv"
)

ARQUIVO_SAIDA = (
    RAIZ / "data" / "processed"
    / "classificacao_serie_b_2025.csv"
)

df = pd.read_csv(ARQUIVO_ENTRADA)

# Garantir que os placares sejam numéricos.
colunas_gols = ["gols_mandante", "gols_visitante"]

for coluna in colunas_gols:
    df[coluna] = pd.to_numeric(df[coluna], errors="raise")

if df[colunas_gols].isna().any().any():
    raise ValueError("Existem placares ausentes.")

# Estatísticas dos mandantes.
mandantes = pd.DataFrame({
    "equipe": df["mandante"],
    "jogos": 1,
    "vitorias": (df["gols_mandante"] > df["gols_visitante"]).astype(int),
    "empates": (df["gols_mandante"] == df["gols_visitante"]).astype(int),
    "derrotas": (df["gols_mandante"] < df["gols_visitante"]).astype(int),
    "gols_pro": df["gols_mandante"],
    "gols_contra": df["gols_visitante"],
})

# Estatísticas dos visitantes.
visitantes = pd.DataFrame({
    "equipe": df["visitante"],
    "jogos": 1,
    "vitorias": (df["gols_visitante"] > df["gols_mandante"]).astype(int),
    "empates": (df["gols_visitante"] == df["gols_mandante"]).astype(int),
    "derrotas": (df["gols_visitante"] < df["gols_mandante"]).astype(int),
    "gols_pro": df["gols_visitante"],
    "gols_contra": df["gols_mandante"],
})

# Unir os desempenhos como mandante e visitante.
classificacao = pd.concat(
    [mandantes, visitantes],
    ignore_index=True,
)

classificacao = (
    classificacao
    .groupby("equipe", as_index=False)
    .sum(numeric_only=True)
)

classificacao["saldo_gols"] = (
    classificacao["gols_pro"] - classificacao["gols_contra"]
)

classificacao["pontos"] = (
    classificacao["vitorias"] * 3
    + classificacao["empates"]
)

classificacao["aproveitamento_pct"] = (
    classificacao["pontos"]
    / (classificacao["jogos"] * 3)
    * 100
).round(2)

# Ordenação padrão: pontos, vitórias, saldo e gols pró.
classificacao = classificacao.sort_values(
    by=["pontos", "vitorias", "saldo_gols", "gols_pro"],
    ascending=[False, False, False, False],
).reset_index(drop=True)

classificacao.insert(
    0,
    "posicao",
    range(1, len(classificacao) + 1),
)

# Verificações de consistência.
if len(classificacao) != 20:
    raise ValueError("A classificação não contém 20 equipes.")

if not (classificacao["jogos"] == 38).all():
    raise ValueError("Há equipes com número de jogos diferente de 38.")

if (
    classificacao["vitorias"]
    + classificacao["empates"]
    + classificacao["derrotas"]
    != classificacao["jogos"]
).any():
    raise ValueError("Existe inconsistência nos resultados.")

classificacao.to_csv(
    ARQUIVO_SAIDA,
    index=False,
    encoding="utf-8-sig",
)

print("CLASSIFICAÇÃO CALCULADA")
print(classificacao.to_string(index=False))

print(f"\nArquivo salvo em:\n{ARQUIVO_SAIDA}")
