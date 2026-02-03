import streamlit as st
import pandas as pd
import base64
import os
import requests
import time
from pathlib import Path
from datetime import datetime

# ==============================================================================
# 1. CONFIGURAÇÕES DE CAMINHOS E SEGURANÇA (ESTRUTURA DATA/)
# ==============================================================================
# Garante que o app encontre a pasta 'data' na raiz do projeto no GitHub
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_DATA = BASE_DIR / "data"
PATH_IMG = BASE_DIR / "assets"

st.set_page_config(page_title="Portal CIG 360", layout="wide", initial_sidebar_state="collapsed")

# Função para converter imagem em Base64 (Garante que o fundo apareça no Cloud)
def get_base64(file_path):
    if file_path.exists():
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# ==============================================================================
# 2. FUNÇÕES DE SUPORTE (DADOS E LOGS)
# ==============================================================================
@st.cache_data(ttl=300)
def carregar_dados():
    try:
        u = pd.read_excel(PATH_DATA / 'usuarios.xlsx')
        r = pd.read_excel(PATH_DATA / 'relatorios.xlsx')
        rel = pd.read_excel(PATH_DATA / 'relacional.xlsx')
        return u, r, rel
    except Exception as e:
        st.error(f"Erro ao acessar base de dados na pasta data/: {e}")
        return None, None, None

def registrar_log(evento, detalhe="", tempo=0):
    user = st.session_state.get('user_info', {'nome': 'Sessão', 'email': 'N/A'})
    try:
        ip = requests.get('https://api.ipify.org', timeout=3).text
    except:
        ip = "0.0.0.0"

    log_entry = pd.DataFrame([{
        'data_hora': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'usuario': user['nome'], 'email': user['email'],
        'evento': evento, 'detalhe': detalhe, 'ip': ip, 'tempo_segundos': tempo
    }])

    log_path = PATH_DATA / 'logs_acesso.xlsx'
    try:
        if log_path.exists():
            df_old = pd.read_excel(log_path)
            pd.concat([df_old, log_entry]).to_excel(log_path, index=False)
        else:
            log_entry.to_excel(log_path, index=False)
    except:
        pass # Evita travar o app se o Excel estiver em uso

# ==============================================================================
# 3. ESTILIZAÇÃO E TELA DE LOGIN (ETAPA 1)
# ==============================================================================
if 'page' not in st.session_state:
    st.session_state.page = 'login'

