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

def get_logo_b64():
    p = os.path.join(os.path.dirname(__file__), "logo_mindinfit.jpeg")
    if os.path.exists(p):
        with open(p, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_b64()
logo_tag = f'<img src="data:image/jpeg;base64,{logo_b64}" style="height:48px;object-fit:contain;" alt="Mind In Fit">' if logo_b64 else '<span style="font-family:Barlow Condensed,sans-serif;font-size:1.6rem;font-weight:900;color:#E8470A;letter-spacing:.05em">MIND IN FIT</span>'

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700;900&family=Barlow:ital,wght@0,300;0,400;0,500;1,300&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    background: #000 !important;
    color: #fff;
}

[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
[data-testid="block-container"],
.stApp, .main { background: #000 !important; }

/* ─── TOPBAR ─── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 0 18px;
    border-bottom: 1px solid #1a1a1a;
    margin-bottom: 48px;
}
.topbar-right {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: .65rem;
    font-weight: 700;
    letter-spacing: .22em;
    text-transform: uppercase;
    color: #555;
    line-height: 1.5;
    text-align: right;
}
.topbar-right span { color: #E8470A; display: block; }

/* ─── HERO ─── */
.hero {
    margin-bottom: 40px;
    padding: 36px 0 32px;
    border-bottom: 1px solid #111;
}
.hero-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: .65rem;
    font-weight: 700;
    letter-spacing: .25em;
    text-transform: uppercase;
    color: #E8470A;
    margin-bottom: 14px;
}
.hero-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: clamp(2.4rem, 5vw, 3.6rem);
    font-weight: 900;
    line-height: 1;
    color: #fff;
    margin-bottom: 16px;
    letter-spacing: -.01em;
}
.hero-sub {
    font-size: .9rem;
    font-weight: 300;
    color: #888;
    line-height: 1.7;
    max-width: 520px;
}
.hero-sub strong { color: #fff; font-weight: 500; }

/* ─── PILL BADGE ─── */
.pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #111;
    border: 1px solid #222;
    border-radius: 100px;
    padding: 5px 14px;
    font-size: .72rem;
    font-weight: 500;
    color: #888;
    margin-bottom: 28px;
}
.pill-dot { width: 6px; height: 6px; border-radius: 50%; background: #E8470A; }

/* ─── SECTION ─── */
.sec-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: .6rem;
    font-weight: 700;
    letter-spacing: .28em;
    text-transform: uppercase;
    color: #E8470A;
    margin-bottom: 6px;
}
.sec-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 1px solid #111;
}

/* ─── INPUTS ─── */
.stTextInput label, .stNumberInput label,
.stTextInput > label, .stNumberInput > label { color: #555 !important; font-size: .75rem !important; letter-spacing: .08em !important; text-transform: uppercase !important; font-family: 'Barlow Condensed', sans-serif !important; }

.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #0a0a0a !important;
    border: 1px solid #1e1e1e !important;
    border-radius: 6px !important;
    color: #fff !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: .9rem !important;
    padding: 10px 14px !important;
    transition: border-color .15s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #E8470A !important;
    box-shadow: 0 0 0 2px rgba(232,71,10,.12) !important;
}

