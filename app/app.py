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
# No Streamlit Cloud, o BASE_DIR deve apontar para a raiz do repo
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_DATA = BASE_DIR / "data"
PATH_IMG = BASE_DIR / "assets"

st.set_page_config(page_title="CIG 360º", layout="wide", initial_sidebar_state="collapsed")

# Função para converter imagem local em Base64 (Garante funcionamento no Cloud)
def get_base64(file_path):
    if file_path.exists():
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# ==============================================================================
# 2. FUNÇÕES DE DADOS (UNIFICADAS)
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

def registrar_log(usuario, email, evento, detalhe="", tempo=0):
    log_path = PATH_DATA / 'logs_acesso.xlsx'
    try:
        ip = requests.get('https://api.ipify.org', timeout=3).text
        novo_log = pd.DataFrame([{
            'data_hora': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'usuario': usuario, 'email': email,
            'evento': evento, 'detalhe': detalhe, 'ip': ip, 'tempo_segundos': tempo
        }])
        if log_path.exists():
            df_old = pd.read_excel(log_path)
            pd.concat([df_old, novo_log]).to_excel(log_path, index=False)
        else:
            novo_log.to_excel(log_path, index=False)
    except: pass

# ==============================================================================
# 3. ESTILIZAÇÃO CUSTOMIZADA (CSS ISOLADO POR TELA)
# ==============================================================================
def apply_common_styles():
    st.markdown("""
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .block-container {padding: 0rem !important;}
            .stButton button {border-radius: 8px;}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 4. NAVEGAÇÃO E TELAS
# ==============================================================================
if 'page' not in st.session_state:
    st.session_state.page = 'login'

apply_common_styles()

# --- TELA 1: LOGIN ---
if st.session_state.page == 'login':
    bg_base64 = get_base64(PATH_IMG / "fundologin.jpg")
    if bg_base64:
        st.markdown(f"""
            <style>
                .stApp {{
                    background-image: url("data:image/jpg;base64,{bg_base64}");
                    background-size: cover;
                    background-position: center;
                }}
            </style>
        """, unsafe_allow_html=True)

    st.markdown("""
        <style>
            .login-card {
                background: rgba(255, 255, 255, 0.95);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.3);
                text-align: center;
                margin-top: 50px;
            }
            .main-title { font-size: 70px; font-weight: 900; color: #1e3a8a; margin: 0px; }
        </style>
    """, unsafe_allow_html=True)

    _, col_card, _ = st.columns([1, 1.3, 1])
    with col_card:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # [Posição 1] logo.png
        if (PATH_IMG / "logo.png").exists():
            st.image(str(PATH_IMG / "logo.png"), width=200)
        
        st.markdown('<h1 class="main-title">CIG 360º</h1>', unsafe_allow_html=True)
        
        # [Posição 2] empresa1.jpg
        if (PATH_IMG / "empresa1.jpg").exists():
            st.image(str(PATH_IMG / "empresa1.jpg"), width=130)
        
        st.write("---")
        user_in = st.text_input("Usuário", placeholder="E-mail de acesso")
        pass_in = st.text_input("Senha", type="password")
        
        if st.button("ACESSAR PORTAL", use_container_width=True):
            df_u, _, _ = carregar_dados()
            if df_u is not None:
                match = df_u[(df_u['email'] == user_in) & (df_u['senha'].astype(str) == pass_in)]
                if not match.empty:
                    st.session_state.user = match.iloc[0].to_dict()
                    st.session_state.page = 'menu'
                    registrar_log(st.session_state.user['nome'], user_in, "LOGIN")
                    st.rerun()
                else:
                    st.error("Credenciais Inválidas")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TELA 2: LISTA DE RELATÓRIOS (ESTILO LISTA) ---
elif st.session_state.page == 'menu':
    st.markdown("<style>.stApp {background-image: none; background-color: #f4f7f6;}</style>", unsafe_allow_html=True)
    
    # Header Minimalista
    with st.container():
        st.markdown(f"""
            <div style='background-color: white; padding: 15px 30px; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: center;'>
                <h2 style='margin:0; color:#1e3a8a;'>Portal CIG 360º</h2>
                <p style='margin:0;'>Olá, <b>{st.session_state.user['nome']}</b></p>
            </div>
        """, unsafe_allow_html=True)

    st.write("#")
    _, col_list, _ = st.columns([0.2, 5, 0.2])
    
    with col_list:
        st.subheader("📂 Meus Relatórios")
        df_u, df_r, df_rel = carregar_dados()
        
        # Join Relacional
        meus_ids = df_rel[df_rel['usuario_id'] == st.session_state.user['usuario_id']]
        meus_relatorios = pd.merge(meus_ids[['relatorio_id']], df_r, on='relatorio_id', how='inner')
        
        search = st.text_input("🔍 Buscar painel...")
        
        for _, row in meus_relatorios.iterrows():
            if search.lower() in row['nome_relatorio'].lower():
                with st.container():
                    c_txt, c_btn = st.columns([4, 1])
                    with c_txt:
                        st.markdown(f"""
                            <div style='background: white; padding: 15px; border-radius: 10px; border-left: 6px solid #1e3a8a; margin-bottom: 5px;'>
                                <span style='font-size: 12px; color: gray;'>{row['categoria']}</span><br>
                                <b style='font-size: 18px;'>{row['nome_relatorio']}</b>
                            </div>
                        """, unsafe_allow_html=True)
                    with c_btn:
                        st.write("##")
                        if st.button("Abrir 📊", key=f"btn_{row['relatorio_id']}", use_container_width=True):
                            st.session_state.current_rel = row.to_dict()
                            st.session_state.start_time = time.time()
                            st.session_state.page = 'view'
                            st.rerun()

        st.write("---")
        if st.button("Sair do Portal 🚪", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# --- TELA 3: VISUALIZAÇÃO FOCO TOTAL ---
elif st.session_state.page == 'view':
    # Barra superior ultra-fina
    c_back, c_title, c_exit = st.columns([1.5, 7, 1.5])
    with c_back:
        if st.button("⬅️ Voltar ao Menu", use_container_width=True):
            st.session_state.page = 'menu'
            st.rerun()
    with c_title:
        st.markdown(f"<h4 style='text-align: center; margin-top: 5px;'>{st.session_state.current_rel['nome_relatorio']}</h4>", unsafe_allow_html=True)
    with c_exit:
        if st.button("Sair 🚪", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # Iframe ocupando 95% da altura
    st.markdown(f"""
        <iframe src="{st.session_state.current_rel['link']}" 
        style="width:100%; height:93vh; border:none;" allowFullScreen="true"></iframe>
    """, unsafe_allow_html=True)