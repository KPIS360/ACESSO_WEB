import streamlit as st
import pandas as pd
import base64
import requests
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
# 3. CSS (DESIGN SYSTEM LOVABLE REFINADO)
# ==============================================================================
def apply_styles():
    st.markdown("""
        <style>
            /* Reset e Base */
            #MainMenu, footer, header {visibility: hidden;}
            .block-container {padding: 0rem !important; max-width: 100% !important;}
            .stApp { 
                background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            
            /* ============================================
               TELA 1: LOGIN 
            ============================================ */
            .login-container {
                max-width: 480px;
                margin: 0 auto;
                padding: 40px 20px;
            }
            
            .main-title-login {
                color: #1a1a1a !important; 
                font-size: 42px; 
                font-weight: 700;
                text-align: center; 
                margin: 30px 0 10px 0;
                letter-spacing: -0.5px;
            }
            
            .logo-container {
                text-align: center;
                margin: 40px 0;
            }
            
            .empresa-logo { 
                position: absolute; 
                top: 20px; 
                right: 40px; 
                z-index: 999;
            }
            
            .label-dark { 
                color: #2d3748 !important; 
                font-size: 15px; 
                font-weight: 600; 
                margin-top: 20px; 
                margin-bottom: 8px; 
                display: block;
            }
            
            /* Inputs da Tela de Login */
            .stTextInput input {
                border-radius: 8px !important;
                border: 1.5px solid #e2e8f0 !important;
                padding: 12px 16px !important;
                font-size: 15px !important;
                transition: all 0.2s ease !important;
                background-color: #ffffff !important;
            }
            
            .stTextInput input:focus {
                border-color: #ED3237 !important;
                box-shadow: 0 0 0 3px rgba(237, 50, 55, 0.1) !important;
            }
            
            /* Botão Login (Primary) */
            div[data-testid="stButton"] button[kind="primary"] {
                background: linear-gradient(135deg, #ED3237 0%, #d42a2f 100%) !important;
                color: white !important;
                height: 52px !important; 
                font-size: 16px !important; 
                font-weight: 600 !important;
                border-radius: 8px !important; 
                border: none !important;
                width: 100%;
                box-shadow: 0 4px 12px rgba(237, 50, 55, 0.25) !important;
                transition: all 0.3s ease !important;
                letter-spacing: 0.3px;
            }
            
            div[data-testid="stButton"] button[kind="primary"]:hover {
                background: linear-gradient(135deg, #d42a2f 0%, #c2282d 100%) !important;
                transform: translateY(-1px);
                box-shadow: 0 6px 16px rgba(237, 50, 55, 0.35) !important;
            }

            /* ============================================
               TELA 2: LISTA DE RELATÓRIOS 
            ============================================ */
            
            .main-header {
                background-color: #ffffff;
                padding: 24px 40px;
                border-bottom: 1px solid #e2e8f0;
                margin-bottom: 0;
            }
            
            .welcome-text {
                color: #1a202c;
                font-size: 28px;
                font-weight: 700;
                margin: 0;
                letter-spacing: -0.3px;
            }
            
            /* Botão Sair (Secondary) */
            div[data-testid="stButton"] button[kind="secondary"] {
                background-color: #f8fafc !important; 
                color: #475569 !important;
                border: 1.5px solid #e2e8f0 !important; 
                border-radius: 8px !important;
                font-weight: 600 !important;
                font-size: 14px !important;
                padding: 10px 24px !important;
                transition: all 0.2s ease !important;
                height: 42px !important;
            }
            
            div[data-testid="stButton"] button[kind="secondary"]:hover {
                background-color: #f1f5f9 !important;
                border-color: #cbd5e1 !important;
                transform: translateY(-1px);
            }
            
            /* Container da Tabela */
            .reports-container {
                background-color: #ffffff;
                border-radius: 12px;
                padding: 32px;
                margin: 24px 40px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            }
            
            /* Cabeçalho da Tabela */
            .table-header {
                font-family: 'Inter', sans-serif;
                font-size: 13px;
                font-weight: 700;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                padding-bottom: 16px;
                border-bottom: 2px solid #f1f5f9;
                margin-bottom: 4px;
            }

            /* Linhas da Tabela */
            .table-row {
                padding: 20px 0;
                border-bottom: 1px solid #f8fafc;
                transition: background-color 0.2s ease;
            }
            
            .table-row:hover {
                background-color: #fafbfc;
            }
            
            /* Texto Principal da Tabela */
            .table-text {
                font-family: 'Inter', sans-serif;
                font-size: 15px;
                font-weight: 600;
                color: #1e293b;
                line-height: 1.6;
            }
            
            /* Texto Secundário */
            .table-sub {
                font-family: 'Inter', sans-serif;
                font-size: 14px;
                font-weight: 500;
                color: #64748b;
                line-height: 1.6;
            }

            /* Botão "Acessar" como Link */
            .action-link button {
                background: none !important;
                border: none !important;
                padding: 0 !important;
                color: #3b82f6 !important;
                text-decoration: none !important;
                font-size: 14px !important;
                font-weight: 600 !important;
                cursor: pointer !important;
                transition: color 0.2s ease !important;
            }
            
            .action-link button:hover {
                color: #2563eb !important;
                text-decoration: underline !important;
            }
            
            /* Badge Power BI */
            .badge-powerbi {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background-color: #f8f4ff;
                color: #7c3aed;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
            }
            
            /* Status Online */
            .status-online {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                color: #10b981;
                font-size: 14px;
                font-weight: 600;
            }
            
            .status-dot {
                width: 8px;
                height: 8px;
                background-color: #10b981;
                border-radius: 50%;
                display: inline-block;
            }

            /* ============================================
               TELA 3: VISUALIZAÇÃO DO RELATÓRIO 
            ============================================ */
            
            .view-header {
                background-color: #ffffff;
                padding: 16px 40px;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .view-title {
                font-size: 20px;
                font-weight: 700;
                color: #1e293b;
                margin: 0;
            }
            
            /* Botão Voltar */
            .btn-back {
                background-color: #f8fafc !important;
                color: #475569 !important;
                border: 1.5px solid #e2e8f0 !important;
                border-radius: 8px !important;
                font-weight: 600 !important;
                padding: 8px 16px !important;
            }
            
            /* Iframe Container */
            .iframe-container {
                padding: 0;
                margin: 0;
                height: calc(100vh - 80px);
            }
            
            /* Responsividade */
            @media (max-width: 768px) {
                .reports-container {
                    margin: 16px;
                    padding: 20px;
                }
                
                .main-header {
                    padding: 16px 20px;
                }
                
                .table-header {
                    font-size: 11px;
                }
                
                .table-text {
                    font-size: 14px;
                }
            }
        </style>
    """, unsafe_allow_html=True)

