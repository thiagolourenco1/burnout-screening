import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import base64
import os

st.set_page_config(
    page_title="Mind In Fit | Triagem de Bem-Estar",
    page_icon="🧠",
    layout="centered"
)

# ── Logo em base64 ──────────────────────────────────────────
def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "logo_mindinfit.jpeg")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_base64()
logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" class="logo" alt="Mind In Fit">' if logo_b64 else '<span class="logo-text">MIND IN FIT</span>'

# ── CSS ─────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@300;400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Barlow', sans-serif;
    background-color: #000000;
    color: #FFFFFF;
}}

.main {{ background-color: #000000; }}
h1, h2, h3 {{ font-family: 'Barlow Condensed', sans-serif; color: #FFFFFF; letter-spacing: 0.02em; }}

/* ── HEADER ── */
.header {{
    background: #000000;
    border-bottom: 3px solid #E8470A;
    padding: 24px 0 20px;
    margin-bottom: 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.logo {{ height: 52px; object-fit: contain; }}
.logo-text {{ font-family: 'Barlow Condensed', sans-serif; font-size: 1.8rem; font-weight: 800; color: #E8470A; letter-spacing: 0.05em; }}

.header-label {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #FFFFFF;
    text-align: right;
    line-height: 1.4;
}}

/* ── HERO ── */
.hero {{
    border-left: 5px solid #E8470A;
    padding: 28px 32px;
    background: #0A0A0A;
    margin-bottom: 32px;
}}

.hero .eyebrow {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #E8470A;
    margin-bottom: 10px;
}}

.hero h1 {{
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1.1;
    margin: 0 0 12px;
    color: #FFFFFF;
}}

.hero p {{
    color: #FFFFFF;
    font-size: 0.9rem;
    margin: 0;
    line-height: 1.6;
}}

/* ── SECTION ── */
.section {{
    background: #0A0A0A;
    border: 1px solid #1A1A1A;
    border-top: 3px solid #E8470A;
    border-radius: 2px;
    padding: 28px;
    margin-bottom: 20px;
}}

.section-title {{
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #E8470A;
    margin-bottom: 20px;
}}

/* ── RESULT ── */
.result {{
    border: 2px solid;
    padding: 36px;
    margin: 24px 0;
    text-align: center;
    position: relative;
    overflow: hidden;
}}
.result::before {{
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 6px; height: 100%;
    background: currentColor;
}}
.result-baixo   {{ border-color: #22C55E; color: #22C55E; background: #000000; }}
.result-atencao {{ border-color: #EAB308; color: #EAB308; background: #000000; }}
.result-alto    {{ border-color: #E8470A; color: #E8470A; background: #000000; }}
.result-elevado {{ border-color: #EF4444; color: #EF4444; background: #000000; }}
.result h2 {{ font-family: 'Barlow Condensed', sans-serif; font-size: 3rem; font-weight: 800; margin: 0 0 4px; }}
.result h3 {{ font-size: 1.1rem; font-weight: 600; margin: 0 0 12px; letter-spacing: 0.1em; text-transform: uppercase; }}
.result p  {{ color: #FFFFFF; font-size: 0.9rem; margin: 0; }}

/* ── AVISO ── */
.aviso {{
    border-left: 4px solid #E8470A;
    background: #0A0A0A;
    padding: 14px 18px;
    font-size: 0.82rem;
    color: #FFFFFF;
    margin-top: 24px;
    line-height: 1.6;
}}

/* ── BOTÃO ── */
.stButton>button {{
    background: #E8470A !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 14px 32px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    height: auto !important;
    transition: opacity 0.2s !important;
}}
.stButton>button:hover {{ opacity: 0.85 !important; }}

/* ── INPUTS ── */
.stTextInput>div>div>input,
.stNumberInput>div>div>input {{
    background: #0A0A0A !important;
    border: 1px solid #333333 !important;
    border-radius: 2px !important;
    color: #FFFFFF !important;
    font-family: 'Barlow', sans-serif !important;
}}
.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus {{
    border-color: #E8470A !important;
    box-shadow: 0 0 0 1px #E8470A !important;
}}

/* Labels dos inputs */
.stTextInput label, .stNumberInput label {{ color: #FFFFFF !important; }}

/* ── RADIO — forçar texto branco em todos os estados ── */
.stRadio > label {{ color: #FFFFFF !important; font-size: 0.9rem !important; }}
.stRadio label {{ color: #FFFFFF !important; }}
.stRadio label p {{ color: #FFFFFF !important; }}
.stRadio span {{ color: #FFFFFF !important; }}
div[data-testid="stRadio"] {{ color: #FFFFFF !important; }}
div[data-testid="stRadio"] label {{ color: #FFFFFF !important; }}
div[data-testid="stRadio"] label span {{ color: #FFFFFF !important; }}
div[data-testid="stRadio"] p {{ color: #FFFFFF !important; }}
div[data-testid="stRadio"] div {{ color: #FFFFFF !important; }}
.stRadio [data-testid="stMarkdownContainer"] p {{ color: #FFFFFF !important; }}
.stRadio [data-testid="stMarkdownContainer"] {{ color: #FFFFFF !important; }}

/* ── Texto geral das perguntas e labels ── */
p {{ color: #FFFFFF !important; }}
label {{ color: #FFFFFF !important; }}
.stMarkdown p {{ color: #FFFFFF !important; }}
[data-testid="stMarkdownContainer"] p {{ color: #FFFFFF !important; }}
[data-testid="stText"] {{ color: #FFFFFF !important; }}
small {{ color: #CCCCCC !important; }}

/* ── RODAPÉ ── */
footer {{ visibility: hidden; }}
div[data-testid="stSidebar"] {{ display: none; }}

/* ── Forçar fundo preto em todos os containers do Streamlit ── */
[data-testid="stAppViewContainer"] {{ background-color: #000000 !important; }}
[data-testid="stHeader"] {{ background-color: #000000 !important; }}
[data-testid="block-container"] {{ background-color: #000000 !important; }}
section[data-testid="stSidebar"] {{ background-color: #000000 !important; }}
.stApp {{ background-color: #000000 !important; }}

.rodape {{
    text-align: center;
    padding: 32px 0 16px;
    font-size: 0.75rem;
    color: #FFFFFF;
    letter-spacing: 0.05em;
    border-top: 1px solid #1A1A1A;
    margin-top: 40px;
}}
</style>
""", unsafe_allow_html=True)


# ── CONEXÃO GOOGLE SHEETS ────────────────────────────────────
@st.cache_resource
def conectar_sheets():
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Erro ao conectar ao Google Sheets: {e}")
        return None


def salvar_resposta(dados: dict):
    client = conectar_sheets()
    if client is None:
        return False
    try:
        sheet_id = st.secrets["sheet_id"]
        spreadsheet = client.open_by_key(sheet_id)
        try:
            aba = spreadsheet.worksheet("respostas")
        except gspread.exceptions.WorksheetNotFound:
            aba = spreadsheet.add_worksheet(title="respostas", rows=1000, cols=30)
            cabecalho = [
                "timestamp", "nome", "email", "setor", "cargo", "idade",
                "q1","q2","q3","q4","q5","q6","q7","q8","q9","q10",
                "score_total", "classificacao",
                "fadiga_fisica", "exaustao_emocional", "recuperacao_saude"
            ]
            aba.append_row(cabecalho)
        linha = [
            dados["timestamp"], dados["nome"], dados["email"],
            dados["setor"], dados["cargo"], dados["idade"],
            *dados["pontuacoes"],
            dados["score_total"], dados["classificacao"],
            dados["fadiga"], dados["emocional"], dados["recuperacao"]
        ]
        aba.append_row(linha)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar dados: {e}")
        return False


# ── ESCALA & PERGUNTAS ────────────────────────────────────────
ESCALA = {"Nunca": 0, "Raramente": 1, "Às vezes": 2, "Frequentemente": 3, "Sempre": 4}

DOMINIOS = {
    "FADIGA FÍSICA": [
        "Você se sente cansado(a) ao acordar para trabalhar?",
        "Você sente esgotamento físico ao final do expediente?",
        "Você sente que seu trabalho drena sua energia?",
        "Você percebe dificuldade de recuperação mesmo após descanso?",
    ],
    "EXAUSTÃO EMOCIONAL": [
        "Você sente exaustão emocional relacionada ao trabalho?",
        "Você percebe queda de motivação nas tarefas diárias?",
        "Você sente dificuldade de concentração durante o trabalho?",
    ],
    "RECUPERAÇÃO E SAÚDE": [
        "Você sente que o trabalho afeta negativamente sua saúde?",
        "Você percebe piora do sono nas últimas semanas?",
        "Você sente redução da disposição física geral?",
    ]
}

# ── HEADER ───────────────────────────────────────────────────
st.markdown(f"""
<div class="header">
    {logo_html}
    <div class="header-label">TRIAGEM CORPORATIVA<br>BEM-ESTAR OCUPACIONAL</div>
</div>
""", unsafe_allow_html=True)

# ── HERO ─────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="eyebrow">📋 Avaliação psicofisiológica</div>
    <h1>Como você está?</h1>
    <p>Triagem baseada no Copenhagen Burnout Inventory (CBI). Suas respostas são confidenciais e levam cerca de <strong style="color:#F0EDE8">3 minutos</strong>.</p>
</div>
""", unsafe_allow_html=True)

# ── DADOS DO COLABORADOR ──────────────────────────────────────
st.markdown('<div class="section"><div class="section-title">01 — Identificação</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    nome  = st.text_input("Nome completo *")
    email = st.text_input("E-mail corporativo *")
    setor = st.text_input("Setor / Departamento *")
with col2:
    cargo = st.text_input("Cargo *")
    idade = st.number_input("Idade *", min_value=18, max_value=70, value=30)
st.markdown('</div>', unsafe_allow_html=True)

# ── QUESTIONÁRIO ──────────────────────────────────────────────
st.markdown('<div style="margin-bottom:8px; font-family:\'Barlow Condensed\',sans-serif; font-size:0.7rem; font-weight:700; letter-spacing:0.2em; color:#666; text-transform:uppercase;">02 — Questionário</div>', unsafe_allow_html=True)

pontuacoes = []
num_pergunta = 1

for dominio, perguntas in DOMINIOS.items():
    st.markdown(f'<div class="section"><div class="section-title">{dominio}</div>', unsafe_allow_html=True)
    for pergunta in perguntas:
        resposta = st.radio(
            f"{num_pergunta}. {pergunta}",
            options=list(ESCALA.keys()),
            horizontal=True,
            key=f"q{num_pergunta}",
            index=None
        )
        pontuacoes.append(resposta)
        num_pergunta += 1
    st.markdown('</div>', unsafe_allow_html=True)

# ── AVISO ─────────────────────────────────────────────────────
st.markdown("""
<div class="aviso">
    ⚠️ Esta ferramenta é de triagem e <strong style="color:#F0EDE8">não fornece diagnóstico clínico</strong>.
    Dados utilizados exclusivamente para ações de saúde ocupacional. Tratamento em conformidade com a LGPD.
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── ENVIO ─────────────────────────────────────────────────────
if st.button("ENVIAR RESPOSTAS"):
    campos_vazios = not all([nome.strip(), email.strip(), setor.strip(), cargo.strip()])
    respostas_incompletas = any(r is None for r in pontuacoes)

    if campos_vazios:
        st.error("⚠️ Preencha todos os campos obrigatórios.")
    elif respostas_incompletas:
        st.error("⚠️ Responda todas as perguntas antes de enviar.")
    else:
        pts = [ESCALA[r] for r in pontuacoes]
        score_total = sum(pts)
        fadiga      = sum(pts[0:4])
        emocional   = sum(pts[4:7])
        recuperacao = sum(pts[7:10])

        if score_total <= 10:
            classificacao = "Baixo risco";   emoji = "🟢"; css = "result-baixo"
            interpretacao = "Baixos sinais de exaustão ocupacional. Continue mantendo seus hábitos de autocuidado."
            rec = "Manutenção de hábitos saudáveis e prática regular de atividade física."
        elif score_total <= 20:
            classificacao = "Atenção";        emoji = "🟡"; css = "result-atencao"
            interpretacao = "Sinais moderados de fadiga ocupacional. Atenção às estratégias de recuperação."
            rec = "Pausas ativas, estratégias de recuperação e início de programa de exercício físico supervisionado."
        elif score_total <= 30:
            classificacao = "Alto risco";    emoji = "🟠"; css = "result-alto"
            interpretacao = "Importantes sinais de exaustão. Intervenção estruturada é recomendada."
            rec = "Programa de exercício físico supervisionado, estratégias de recuperação e acompanhamento contínuo."
        else:
            classificacao = "Risco elevado"; emoji = "🔴"; css = "result-elevado"
            interpretacao = "Elevado risco psicofisiológico. Avaliação profissional especializada é indicada."
            rec = "Avaliação profissional urgente. Suporte ocupacional e recuperação psicofisiológica imediata."

        dados = {
            "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nome": nome, "email": email, "setor": setor, "cargo": cargo, "idade": idade,
            "pontuacoes":   pts,
            "score_total":  score_total,
            "classificacao": f"{emoji} {classificacao}",
            "fadiga": fadiga, "emocional": emocional, "recuperacao": recuperacao
        }

        with st.spinner("Registrando suas respostas..."):
            sucesso = salvar_resposta(dados)

        st.markdown("---")

        st.markdown(f"""
        <div class="result {css}">
            <h2>{score_total}/40</h2>
            <h3>{emoji} {classificacao}</h3>
            <p>{interpretacao}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        col1.metric("Fadiga Física",       f"{fadiga}/16")
        col2.metric("Exaustão Emocional",  f"{emocional}/12")
        col3.metric("Recuperação/Saúde",   f"{recuperacao}/12")

        st.markdown(f"""
        <div class="section" style="margin-top:20px">
            <div class="section-title">💡 Recomendação</div>
            <p style="color:#999; font-size:0.9rem; line-height:1.7; margin:0">{rec}</p>
        </div>
        """, unsafe_allow_html=True)

        if sucesso:
            st.success("✅ Respostas registradas com sucesso. Obrigado pela participação.")
        else:
            st.warning("⚠️ Não foi possível salvar. Entre em contato com o RH.")

# ── RODAPÉ ────────────────────────────────────────────────────
st.markdown("""
<div class="rodape">
    MIND IN FIT &nbsp;·&nbsp; Triagem de Bem-Estar Ocupacional &nbsp;·&nbsp; Baseado no Copenhagen Burnout Inventory (CBI)
</div>
""", unsafe_allow_html=True)
