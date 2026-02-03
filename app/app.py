import streamlit as st
import pandas as pd
import base64
from pathlib import Path

# Configurações de Caminho
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_DATA = BASE_DIR / "data"
PATH_IMG = BASE_DIR / "assets"

st.set_page_config(page_title="CIG 360º | Login", layout="wide", initial_sidebar_state="collapsed")

def get_base64(file_path):
    if file_path.exists():
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# --- CSS SÊNIOR PARA LAYOUT 100% ---
def apply_login_styles():
    bg_base64 = get_base64(PATH_IMG / "fundologin.jpg")
    bg_css = f"url('data:image/jpg;base64,{bg_base64}')" if bg_base64 else "#1e3a8a"
    
    st.markdown(f"""
        <style>
            /* 1. Remover barra branca e paddings */
            .block-container {{ padding: 0rem !important; }}
            header {{ visibility: hidden; }}
            
            /* Fundo da Tela */
            .stApp {{
                background-image: {bg_css};
                background-size: cover;
                background-position: center;
            }}

            /* 4. Posição Empresa (Canto Superior Direito) */
            .empresa-logo {{
                position: absolute;
                top: 20px;
                right: 40px;
                z-index: 100;
            }}

            /* 5. Caixa Branca de Login (Legibilidade) */
            .login-container {{
                background-color: rgba(255, 255, 255, 0.92);
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                max-width: 450px;
                margin: auto;
                text-align: center;
            }}

            .main-title {{
                color: white;
                font-size: 52px;
                font-weight: 800;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                text-align: center;
                margin-top: 5vh;
                margin-bottom: 5px;
            }}
            
            .stButton button {{
                background-color: #1e3a8a;
                color: white;
                height: 3.5em;
                margin-top: 10px; /* 6. Botão mais próximo */
            }}
        </style>
    """, unsafe_allow_html=True)

# --- TELA 1: LOGIN ---
if 'page' not in st.session_state or st.session_state.page == 'login':
    apply_login_styles()

    # 4. Renderiza Logo Empresa no Canto Superior Direito
    empresa_base64 = get_base64(PATH_IMG / "empresa.jpg")
    if empresa_base64:
        st.markdown(f'<div class="empresa-logo"><img src="data:image/jpg;base64,{empresa_base64}" width="120"></div>', unsafe_allow_html=True)

    # Espaçamento para centralizar verticalmente
    st.write("##")
    
    # 3. Título Principal
    st.markdown('<h1 class="main-title">Portal CIG 360º | GIROAgro</h1>', unsafe_allow_html=True)
    
    # 2. Logo.png Centralizada abaixo do Título
    col_l1, col_l2, col_l3 = st.columns([1, 0.5, 1])
    with col_l2:
        logo_base64 = get_base64(PATH_IMG / "logo.png")
        if logo_base64:
            st.image(f"data:image/png;base64,{logo_base64}", use_container_width=True)

    st.write("#") # Espaço entre Logo e Caixa de Login

    # 5. Container de Login Centralizado
    _, col_card, _ = st.columns([1, 1.2, 1])
    with col_card:
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.subheader("Acesso Restrito")
            
            email = st.text_input("E-mail de Acesso", placeholder="seu@email.com", label_visibility="collapsed")
            senha = st.text_input("Senha", type="password", placeholder="Sua senha", label_visibility="collapsed")
            
            # 6. Botão posicionado próximo aos campos
            if st.button("ACESSAR PORTAL", use_container_width=True):
                # ... lógica de validação aqui ...
                pass
            st.markdown('</div>', unsafe_allow_html=True)