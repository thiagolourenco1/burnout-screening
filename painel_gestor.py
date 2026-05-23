import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Painel do Gestor — Burnout Screening",
    page_icon="📊",
    layout="wide"
)

# =========================
# ESTILO VISUAL
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main { background-color: #0F0F0F; color: #E8E4DF; }
h1, h2, h3 { font-family: 'DM Serif Display', serif; color: #F5F2EE; }

.login-card {
    background: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-radius: 20px;
    padding: 48px;
    max-width: 420px;
    margin: 80px auto;
    text-align: center;
}

.login-card h2 { font-size: 1.8rem; margin-bottom: 8px; }
.login-card p  { color: #78716C; font-size: 0.9rem; margin-bottom: 32px; }

.kpi-card {
    background: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
}

.kpi-card .valor  { font-size: 2.5rem; font-weight: 700; margin: 8px 0 4px; }
.kpi-card .label  { font-size: 0.8rem; color: #78716C; text-transform: uppercase; letter-spacing: 0.08em; }
.kpi-card .verde  { color: #4ADE80; }
.kpi-card .amarelo { color: #FDE047; }
.kpi-card .laranja { color: #FB923C; }
.kpi-card .vermelho { color: #F87171; }

.table-row {
    background: #1A1A1A;
    border: 1px solid #2A2A2A;
    border-radius: 10px;
    padding: 14px 18px;
    margin: 6px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 0.9rem;
}

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-baixo    { background: #14532D; color: #4ADE80; }
.badge-atencao  { background: #713F12; color: #FDE047; }
.badge-alto     { background: #7C2D12; color: #FB923C; }
.badge-elevado  { background: #7F1D1D; color: #F87171; }

.stButton>button {
    background: #F5F2EE !important;
    color: #0F0F0F !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stTextInput>div>div>input {
    background: #1A1A1A !important;
    border: 1px solid #3A3A3A !important;
    color: #E8E4DF !important;
    border-radius: 10px !important;
}

div[data-testid="stSidebar"] { background: #0F0F0F !important; border-right: 1px solid #1A1A1A; }
</style>
""", unsafe_allow_html=True)


# =========================
# AUTENTICAÇÃO
# =========================
def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.markdown("""
        <div class="login-card">
            <h2>📊 Painel do Gestor</h2>
            <p>Acesso restrito. Insira a senha para continuar.</p>
        </div>
        """, unsafe_allow_html=True)

        col_c = st.columns([1, 2, 1])[1]
        with col_c:
            senha = st.text_input("Senha de acesso", type="password", label_visibility="collapsed",
                                   placeholder="••••••••")
            if st.button("Entrar"):
                if senha == st.secrets.get("senha_gestor", "burnout2025"):
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
        st.stop()

verificar_senha()


# =========================
# CONEXÃO GOOGLE SHEETS
# =========================
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
        st.error(f"Erro ao conectar: {e}")
        return None


@st.cache_data(ttl=120)  # atualiza a cada 2 minutos
def carregar_dados():
    client = conectar_sheets()
    if client is None:
        return pd.DataFrame()
    try:
        sheet_id = st.secrets["sheet_id"]
        spreadsheet = client.open_by_key(sheet_id)
        aba = spreadsheet.worksheet("respostas")
        dados = aba.get_all_records()
        df = pd.DataFrame(dados)
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df["score_total"] = pd.to_numeric(df["score_total"], errors="coerce")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()


def classificar_score(score):
    if score <= 10: return "Baixo risco"
    if score <= 20: return "Atenção"
    if score <= 30: return "Alto risco"
    return "Risco elevado"


def badge_html(classificacao):
    mapa = {
        "Baixo risco":  "badge-baixo",
        "Atenção":      "badge-atencao",
        "Alto risco":   "badge-alto",
        "Risco elevado":"badge-elevado",
    }
    emoji_mapa = {
        "Baixo risco": "🟢", "Atenção": "🟡",
        "Alto risco": "🟠", "Risco elevado": "🔴"
    }
    # Extrai só o texto, removendo emoji do banco
    texto = classificacao.replace("🟢 ","").replace("🟡 ","").replace("🟠 ","").replace("🔴 ","")
    css = mapa.get(texto, "badge-baixo")
    emoji = emoji_mapa.get(texto, "")
    return f'<span class="badge {css}">{emoji} {texto}</span>'


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## 🌿 Burnout Screening")
    st.markdown("---")
    pagina = st.radio(
        "Navegação",
        ["📊 Dashboard", "👥 Colaboradores", "🏢 Por Setor", "📄 Relatório Individual"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    if st.button("🔓 Sair"):
        st.session_state.autenticado = False
        st.rerun()
    st.caption(f"Atualizado: {datetime.now().strftime('%H:%M')}")


# =========================
# CARREGAR DADOS
# =========================
df = carregar_dados()

if df.empty:
    st.title("📊 Painel do Gestor")
    st.info("Nenhuma resposta registrada ainda. Aguarde os colaboradores preencherem o questionário.")
    st.stop()

# Limpar classificação (remover emojis para filtros)
df["class_limpa"] = df["classificacao"].str.replace(r"[🟢🟡🟠🔴] ", "", regex=True).str.strip()

# =========================
# PÁGINA: DASHBOARD
# =========================
if "Dashboard" in pagina:

    st.title("📊 Dashboard Geral")
    st.markdown(f"**{len(df)} respostas** coletadas até agora.")
    st.markdown("---")

    # KPIs
    total       = len(df)
    baixo       = (df["class_limpa"] == "Baixo risco").sum()
    atencao     = (df["class_limpa"] == "Atenção").sum()
    alto        = (df["class_limpa"] == "Alto risco").sum()
    elevado     = (df["class_limpa"] == "Risco elevado").sum()
    media_score = df["score_total"].mean()
    em_risco    = alto + elevado

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f'<div class="kpi-card"><div class="label">Total</div><div class="valor">{total}</div><div class="label">respostas</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="kpi-card"><div class="label">Baixo Risco</div><div class="valor verde">{baixo}</div><div class="label">{baixo/total*100:.0f}%</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="kpi-card"><div class="label">Atenção</div><div class="valor amarelo">{atencao}</div><div class="label">{atencao/total*100:.0f}%</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="kpi-card"><div class="label">Alto Risco</div><div class="valor laranja">{alto}</div><div class="label">{alto/total*100:.0f}%</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="kpi-card"><div class="label">Risco Elevado</div><div class="valor vermelho">{elevado}</div><div class="label">{elevado/total*100:.0f}%</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # Distribuição por classificação
        contagem = df["class_limpa"].value_counts().reset_index()
        contagem.columns = ["Classificação", "Quantidade"]
        ordem = ["Baixo risco", "Atenção", "Alto risco", "Risco elevado"]
        cores = {"Baixo risco": "#4ADE80", "Atenção": "#FDE047", "Alto risco": "#FB923C", "Risco elevado": "#F87171"}
        fig_pizza = px.pie(
            contagem, names="Classificação", values="Quantidade",
            color="Classificação", color_discrete_map=cores,
            title="Distribuição por Nível de Risco",
            hole=0.45
        )
        fig_pizza.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E8E4DF", title_font_size=16
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

    with col_b:
        # Médias por domínio
        medias = {
            "Fadiga Física":      df["fadiga_fisica"].mean(),
            "Exaustão Emocional": df["exaustao_emocional"].mean(),
            "Recup. e Saúde":     df["recuperacao_saude"].mean()
        }
        fig_bar = go.Figure(go.Bar(
            x=list(medias.keys()),
            y=list(medias.values()),
            marker_color=["#FB923C", "#F87171", "#60A5FA"],
            text=[f"{v:.1f}" for v in medias.values()],
            textposition="outside"
        ))
        fig_bar.update_layout(
            title="Média por Domínio",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E8E4DF", title_font_size=16,
            yaxis=dict(gridcolor="#2A2A2A"),
            xaxis=dict(gridcolor="#2A2A2A")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Score ao longo do tempo
    df_tempo = df.copy()
    df_tempo["data"] = df_tempo["timestamp"].dt.date
    media_dia = df_tempo.groupby("data")["score_total"].mean().reset_index()
    fig_linha = px.line(
        media_dia, x="data", y="score_total",
        title="Evolução do Score Médio ao Longo do Tempo",
        markers=True, line_shape="spline"
    )
    fig_linha.update_traces(line_color="#FDE047", marker_color="#FDE047")
    fig_linha.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E8E4DF", title_font_size=16,
        yaxis=dict(gridcolor="#2A2A2A", range=[0, 40]),
        xaxis=dict(gridcolor="#2A2A2A")
    )
    st.plotly_chart(fig_linha, use_container_width=True)

    # Exportar tudo
    st.markdown("#### ⬇️ Exportar dados completos")
    csv_completo = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Baixar CSV Completo",
        data=csv_completo,
        file_name=f"burnout_completo_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


# =========================
# PÁGINA: COLABORADORES
# =========================
elif "Colaboradores" in pagina:

    st.title("👥 Lista de Colaboradores")

    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        setores_disponiveis = ["Todos"] + sorted(df["setor"].dropna().unique().tolist())
        filtro_setor = st.selectbox("Filtrar por Setor", setores_disponiveis)
    with col_f2:
        riscos_disponiveis = ["Todos", "Baixo risco", "Atenção", "Alto risco", "Risco elevado"]
        filtro_risco = st.selectbox("Filtrar por Risco", riscos_disponiveis)
    with col_f3:
        busca = st.text_input("Buscar por nome", placeholder="Digite o nome...")

    df_filtrado = df.copy()
    if filtro_setor != "Todos":
        df_filtrado = df_filtrado[df_filtrado["setor"] == filtro_setor]
    if filtro_risco != "Todos":
        df_filtrado = df_filtrado[df_filtrado["class_limpa"] == filtro_risco]
    if busca:
        df_filtrado = df_filtrado[df_filtrado["nome"].str.contains(busca, case=False, na=False)]

    st.markdown(f"**{len(df_filtrado)} colaboradores** encontrados.")
    st.markdown("---")

    for _, row in df_filtrado.sort_values("score_total", ascending=False).iterrows():
        badge = badge_html(row["classificacao"])
        data_fmt = row["timestamp"].strftime("%d/%m/%Y %H:%M")
        st.markdown(f"""
        <div class="table-row">
            <div>
                <strong>{row['nome']}</strong><br>
                <small style="color:#78716C">{row['cargo']} · {row['setor']} · {row['idade']} anos</small>
            </div>
            <div style="text-align:right">
                <strong style="font-size:1.1rem">{int(row['score_total'])}/40</strong><br>
                {badge}<br>
                <small style="color:#78716C">{data_fmt}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Exportar filtrado
    st.markdown("<br>", unsafe_allow_html=True)
    csv_filtrado = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Exportar lista filtrada", data=csv_filtrado,
                       file_name="colaboradores_filtrados.csv", mime="text/csv")


# =========================
# PÁGINA: POR SETOR
# =========================
elif "Setor" in pagina:

    st.title("🏢 Análise por Setor")

    resumo_setor = df.groupby("setor").agg(
        colaboradores=("nome", "count"),
        score_medio=("score_total", "mean"),
        fadiga_media=("fadiga_fisica", "mean"),
        emocional_media=("exaustao_emocional", "mean"),
        recuperacao_media=("recuperacao_saude", "mean"),
    ).reset_index().sort_values("score_medio", ascending=False)

    resumo_setor["risco"] = resumo_setor["score_medio"].apply(classificar_score)

    fig_setor = px.bar(
        resumo_setor, x="setor", y="score_medio",
        color="risco",
        color_discrete_map={
            "Baixo risco": "#4ADE80", "Atenção": "#FDE047",
            "Alto risco": "#FB923C",  "Risco elevado": "#F87171"
        },
        text=resumo_setor["score_medio"].apply(lambda x: f"{x:.1f}"),
        title="Score Médio por Setor"
    )
    fig_setor.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#E8E4DF", title_font_size=16,
        yaxis=dict(gridcolor="#2A2A2A", range=[0, 42]),
        xaxis=dict(gridcolor="#2A2A2A")
    )
    st.plotly_chart(fig_setor, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Detalhamento por Setor")

    for _, row in resumo_setor.iterrows():
        with st.expander(f"🏢 {row['setor']}  —  {row['colaboradores']} colaboradores  •  Score médio: {row['score_medio']:.1f}/40"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Score Médio",        f"{row['score_medio']:.1f}/40")
            c2.metric("Fadiga Física",       f"{row['fadiga_media']:.1f}/16")
            c3.metric("Exaustão Emocional",  f"{row['emocional_media']:.1f}/12")
            c4.metric("Recuperação/Saúde",   f"{row['recuperacao_media']:.1f}/12")

            # Colaboradores do setor
            df_setor = df[df["setor"] == row["setor"]][["nome","cargo","score_total","classificacao"]].copy()
            df_setor.columns = ["Nome","Cargo","Score","Classificação"]
            st.dataframe(df_setor, use_container_width=True, hide_index=True)


# =========================
# PÁGINA: RELATÓRIO INDIVIDUAL
# =========================
elif "Individual" in pagina:

    st.title("📄 Relatório Individual")

    nomes = sorted(df["nome"].dropna().unique().tolist())
    colaborador_sel = st.selectbox("Selecione o colaborador", nomes)

    df_pessoa = df[df["nome"] == colaborador_sel].sort_values("timestamp", ascending=False)

    if df_pessoa.empty:
        st.warning("Nenhum dado encontrado para este colaborador.")
    else:
        ultima = df_pessoa.iloc[0]

        st.markdown("---")
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"### {ultima['nome']}")
            st.markdown(f"**Cargo:** {ultima['cargo']}  |  **Setor:** {ultima['setor']}  |  **Idade:** {ultima['idade']} anos")
            st.markdown(f"**Último preenchimento:** {ultima['timestamp'].strftime('%d/%m/%Y às %H:%M')}")

        with col2:
            score = int(ultima["score_total"])
            class_limpa = ultima["class_limpa"]
            cor = {"Baixo risco":"#4ADE80","Atenção":"#FDE047","Alto risco":"#FB923C","Risco elevado":"#F87171"}.get(class_limpa,"#E8E4DF")
            st.markdown(f"""
            <div class="kpi-card" style="border-color:{cor}33">
                <div class="label">Score Total</div>
                <div class="valor" style="color:{cor}">{score}/40</div>
                <div class="label">{class_limpa}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Radar dos domínios
        categorias = ["Fadiga Física", "Exaustão Emocional", "Recup. e Saúde"]
        valores_pessoa = [
            ultima["fadiga_fisica"] / 16 * 100,
            ultima["exaustao_emocional"] / 12 * 100,
            ultima["recuperacao_saude"] / 12 * 100,
        ]
        media_geral = [
            df["fadiga_fisica"].mean() / 16 * 100,
            df["exaustao_emocional"].mean() / 12 * 100,
            df["recuperacao_saude"].mean() / 12 * 100,
        ]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=valores_pessoa + [valores_pessoa[0]],
            theta=categorias + [categorias[0]],
            fill="toself", name=colaborador_sel,
            line_color="#FDE047", fillcolor="rgba(253,224,71,0.15)"
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=media_geral + [media_geral[0]],
            theta=categorias + [categorias[0]],
            fill="toself", name="Média Geral",
            line_color="#60A5FA", fillcolor="rgba(96,165,250,0.1)"
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2A2A2A", color="#78716C"),
                angularaxis=dict(color="#E8E4DF")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#E8E4DF",
            title="Perfil por Domínio (% do máximo) vs. Média Geral",
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Detalhes dos domínios
        c1, c2, c3 = st.columns(3)
        c1.metric("🏋️ Fadiga Física",      f"{int(ultima['fadiga_fisica'])}/16",
                  delta=f"{ultima['fadiga_fisica'] - df['fadiga_fisica'].mean():.1f} vs. média")
        c2.metric("😔 Exaustão Emocional", f"{int(ultima['exaustao_emocional'])}/12",
                  delta=f"{ultima['exaustao_emocional'] - df['exaustao_emocional'].mean():.1f} vs. média")
        c3.metric("💤 Recuperação/Saúde",  f"{int(ultima['recuperacao_saude'])}/12",
                  delta=f"{ultima['recuperacao_saude'] - df['recuperacao_saude'].mean():.1f} vs. média")

        # Histórico (se respondeu mais de uma vez)
        if len(df_pessoa) > 1:
            st.markdown("#### 📈 Histórico de Respostas")
            fig_hist = px.line(
                df_pessoa.sort_values("timestamp"), x="timestamp", y="score_total",
                markers=True, line_shape="spline", title="Evolução do Score"
            )
            fig_hist.update_traces(line_color="#FDE047", marker_color="#FDE047")
            fig_hist.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#E8E4DF", yaxis=dict(gridcolor="#2A2A2A", range=[0,40]),
                xaxis=dict(gridcolor="#2A2A2A")
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        # Recomendação
        st.markdown("#### 💡 Recomendação")
        score_val = int(ultima["score_total"])
        if score_val <= 10:
            st.success("Manutenção de hábitos saudáveis e monitoramento periódico.")
        elif score_val <= 20:
            st.warning("Implementar pausas ativas e incentivar exercício físico regular.")
        elif score_val <= 30:
            st.warning("Exercício físico supervisionado e estratégias de recuperação estruturadas.")
        else:
            st.error("Avaliação profissional especializada recomendada com urgência.")

        # Exportar relatório individual
        csv_ind = df_pessoa.to_csv(index=False).encode("utf-8")
        st.download_button(
            f"📥 Exportar relatório de {colaborador_sel}",
            data=csv_ind,
            file_name=f"relatorio_{colaborador_sel.replace(' ','_')}.csv",
            mime="text/csv"
        )


# =========================
# RODAPÉ
# =========================
st.markdown("---")
st.caption("Painel restrito ao gestor • Burnout Screening • Dados confidenciais")
