import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import json
import os

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Triagem de Bem-Estar Ocupacional",
    page_icon="🌿",
    layout="centered"
)

# =========================
# ESTILO VISUAL
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main {
    background-color: #F5F2EE;
}

h1, h2, h3 {
    font-family: 'DM Serif Display', serif;
    color: #1C1917;
}

/* Cabeçalho hero */
.hero {
    background: linear-gradient(135deg, #1C1917 0%, #292524 60%, #3D2F26 100%);
    border-radius: 20px;
    padding: 48px 40px;
    margin-bottom: 32px;
    color: white;
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(250,204,21,0.08);
}

.hero h1 {
    color: white;
    font-size: 2rem;
    margin-bottom: 8px;
}

.hero p {
    color: #D6D3D1;
    font-size: 0.95rem;
    margin: 0;
}

.hero .badge {
    display: inline-block;
    background: rgba(250,204,21,0.15);
    border: 1px solid rgba(250,204,21,0.3);
    color: #FDE68A;
    font-size: 0.75rem;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 16px;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Cards de seção */
.section-card {
    background: white;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
    border: 1px solid #E7E5E4;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* Resultado */
.result-card {
    border-radius: 20px;
    padding: 36px;
    margin: 24px 0;
    text-align: center;
}

.result-baixo  { background: linear-gradient(135deg, #DCFCE7, #BBF7D0); border: 2px solid #86EFAC; }
.result-atencao { background: linear-gradient(135deg, #FEF9C3, #FEF08A); border: 2px solid #FDE047; }
.result-alto   { background: linear-gradient(135deg, #FFEDD5, #FED7AA); border: 2px solid #FDBA74; }
.result-elevado { background: linear-gradient(135deg, #FEE2E2, #FECACA); border: 2px solid #FCA5A5; }

.result-card h2 { font-size: 2.5rem; margin-bottom: 4px; }
.result-card h3 { font-size: 1.25rem; margin-bottom: 8px; }
.result-card p  { font-size: 0.95rem; margin: 0; }

/* Barra de domínio */
.dominio-bar {
    background: #F5F2EE;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Botão principal */
.stButton>button {
    background: linear-gradient(135deg, #1C1917, #3D2F26) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 32px !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    font-family: 'DM Sans', sans-serif !important;
    width: 100% !important;
    height: auto !important;
    transition: all 0.2s !important;
    letter-spacing: 0.02em !important;
}

.stButton>button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* Radio buttons */
.stRadio > label { font-size: 0.95rem !important; }
.stRadio > div { gap: 4px !important; }

/* Aviso de rodapé */
.aviso {
    background: #FEF3C7;
    border-left: 4px solid #F59E0B;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    font-size: 0.85rem;
    color: #78350F;
    margin-top: 24px;
}

/* Progress */
.progress-info {
    text-align: right;
    font-size: 0.8rem;
    color: #78716C;
    margin-bottom: 16px;
}

div[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)


# =========================
# CONEXÃO GOOGLE SHEETS
# =========================
@st.cache_resource
def conectar_sheets():
    """Conecta ao Google Sheets usando credenciais do secrets.toml"""
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        # As credenciais ficam em .streamlit/secrets.toml
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Erro ao conectar ao Google Sheets: {e}")
        return None


def salvar_resposta(dados: dict):
    """Salva uma linha de resposta na planilha"""
    client = conectar_sheets()
    if client is None:
        return False
    try:
        sheet_id = st.secrets["sheet_id"]
        spreadsheet = client.open_by_key(sheet_id)

        # Aba 'respostas' — cria se não existir
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


# =========================
# ESCALA DE RESPOSTAS
# =========================
ESCALA = {
    "Nunca": 0,
    "Raramente": 1,
    "Às vezes": 2,
    "Frequentemente": 3,
    "Sempre": 4
}

# =========================
# PERGUNTAS POR DOMÍNIO
# =========================
DOMINIOS = {
    "🏋️ Fadiga Física": [
        "Você se sente cansado(a) ao acordar para trabalhar?",
        "Você sente esgotamento físico ao final do expediente?",
        "Você sente que seu trabalho drena sua energia?",
        "Você percebe dificuldade de recuperação mesmo após descanso?",
    ],
    "😔 Exaustão Emocional": [
        "Você sente exaustão emocional relacionada ao trabalho?",
        "Você percebe queda de motivação nas tarefas diárias?",
        "Você sente dificuldade de concentração durante o trabalho?",
    ],
    "💤 Recuperação e Saúde": [
        "Você sente que o trabalho afeta negativamente sua saúde?",
        "Você percebe piora do sono nas últimas semanas?",
        "Você sente redução da disposição física geral?",
    ]
}

# =========================
# HERO
# =========================
st.markdown("""
<div class="hero">
    <div class="badge">🌿 Bem-Estar Ocupacional</div>
    <h1>Como você está?</h1>
    <p>Triagem de risco psicofisiológico baseada no Copenhagen Burnout Inventory (CBI).<br>
    Suas respostas são confidenciais e levam cerca de <strong style="color:white">3 minutos</strong>.</p>
</div>
""", unsafe_allow_html=True)

# =========================
# DADOS DO COLABORADOR
# =========================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### 👤 Seus dados")

col1, col2 = st.columns(2)
with col1:
    nome  = st.text_input("Nome completo *")
    email = st.text_input("E-mail corporativo *")
    setor = st.text_input("Setor / Departamento *")
with col2:
    cargo = st.text_input("Cargo *")
    idade = st.number_input("Idade *", min_value=18, max_value=70, value=30)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# QUESTIONÁRIO
# =========================
st.markdown("### 📋 Questionário")
st.markdown("Responda com honestidade. Não há respostas certas ou erradas.")

pontuacoes = []
num_pergunta = 1
total_perguntas = sum(len(v) for v in DOMINIOS.values())

for dominio, perguntas in DOMINIOS.items():
    st.markdown(f'<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f"**{dominio}**")
    for pergunta in perguntas:
        resposta = st.radio(
            f"{num_pergunta}. {pergunta}",
            options=list(ESCALA.keys()),
            horizontal=True,
            key=f"q{num_pergunta}",
            index=None  # força o usuário a escolher
        )
        pontuacoes.append(resposta)
        num_pergunta += 1
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# AVISO LGPD
# =========================
st.markdown("""
<div class="aviso">
    ⚠️ <strong>Aviso:</strong> Esta ferramenta é de triagem e <strong>não fornece diagnóstico clínico</strong>.
    Os dados coletados são utilizados exclusivamente para apoio a ações de saúde ocupacional.
    Tratamento conforme a LGPD.
</div>
""", unsafe_allow_html=True)

# =========================
# BOTÃO ENVIAR
# =========================
st.markdown("<br>", unsafe_allow_html=True)

if st.button("✅ Enviar minhas respostas"):

    # Validações
    campos_vazios = not all([nome.strip(), email.strip(), setor.strip(), cargo.strip()])
    respostas_incompletas = any(r is None for r in pontuacoes)

    if campos_vazios:
        st.error("⚠️ Preencha todos os campos obrigatórios (Nome, E-mail, Setor, Cargo).")
    elif respostas_incompletas:
        st.error("⚠️ Responda todas as perguntas do questionário antes de enviar.")
    else:
        # Converter respostas para pontuações
        pts = [ESCALA[r] for r in pontuacoes]

        score_total = sum(pts)
        fadiga      = sum(pts[0:4])
        emocional   = sum(pts[4:7])
        recuperacao = sum(pts[7:10])

        # Classificação
        if score_total <= 10:
            classificacao = "Baixo risco"
            emoji_class   = "🟢"
            css_class     = "result-baixo"
            interpretacao = "Baixos sinais de exaustão ocupacional. Continue mantendo seus hábitos de autocuidado."
        elif score_total <= 20:
            classificacao = "Atenção"
            emoji_class   = "🟡"
            css_class     = "result-atencao"
            interpretacao = "Sinais moderados de fadiga ocupacional. Recomenda-se atenção às estratégias de recuperação."
        elif score_total <= 30:
            classificacao = "Alto risco"
            emoji_class   = "🟠"
            css_class     = "result-alto"
            interpretacao = "Importantes sinais de exaustão. Intervenção estruturada com exercício físico é recomendada."
        else:
            classificacao = "Risco elevado"
            emoji_class   = "🔴"
            css_class     = "result-elevado"
            interpretacao = "Elevado risco psicofisiológico. Avaliação profissional especializada é fortemente indicada."

        # Salvar no Google Sheets
        dados = {
            "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nome":         nome,
            "email":        email,
            "setor":        setor,
            "cargo":        cargo,
            "idade":        idade,
            "pontuacoes":   pts,
            "score_total":  score_total,
            "classificacao": f"{emoji_class} {classificacao}",
            "fadiga":       fadiga,
            "emocional":    emocional,
            "recuperacao":  recuperacao
        }

        with st.spinner("Salvando suas respostas..."):
            sucesso = salvar_resposta(dados)

        st.markdown("---")

        # Resultado visual
        st.markdown(f"""
        <div class="result-card {css_class}">
            <h2>{emoji_class}</h2>
            <h3>{classificacao}</h3>
            <p style="font-size:1.5rem; font-weight:600; margin:8px 0">Score: {score_total}/40</p>
            <p>{interpretacao}</p>
        </div>
        """, unsafe_allow_html=True)

        # Domínios
        st.markdown("#### 🔬 Análise por Domínio")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("🏋️ Fadiga Física",       f"{fadiga}/16")
        with col2: st.metric("😔 Exaustão Emocional",   f"{emocional}/12")
        with col3: st.metric("💤 Recuperação e Saúde",  f"{recuperacao}/12")

        # Recomendação
        st.markdown("#### 💡 Recomendação")
        if score_total <= 10:
            st.success("Mantenha hábitos saudáveis, pratique atividade física regularmente e faça monitoramento periódico.")
        elif score_total <= 20:
            st.warning("Implemente pausas ativas, estratégias de recuperação e incentive a prática regular de exercício físico.")
        elif score_total <= 30:
            st.warning("Recomenda-se exercício físico supervisionado, estratégias de recuperação e acompanhamento contínuo.")
        else:
            st.error("Procure avaliação profissional especializada. Implemente suporte ocupacional e recuperação psicofisiológica.")

        if sucesso:
            st.success("✅ Respostas enviadas com sucesso! Obrigado pela participação.")
        else:
            st.warning("⚠️ Não foi possível salvar no banco de dados. Entre em contato com o RH.")

# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.caption("Triagem de bem-estar ocupacional • Baseado no Copenhagen Burnout Inventory (CBI) • Uso exclusivo corporativo")
