import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def exigir_login():
    if st.session_state.get("autenticado"):
        st.sidebar.button("Sair", on_click=_sair)
        return

    st.title("🔒 Camada Certa Manager")
    st.subheader("Login")

    with st.form("form_login"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

    if entrar:
        if usuario == os.getenv("USUARIO_APP") and senha == os.getenv("SENHA_APP"):
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    st.stop()


def _sair():
    st.session_state["autenticado"] = False
