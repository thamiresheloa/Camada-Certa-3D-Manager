from datetime import date

import streamlit as st

from services.produto_service import ProdutoService
from services.venda_service import ItemVendaData, VendaData, VendaService
from utils.auth import exigir_login

exigir_login()

st.title("🛒 Vendas")
st.caption("Registro das vendas realizadas.")

venda_service = VendaService()
produto_service = ProdutoService()

vendas = venda_service.listar()
produtos = produto_service.listar()
opcoes_produto = {p.id: f"{p.nome} — R$ {p.preco_sugerido or 0:.2f}" for p in produtos}
produtos_por_id = {p.id: p for p in produtos}


def formatar_pago(valor):
    if valor is True:
        return "Sim"
    if valor is False:
        return "Não"
    return "-"


st.subheader("Vendas registradas")
if not vendas:
    st.info("Nenhuma venda registrada ainda.")
else:
    st.dataframe(
        [
            {
                "Produtos": ", ".join(
                    f"{item.produto.nome if item.produto else '-'} ({item.quantidade}x)" for item in v.itens
                ),
                "Cliente": v.cliente,
                "Canal": v.canal,
                "Valor": v.valor_venda,
                "Forma de pagamento": v.forma_pagamento,
                "Pago": formatar_pago(v.pago),
                "Data": v.data_venda.strftime("%d/%m/%Y") if v.data_venda else "-",
            }
            for v in vendas
        ],
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.subheader("Nova venda")

if "carrinho_novo" not in st.session_state:
    st.session_state["carrinho_novo"] = []

if not produtos:
    st.warning("Cadastre um produto antes de registrar uma venda.")
else:
    st.markdown("**Adicionar produto**")
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        produto_id_novo = st.selectbox(
            "Produto",
            options=list(opcoes_produto.keys()),
            format_func=lambda id_: opcoes_produto[id_],
            key="produto_novo",
        )
    with col2:
        quantidade_novo = st.number_input("Quantidade", min_value=1, step=1, value=1, key="quantidade_novo")
    with col3:
        valor_unitario_novo = st.number_input(
            "Valor unitário (R$)",
            min_value=0.0,
            step=1.0,
            value=float(produtos_por_id[produto_id_novo].preco_sugerido or 0),
            key="valor_unitario_novo",
        )

    if st.button("Adicionar item à venda"):
        st.session_state["carrinho_novo"].append(
            {
                "produto_id": produto_id_novo,
                "quantidade": int(quantidade_novo),
                "valor_unitario": valor_unitario_novo,
            }
        )
        st.rerun()

    if st.session_state["carrinho_novo"]:
        st.markdown("**Itens da venda**")
        for indice, item in enumerate(st.session_state["carrinho_novo"]):
            produto = produtos_por_id.get(item["produto_id"])
            col_desc, col_remover = st.columns([4, 1])
            subtotal = item["quantidade"] * item["valor_unitario"]
            col_desc.write(
                f"{produto.nome if produto else '-'} — "
                f"{item['quantidade']}x R\\$ {item['valor_unitario']:.2f} = R\\$ {subtotal:.2f}"
            )
            if col_remover.button("Remover", key=f"remover_novo_{indice}"):
                st.session_state["carrinho_novo"].pop(indice)
                st.rerun()

        total_novo = sum(i["quantidade"] * i["valor_unitario"] for i in st.session_state["carrinho_novo"])
        st.metric("Total da venda", f"R$ {total_novo:.2f}")

        with st.form("form_nova_venda"):
            cliente = st.text_input("Cliente")
            canal = st.text_input("Canal")
            forma_pagamento = st.text_input("Forma de pagamento")
            pago = st.selectbox("Pago", options=["Sim", "Não"])
            data_venda = st.date_input("Data da venda", value=date.today(), format="DD/MM/YYYY")

            registrar = st.form_submit_button("Registrar venda")

        if registrar:
            try:
                dados = VendaData(
                    itens=[ItemVendaData(**item) for item in st.session_state["carrinho_novo"]],
                    pago=(pago == "Sim"),
                    cliente=cliente,
                    canal=canal,
                    forma_pagamento=forma_pagamento,
                    data_venda=data_venda,
                )
                venda_service.criar(dados)
                st.session_state["carrinho_novo"] = []
                st.success("Venda registrada com sucesso!")
                st.rerun()
            except ValueError as erro:
                st.error(str(erro))

if vendas:
    st.divider()
    st.subheader("Editar / excluir venda")

    opcoes_venda = {
        v.id: (
            f"#{v.id} — {v.cliente or 'sem cliente'} — "
            f"{v.data_venda.strftime('%d/%m/%Y') if v.data_venda else ''} — R$ {v.valor_venda or 0:.2f}"
        )
        for v in vendas
    }
    selecionado_id = st.selectbox(
        "Selecione uma venda",
        options=list(opcoes_venda.keys()),
        format_func=lambda id_: opcoes_venda[id_],
    )
    venda_atual = venda_service.obter(selecionado_id)

    if st.session_state.get("editando_id") != selecionado_id:
        st.session_state["editando_id"] = selecionado_id
        st.session_state["carrinho_edicao"] = [
            {
                "produto_id": item.produto_id,
                "quantidade": item.quantidade,
                "valor_unitario": item.valor_unitario,
            }
            for item in venda_atual.itens
        ]

    st.markdown("**Adicionar produto**")
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        produto_id_edicao = st.selectbox(
            "Produto",
            options=list(opcoes_produto.keys()),
            format_func=lambda id_: opcoes_produto[id_],
            key="produto_edicao",
        )
    with col2:
        quantidade_edicao = st.number_input("Quantidade", min_value=1, step=1, value=1, key="quantidade_edicao")
    with col3:
        valor_unitario_edicao = st.number_input(
            "Valor unitário (R$)",
            min_value=0.0,
            step=1.0,
            value=float(produtos_por_id[produto_id_edicao].preco_sugerido or 0),
            key="valor_unitario_edicao",
        )

    if st.button("Adicionar item", key="adicionar_item_edicao"):
        st.session_state["carrinho_edicao"].append(
            {
                "produto_id": produto_id_edicao,
                "quantidade": int(quantidade_edicao),
                "valor_unitario": valor_unitario_edicao,
            }
        )
        st.rerun()

    st.markdown("**Itens da venda**")
    if not st.session_state["carrinho_edicao"]:
        st.info("Nenhum item nesta venda. Adicione ao menos um produto.")
    for indice, item in enumerate(st.session_state["carrinho_edicao"]):
        produto = produtos_por_id.get(item["produto_id"])
        col_desc, col_remover = st.columns([4, 1])
        subtotal = item["quantidade"] * item["valor_unitario"]
        col_desc.write(
            f"{produto.nome if produto else '-'} — {item['quantidade']}x R\\$ {item['valor_unitario']:.2f} = R\\$ {subtotal:.2f}"
        )
        if col_remover.button("Remover", key=f"remover_edicao_{indice}"):
            st.session_state["carrinho_edicao"].pop(indice)
            st.rerun()

    total_edicao = sum(i["quantidade"] * i["valor_unitario"] for i in st.session_state["carrinho_edicao"])
    st.metric("Total da venda", f"R$ {total_edicao:.2f}")

    with st.form("form_editar_venda"):
        e_cliente = st.text_input("Cliente", value=venda_atual.cliente or "")
        e_canal = st.text_input("Canal", value=venda_atual.canal or "")
        e_forma_pagamento = st.text_input("Forma de pagamento", value=venda_atual.forma_pagamento or "")
        e_pago = st.selectbox("Pago", options=["Sim", "Não"], index=0 if venda_atual.pago else 1)
        e_data_venda = st.date_input("Data da venda", value=venda_atual.data_venda, format="DD/MM/YYYY")

        col_salvar, col_excluir = st.columns(2)
        salvar = col_salvar.form_submit_button("Salvar alterações")
        excluir = col_excluir.form_submit_button("Excluir venda")

    if salvar:
        try:
            dados = VendaData(
                itens=[ItemVendaData(**item) for item in st.session_state["carrinho_edicao"]],
                pago=(e_pago == "Sim"),
                cliente=e_cliente,
                canal=e_canal,
                forma_pagamento=e_forma_pagamento,
                data_venda=e_data_venda,
            )
            venda_service.atualizar(selecionado_id, dados)
            st.session_state.pop("editando_id", None)
            st.session_state.pop("carrinho_edicao", None)
            st.success("Venda atualizada com sucesso!")
            st.rerun()
        except ValueError as erro:
            st.error(str(erro))

    if excluir:
        venda_service.excluir(selecionado_id)
        st.session_state.pop("editando_id", None)
        st.session_state.pop("carrinho_edicao", None)
        st.success("Venda excluída.")
        st.rerun()
