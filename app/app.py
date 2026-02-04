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
# 3. CSS (DESIGN SYSTEM ROBUSTO)
# ==============================================================================
def apply_styles():
    st.markdown("""
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .block-container {padding: 0rem !important;}
            .stApp { background-color: #FFFFFF; }
            
            /* --- TELA 1: LOGIN (CONTRASTE E CORES) --- */
            .main-title-login {
                color: #000000 !important; font-size: 58px; font-weight: 800;
                text-align: center; margin-top: 5vh;
            }
            .label-dark { 
                color: #000000 !important; font-size: 19px; font-weight: 600; 
                margin-top: 15px; margin-bottom: 5px; display: block;
            }
            
            /* FORÇAR COR VERMELHA NO BOTÃO PRIMÁRIO (LOGIN) */
            div[data-testid="stButton"] button[kind="primary"] {
                background-color: #ED3237 !important; 
                color: white !important;
                height: 55px !important; 
                font-size: 20px !important; 
                font-weight: bold !important;
                border-radius: 10px !important; 
                border: none !important;
                width: 100%;
            }
            div[data-testid="stButton"] button[kind="primary"]:hover {
                background-color: #c2282d !important;
            }

            .empresa-logo { position: absolute; top: 15px; right: 35px; z-index: 999; }

            /* --- TELA 2: LISTA LOVABLE (FONTS MAIORES) --- */
            
            /* Botão Sair (Secundário) */
            div[data-testid="stButton"] button[kind="secondary"] {
                background-color: #F1F5F9 !important; 
                color: #0F172A !important;
                border: 1px solid #E2E8F0 !important; 
                border-radius: 6px !important;
                font-weight: 600;
            }

            /* Cabeçalho da Tabela */
            .table-header {
                font-family: 'Inter', sans-serif;
                font-size: 16px; /* Aumentado */
                font-weight: 700;
                color: #64748B;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                padding-bottom: 12px;
                border-bottom: 2px solid #E2E8F0;
                margin-bottom: 10px;
            }

            /* Texto Geral da Tabela */
            .table-text {
                font-family: 'Inter', sans-serif;
                font-size: 18px; /* Aumentado para legibilidade */
                font-weight: 500;
                color: #0F172A;
                padding-top: 15px;
            }
            
            .table-sub {
                font-family: 'Inter', sans-serif;
                font-size: 18px;
                color: #475569;
                padding-top: 15px;
            }

            /* Coluna Ação (Link Style) */
            .action-link button {
                background: none !important;
                border: none !important;
                padding: 0 !important;
                color: #2563EB !important;
                text-decoration: none !important;
                font-size: 18px !important;
                font-weight: 600 !important;
                margin-top: 15px !important;
                cursor: pointer !important;
            }
            .action-link button:hover {
                color: #1d4ed8 !important;
                text-decoration: underline !important;
            }

            /* Divisória */
            .divider { border-bottom: 1px solid #F1F5F9; margin: 10px 0; }
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
        
        st.write("##")
        # Usando type='primary' para o CSS capturar e aplicar o vermelho
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
                    st.error("Credenciais inválidas.")

# --- TELA 2: LISTA DE RELATÓRIOS (5 COLUNAS) ---
elif st.session_state.page == 'menu':
    # Header
    c1, c2 = st.columns([6, 1])
    c1.markdown(f"<h2 style='color: #0F172A; margin:0;'>Olá, {st.session_state.user_info['nome']}</h2>", unsafe_allow_html=True)
    # Botão Sair como 'secondary' para não ficar vermelho
    if c2.button("Sair", type="secondary", key="logout_btn", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.write("##")
    
    # Cabeçalho da Tabela (5 Colunas)
    # Proporção ajustada para caber tudo: 3 | 2 | 2 | 1.5 | 1
    with st.container():
        h1, h2, h3, h4, h5 = st.columns([3, 2, 2, 1.5, 1])
        h1.markdown('<div class="table-header">NOME RELATÓRIO</div>', unsafe_allow_html=True)
        h2.markdown('<div class="table-header">ACESSAR RELATÓRIO</div>', unsafe_allow_html=True)
        h3.markdown('<div class="table-header">DEPARTAMENTO</div>', unsafe_allow_html=True)
        h4.markdown('<div class="table-header">FERRAMENTA</div>', unsafe_allow_html=True)
        h5.markdown('<div class="table-header">STATUS</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # Lista de Dados
    df_u, df_r, df_rel = carregar_dados()
    if df_rel is not None:
        meus_ids = df_rel[df_rel['usuario_id'] == st.session_state.user_info['usuario_id']]
        meus_relatorios = pd.merge(meus_ids[['relatorio_id']], df_r, on='relatorio_id', how='inner')

        for i, (_, row) in enumerate(meus_relatorios.iterrows()):
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 1.5, 1])
                
                # 1. Nome Relatório
                with c1:
                    st.markdown(f'<div class="table-text">{row["nome_relatorio"]}</div>', unsafe_allow_html=True)

                # 2. Acessar Relatório (Ação em texto azul clicável)
                with c2:
                    st.markdown('<div class="action-link">', unsafe_allow_html=True)
                    if st.button("Acessar Relatório", key=f"lnk_{row['relatorio_id']}"):
                        st.session_state.report_url = row['link']
                        st.session_state.report_name = row['nome_relatorio']
                        st.session_state.page = 'view'
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                # 3. Departamento
                with c3:
                    st.markdown(f'<div class="table-sub">{row["categoria"]}</div>', unsafe_allow_html=True)

                # 4. Ferramenta
                with c4:
                    st.markdown(f'<div class="table-sub">Power BI</div>', unsafe_allow_html=True)

                # 5. Status
                with c5:
                    st.markdown(f'<div class="table-text" style="color: #10B981; font-size: 16px;">🟢 Online</div>', unsafe_allow_html=True)
                
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