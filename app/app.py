import streamlit as st
import pandas as pd
import time
import requests
import os
from datetime import datetime
from pathlib import Path

# ==============================================================================
# 1. CONFIGURAÇÕES DE CAMINHOS DINÂMICOS (CORREÇÃO SÊNIOR)
# ==============================================================================
# Isso garante que ele ache as pastas 'data' ou 'CORE' na raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent 

# AJUSTE AQUI: Verifique se sua pasta no GitHub se chama 'data' ou 'CORE'
# Se for 'data', mude para: PATH_CORE = BASE_DIR / "data"
PATH_CORE = BASE_DIR / "data" 
PATH_IMG = BASE_DIR / "assets"

st.set_page_config(page_title="Portal CIG 360", layout="wide", initial_sidebar_state="collapsed")

# CSS para Centralização e Estilo
st.markdown("""
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        .main { background-color: #f5f7f9; }
        .stTextInput { width: 100%; }
        .login-header { text-align: center; margin-bottom: 20px; }
        .login-title { font-size: 50px; font-weight: bold; color: #1E3A8A; margin-top: -20px; }
    </style>
""", unsafe_allow_html=True)

# ... (Funções carregar_dados e registrar_log permanecem as mesmas) ...

# --- TELA 1: LOGIN EVOLUÍDA ---
if st.session_state.page == 'login':
    _, col_login, _ = st.columns([1, 1.2, 1])
    
    with col_login:
        st.write("#") # Espaçamento superior
        
        # Título Centralizado com Imagem
        logo_path = PATH_IMG / "logo.png"
        st.markdown('<div class="login-header">', unsafe_allow_html=True)
        if logo_path.exists():
            st.image(str(logo_path), width=180) # Logo acima ou ao lado
        st.markdown('<h1 class="login-title">CIG 360º</h1>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Container de Login
        with st.container():
            email = st.text_input("E-mail", placeholder="seu@email.com")
            senha = st.text_input("Senha", type="password", placeholder="******")
            
            st.write("##")
            if st.button("ACESSAR PORTAL", use_container_width=True):
                df_u, _, _ = carregar_dados()
                
                if df_u is not None:
                    # Garantir que a comparação ignore espaços e maiúsculas
                    user = df_u[(df_u['email'].str.strip() == email.strip()) & 
                                (df_u['senha'].astype(str) == senha)]
                    
                    if not user.empty:
                        st.session_state.user_info = user.iloc[0].to_dict()
                        st.session_state.page = 'menu'
                        registrar_log("LOGIN", "Sucesso")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos.")
                else:
                    st.error("⚠️ Banco de dados não localizado. Verifique a pasta 'data'.")