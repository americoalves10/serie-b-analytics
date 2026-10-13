
from pathlib import Path
import pandas as pd

# Diretório raiz do projeto
RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "data" / "processed"

# Bases auditadas de cada temporada
arquivos = [
    PASTA / "partidas_serie_b_2022.csv",
    PASTA / "partidas_serie_b_2023.csv",
    PASTA / "partidas_serie_b_2024_completa.csv",
    PASTA / "partidas_serie_b_2025_completa.csv",
]

bases = []

for arquivo in arquivos:
    if not arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {arquivo}"
        )

    df = pd.read_csv(arquivo)

    colunas_esperadas = [
        "temporada",
        "data",
        "mandante",
        "visitante",
        "gols_mandante",
        "gols_visitante",
    ]

    if list(df.columns) != colunas_esperadas:
        raise ValueError(
            f"Colunas inesperadas no arquivo: {arquivo.name}"
        )

    bases.append(df)

# Consolidar as quatro temporadas
consolidado = pd.concat(bases, ignore_index=True)

# Validar as datas
consolidado["data"] = pd.to_datetime(
    consolidado["data"], errors="raise"
)

# Ordenar cronologicamente
consolidado = consolidado.sort_values(
    ["temporada", "data"]
).reset_index(drop=True)

# Validar a quantidade de partidas por temporada
partidas_por_temporada = (
    consolidado.groupby("temporada").size()
)

esperado = {2022: 380, 2023: 380, 2024: 380, 2025: 380}

if partidas_por_temporada.to_dict() != esperado:
    raise ValueError(
        "Quantidade de partidas inesperada por temporada:\n"
        f"{partidas_por_temporada}"
    )

# Validar campos essenciais
campos_obrigatorios = [
    "temporada",
    "data",
    "mandante",
    "visitante",
    "gols_mandante",
    "gols_visitante",
]

if consolidado[campos_obrigatorios].isna().any().any():
    raise ValueError(
        "Existem campos obrigatórios vazios na base consolidada."
    )

# Verificar partidas duplicadas
chave = [
    "temporada",
    "data",
    "mandante",
    "visitante",
]

duplicadas = consolidado.duplicated(subset=chave)

if duplicadas.any():
    raise ValueError(
        f"Foram encontradas {duplicadas.sum()} partidas duplicadas."
    )

# Salvar somente após passar pelas validações
saida = PASTA / "partidas_serie_b_2022_2025.csv"

consolidado.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig",
    date_format="%Y-%m-%d",
)

print("Consolidação concluída com sucesso!")
print(f"Arquivo: {saida}")
print(f"Total de partidas: {len(consolidado)}")

print("\nPartidas por temporada:")
print(partidas_por_temporada.to_string())

print("\nEquipes por temporada:")
for temporada, grupo in consolidado.groupby("temporada"):
    equipes = set(grupo["mandante"]) | set(grupo["visitante"])
    print(f"{temporada}: {len(equipes)} equipes")

print("\nPrimeiras linhas:")
print(consolidado.head().to_string(index=False))
