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
            
            /* --- TELA 1 (LOGIN) --- */
            .main-title-login {
                color: #000000 !important; font-size: 58px; font-weight: 800;
                text-align: center; margin-top: 5vh;
            }
            .label-dark { 
                color: #000000 !important; font-size: 19px; font-weight: 500; 
                margin-top: 15px; margin-bottom: 5px; display: block;
            }
            /* Botão Vermelho Restaurado (#ED3237) */
            .btn-acessar button {
                background-color: #ED3237 !important; color: white !important;
                height: 55px !important; font-size: 20px !important; font-weight: bold !important;
                border-radius: 10px !important; border: none !important; margin-top: 20px;
            }
            .empresa-logo { position: absolute; top: 15px; right: 35px; z-index: 999; }

            /* --- TELA 2 (LISTA LOVABLE) --- */
            /* Botão Sair */
            div[data-testid="stBaseButton-secondary"] {
                background-color: #F1F5F9 !important; color: #0F172A !important;
                border: 1px solid #E2E8F0 !important; border-radius: 6px !important;
            }
            
            /* Cabeçalho da Tabela */
            .lovable-header {
                font-size: 14px; font-weight: 600; color: #64748B;
                padding-bottom: 10px; border-bottom: 1px solid #E2E8F0;
                margin-bottom: 10px;
            }
            
            /* Linhas da Tabela */
            .lovable-row {
                padding: 15px 0; border-bottom: 1px solid #F1F5F9;
                display: flex; align-items: center; transition: 0.2s;
            }
            .lovable-text { color: #334155; font-size: 15px; font-weight: 500; }
            .lovable-sub { color: #64748B; font-size: 14px; }
            
            /* Botão Link (Nome do Relatório) */
            .stButton button {
                text-align: left; padding-left: 0;
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

# --- TELA 2: LISTA DE RELATÓRIOS (ESTILO LOVABLE) ---
elif st.session_state.page == 'menu':
    # Barra de Boas-vindas
    c1, c2 = st.columns([6, 1])
    c1.markdown(f"<h2 style='color: #0F172A; margin:0;'>Olá, {st.session_state.user_info['nome']}</h2>", unsafe_allow_html=True)
    if c2.button("Sair", key="logout_btn", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.write("##")
    
    # Cabeçalho da Tabela (Estilo Lovable Image)
    # Colunas: Nome (4) | Departamento (2) | Plataforma (2) | Status (1)
    with st.container():
        h1, h2, h3, h4 = st.columns([4, 2, 2, 1])
        h1.markdown('<div class="lovable-header">PAINEL / RELATÓRIO</div>', unsafe_allow_html=True)
        h2.markdown('<div class="lovable-header">DEPARTAMENTO</div>', unsafe_allow_html=True)
        h3.markdown('<div class="lovable-header">PLATAFORMA</div>', unsafe_allow_html=True)
        h4.markdown('<div class="lovable-header">STATUS</div>', unsafe_allow_html=True) # 4ª Coluna Sugerida

    # Conteúdo da Lista
    df_u, df_r, df_rel = carregar_dados()
    if df_rel is not None:
        meus_ids = df_rel[df_rel['usuario_id'] == st.session_state.user_info['usuario_id']]
        meus_relatorios = pd.merge(meus_ids[['relatorio_id']], df_r, on='relatorio_id', how='inner')

        for i, (_, row) in enumerate(meus_relatorios.iterrows()):
            with st.container():
                # Fundo alternado para efeito visual (opcional)
                bg_style = "background-color: #F8FAFC;" if i % 2 == 0 else "background-color: #FFFFFF;"
                
                c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
                
                # Coluna 1: Botão Link (Nome) - Ação Principal
                with c1:
                    # Usamos um botão transparente que parece texto para ser clicável
                    if st.button(f"📊 {row['nome_relatorio']}", key=f"lnk_{row['relatorio_id']}"):
                        st.session_state.report_url = row['link']
                        st.session_state.report_name = row['nome_relatorio']
                        st.session_state.page = 'view'
                        st.rerun()

                # Coluna 2: Categoria/Departamento
                with c2:
                    st.markdown(f'<div class="lovable-sub" style="padding-top: 10px;">{row["categoria"]}</div>', unsafe_allow_html=True)

                # Coluna 3: Plataforma (Power BI fixo ou vindo do excel se tiver coluna)
                with c3:
                    st.markdown(f'<div class="lovable-text" style="padding-top: 10px;">⚡ Power BI</div>', unsafe_allow_html=True)

                # Coluna 4: Status (Sugestão Visual)
                with c4:
                    st.markdown(f'<div style="padding-top: 10px; color: #10B981; font-weight:bold; font-size:12px;">🟢 Online</div>', unsafe_allow_html=True)
                
                st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #F1F5F9;'>", unsafe_allow_html=True)

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