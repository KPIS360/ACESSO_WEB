import streamlit as st
import pandas as pd
import base64
from pathlib import Path
from datetime import datetime
import requests

# Configurações de Caminho
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_DATA = BASE_DIR / "data"
PATH_IMG = BASE_DIR / "assets"

def get_base64(file_path):
    if file_path.exists():
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

def apply_login_styles():
    bg_base64 = get_base64(PATH_IMG / "fundologin.jpg")
    bg_css = f"url('data:image/jpg;base64,{bg_base64}')" if bg_base64 else "#1e3a8a"
    
    st.markdown(f"""
        <style>
            .block-container {{ padding: 0rem !important; }}
            header {{ visibility: hidden; }}
            
            .stApp {{
                background-image: {bg_css};
                background-size: cover;
                background-position: center;
            }}

            /* 1º Título Branco e Impactante */
            .main-title {{
                color: white !important;
                font-size: 58px;
                font-weight: 800;
                text-align: center;
                margin-top: 5vh;
                margin-bottom: 10px;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.6);
            }}

            /* 2º Posicionamento da empresa1.jpg (Superior Direito) */
            .empresa-logo {{
                position: absolute;
                top: 15px;
                right: 35px;
                z-index: 999;
            }}

            /* 3º e 4º Ajuste Proporcional dos Campos e Botão */
            .stTextInput > div > div > input {{
                height: 55px !important;
                font-size: 18px !important;
                background-color: rgba(255, 255, 255, 0.95) !important;
            }}

            /* 5º Botão na cor #ED3237 */
            .stButton button {{
                background-color: #ED3237 !important;
                color: white !important;
                height: 55px !important;
                font-size: 20px !important;
                font-weight: bold !important;
                border: none !important;
                border-radius: 10px !important;
                transition: 0.3s;
                margin-top: 10px;
            }}
            .stButton button:hover {{
                background-color: #c2282d !important;
                transform: scale(1.02);
            }}

            /* Labels em Branco */
            .label-text {{
                color: white !important;
                font-size: 19px;
                font-weight: 500;
                margin-bottom: -30px;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
            }}
        </style>
    """, unsafe_allow_html=True)

# Lógica de Dados (Simples e Direta)
def validar_login(user, pwd):
    try:
        df_u = pd.read_excel(PATH_DATA / 'usuarios.xlsx')
        match = df_u[(df_u['email'] == user) & (df_u['senha'].astype(str) == pwd)]
        return match.iloc[0].to_dict() if not match.empty else None
    except:
        return None

# --- RENDERIZAÇÃO ---
if 'page' not in st.session_state:
    st.session_state.page = 'login'

if st.session_state.page == 'login':
    apply_login_styles()

    # 2º Imagem empresa1.jpg no canto
    emp_base = get_base64(PATH_IMG / "empresa1.jpg")
    if emp_base:
        st.markdown(f'<div class="empresa-logo"><img src="data:image/jpg;base64,{emp_base}" width="160"></div>', unsafe_allow_html=True)

    # 1º Título Centralizado
    st.markdown('<h1 class="main-title">Portal CIG 360º | GIROAgro</h1>', unsafe_allow_html=True)
    
    # Logo Central
    c1, c2, c3 = st.columns([1, 0.35, 1])
    with c2:
        logo_base = get_base64(PATH_IMG / "logo.png")
        if logo_base:
            st.image(f"data:image/png;base64,{logo_base}", use_container_width=True)

    # 3º e 4º Formulário Proporcional
    _, col_form, _ = st.columns([1, 1, 1]) # Coluna central maior para proporcionalidade
    with col_form:
        st.write("##")
        st.markdown('<p class="label-text">E-mail Corporativo:</p>', unsafe_allow_html=True)
        email_input = st.text_input("", placeholder="usuario@giroagro.com.br", key="email")
        
        st.markdown('<p class="label-text">Senha:</p>', unsafe_allow_html=True)
        senha_input = st.text_input("", type="password", placeholder="••••••••", key="senha")
        
        if st.button("ACESSAR PORTAL", use_container_width=True):
            user_data = validar_login(email_input, senha_input)
            if user_data:
                st.session_state.user_info = user_data
                st.session_state.page = 'menu'
                st.rerun()
            else:
                st.error("Credenciais inválidas. Tente novamente.")