import streamlit as st
import pandas as pd
import time
import requests
import os
from datetime import datetime
from pathlib import Path

# ==============================================================================
# 1. CONFIGURAÇÕES DE CAMINHOS DINÂMICOS (SÊNIOR)
# ==============================================================================
# Detecta a pasta onde o app.py está (independente de onde é executado)
BASE_DIR = Path(__file__).parent.parent 

# Define os caminhos relativos à raiz do projeto (ACESSO_WEB)
PATH_CORE = BASE_DIR / "CORE"
PATH_IMG = BASE_DIR / "IMG"

st.set_page_config(page_title="Portal CIG 360", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# 2. CSS E INTERFACE
# ==============================================================================
st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .report-card {
            background-color: #f9f9f9;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #ddd;
            text-align: center;
            margin-bottom: 10px;
        }
        .stButton button { width: 100%; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. FUNÇÕES DE SUPORTE
# ==============================================================================

@st.cache_data(ttl=300) # Cache de 5 min para performance
def carregar_dados():
    try:
        u = pd.read_excel(PATH_CORE / 'usuarios.xlsx')
        r = pd.read_excel(PATH_CORE / 'relatorios.xlsx')
        rel = pd.read_excel(PATH_CORE / 'relacional.xlsx')
        return u, r, rel
    except Exception as e:
        st.error(f"Erro ao acessar base de dados: {e}")
        return None, None, None

def registrar_log(evento, detalhe="", tempo=0):
    user = st.session_state.get('user_info', {'nome': 'Sessão', 'email': 'N/A'})
    try:
        ip = requests.get('https://api.ipify.org', timeout=3).text
    except:
        ip = "0.0.0.0"

    log_entry = pd.DataFrame([{
        'data_hora': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'usuario': user['nome'],
        'email': user['email'],
        'evento': evento,
        'detalhe': detalhe,
        'ip': ip,
        'tempo_segundos': tempo
    }])

    log_path = PATH_CORE / 'logs_acesso.xlsx'
    try:
        if log_path.exists():
            df_old = pd.read_excel(log_path)
            pd.concat([df_old, log_entry]).to_excel(log_path, index=False)
        else:
            log_entry.to_excel(log_path, index=False)
    except Exception as e:
        print(f"Erro ao salvar log (concorrência): {e}")

# ==============================================================================
# 4. LÓGICA DE TELAS
# ==============================================================================

if 'page' not in st.session_state:
    st.session_state.page = 'login'

# --- TELA 1: LOGIN ---
if st.session_state.page == 'login':
    _, col_login, _ = st.columns([1, 1, 1])
    with col_login:
        logo_path = PATH_IMG / "logo.png"
        if logo_path.exists():
            st.image(str(logo_path), width=200)
        
        st.title("Login")
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        
        if st.button("Entrar"):
            df_u, _, _ = carregar_dados()
            user = df_u[(df_u['email'] == email) & (df_u['senha'].astype(str) == senha)]
            if not user.empty:
                st.session_state.user_info = user.iloc[0].to_dict()
                st.session_state.page = 'menu'
                registrar_log("LOGIN")
                st.rerun()
            else:
                st.error("Credenciais inválidas")

# --- TELA 2: SELEÇÃO ---
elif st.session_state.page == 'menu':
    c1, c2 = st.columns([4, 1])
    c1.title(f"Olá, {st.session_state.user_info['nome']}")
    if c2.button("Sair 🚪"):
        registrar_log("LOGOUT")
        st.session_state.clear()
        st.session_state.page = 'login'
        st.rerun()

    df_u, df_r, df_rel = carregar_dados()
    meus_acessos = pd.merge(df_rel[df_rel['usuario_id'] == st.session_state.user_info['usuario_id']], df_r, on='relatorio_id')

    # Filtros
    f_col1, f_col2 = st.columns([2, 1])
    busca = f_col1.text_input("🔍 Buscar Relatório")
    cat_filtro = f_col2.selectbox("📂 Categoria", ["Todas"] + list(meus_acessos['categoria'].unique()))

    df_f = meus_acessos.copy()
    if busca:
        df_f = df_f[df_f['nome_relatorio'].str.contains(busca, case=False)]
    if cat_filtro != "Todas":
        df_f = df_f[df_f['categoria'] == cat_filtro]

    # Galeria
    for categoria in df_f['categoria'].unique():
        st.subheader(categoria)
        df_c = df_f[df_f['categoria'] == categoria]
        cols = st.columns(3)
        for i, (_, row) in enumerate(df_c.iterrows()):
            with cols[i % 3]:
                st.markdown(f"<div class='report-card'><b>{row['nome_relatorio']}</b></div>", unsafe_allow_html=True)
                if st.button("Abrir", key=f"btn_{row['relatorio_id']}"):
                    st.session_state.report = row.to_dict()
                    st.session_state.start_time = time.time()
                    st.session_state.page = 'view'
                    st.rerun()

# --- TELA 3: VIEW ---
elif st.session_state.page == 'view':
    rep = st.session_state.report
    c_v1, c_v2, c_v3 = st.columns([6, 1, 1])
    c_v1.subheader(rep['nome_relatorio'])
    
    if c_v2.button("⬅️ Voltar"):
        tempo = int(time.time() - st.session_state.start_time)
        registrar_log("FECHOU_DASH", rep['nome_relatorio'], tempo)
        st.session_state.page = 'menu'
        st.rerun()
        
    if c_v3.button("Sair 🚪"):
        st.session_state.clear()
        st.session_state.page = 'login'
        st.rerun()

    st.markdown(f'<iframe src="{rep["link"]}" width="100%" height="800px" frameborder="0"></iframe>', unsafe_allow_html=True)