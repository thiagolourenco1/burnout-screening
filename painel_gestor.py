import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64
import os

st.set_page_config(
    page_title="Mind In Fit | Painel do Gestor",
    page_icon="📊",
    layout="wide"
)

# ── Logo ─────────────────────────────────────────────────────
def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "logo_mindinfit.jpeg")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_base64()
logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" class="logo" alt="Mind In Fit">' if logo_b64 else '<span class="logo-text">MIND IN FIT</span>'

# ── CSS ──────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@300;400;500&display=swap');

html, body, [class*="css"] {{ font-family: 'Barlow', sans-serif; background-color: #000000; color: #FFFFFF; }}
.main {{ background-color: #000000; }}
h1, h2, h3 {{ font-family: 'Barlow Condensed', sans-serif; color: #FFFFFF; }}

.logo {{ height: 44px; object-fit: contain; }}
.logo-text {{ font-family: 'Barlow Condensed', sans-serif; font-size: 1.5rem; font-weight: 800; color: #E8470A; }}

.login-wrap {{
    max-width: 400px;
    margin: 100px auto;
    background: #0A0A0A;
    border: 1px solid #1A1A1A;
    border-top: 4px solid #E8470A;
    padding: 48px 40px;
    text-align: center;
}}
.login-wrap h2 {{ font-size: 1.8rem; font-weight: 800; margin-bottom: 6px; color: #FFFFFF; }}
.login-wrap p {{ color: #FFFFFF; font-size: 0.85rem; margin-bottom: 32px; }}

.kpi {{
    background: #0A0A0A;
    border: 1px solid #1A1A1A;
    border-top: 3px solid #E8470A;
    padding: 20px;
    text-align: center;
}}
.kpi .val {{ font-family: 'Barlow Condensed', sans-serif; font-size: 2.2rem; font-weight: 800; margin: 6px 0 2px; }}
.kpi .lbl {{ font-size: 0.7rem; letter-spacing: 0.15em; text-transform: uppercase; color: #FFFFFF; }}
.verde   {{ color: #22C55E; }} .amarelo {{ color: #EAB308; }}
.laranja {{ color: #E8470A; }} .vermelho {{ color: #EF4444; }}

.row-card {{
    background: #0A0A0A;
    border: 1px solid #1A1A1A;
    border-left: 4px solid #E8470A;
    padding: 14px 18px;
    margin: 6px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.88rem;
    color: #FFFFFF;
}}

.badge {{ display: inline-block; padding: 2px 10px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }}
.b-baixo   {{ background: #000000; color: #22C55E; border: 1px solid #22C55E; }}
.b-atencao {{ background: #000000; color: #EAB308; border: 1px solid #EAB308; }}
.b-alto    {{ background: #000000; color: #E8470A; border: 1px solid #E8470A; }}
.b-elevado {{ background: #000000; color: #EF4444; border: 1px solid #EF4444; }}

.stButton>button {{
    background: #E8470A !important; color: #FFFFFF !important;
    border: none !important; border-radius: 2px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 0.9rem !important; font-weight: 700 !important;
    letter-spacing: 0.1em !important; text-transform: uppercase !important;
}}

.stTextInput>div>div>input {{
    background: #0A0A0A !important; border: 1px solid #333333 !important;
    border-radius: 2px !important; color: #FFFFFF !important;
}}
.stTextInput>div>div>input:focus {{ border-color: #E8470A !important; }}
.stTextInput label {{ color: #FFFFFF !important; }}
.stSelectbox label {{ color: #FFFFFF !important; }}
div[data-testid="stSelectbox"] div {{ color: #FFFFFF !important; background: #0A0A0A !important; }}

div[data-testid="stSidebar"] {{ background: #000000 !important; border-right: 1px solid #1A1A1A !important; }}
div[data-testid="stSidebar"] .stRadio label {{ color: #FFFFFF !important; }}
div[data-testid="stSidebar"] p {{ color: #FFFFFF !important; }}
div[data-testid="stSidebar"] span {{ color: #FFFFFF !important; }}
footer {{ visibility: hidden; }}

.page-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2rem; font-weight: 800;
    border-left: 5px solid #E8470A;
    padding-left: 16px;
    margin-bottom: 24px;
    color: #FFFFFF;
}}
</style>
""", unsafe_allow_html=True)


# ── AUTENTICAÇÃO ─────────────────────────────────────────────
def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if not st.session_state.autenticado:
        st.markdown(f"""
        <div class="login-wrap">
            {logo_html}
            <h2 style="margin-top:20px">Painel do Gestor</h2>
            <p>Acesso restrito. Insira a senha para continuar.</p>
        </div>
        """, unsafe_allow_html=True)
        col = st.columns([1, 2, 1])[1]
        with col:
            senha = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="••••••••")
            if st.button("ENTRAR"):
                if senha == st.secrets.get("senha_gestor", "burnout2025"):
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
        st.stop()

verificar_senha()


# ── GOOGLE SHEETS ─────────────────────────────────────────────
@st.cache_resource
def conectar_sheets():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Erro ao conectar: {e}"); return None

@st.cache_data(ttl=120)
def carregar_dados():
    client = conectar_sheets()
    if client is None: return pd.DataFrame()
    try:
        spreadsheet = client.open_by_key(st.secrets["sheet_id"])
        aba = spreadsheet.worksheet("respostas")
        df = pd.DataFrame(aba.get_all_records())
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["score_total"] = pd.to_numeric(df["score_total"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}"); return pd.DataFrame()

def classificar(score):
    if score <= 10: return "Baixo risco"
    if score <= 20: return "Atenção"
    if score <= 30: return "Alto risco"
    return "Risco elevado"

def badge(c):
    t = c.replace("🟢 ","").replace("🟡 ","").replace("🟠 ","").replace("🔴 ","").strip()
    m = {"Baixo risco":"b-baixo","Atenção":"b-atencao","Alto risco":"b-alto","Risco elevado":"b-elevado"}
    e = {"Baixo risco":"🟢","Atenção":"🟡","Alto risco":"🟠","Risco elevado":"🔴"}
    return f'<span class="badge {m.get(t,"b-baixo")}">{e.get(t,"")} {t}</span>'

PLOT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#F0EDE8", title_font_size=15,
            yaxis=dict(gridcolor="#1E1E1E"), xaxis=dict(gridcolor="#1E1E1E"))
CORES = {"Baixo risco":"#22C55E","Atenção":"#EAB308","Alto risco":"#E8470A","Risco elevado":"#EF4444"}

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(logo_html, unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#1E1E1E;margin:16px 0'>", unsafe_allow_html=True)
    pagina = st.radio("", ["📊 Dashboard", "👥 Colaboradores", "🏢 Por Setor", "📄 Relatório Individual"], label_visibility="collapsed")
    st.markdown("<hr style='border-color:#1E1E1E;margin:16px 0'>", unsafe_allow_html=True)
    if st.button("SAIR"):
        st.session_state.autenticado = False; st.rerun()
    st.caption(f"Atualizado: {datetime.now().strftime('%H:%M')}")

# ── DADOS ─────────────────────────────────────────────────────
df = carregar_dados()
if df.empty:
    st.markdown('<div class="page-title">📊 Dashboard</div>', unsafe_allow_html=True)
    st.info("Nenhuma resposta registrada ainda.")
    st.stop()

df["class_limpa"] = df["classificacao"].str.replace(r"[🟢🟡🟠🔴] ", "", regex=True).str.strip()

# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
if "Dashboard" in pagina:
    st.markdown('<div class="page-title">📊 Dashboard Geral</div>', unsafe_allow_html=True)

    total   = len(df)
    baixo   = (df["class_limpa"] == "Baixo risco").sum()
    atencao = (df["class_limpa"] == "Atenção").sum()
    alto    = (df["class_limpa"] == "Alto risco").sum()
    elevado = (df["class_limpa"] == "Risco elevado").sum()

    c1,c2,c3,c4,c5 = st.columns(5)
    c1.markdown(f'<div class="kpi"><div class="lbl">Total</div><div class="val">{total}</div><div class="lbl">respostas</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi"><div class="lbl">Baixo Risco</div><div class="val verde">{baixo}</div><div class="lbl">{baixo/total*100:.0f}%</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi"><div class="lbl">Atenção</div><div class="val amarelo">{atencao}</div><div class="lbl">{atencao/total*100:.0f}%</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="kpi"><div class="lbl">Alto Risco</div><div class="val laranja">{alto}</div><div class="lbl">{alto/total*100:.0f}%</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="kpi"><div class="lbl">Risco Elevado</div><div class="val vermelho">{elevado}</div><div class="lbl">{elevado/total*100:.0f}%</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ca, cb = st.columns(2)

    with ca:
        contagem = df["class_limpa"].value_counts().reset_index()
        contagem.columns = ["Classificação","Quantidade"]
        fig = px.pie(contagem, names="Classificação", values="Quantidade",
                     color="Classificação", color_discrete_map=CORES,
                     title="Distribuição por Nível de Risco", hole=0.5)
        fig.update_layout(**PLOT)
        st.plotly_chart(fig, use_container_width=True)

    with cb:
        medias = {"Fadiga Física": df["fadiga_fisica"].mean(),
                  "Exaustão Emocional": df["exaustao_emocional"].mean(),
                  "Recup. e Saúde": df["recuperacao_saude"].mean()}
        fig2 = go.Figure(go.Bar(x=list(medias.keys()), y=list(medias.values()),
                                marker_color=["#E8470A","#EF4444","#EAB308"],
                                text=[f"{v:.1f}" for v in medias.values()], textposition="outside"))
        fig2.update_layout(title="Média por Domínio", **PLOT)
        st.plotly_chart(fig2, use_container_width=True)

    df_t = df.copy(); df_t["data"] = df_t["timestamp"].dt.date
    med_dia = df_t.groupby("data")["score_total"].mean().reset_index()
    fig3 = px.line(med_dia, x="data", y="score_total", title="Evolução do Score Médio", markers=True, line_shape="spline")
    fig3.update_traces(line_color="#E8470A", marker_color="#E8470A")
    fig3.update_layout(**PLOT, yaxis=dict(gridcolor="#1E1E1E", range=[0,40]))
    st.plotly_chart(fig3, use_container_width=True)

    st.download_button("⬇️ EXPORTAR CSV COMPLETO", df.to_csv(index=False).encode("utf-8"),
                       f"mindinfit_burnout_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")

# ══════════════════════════════════════════════════════════════
# COLABORADORES
# ══════════════════════════════════════════════════════════════
elif "Colaboradores" in pagina:
    st.markdown('<div class="page-title">👥 Colaboradores</div>', unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1: filtro_setor = st.selectbox("Setor", ["Todos"] + sorted(df["setor"].dropna().unique().tolist()))
    with c2: filtro_risco = st.selectbox("Risco", ["Todos","Baixo risco","Atenção","Alto risco","Risco elevado"])
    with c3: busca = st.text_input("Buscar por nome", placeholder="Nome...")

    df2 = df.copy()
    if filtro_setor != "Todos": df2 = df2[df2["setor"] == filtro_setor]
    if filtro_risco != "Todos": df2 = df2[df2["class_limpa"] == filtro_risco]
    if busca: df2 = df2[df2["nome"].str.contains(busca, case=False, na=False)]

    st.markdown(f"**{len(df2)} colaboradores encontrados**")
    st.markdown("---")

    for _, row in df2.sort_values("score_total", ascending=False).iterrows():
        st.markdown(f"""
        <div class="row-card">
            <div><strong>{row['nome']}</strong><br>
            <small style="color:#666">{row['cargo']} · {row['setor']} · {row['idade']} anos</small></div>
            <div style="text-align:right">
                <strong style="font-size:1.1rem;font-family:'Barlow Condensed',sans-serif">{int(row['score_total'])}/40</strong><br>
                {badge(row['classificacao'])}<br>
                <small style="color:#444">{row['timestamp'].strftime('%d/%m/%Y')}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("⬇️ EXPORTAR LISTA", df2.to_csv(index=False).encode("utf-8"),
                       "colaboradores.csv", "text/csv")

# ══════════════════════════════════════════════════════════════
# POR SETOR
# ══════════════════════════════════════════════════════════════
elif "Setor" in pagina:
    st.markdown('<div class="page-title">🏢 Análise por Setor</div>', unsafe_allow_html=True)

    res = df.groupby("setor").agg(
        colaboradores=("nome","count"),
        score_medio=("score_total","mean"),
        fadiga_media=("fadiga_fisica","mean"),
        emocional_media=("exaustao_emocional","mean"),
        recuperacao_media=("recuperacao_saude","mean"),
    ).reset_index().sort_values("score_medio", ascending=False)
    res["risco"] = res["score_medio"].apply(classificar)

    fig = px.bar(res, x="setor", y="score_medio", color="risco", color_discrete_map=CORES,
                 text=res["score_medio"].apply(lambda x: f"{x:.1f}"), title="Score Médio por Setor")
    fig.update_layout(**PLOT, yaxis=dict(gridcolor="#1E1E1E", range=[0,42]))
    st.plotly_chart(fig, use_container_width=True)

    for _, row in res.iterrows():
        with st.expander(f"🏢 {row['setor']}  ·  {row['colaboradores']} pessoas  ·  Score médio: {row['score_medio']:.1f}/40"):
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Score Médio", f"{row['score_medio']:.1f}/40")
            c2.metric("Fadiga Física", f"{row['fadiga_media']:.1f}/16")
            c3.metric("Exaustão Emocional", f"{row['emocional_media']:.1f}/12")
            c4.metric("Recuperação/Saúde", f"{row['recuperacao_media']:.1f}/12")
            df_s = df[df["setor"] == row["setor"]][["nome","cargo","score_total","classificacao"]]
            df_s.columns = ["Nome","Cargo","Score","Classificação"]
            st.dataframe(df_s, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# RELATÓRIO INDIVIDUAL
# ══════════════════════════════════════════════════════════════
elif "Individual" in pagina:
    st.markdown('<div class="page-title">📄 Relatório Individual</div>', unsafe_allow_html=True)

    nomes = sorted(df["nome"].dropna().unique().tolist())
    sel = st.selectbox("Selecione o colaborador", nomes)
    df_p = df[df["nome"] == sel].sort_values("timestamp", ascending=False)

    if df_p.empty:
        st.warning("Nenhum dado encontrado.")
    else:
        u = df_p.iloc[0]
        score = int(u["score_total"])
        cl = u["class_limpa"]
        cor = {"Baixo risco":"#22C55E","Atenção":"#EAB308","Alto risco":"#E8470A","Risco elevado":"#EF4444"}.get(cl,"#E8470A")

        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"### {u['nome']}")
            st.markdown(f"**{u['cargo']}** · {u['setor']} · {u['idade']} anos")
            st.markdown(f"Preenchido em: {u['timestamp'].strftime('%d/%m/%Y às %H:%M')}")
        with c2:
            st.markdown(f"""
            <div class="kpi" style="border-top-color:{cor}">
                <div class="lbl">Score</div>
                <div class="val" style="color:{cor}">{score}/40</div>
                <div class="lbl">{cl}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        cats = ["Fadiga Física","Exaustão Emocional","Recup. e Saúde"]
        vp = [u["fadiga_fisica"]/16*100, u["exaustao_emocional"]/12*100, u["recuperacao_saude"]/12*100]
        vm = [df["fadiga_fisica"].mean()/16*100, df["exaustao_emocional"].mean()/12*100, df["recuperacao_saude"].mean()/12*100]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=vp+[vp[0]], theta=cats+[cats[0]], fill="toself",
                                      name=sel, line_color="#E8470A", fillcolor="rgba(232,71,10,0.12)"))
        fig.add_trace(go.Scatterpolar(r=vm+[vm[0]], theta=cats+[cats[0]], fill="toself",
                                      name="Média Geral", line_color="#666", fillcolor="rgba(100,100,100,0.08)"))
        fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
                                     radialaxis=dict(visible=True, range=[0,100], gridcolor="#222", color="#666"),
                                     angularaxis=dict(color="#F0EDE8")),
                          paper_bgcolor="rgba(0,0,0,0)", font_color="#F0EDE8",
                          title="Perfil por Domínio (% do máximo) vs. Média Geral",
                          legend=dict(bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)

        c1,c2,c3 = st.columns(3)
        c1.metric("Fadiga Física",      f"{int(u['fadiga_fisica'])}/16",      delta=f"{u['fadiga_fisica']-df['fadiga_fisica'].mean():.1f} vs média")
        c2.metric("Exaustão Emocional", f"{int(u['exaustao_emocional'])}/12", delta=f"{u['exaustao_emocional']-df['exaustao_emocional'].mean():.1f} vs média")
        c3.metric("Recuperação/Saúde",  f"{int(u['recuperacao_saude'])}/12",  delta=f"{u['recuperacao_saude']-df['recuperacao_saude'].mean():.1f} vs média")

        if len(df_p) > 1:
            st.markdown("#### Histórico")
            fig2 = px.line(df_p.sort_values("timestamp"), x="timestamp", y="score_total",
                           markers=True, line_shape="spline", title="Evolução do Score")
            fig2.update_traces(line_color="#E8470A", marker_color="#E8470A")
            fig2.update_layout(**PLOT, yaxis=dict(gridcolor="#1E1E1E", range=[0,40]))
            st.plotly_chart(fig2, use_container_width=True)

        st.download_button(f"⬇️ EXPORTAR RELATÓRIO — {sel}",
                           df_p.to_csv(index=False).encode("utf-8"),
                           f"relatorio_{sel.replace(' ','_')}.csv", "text/csv")

# ── RODAPÉ ────────────────────────────────────────────────────
st.markdown("---")
st.caption("Mind In Fit · Painel restrito ao gestor · Dados confidenciais")
