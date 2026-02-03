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

            /* 4º Barra Vermelha e Texto Branco no Botão */
            .stButton button {{
                background-color: #FF0000 !important;
                color: white !important;
                border: none;
                height: 3.5em;
                font-weight: bold;
                margin-top: 20px;
            }}

            /* 1º e 3º Texto em Branco para Contraste */
            .label-text {{
                color: white !important;
                font-weight: 500;
                margin-bottom: -35px;
                font-size: 16px;
            }}

            .main-title {{
                color: white;
                font-size: 52px;
                font-weight: 800;
                text-align: center;
                margin-top: 5vh;
            }}

            /* 4º Posição Empresa Canto Superior Direito */
            .empresa-logo {{
                position: absolute;
                top: 20px;
                right: 40px;
                z-index: 100;
            }}
            
            /* 2º Removendo caixas brancas extras de containers */
            .stVerticalBlock {{ gap: 0.5rem; }}
        </style>
    """, unsafe_allow_html=True)

if 'page' not in st.session_state or st.session_state.page == 'login':
    apply_login_styles()

    # 5º Incluir imagem empresa1.jpg no canto superior direito
    emp_base64 = get_base64(PATH_IMG / "empresa1.jpg")
    if emp_base64:
        st.markdown(f'<div class="empresa-logo"><img src="data:image/jpg;base64,{emp_base64}" width="130"></div>', unsafe_allow_html=True)

    st.write("##")
    # 1º e 3º Título em Branco
    st.markdown('<h1 class="main-title">Portal CIG 360º | GIROAgro</h1>', unsafe_allow_html=True)
    
    # Logo.png Centralizada
    col_l1, col_l2, col_l3 = st.columns([1, 0.4, 1])
    with col_l2:
        logo_base64 = get_base64(PATH_IMG / "logo.png")
        if logo_base64:
            st.image(f"data:image/png;base64,{logo_base64}", use_container_width=True)

    # Área de Login
    _, col_login, _ = st.columns([1, 1, 1])
    with col_login:
        st.write("##")
        
        # Observação: Subtítulos específicos em branco
        st.markdown('<p class="label-text">E-mail Corporativo:</p>', unsafe_allow_html=True)
        email = st.text_input("", placeholder="usuario@giroagro.com.br", key="email_input")
        
        st.markdown('<p class="label-text">Senha:</p>', unsafe_allow_html=True)
        senha = st.text_input("", type="password", placeholder="Digite sua senha", key="pass_input")
        
        if st.button("ACESSAR PORTAL", use_container_width=True):
            # Lógica de autenticação aqui
            pass