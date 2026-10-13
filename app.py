from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Série B | O caminho do acesso", page_icon="⚽", layout="wide")

BG = "#0B1220"
GREEN = "#41E0B5"
BLUE = "#63A7FF"
WHITE = "#F4F7FB"
MUTED = "#9CAFC7"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@500;600;700&display=swap');
.stApp {{ background: radial-gradient(circle at 85% 0%, rgba(65,224,181,.09), transparent 28%), {BG}; color:{WHITE}; }}
[data-testid="stSidebar"] {{ background:#0E1828; }}
h1,h2,h3 {{ font-family:'Space Grotesk',sans-serif!important; letter-spacing:-.03em; }}
.hero {{ padding:1.6rem; border:1px solid #29364a; border-radius:22px; background:linear-gradient(115deg,rgba(65,224,181,.12),rgba(99,167,255,.08) 55%,#131e30); margin-bottom:1rem; }}
.eyebrow {{ color:{GREEN}; text-transform:uppercase; letter-spacing:.15em; font-size:.75rem; font-weight:700; }}
.hero-title {{ font-family:'Space Grotesk',sans-serif; font-size:clamp(2rem,4vw,3.2rem); line-height:1.05; font-weight:700; margin:.5rem 0; }}
.muted {{ color:{MUTED}; line-height:1.6; }}
.metric {{ background:#131E30; border:1px solid #29364a; border-radius:16px; padding:1rem; min-height:120px; }}
.metric-label {{ color:{MUTED}; font-size:.8rem; }}
.metric-value {{ font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700; margin:.25rem 0; }}
.metric-note {{ color:{GREEN}; font-size:.8rem; }}
.insight {{ background:rgba(65,224,181,.075); border-left:3px solid {GREEN}; border-radius:0 12px 12px 0; padding:1rem; line-height:1.6; }}
</style>
""", unsafe_allow_html=True)

BASE = Path(__file__).resolve().parent
FILE = BASE / "data" / "processed" / "desempenho_equipes_2022_2025.csv"

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df["temporada"] = pd.to_numeric(df["temporada"], errors="raise").astype(int)
    df["promovido"] = df["promovido"].astype(str).str.lower().map({"true": True, "false": False, "1": True, "0": False})
    numeric = ["partidas","vitorias","empates","derrotas","gols_marcados","gols_sofridos","pontos","saldo_gols","aproveitamento_pct"]
    for c in numeric:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

if not FILE.exists():
    st.error("Arquivo não encontrado: data/processed/desempenho_equipes_2022_2025.csv. Salve app.py na raiz do projeto.")
    st.stop()

try:
    data = load_data(str(FILE)).dropna(subset=["temporada","clube","promovido"])
except Exception as e:
    st.error(f"Erro ao carregar a base: {e}")
    st.stop()

st.sidebar.markdown("## ⚽ SÉRIE B")
st.sidebar.caption("O CAMINHO DO ACESSO · 2022–2025")
page = st.sidebar.radio("Navegação", ["Visão geral", "Perfil dos promovidos", "Explorar clubes"])
years = sorted(data["temporada"].unique())
selected = st.sidebar.multiselect("Temporadas", years, default=years)
if not selected:
    st.warning("Selecione pelo menos uma temporada.")
    st.stop()

df = data[data["temporada"].isin(selected)].copy()
up = df[df["promovido"] == True]
other = df[df["promovido"] == False]

def style_fig(fig, height=380):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color=WHITE), margin=dict(l=12,r=12,t=45,b=12),
        legend=dict(orientation="h", y=1.02, x=0),
        hoverlabel=dict(bgcolor="#17243A", font_color=WHITE),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor="rgba(156,175,199,.13)", zeroline=False, tickfont=dict(color=MUTED))
    return fig

def heading(kicker, title, subtitle=""):
    st.markdown(f"<div class='eyebrow'>{kicker}</div>", unsafe_allow_html=True)
    st.subheader(title)
    if subtitle:
        st.markdown(f"<div class='muted'>{subtitle}</div>", unsafe_allow_html=True)

def metric(label, value, note):
    st.markdown(f"<div class='metric'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-note'>{note}</div></div>", unsafe_allow_html=True)

if page == "Visão geral":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">INVESTIGAÇÃO · QUATRO TEMPORADAS</div>
      <div class="hero-title">O que separa quem sobe<br>de quem fica?</div>
      <div class="muted">Uma leitura comparativa da Série B para identificar padrões de desempenho associados ao acesso à elite do futebol brasileiro.</div>
    </div>
    """, unsafe_allow_html=True)

    pts_up, pts_other = up["pontos"].mean(), other["pontos"].mean()
    wins_diff = up["vitorias"].mean() - other["vitorias"].mean()
    goals_diff = up["gols_marcados"].mean() - other["gols_marcados"].mean()
    goals_against_diff = up["gols_sofridos"].mean() - other["gols_sofridos"].mean()
    c = st.columns(4)
    with c[0]: metric("TEMPORADAS", str(len(selected)), "2022–2025")
    with c[1]: metric("CLUBES PROMOVIDOS", str(len(up)), "4 por temporada selecionada")
    with c[2]: metric("VANTAGEM EM PONTOS", f"+{pts_up-pts_other:.1f}", "média por equipe-temporada")
    with c[3]: metric("VANTAGEM EM VITÓRIAS", f"+{wins_diff:.1f}", "média por equipe-temporada")

    left, right = st.columns(2)
    with left:
        heading("01 · A DIFERENÇA", "Pontos médios por grupo")
        m = pd.DataFrame({"Grupo":["Promovidos","Demais clubes"],"Pontos":[pts_up,pts_other]})
        fig = px.bar(m, x="Grupo", y="Pontos", color="Grupo", text=m["Pontos"].map(lambda x:f"{x:.1f}"),
                     color_discrete_map={"Promovidos":GREEN,"Demais clubes":BLUE})
        fig.update_traces(textposition="outside")
        fig.update_yaxes(title=None, range=[0, max(m["Pontos"])*1.2])
        fig.update_xaxes(title=None)
        fig.update_layout(showlegend=False)
        st.plotly_chart(style_fig(fig, 350), use_container_width=True)
    with right:
        heading("02 · O PADRÃO", "Diferença de pontos por temporada", "Valor positivo favorece os promovidos.")
        means = df.groupby(["temporada","promovido"], as_index=False)["pontos"].mean()
        p = means.pivot(index="temporada",columns="promovido",values="pontos")
        if True in p.columns and False in p.columns:
            delta = (p[True]-p[False]).rename("Diferença").reset_index()
            fig = px.bar(delta, x=delta["temporada"].astype(str), y="Diferença",
                         text=delta["Diferença"].map(lambda x:f"+{x:.1f}"), color_discrete_sequence=[GREEN])
            fig.update_traces(textposition="outside")
            fig.update_xaxes(title="Temporada")
            fig.update_yaxes(title="Pontos")
            st.plotly_chart(style_fig(fig,350), use_container_width=True)
        else:
            st.info("Selecione temporadas com ambos os grupos.")

    st.markdown(f"""<div class="insight"><b>Leitura principal:</b> os promovidos tiveram média de <b>{pts_up:.1f} pontos</b>, contra <b>{pts_other:.1f}</b> dos demais clubes — diferença de <b>{pts_up-pts_other:.1f} pontos</b>. O resultado descreve uma associação, não prova causalidade.</div>""", unsafe_allow_html=True)

    heading("03 · EVOLUÇÃO", "A diferença se mantém ao longo do tempo?", "Cada linha representa a média de pontos de um grupo.")
    means["Grupo"] = means["promovido"].map({True:"Promovidos",False:"Demais clubes"})
    fig = px.line(means, x=means["temporada"].astype(str), y="pontos", color="Grupo", markers=True,
                  text=means["pontos"].map(lambda x:f"{x:.1f}"),
                  color_discrete_map={"Promovidos":GREEN,"Demais clubes":BLUE})
    fig.update_traces(line_width=3, textposition="top center")
    fig.update_xaxes(title="Temporada")
    fig.update_yaxes(title="Pontos médios")
    st.plotly_chart(style_fig(fig,370), use_container_width=True)

elif page == "Perfil dos promovidos":
    st.markdown("""
    <div class="hero"><div class="eyebrow">ANATOMIA DO DESEMPENHO</div>
    <div class="hero-title">Atacar mais.<br>Conceder menos.</div>
    <div class="muted">O acesso aparece como um conjunto de resultados: conquistar pontos, transformar jogos em vitórias e equilibrar ataque e defesa.</div></div>
    """, unsafe_allow_html=True)
    d = df.copy()
    d["Grupo"] = d["promovido"].map({True:"Promovidos",False:"Demais clubes"})
    d["Gols marcados por jogo"] = d["gols_marcados"] / d["partidas"]
    d["Gols sofridos por jogo"] = d["gols_sofridos"] / d["partidas"]
    a,b = st.columns(2)
    with a:
        heading("ATAQUE", "Gols marcados por partida")
        fig = px.box(d, x="Grupo", y="Gols marcados por jogo", color="Grupo", points="all",
                     hover_data=["temporada","clube"], color_discrete_map={"Promovidos":GREEN,"Demais clubes":BLUE})
        fig.update_xaxes(title=None)
        st.plotly_chart(style_fig(fig), use_container_width=True)
    with b:
        heading("DEFESA", "Gols sofridos por partida", "Valores menores significam menos gols concedidos.")
        fig = px.box(d, x="Grupo", y="Gols sofridos por jogo", color="Grupo", points="all",
                     hover_data=["temporada","clube"], color_discrete_map={"Promovidos":GREEN,"Demais clubes":BLUE})
        fig.update_xaxes(title=None)
        st.plotly_chart(style_fig(fig), use_container_width=True)

    heading("EQUILÍBRIO", "Ataque, defesa e pontos", "Cada bolha representa um clube em uma temporada.")
    fig = px.scatter(d, x="gols_marcados", y="gols_sofridos", color="Grupo", size="pontos",
                     hover_name="clube", hover_data=["temporada","pontos","saldo_gols","aproveitamento_pct"],
                     color_discrete_map={"Promovidos":GREEN,"Demais clubes":BLUE},
                     labels={"gols_marcados":"Gols marcados","gols_sofridos":"Gols sofridos"})
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(style_fig(fig,460), use_container_width=True)
    st.markdown("<div class='insight'><b>Como interpretar:</b> procure os promovidos mais à direita (mais gols marcados) e mais acima (menos gols sofridos, pois o eixo vertical está invertido). O tamanho da bolha representa os pontos.</div>", unsafe_allow_html=True)

    heading("RESUMO", "Comparação entre grupos")
    summary = d.groupby("Grupo").agg(
        Pontos=("pontos","mean"), Vitórias=("vitorias","mean"), Empates=("empates","mean"),
        Derrotas=("derrotas","mean"), **{"Gols marcados":("gols_marcados","mean"),
        "Gols sofridos":("gols_sofridos","mean"),"Saldo de gols":("saldo_gols","mean"),
        "Aproveitamento (%)":("aproveitamento_pct","mean")}
    ).round(2)
    st.dataframe(summary, use_container_width=True)

else:
    st.markdown("""
    <div class="hero"><div class="eyebrow">EXPLORE OS DADOS</div>
    <div class="hero-title">Cada clube conta<br>uma parte da história.</div>
    <div class="muted">Filtre uma temporada, examine os números e compare equipes dentro do contexto de cada campeonato.</div></div>
    """, unsafe_allow_html=True)
    left,right = st.columns(2)
    with left:
        year = st.selectbox("Temporada", years, index=len(years)-1)
    with right:
        group = st.selectbox("Grupo", ["Todas","Promovidos","Demais clubes"])
    t = data[data["temporada"] == year].copy()
    if group == "Promovidos":
        t = t[t["promovido"] == True]
    elif group == "Demais clubes":
        t = t[t["promovido"] == False]
    t = t.sort_values(["pontos","saldo_gols","gols_marcados"],ascending=[False,False,False]).reset_index(drop=True)
    t.insert(0,"Posição por pontos",range(1,len(t)+1))
    t["Grupo"] = t["promovido"].map({True:"Promovido",False:"Não promovido"})
    cols = ["Posição por pontos","clube","Grupo","partidas","vitorias","empates","derrotas",
            "gols_marcados","gols_sofridos","saldo_gols","pontos","aproveitamento_pct"]
    st.dataframe(t[cols].rename(columns={
        "clube":"Clube","partidas":"Jogos","vitorias":"Vitórias","empates":"Empates",
        "derrotas":"Derrotas","gols_marcados":"Gols marcados","gols_sofridos":"Gols sofridos",
        "saldo_gols":"Saldo","pontos":"Pontos","aproveitamento_pct":"Aproveitamento (%)"
    }), use_container_width=True, hide_index=True)
    st.download_button("⬇️ Baixar tabela filtrada (CSV)", t[cols].to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"serie_b_{year}_{group.lower().replace(' ','_')}.csv", mime="text/csv")
    heading("MAPA DE DESEMPENHO", "Pontos e saldo de gols")
    all_year = data[data["temporada"] == year].copy()
    all_year["Grupo"] = all_year["promovido"].map({True:"Promovidos",False:"Demais clubes"})
    fig = px.scatter(all_year, x="saldo_gols", y="pontos", color="Grupo", size="vitorias",
                     hover_name="clube", hover_data=["gols_marcados","gols_sofridos"],
                     color_discrete_map={"Promovidos":GREEN,"Demais clubes":BLUE},
                     labels={"saldo_gols":"Saldo de gols","pontos":"Pontos","vitorias":"Vitórias"})
    st.plotly_chart(style_fig(fig,440), use_container_width=True)
    st.caption("A ordenação por pontos, saldo e gols marcados é exploratória e não substitui a classificação oficial, que pode considerar outros critérios de desempate.")

st.markdown("---")
st.markdown("<div class='muted'><b>Nota metodológica:</b> unidade de análise: equipe por temporada. Em cada ano, os quatro clubes promovidos são comparados aos outros 16 participantes. Os indicadores descrevem diferenças observadas, não demonstram causalidade. Confira a exatidão dos placares e a lista de promovidos antes da entrega final.</div>", unsafe_allow_html=True)
