import streamlit as st
import pandas as pd
import time
import requests
import os
from datetime import datetime
from pathlib import Path

# ==============================================================================
# 1. CONFIGURAÇÕES DE CAMINHOS E SEGURANÇA
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
PATH_DATA = BASE_DIR / "data"
PATH_IMG = BASE_DIR / "assets"

st.set_page_config(page_title="CIG 360º | Portal", layout="wide", initial_sidebar_state="collapsed")

# ==============================================================================
# 2. ESTILIZAÇÃO CUSTOMIZADA (CSS SÊNIOR)
# ==============================================================================
def apply_custom_styles():
    # Caminhos das imagens para o CSS
    # Nota: No Streamlit Cloud, imagens locais para CSS precisam estar na pasta 'static' ou codificadas em Base64.
    # Para facilitar, vamos usar cores e fontes, e imagens via st.image.
    st.markdown(f"""
        <style>
            #MainMenu, footer, header {{visibility: hidden;}}
            
            /* Fundo da Tela de Login */
            .stApp {{
                background-image: url("https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2070"); /* Placeholder para fundologin */
                background-size: cover;
            }}

            .login-box {{
                background-color: rgba(255, 255, 255, 0.9);
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                text-align: center;
            }}
            .main-title {{
                font-size: 60px !important;
                font-weight: 800;
                color: #1E3A8A;
                margin-bottom: 0px;
            }}
        </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# ==============================================================================
# 3. FUNÇÕES DE DADOS (COM TRATAMENTO DE ERRO)
# ==============================================================================
def carregar_dados():
    try:
        # Usando caminhos dinâmicos que funcionam no Cloud
        u = pd.read_excel(PATH_DATA / 'usuarios.xlsx')
        r = pd.read_excel(PATH_DATA / 'relatorios.xlsx')
        rel = pd.read_excel(PATH_DATA / 'relacional.xlsx')
        return u, r, rel
    except Exception as e:
        st.error(f"Erro ao acessar CORE/data: {e}")
        return None, None, None

def registrar_log(evento, detalhe="", tempo=0):
    user = st.session_state.get('user_info', {'nome': 'Anonimo', 'email': 'N/A'})
    log_path = PATH_DATA / 'logs_acesso.xlsx'
    try:
        ip = requests.get('https://api.ipify.org', timeout=3).text
        novo_log = pd.DataFrame([{
            'data_hora': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'usuario': user['nome'], 'email': user['email'],
            'evento': evento, 'detalhe': detalhe, 'ip': ip, 'tempo_segundos': tempo
        }])
        if log_path.exists():
            df_old = pd.read_excel(log_path)
            pd.concat([df_old, novo_log]).to_excel(log_path, index=False)
        else:
            novo_log.to_excel(log_path, index=False)
    except: pass

# ==============================================================================
# 4. LÓGICA DE NAVEGAÇÃO
# ==============================================================================
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# --- TELA 1: LOGIN ---
if st.session_state.page == 'login':
    _, col_login, _ = st.columns([1, 1.5, 1])
    
    with col_login:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        # Posição 1: logo.png
        if (PATH_IMG / "logo.png").exists():
            st.image(str(PATH_IMG / "logo.png"), width=150)
        
        st.markdown('<h1 class="main-title">CIG 360º</h1>', unsafe_allow_html=True)
        
        # Posição 2: empresa1.jpg
        if (PATH_IMG / "empresa1.jpg").exists():
            st.image(str(PATH_IMG / "empresa1.jpg"), width=100)
            
        st.write("### Login de Acesso")
        email = st.text_input("Usuário (E-mail)")
        senha = st.text_input("Senha", type="password")
        
        if st.button("ENTRAR", use_container_width=True):
            df_u, _, _ = carregar_dados()
            if df_u is not None:
                user = df_u[(df_u['email'] == email) & (df_u['senha'].astype(str) == senha)]
                if not user.empty:
                    st.session_state.user_info = user.iloc[0].to_dict()
                    st.session_state.page = 'menu'
                    registrar_log("LOGIN")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- TELA 2: MENU ---
elif st.session_state.page == 'menu':
    df_u, df_r, df_rel = carregar_dados()
    
    # Header do Menu
    c1, c2 = st.columns([5, 1])
    c1.title(f"Bem-vindo, {st.session_state.user_info['nome']}")
    if c2.button("Sair 🚪", use_container_width=True):
        registrar_log("LOGOUT")
        st.session_state.clear()
        st.rerun()

    # Lógica Relacional corrigindo o KeyError
    meus_ids = df_rel[df_rel['usuario_id'] == st.session_state.user_info['usuario_id']]
    # Forçamos o merge para garantir que a coluna 'nome_relatorio' venha da tabela certa
    meus_relatorios = pd.merge(meus_ids[['relatorio_id']], df_r, on='relatorio_id', how='inner')

    # Filtros e Cards (Como solicitado anteriormente)
    busca = st.text_input("Filtrar relatório...")
    
    for cat in meus_relatorios['categoria'].unique():
        st.subheader(f"📂 {cat}")
        df_cat = meus_relatorios[meus_relatorios['categoria'] == cat]
        cols = st.columns(3)
        for i, (_, row) in enumerate(df_cat.iterrows()):
            with cols[i % 3]:
                # O Erro acontecia aqui. Agora usamos o nome garantido pelo merge.
                if st.button(row['nome_relatorio'], key=f"rel_{row['relatorio_id']}"):
                    st.session_state.current_rel = row.to_dict()
                    st.session_state.start_time = time.time()
                    st.session_state.page = 'view'
                    st.rerun()

# --- TELA 3: VIEW ---
elif st.session_state.page == 'view':
    # Botão Voltar e Sair no topo para melhor UX
    cv1, cv2, cv3 = st.columns([6, 1, 1])
    cv1.write(f"### Exibindo: {st.session_state.current_rel['nome_relatorio']}")
    if cv2.button("⬅️ Voltar"):
        tempo = int(time.time() - st.session_state.start_time)
        registrar_log("FECHOU", st.session_state.current_rel['nome_relatorio'], tempo)
        st.session_state.page = 'menu'
        st.rerun()
    if cv3.button("Sair 🚪"):
        st.session_state.clear()
        st.rerun()

    st.markdown(f'<iframe src="{st.session_state.current_rel["link"]}" width="100%" height="850px" frameborder="0"></iframe>', unsafe_allow_html=True)