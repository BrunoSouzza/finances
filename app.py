import streamlit as st
from streamlit_google_auth import Authenticate
from tempfile import NamedTemporaryFile
import json

st.set_page_config(page_title="Login Seguro", layout="wide")
st.title('HUB')

if 'connected' not in st.session_state:
    # Escreve os dados do secrets em um arquivo temporário
    with NamedTemporaryFile(mode="w+", delete=False) as temp:
        json.dump({"web": dict(st.secrets["google_credentials"]["web"])}, temp)
        temp.flush()
        authenticator = Authenticate(
            secret_credentials_path=temp.name,
            cookie_name='my_cookie_name',
            cookie_key='my_cookie_key',
            redirect_uri='https://relatorio-financeiro.streamlit.app',
        )
        st.session_state["authenticator"] = authenticator

# Verifica autenticação
st.session_state["authenticator"].check_authentification()

# Botão de login
st.session_state["authenticator"].login()

# Conteúdo se logado
if st.session_state.get("connected"):
    with st.sidebar:
        st.image(st.session_state['user_info'].get('picture'), width=100)
        st.markdown(f"**{st.session_state['user_info'].get('name')}**")
        st.caption(st.session_state['user_info'].get('email'))
        if st.button('Sair'):
            st.session_state["authenticator"].logout()
            st.rerun()

    st.success(f"Bem-vindo, {st.session_state['user_info'].get('name')}!")