apply_styles()

# ==============================================================================
# 4. LÓGICA DE NAVEGAÇÃO
# ==============================================================================

# --- TELA 1: LOGIN ---
if st.session_state.page == 'login':
    # Logo da Empresa no canto superior direito
    emp_base = get_base64(PATH_IMG / "empresa1.jpg")
    if emp_base:
        st.markdown(f'<div class="empresa-logo"><img src="data:image/jpg;base64,{emp_base}" width="100"></div>', unsafe_allow_html=True)

    # Container centralizado
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Título
    st.markdown('<h1 class="main-title-login">Portal CIG 360º | GIROAgro</h1>', unsafe_allow_html=True)
    
    # Logo CIG 360
    logo_base = get_base64(PATH_IMG / "logo.png")
    if logo_base:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.markdown(f'<img src="data:image/png;base64,{logo_base}" width="280">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Formulário
    st.markdown('<label class="label-dark">E-mail Corporativo:</label>', unsafe_allow_html=True)
    email_in = st.text_input("", placeholder="usuario@giroagro.com.br", key="email", label_visibility="collapsed")
    
    st.markdown('<label class="label-dark">Senha:</label>', unsafe_allow_html=True)
    senha_in = st.text_input("", type="password", placeholder="••••••••", key="senha", label_visibility="collapsed")
    
    st.write("")
    st.write("")
    
    # Botão de Login
    if st.button("ACESSAR PORTAL", type="primary", use_container_width=True):
        df_u, _, _ = carregar_dados()
        if df_u is not None:
            user = df_u[(df_u['email'].str.strip() == email_in.strip()) & (df_u['senha'].astype(str) == senha_in)]
            if not user.empty:
                st.session_state.user_info = user.iloc[0].to_dict()
                st.session_state.page = 'menu'
                registrar_log(st.session_state.user_info['nome'], email_in, "LOGIN")
                st.rerun()
            else:
                st.error("❌ Credenciais inválidas. Verifique seu e-mail e senha.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- TELA 2: LISTA DE RELATÓRIOS ---
elif st.session_state.page == 'menu':
    # Cabeçalho
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown(f'<h2 class="welcome-text">Olá, {st.session_state.user_info["nome"]}</h2>', unsafe_allow_html=True)
    with col2:
        if st.button("Sair", type="secondary", key="logout_btn", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Container da Tabela
    st.markdown('<div class="reports-container">', unsafe_allow_html=True)
    
    # Cabeçalho da Tabela
    h1, h2, h3, h4, h5 = st.columns([3, 1.5, 2, 1.5, 1.2])
    with h1:
        st.markdown('<div class="table-header">Relatório</div>', unsafe_allow_html=True)
    with h2:
        st.markdown('<div class="table-header">Acesso</div>', unsafe_allow_html=True)
    with h3:
        st.markdown('<div class="table-header">Categoria</div>', unsafe_allow_html=True)
    with h4:
        st.markdown('<div class="table-header">Ferramenta</div>', unsafe_allow_html=True)
    with h5:
        st.markdown('<div class="table-header">Status</div>', unsafe_allow_html=True)

    # Dados
    df_u, df_r, df_rel = carregar_dados()
    if df_rel is not None and df_r is not None:
        meus_ids = df_rel[df_rel['usuario_id'] == st.session_state.user_info['usuario_id']]
        meus_relatorios = pd.merge(meus_ids[['relatorio_id']], df_r, on='relatorio_id', how='inner')

        for idx, (_, row) in enumerate(meus_relatorios.iterrows()):
            st.markdown('<div class="table-row">', unsafe_allow_html=True)
            
            c1, c2, c3, c4, c5 = st.columns([3, 1.5, 2, 1.5, 1.2])
            
            # Nome do Relatório
            with c1:
                st.markdown(f'<div class="table-text">{row["nome_relatorio"]}</div>', unsafe_allow_html=True)

            # Botão Acessar
            with c2:
                st.markdown('<div class="action-link">', unsafe_allow_html=True)
                if st.button("Acessar", key=f"btn_{row['relatorio_id']}"):
                    st.session_state.report_url = row['link']
                    st.session_state.report_name = row['nome_relatorio']
                    st.session_state.page = 'view'
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            # Categoria
            with c3:
                st.markdown(f'<div class="table-sub">{row["categoria"]}</div>', unsafe_allow_html=True)

            # Ferramenta (Power BI Badge)
            with c4:
                st.markdown('<div class="badge-powerbi">📊 Power BI</div>', unsafe_allow_html=True)

            # Status
            with c5:
                st.markdown('<div class="status-online"><span class="status-dot"></span>Online</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- TELA 3: VISUALIZAÇÃO DO RELATÓRIO ---
elif st.session_state.page == 'view':
    # Cabeçalho
    col_back, col_title, col_exit = st.columns([1, 8, 1])
    
    with col_back:
        if st.button("← Voltar", key="btn_voltar"):
            st.session_state.page = 'menu'
            st.rerun()
    
    with col_title:
        st.markdown(f'<h4 class="view-title" style="text-align: center;">{st.session_state.report_name}</h4>', unsafe_allow_html=True)
    
    with col_exit:
        if st.button("Sair", type="secondary", key="btn_sair_view"):
            st.session_state.clear()
            st.rerun()

    # Iframe
    st.markdown(f'''
        <div class="iframe-container">
            <iframe 
                src="{st.session_state.report_url}" 
                width="100%" 
                height="100%" 
                frameborder="0" 
                allowFullScreen="true">
            </iframe>
        </div>
    ''', unsafe_allow_html=True)