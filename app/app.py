import streamlit as st
import pandas as pd
import base64
import os
import requests
import time
from pathlib import Path
from datetime import datetime

# ==============================================================================
# 1. CONFIGURAÇÕES DE CAMINHOS
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_DATA = BASE_DIR / "data"
PATH_IMG = BASE_DIR / "assets"

st.set_page_config(page_title="Portal CIG 360", layout="wide", initial_sidebar_state="collapsed")

# Inicialização segura do Session State (Evita o NameError)
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Função para converter imagem em Base64
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
        st.error(f"Erro ao acessar pasta data/: {e}")
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
# 3. ESTILIZAÇÃO (CSS)
# ==============================================================================
def apply_styles():
    st.markdown("""
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .block-container {padding: 0rem !important;}
            
            /* Título Branco Central */
            .main-title {
                color: white !important; font-size: 58px; font-weight: 800;
                text-align: center; margin-top: 5vh; text-shadow: 2px 2px 8px rgba(0,0,0,0.6);
            }
            
            /* Labels Brancos acima dos Inputs (Corrigido) */
            .label-white { 
                color: white !important; font-size: 19px; font-weight: 500; 
                margin-top: 15px; margin-bottom: 5px; display: block;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
            }

            /* Botão Vermelho #ED3237 */
            .stButton button {
                background-color: #ED3237 !important; color: white !important;
                height: 55px !important; font-size: 20px !important; font-weight: bold !important;
                border-radius: 10px !important; border: none !important; margin-top: 20px;
            }
            
            /* Logo Empresa no Canto */
            .empresa-logo { position: absolute; top: 15px; right: 35px; z-index: 999; }
        </style>
    """, unsafe_allow_html=True)

    if st.session_state.page == 'login':
        bg_base64 = get_base64(PATH_IMG / "fundologin.jpg")
        if bg_base64:
            st.markdown(f"""
                <style>
                    .stApp {{
                        background-image: url("data:image/jpg;base64,{bg_base64}");
                        background-size: cover; background-position: center;
                    }}
                </style>
            """, unsafe_allow_html=True)

# ==============================================================================
# 4. LÓGICA DE TELAS
# ==============================================================================
apply_styles()

if st.session_state.page == 'login':
    # Logo Empresa reduzida em 15% (~135px)
    emp_base = get_base64(PATH_IMG / "empresa1.jpg")
    if emp_base:
        st.markdown(f'<div class="empresa-logo"><img src="data:image/jpg;base64,{emp_base}" width="135"></div>', unsafe_allow_html=True)

    st.markdown('<h1 class="main-title">Portal CIG 360º | GIROAgro</h1>', unsafe_allow_html=True)
    
    # Logo Central
    _, col_logo, _ = st.columns([1, 0.35, 1])
    with col_logo:
        logo_base = get_base64(PATH_IMG / "logo.png")
        if logo_base:
            st.image(f"data:image/png;base64,{logo_base}", use_container_width=True)

    # Formulário de Login
    _, col_form, _ = st.columns([1, 1, 1])
    with col_form:
        st.write("##")
        st.markdown('<label class="label-white">E-mail Corporativo:</label>', unsafe_allow_html=True)
        email_in = st.text_input("", placeholder="usuario@giroagro.com.br", key="email", label_visibility="collapsed")
        
        st.markdown('<label class="label-white">Senha:</label>', unsafe_allow_html=True)
        senha_in = st.text_input("", type="password", placeholder="••••••••", key="senha", label_visibility="collapsed")
        
        if st.button("ACESSAR PORTAL", use_container_width=True):
            df_u, _, _ = carregar_dados()
            if df_u is not None:
                user = df_u[(df_u['email'].str.strip() == email_in.strip()) & (df_u['senha'].astype(str) == senha_in)]
                if not user.empty:
                    st.session_state.user_info = user.iloc[0].to_dict()
                    st.session_state.page = 'menu'
                    registrar_log(st.session_state.user_info['nome'], email_in, "LOGIN")
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")

elif st.session_state.page == 'menu':
    st.markdown("<style>.stApp {background-image: none; background-color: #f8fafc;}</style>", unsafe_allow_html=True)
    st.title(f"Olá, {st.session_state.user_info['nome']}")
    if st.button("Sair 🚪"):
        st.session_state.clear()
        st.rerun()