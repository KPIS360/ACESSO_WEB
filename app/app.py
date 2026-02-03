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
# 2. FUNÇÕES DE DADOS E LOGS (UNIFICADAS NO ARQUIVO)
# ==============================================================================
def carregar_dados():
    try:
        # Busca os arquivos na pasta 'data' conforme sua estrutura de deploy
        u = pd.read_excel(PATH_DATA / 'usuarios.xlsx')
        r = pd.read_excel(PATH_DATA / 'relatorios.xlsx')
        rel = pd.read_excel(PATH_DATA / 'relacional.xlsx')
        return u, r, rel
    except Exception as e:
        st.error(f"Erro ao acessar base de dados na pasta data/: {e}")
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
# 3. ESTILIZAÇÃO (CSS REVISADO)
# ==============================================================================
def apply_styles():
    st.markdown("""
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .block-container {padding: 0rem !important;}
            
            /* Removido fundologin.jpg: Fundo limpo para contraste com texto preto */
            .stApp { background-color: #FFFFFF; }
            
            /* Título e Subtítulos em PRETO para contraste no fundo branco */
            .main-title {
                color: #000000 !important; font-size: 58px; font-weight: 800;
                text-align: center; margin-top: 5vh;
            }
            
            .label-dark { 
                color: #000000 !important; font-size: 19px; font-weight: 500; 
                margin-top: 15px; margin-bottom: 5px; display: block;
            }

            /* Botão Vermelho #ED3237 conforme solicitado */
            .stButton button {
                background-color: #ED3237 !important; color: white !important;
                height: 55px !important; font-size: 20px !important; font-weight: bold !important;
                border-radius: 10px !important; border: none !important; margin-top: 20px;
            }
            
            /* Logo Empresa no Canto Superior Direito */
            .empresa-logo { position: absolute; top: 15px; right: 35px; z-index: 999; }
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. LÓGICA DE TELAS
# ==============================================================================
apply_styles()

if st.session_state.page == 'login':
    # Logo Empresa reduzida em mais 20% (ajustada para ~110px)
    emp_base = get_base64(PATH_IMG / "empresa1.jpg")
    if emp_base:
        st.markdown(f'<div class="empresa-logo"><img src="data:image/jpg;base64,{emp_base}" width="110"></div>', unsafe_allow_html=True)

    # Título em PRETO
    st.markdown('<h1 class="main-title">Portal CIG 360º | GIROAgro</h1>', unsafe_allow_html=True)
    
    # Logo Central (logo.png)
    _, col_logo, _ = st.columns([1, 0.35, 1])
    with col_logo:
        logo_base = get_base64(PATH_IMG / "logo.png")
        if logo_base:
            st.image(f"data:image/png;base64,{logo_base}", use_container_width=True)

    # Formulário de Login (Texto em PRETO)
    _, col_form, _ = st.columns([1, 1, 1])
    with col_form:
        st.write("##")
        st.markdown('<label class="label-dark">E-mail Corporativo:</label>', unsafe_allow_html=True)
        email_in = st.text_input("", placeholder="usuario@giroagro.com.br", key="email", label_visibility="collapsed")
        
        st.markdown('<label class="label-dark">Senha:</label>', unsafe_allow_html=True)
        senha_in = st.text_input("", type="password", placeholder="••••••••", key="senha", label_visibility="collapsed")
        
        if st.button("ACESSAR PORTAL", use_container_width=True):
            df_u, _, _ = carregar_dados()
            if df_u is not None:
                # Validação direta sem arquivos externos para evitar erros de deploy
                user = df_u[(df_u['email'].str.strip() == email_in.strip()) & (df_u['senha'].astype(str) == senha_in)]
                if not user.empty:
                    st.session_state.user_info = user.iloc[0].to_dict()
                    st.session_state.page = 'menu'
                    registrar_log(st.session_state.user_info['nome'], email_in, "LOGIN")
                    st.rerun()
                else:
                    st.error("Credenciais inválidas. Verifique seu e-mail e senha.")

elif st.session_state.page == 'menu':
    st.markdown("<style>.stApp {background-color: #f8fafc;}</style>", unsafe_allow_html=True)
    st.title(f"Olá, {st.session_state.user_info['nome']}")
    
    # Botão de Sair com funcionalidade garantida
    if st.button("Sair 🚪"):
        st.session_state.clear()
        st.rerun()
    
    # Carregamento da galeria de relatórios conforme permissões
    df_u, df_r, df_rel = carregar_dados()
    if df_rel is not None:
        meus_ids = df_rel[df_rel['usuario_id'] == st.session_state.user_info['usuario_id']]
        meus_relatorios = pd.merge(meus_ids[['relatorio_id']], df_r, on='relatorio_id', how='inner')
        
        st.write("### 📂 Selecione seu relatório abaixo:")
        for _, row in meus_relatorios.iterrows():
            if st.button(f"📊 {row['nome_relatorio']}", key=f"btn_{row['relatorio_id']}", use_container_width=True):
                st.session_state.report_url = row['link']
                st.session_state.report_name = row['nome_relatorio']
                st.session_state.page = 'view'
                st.rerun()

elif st.session_state.page == 'view':
    st.markdown("<style>.stApp {background-color: #FFFFFF;}</style>", unsafe_allow_html=True)
    
    # Barra de navegação do dashboard
    c_back, c_title = st.columns([1, 8])
    if c_back.button("⬅️ Voltar"):
        st.session_state.page = 'menu'
        st.rerun()
    c_title.subheader(st.session_state.get('report_name', 'Relatório'))

    # Iframe de visualização focada
    st.markdown(f'<iframe src="{st.session_state.report_url}" width="100%" height="880px" frameborder="0" allowFullScreen="true"></iframe>', unsafe_allow_html=True)