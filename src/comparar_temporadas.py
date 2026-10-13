
from pathlib import Path
import pandas as pd

arquivo = Path(
    "data/processed/desempenho_equipes_2022_2025.csv"
)

df = pd.read_csv(arquivo)

indicadores = [
    "pontos",
    "vitorias",
    "gols_marcados",
    "gols_sofridos",
    "saldo_gols",
    "aproveitamento_pct",
]

resultados = []

for temporada, grupo in df.groupby("temporada"):
    promovidos = grupo[grupo["promovido"] == True]
    demais = grupo[grupo["promovido"] == False]

    if len(promovidos) != 4 or len(demais) != 16:
        raise ValueError(
            f"Quantidade inesperada de equipes em {temporada}: "
            f"{len(promovidos)} promovidos e {len(demais)} demais."
        )

    linha = {
        "temporada": temporada,
        "qtd_promovidos": len(promovidos),
        "qtd_demais": len(demais),
    }

    for indicador in indicadores:
        media_promovidos = promovidos[indicador].mean()
        media_demais = demais[indicador].mean()

        linha[f"{indicador}_promovidos"] = media_promovidos
        linha[f"{indicador}_demais"] = media_demais
        linha[f"dif_{indicador}"] = (
            media_promovidos - media_demais
        )

    resultados.append(linha)

comparacao = pd.DataFrame(resultados)

# Salvar resultados detalhados
saida = Path(
    "data/processed/comparacao_por_temporada.csv"
)
comparacao.to_csv(
    saida, index=False, encoding="utf-8-sig"
)

# Exibir as diferenças principais
colunas = [
    "temporada",
    "pontos_promovidos",
    "pontos_demais",
    "dif_pontos",
    "vitorias_promovidos",
    "vitorias_demais",
    "dif_vitorias",
    "gols_marcados_promovidos",
    "gols_marcados_demais",
    "dif_gols_marcados",
    "gols_sofridos_promovidos",
    "gols_sofridos_demais",
    "dif_gols_sofridos",
    "saldo_gols_promovidos",
    "saldo_gols_demais",
    "dif_saldo_gols",
]

print("\nCOMPARAÇÃO POR TEMPORADA")
print(
    comparacao[colunas].round(2).to_string(index=False)
)

print(f"\nArquivo salvo: {saida}")
