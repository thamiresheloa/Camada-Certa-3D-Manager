import streamlit as st

from utils.auth import exigir_login

if not st.session_state.get("autenticado"):
    st.info(
        "🔒 Área restrita à administração da Camada Certa. "
        "Não é necessário fazer login para comprar — acesse a Loja para realizar seu pedido."
    )

exigir_login()
