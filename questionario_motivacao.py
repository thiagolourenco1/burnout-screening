import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import base64, os, random

st.set_page_config(
    page_title="Mind In Fit | Motivação para Atividade Física",
    page_icon="💪",
    layout="centered"
)

def get_logo_b64():
    p = os.path.join(os.path.dirname(__file__), "logo_mindinfit.jpeg")
    if os.path.exists(p):
        with open(p, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_b64()
logo_tag = f'<img src="data:image/jpeg;base64,{logo_b64}" style="height:48px;object-fit:contain;display:block;" alt="Mind In Fit">' if logo_b64 else '<span style="color:#E8470A;font-weight:900;font-size:1.6rem">MIND IN FIT</span>'

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700;900&family=Barlow:wght@300;400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"]{font-family:'Barlow',sans-serif;background:#000 !important;color:#fff;}
[data-testid="stAppViewContainer"],[data-testid="stHeader"],[data-testid="block-container"],.stApp,.main{background:#000 !important;}

.topbar{display:flex;align-items:center;justify-content:space-between;padding:20px 0 18px;border-bottom:1px solid #1a1a1a;margin-bottom:48px;}
.topbar-right{font-family:'Barlow Condensed',sans-serif;font-size:.65rem;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:#555;line-height:1.5;text-align:right;}
.topbar-right span{color:#E8470A;display:block;}

.hero{margin-bottom:40px;padding:36px 0 32px;border-bottom:1px solid #111;}
.hero-label{font-family:'Barlow Condensed',sans-serif;font-size:.65rem;font-weight:700;letter-spacing:.25em;text-transform:uppercase;color:#E8470A;margin-bottom:14px;}
.hero-title{font-family:'Barlow Condensed',sans-serif;font-size:clamp(2.2rem,5vw,3.2rem);font-weight:900;line-height:1;color:#fff;margin-bottom:16px;}
.hero-sub{font-size:.9rem;font-weight:300;color:#888;line-height:1.7;}
.hero-sub strong{color:#fff;font-weight:500;}

.pill{display:inline-flex;align-items:center;gap:6px;background:#111;border:1px solid #222;border-radius:100px;padding:5px 14px;font-size:.72rem;font-weight:500;color:#888;margin-bottom:28px;}
.pill-dot{width:6px;height:6px;border-radius:50%;background:#E8470A;}

.divider{height:1px;background:#111;margin:32px 0;}

.instrucao{background:#0a0a0a;border:1px solid #1e1e1e;border-left:3px solid #E8470A;border-radius:8px;padding:16px 20px;margin-bottom:32px;}

.aviso{display:flex;gap:12px;align-items:flex-start;background:#0a0a0a;border:1px solid #1e1e1e;border-left:3px solid #E8470A;border-radius:8px;padding:14px 16px;font-size:.8rem;color:#666 !important;line-height:1.6;margin-top:32px;}
.aviso strong{color:#aaa !important;}

.stButton>button{background:#E8470A !important;color:#fff !important;border:none !important;border-radius:8px !important;padding:13px 28px !important;font-family:'Barlow Condensed',sans-serif !important;font-size:.95rem !important;font-weight:700 !important;letter-spacing:.1em !important;text-transform:uppercase !important;width:100% !important;height:auto !important;transition:all .2s !important;margin-top:8px !important;}
.stButton>button:hover{background:#c93c08 !important;}

.stTextInput>div>div>input,.stNumberInput>div>div>input{background:#0a0a0a !important;border:1px solid #1e1e1e !important;border-radius:6px !important;color:#fff !important;}
.stTextInput>div>div>input:focus{border-color:#E8470A !important;}
.stTextInput label,.stNumberInput label{color:#555 !important;font-size:.75rem !important;letter-spacing:.08em !important;text-transform:uppercase !important;}

p,label,span,div{color:#fff !important;}
.stRadio label{font-size:.88rem !important;}
.stRadio [data-testid="stMarkdownContainer"] p{color:#fff !important;font-size:.92rem !important;}

.result-wrap{border-radius:12px;padding:32px;text-align:center;margin:24px 0;background:linear-gradient(135deg,#0a0a0a,#111);border:1px solid #E8470A33;}

.foot{text-align:center;padding:40px 0 20px;font-size:.7rem;color:#333 !important;letter-spacing:.08em;border-top:1px solid #111;margin-top:48px;}
footer{visibility:hidden;}
div[data-testid="stSidebar"]{display:none;}
</style>
""", unsafe_allow_html=True)

# ── GOOGLE SHEETS ─────────────────────────────────────────────
@st.cache_resource
def conectar_sheets():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Erro: {e}"); return None

def salvar_resposta(dados):
    client = conectar_sheets()
    if not client: return False
    try:
        sp = client.open_by_key(st.secrets["sheet_id"])
        try:
            aba = sp.worksheet("motivacao")
        except:
            aba = sp.add_worksheet("motivacao", 1000, 40)
            aba.append_row([
                "timestamp","nome","email","setor","cargo","idade",
                "p1_q1","p1_q2","p1_q3","p1_q4",   # psicológico
                "p2_q1","p2_q2","p2_q3","p2_q4",   # interpessoal
                "p3_q1","p3_q2","p3_q3","p3_q4",   # saúde
                "p4_q1","p4_q2","p4_q3","p4_q4",   # estético
                "p5_q1","p5_q2","p5_q3","p5_q4",   # condição física
                "media_psicologico","media_interpessoal","media_saude",
                "media_estetico","media_condicao",
                "sdt_desmotivado","sdt_reg_externa","sdt_reg_introjetada",
                "sdt_reg_identificacao","sdt_reg_integrada","sdt_motivacao_intrinseca",
                "estagio_dominante"
            ])
        aba.append_row([
            dados["timestamp"],dados["nome"],dados["email"],
            dados["setor"],dados["cargo"],dados["idade"],
            *dados["respostas_ordenadas"],
            dados["m_psico"],dados["m_inter"],dados["m_saude"],
            dados["m_est"],dados["m_cond"],
            dados["sdt_desm"],dados["sdt_ext"],dados["sdt_intro"],
            dados["sdt_ident"],dados["sdt_integ"],dados["sdt_intr"],
            dados["estagio_dom"]
        ])
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}"); return False

# ── PERGUNTAS COM PILAR MAPEADO ───────────────────────────────
# Cada item: (pilar_index 0-4, texto)
# Pilares: 0=Psicológico, 1=Interpessoal, 2=Saúde, 3=Estético, 4=Condição
PERGUNTAS_ORIGINAL = [
    (0, "Para ajudar a controlar o estresse"),
    (0, "Para ter meu tempo para pensar"),
    (0, "Para me sentir bem"),
    (0, "Porque eu gosto da sensação de me exercitar"),
    (1, "Para demonstrar aos outros meu valor"),
    (1, "Para passar tempo com meus amigos"),
    (1, "Para conhecer pessoas"),
    (1, "Para aproveitar as experiências de se exercitar"),
    (2, "Para prevenir doenças"),
    (2, "Porque meu médico aconselhou"),
    (2, "Para ter um corpo saudável"),
    (2, "Para me ajudar a recuperar de lesões ou dores"),
    (3, "Para parecer mais jovem"),
    (3, "Para melhorar minha aparência"),
    (3, "Porque eu quero manter uma boa saúde"),
    (3, "Para me dar desafios pessoais para enfrentar"),
    (4, "Para aumentar minha força física"),
    (4, "Para me tornar mais ágil / forte / resistente"),
    (4, "Para me dar metas para trabalhar em direção a algo"),
    (4, "Para desenvolver habilidades"),
]

ESCALA = {"1 — Nunca":1,"2 — Raramente":2,"3 — Às vezes":3,"4 — Frequentemente":4,"5 — Sempre":5}

# Embaralhar as perguntas — ordem fixa por sessão usando seed
if "ordem" not in st.session_state:
    indices = list(range(len(PERGUNTAS_ORIGINAL)))
    random.shuffle(indices)
    st.session_state.ordem = indices

PERGUNTAS_EMBARALHADAS = [PERGUNTAS_ORIGINAL[i] for i in st.session_state.ordem]

# ── TOPBAR ─────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
    {logo_tag}
    <div class="topbar-right">
        <span>MIND IN FIT</span>
        Motivação para Atividade Física
    </div>
</div>
""", unsafe_allow_html=True)

# ── HERO ───────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="pill"><div class="pill-dot"></div>Teoria da Autodeterminação · SDT</div>
    <div class="hero-label">Questionário de Motivação</div>
    <div class="hero-title">Por que você se<br>exercita?</div>
    <p class="hero-sub">
        Responda com honestidade — não há respostas certas ou erradas.<br>
        Suas respostas são <strong>confidenciais</strong> e levam cerca de <strong>5 minutos</strong>.
    </p>
</div>
""", unsafe_allow_html=True)

# ── IDENTIFICAÇÃO ──────────────────────────────────────────────
st.markdown('<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:.6rem;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:#E8470A;margin-bottom:6px">Etapa 01</div>', unsafe_allow_html=True)
st.markdown('<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.25rem;font-weight:700;color:#fff;margin-bottom:24px;padding-bottom:12px;border-bottom:1px solid #111">Identificação</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    nome  = st.text_input("Nome completo")
    email = st.text_input("E-mail corporativo")
    setor = st.text_input("Setor / Departamento")
with c2:
    cargo = st.text_input("Cargo")
    idade = st.number_input("Idade", min_value=18, max_value=70, value=30)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── INSTRUÇÃO ──────────────────────────────────────────────────
st.markdown("""
<div class="instrucao">
    <p style="font-family:'Barlow Condensed',sans-serif;font-size:.65rem;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:#E8470A;margin-bottom:8px">Instruções</p>
    <p style="font-size:.88rem;color:#aaa;line-height:1.7;margin:0">
        Para cada afirmação abaixo, indique <strong style="color:#fff">com que frequência</strong>
        cada motivo te leva a praticar ou buscar a atividade física, usando a escala de
        <strong style="color:#fff">1 (Nunca)</strong> a <strong style="color:#fff">5 (Sempre)</strong>.
    </p>
</div>
""", unsafe_allow_html=True)

# ── QUESTIONÁRIO ───────────────────────────────────────────────
st.markdown('<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:.6rem;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:#E8470A;margin-bottom:6px">Etapa 02</div>', unsafe_allow_html=True)
st.markdown('<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:1.25rem;font-weight:700;color:#fff;margin-bottom:24px;padding-bottom:12px;border-bottom:1px solid #111">Questionário</div>', unsafe_allow_html=True)

respostas_embaralhadas = []
for n, (pilar_idx, pergunta) in enumerate(PERGUNTAS_EMBARALHADAS, 1):
    r = st.radio(
        f"{n}. {pergunta}",
        options=list(ESCALA.keys()),
        horizontal=True,
        key=f"mq{n}",
        index=None
    )
    respostas_embaralhadas.append((pilar_idx, r))
    if n < len(PERGUNTAS_EMBARALHADAS):
        st.markdown('<div style="height:1px;background:#0a0a0a;margin:8px 0"></div>', unsafe_allow_html=True)

# ── AVISO ──────────────────────────────────────────────────────
st.markdown("""
<div class="aviso">
    <span style="font-size:1rem">⚠️</span>
    <span>Suas respostas são <strong>confidenciais</strong> e serão utilizadas exclusivamente
    para personalizar estratégias de incentivo à atividade física. Tratamento conforme a <strong>LGPD</strong>.</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── ENVIO ──────────────────────────────────────────────────────
if st.button("ENVIAR RESPOSTAS"):
    if not all([nome.strip(), email.strip(), setor.strip(), cargo.strip()]):
        st.error("Preencha todos os campos obrigatórios.")
    elif any(r is None for _, r in respostas_embaralhadas):
        st.error("Responda todas as perguntas antes de enviar.")
    else:
        # Reorganizar respostas na ordem original dos pilares
        pts_por_pilar = {0:[], 1:[], 2:[], 3:[], 4:[]}
        for pilar_idx, resp in respostas_embaralhadas:
            pts_por_pilar[pilar_idx].append(ESCALA[resp])

        # Garantir ordem correta para salvar
        respostas_ordenadas = (
            pts_por_pilar[0] +  # psicológico
            pts_por_pilar[1] +  # interpessoal
            pts_por_pilar[2] +  # saúde
            pts_por_pilar[3] +  # estético
            pts_por_pilar[4]    # condição física
        )

        # Médias por pilar
        m_psico = sum(pts_por_pilar[0]) / 4
        m_inter = sum(pts_por_pilar[1]) / 4
        m_saude = sum(pts_por_pilar[2]) / 4
        m_est   = sum(pts_por_pilar[3]) / 4
        m_cond  = sum(pts_por_pilar[4]) / 4

        # Pilar dominante
        pilar_dom_raw = max(
            {"Psicológico":m_psico,"Interpessoal":m_inter,"Saúde":m_saude,"Estético":m_est,"Condição":m_cond},
            key=lambda k: {"Psicológico":m_psico,"Interpessoal":m_inter,"Saúde":m_saude,"Estético":m_est,"Condição":m_cond}[k]
        )

        # Cálculo SDT
        sdt_desm  = round(m_saude, 2) if pilar_dom_raw == "Saúde" else round(m_saude * 0.5, 2)
        sdt_ext   = round((m_saude + m_inter + m_psico) / 3, 2)
        sdt_intro = round((m_saude + m_est) / 2, 2)
        sdt_ident = round((m_saude + m_cond) / 2, 2)
        sdt_integ = round(m_psico, 2)
        sdt_intr  = round((m_psico + m_cond) / 2, 2)

        sdt_scores = {
            "Desmotivado":           sdt_desm,
            "Regulação Externa":     sdt_ext,
            "Regulação Introjetada": sdt_intro,
            "Regulação Identificada":sdt_ident,
            "Regulação Integrada":   sdt_integ,
            "Motivação Intrínseca":  sdt_intr,
        }
        estagio_dom = max(sdt_scores, key=sdt_scores.get)

        def fmt(v): return str(round(float(v), 2)).replace(",", ".")

        ok = salvar_resposta({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nome":nome,"email":email,"setor":setor,"cargo":cargo,"idade":idade,
            "respostas_ordenadas": respostas_ordenadas,
            "m_psico":fmt(m_psico),"m_inter":fmt(m_inter),
            "m_saude":fmt(m_saude),"m_est":fmt(m_est),"m_cond":fmt(m_cond),
            "sdt_desm":fmt(sdt_desm),"sdt_ext":fmt(sdt_ext),"sdt_intro":fmt(sdt_intro),
            "sdt_ident":fmt(sdt_ident),"sdt_integ":fmt(sdt_integ),"sdt_intr":fmt(sdt_intr),
            "estagio_dom":estagio_dom
        })

        # Tela de confirmação simples — sem revelar análise
        st.markdown("""
        <div class="result-wrap">
            <div style="font-size:3rem;margin-bottom:12px">✅</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.6rem;font-weight:900;color:#fff;margin-bottom:8px">Respostas Enviadas!</div>
            <p style="font-size:.9rem;color:#888;margin:0;line-height:1.7">
                Obrigado pela participação.<br>
                Sua avaliação foi registrada com sucesso e será analisada pela equipe Mind In Fit.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if not ok:
            st.warning("⚠️ Não foi possível salvar. Entre em contato com o RH.")

# ── FOOTER ─────────────────────────────────────────────────────
st.markdown("""
<div class="foot">
    MIND IN FIT &nbsp;·&nbsp; Avaliação de Motivação para Atividade Física &nbsp;·&nbsp; Uso exclusivo corporativo
</div>
""", unsafe_allow_html=True)