def apply_styles():
    st.markdown("""
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .block-container {padding: 0rem !important;}
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.page == 'login':
        bg_base64 = get_base64(PATH_IMG / "fundologin.jpg")
        bg_css = f"url('data:image/jpg;base64,{bg_base64}')" if bg_base64 else "#1e3a8a"
        st.markdown(f"""
            <style>
                .stApp {{
                    background-image: {bg_css};
                    background-size: cover;
                    background-position: center;
                }}
                /* 1º e 3º: Texto Branco e Título */
                .main-title {{
                    color: white !important; font-size: 58px; font-weight: 800;
                    text-align: center; margin-top: 5vh; text-shadow: 2px 2px 8px rgba(0,0,0,0.6);
                }}
                .label-white {{ color: white !important; font-size: 18px; font-weight: 500; margin-bottom: -30px; }}
                
                /* 4º: Botão Vermelho #ED3237 */
                .stButton button {{
                    background-color: #ED3237 !important; color: white !important;
                    height: 55px !important; font-size: 20px !important; font-weight: bold !important;
                    border-radius: 10px !important; border: none !important; margin-top: 10px;
                }}
                /* 2º: Posicionamento empresa1.jpg no canto */
                .empresa-logo {{ position: absolute; top: 15px; right: 35px; z-index: 999; }}
            </style>
        """, unsafe_allow_html=True)

apply_styles()

# --- TELA 1: LOGIN ---
if st.session_state.page == 'login':
    # 2º Imagem empresa1.jpg no canto superior direito
    emp_base = get_base64(PATH_IMG / "empresa1.jpg")
    if emp_base:
        st.markdown(f'<div class="empresa-logo"><img src="data:image/jpg;base64,{emp_base}" width="160"></div>', unsafe_allow_html=True)

    # 1º Título Centralizado Branco
    st.markdown('<h1 class="main-title">Portal CIG 360º | GIROAgro</h1>', unsafe_allow_html=True)
    
    # Logo Central (logo.png)
    c1, c2, c3 = st.columns([1, 0.35, 1])
    with c2:
        logo_base = get_base64(PATH_IMG / "logo.png")
        if logo_base:
            st.image(f"data:image/png;base64,{logo_base}", use_container_width=True)

    # 3º e 4º Formulário Proporcional (Tamanho 100%)
    _, col_form, _ = st.columns([1, 1, 1])
    with col_form:
        st.write("##")
        st.markdown('<p class="label-white">E-mail Corporativo:</p>', unsafe_allow_html=True)
        email_in = st.text_input("", placeholder="usuario@giroagro.com.br", key="email", label_visibility="collapsed")
        
        st.markdown('<p class="label-white">Senha:</p>', unsafe_allow_html=True)
        senha_in = st.text_input("", type="password", placeholder="••••••••", key="senha", label_visibility="collapsed")
        
        if st.button("ACESSAR PORTAL", use_container_width=True):
            df_u, _, _ = carregar_dados()
            if df_u is not None:
                user = df_u[(df_u['email'].str.strip() == email_in.strip()) & (df_u['senha'].astype(str) == senha_in)]
                if not user.empty:
                    st.session_state.user_info = user.iloc[0].to_dict()
                    st.session_state.page = 'menu'
                    registrar_log("LOGIN")
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")

# --- TELA 2: LISTA DE RELATÓRIOS ---
elif st.session_state.page == 'menu':
    st.markdown("<style>.stApp {background-image: none; background-color: #f8fafc;}</style>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([5, 1])
    c1.title(f"Olá, {st.session_state.user_info['nome']}")
    if c2.button("Sair 🚪"):
        registrar_log("LOGOUT")
        st.session_state.clear()
        st.rerun()

    df_u, df_r, df_rel = carregar_dados()
    meus_acessos = pd.merge(df_rel[df_rel['usuario_id'] == st.session_state.user_info['usuario_id']], df_r, on='relatorio_id')

    st.write("### 📂 Selecione um relatório")
    for _, row in meus_acessos.iterrows():
        with st.container():
            col_t, col_b = st.columns([4, 1])
            col_t.markdown(f"**{row['nome_relatorio']}** \n*{row['categoria']}*")
            if col_b.button("Abrir", key=f"btn_{row['relatorio_id']}", use_container_width=True):
                st.session_state.report = row.to_dict()
                st.session_state.start_time = time.time()
                st.session_state.page = 'view'
                st.rerun()

# --- TELA 3: VISUALIZAÇÃO FOCO TOTAL ---
elif st.session_state.page == 'view':
    st.markdown("<style>.stApp {background-image: none;}</style>", unsafe_allow_html=True)
    rep = st.session_state.report
    c_v1, c_v2, c_v3 = st.columns([6, 1, 1])
    c_v1.write(f"### {rep['nome_relatorio']}")
    
    if c_v2.button("⬅️ Voltar"):
        tempo = int(time.time() - st.session_state.start_time)
        registrar_log("FECHOU_DASH", rep['nome_relatorio'], tempo)
        st.session_state.page = 'menu'
        st.rerun()
        
    if c_v3.button("Sair 🚪"):
        st.session_state.clear()
        st.rerun()

    st.markdown(f'<iframe src="{rep["link"]}" width="100%" height="850px" frameborder="0" allowFullScreen="true"></iframe>', unsafe_allow_html=True)