/* ─── RADIO ─── */
p, label, span, div { color: #fff !important; }
.stRadio > div { gap: 2px !important; }
.stRadio label { font-size: .88rem !important; font-weight: 400 !important; }
.stRadio [data-testid="stMarkdownContainer"] p { color: #fff !important; font-size: .92rem !important; }

/* ─── DIVIDER ─── */
.divider { height: 1px; background: #111; margin: 36px 0; }

/* ─── AVISO ─── */
.aviso {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    background: #0a0a0a;
    border: 1px solid #1e1e1e;
    border-left: 3px solid #E8470A;
    border-radius: 8px;
    padding: 14px 16px;
    font-size: .8rem;
    color: #666 !important;
    line-height: 1.6;
    margin-top: 32px;
}
.aviso strong { color: #aaa !important; }

/* ─── BOTÃO ─── */
.stButton > button {
    background: #E8470A !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 13px 28px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: .95rem !important;
    font-weight: 700 !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    height: auto !important;
    transition: all .2s !important;
    margin-top: 8px !important;
}
.stButton > button:hover { background: #c93c08 !important; transform: translateY(-1px) !important; }

/* ─── RESULT ─── */
.result-wrap {
    border-radius: 12px;
    padding: 36px;
    text-align: center;
    margin: 28px 0;
    position: relative;
    overflow: hidden;
}
.result-baixo   { background: linear-gradient(135deg,#001a0a,#002210); border: 1px solid #00441a; }
.result-atencao { background: linear-gradient(135deg,#1a1500,#221c00); border: 1px solid #443500; }
.result-alto    { background: linear-gradient(135deg,#1a0800,#220e00); border: 1px solid #441c00; }
.result-elevado { background: linear-gradient(135deg,#1a0000,#220000); border: 1px solid #440000; }
.result-score {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 4rem;
    font-weight: 900;
    line-height: 1;
    margin-bottom: 4px;
}
.result-class {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: .15em;
    text-transform: uppercase;
    margin-bottom: 12px;
}
.result-desc { font-size: .88rem; font-weight: 300; color: #aaa !important; }

/* ─── REC BOX ─── */
.rec-box {
    background: #0a0a0a;
    border: 1px solid #1e1e1e;
    border-radius: 10px;
    padding: 20px 24px;
    margin-top: 20px;
}
.rec-box .rec-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: .6rem;
    font-weight: 700;
    letter-spacing: .25em;
    text-transform: uppercase;
    color: #E8470A !important;
    margin-bottom: 8px;
}
.rec-box p { font-size: .88rem; color: #aaa !important; line-height: 1.7; }

/* ─── FOOTER ─── */
.foot {
    text-align: center;
    padding: 40px 0 20px;
    font-size: .7rem;
    color: #333 !important;
    letter-spacing: .08em;
    border-top: 1px solid #111;
    margin-top: 48px;
}

footer { visibility: hidden; }
div[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── GOOGLE SHEETS ────────────────────────────────────────────
@st.cache_resource
def conectar_sheets():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Erro ao conectar: {e}"); return None

def salvar_resposta(dados):
    client = conectar_sheets()
    if not client: return False
    try:
        sp = client.open_by_key(st.secrets["sheet_id"])
        try: aba = sp.worksheet("respostas")
        except:
            aba = sp.add_worksheet("respostas", 1000, 30)
            aba.append_row(["timestamp","nome","email","setor","cargo","idade",
                            "q1","q2","q3","q4","q5","q6","q7","q8","q9","q10",
                            "score_total","classificacao","fadiga_fisica","exaustao_emocional","recuperacao_saude"])
        aba.append_row([dados["timestamp"],dados["nome"],dados["email"],
                        dados["setor"],dados["cargo"],dados["idade"],
                        *dados["pts"],dados["score"],dados["class_str"],
                        dados["fadiga"],dados["emocional"],dados["recuperacao"]])
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}"); return False

# ── CONTEÚDO ─────────────────────────────────────────────────
ESCALA = {"Nunca":0,"Raramente":1,"Às vezes":2,"Frequentemente":3,"Sempre":4}
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

# ── TOPBAR ───────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
    {logo_tag}
    <div class="topbar-right">
        <span>MIND IN FIT</span>
        Bem-Estar Ocupacional
    </div>
</div>
""", unsafe_allow_html=True)

# ── HERO ─────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="pill"><div class="pill-dot"></div>Copenhagen Burnout Inventory · CBI</div>
    <div class="hero-label">Avaliação Psicofisiológica</div>
    <div class="hero-title">Como você<br>está hoje?</div>
    <p class="hero-sub">
        Triagem de risco ocupacional baseada em evidências científicas.<br>
        Suas respostas são <strong>confidenciais</strong> e levam cerca de <strong>3 minutos</strong>.
    </p>
</div>
""", unsafe_allow_html=True)

# ── DADOS ────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Etapa 01</div><div class="sec-title">Identificação</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    nome  = st.text_input("Nome completo")
    email = st.text_input("E-mail corporativo")
    setor = st.text_input("Setor / Departamento")
with c2:
    cargo = st.text_input("Cargo")
    idade = st.number_input("Idade", min_value=18, max_value=70, value=30)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── QUESTIONÁRIO ─────────────────────────────────────────────
st.markdown('<div class="sec-label">Etapa 02</div><div class="sec-title">Questionário</div>', unsafe_allow_html=True)

pontuacoes = []
n = 1
for dominio, perguntas in DOMINIOS.items():
    st.markdown(f'<p style="font-family:Barlow Condensed,sans-serif;font-size:.65rem;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:#E8470A;margin:28px 0 16px">{dominio}</p>', unsafe_allow_html=True)
    for pergunta in perguntas:
        r = st.radio(f"{n}. {pergunta}", list(ESCALA.keys()), horizontal=True, key=f"q{n}", index=None)
        pontuacoes.append(r)
        n += 1
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── AVISO ────────────────────────────────────────────────────
st.markdown("""
<div class="aviso">
    <span style="font-size:1rem">⚠️</span>
    <span>Esta ferramenta é de <strong>triagem</strong> e não fornece diagnóstico clínico.
    Dados utilizados exclusivamente para ações de saúde ocupacional. Tratamento conforme a <strong>LGPD</strong>.</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── ENVIO ────────────────────────────────────────────────────
if st.button("ENVIAR RESPOSTAS"):
    if not all([nome.strip(), email.strip(), setor.strip(), cargo.strip()]):
        st.error("Preencha todos os campos obrigatórios.")
    elif any(r is None for r in pontuacoes):
        st.error("Responda todas as perguntas antes de enviar.")
    else:
        pts = [ESCALA[r] for r in pontuacoes]
        score     = sum(pts)
        fadiga    = sum(pts[0:4])
        emocional = sum(pts[4:7])
        recuper   = sum(pts[7:10])

        if score <= 10:
            cl="Baixo risco"; em="🟢"; css="result-baixo"
            desc="Baixos sinais de exaustão ocupacional. Continue mantendo seus hábitos de autocuidado."
            rec="Manutenção de hábitos saudáveis e prática regular de atividade física."
            cor="#22C55E"
        elif score <= 20:
            cl="Atenção"; em="🟡"; css="result-atencao"
            desc="Sinais moderados de fadiga. Atenção às estratégias de recuperação."
            rec="Pausas ativas, estratégias de recuperação e início de programa de exercício físico supervisionado."
            cor="#EAB308"
        elif score <= 30:
            cl="Alto risco"; em="🟠"; css="result-alto"
            desc="Importantes sinais de exaustão. Intervenção estruturada é recomendada."
            rec="Programa de exercício físico supervisionado e acompanhamento contínuo."
            cor="#E8470A"
        else:
            cl="Risco elevado"; em="🔴"; css="result-elevado"
            desc="Elevado risco psicofisiológico. Avaliação profissional especializada indicada."
            rec="Avaliação profissional urgente e suporte ocupacional imediato."
            cor="#EF4444"

        ok = salvar_resposta({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nome":nome,"email":email,"setor":setor,"cargo":cargo,"idade":idade,
            "pts":pts,"score":score,"class_str":f"{em} {cl}",
            "fadiga":fadiga,"emocional":emocional,"recuperacao":recuper
        })

        st.markdown(f"""
        <div class="result-wrap {css}">
            <div class="result-score" style="color:{cor}">{score}<span style="font-size:1.8rem;color:#555">/40</span></div>
            <div class="result-class" style="color:{cor}">{em} {cl}</div>
            <p class="result-desc">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Fadiga Física",      f"{fadiga}/16")
        c2.metric("Exaustão Emocional", f"{emocional}/12")
        c3.metric("Recuperação/Saúde",  f"{recuper}/12")

        st.markdown(f"""
        <div class="rec-box">
            <div class="rec-label">💡 Recomendação</div>
            <p>{rec}</p>
        </div>
        """, unsafe_allow_html=True)

        if ok:
            st.success("✅ Respostas registradas. Obrigado pela participação!")
        else:
            st.warning("⚠️ Não foi possível salvar. Entre em contato com o RH.")

# ── FOOTER ───────────────────────────────────────────────────
st.markdown("""
<div class="foot">
    MIND IN FIT &nbsp;·&nbsp; Triagem de Bem-Estar Ocupacional &nbsp;·&nbsp; Baseado no Copenhagen Burnout Inventory (CBI)
</div>
""", unsafe_allow_html=True)
