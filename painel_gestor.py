# http://localhost:8502


import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import base64, os, io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

st.set_page_config(page_title="Mind In Fit | Painel", page_icon="📊", layout="wide")

# ── LOGO ─────────────────────────────────────────────────────
def get_logo_b64():
    p = os.path.join(os.path.dirname(__file__), "logo_mindinfit.jpeg")
    if os.path.exists(p):
        with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_b64()
logo_tag  = f'<img src="data:image/jpeg;base64,{logo_b64}" style="height:38px;object-fit:contain;display:block;" alt="MIF">' if logo_b64 else '<span style="color:#E8470A;font-weight:900;font-size:1.2rem;font-family:\'Barlow Condensed\',sans-serif">MIND IN FIT</span>'

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;500;700;900&family=Barlow:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family:'Barlow',sans-serif; background:#000 !important; color:#fff; }
[data-testid="stAppViewContainer"],[data-testid="stHeader"],[data-testid="block-container"],.stApp,.main { background:#000 !important; }
p, label, span, div { color:#fff !important; }

/* ══ SIDEBAR ══ */
div[data-testid="stSidebar"],
div[data-testid="stSidebar"] > div,
div[data-testid="stSidebar"] > div > div,
div[data-testid="stSidebar"] > div > div > div,
section[data-testid="stSidebar"] {
    background: #E8470A !important;
    border-right: none !important;
    width: 260px !important;
    min-width: 260px !important;
}
div[data-testid="stSidebar"] * { color: #fff !important; }
div[data-testid="stSidebar"] .stRadio { display:none !important; }
div[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0 !important; }

div[data-testid="stSidebar"] .stButton { margin: 0 !important; padding: 0 !important; }
div[data-testid="stSidebar"] .stButton > button {
    opacity: 1 !important;
    position: relative !important;
    margin: 0 !important;
    width: 100% !important;
    height: auto !important;
    padding: 10px 16px !important;
    border: none !important;
    border-left: 3px solid transparent !important;
    border-radius: 0 !important;
    background: transparent !important;
    color: rgba(255,255,255,0.7) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: .78rem !important;
    font-weight: 700 !important;
    letter-spacing: .12em !important;
    text-transform: uppercase !important;
    text-align: left !important;
    transition: all .15s !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0,0,0,0.15) !important;
    color: #fff !important;
    border-left-color: #fff !important;
}
div[data-testid="stSidebar"] .stRadio { display:none !important; }
div[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0 !important; }

/* Todos os botões da sidebar */
div[data-testid="stSidebar"] .stButton > button {
    opacity: 1 !important;
    position: relative !important;
    margin: 0 !important;
    width: 100% !important;
    height: auto !important;
    padding: 10px 16px !important;
    border: none !important;
    border-left: 3px solid rgba(255,255,255,0.3) !important;
    border-radius: 0 !important;
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
    color: #fff !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: .82rem !important;
    font-weight: 700 !important;
    letter-spacing: .12em !important;
    text-transform: uppercase !important;
    text-align: left !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    transition: all .15s !important;
    -webkit-appearance: none !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,.04) !important;
    color: #ccc !important;
    border-left-color: #333 !important;
}

/* ── Nav wrapper ── */
.sb-wrap {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 0;
}

/* ── Logo area ── */
.sb-logo {
    padding: 20px 18px 16px;
    border-bottom: 1px solid #111;
}
.sb-brand {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: .55rem;
    font-weight: 700;
    letter-spacing: .25em;
    text-transform: uppercase;
    color: #333 !important;
    margin-top: 8px;
}

/* ── Nav section label ── */
.sb-section {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: .5rem;
    font-weight: 700;
    letter-spacing: .28em;
    text-transform: uppercase;
    color: #222 !important;
    padding: 12px 18px 6px;
}

/* ── Nav item ── */
.sb-item {
    position: relative;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 18px;
    border-left: 2px solid transparent;
    transition: all .15s;
    cursor: pointer;
    margin: 1px 0;
}
.sb-item:hover { background: rgba(255,255,255,.04); border-left-color: #333; }
.sb-item.active { background: rgba(232,71,10,.08); border-left-color: #E8470A; }

.sb-icon { width:14px; height:14px; flex-shrink:0; color:#444 !important; transition:color .15s; }
.sb-item:hover .sb-icon { color:#aaa !important; }
.sb-item.active .sb-icon { color:#E8470A !important; }

.sb-label {
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: .78rem !important;
    font-weight: 700 !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
    color: #666 !important;
    transition: color .15s;
}
.sb-item:hover .sb-label { color: #ccc !important; }
.sb-item.active .sb-label { color: #fff !important; }

/* ── Divider ── */
.sb-divider { height:1px; background:#111; margin: 6px 0; }

/* ── Sair ── */
.sb-footer { padding: 12px 18px; border-top: 1px solid #111; margin-top: auto; }

/* Sair button — visível */
div[data-testid="stSidebar"] .stButton:last-of-type > button {
    opacity: 1 !important;
    position: relative !important;
    margin-top: 0 !important;
    background: transparent !important;
    color: #E8470A !important;
    border: 1px solid #E8470A33 !important;
    border-radius: 6px !important;
    padding: 7px 14px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: .72rem !important;
    font-weight: 700 !important;
    letter-spacing: .12em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    height: auto !important;
    transition: all .2s !important;
}
div[data-testid="stSidebar"] .stButton:last-of-type > button:hover {
    background: #E8470A11 !important;
    border-color: #E8470A66 !important;
}

/* ══ MAIN AREA ══ */
.page-hdr {
    display:flex; align-items:baseline; gap:10px;
    padding-bottom:14px; border-bottom:1px solid #0e0e0e; margin-bottom:24px;
}
.page-hdr h1 { font-family:'Barlow Condensed',sans-serif; font-size:1.6rem; font-weight:900; color:#fff; margin:0; }
.page-hdr .pg-tag { font-size:.58rem; font-weight:700; letter-spacing:.22em; text-transform:uppercase; color:#E8470A !important; }

/* KPI */
.kpi { background:#080810; border:1px solid #0e0e1a; border-radius:10px; padding:20px 18px; text-align:center; transition:border-color .2s; }
.kpi:hover { border-color:#E8470A44; }
.kpi-val { font-family:'Barlow Condensed',sans-serif; font-size:2.4rem; font-weight:900; line-height:1; margin:8px 0 4px; }
.kpi-lbl { font-size:.72rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:#888 !important; margin-bottom:2px; }
.kpi-sub { font-size:.82rem; color:#555 !important; font-weight:500; margin-top:4px; }
.cg{color:#22C55E;} .cy{color:#EAB308;} .co{color:#E8470A;} .cr{color:#EF4444;} .cw{color:#fff;}

/* Row card */
.row-card { background:#080810; border:1px solid #0e0e1a; border-radius:8px; padding:13px 16px; margin:4px 0; display:flex; align-items:center; justify-content:space-between; transition:border-color .15s, background .15s; }
.row-card:hover { background:#0f0f1a; border-color:#1a1a2e; }
.row-name { font-weight:500; font-size:.88rem; }
.row-meta { font-size:.74rem; color:#333 !important; margin-top:2px; }
.row-score { font-family:'Barlow Condensed',sans-serif; font-size:1.2rem; font-weight:700; }

/* Badge */
.badge { display:inline-block; padding:2px 9px; border-radius:3px; font-size:.65rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }
.bg{background:#001a0a;color:#22C55E;border:1px solid #22C55E22;}
.by{background:#1a1400;color:#EAB308;border:1px solid #EAB30822;}
.bo{background:#1a0800;color:#E8470A;border:1px solid #E8470A22;}
.br{background:#1a0000;color:#EF4444;border:1px solid #EF444422;}

/* Page title */
.sec-lbl { font-family:'Barlow Condensed',sans-serif; font-size:.58rem; font-weight:700; letter-spacing:.25em; text-transform:uppercase; color:#E8470A !important; margin-bottom:12px; }

/* Delete zone */
.del-zone { background:#080810; border:1px solid #0e0e1a; border-radius:10px; padding:22px; margin-top:8px; }
.del-warn { background:#1a0000; border:1px solid #EF444422; border-radius:6px; padding:10px 14px; font-size:.8rem; color:#EF4444 !important; margin-bottom:14px; }

/* Login */
.login-outer { display:flex; align-items:center; justify-content:center; min-height:85vh; }
.login-card { width:360px; background:#080810; border:1px solid #0e0e1a; border-radius:14px; padding:44px 36px; text-align:center; }
.login-card h2 { font-family:'Barlow Condensed',sans-serif; font-size:1.6rem; font-weight:900; color:#fff; margin:18px 0 6px; }
.login-card p { font-size:.8rem; color:#333 !important; margin-bottom:24px; }

/* Login button override */
.login-outer .stButton>button {
    background: #E8470A !important;
    color: #fff !important;
    border: none !important;
    border-radius: 7px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    padding: 10px !important;
    opacity: 1 !important;
    position: relative !important;
    height: auto !important;
}
.login-outer .stButton>button:hover { background: #c93c08 !important; }

/* Main buttons — laranja por padrão */
[data-testid="block-container"] .stButton>button {
    background:#E8470A !important; color:#fff !important; border:none !important; border-radius:7px !important;
    font-family:'Barlow Condensed',sans-serif !important; font-weight:700 !important;
    letter-spacing:.08em !important; text-transform:uppercase !important; transition:all .2s !important;
}
[data-testid="block-container"] .stButton>button:hover { background:#c93c08 !important; }

/* Botão de download — fundo branco */
[data-testid="block-container"] .stDownloadButton>button {
    background:#fff !important; color:#000 !important; border:none !important; border-radius:7px !important;
    font-family:'Barlow Condensed',sans-serif !important; font-weight:700 !important;
    letter-spacing:.08em !important; text-transform:uppercase !important; transition:all .2s !important;
}
[data-testid="block-container"] .stDownloadButton>button:hover { background:#e8e8e8 !important; }

/* Inputs */
.stTextInput>div>div>input { background:#080810 !important; border:1px solid #0e0e1a !important; border-radius:7px !important; color:#fff !important; }
.stTextInput>div>div>input:focus { border-color:#E8470A !important; }
.stMultiSelect>div>div, .stSelectbox>div>div { background:#080810 !important; border:1px solid #0e0e1a !important; border-radius:7px !important; }

footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ── AUTENTICAÇÃO ─────────────────────────────────────────────
if "auth" not in st.session_state: st.session_state.auth = False
if "pagina" not in st.session_state: st.session_state.pagina = "Dashboard"

if not st.session_state.auth:
    st.markdown(f'<div class="login-outer"><div class="login-card">{logo_tag}<h2>Painel do Gestor</h2><p>Acesso restrito. Insira a senha para continuar.</p></div></div>', unsafe_allow_html=True)
    col = st.columns([1,2,1])[1]
    with col:
        senha = st.text_input("", type="password", placeholder="Senha de acesso", label_visibility="collapsed")
        if st.button("ENTRAR"):
            if senha == st.secrets.get("senha_gestor","MindInFit"):
                st.session_state.auth = True; st.rerun()
            else: st.error("Senha incorreta.")
    st.stop()

# ── SHEETS ───────────────────────────────────────────────────
@st.cache_resource
def conectar():
    try:
        scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
        creds=Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]),scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e: st.error(f"Erro: {e}"); return None

@st.cache_data(ttl=60)
def carregar_motivacao():
    c=conectar()
    if not c: return pd.DataFrame()
    try:
        sp=c.open_by_key(st.secrets["sheet_id"])
        try: aba=sp.worksheet("motivacao")
        except: return pd.DataFrame()
        df=pd.DataFrame(aba.get_all_records())
        if not df.empty:
            df["timestamp"]=pd.to_datetime(df["timestamp"])
            for col in ["media_psicologico","media_interpessoal","media_saude","media_estetico","media_condicao",
                        "sdt_desmotivado","sdt_reg_externa","sdt_reg_introjetada",
                        "sdt_reg_identificacao","sdt_reg_integrada","sdt_motivacao_intrinseca"]:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(",", ".").str.strip()
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            df["_row"]=range(2,len(df)+2)
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=60)
def carregar():
    c=conectar()
    if not c: return pd.DataFrame()
    try:
        sp=c.open_by_key(st.secrets["sheet_id"])
        aba=sp.worksheet("respostas")
        df=pd.DataFrame(aba.get_all_records())
        if not df.empty:
            df["timestamp"]=pd.to_datetime(df["timestamp"])
            df["score_total"]=pd.to_numeric(df["score_total"],errors="coerce")
            df["_row"]=range(2,len(df)+2)
        return df
    except Exception as e: st.error(f"Erro: {e}"); return pd.DataFrame()

def excluir_linhas(rows):
    c=conectar()
    if not c: return False
    try:
        sp=c.open_by_key(st.secrets["sheet_id"])
        aba=sp.worksheet("respostas")
        for r in sorted(rows,reverse=True): aba.delete_rows(r)
        carregar.clear(); return True
    except Exception as e: st.error(f"Erro: {e}"); return False

def cl_txt(c): return c.replace("🟢 ","").replace("🟡 ","").replace("🟠 ","").replace("🔴 ","").strip()
def cor_s(s):
    if s<=10: return "#22C55E"
    if s<=20: return "#EAB308"
    if s<=30: return "#E8470A"
    return "#EF4444"
def classificar(s):
    if s<=10: return "Baixo risco"
    if s<=20: return "Atenção"
    if s<=30: return "Alto risco"
    return "Risco elevado"
def badge(c):
    t=cl_txt(c)
    m={"Baixo risco":"bg","Atenção":"by","Alto risco":"bo","Risco elevado":"br"}
    e={"Baixo risco":"🟢","Atenção":"🟡","Alto risco":"🟠","Risco elevado":"🔴"}
    return f'<span class="badge {m.get(t,"bo")}">{e.get(t,"")} {t}</span>'

PB = dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
          font_color="#fff",title_font_size=13,title_font_color="#aaa",
          legend=dict(bgcolor="rgba(0,0,0,0)",font_color="#666"))
CORES={"Baixo risco":"#22C55E","Atenção":"#EAB308","Alto risco":"#E8470A","Risco elevado":"#EF4444"}

# ── PDF GENERATOR ────────────────────────────────────────────
def gerar_pdf(u, df, logo_path=None):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=18*mm, bottomMargin=18*mm)
    W, H = A4
    ORANGE = colors.HexColor("#E8470A")
    BLACK  = colors.HexColor("#000000")
    DARK   = colors.HexColor("#0a0a0a")
    GRAY   = colors.HexColor("#888888")
    LGRAY  = colors.HexColor("#cccccc")
    WHITE  = colors.white

    def sty(name, **kw): return ParagraphStyle(name, **kw)

    s_eyebrow = sty("eyebrow", fontName="Helvetica-Bold", fontSize=7,
                    textColor=ORANGE, spaceAfter=4, leading=10,
                    letterSpacing=2)
    s_title   = sty("title",   fontName="Helvetica-Bold", fontSize=28,
                    textColor=WHITE, spaceAfter=4, leading=32)
    s_sub     = sty("sub",     fontName="Helvetica",      fontSize=10,
                    textColor=LGRAY, spaceAfter=12, leading=15)
    s_sec     = sty("sec",     fontName="Helvetica-Bold", fontSize=7,
                    textColor=ORANGE, spaceAfter=6, leading=10, letterSpacing=2)
    s_body    = sty("body",    fontName="Helvetica",      fontSize=9,
                    textColor=LGRAY, spaceAfter=6, leading=14)
    s_bold    = sty("bold",    fontName="Helvetica-Bold", fontSize=9,
                    textColor=WHITE, spaceAfter=4, leading=14)
    s_score   = sty("score",   fontName="Helvetica-Bold", fontSize=42,
                    textColor=colors.HexColor(cor_s(int(u["score_total"]))),
                    spaceAfter=2, leading=46, alignment=TA_CENTER)
    s_class_c = sty("classc",  fontName="Helvetica-Bold", fontSize=11,
                    textColor=colors.HexColor(cor_s(int(u["score_total"]))),
                    spaceAfter=6, leading=14, alignment=TA_CENTER)
    s_footer  = sty("footer",  fontName="Helvetica",      fontSize=7,
                    textColor=colors.HexColor("#333333"),
                    alignment=TA_CENTER, leading=10)
    s_right   = sty("right",   fontName="Helvetica",      fontSize=8,
                    textColor=GRAY, alignment=TA_RIGHT, leading=12)

    story = []

    # ── CABEÇALHO ──
    header_data = [[
        Paragraph("MIND IN FIT", sty("mif", fontName="Helvetica-Bold", fontSize=16,
                                     textColor=ORANGE, leading=18)),
        Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", s_right)
    ]]
    ht = Table(header_data, colWidths=[90*mm, 80*mm])
    ht.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING",(0,0),(-1,-1),10),
    ]))
    story.append(ht)
    story.append(HRFlowable(width="100%", thickness=1, color=ORANGE, spaceAfter=14))

    # ── TÍTULO ──
    story.append(Paragraph("RELATÓRIO INDIVIDUAL", s_eyebrow))
    story.append(Paragraph(u["nome"], s_title))
    story.append(Paragraph(f"{u['cargo']}  ·  {u['setor']}  ·  {u['idade']} anos", s_sub))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#111111"), spaceAfter=16))

    # ── SCORE PRINCIPAL ──
    score_val = int(u["score_total"])
    cl = cl_txt(u["classificacao"])
    cor = cor_s(score_val)

    score_data = [[
        Paragraph(f"{score_val}/40", s_score),
        Paragraph(cl.upper(), s_class_c),
        Paragraph(
            {"Baixo risco":"Baixos sinais de exaustão ocupacional.",
             "Atenção":"Sinais moderados de fadiga ocupacional.",
             "Alto risco":"Importantes sinais de exaustão. Intervenção recomendada.",
             "Risco elevado":"Elevado risco. Avaliação especializada indicada."}.get(cl,""),
            s_body)
    ]]
    st_score = Table([[Paragraph(f"{score_val}/40", s_score)],
                      [Paragraph(cl.upper(), s_class_c)]],
                     colWidths=[170*mm])
    st_score.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#050508")),
        ("BOX",(0,0),(-1,-1),1,colors.HexColor(cor)),
        ("ROUNDEDCORNERS",[6]),
        ("TOPPADDING",(0,0),(-1,-1),16),
        ("BOTTOMPADDING",(0,0),(-1,-1),16),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
    ]))
    story.append(st_score)
    story.append(Spacer(1, 14))

    # ── DOMÍNIOS ──
    story.append(Paragraph("ANÁLISE POR DOMÍNIO", s_sec))
    dom_data = [
        ["DOMÍNIO", "SCORE", "MÁXIMO", "PERCENTUAL"],
        ["Fadiga Física",      str(int(u["fadiga_fisica"])),      "16", f"{int(u['fadiga_fisica'])/16*100:.0f}%"],
        ["Exaustão Emocional", str(int(u["exaustao_emocional"])), "12", f"{int(u['exaustao_emocional'])/12*100:.0f}%"],
        ["Recuperação e Saúde",str(int(u["recuperacao_saude"])),  "12", f"{int(u['recuperacao_saude'])/12*100:.0f}%"],
        ["TOTAL",              str(score_val),                    "40", f"{score_val/40*100:.0f}%"],
    ]
    dt = Table(dom_data, colWidths=[80*mm,25*mm,25*mm,40*mm])
    dt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0a0a14")),
        ("TEXTCOLOR",(0,0),(-1,0),ORANGE),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,0),7),
        ("LETTERSPACE",(0,0),(-1,0),1.5),
        ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#0a0a14")),
        ("TEXTCOLOR",(0,-1),(-1,-1),WHITE),
        ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
        ("FONTSIZE",(1,1),(-1,-1),10),
        ("TEXTCOLOR",(1,1),(-1,-1),WHITE),
        ("TEXTCOLOR",(0,1),(0,-2),LGRAY),
        ("FONTNAME",(0,1),(0,-2),"Helvetica"),
        ("FONTSIZE",(0,1),(0,-2),9),
        ("ALIGN",(1,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-2),[colors.HexColor("#050508"),colors.HexColor("#080810")]),
        ("TOPPADDING",(0,0),(-1,-1),9),
        ("BOTTOMPADDING",(0,0),(-1,-1),9),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("RIGHTPADDING",(0,0),(-1,-1),10),
        ("LINEBELOW",(0,0),(-1,0),0.5,colors.HexColor("#1a1a2a")),
        ("LINEABOVE",(0,-1),(-1,-1),0.5,colors.HexColor("#1a1a2a")),
    ]))
    story.append(dt)
    story.append(Spacer(1, 16))

    # ── COMPARATIVO COM MÉDIA ──
    story.append(Paragraph("COMPARATIVO COM A MÉDIA GERAL", s_sec))
    avg_f = df["fadiga_fisica"].mean()
    avg_e = df["exaustao_emocional"].mean()
    avg_r = df["recuperacao_saude"].mean()
    avg_t = df["score_total"].mean()

    def delta(val, avg):
        d = val - avg
        sign = "+" if d >= 0 else ""
        return f"{sign}{d:.1f}"

    cmp_data = [
        ["INDICADOR",         "COLABORADOR", "MÉDIA GERAL", "DIFERENÇA"],
        ["Fadiga Física",     f"{int(u['fadiga_fisica'])}/16",      f"{avg_f:.1f}/16", delta(u['fadiga_fisica'],avg_f)],
        ["Exaustão Emocional",f"{int(u['exaustao_emocional'])}/12", f"{avg_e:.1f}/12", delta(u['exaustao_emocional'],avg_e)],
        ["Recuperação/Saúde", f"{int(u['recuperacao_saude'])}/12",  f"{avg_r:.1f}/12", delta(u['recuperacao_saude'],avg_r)],
        ["Score Total",       f"{score_val}/40",                    f"{avg_t:.1f}/40", delta(score_val,avg_t)],
    ]
    ct = Table(cmp_data, colWidths=[65*mm,35*mm,35*mm,35*mm])
    ct.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0a0a14")),
        ("TEXTCOLOR",(0,0),(-1,0),ORANGE),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,0),7),
        ("TEXTCOLOR",(0,1),(0,-1),LGRAY),
        ("TEXTCOLOR",(1,1),(-1,-1),WHITE),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTNAME",(0,1),(0,-1),"Helvetica"),
        ("FONTNAME",(1,1),(-1,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,1),(-1,-1),9),
        ("ALIGN",(1,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#050508"),colors.HexColor("#080810")]),
        ("TOPPADDING",(0,0),(-1,-1),9),
        ("BOTTOMPADDING",(0,0),(-1,-1),9),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("RIGHTPADDING",(0,0),(-1,-1),10),
        ("LINEBELOW",(0,0),(-1,0),0.5,colors.HexColor("#1a1a2a")),
    ]))
    story.append(ct)
    story.append(Spacer(1, 16))

    # ── RECOMENDAÇÃO ──
    story.append(Paragraph("RECOMENDAÇÃO", s_sec))
    rec = {
        "Baixo risco":   "Manutenção de hábitos saudáveis e prática regular de atividade física. Monitoramento periódico recomendado.",
        "Atenção":       "Implementação de pausas ativas, estratégias de recuperação e início de programa de exercício físico supervisionado. Reavaliar em 30 dias.",
        "Alto risco":    "Programa estruturado de exercício físico supervisionado, estratégias de recuperação e acompanhamento contínuo pela Mind In Fit.",
        "Risco elevado": "Avaliação profissional especializada com urgência. Implementação imediata de suporte ocupacional e programa intensivo de recuperação psicofisiológica."
    }.get(cl, "")
    rec_table = Table([[Paragraph(rec, s_body)]], colWidths=[170*mm])
    rec_table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#050508")),
        ("LEFTBORDERCOLOR",(0,0),(0,-1),ORANGE),
        ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#0e0e1a")),
        ("LINEBEFORE",(0,0),(0,-1),3,ORANGE),
        ("TOPPADDING",(0,0),(-1,-1),12),
        ("BOTTOMPADDING",(0,0),(-1,-1),12),
        ("LEFTPADDING",(0,0),(-1,-1),14),
        ("RIGHTPADDING",(0,0),(-1,-1),14),
    ]))
    story.append(rec_table)
    story.append(Spacer(1, 20))

    # ── RODAPÉ ──
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#111111"), spaceAfter=10))
    story.append(Paragraph(
        f"MIND IN FIT  ·  Triagem de Bem-Estar Ocupacional  ·  Baseado no Copenhagen Burnout Inventory (CBI)  ·  Documento confidencial",
        s_footer))
    story.append(Paragraph(
        f"Este relatório é de triagem e NÃO constitui diagnóstico clínico. Uso exclusivo corporativo.",
        sty("disc", fontName="Helvetica", fontSize=6, textColor=colors.HexColor("#222222"),
            alignment=TA_CENTER, leading=9, spaceAfter=0)))

    doc.build(story)
    buf.seek(0)
    return buf.read()

# ── SIDEBAR ───────────────────────────────────────────────────
PAGES = [
    ("Dashboard",            "M4 5a1 1 0 000 2h1a1 1 0 000-2H4zM4 9a1 1 0 000 2h1a1 1 0 000-2H4zM4 13a1 1 0 100 2h1a1 1 0 100-2H4zM9 5a1 1 0 000 2h7a1 1 0 000-2H9zM9 9a1 1 0 000 2h7a1 1 0 000-2H9zM9 13a1 1 0 100 2h7a1 1 0 100-2H9z",
     "M3 3h7v7H3zm11 0h7v7h-7zM3 14h7v7H3zm11 3h2v-2h2v2h2v2h-2v2h-2v-2h-2z"),
    ("Colaboradores",        "M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z",
     "M15 7a3 3 0 11-6 0 3 3 0 016 0z"),
    ("Por Setor",            "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
     "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16"),
    ("Relatório Individual", "M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
     "M9 17v-2m3 2v-4m3 4v-6"),
    ("Gerenciar Respostas",  "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16",
     "M19 7l-.867 12.142"),
    ("Motivação",            "M13 10V3L4 14h7v7l9-11h-7z",
     "M13 10V3L4 14h7v7l9-11h-7z"),
]

# ── SDT INFO ──────────────────────────────────────────────────
SDT_INFO = [
    {"nome":"Desmotivado",            "col":"sdt_desmotivado",         "cor":"#888888","auto":False,
     "carac":"Baixo volume e intensidade. Pouco dano ao tecido para indução de pouca dor.",
     "estrat":"Recompensa Imediata · Elogios · SMS · Convite à próxima sessão"},
    {"nome":"Regulação Externa",      "col":"sdt_reg_externa",         "cor":"#EF4444","auto":False,
     "carac":"Recompensa imediata · Evitar punição ou reprovação.",
     "estrat":"Suporte Social · Self-Talking · Imaginação do resultado"},
    {"nome":"Regulação Introjetada",  "col":"sdt_reg_introjetada",     "cor":"#E8470A","auto":False,
     "carac":"Sensação de pressão interna e sentimento de culpa.",
     "estrat":"Pensamentos dissociativos · Visualização do resultado · Incentivo à recompensa pessoal"},
    {"nome":"Regulação Identificada", "col":"sdt_reg_identificacao",   "cor":"#EAB308","auto":True,
     "carac":"Busca afirmação pessoal e é consciente das etapas.",
     "estrat":"Metas curtas · Desafios · Propostas de avaliação"},
    {"nome":"Regulação Integrada",    "col":"sdt_reg_integrada",       "cor":"#84CC16","auto":True,
     "carac":"Conduta consistente com as metas.",
     "estrat":"Dar feedback · Não deixar treino vencer · Atenção à periodização"},
    {"nome":"Motivação Intrínseca",   "col":"sdt_motivacao_intrinseca","cor":"#22C55E","auto":True,
     "carac":"Interesse alto na atividade, busca prazer e divertimento.",
     "estrat":"Desafios · Feedback numérico · Atenção à periodização"},
]

with st.sidebar:
    params = st.query_params
    if "page" in params:
        st.session_state.pagina = params["page"]
        st.query_params.clear()
        st.rerun()

    MENU = [
        ("Dashboard",           "▣"),
        ("Colaboradores",       "⊞"),
        ("Por Setor",           "⊟"),
        ("Relatório Individual","▤"),
        ("Gerenciar Respostas", "⊠"),
        ("Motivação",           "⚡"),
    ]

    if logo_b64:
        st.markdown(f'<img src="data:image/jpeg;base64,{logo_b64}" style="height:32px;object-fit:contain;display:block;margin-bottom:8px">', unsafe_allow_html=True)

    for name, icon in MENU:
        active = st.session_state.pagina == name
        if st.button(
            f"{'▶' if active else '  '} {icon} {name}",
            key=f"nb_{name}",
            use_container_width=True,
            type="primary" if active else "secondary"
        ):
            st.session_state.pagina = name
            st.rerun()

    st.markdown("---")
    st.caption(f"⏱ {datetime.now().strftime('%H:%M')}")
    if st.button("⏻ SAIR", key="nb_sair", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

pagina = st.session_state.pagina

# ── DADOS ─────────────────────────────────────────────────────
df = carregar()
if df.empty and pagina not in ["Gerenciar Respostas", "Motivação"]:
    st.markdown('<div class="page-hdr"><h1>Dashboard</h1></div>', unsafe_allow_html=True)
    st.info("Nenhuma resposta registrada ainda."); st.stop()
if not df.empty:
    df["class_limpa"] = df["classificacao"].apply(cl_txt)

# ══════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════
if pagina == "Dashboard":
    st.markdown('<div class="page-hdr"><span class="pg-tag">Mind In Fit</span><h1>Dashboard Geral</h1></div>', unsafe_allow_html=True)
    total=len(df); baixo=(df["class_limpa"]=="Baixo risco").sum(); atencao=(df["class_limpa"]=="Atenção").sum()
    alto=(df["class_limpa"]=="Alto risco").sum(); elevado=(df["class_limpa"]=="Risco elevado").sum()
    media=df["score_total"].mean()

    c1,c2,c3,c4,c5,c6=st.columns(6)
    for col,val,css,lbl,sub in [
        (c1,total,"cw","Total","respostas"),
        (c2,baixo,"cg","Baixo Risco",f"{baixo/total*100:.0f}%"),
        (c3,atencao,"cy","Atenção",f"{atencao/total*100:.0f}%"),
        (c4,alto,"co","Alto Risco",f"{alto/total*100:.0f}%"),
        (c5,elevado,"cr","Risco Elevado",f"{elevado/total*100:.0f}%"),
        (c6,f"{media:.1f}","cw","Score Médio","/40"),
    ]:
        col.markdown(f'<div class="kpi"><div class="kpi-lbl">{lbl}</div><div class="kpi-val {css}">{val}</div><div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ca,cb=st.columns(2)
    with ca:
        cnt=df["class_limpa"].value_counts().reset_index(); cnt.columns=["Classificação","n"]
        fig=px.pie(cnt,names="Classificação",values="n",color="Classificação",color_discrete_map=CORES,hole=.55,title="Distribuição de Risco")
        fig.update_layout(**PB); fig.update_traces(textfont_color="#fff")
        st.plotly_chart(fig,use_container_width=True)
    with cb:
        md={"Fadiga Física":df["fadiga_fisica"].mean(),"Exaustão Emocional":df["exaustao_emocional"].mean(),"Recup. e Saúde":df["recuperacao_saude"].mean()}
        fig2=go.Figure(go.Bar(x=list(md.keys()),y=list(md.values()),marker_color=["#E8470A","#EF4444","#EAB308"],text=[f"{v:.1f}" for v in md.values()],textposition="outside",textfont_color="#fff"))
        fig2.update_layout(title="Média por Domínio",**PB,yaxis=dict(gridcolor="#0e0e0e",color="#333"),xaxis=dict(color="#333"))
        st.plotly_chart(fig2,use_container_width=True)

    df_t=df.copy(); df_t["data"]=df_t["timestamp"].dt.date
    med=df_t.groupby("data")["score_total"].mean().reset_index()
    fig3=px.area(med,x="data",y="score_total",title="Evolução do Score Médio")
    fig3.update_traces(line_color="#E8470A",fillcolor="rgba(232,71,10,.06)")
    fig3.update_layout(**PB,yaxis=dict(gridcolor="#0e0e0e",range=[0,40],color="#333"),xaxis=dict(color="#333"))
    st.plotly_chart(fig3,use_container_width=True)

    st.download_button("⬇️ EXPORTAR CSV",df.drop(columns=["_row"],errors="ignore").to_csv(index=False).encode("utf-8"),f"mindinfit_{datetime.now().strftime('%Y%m%d')}.csv","text/csv")

# ══════════════════════════════════════════════════════════════
# COLABORADORES
# ══════════════════════════════════════════════════════════════
elif pagina == "Colaboradores":
    st.markdown('<div class="page-hdr"><span class="pg-tag">Mind In Fit</span><h1>Colaboradores</h1></div>', unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1: fs=st.selectbox("Setor",["Todos"]+sorted(df["setor"].dropna().unique().tolist()))
    with c2: fr=st.selectbox("Risco",["Todos","Baixo risco","Atenção","Alto risco","Risco elevado"])
    with c3: fb=st.text_input("Buscar","",placeholder="Nome...")
    d=df.copy()
    if fs!="Todos": d=d[d["setor"]==fs]
    if fr!="Todos": d=d[d["class_limpa"]==fr]
    if fb: d=d[d["nome"].str.contains(fb,case=False,na=False)]
    st.markdown(f'<p style="font-size:.75rem;color:#333;margin-bottom:12px">{len(d)} colaboradores</p>', unsafe_allow_html=True)
    for _,row in d.sort_values("score_total",ascending=False).iterrows():
        cor=cor_s(int(row["score_total"]))
        st.markdown(f'<div class="row-card"><div><div class="row-name">{row["nome"]}</div><div class="row-meta">{row["cargo"]} · {row["setor"]} · {row["idade"]} anos · {row["timestamp"].strftime("%d/%m/%Y")}</div></div><div style="text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:5px"><div class="row-score" style="color:{cor}">{int(row["score_total"])}<span style="font-size:.75rem;color:#222">/40</span></div>{badge(row["classificacao"])}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    st.download_button("⬇️ EXPORTAR",d.drop(columns=["_row"],errors="ignore").to_csv(index=False).encode("utf-8"),"colaboradores.csv","text/csv")

# ══════════════════════════════════════════════════════════════
# POR SETOR
# ══════════════════════════════════════════════════════════════
elif pagina == "Por Setor":
    st.markdown('<div class="page-hdr"><span class="pg-tag">Mind In Fit</span><h1>Análise por Setor</h1></div>', unsafe_allow_html=True)
    res=df.groupby("setor").agg(n=("nome","count"),score=("score_total","mean"),fadiga=("fadiga_fisica","mean"),emocional=("exaustao_emocional","mean"),recuperacao=("recuperacao_saude","mean")).reset_index().sort_values("score",ascending=False)
    res["risco"]=res["score"].apply(classificar)
    fig=px.bar(res,x="setor",y="score",color="risco",color_discrete_map=CORES,text=res["score"].apply(lambda x:f"{x:.1f}"),title="Score Médio por Setor")
    fig.update_layout(**PB,yaxis=dict(gridcolor="#0e0e0e",range=[0,42],color="#333"),xaxis=dict(color="#333"))
    fig.update_traces(textfont_color="#fff")
    st.plotly_chart(fig,use_container_width=True)
    for _,row in res.iterrows():
        with st.expander(f"🏢 {row['setor']}  ·  {row['n']} pessoas  ·  Score: {row['score']:.1f}/40"):
            c1,c2,c3,c4=st.columns(4)
            c1.metric("Score",f"{row['score']:.1f}/40"); c2.metric("Fadiga",f"{row['fadiga']:.1f}/16")
            c3.metric("Emocional",f"{row['emocional']:.1f}/12"); c4.metric("Recuperação",f"{row['recuperacao']:.1f}/12")
            ds=df[df["setor"]==row["setor"]][["nome","cargo","score_total","classificacao"]].copy()
            ds.columns=["Nome","Cargo","Score","Classificação"]
            st.dataframe(ds,use_container_width=True,hide_index=True)

# ══════════════════════════════════════════════════════════════
# RELATÓRIO INDIVIDUAL
# ══════════════════════════════════════════════════════════════
elif pagina == "Relatório Individual":
    st.markdown('<div class="page-hdr"><span class="pg-tag">Mind In Fit</span><h1>Relatório Individual</h1></div>', unsafe_allow_html=True)
    nomes=sorted(df["nome"].dropna().unique().tolist())
    sel=st.selectbox("Colaborador",nomes)
    dp=df[df["nome"]==sel].sort_values("timestamp",ascending=False)
    if dp.empty: st.warning("Nenhum dado encontrado.")
    else:
        u=dp.iloc[0]; score=int(u["score_total"]); cor=cor_s(score)
        c1,c2=st.columns([3,1])
        with c1:
            st.markdown(f"### {u['nome']}")
            st.markdown(f"**{u['cargo']}** · {u['setor']} · {u['idade']} anos")
            st.caption(f"Preenchido em {u['timestamp'].strftime('%d/%m/%Y às %H:%M')}")
        with c2:
            st.markdown(f'<div class="kpi"><div class="kpi-lbl">Score</div><div class="kpi-val" style="color:{cor}">{score}/40</div><div class="kpi-sub">{cl_txt(u["classificacao"])}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        cats=["Fadiga Física","Exaustão Emocional","Recup. e Saúde"]
        vp=[u["fadiga_fisica"]/16*100,u["exaustao_emocional"]/12*100,u["recuperacao_saude"]/12*100]
        vm=[df["fadiga_fisica"].mean()/16*100,df["exaustao_emocional"].mean()/12*100,df["recuperacao_saude"].mean()/12*100]
        fig=go.Figure()
        fig.add_trace(go.Scatterpolar(r=vp+[vp[0]],theta=cats+[cats[0]],fill="toself",name=sel,line_color="#E8470A",fillcolor="rgba(232,71,10,.08)"))
        fig.add_trace(go.Scatterpolar(r=vm+[vm[0]],theta=cats+[cats[0]],fill="toself",name="Média Geral",line_color="#333",fillcolor="rgba(100,100,100,.04)"))
        fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",radialaxis=dict(visible=True,range=[0,100],gridcolor="#111",color="#444"),angularaxis=dict(color="#666")),**PB,title="Perfil por Domínio vs. Média Geral")
        st.plotly_chart(fig,use_container_width=True)
        c1,c2,c3=st.columns(3)
        c1.metric("Fadiga Física",f"{int(u['fadiga_fisica'])}/16",delta=f"{u['fadiga_fisica']-df['fadiga_fisica'].mean():.1f} vs média")
        c2.metric("Exaustão Emocional",f"{int(u['exaustao_emocional'])}/12",delta=f"{u['exaustao_emocional']-df['exaustao_emocional'].mean():.1f} vs média")
        c3.metric("Recuperação/Saúde",f"{int(u['recuperacao_saude'])}/12",delta=f"{u['recuperacao_saude']-df['recuperacao_saude'].mean():.1f} vs média")

        st.markdown("---")
        st.markdown("#### ⬇️ Exportar Relatório")
        c1,c2=st.columns(2)
        with c1:
            st.download_button("📄 BAIXAR PDF",data=gerar_pdf(u,df),
                               file_name=f"relatorio_{sel.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                               mime="application/pdf",use_container_width=True)
        with c2:
            st.download_button("📊 BAIXAR CSV",data=dp.drop(columns=["_row"],errors="ignore").to_csv(index=False).encode("utf-8"),
                               file_name=f"relatorio_{sel.replace(' ','_')}.csv",mime="text/csv",use_container_width=True)

# ══════════════════════════════════════════════════════════════
# GERENCIAR RESPOSTAS
# ══════════════════════════════════════════════════════════════
elif pagina == "Gerenciar Respostas":
    st.markdown('<div class="page-hdr"><span class="pg-tag">Mind In Fit</span><h1>Gerenciar Respostas</h1></div>', unsafe_allow_html=True)
    if df.empty: st.info("Nenhuma resposta registrada ainda."); st.stop()
    tab1,tab2=st.tabs(["🗑️ Excluir por Nome","☑️ Excluir Múltiplas"])
    with tab1:
        nomes=sorted(df["nome"].dropna().unique().tolist())
        sel=st.selectbox("Colaborador", nomes if nomes else [""], label_visibility="collapsed")
        if sel:
            dp=df[df["nome"]==sel].sort_values("timestamp",ascending=False)
            st.markdown(f"**{len(dp)} resposta(s)** de **{sel}**")
            for _,row in dp.iterrows():
                cor=cor_s(int(row["score_total"]))
                st.markdown(f'<div class="row-card"><div><div class="row-name">{row["nome"]}</div><div class="row-meta">{row["cargo"]} · {row["timestamp"].strftime("%d/%m/%Y %H:%M")}</div></div><div style="text-align:right"><div class="row-score" style="color:{cor}">{int(row["score_total"])}/40</div>{badge(row["classificacao"])}</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="del-zone">', unsafe_allow_html=True)
            st.markdown(f'<div class="del-warn">⚠️ Excluirá <strong>todas as {len(dp)} resposta(s)</strong> de <strong>{sel}</strong> permanentemente.</div>', unsafe_allow_html=True)
            ca,cb=st.columns(2)
            with ca: conf=st.text_input("Digite o nome para confirmar:",placeholder=sel,key="conf1")
            with cb:
                st.markdown("<br>",unsafe_allow_html=True)
                if st.button(f"🗑️ EXCLUIR RESPOSTAS DE {sel.upper()}",key="del1"):
                    if conf.strip().lower()==sel.strip().lower():
                        if excluir_linhas(dp["_row"].tolist()): st.success(f"✅ Respostas de {sel} excluídas!"); st.rerun()
                    else: st.error("Nome não confere.")
            st.markdown('</div>',unsafe_allow_html=True)
    with tab2:
        df_s=df[["nome","cargo","setor","timestamp","score_total","_row"]].copy()
        df_s["data"]=df_s["timestamp"].dt.strftime("%d/%m/%Y %H:%M")
        opcoes={f"{r['nome']} · {r['data']} · Score {int(r['score_total'])}/40":r["_row"] for _,r in df_s.sort_values("score_total",ascending=False).iterrows()}
        sels=st.multiselect("Respostas:",list(opcoes.keys()),placeholder="Selecione respostas...")
        if sels:
            st.markdown(f'<div class="del-warn">⚠️ <strong>{len(sels)} resposta(s)</strong> selecionada(s) para exclusão permanente.</div>', unsafe_allow_html=True)
            if st.button(f"🗑️ EXCLUIR {len(sels)} RESPOSTA(S)",key="del2"):
                if excluir_linhas([opcoes[s] for s in sels]): st.success(f"✅ {len(sels)} resposta(s) excluída(s)!"); st.rerun()

st.markdown("---")
st.caption("Mind In Fit · Painel do Gestor · Dados confidenciais")
# ══════════════════════════════════════════════════════════════
# MOTIVAÇÃO
# ══════════════════════════════════════════════════════════════
if pagina == "Motivação":
    st.markdown('<div class="page-hdr"><span class="pg-tag">Mind In Fit</span><h1>Motivação para Atividade Física</h1></div>', unsafe_allow_html=True)

    df_mot = carregar_motivacao()

    if df_mot.empty:
        st.info("Nenhuma resposta do questionário de motivação registrada ainda.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "👤 Individual + PDF", "🗑️ Gerenciar"])

    # ── VISÃO GERAL ──────────────────────────────────────────
    with tab1:
        total_m = len(df_mot)
        dom_counts = df_mot["estagio_dominante"].value_counts() if "estagio_dominante" in df_mot.columns else pd.Series()
        auto_det = df_mot["estagio_dominante"].isin(["Regulação Identificada","Regulação Integrada","Motivação Intrínseca"]).sum() if "estagio_dominante" in df_mot.columns else 0

        c1,c2,c3 = st.columns(3)
        c1.markdown(f'<div class="kpi"><div class="kpi-lbl">Total Respostas</div><div class="kpi-val cw">{total_m}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="kpi"><div class="kpi-lbl">Estágio Mais Comum</div><div class="kpi-val co" style="font-size:.9rem;line-height:1.2">{dom_counts.index[0] if len(dom_counts)>0 else "-"}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="kpi"><div class="kpi-lbl">Auto-Deterministas</div><div class="kpi-val cg">{auto_det}</div><div class="kpi-sub">{auto_det/total_m*100:.0f}%</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        ca, cb = st.columns(2)

        with ca:
            cats = ["Psicológico","Interpessoal","Saúde","Estético","Condição Física"]
            mcols = ["media_psicologico","media_interpessoal","media_saude","media_estetico","media_condicao"]
            vals_m = [df_mot[c].mean() if c in df_mot.columns else 0 for c in mcols]
            fig_r = go.Figure(go.Scatterpolar(
                r=vals_m+[vals_m[0]], theta=cats+[cats[0]],
                fill="toself", line_color="#E8470A", fillcolor="rgba(232,71,10,0.1)"
            ))
            fig_r.update_layout(
                polar=dict(bgcolor="rgba(0,0,0,0)",
                           radialaxis=dict(visible=True,range=[0,5],gridcolor="#111",color="#555"),
                           angularaxis=dict(color="#aaa")),
                paper_bgcolor="rgba(0,0,0,0)", font_color="#fff",
                title="Perfil Médio dos Pilares", showlegend=False, height=320
            )
            st.plotly_chart(fig_r, use_container_width=True)

        with cb:
            sdt_medias = {s["nome"]: df_mot[s["col"]].mean() if s["col"] in df_mot.columns else 0 for s in SDT_INFO}
            fig_sdt = go.Figure(go.Bar(
                x=list(sdt_medias.keys()), y=list(sdt_medias.values()),
                marker_color=[s["cor"] for s in SDT_INFO],
                text=[f"{v:.2f}" for v in sdt_medias.values()],
                textposition="outside", textfont_color="#fff"
            ))
            fig_sdt.update_layout(
                title="Média por Estágio SDT",
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#fff", yaxis=dict(gridcolor="#111",range=[0,5.5],color="#555"),
                xaxis=dict(color="#555", tickangle=-20)
            )
            st.plotly_chart(fig_sdt, use_container_width=True)

        if "estagio_dominante" in df_mot.columns:
            ec = df_mot["estagio_dominante"].value_counts().reset_index()
            ec.columns = ["Estágio","n"]
            cor_map = {s["nome"]:s["cor"] for s in SDT_INFO}
            fig_pie = px.pie(ec, names="Estágio", values="n", color="Estágio",
                             color_discrete_map=cor_map, hole=0.5,
                             title="Distribuição dos Estágios Dominantes")
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#fff")
            st.plotly_chart(fig_pie, use_container_width=True)

    # ── INDIVIDUAL + PDF ─────────────────────────────────────
    with tab2:
        nomes_m = sorted(df_mot["nome"].dropna().unique().tolist())
        sel_m = st.selectbox("Selecione o colaborador", nomes_m, key="sel_mot")
        dp_m = df_mot[df_mot["nome"]==sel_m].sort_values("timestamp", ascending=False)

        if not dp_m.empty:
            u_m = dp_m.iloc[0]
            estagio_dom = u_m.get("estagio_dominante", "-")
            sdt_dom_info = next((s for s in SDT_INFO if s["nome"]==estagio_dom), SDT_INFO[0])

            c1,c2 = st.columns([3,1])
            with c1:
                st.markdown(f"### {u_m['nome']}")
                st.markdown(f"**{u_m['cargo']}** · {u_m['setor']} · {u_m['idade']} anos")
                st.caption(f"Preenchido em {u_m['timestamp'].strftime('%d/%m/%Y às %H:%M')}")
            with c2:
                st.markdown(f'<div class="kpi" style="border-top-color:{sdt_dom_info["cor"]}"><div class="kpi-lbl">Estágio</div><div class="kpi-val" style="color:{sdt_dom_info["cor"]};font-size:.85rem;line-height:1.2">{estagio_dom}</div></div>', unsafe_allow_html=True)

            st.markdown("---")

            cats = ["Psicológico","Interpessoal","Saúde","Estético","Condição Física"]
            mcols = ["media_psicologico","media_interpessoal","media_saude","media_estetico","media_condicao"]
            v_ind = [float(u_m.get(c,0)) for c in mcols]
            v_med = [df_mot[c].mean() if c in df_mot.columns else 0 for c in mcols]

            fig_ind = go.Figure()
            fig_ind.add_trace(go.Scatterpolar(r=v_ind+[v_ind[0]], theta=cats+[cats[0]], fill="toself",
                                               name=sel_m, line_color="#E8470A", fillcolor="rgba(232,71,10,0.1)"))
            fig_ind.add_trace(go.Scatterpolar(r=v_med+[v_med[0]], theta=cats+[cats[0]], fill="toself",
                                               name="Média Geral", line_color="#444", fillcolor="rgba(100,100,100,0.05)"))
            fig_ind.update_layout(
                polar=dict(bgcolor="rgba(0,0,0,0)",
                           radialaxis=dict(visible=True,range=[0,5],gridcolor="#111",color="#555"),
                           angularaxis=dict(color="#aaa")),
                paper_bgcolor="rgba(0,0,0,0)", font_color="#fff",
                title="Perfil de Motivação vs. Média Geral",
                legend=dict(bgcolor="rgba(0,0,0,0)"), height=340
            )
            st.plotly_chart(fig_ind, use_container_width=True)

            st.markdown("#### Estágios de Regulação Motivacional")
            for sdt in SDT_INFO:
                val = float(u_m.get(sdt["col"],0))
                is_dom = sdt["nome"] == estagio_dom
                bdr = f"2px solid {sdt['cor']}" if is_dom else f"1px solid {sdt['cor']}33"
                dom_b = f' <span style="font-size:.58rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:{sdt["cor"]};background:{sdt["cor"]}22;padding:2px 6px;border-radius:3px">★ DOMINANTE</span>' if is_dom else ""
                auto_c = "#22C55E" if sdt["auto"] else "#EF4444"
                auto_l = "AUTO-DET." if sdt["auto"] else "NÃO-AUTO-DET."
                st.markdown(f'<div style="background:#080810;border:{bdr};border-radius:10px;padding:12px 16px;margin:4px 0;display:flex;align-items:center;gap:14px"><div style="font-family:Barlow Condensed,sans-serif;font-size:1.5rem;font-weight:900;min-width:42px;text-align:center;color:{sdt["cor"]}">{val:.1f}</div><div style="flex:1"><div style="font-family:Barlow Condensed,sans-serif;font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:{sdt["cor"]};margin-bottom:3px">{sdt["nome"]}{dom_b} <span style="font-size:.58rem;color:{auto_c};background:{auto_c}22;padding:1px 5px;border-radius:3px">{auto_l}</span></div><div style="font-size:.74rem;color:#aaa;line-height:1.4;margin-bottom:2px">{sdt["carac"]}</div><div style="font-size:.7rem;color:#666;font-style:italic">💡 {sdt["estrat"]}</div></div></div>', unsafe_allow_html=True)

            st.markdown("---")

            def gerar_pdf_motivacao(u_m, df_mot):
                buf = io.BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=A4,
                                        leftMargin=20*mm, rightMargin=20*mm,
                                        topMargin=18*mm, bottomMargin=18*mm)
                ORANGE = colors.HexColor("#E8470A")
                WHITE  = colors.white
                LGRAY  = colors.HexColor("#cccccc")
                GRAY   = colors.HexColor("#888888")

                def sty(name, **kw): return ParagraphStyle(name, **kw)
                s_ey  = sty("ey",  fontName="Helvetica-Bold", fontSize=7,  textColor=ORANGE, spaceAfter=4, leading=10, letterSpacing=2)
                s_ti  = sty("ti",  fontName="Helvetica-Bold", fontSize=26, textColor=WHITE,  spaceAfter=4, leading=30)
                s_sub = sty("sub", fontName="Helvetica",      fontSize=10, textColor=LGRAY,  spaceAfter=12, leading=15)
                s_sec = sty("sec", fontName="Helvetica-Bold", fontSize=7,  textColor=ORANGE, spaceAfter=6, leading=10, letterSpacing=2)
                s_bod = sty("bod", fontName="Helvetica",      fontSize=9,  textColor=LGRAY,  spaceAfter=6, leading=14)
                s_rig = sty("rig", fontName="Helvetica",      fontSize=8,  textColor=GRAY,   alignment=TA_RIGHT, leading=12)
                s_ft  = sty("ft",  fontName="Helvetica",      fontSize=7,  textColor=colors.HexColor("#333333"), alignment=TA_CENTER, leading=10)
                story = []

                ht = Table([[Paragraph("MIND IN FIT", sty("mif",fontName="Helvetica-Bold",fontSize=16,textColor=ORANGE,leading=18)),
                             Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", s_rig)]],
                           colWidths=[90*mm,80*mm])
                ht.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),("BOTTOMPADDING",(0,0),(-1,-1),10)]))
                story.append(ht)
                story.append(HRFlowable(width="100%",thickness=1,color=ORANGE,spaceAfter=14))

                story.append(Paragraph("RELATÓRIO DE MOTIVAÇÃO PARA ATIVIDADE FÍSICA", s_ey))
                story.append(Paragraph(str(u_m["nome"]), s_ti))
                story.append(Paragraph(f"{u_m['cargo']}  ·  {u_m['setor']}  ·  {u_m['idade']} anos", s_sub))
                story.append(HRFlowable(width="100%",thickness=0.5,color=colors.HexColor("#111111"),spaceAfter=14))

                ed = str(u_m.get("estagio_dominante","-"))
                sdt_d = next((s for s in SDT_INFO if s["nome"]==ed), SDT_INFO[0])
                ed_cor = colors.HexColor(sdt_d["cor"])
                ed_t = Table([[Paragraph(ed.upper(), sty("edc",fontName="Helvetica-Bold",fontSize=18,textColor=ed_cor,leading=22,alignment=TA_CENTER))],
                               [Paragraph("ESTÁGIO MOTIVACIONAL DOMINANTE", sty("edl",fontName="Helvetica-Bold",fontSize=7,textColor=GRAY,leading=10,alignment=TA_CENTER,letterSpacing=1.5))]],
                             colWidths=[170*mm])
                ed_t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#050508")),
                                          ("BOX",(0,0),(-1,-1),1.5,ed_cor),
                                          ("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),14)]))
                story.append(ed_t)
                story.append(Spacer(1,14))

                story.append(Paragraph("PERFIL POR PILAR (MÉDIA 1–5)", s_sec))
                pilar_nomes = ["Psicológico","Interpessoal","Saúde","Estético","Condição Física"]
                pilar_cols  = ["media_psicologico","media_interpessoal","media_saude","media_estetico","media_condicao"]
                pd_data = [["PILAR","SCORE","MÉDIA GERAL","DIFERENÇA"]]
                for pn,pc in zip(pilar_nomes,pilar_cols):
                    v=float(u_m.get(pc,0)); avg=df_mot[pc].mean() if pc in df_mot.columns else 0; d=v-avg
                    pd_data.append([pn,f"{v:.2f}",f"{avg:.2f}",f"{'+' if d>=0 else ''}{d:.2f}"])
                pt = Table(pd_data, colWidths=[70*mm,30*mm,35*mm,35*mm])
                pt.setStyle(TableStyle([
                    ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0a0a14")),("TEXTCOLOR",(0,0),(-1,0),ORANGE),
                    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),7),
                    ("TEXTCOLOR",(0,1),(0,-1),LGRAY),("TEXTCOLOR",(1,1),(-1,-1),WHITE),
                    ("FONTNAME",(0,1),(0,-1),"Helvetica"),("FONTNAME",(1,1),(-1,-1),"Helvetica-Bold"),
                    ("FONTSIZE",(0,1),(-1,-1),9),("ALIGN",(1,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#050508"),colors.HexColor("#080810")]),
                    ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
                    ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
                    ("LINEBELOW",(0,0),(-1,0),0.5,colors.HexColor("#1a1a2a"))]))
                story.append(pt)
                story.append(Spacer(1,14))

                story.append(Paragraph("ESTÁGIOS DE REGULAÇÃO MOTIVACIONAL (SDT)", s_sec))
                sdt_data = [["ESTÁGIO","SCORE","AUTO-DET.","CARACTERÍSTICA"]]
                for sdt in SDT_INFO:
                    val=float(u_m.get(sdt["col"],0))
                    sdt_data.append([sdt["nome"],f"{val:.2f}","SIM" if sdt["auto"] else "NÃO",
                                     sdt["carac"][:55]+"..." if len(sdt["carac"])>55 else sdt["carac"]])
                st_t = Table(sdt_data, colWidths=[45*mm,20*mm,20*mm,85*mm])
                st_t.setStyle(TableStyle([
                    ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0a0a14")),("TEXTCOLOR",(0,0),(-1,0),ORANGE),
                    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),7),
                    ("TEXTCOLOR",(0,1),(0,-1),LGRAY),("TEXTCOLOR",(1,1),(-1,-1),WHITE),
                    ("FONTNAME",(0,1),(-1,-1),"Helvetica"),("FONTSIZE",(0,1),(-1,-1),8),
                    ("ALIGN",(1,0),(2,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#050508"),colors.HexColor("#080810")]),
                    ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
                    ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
                    ("LINEBELOW",(0,0),(-1,0),0.5,colors.HexColor("#1a1a2a"))]))
                story.append(st_t)
                story.append(Spacer(1,14))

                story.append(Paragraph("ESTRATÉGIA RECOMENDADA", s_sec))
                rec_t = Table([[Paragraph(sdt_d["estrat"], s_bod)]], colWidths=[170*mm])
                rec_t.setStyle(TableStyle([
                    ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#050508")),
                    ("LINEBEFORE",(0,0),(0,-1),3,ed_cor),
                    ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#0e0e1a")),
                    ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
                    ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14)]))
                story.append(rec_t)
                story.append(Spacer(1,20))

                story.append(HRFlowable(width="100%",thickness=0.5,color=colors.HexColor("#111111"),spaceAfter=10))
                story.append(Paragraph("MIND IN FIT  ·  Avaliação de Motivação  ·  Teoria da Autodeterminação (SDT)  ·  Documento confidencial", s_ft))

                doc.build(story)
                buf.seek(0)
                return buf.read()

            st.download_button(
                "📄 BAIXAR PDF — RELATÓRIO DE MOTIVAÇÃO",
                data=gerar_pdf_motivacao(u_m, df_mot),
                file_name=f"motivacao_{sel_m.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # ── GERENCIAR ────────────────────────────────────────────
    with tab3:
        nomes_gm = sorted(df_mot["nome"].dropna().unique().tolist())
        if nomes_gm:
            sel_gm = st.selectbox("Colaborador", nomes_gm, key="sel_gm_del")
            dp_gm = df_mot[df_mot["nome"]==sel_gm]
            st.markdown(f"**{len(dp_gm)} resposta(s)** de **{sel_gm}**")
            conf_gm = st.text_input("Digite o nome para confirmar:", placeholder=sel_gm, key="conf_gm")
            if st.button(f"EXCLUIR RESPOSTAS DE {sel_gm.upper()}", key="del_gm"):
                if conf_gm.strip().lower()==sel_gm.strip().lower():
                    try:
                        c=conectar()
                        sp=c.open_by_key(st.secrets["sheet_id"])
                        aba=sp.worksheet("motivacao")
                        for r in sorted(dp_gm["_row"].tolist(),reverse=True): aba.delete_rows(r)
                        carregar_motivacao.clear()
                        st.success(f"✅ Respostas de {sel_gm} excluídas!"); st.rerun()
                    except Exception as e: st.error(f"Erro: {e}")
                else: st.error("Nome não confere.")
