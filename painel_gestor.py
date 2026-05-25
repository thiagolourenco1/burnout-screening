import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64, os

st.set_page_config(page_title="Mind In Fit | Painel", page_icon="📊", layout="wide")

def get_logo_b64():
    p = os.path.join(os.path.dirname(__file__), "logo_mindinfit.jpeg")
    if os.path.exists(p):
        with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_b64()
logo_tag = f'<img src="data:image/jpeg;base64,{logo_b64}" style="height:36px;object-fit:contain;" alt="MIF">' if logo_b64 else '<span style="color:#E8470A;font-weight:900;font-size:1.2rem;font-family:Barlow Condensed,sans-serif">MIND IN FIT</span>'

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700;900&family=Barlow:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Barlow', sans-serif; background: #000 !important; color: #fff; }
[data-testid="stAppViewContainer"],[data-testid="stHeader"],[data-testid="block-container"],.stApp,.main { background: #000 !important; }
p, label, span { color: #fff !important; }

/* ── LOGIN ── */
.login-outer { display:flex; align-items:center; justify-content:center; min-height:80vh; }
.login-card {
    width: 380px;
    background: #0a0a0a;
    border: 1px solid #1a1a1a;
    border-radius: 16px;
    padding: 48px 40px;
    text-align: center;
}
.login-card h2 { font-family:'Barlow Condensed',sans-serif; font-size:1.7rem; font-weight:900; color:#fff; margin:20px 0 6px; }
.login-card p  { font-size:.83rem; color:#555 !important; margin-bottom:28px; }
.login-divider { height:1px; background:#1a1a1a; margin:20px 0; }

/* ── SIDEBAR ── */
div[data-testid="stSidebar"] {
    background: #080808 !important;
    border-right: 1px solid #141414 !important;
}
div[data-testid="stSidebar"] * { color: #fff !important; }

/* ── KPI CARD ── */
.kpi {
    background: #0a0a0a;
    border: 1px solid #1a1a1a;
    border-radius: 12px;
    padding: 22px 20px;
    text-align: center;
    transition: border-color .2s;
}
.kpi:hover { border-color: #E8470A; }
.kpi-val { font-family:'Barlow Condensed',sans-serif; font-size:2.4rem; font-weight:900; line-height:1; margin:8px 0 4px; }
.kpi-lbl { font-size:.65rem; font-weight:700; letter-spacing:.18em; text-transform:uppercase; color:#444 !important; }
.kpi-sub { font-size:.75rem; color:#555 !important; margin-top:4px; }
.c-green  { color:#22C55E; } .c-yellow { color:#EAB308; }
.c-orange { color:#E8470A; } .c-red    { color:#EF4444; }
.c-white  { color:#fff; }

/* ── ROW CARD ── */
.row-card {
    background: #0a0a0a;
    border: 1px solid #141414;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 5px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: border-color .15s, background .15s;
}
.row-card:hover { background: #111; border-color: #222; }
.row-name { font-weight:500; font-size:.92rem; color:#fff !important; }
.row-meta { font-size:.78rem; color:#444 !important; margin-top:2px; }
.row-score { font-family:'Barlow Condensed',sans-serif; font-size:1.3rem; font-weight:700; }

/* ── BADGE ── */
.badge {
    display:inline-block; padding:2px 10px;
    border-radius:4px; font-size:.68rem;
    font-weight:700; letter-spacing:.08em;
    text-transform:uppercase;
}
.b-green  { background:#001a0a; color:#22C55E; border:1px solid #22C55E33; }
.b-yellow { background:#1a1400; color:#EAB308; border:1px solid #EAB30833; }
.b-orange { background:#1a0800; color:#E8470A; border:1px solid #E8470A33; }
.b-red    { background:#1a0000; color:#EF4444; border:1px solid #EF444433; }

/* ── PAGE TITLE ── */
.page-hdr {
    display:flex; align-items:baseline; gap:12px;
    padding-bottom:16px; border-bottom:1px solid #111;
    margin-bottom:28px;
}
.page-hdr h1 {
    font-family:'Barlow Condensed',sans-serif;
    font-size:1.8rem; font-weight:900; color:#fff;
    margin:0;
}
.page-hdr span { font-size:.65rem; font-weight:700; letter-spacing:.2em; text-transform:uppercase; color:#E8470A; }

/* ── SECTION LABEL ── */
.sec-lbl {
    font-family:'Barlow Condensed',sans-serif;
    font-size:.6rem; font-weight:700;
    letter-spacing:.25em; text-transform:uppercase;
    color:#E8470A !important; margin-bottom:14px;
}

/* ── DELETE ZONE ── */
.delete-zone {
    background:#0a0a0a;
    border:1px solid #1a1a1a;
    border-radius:12px;
    padding:24px;
    margin-top:8px;
}
.delete-warning {
    background:#1a0000;
    border:1px solid #EF444433;
    border-radius:8px;
    padding:12px 16px;
    font-size:.82rem;
    color:#EF4444 !important;
    margin-bottom:16px;
}

/* ── BOTÕES ── */
.stButton>button {
    background:#E8470A !important; color:#fff !important;
    border:none !important; border-radius:8px !important;
    font-family:'Barlow Condensed',sans-serif !important;
    font-weight:700 !important; letter-spacing:.08em !important;
    text-transform:uppercase !important;
    transition:all .2s !important;
}
.stButton>button:hover { background:#c93c08 !important; }

/* ── INPUTS ── */
.stTextInput>div>div>input, .stSelectbox>div>div {
    background:#0a0a0a !important; border:1px solid #1e1e1e !important;
    border-radius:8px !important; color:#fff !important;
}
.stTextInput>div>div>input:focus { border-color:#E8470A !important; }
.stMultiSelect>div>div { background:#0a0a0a !important; border:1px solid #1e1e1e !important; border-radius:8px !important; }

footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ── AUTENTICAÇÃO ─────────────────────────────────────────────
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown(f"""
    <div class="login-outer">
        <div class="login-card">
            {logo_tag}
            <h2>Painel do Gestor</h2>
            <p>Acesso restrito. Insira a senha para continuar.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    col = st.columns([1,2,1])[1]
    with col:
        senha = st.text_input("", type="password", placeholder="Senha de acesso", label_visibility="collapsed")
        if st.button("ENTRAR"):
            if senha == st.secrets.get("senha_gestor","MindInFit"):
                st.session_state.auth = True; st.rerun()
            else: st.error("Senha incorreta.")
    st.stop()

# ── GOOGLE SHEETS ─────────────────────────────────────────────
@st.cache_resource
def conectar():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Erro: {e}"); return None

@st.cache_data(ttl=60)
def carregar():
    c = conectar()
    if not c: return pd.DataFrame()
    try:
        sp = c.open_by_key(st.secrets["sheet_id"])
        aba = sp.worksheet("respostas")
        df = pd.DataFrame(aba.get_all_records())
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["score_total"] = pd.to_numeric(df["score_total"], errors="coerce")
            df["_row"] = range(2, len(df)+2)  # linha real na planilha (1=header)
        return df
    except Exception as e:
        st.error(f"Erro: {e}"); return pd.DataFrame()

def excluir_linhas(row_nums):
    """Exclui linhas da planilha (do maior para o menor para não deslocar índices)"""
    c = conectar()
    if not c: return False
    try:
        sp = c.open_by_key(st.secrets["sheet_id"])
        aba = sp.worksheet("respostas")
        for r in sorted(row_nums, reverse=True):
            aba.delete_rows(r)
        carregar.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao excluir: {e}"); return False

def cl_texto(c):
    return c.replace("🟢 ","").replace("🟡 ","").replace("🟠 ","").replace("🔴 ","").strip()

def badge(c):
    t = cl_texto(c)
    m = {"Baixo risco":"b-green","Atenção":"b-yellow","Alto risco":"b-orange","Risco elevado":"b-red"}
    e = {"Baixo risco":"🟢","Atenção":"🟡","Alto risco":"🟠","Risco elevado":"🔴"}
    return f'<span class="badge {m.get(t,"b-orange")}">{e.get(t,"")} {t}</span>'

def cor_score(s):
    if s<=10: return "#22C55E"
    if s<=20: return "#EAB308"
    if s<=30: return "#E8470A"
    return "#EF4444"

def classificar(s):
    if s<=10: return "Baixo risco"
    if s<=20: return "Atenção"
    if s<=30: return "Alto risco"
    return "Risco elevado"

PLOT_BASE = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                 font_color="#fff", title_font_size=14, title_font_color="#fff",
                 legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#aaa"))
CORES = {"Baixo risco":"#22C55E","Atenção":"#EAB308","Alto risco":"#E8470A","Risco elevado":"#EF4444"}

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown(logo_tag, unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#141414;margin:16px 0'>", unsafe_allow_html=True)
    pagina = st.radio("", ["📊 Dashboard","👥 Colaboradores","🏢 Por Setor","📄 Relatório Individual","🗑️ Gerenciar Respostas"], label_visibility="collapsed")
    st.markdown("<hr style='border-color:#141414;margin:16px 0'>", unsafe_allow_html=True)
    if st.button("SAIR"): st.session_state.auth = False; st.rerun()
    st.caption(f"Atualizado: {datetime.now().strftime('%H:%M')}")

# ── DADOS ─────────────────────────────────────────────────────
df = carregar()
if df.empty and "Gerenciar" not in pagina:
    st.markdown('<div class="page-hdr"><h1>Dashboard</h1></div>', unsafe_allow_html=True)
    st.info("Nenhuma resposta registrada ainda.")
    st.stop()

if not df.empty:
    df["class_limpa"] = df["classificacao"].apply(cl_texto)

# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
if "Dashboard" in pagina:
    st.markdown('<div class="page-hdr"><span>Mind In Fit</span><h1>Dashboard Geral</h1></div>', unsafe_allow_html=True)

    total   = len(df)
    baixo   = (df["class_limpa"]=="Baixo risco").sum()
    atencao = (df["class_limpa"]=="Atenção").sum()
    alto    = (df["class_limpa"]=="Alto risco").sum()
    elevado = (df["class_limpa"]=="Risco elevado").sum()
    media   = df["score_total"].mean()
    risco   = alto + elevado

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    cards = [
        (c1, total,  "#fff",    "Total",        "respostas"),
        (c2, baixo,  "#22C55E", "Baixo Risco",  f"{baixo/total*100:.0f}%"),
        (c3, atencao,"#EAB308", "Atenção",       f"{atencao/total*100:.0f}%"),
        (c4, alto,   "#E8470A", "Alto Risco",    f"{alto/total*100:.0f}%"),
        (c5, elevado,"#EF4444", "Risco Elevado", f"{elevado/total*100:.0f}%"),
        (c6, f"{media:.1f}", "#aaa", "Score Médio", "/40"),
    ]
    for col, val, cor, lbl, sub in cards:
        col.markdown(f'<div class="kpi"><div class="kpi-lbl">{lbl}</div><div class="kpi-val" style="color:{cor}">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        cnt = df["class_limpa"].value_counts().reset_index()
        cnt.columns = ["Classificação","n"]
        fig = px.pie(cnt, names="Classificação", values="n", color="Classificação",
                     color_discrete_map=CORES, hole=.55, title="Distribuição de Risco")
        fig.update_layout(**PLOT_BASE)
        fig.update_traces(textfont_color="#fff")
        st.plotly_chart(fig, use_container_width=True)
    with cb:
        md = {"Fadiga Física":df["fadiga_fisica"].mean(),
              "Exaustão Emocional":df["exaustao_emocional"].mean(),
              "Recup. e Saúde":df["recuperacao_saude"].mean()}
        fig2 = go.Figure(go.Bar(
            x=list(md.keys()), y=list(md.values()),
            marker_color=["#E8470A","#EF4444","#EAB308"],
            text=[f"{v:.1f}" for v in md.values()], textposition="outside",
            textfont_color="#fff"
        ))
        fig2.update_layout(title="Média por Domínio", **PLOT_BASE,
                           yaxis=dict(gridcolor="#111",color="#555"),
                           xaxis=dict(color="#555"))
        st.plotly_chart(fig2, use_container_width=True)

    df_t = df.copy(); df_t["data"] = df_t["timestamp"].dt.date
    med = df_t.groupby("data")["score_total"].mean().reset_index()
    fig3 = px.area(med, x="data", y="score_total", title="Evolução do Score Médio")
    fig3.update_traces(line_color="#E8470A", fillcolor="rgba(232,71,10,.08)")
    fig3.update_layout(**PLOT_BASE, yaxis=dict(gridcolor="#111",range=[0,40],color="#555"), xaxis=dict(gridcolor="#111",color="#555"))
    st.plotly_chart(fig3, use_container_width=True)

    st.download_button("⬇️ EXPORTAR CSV", df.drop(columns=["_row"],errors="ignore").to_csv(index=False).encode("utf-8"),
                       f"mindinfit_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")

# ══════════════════════════════════════════════════════════════
# COLABORADORES
# ══════════════════════════════════════════════════════════════
elif "Colaboradores" in pagina:
    st.markdown('<div class="page-hdr"><span>Mind In Fit</span><h1>Colaboradores</h1></div>', unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1: fs = st.selectbox("Setor",["Todos"]+sorted(df["setor"].dropna().unique().tolist()))
    with c2: fr = st.selectbox("Risco",["Todos","Baixo risco","Atenção","Alto risco","Risco elevado"])
    with c3: fb = st.text_input("Buscar nome","",placeholder="Nome...")

    d = df.copy()
    if fs!="Todos": d=d[d["setor"]==fs]
    if fr!="Todos": d=d[d["class_limpa"]==fr]
    if fb: d=d[d["nome"].str.contains(fb,case=False,na=False)]

    st.markdown(f'<p style="font-size:.8rem;color:#555;margin-bottom:16px">{len(d)} colaboradores encontrados</p>', unsafe_allow_html=True)

    for _,row in d.sort_values("score_total",ascending=False).iterrows():
        cor = cor_score(int(row["score_total"]))
        st.markdown(f"""
        <div class="row-card">
            <div>
                <div class="row-name">{row['nome']}</div>
                <div class="row-meta">{row['cargo']} · {row['setor']} · {row['idade']} anos · {row['timestamp'].strftime('%d/%m/%Y')}</div>
            </div>
            <div style="text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:6px">
                <div class="row-score" style="color:{cor}">{int(row['score_total'])}<span style="font-size:.8rem;color:#444">/40</span></div>
                {badge(row['classificacao'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("⬇️ EXPORTAR LISTA", d.drop(columns=["_row"],errors="ignore").to_csv(index=False).encode("utf-8"), "colaboradores.csv","text/csv")

# ══════════════════════════════════════════════════════════════
# POR SETOR
# ══════════════════════════════════════════════════════════════
elif "Setor" in pagina:
    st.markdown('<div class="page-hdr"><span>Mind In Fit</span><h1>Análise por Setor</h1></div>', unsafe_allow_html=True)

    res = df.groupby("setor").agg(
        n=("nome","count"),
        score=("score_total","mean"),
        fadiga=("fadiga_fisica","mean"),
        emocional=("exaustao_emocional","mean"),
        recuperacao=("recuperacao_saude","mean"),
    ).reset_index().sort_values("score",ascending=False)
    res["risco"] = res["score"].apply(classificar)

    fig = px.bar(res, x="setor", y="score", color="risco", color_discrete_map=CORES,
                 text=res["score"].apply(lambda x:f"{x:.1f}"), title="Score Médio por Setor")
    fig.update_layout(**PLOT_BASE, yaxis=dict(gridcolor="#111",range=[0,42],color="#555"), xaxis=dict(color="#555"))
    fig.update_traces(textfont_color="#fff")
    st.plotly_chart(fig, use_container_width=True)

    for _,row in res.iterrows():
        cor = cor_score(row["score"])
        with st.expander(f"🏢 {row['setor']}  ·  {row['n']} pessoas  ·  Score: {row['score']:.1f}/40"):
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Score Médio",f"{row['score']:.1f}/40")
            c2.metric("Fadiga Física",f"{row['fadiga']:.1f}/16")
            c3.metric("Exaustão Emocional",f"{row['emocional']:.1f}/12")
            c4.metric("Recuperação/Saúde",f"{row['recuperacao']:.1f}/12")
            ds = df[df["setor"]==row["setor"]][["nome","cargo","score_total","classificacao"]]
            ds.columns = ["Nome","Cargo","Score","Classificação"]
            st.dataframe(ds, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# RELATÓRIO INDIVIDUAL
# ══════════════════════════════════════════════════════════════
elif "Individual" in pagina:
    st.markdown('<div class="page-hdr"><span>Mind In Fit</span><h1>Relatório Individual</h1></div>', unsafe_allow_html=True)

    nomes = sorted(df["nome"].dropna().unique().tolist())
    sel = st.selectbox("Colaborador", nomes)
    dp = df[df["nome"]==sel].sort_values("timestamp",ascending=False)

    if dp.empty:
        st.warning("Nenhum dado encontrado.")
    else:
        u = dp.iloc[0]
        score = int(u["score_total"])
        cor = cor_score(score)

        c1,c2 = st.columns([3,1])
        with c1:
            st.markdown(f"### {u['nome']}")
            st.markdown(f"**{u['cargo']}** · {u['setor']} · {u['idade']} anos")
            st.caption(f"Preenchido em {u['timestamp'].strftime('%d/%m/%Y às %H:%M')}")
        with c2:
            st.markdown(f'<div class="kpi"><div class="kpi-lbl">Score</div><div class="kpi-val" style="color:{cor}">{score}/40</div><div class="kpi-sub">{cl_texto(u["classificacao"])}</div></div>', unsafe_allow_html=True)

        st.markdown("---")

        cats = ["Fadiga Física","Exaustão Emocional","Recup. e Saúde"]
        vp = [u["fadiga_fisica"]/16*100, u["exaustao_emocional"]/12*100, u["recuperacao_saude"]/12*100]
        vm = [df["fadiga_fisica"].mean()/16*100, df["exaustao_emocional"].mean()/12*100, df["recuperacao_saude"].mean()/12*100]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=vp+[vp[0]], theta=cats+[cats[0]], fill="toself",
                                      name=sel, line_color="#E8470A", fillcolor="rgba(232,71,10,.1)"))
        fig.add_trace(go.Scatterpolar(r=vm+[vm[0]], theta=cats+[cats[0]], fill="toself",
                                      name="Média Geral", line_color="#444", fillcolor="rgba(100,100,100,.06)"))
        fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
                                     radialaxis=dict(visible=True,range=[0,100],gridcolor="#222",color="#555"),
                                     angularaxis=dict(color="#aaa")),
                          **PLOT_BASE, title="Perfil por Domínio vs. Média Geral")
        st.plotly_chart(fig, use_container_width=True)

        c1,c2,c3 = st.columns(3)
        c1.metric("Fadiga Física",      f"{int(u['fadiga_fisica'])}/16",      delta=f"{u['fadiga_fisica']-df['fadiga_fisica'].mean():.1f} vs média")
        c2.metric("Exaustão Emocional", f"{int(u['exaustao_emocional'])}/12", delta=f"{u['exaustao_emocional']-df['exaustao_emocional'].mean():.1f} vs média")
        c3.metric("Recuperação/Saúde",  f"{int(u['recuperacao_saude'])}/12",  delta=f"{u['recuperacao_saude']-df['recuperacao_saude'].mean():.1f} vs média")

        if len(dp)>1:
            st.markdown("#### Histórico")
            fig2 = px.line(dp.sort_values("timestamp"), x="timestamp", y="score_total", markers=True, line_shape="spline")
            fig2.update_traces(line_color="#E8470A", marker_color="#E8470A")
            fig2.update_layout(**PLOT_BASE, yaxis=dict(gridcolor="#111",range=[0,40],color="#555"), xaxis=dict(color="#555"))
            st.plotly_chart(fig2, use_container_width=True)

        st.download_button(f"⬇️ EXPORTAR — {sel}",
                           dp.drop(columns=["_row"],errors="ignore").to_csv(index=False).encode("utf-8"),
                           f"relatorio_{sel.replace(' ','_')}.csv","text/csv")

# ══════════════════════════════════════════════════════════════
# GERENCIAR RESPOSTAS (EXCLUSÃO)
# ══════════════════════════════════════════════════════════════
elif "Gerenciar" in pagina:
    st.markdown('<div class="page-hdr"><span>Mind In Fit</span><h1>Gerenciar Respostas</h1></div>', unsafe_allow_html=True)

    if df.empty:
        st.info("Nenhuma resposta registrada ainda.")
        st.stop()

    tab1, tab2 = st.tabs(["🗑️ Excluir por Nome", "☑️ Excluir Múltiplas"])

    # ── EXCLUIR POR NOME ──
    with tab1:
        st.markdown('<p class="sec-lbl">Selecione o colaborador</p>', unsafe_allow_html=True)
        nomes = sorted(df["nome"].dropna().unique().tolist())
        sel = st.selectbox("", nomes, label_visibility="collapsed")

        dp = df[df["nome"]==sel].sort_values("timestamp",ascending=False)
        st.markdown(f"**{len(dp)} resposta(s)** encontrada(s) para **{sel}**")

        for _,row in dp.iterrows():
            cor = cor_score(int(row["score_total"]))
            st.markdown(f"""
            <div class="row-card">
                <div>
                    <div class="row-name">{row['nome']}</div>
                    <div class="row-meta">{row['cargo']} · {row['setor']} · {row['timestamp'].strftime('%d/%m/%Y %H:%M')}</div>
                </div>
                <div style="text-align:right">
                    <div class="row-score" style="color:{cor}">{int(row['score_total'])}/40</div>
                    {badge(row['classificacao'])}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="delete-zone">', unsafe_allow_html=True)
        st.markdown(f'<div class="delete-warning">⚠️ Esta ação excluirá <strong>todas as {len(dp)} resposta(s)</strong> de <strong>{sel}</strong> permanentemente.</div>', unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            confirma = st.text_input("Digite o nome para confirmar:", placeholder=sel, key="conf_nome")
        with col_b:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"🗑️ EXCLUIR TODAS AS RESPOSTAS DE {sel.upper()}", key="del_nome"):
                if confirma.strip().lower() == sel.strip().lower():
                    rows = dp["_row"].tolist()
                    if excluir_linhas(rows):
                        st.success(f"✅ {len(rows)} resposta(s) de {sel} excluída(s) com sucesso!")
                        st.rerun()
                else:
                    st.error("Nome não confere. Digite exatamente como aparece.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── EXCLUIR MÚLTIPLAS ──
    with tab2:
        st.markdown('<p class="sec-lbl">Selecione as respostas para excluir</p>', unsafe_allow_html=True)

        df_show = df[["nome","cargo","setor","timestamp","score_total","classificacao","_row"]].copy()
        df_show["data"] = df_show["timestamp"].dt.strftime("%d/%m/%Y %H:%M")
        df_show = df_show.sort_values("score_total", ascending=False)

        opcoes = {
            f"{row['nome']} · {row['data']} · Score {int(row['score_total'])}/40": row["_row"]
            for _, row in df_show.iterrows()
        }

        selecionados = st.multiselect(
            "Escolha as respostas:",
            options=list(opcoes.keys()),
            placeholder="Selecione uma ou mais respostas..."
        )

        if selecionados:
            st.markdown(f'<div class="delete-warning">⚠️ <strong>{len(selecionados)} resposta(s)</strong> selecionada(s) para exclusão permanente.</div>', unsafe_allow_html=True)

            if st.button(f"🗑️ EXCLUIR {len(selecionados)} RESPOSTA(S) SELECIONADA(S)", key="del_multi"):
                rows = [opcoes[s] for s in selecionados]
                if excluir_linhas(rows):
                    st.success(f"✅ {len(rows)} resposta(s) excluída(s) com sucesso!")
                    st.rerun()

# ── FOOTER ───────────────────────────────────────────────────
st.markdown("---")
st.caption("Mind In Fit · Painel do Gestor · Dados confidenciais")
