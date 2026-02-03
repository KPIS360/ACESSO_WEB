import streamlit as st
import pandas as pd
import time
import requests
import os
from datetime import datetime
from pathlib import Path

# ==============================================================================
# 1. CONFIGURAÇÕES DE CAMINHOS DINÂMICOS (SÊNIOR)
# ==============================================================================
# BASE_DIR aponta para a raiz do repositório
BASE_DIR = Path(__file__).resolve().parent.parent 
PATH_DATA = BASE_DIR / "data"
PATH_IMG = BASE_DIR / "assets"

st.set_page_config(page_title="Portal CIG 360", layout="wide", initial_sidebar_state="collapsed")

# CSS para Layout e Background futuro
st.markdown(f"""
    <style>
        #MainMenu, footer, header {{visibility: hidden;}}
        .main {{
            background-color: #f0f2f6; /* Placeholder para imagem de fundo futura */
        }}
        .login-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }}
        .login-header-row {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .login-title {{
            font-size: 38px;
            font-weight: bold;
            color: #1E3A8A;
            margin: 0;
        }}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. FUNÇÕES CORE (DECLARADAS ANTES DO USO)
# ==============================================================================

def registrar_log(usuario, email, evento, detalhe="", tempo=0):
    try:
        ip = requests.get('https://api.ipify.org', timeout=3).text
    except:
        ip = "0.0.0.0"

    novo_log = pd.DataFrame([{
        'data_hora': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'usuario': usuario,
        'email': email,
        'evento': evento,
        'detalhe': detalhe,
        'ip': ip,
        'tempo_segundos': tempo
    }])
    
    file_path = PATH_DATA / 'logs_acesso.xlsx'
    try:
        if file_path.exists():
            df_old = pd.read_excel(file_path)
            pd.concat([df_old, novo_log]).to_excel(file_path, index=False)
        else:
            novo_log.to_excel(file_path, index=False)
    except:
        pass # Evita travar o app se o Excel estiver em uso

def carregar_dados():
    try:
        u = pd.read_excel(PATH_DATA / 'usuarios.xlsx')
        r = pd.read_excel(PATH_DATA / 'relatorios.xlsx')
        rel = pd.read_excel(PATH_DATA / 'relacional.xlsx')
        return u, r, rel
    except Exception as e:
        # Mostra erro no Streamlit se não achar os arquivos
        st.error(f"Erro ao carregar arquivos em {PATH_DATA}: {e}")
        return None, None, None

# ==============================================================================
# 3. LÓGICA DE NAVEGAÇÃO
# ==============================================================================

if 'page' not in st.session_state:
    st.session_state.page = 'login'

# --- TELA 1: LOGIN ---
if st.session_state.page == 'login':
    _, col_login, _ = st.columns([1, 2, 1])
    
    with col_login:
        st.write("###")
        
        # Header: Imagem à frente do Texto
        logo_path = PATH_IMG / "logo.png"
        col_img, col_txt = st.columns([1, 4])
        
        with col_img:
            if logo_path.exists():
                st.image(str(logo_path), width=80)
        with col_txt:
            st.markdown(f'<p class="login-title">Portal CIG 360º | GIROAgro</p>', unsafe_allow_html=True)
        
        st.write("---")
        
        with st.form("login_form"):
            user_input = st.text_input("Usuário (E-mail)")
            pass_input = st.text_input("Senha", type="password")
            submit = st.form_submit_button("ENTRAR NO PORTAL", use_container_width=True)
            
            if submit:
                df_u, _, _ = carregar_dados()
                if df_u is not None:
                    # Busca usuário e senha
                    auth = df_u[(df_u['email'] == user_input) & (df_u['senha'].astype(str) == pass_input)]
                    
                    if not auth.empty:
                        st.session_state.user_info = auth.iloc[0].to_dict()
                        st.session_state.page = 'menu'
                        registrar_log(auth.iloc[0]['nome'], user_input, "LOGIN", "Sucesso")
                        st.rerun()
                    else:
                        st.error("Usuário ou senha inválidos.")

# --- TELA 2: MENU ---
elif st.session_state.page == 'menu':
    # Barra Superior
    c1, c2 = st.columns([5, 1])
    c1.title(f"Olá, {st.session_state.user_info['nome']}")
    if c2.button("Sair 🚪"):
        st.session_state.clear()
        st.rerun()

    df_u, df_r, df_rel = carregar_dados()
    # Merge para pegar relatórios do usuário
    meus_rel = pd.merge(df_rel[df_rel['usuario_id'] == st.session_state.user_info['usuario_id']], df_r, on='relatorio_id')
    
    # Busca e Filtro
    busca = st.text_input("🔍 Pesquisar Relatório")
    
    # Exibição por Categorias
    for cat in meus_rel['categoria'].unique():
        st.subheader(cat)
        df_cat = meus_rel[meus_rel['categoria'] == cat]
        if busca:
            df_cat = df_cat[df_cat['nome_relatorio'].str.contains(busca, case=False)]
        
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df_cat.iterrows()):
            with cols[i % 3]:
                if st.button(row['nome_relatorio'], key=f"rel_{row['relatorio_id']}", use_container_width=True):
                    st.session_state.current_rel = row.to_dict()
                    st.session_state.start_time = time.time()
                    st.session_state.page = 'view'
                    st.rerun()

# --- TELA 3: VIEW ---
elif st.session_state.page == 'view':
    rel = st.session_state.current_rel
    col_v1, col_v2 = st.columns([6, 1])
    col_v1.subheader(f"Dashboard: {rel['nome_relatorio']}")
    if col_v2.button("⬅️ Voltar"):
        tempo = int(time.time() - st.session_state.start_time)
        registrar_log(st.session_state.user_info['nome'], st.session_state.user_info['email'], "FECHOU", rel['nome_relatorio'], tempo)
        st.session_state.page = 'menu'
        st.rerun()
    
    st.markdown(f'<iframe src="{rel["link"]}" width="100%" height="800px" frameborder="0"></iframe>', unsafe_allow_html=True)