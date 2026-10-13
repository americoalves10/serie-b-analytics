
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent

ARQUIVO_ORIGINAL = (
    RAIZ / "data" / "processed"
    / "partidas_serie_b_2025_brazilianfootball.csv"
)

ARQUIVO_FINAL = (
    RAIZ / "data" / "processed"
    / "partidas_serie_b_2025_completa.csv"
)

df = pd.read_csv(ARQUIVO_ORIGINAL)

# Partidas confirmadas nas páginas oficiais da CBF.
novos_jogos = pd.DataFrame([
    {
        "temporada": 2025,
        "data": "2025-05-15",
        "mandante": "Ferroviária / SP",
        "visitante": "Avaí / SC",
        "gols_mandante": 1,
        "gols_visitante": 1,
    },
    {
        "temporada": 2025,
        "data": "2025-07-13",
        "mandante": "Criciúma / SC",
        "visitante": "Ferroviária / SP",
        "gols_mandante": 2,
        "gols_visitante": 1,
    },
    {
        "temporada": 2025,
        "data": "2025-07-14",
        "mandante": "Athletic / MG",
        "visitante": "Avaí / SC",
        "gols_mandante": 4,
        "gols_visitante": 0,
    },
    {
        "temporada": 2025,
        "data": "2025-08-03",
        "mandante": "Athletico Paranaense / PR",
        "visitante": "Paysandu / PA",
        "gols_mandante": 1,
        "gols_visitante": 1,
    },
    {
        "temporada": 2025,
        "data": "2025-11-09",
        "mandante": "Paysandu / PA",
        "visitante": "Coritiba / PR",
        "gols_mandante": 1,
        "gols_visitante": 2,
    },
])

# Impedir que os jogos sejam acrescentados duas vezes.
chaves = ["data", "mandante", "visitante"]

df["data"] = pd.to_datetime(
    df["data"], errors="raise"
).dt.strftime("%Y-%m-%d")

novos_jogos["data"] = pd.to_datetime(
    novos_jogos["data"], errors="raise"
).dt.strftime("%Y-%m-%d")

existentes = set(map(tuple, df[chaves].values.tolist()))
adicionais = set(map(tuple, novos_jogos[chaves].values.tolist()))

if len(adicionais) != 5:
    raise ValueError("Existem jogos repetidos na lista adicional.")

if existentes.intersection(adicionais):
    raise ValueError(
        "Pelo menos um dos cinco jogos já existe na base original."
    )

df_completa = pd.concat(
    [df, novos_jogos],
    ignore_index=True,
)

# Validar antes de salvar.
equipes = pd.concat([
    df_completa["mandante"],
    df_completa["visitante"],
]).value_counts()

print("Partidas:", len(df_completa))
print("Equipes:", len(equipes))
print("Equipes com 38 jogos:", int((equipes == 38).sum()))
print("Equipes fora de 38 jogos:", int((equipes != 38).sum()))

if len(df_completa) != 380:
    raise ValueError("A base não contém exatamente 380 partidas.")

if len(equipes) != 20 or not (equipes == 38).all():
    raise ValueError(
        "A validação das equipes falhou. "
        "Confira os nomes e a distribuição dos jogos."
    )

if df_completa.duplicated(subset=chaves).any():
    raise ValueError("Foram encontrados confrontos duplicados.")

df_completa = df_completa.sort_values("data")
df_completa.to_csv(
    ARQUIVO_FINAL,
    index=False,
    encoding="utf-8-sig",
)

print("\nBase validada e salva em:")
print(ARQUIVO_FINAL)
