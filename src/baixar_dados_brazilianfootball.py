
import json
import re
from pathlib import Path

import pandas as pd
import requests

# ============================================================
# 1. CONFIGURAÇÃO DAS PASTAS
# ============================================================

RAIZ = Path(__file__).resolve().parent.parent

PASTA_RAW = RAIZ / "data" / "raw"
PASTA_PROCESSED = RAIZ / "data" / "processed"

PASTA_RAW.mkdir(parents=True, exist_ok=True)
PASTA_PROCESSED.mkdir(parents=True, exist_ok=True)

TEMPORADA = 2025

URL = (
    "https://raw.githubusercontent.com/"
    "BrazilianFootball/Data/main/results/processed/"
    f"Serie_B_{TEMPORADA}_games.json"
)

# ============================================================
# 2. BAIXAR OS DADOS
# ============================================================

print(f"Baixando os jogos da Série B de {TEMPORADA}...")

resposta = requests.get(URL, timeout=30)
resposta.raise_for_status()

dados = resposta.json()

# Guardar o JSON original sem modificar a fonte
arquivo_json = PASTA_RAW / f"serie_b_{TEMPORADA}_brazilianfootball.json"

with open(arquivo_json, "w", encoding="utf-8") as arquivo:
    json.dump(dados, arquivo, ensure_ascii=False, indent=2)

# O arquivo pode estar organizado como dicionário ou lista
jogos = list(dados.values()) if isinstance(dados, dict) else dados

print("Registros encontrados:", len(jogos))

# ============================================================
# 3. ORGANIZAR OS DADOS
# ============================================================

partidas = []

for jogo in jogos:
    resultado = str(jogo.get("Result", "")).strip()

    # Interpretar placares como "1 X 0"
    correspondencia = re.fullmatch(
        r"(\d+)\s*X\s*(\d+)",
        resultado,
        flags=re.IGNORECASE
    )

    if not correspondencia:
        gols_mandante = None
        gols_visitante = None
    else:
        gols_mandante = int(correspondencia.group(1))
        gols_visitante = int(correspondencia.group(2))

    partidas.append({
        "temporada": TEMPORADA,
        "data": jogo.get("Date"),
        "mandante": jogo.get("Home"),
        "visitante": jogo.get("Away"),
        "gols_mandante": gols_mandante,
        "gols_visitante": gols_visitante,
    })

df = pd.DataFrame(partidas)

# Converter datas para formato de data
df["data"] = pd.to_datetime(
    df["data"],
    format="%d/%m/%Y",
    errors="coerce"
)

# ============================================================
# 4. VALIDAR A BASE
# ============================================================

placar_valido = (
    df["gols_mandante"].notna()
    & df["gols_visitante"].notna()
)

sem_equipes = df["mandante"].isna() | df["visitante"].isna()
sem_data = df["data"].isna()

print("\n========== VALIDAÇÃO ==========")
print("Total de partidas:", len(df))
print("Partidas com placar:", int(placar_valido.sum()))
print("Partidas sem placar:", int((~placar_valido).sum()))
print("Partidas sem data válida:", int(sem_data.sum()))
print("Partidas sem nome de equipe:", int(sem_equipes.sum()))
print("Linhas duplicadas:", int(df.duplicated().sum()))

# ============================================================
# 5. SALVAR EM UM NOVO CSV
# ============================================================

arquivo_csv = (
    PASTA_PROCESSED
    / f"partidas_serie_b_{TEMPORADA}_brazilianfootball.csv"
)

df.to_csv(
    arquivo_csv,
    index=False,
    encoding="utf-8-sig",
    date_format="%Y-%m-%d"
)

print("\nArquivo salvo em:")
print(arquivo_csv)

print("\nPrimeiras cinco partidas:")
print(df.head().to_string(index=False))
