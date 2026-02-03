# --- CSS REFINADO (AJUSTE DE SUBTÍTULOS E IMAGEM) ---
def apply_login_styles():
    bg_base64 = get_base64(PATH_IMG / "fundologin.jpg")
    bg_css = f"url('data:image/jpg;base64,{bg_base64}')" if bg_base64 else "#1e3a8a"
    
    st.markdown(f"""
        <style>
            .block-container {{ padding: 0rem !important; }}
            header {{ visibility: hidden; }}
            
            .stApp {{
                background-image: {bg_css};
                background-size: cover;
                background-position: center;
            }}

            /* 1º Correção dos Subtítulos (Labels) */
            .label-white {{ 
                color: white !important; 
                font-size: 18px; 
                font-weight: 500; 
                margin-top: 15px;
                margin-bottom: 5px; /* Espaço para não ficar atrás do campo */
                display: block;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
            }}
            
            /* Ajuste para remover o label padrão do Streamlit que empurra tudo */
            div[data-testid="stFormSubmitButton"] > button {{ margin-top: 20px; }}

            /* 2º Redimensionamento empresa1.jpg (Reduzido em 15%) */
            .empresa-logo {{ 
                position: absolute; 
                top: 15px; 
                right: 35px; 
                z-index: 999; 
            }}

            .main-title {{
                color: white !important; font-size: 58px; font-weight: 800;
                text-align: center; margin-top: 5vh; text-shadow: 2px 2px 8px rgba(0,0,0,0.6);
            }}

            .stButton button {{
                background-color: #ED3237 !important; color: white !important;
                height: 55px !important; font-size: 20px !important; font-weight: bold !important;
                border-radius: 10px !important; border: none !important;
            }}
        </style>
    """, unsafe_allow_html=True)

# --- RENDERIZAÇÃO NA TELA 1 ---
if st.session_state.page == 'login':
    apply_login_styles()

    # 2º Imagem empresa1.jpg Redimensionada (Width de 160 para ~135)
    emp_base = get_base64(PATH_IMG / "empresa1.jpg")
    if emp_base:
        st.markdown(f'<div class="empresa-logo"><img src="data:image/jpg;base64,{emp_base}" width="135"></div>', unsafe_allow_html=True)

    st.markdown('<h1 class="main-title">Portal CIG 360º | GIROAgro</h1>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 0.35, 1])
    with c2:
        logo_base = get_base64(PATH_IMG / "logo.png")
        if logo_base:
            st.image(f"data:image/png;base64,{logo_base}", use_container_width=True)

    _, col_form, _ = st.columns([1, 1, 1])
    with col_form:
        st.write("##")
        # 1º Subtítulo agora posicionado corretamente
        st.markdown('<label class="label-white">E-mail Corporativo:</label>', unsafe_allow_html=True)
        email_in = st.text_input("", placeholder="usuario@giroagro.com.br", key="email", label_visibility="collapsed")
        
        st.markdown('<label class="label-white">Senha:</label>', unsafe_allow_html=True)
        senha_in = st.text_input("", type="password", placeholder="••••••••", key="senha", label_visibility="collapsed")
        
        if st.button("ACESSAR PORTAL", use_container_width=True):
            # ... (Lógica de validação permanece igual) ...
            pass