import streamlit as st

from services.dashboard_service import DashboardService

st.set_page_config(page_title="Camada Certa Manager", page_icon="🧩", layout="centered")

st.title("🧩 Camada Certa Manager")
st.caption("Visão geral da operação da Camada Certa 3D.")

dashboard_service = DashboardService()
resumo = dashboard_service.resumo()

col1, col2, col3 = st.columns(3)
col1.metric("Receita do mês", f"R$ {resumo.receita_mes:.2f}")
col2.metric("Lucro do mês", f"R$ {resumo.lucro_mes:.2f}")
col3.metric("Pedidos realizados", resumo.pedidos_mes)

col4, col5, col6 = st.columns(3)
col4.metric("Produtos vendidos", resumo.produtos_vendidos_mes)
col5.metric("Horas de impressão", f"{resumo.horas_impressao_mes:.1f} h")
col6.metric("Filamento consumido", f"{resumo.filamento_consumido_mes:.0f} g")

st.divider()
st.subheader("Últimas vendas")
if not resumo.ultimas_vendas:
    st.info("Nenhuma venda registrada ainda.")
else:
    st.dataframe(
        [
            {
                "Produto": v.produto.nome if v.produto else "-",
                "Quantidade": v.quantidade,
                "Valor": v.valor_venda,
                "Data": v.data_venda,
            }
            for v in resumo.ultimas_vendas
        ],
        use_container_width=True,
        hide_index=True,
    )

st.subheader("Produtos mais vendidos")
if not resumo.produtos_mais_vendidos:
    st.info("Nenhum dado de vendas ainda.")
else:
    st.dataframe(
        [{"Produto": nome, "Unidades vendidas": qtd} for nome, qtd in resumo.produtos_mais_vendidos],
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.caption("Use o menu lateral para acessar as demais telas do sistema.")
