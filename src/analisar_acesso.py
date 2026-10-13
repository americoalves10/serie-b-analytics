
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent

ARQUIVO = (
    RAIZ / "data" / "processed"
    / "classificacao_serie_b_2025.csv"
)

SAIDA = (
    RAIZ / "data" / "processed"
    / "comparacao_acesso_2025.csv"
)

df = pd.read_csv(ARQUIVO)

# Identificar os quatro clubes que conquistaram o acesso.
df["acesso"] = (df["posicao"] <= 4).map({
    True: "Com acesso",
    False: "Sem acesso",
})

# Indicadores por partida.
df["pontos_por_jogo"] = df["pontos"] / df["jogos"]
df["vitorias_pct"] = df["vitorias"] / df["jogos"] * 100
df["gols_pro_por_jogo"] = df["gols_pro"] / df["jogos"]
df["gols_contra_por_jogo"] = df["gols_contra"] / df["jogos"]
df["saldo_por_jogo"] = df["saldo_gols"] / df["jogos"]

indicadores = [
    "pontos",
    "vitorias",
    "empates",
    "derrotas",
    "gols_pro",
    "gols_contra",
    "saldo_gols",
    "aproveitamento_pct",
    "pontos_por_jogo",
    "vitorias_pct",
    "gols_pro_por_jogo",
    "gols_contra_por_jogo",
    "saldo_por_jogo",
]

# Comparar as médias dos dois grupos.
comparacao = (
    df.groupby("acesso")[indicadores]
    .mean()
    .round(2)
    .T
)

comparacao["diferenca_acesso_menos_sem_acesso"] = (
    comparacao["Com acesso"] - comparacao["Sem acesso"]
).round(2)

print("QUANTIDADE DE CLUBES POR GRUPO")
print(df["acesso"].value_counts().to_string())

print("\nCOMPARAÇÃO DAS MÉDIAS")
print(comparacao.to_string())

print("\nCLUBES COM ACESSO")
print(
    df[df["acesso"] == "Com acesso"][
        ["posicao", "equipe", "pontos", "vitorias",
         "gols_pro", "gols_contra", "saldo_gols"]
    ].to_string(index=False)
)

comparacao.to_csv(SAIDA, encoding="utf-8-sig")

print(f"\nComparação salva em:\n{SAIDA}")
