# ⚽ Série B Analytics — O Caminho do Acesso (2022–2025)

## Sobre o projeto

Este projeto analisa os resultados do Campeonato Brasileiro Série B nas temporadas de 2022, 2023, 2024 e 2025, buscando identificar padrões de desempenho associados ao acesso à Série A.

A investigação compara as equipes promovidas com as demais equipes participantes, considerando indicadores esportivos e diferenças entre temporadas.

## 🎯 Objetivo

Investigar quais características de desempenho aparecem com maior frequência entre as equipes promovidas da Série B para a Série A.

A análise é exploratória e descritiva. Os resultados identificam associações e padrões, mas não demonstram, por si só, relações de causa e efeito.

## 📊 Indicadores analisados

- Pontuação total.
- Vitórias, empates e derrotas.
- Gols marcados.
- Gols sofridos.
- Saldo de gols.
- Aproveitamento percentual.
- Comparação entre equipes promovidas e não promovidas.
- Comparação dos resultados entre as temporadas.

## 🗂️ Estrutura do projeto

```text
serie-b-analytics/
├── app.py
├── README.md
├── .gitignore
├── data/
│   ├── raw/
│   │   └── Arquivos originais das temporadas
│   └── processed/
│       └── Bases processadas e resultados das análises
├── src/
│   └── Scripts de coleta, auditoria e análise
└── .venv/
    └── Ambiente virtual local do Python
```

A pasta `.venv` é local e não deve ser enviada ao GitHub.

## 🛠️ Tecnologias utilizadas

- Python
- Pandas
- Streamlit
- Plotly
- CSV e JSON
- Git e GitHub

## 🚀 Como executar o projeto

### 1. Clonar o repositório

```bash
git clone URL_DO_REPOSITORIO
cd serie-b-analytics
```

Substitua `URL_DO_REPOSITORIO` pelo endereço do repositório no GitHub.

### 2. Criar um ambiente virtual

```bash
python -m venv .venv
```

### 3. Ativar o ambiente virtual no Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instalar as dependências

```bash
python -m pip install pandas streamlit plotly
```

### 5. Executar o dashboard

Na raiz do projeto, execute:

```bash
python -m streamlit run app.py
```

Abra o endereço local apresentado no terminal, normalmente:

http://localhost:8501

## 📈 Dashboard

O dashboard permite explorar os resultados por meio de três seções:

1. **Visão geral:** indicadores e comparações entre equipes promovidas e não promovidas.
2. **Perfil dos promovidos:** análise dos gols marcados e sofridos pelas equipes.
3. **Explorar clubes:** consulta aos indicadores por equipe e temporada, com filtros e possibilidade de exportar dados.

## 🔎 Cuidados na interpretação

As comparações consideram as temporadas analisadas e os indicadores disponíveis nas bases processadas.

Os resultados devem ser interpretados como evidências descritivas. Diferenças estatísticas ou numéricas não comprovam, isoladamente, que um indicador causou o acesso de uma equipe.

A qualidade das conclusões depende da integridade e da consistência dos dados utilizados.

## 👨‍💻 Finalidade

Projeto de análise de dados desenvolvido para estudar o desempenho das equipes do Campeonato Brasileiro Série B e comunicar os resultados por meio de um dashboard interativo.