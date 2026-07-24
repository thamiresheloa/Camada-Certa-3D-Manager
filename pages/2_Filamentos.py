import streamlit as st

from services.filamento_service import FilamentoData, FilamentoService

st.set_page_config(page_title="Filamentos", page_icon="🧵")
st.title("🧵 Filamentos")
st.caption("Cadastro dos materiais utilizados na impressão.")

service = FilamentoService()
filamentos = service.listar()

st.subheader("Filamentos cadastrados")
if not filamentos:
    st.info("Nenhum filamento cadastrado ainda.")
else:
    st.dataframe(
        [
            {
                "Nome": f.nome,
                "Marca": f.marca,
                "Cor": f.cor,
                "Tipo": f.tipo,
                "Valor/kg": f.valor_kg,
                "Peso original (g)": f.peso_original,
                "Peso restante (g)": f.peso_restante,
                "Fornecedor": f.fornecedor,
                "Data da compra": f.data_compra,
                "Validade": f.validade,
            }
            for f in filamentos
        ],
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.subheader("Novo filamento")

with st.form("form_novo_filamento", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome")
        marca = st.text_input("Marca")
        cor = st.text_input("Cor")
        tipo = st.text_input("Tipo")
        fornecedor = st.text_input("Fornecedor")
    with col2:
        valor_kg = st.number_input("Valor por kg (R$)", min_value=0.0, step=0.5)
        peso_original = st.number_input("Peso original (g)", min_value=0.0, step=50.0)
        peso_restante = st.number_input("Peso restante (g)", min_value=0.0, step=50.0)
        data_compra = st.date_input("Data da compra", value=None)
        validade = st.date_input("Validade", value=None)

    criar = st.form_submit_button("Cadastrar")

if criar:
    try:
        dados = FilamentoData(
            nome=nome,
            marca=marca,
            cor=cor,
            tipo=tipo,
            valor_kg=valor_kg,
            peso_original=peso_original,
            peso_restante=peso_restante,
            fornecedor=fornecedor,
            data_compra=data_compra,
            validade=validade,
        )
        service.criar(dados)
        st.success("Filamento cadastrado com sucesso!")
        st.rerun()
    except ValueError as erro:
        st.error(str(erro))

if filamentos:
    st.divider()
    st.subheader("Editar / excluir filamento")

    opcoes = {f.id: f"{f.nome} — {f.marca} — {f.cor}" for f in filamentos}
    selecionado_id = st.selectbox(
        "Selecione um filamento",
        options=list(opcoes.keys()),
        format_func=lambda id_: opcoes[id_],
    )
    filamento_atual = service.obter(selecionado_id)

    with st.form("form_editar_filamento"):
        col1, col2 = st.columns(2)
        with col1:
            e_nome = st.text_input("Nome", value=filamento_atual.nome or "")
            e_marca = st.text_input("Marca", value=filamento_atual.marca or "")
            e_cor = st.text_input("Cor", value=filamento_atual.cor or "")
            e_tipo = st.text_input("Tipo", value=filamento_atual.tipo or "")
            e_fornecedor = st.text_input("Fornecedor", value=filamento_atual.fornecedor or "")
        with col2:
            e_valor_kg = st.number_input(
                "Valor por kg (R$)", min_value=0.0, step=0.5, value=float(filamento_atual.valor_kg or 0)
            )
            e_peso_original = st.number_input(
                "Peso original (g)", min_value=0.0, step=50.0, value=float(filamento_atual.peso_original or 0)
            )
            e_peso_restante = st.number_input(
                "Peso restante (g)", min_value=0.0, step=50.0, value=float(filamento_atual.peso_restante or 0)
            )
            e_data_compra = st.date_input("Data da compra", value=filamento_atual.data_compra)
            e_validade = st.date_input("Validade", value=filamento_atual.validade)

        col_salvar, col_excluir = st.columns(2)
        salvar = col_salvar.form_submit_button("Salvar alterações")
        excluir = col_excluir.form_submit_button("Excluir filamento")

    if salvar:
        try:
            dados = FilamentoData(
                nome=e_nome,
                marca=e_marca,
                cor=e_cor,
                tipo=e_tipo,
                valor_kg=e_valor_kg,
                peso_original=e_peso_original,
                peso_restante=e_peso_restante,
                fornecedor=e_fornecedor,
                data_compra=e_data_compra,
                validade=e_validade,
            )
            service.atualizar(selecionado_id, dados)
            st.success("Filamento atualizado com sucesso!")
            st.rerun()
        except ValueError as erro:
            st.error(str(erro))

    if excluir:
        service.excluir(selecionado_id)
        st.success("Filamento excluído.")
        st.rerun()
