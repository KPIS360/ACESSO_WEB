import streamlit as st
import pandas as pd
import base64
import os
import requests
import time
from pathlib import Path
from datetime import datetime

# ==============================================================================
# 1. CONFIGURAÇÕES
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_DATA = BASE_DIR / "data"
PATH_IMG = BASE_DIR / "assets"

st.set_page_config(page_title="Portal CIG 360", layout="wide", initial_sidebar_state="collapsed")

if 'page' not in st.session_state:
    st.session_state.page = 'login'

def get_base64(file_path):
    if file_path.exists():
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# ==============================================================================
# 2. DADOS E LOGS
# ==============================================================================
def carregar_dados():
    try:
        u = pd.read_excel(PATH_DATA / 'usuarios.xlsx')
        r = pd.read_excel(PATH_DATA / 'relatorios.xlsx')
        rel = pd.read_excel(PATH_DATA / 'relacional.xlsx')
        return u, r, rel
    except Exception as e:
        st.error(f"Erro ao acessar dados: {e}")
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
# 3. CSS (DESIGN SYSTEM)
# ==============================================================================
def apply_styles():
    st.markdown("""
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .block-container {padding: 0rem !important;}
            .stApp { background-color: #FFFFFF; }
            
            /* --- TELA 1 (LOGIN) - MANTIDA --- */
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

            /* --- TELA 2 (LISTA LOVABLE CLEAN) --- */
            
            /* Botão Sair - Discreto */
            div[data-testid="stBaseButton-secondary"] {
                background-color: #F1F5F9 !important; color: #0F172A !important;
                border: 1px solid #E2E8F0 !important; border-radius: 6px !important;
            }

            /* Cabeçalho da Tabela */
            .table-header {
                font-family: 'Inter', sans-serif;
                font-size: 14px;
                font-weight: 600;
                color: #64748B;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                padding-bottom: 12px;
                border-bottom: 2px solid #E2E8F0;
                margin-bottom: 10px;
            }

            /* Texto do Relatório (Coluna 1) */
            .report-name {
                font-family: 'Inter', sans-serif;
                font-size: 18px; /* Aumentado */
                font-weight: 500;
                color: #0F172A;
                padding: 18px 0;
            }

            /* "Botão" Texto (Coluna 2) - Transformando botão em link */
            .btn-link button {
                background-color: transparent !important;
                border: none !important;
                color: #2563EB !important; /* Azul Link */
                font-weight: 600 !important;
                font-size: 16px !important;
                text-decoration: none !important;
                box-shadow: none !important;
                padding: 0 !important;
                margin-top: 15px !important; /* Alinhamento visual */
                display: flex;
                justify-content: flex-end; /* Alinha a direita */
            }
            .btn-link button:hover {
                color: #1e40af !important;
                text-decoration: underline !important;
            }

            /* Linha Divisória Customizada */
            .divider {
                border-bottom: 1px solid #F1F5F9;
                margin: 0;
            }
        </style>
    """, unsafe_allow_html=True)

apply_styles()

# ==============================================================================
# 4. LÓGICA DE NAVEGAÇÃO
# ==============================================================================

# --- TELA 1: LOGIN ---
if st.session_state.page == 'login':
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

# --- TELA 2: LISTA DE RELATÓRIOS (ESTILO TABELA LOVABLE) ---
elif st.session_state.page == 'menu':
    # Header com Nome e Sair
    c1, c2 = st.columns([6, 1])
    c1.markdown(f"<h2 style='color: #0F172A; margin:0;'>Olá, {st.session_state.user_info['nome']}</h2>", unsafe_allow_html=True)
    if c2.button("Sair", key="logout_btn", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.write("##")
    
    # Cabeçalho da Lista
    # Proporção: Nome (5 partes) | Ação (1 parte)
    with st.container():
        h1, h2 = st.columns([5, 1])
        h1.markdown('<div class="table-header">NOME DO RELATÓRIO</div>', unsafe_allow_html=True)
        h2.markdown('<div class="table-header" style="text-align: right;">AÇÃO</div>', unsafe_allow_html=True)

    # Lista de Relatórios
    df_u, df_r, df_rel = carregar_dados()
    if df_rel is not None:
        meus_ids = df_rel[df_rel['usuario_id'] == st.session_state.user_info['usuario_id']]
        meus_relatorios = pd.merge(meus_ids[['relatorio_id']], df_r, on='relatorio_id', how='inner')

        for i, (_, row) in enumerate(meus_relatorios.iterrows()):
            # Container da linha para organização
            with st.container():
                c_name, c_action = st.columns([5, 1])
                
                # Coluna 1: Nome do Relatório (Texto Limpo e Maior)
                with c_name:
                    st.markdown(f'<div class="report-name">{row["nome_relatorio"]}</div>', unsafe_allow_html=True)

                # Coluna 2: Ação (Botão disfarçado de Link)
                with c_action:
                    st.markdown('<div class="btn-link">', unsafe_allow_html=True)
                    # O texto do botão é "Abrir Relatório" conforme pedido, mas parece um link azul
                    if st.button("Abrir Relatório", key=f"lnk_{row['relatorio_id']}"):
                        st.session_state.report_url = row['link']
                        st.session_state.report_name = row['nome_relatorio']
                        st.session_state.page = 'view'
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Divisória sutil entre linhas
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# --- TELA 3: VIEW ---
elif st.session_state.page == 'view':
    c_back, c_title, c_exit = st.columns([1, 8, 1])
    if c_back.button("⬅️ Voltar"):
        st.session_state.page = 'menu'
        st.rerun()
    c_title.markdown(f"<h4 style='text-align: center; color: #0F172A;'>{st.session_state.report_name}</h4>", unsafe_allow_html=True)
    if c_exit.button("Sair"):
        st.session_state.clear()
        st.rerun()

    st.markdown(f'<iframe src="{st.session_state.report_url}" width="100%" height="880px" frameborder="0" allowFullScreen="true"></iframe>', unsafe_allow_html=True)