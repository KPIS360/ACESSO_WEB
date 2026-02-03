import streamlit as st
import pandas as pd
import time
import requests
import os
import base64
from datetime import datetime
from pathlib import Path

# ==============================================================================
# 1. CONFIGURAÇÕES E CAMINHOS
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_DATA = BASE_DIR / "data"
PATH_IMG = BASE_DIR / "assets"

st.set_page_config(page_title="CIG 360º | Login", layout="wide", initial_sidebar_state="collapsed")

# Função Sênior para converter imagem local em Base64
def get_base64(file_path):
    if file_path.exists():
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# ==============================================================================
# 2. FUNÇÕES DE DADOS E LOGS
# ==============================================================================
def carregar_dados():
    try:
        u = pd.read_excel(PATH_DATA / 'usuarios.xlsx')
        r = pd.read_excel(PATH_DATA / 'relatorios.xlsx')
        rel = pd.read_excel(PATH_DATA / 'relacional.xlsx')
        return u, r, rel
    except Exception as e:
        st.error(f"Erro ao carregar banco de dados: {e}")
        return None, None, None

def registrar_log(usuario, email, evento):
    try:
        ip = requests.get('https://api.ipify.org', timeout=3).text
        log_path = PATH_DATA / 'logs_acesso.xlsx'
        novo_log = pd.DataFrame([{
            'data_hora': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'usuario': usuario, 'email': email, 'evento': evento, 'ip': ip
        }])
        if log_path.exists():
            df_old = pd.read_excel(log_path)
            pd.concat([df_old, novo_log]).to_excel(log_path, index=False)
        else:
            novo_log.to_excel(log_path, index=False)
    except: pass

# ==============================================================================
# 3. LÓGICA DE NAVEGAÇÃO
# ==============================================================================
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# --- CSS GLOBAL ---
st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .block-container {padding: 0rem !important;}
        .stButton button {border-radius: 8px; font-weight: bold; height: 3em;}
    </style>
""", unsafe_allow_html=True)

# --- TELA 1: LOGIN ---
if st.session_state.page == 'login':
    # Aplicar Fundo via Base64
    bg_base64 = get_base64(PATH_IMG / "fundologin.jpg")
    if bg_base64:
        st.markdown(f"""
            <style>
                .stApp {{
                    background-image: url("data:image/jpg;base64,{bg_base64}");
                    background-size: cover;
                    background-position: center;
                }}
            </style>
        """, unsafe_allow_html=True)

    # Estilo do Card de Login
    st.markdown("""
        <style>
            .login-card {
                background: rgba(255, 255, 255, 0.96);
                padding: 50px;
                border-radius: 20px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.4);
                text-align: center;
                margin-top: 40px;
            }
            .title-cig { 
                font-size: 75px !important; 
                font-weight: 900; 
                color: #1e3a8a; 
                margin: 0px !important;
                line-height: 1;
            }
        </style>
    """, unsafe_allow_html=True)

    _, col_card, _ = st.columns([1, 1.4, 1])
    
    with col_card:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # [Posição 1] logo.png
        if (PATH_IMG / "logo.png").exists():
            st.image(str(PATH_IMG / "logo.png"), width=220)
        
        # Título Central
        st.markdown('<h1 class="title-cig">CIG 360º</h1>', unsafe_allow_html=True)
        
        # [Posição 2] empresa1.jpg
        if (PATH_IMG / "empresa1.jpg").exists():
            st.image(str(PATH_IMG / "empresa1.jpg"), width=150)
        
        st.write("##")
        email = st.text_input("E-mail de Acesso", placeholder="exemplo@giro.com")
        senha = st.text_input("Senha", type="password", placeholder="******")
        
        st.write("#")
        if st.button("ACESSAR PORTAL", use_container_width=True):
            df_u, _, _ = carregar_dados()
            if df_u is not None:
                user = df_u[(df_u['email'] == email) & (df_u['senha'].astype(str) == senha)]
                if not user.empty:
                    st.session_state.user = user.iloc[0].to_dict()
                    st.session_state.page = 'menu'
                    registrar_log(st.session_state.user['nome'], email, "LOGIN")
                    st.rerun()
                else:
                    st.error("Credenciais incorretas.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- Lógica das outras telas (Menu e View) permanece simplificada abaixo ---
elif st.session_state.page == 'menu':
    st.markdown("<style>.stApp {background-image: none; background-color: #f0f2f6;}</style>", unsafe_allow_html=True)
    st.title(f"Olá, {st.session_state.user['nome']}")
    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()
    # Aqui virá a lista de relatórios no próximo passo...