import streamlit as st

st.set_page_config(page_title="Camada Certa Manager", page_icon="🧩", layout="centered")

pagina_inicial = st.Page("pages/0_Pagina_Inicial.py", title="Página Inicial", icon="🧩", default=True)
configuracoes = st.Page("pages/1_Configuracoes.py", title="Configurações", icon="⚙️")
filamentos = st.Page("pages/2_Filamentos.py", title="Filamentos", icon="🧵")
produtos = st.Page("pages/3_Produtos.py", title="Produtos", icon="📦")
vendas = st.Page("pages/4_Vendas.py", title="Vendas", icon="🛒")
relatorios = st.Page("pages/5_Relatorios.py", title="Relatórios", icon="📊")

if st.session_state.get("autenticado"):
    paginas = [pagina_inicial, configuracoes, filamentos, produtos, vendas, relatorios]
else:
    paginas = [pagina_inicial]

pg = st.navigation(paginas)
pg.run()
