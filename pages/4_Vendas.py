from datetime import date

import streamlit as st

from services.produto_service import ProdutoService
from services.venda_service import VendaData, VendaService

st.set_page_config(page_title="Vendas", page_icon="🛒")
st.title("🛒 Vendas")
st.caption("Registro das vendas realizadas.")

venda_service = VendaService()
produto_service = ProdutoService()

vendas = venda_service.listar()
produtos = produto_service.listar()
opcoes_produto = {p.id: f"{p.nome} — R$ {p.preco_sugerido or 0:.2f}" for p in produtos}

st.subheader("Vendas registradas")
if not vendas:
    st.info("Nenhuma venda registrada ainda.")
else:
    st.dataframe(
        [
            {
                "Produto": v.produto.nome if v.produto else "-",
                "Quantidade": v.quantidade,
                "Cliente": v.cliente,
                "Canal": v.canal,
                "Valor": v.valor_venda,
                "Forma de pagamento": v.forma_pagamento,
                "Data": v.data_venda,
            }
            for v in vendas
        ],
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.subheader("Nova venda")

if not produtos:
    st.warning("Cadastre um produto antes de registrar uma venda.")
else:
    produto_id = st.selectbox(
        "Produto", options=list(opcoes_produto.keys()), format_func=lambda id_: opcoes_produto[id_]
    )
    quantidade = st.number_input("Quantidade", min_value=1, step=1, value=1)
    sugestao = venda_service.sugerir_valor_total(produto_id, quantidade)

    col1, col2 = st.columns(2)
    with col1:
        valor_venda = st.number_input(
            "Valor total da venda (R$)", min_value=0.0, step=1.0, value=float(sugestao)
        )
        cliente = st.text_input("Cliente")
        canal = st.text_input("Canal")
    with col2:
        forma_pagamento = st.text_input("Forma de pagamento")
        data_venda = st.date_input("Data da venda", value=date.today())

    if st.button("Registrar venda"):
        try:
            dados = VendaData(
                produto_id=produto_id,
                quantidade=int(quantidade),
                valor_venda=valor_venda,
                cliente=cliente,
                canal=canal,
                forma_pagamento=forma_pagamento,
                data_venda=data_venda,
            )
            venda_service.criar(dados)
            st.success("Venda registrada com sucesso!")
            st.rerun()
        except ValueError as erro:
            st.error(str(erro))

if vendas:
    st.divider()
    st.subheader("Editar / excluir venda")

    opcoes_venda = {
        v.id: f"{v.produto.nome if v.produto else '-'} — {v.quantidade}x — {v.data_venda or ''}" for v in vendas
    }
    selecionado_id = st.selectbox(
        "Selecione uma venda",
        options=list(opcoes_venda.keys()),
        format_func=lambda id_: opcoes_venda[id_],
    )
    venda_atual = venda_service.obter(selecionado_id)

    with st.form("form_editar_venda"):
        produto_ids = list(opcoes_produto.keys())
        indice_atual = produto_ids.index(venda_atual.produto_id) if venda_atual.produto_id in produto_ids else 0
        e_produto_id = st.selectbox(
            "Produto",
            options=produto_ids,
            format_func=lambda id_: opcoes_produto[id_],
            index=indice_atual,
        )
        e_quantidade = st.number_input(
            "Quantidade", min_value=1, step=1, value=int(venda_atual.quantidade or 1)
        )
        e_valor_venda = st.number_input(
            "Valor total da venda (R$)", min_value=0.0, step=1.0, value=float(venda_atual.valor_venda or 0)
        )
        e_cliente = st.text_input("Cliente", value=venda_atual.cliente or "")
        e_canal = st.text_input("Canal", value=venda_atual.canal or "")
        e_forma_pagamento = st.text_input("Forma de pagamento", value=venda_atual.forma_pagamento or "")
        e_data_venda = st.date_input("Data da venda", value=venda_atual.data_venda)

        col_salvar, col_excluir = st.columns(2)
        salvar = col_salvar.form_submit_button("Salvar alterações")
        excluir = col_excluir.form_submit_button("Excluir venda")

    if salvar:
        try:
            dados = VendaData(
                produto_id=e_produto_id,
                quantidade=int(e_quantidade),
                valor_venda=e_valor_venda,
                cliente=e_cliente,
                canal=e_canal,
                forma_pagamento=e_forma_pagamento,
                data_venda=e_data_venda,
            )
            venda_service.atualizar(selecionado_id, dados)
            st.success("Venda atualizada com sucesso!")
            st.rerun()
        except ValueError as erro:
            st.error(str(erro))

    if excluir:
        venda_service.excluir(selecionado_id)
        st.success("Venda excluída.")
        st.rerun()
