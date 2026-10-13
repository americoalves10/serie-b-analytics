
import json
import re
import unicodedata
import urllib.request
from pathlib import Path

import pandas as pd


# ============================================================
# 1. CAMINHOS E FONTE DO CALENDÁRIO
# ============================================================

RAIZ = Path(__file__).resolve().parent.parent

ARQUIVO_BASE = (
    RAIZ / "data" / "processed" / "auditoria"
    / "partidas_serie_b_2025_brazilianfootball.csv"
)

ARQUIVO_SAIDA = (
    RAIZ / "data" / "processed" / "auditoria"
    / "jogos_ausentes_para_verificacao.csv"
)

URL_CALENDARIO = (
    "https://raw.githubusercontent.com/openfootball/"
    "football.json/master/2025/br.2.json"
)


# ============================================================
# 2. PADRONIZAR NOMES DE EQUIPES
# ============================================================

def normalizar_equipe(nome):
    nome = str(nome).strip().lower()

    # Remover acentos
    nome = unicodedata.normalize("NFKD", nome)
    nome = "".join(
        caractere
        for caractere in nome
        if not unicodedata.combining(caractere)
    )

    # Remover a UF no final, com ou sem barra
    nome = re.sub(r"/\s*[a-z]{2}\s*$", "", nome)
    nome = re.sub(r"\s+[a-z]{2}\s*$", "", nome)

    # Remover termos que variam entre as fontes
    nome = re.sub(
        r"\b(fc|sc|ec|saf|clube)\b",
        " ",
        nome,
    )

    # Manter apenas letras e números
    nome = re.sub(r"[^a-z0-9]", "", nome)

    # Resolver diferenças conhecidas entre os nomes
    equivalencias = {
        "crbrasil": "crb",
        "operarioferroviario": "operario",
        "gremionovorizontino": "novorizontino",
        "atleticogo": "atleticogoianiense",
        "americamineiro": "america",
    }

    return equivalencias.get(nome, nome)


# ============================================================
# 3. CARREGAR A BASE JÁ COLETADA
# ============================================================

if not ARQUIVO_BASE.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {ARQUIVO_BASE}"
    )

df = pd.read_csv(ARQUIVO_BASE)

colunas_necessarias = {"mandante", "visitante"}

if not colunas_necessarias.issubset(df.columns):
    raise ValueError(
        "A base não possui as colunas mandante e visitante."
    )

# Cada confronto é identificado pela ordem mandante/visitante.
confrontos_base = set(
    zip(
        df["mandante"].map(normalizar_equipe),
        df["visitante"].map(normalizar_equipe),
    )
)


# ============================================================
# 4. BAIXAR O CALENDÁRIO DO OPENFOOTBALL
# ============================================================

print("Baixando o calendário do OpenFootball...")

requisicao = urllib.request.Request(
    URL_CALENDARIO,
    headers={"User-Agent": "Mozilla/5.0"},
)

with urllib.request.urlopen(requisicao, timeout=30) as resposta:
    calendario = json.loads(resposta.read().decode("utf-8"))

partidas_calendario = calendario["matches"]

print(f"Partidas no calendário: {len(partidas_calendario)}")
print(f"Partidas na base coletada: {len(df)}")


# ============================================================
# 5. IDENTIFICAR CONFRONTOS QUE NÃO ESTÃO NA BASE
# ============================================================

ausentes = []

for partida in partidas_calendario:
    mandante_original = partida["team1"]
    visitante_original = partida["team2"]

    confronto = (
        normalizar_equipe(mandante_original),
        normalizar_equipe(visitante_original),
    )

    if confronto not in confrontos_base:
        placar = "SEM PLACAR"

        score = partida.get("score", {})
        gols = score.get("ft") if isinstance(score, dict) else None

        if isinstance(gols, list) and len(gols) >= 2:
            placar = f"{gols[0]} x {gols[1]}"

        ausentes.append({
            "data": partida.get("date"),
            "mandante_calendario": mandante_original,
            "visitante_calendario": visitante_original,
            "placar_openfootball": placar,
        })


# ============================================================
# 6. CONFERIR E SALVAR
# ============================================================

resultado = pd.DataFrame(ausentes)

print("\n========== RESULTADO DA COMPARAÇÃO ==========")
print(f"Confrontos ausentes encontrados: {len(resultado)}")

if not resultado.empty:
    print(resultado.to_string(index=False))

    resultado.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8-sig",
    )

    print(f"\nArquivo salvo em:\n{ARQUIVO_SAIDA}")

else:
    print(
        "\nNenhum confronto ausente foi identificado. "
        "Verifique possíveis diferenças nos nomes das equipes."
    )

print("\nComparação concluída. Nenhum jogo foi adicionado à base.")
