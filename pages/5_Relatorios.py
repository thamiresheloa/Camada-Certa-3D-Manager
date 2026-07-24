from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from services.relatorio_service import RelatorioService
from utils.auth import exigir_login

st.set_page_config(page_title="Relatórios", page_icon="📊", layout="centered")
exigir_login()

st.title("📊 Relatórios")
st.caption("Análise histórica das vendas e da operação.")

relatorio_service = RelatorioService()

col_inicio, col_fim = st.columns(2)
with col_inicio:
    data_inicio = st.date_input("De", value=date.today() - timedelta(days=90))
with col_fim:
    data_fim = st.date_input("Até", value=date.today())

relatorio = relatorio_service.gerar(data_inicio=data_inicio, data_fim=data_fim)

col1, col2, col3 = st.columns(3)
col1.metric("Receita", f"R$ {relatorio.receita_total:.2f}")
col2.metric("Lucro", f"R$ {relatorio.lucro_total:.2f}")
col3.metric("Ticket médio", f"R$ {relatorio.ticket_medio:.2f}")

col4, col5, col6 = st.columns(3)
col4.metric("Pedidos", relatorio.pedidos)
col5.metric("Horas impressas", f"{relatorio.horas_impressas:.1f} h")
col6.metric("Consumo de material", f"{relatorio.consumo_material:.0f} g")

st.divider()

if not relatorio.pedidos:
    st.info("Nenhuma venda no período selecionado.")
else:
    st.subheader("Receita por dia")
    df_receita = pd.DataFrame(relatorio.receita_por_dia, columns=["Data", "Receita"])
    st.plotly_chart(px.bar(df_receita, x="Data", y="Receita"), use_container_width=True)

    col_prod, col_fil = st.columns(2)
    with col_prod:
        st.subheader("Produtos mais vendidos")
        df_produtos = pd.DataFrame(relatorio.produtos_mais_vendidos, columns=["Produto", "Unidades"])
        st.plotly_chart(px.bar(df_produtos, x="Unidades", y="Produto", orientation="h"), use_container_width=True)

    with col_fil:
        st.subheader("Filamento mais utilizado")
        df_filamento = pd.DataFrame(relatorio.filamento_mais_utilizado, columns=["Filamento", "Gramas"])
        st.plotly_chart(px.bar(df_filamento, x="Gramas", y="Filamento", orientation="h"), use_container_width=True)
