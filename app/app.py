import streamlit as st
import pandas as pd
import time
import requests
import os
import base64
from datetime import datetime
from pathlib import Path

# ==============================================================================
# 1. CONFIGURAÇÕES E CAMINHOS
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_DATA = BASE_DIR / "data"
PATH_IMG = BASE_DIR / "assets"

st.set_page_config(page_title="CIG 360º", layout="wide", initial_sidebar_state="collapsed")

# Função para converter imagem local em Base64 (Garante que o fundo funcione no Cloud)
def get_base64(file_path):
    if file_path.exists():
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# ==============================================================================
# 2. ESTILIZAÇÃO CUSTOMIZADA (LOVABLE STYLE)
# ==============================================================================
def apply_styles(page):
    # Estilos globais para esconder menus
    hide_style = """
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .block-container {padding: 0rem !important;}
        </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

    if page == 'login':
        bg_base64 = get_base64(PATH_IMG / "fundologin.jpg")
        bg_css = f"background-image: url('data:image/jepg;base64,{bg_base64}');" if bg_base64 else "background-color: #1e3a8a;"
        
        st.markdown(f"""
            <style>
                .stApp {{
                    {bg_css}
                    background-size: cover;
                }}
                .login-card {{
                    background: rgba(255, 255, 255, 0.95);
                    padding: 3rem;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
                    text-align: center;
                    max-width: 450px;
                    margin: auto;
                }}
                .main-title {{ font-size: 65px; font-weight: 900; color: #1e3a8a; line-height: 1; margin: 10px 0; }}
            </style>
        """, unsafe_allow_html=True)
    
    else:
        # Estilo para Telas Internas (Limpo e Focado)
        st.markdown("""
            <style>
                .stApp { background-color: #f8fafc; }
                .report-item {
                    background: white;
                    padding: 1.5rem;
                    border-radius: 12px;
                    border-left: 5px solid #1e3a8a;
                    margin-bottom: 1rem;
                    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                    transition: transform 0.2s;
                }
                .report-item:hover { transform: translateX(10px); }
            </style>
        """, unsafe_allow_html=True)

# ==============================================================================
# 3. NAVEGAÇÃO E TELAS
# ==============================================================================

if 'page' not in st.session_state:
    st.session_state.page = 'login'

# --- TELA 1: LOGIN ---
if st.session_state.page == 'login':
    apply_styles('login')
    st.write("#") # Espaçador
    st.write("#")
    
    _, col_card, _ = st.columns([1, 1.2, 1])
    
    with col_card:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # [Caixa 1] Logo principal
        if (PATH_IMG / "logo.png").exists():
            st.image(str(PATH_IMG / "logo.png"), width=180)
        
        st.markdown('<h1 class="main-title">CIG 360º</h1>', unsafe_allow_html=True)
        
        # [Caixa 2] Logo Empresa
        if (PATH_IMG / "empresa1.jpg").exists():
            st.image(str(PATH_IMG / "empresa1.jpg"), width=120)
        
        st.write("---")
        user_in = st.text_input("Usuário", placeholder="email@exemplo.com")
        pass_in = st.text_input("Senha", type="password")
        
        if st.button("ACESSAR PORTAL", use_container_width=True):
            # Lógica de validação (Simulação ou carregar_dados())
            from app_functions import carregar_dados # Se estiver em arquivo separado
            df_u, _, _ = carregar_dados(PATH_DATA)
            match = df_u[(df_u['email'] == user_in) & (df_u['senha'].astype(str) == pass_in)]
            if not match.empty:
                st.session_state.user = match.iloc[0].to_dict()
                st.session_state.page = 'menu'
                st.rerun()
            else:
                st.error("Credenciais Inválidas")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TELA 2: LISTA DE RELATÓRIOS ---
elif st.session_state.page == 'menu':
    apply_styles('menu')
    
    with st.container():
        c1, c2 = st.columns([5, 1])
        c1.markdown(f"## Olá, {st.session_state.user['nome']}")
        if c2.button("Sair 🚪", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.write("### 📂 Selecione um relatório para visualizar")
    
    # Busca e Filtros
    from app_functions import carregar_dados, get_meus_relatorios
    _, df_r, df_rel = carregar_dados(PATH_DATA)
    meus_relatorios = get_meus_relatorios(df_rel, df_r, st.session_state.user['usuario_id'])
    
    search = st.text_input("🔍 Buscar por nome...", placeholder="Digite o nome do painel")
    
    for _, row in meus_relatorios.iterrows():
        if search.lower() in row['nome_relatorio'].lower():
            with st.container():
                st.markdown(f"""
                <div class="report-item">
                    <p style="margin:0; color:#64748b; font-size:12px; font-weight:bold;">{row['categoria'].upper()}</p>
                    <h4 style="margin:0; color:#1e293b;">{row['nome_relatorio']}</h4>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Abrir Dashboard", key=f"id_{row['relatorio_id']}", use_container_width=True):
                    st.session_state.current_rel = row.to_dict()
                    st.session_state.page = 'view'
                    st.rerun()

# --- TELA 3: FOCO TOTAL ---
elif st.session_state.page == 'view':
    apply_styles('view')
    
    # Barra Superior Minimalista
    header = st.columns([8, 1, 1])
    header[0].markdown(f"**Exibindo:** {st.session_state.current_rel['nome_relatorio']}")
    if header[1].button("⬅️ Voltar", use_container_width=True):
        st.session_state.page = 'menu'
        st.rerun()
    if header[2].button("Sair 🚪", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # Iframe ocupando o máximo de tela possível
    st.markdown(f"""
        <iframe src="{st.session_state.current_rel['link']}" 
        style="width:100%; height:92vh; border:none;" allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)