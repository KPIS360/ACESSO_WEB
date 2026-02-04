import streamlit as st
import pandas as pd
import base64
import os
import requests
import time
from pathlib import Path
from datetime import datetime

# ==============================================================================
# 1. CONFIGURAÇÕES DE CAMINHOS E SEGURANÇA
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_DATA = BASE_DIR / "data"
PATH_IMG = BASE_DIR / "assets"

st.set_page_config(page_title="Portal CIG 360", layout="wide", initial_sidebar_state="collapsed")

# Inicialização segura do Session State
if 'page' not in st.session_state:
    st.session_state.page = 'login'

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
        st.error(f"Erro ao acessar base de dados: {e}")
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
# 3. ESTILIZAÇÃO CSS (TELAS 1 E 2)
# ==============================================================================
def apply_styles():
    st.markdown("""
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .block-container {padding: 0rem !important;}
            
            /* --- ESTILOS TELA 1 (LOGIN) --- */
            .main-title-login {
                color: #000000 !important; font-size: 58px; font-weight: 800;
                text-align: center; margin-top: 5vh;
            }
            .label-dark { 
                color: #000000 !important; font-size: 19px; font-weight: 500; 
                margin-top: 15px; margin-bottom: 5px; display: block;
            }
            .btn-acessar button {
                background-color: #ED3237 !important; color: white !important;
                height: 55px !important; font-size: 20px !important; font-weight: bold !important;
                border-radius: 10px !important; border: none !important; margin-top: 20px;
            }
            .empresa-logo { position: absolute; top: 15px; right: 35px; z-index: 999; }

            /* --- ESTILOS TELA 2 (MENU LOVABLE) --- */
            .stApp { background-color: #FFFFFF; }
            
            .report-card-lovable {
                background: white;
                padding: 24px;
                border-radius: 16px;
                border: 1px solid #E2E8F0;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                transition: all 0.3s ease;
                text-align: center;
                margin-bottom: 10px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .report-card-lovable:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                border-color: #ED3237;
            }
            
            /* Botão Sair Customizado */
            div[data-testid="stBaseButton-secondary"] {
                background-color: #F0F2F6 !important;
                color: #000000 !important;
                border: none !important;
                border-radius: 8px !important;
            }
        </style>
    """, unsafe_allow_html=True)

apply_styles()

# ==============================================================================
# 4. LÓGICA DE TELAS
# ==============================================================================

# --- TELA 1: LOGIN ---
if st.session_state.page == 'login':
    # Logo Empresa reduzida (110px conforme pedido)
    emp_base = get_base64(PATH_IMG / "empresa1.jpg")
    if emp_base:
        st.markdown(f'<div class="empresa-logo"><img src="data:image/jpg;base64,{emp_base}" width="110"></div>', unsafe_allow_html=True)

    st.markdown('<h1 class="main-title-login">Portal CIG 360º | GIROAgro</h1>', unsafe_allow_html=True)
    
    _, col_logo, _ = st.columns([1, 0.35, 1])
    with col_logo:
        logo_base = get_base64(PATH_IMG / "logo.png")
        if logo_base:
            st.image(f"data:image/png;base64,{logo_base}", use_container_width=True)

    _, col_form, _ = st.columns([1, 1, 1])
    with col_form:
        st.write("##")
        st.markdown('<label class="label-dark">E-mail Corporativo:</label>', unsafe_allow_html=True)
        email_in = st.text_input("", placeholder="usuario@giroagro.com.br", key="email", label_visibility="collapsed")
        
        st.markdown('<label class="label-dark">Senha:</label>', unsafe_allow_html=True)
        senha_in = st.text_input("", type="password", placeholder="••••••••", key="senha", label_visibility="collapsed")
        
        st.markdown('<div class="btn-acessar">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

# --- TELA 2: MENU (LISTA LOVABLE) ---
elif st.session_state.page == 'menu':
    # Barra Superior
    col_welcome, col_exit = st.columns([6, 1])
    with col_welcome:
        st.markdown(f"<h2 style='color: #1E293B; padding-left: 20px;'>Olá, {st.session_state.user_info['nome']}</h2>", unsafe_allow_html=True)
    with col_exit:
        if st.button("Sair", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.write("---")
    _, col_content, _ = st.columns([0.1, 5, 0.1])
    
    with col_content:
        st.markdown("#### 📂 Selecione seu relatório abaixo:")
        df_u, df_r, df_rel = carregar_dados()
        
        if df_rel is not None:
            meus_ids = df_rel[df_rel['usuario_id'] == st.session_state.user_info['usuario_id']]
            meus_relatorios = pd.merge(meus_ids[['relatorio_id']], df_r, on='relatorio_id', how='inner')
            
            # Grid de Relatórios
            grid_cols = st.columns(3)
            for i, (_, row) in enumerate(meus_relatorios.iterrows()):
                with grid_cols[i % 3]:
                    st.markdown(f"""
                        <div class="report-card-lovable">
                            <div style="color: #64748B; font-size: 12px; font-weight: 600;">{row['categoria'].upper()}</div>
                            <div style="color: #1E293B; font-size: 18px; font-weight: 700; margin: 10px 0;">📊 {row['nome_relatorio']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("Abrir Painel", key=f"btn_{row['relatorio_id']}", use_container_width=True):
                        st.session_state.report_url = row['link']
                        st.session_state.report_name = row['nome_relatorio']
                        st.session_state.page = 'view'
                        st.rerun()

# --- TELA 3: VIEW (DASHBOARD) ---
elif st.session_state.page == 'view':
    c_back, c_title, c_exit = st.columns([1, 8, 1])
    if c_back.button("⬅️ Voltar"):
        st.session_state.page = 'menu'
        st.rerun()
    c_title.markdown(f"<h4 style='text-align: center;'>{st.session_state.report_name}</h4>", unsafe_allow_html=True)
    if c_exit.button("Sair"):
        st.session_state.clear()
        st.rerun()

    st.markdown(f'<iframe src="{st.session_state.report_url}" width="100%" height="880px" frameborder="0" allowFullScreen="true"></iframe>', unsafe_allow_html=True)