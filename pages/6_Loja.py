from datetime import date

import streamlit as st

from services.produto_service import ProdutoService
from services.venda_service import FORMAS_PAGAMENTO, ItemVendaData, VendaData, VendaService
from utils.produtos_ui import renderizar_miniatura, truncar_nome

CAMINHO_LOGO = "assets/logo.jpeg"
CAMINHO_LOGO_HORIZONTAL = "assets/Logo_horizontal.png"

produto_service = ProdutoService()
venda_service = VendaService()

st.sidebar.image(CAMINHO_LOGO, use_container_width=True)

st.image(CAMINHO_LOGO_HORIZONTAL, width=300)
st.caption("Confira nossos produtos e monte seu pedido.")

if "carrinho_loja" not in st.session_state:
    st.session_state["carrinho_loja"] = {}

carrinho = st.session_state["carrinho_loja"]

produtos = produto_service.listar()

st.subheader("Nossos produtos")
if not produtos:
    st.info("Nenhum produto disponível no momento.")
else:
    for inicio in range(0, len(produtos), 4):
        colunas = st.columns(4)
        for coluna, produto in zip(colunas, produtos[inicio : inicio + 4]):
            with coluna:
                with st.container(border=True, height=340):
                    renderizar_miniatura(produto.foto)
                    st.markdown(f"**{truncar_nome(produto.nome)}**")
                    preco_texto = (
                        f"R\\$ {produto.preco_sugerido:.2f}" if produto.preco_sugerido is not None else "-"
                    )
                    st.write(preco_texto)
                    if st.button("🛒 Adicionar ao carrinho", key=f"add_carrinho_{produto.id}", use_container_width=True):
                        if produto.id in carrinho:
                            carrinho[produto.id]["quantidade"] += 1
                        else:
                            carrinho[produto.id] = {
                                "quantidade": 1,
                                "valor_unitario": produto.preco_sugerido or 0.0,
                            }
                        st.rerun()

produtos_por_id = {p.id: p for p in produtos}

st.divider()
st.subheader("Seu carrinho")

if not carrinho:
    st.info("Seu carrinho está vazio. Adicione produtos acima.")
else:
    for produto_id, item in list(carrinho.items()):
        produto = produtos_por_id.get(produto_id)
        col_desc, col_remover = st.columns([4, 1])
        subtotal = item["quantidade"] * item["valor_unitario"]
        col_desc.write(
            f"{produto.nome if produto else '-'} — "
            f"{item['quantidade']}x R\\$ {item['valor_unitario']:.2f} = R\\$ {subtotal:.2f}"
        )
        if col_remover.button("Remover", key=f"remover_carrinho_{produto_id}"):
            carrinho.pop(produto_id)
            st.rerun()

    total = sum(item["quantidade"] * item["valor_unitario"] for item in carrinho.values())
    st.metric("Total do pedido", f"R$ {total:.2f}")

    st.subheader("Finalizar pedido")
    with st.form("form_pedido_publico"):
        nome = st.text_input("Nome")
        email = st.text_input("Email")
        telefone = st.text_input("Telefone")
        forma_pagamento = st.selectbox("Forma de pagamento", options=FORMAS_PAGAMENTO)
        observacoes = st.text_area("Observações (opcional)")

        realizar_pedido = st.form_submit_button("Realizar Pedido")

    if realizar_pedido:
        if not carrinho:
            st.error("Adicione ao menos um produto ao carrinho.")
        elif not nome.strip():
            st.error("Informe seu nome.")
        elif not email.strip():
            st.error("Informe seu email.")
        elif not telefone.strip():
            st.error("Informe seu telefone.")
        else:
            dados = VendaData(
                itens=[
                    ItemVendaData(
                        produto_id=produto_id,
                        quantidade=item["quantidade"],
                        valor_unitario=item["valor_unitario"],
                    )
                    for produto_id, item in carrinho.items()
                ],
                pago=False,
                cliente=nome,
                email=email,
                telefone=telefone,
                forma_pagamento=forma_pagamento,
                canal="Solicitado via App",
                status="Orçamento",
                observacoes=observacoes,
                data_venda=date.today(),
            )
            venda = venda_service.criar(dados)
            st.session_state["carrinho_loja"] = {}
            st.session_state["pedido_confirmado_id"] = venda.id
            st.rerun()


@st.dialog("Pedido recebido")
def dialog_confirmacao(pedido_id):
    st.write(
        f"Ficamos felizes em receber seu pedido #{pedido_id}. "
        "Entraremos em contato em breve com a confirmação."
    )
    if st.button("Fechar"):
        st.session_state.pop("pedido_confirmado_id", None)
        st.rerun()


if st.session_state.get("pedido_confirmado_id"):
    dialog_confirmacao(st.session_state["pedido_confirmado_id"])
