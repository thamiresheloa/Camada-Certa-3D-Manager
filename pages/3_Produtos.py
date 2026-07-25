import streamlit as st

from services.filamento_service import FilamentoService
from services.produto_service import ProdutoData, ProdutoService
from utils.auth import exigir_login

st.set_page_config(page_title="Produtos", page_icon="📦")
exigir_login()

st.title("📦 Produtos")
st.caption("Ficha técnica e precificação automática dos produtos.")

produto_service = ProdutoService()
filamento_service = FilamentoService()

produtos = produto_service.listar()
filamentos = filamento_service.listar()
opcoes_filamento = {f.id: f.descricao for f in filamentos}

st.subheader("Produtos cadastrados")
if not produtos:
    st.info("Nenhum produto cadastrado ainda.")
else:
    st.dataframe(
        [
            {
                "Nome": p.nome,
                "Filamento": p.filamento.descricao if p.filamento else "-",
                "Peso (g)": p.peso,
                "Tempo (h)": p.tempo,
                "Custo total": p.custo_total,
                "Lucro padrão (%)": p.lucro_padrao,
                "Preço sugerido": p.preco_sugerido,
                "Lucro": p.lucro,
            }
            for p in produtos
        ],
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.subheader("Novo produto")

if not filamentos:
    st.warning("Cadastre um filamento antes de criar um produto.")
else:
    with st.form("form_novo_produto"):
        nome = st.text_input("Nome do produto")
        filamento_id = st.selectbox(
            "Filamento",
            options=list(opcoes_filamento.keys()),
            format_func=lambda id_: opcoes_filamento[id_],
        )
        peso = st.number_input("Peso (g)", min_value=0.0, step=1.0)
        tempo = st.number_input("Tempo de impressão (h)", min_value=0.0, step=0.5)
        lucro_padrao = st.number_input(
            "Lucro padrão (%)", min_value=0.0, max_value=99.0, step=1.0, value=40.0
        )
        foto_arquivo = st.file_uploader("Foto do produto", type=["png", "jpg", "jpeg", "webp"])
        observacao = st.text_area("Observações")

        calcular = st.form_submit_button("Calcular")

    if calcular:
        try:
            resultado = produto_service.calcular_preco(filamento_id, peso, tempo, lucro_padrao)
            st.session_state["novo_produto_resultado"] = resultado
            st.session_state["novo_produto_dados"] = ProdutoData(
                nome=nome,
                filamento_id=filamento_id,
                peso=peso,
                tempo=tempo,
                lucro_padrao=lucro_padrao,
                observacao=observacao,
                foto=foto_arquivo.getvalue() if foto_arquivo else None,
            )
        except ValueError as erro:
            st.session_state.pop("novo_produto_resultado", None)
            st.session_state.pop("novo_produto_dados", None)
            st.error(str(erro))

    resultado = st.session_state.get("novo_produto_resultado")
    dados_pendentes = st.session_state.get("novo_produto_dados")
    if resultado and dados_pendentes:
        if dados_pendentes.foto:
            st.image(dados_pendentes.foto, width=200)
        st.markdown("**Resultado do cálculo**")
        col1, col2, col3 = st.columns(3)
        col1.metric("Custo filamento", f"R$ {resultado.custo_filamento:.2f}")
        col1.metric("Custo energia", f"R$ {resultado.custo_energia:.2f}")
        col2.metric("Custo desgaste", f"R$ {resultado.custo_desgaste:.2f}")
        col2.metric("Custo total", f"R$ {resultado.custo_total:.2f}")
        col3.metric("Preço sugerido", f"R$ {resultado.preco_sugerido:.2f}")
        col3.metric("Lucro", f"R$ {resultado.lucro:.2f}", f"{resultado.margem:.1f}% margem")

        if st.button("Salvar produto"):
            produto_service.criar(dados_pendentes, resultado)
            st.session_state.pop("novo_produto_resultado", None)
            st.session_state.pop("novo_produto_dados", None)
            st.success("Produto salvo com sucesso!")
            st.rerun()

if produtos:
    st.divider()
    st.subheader("Editar / excluir produto")

    opcoes_produto = {p.id: p.nome for p in produtos}
    selecionado_id = st.selectbox(
        "Selecione um produto",
        options=list(opcoes_produto.keys()),
        format_func=lambda id_: opcoes_produto[id_],
    )
    produto_atual = produto_service.obter(selecionado_id)

    if produto_atual.foto:
        st.image(produto_atual.foto, width=200)

    with st.form("form_editar_produto"):
        e_nome = st.text_input("Nome do produto", value=produto_atual.nome or "")
        filamento_ids = list(opcoes_filamento.keys())
        indice_atual = (
            filamento_ids.index(produto_atual.filamento_id)
            if produto_atual.filamento_id in filamento_ids
            else 0
        )
        e_filamento_id = st.selectbox(
            "Filamento",
            options=filamento_ids,
            format_func=lambda id_: opcoes_filamento[id_],
            index=indice_atual,
        )
        e_peso = st.number_input("Peso (g)", min_value=0.0, step=1.0, value=float(produto_atual.peso or 0))
        e_tempo = st.number_input(
            "Tempo de impressão (h)", min_value=0.0, step=0.5, value=float(produto_atual.tempo or 0)
        )
        e_lucro_padrao = st.number_input(
            "Lucro padrão (%)",
            min_value=0.0,
            max_value=99.0,
            step=1.0,
            value=float(produto_atual.lucro_padrao or 40),
        )
        e_foto_arquivo = st.file_uploader("Substituir foto (opcional)", type=["png", "jpg", "jpeg", "webp"])
        e_observacao = st.text_area("Observações", value=produto_atual.observacao or "")

        col_salvar, col_excluir = st.columns(2)
        recalcular_salvar = col_salvar.form_submit_button("Recalcular e salvar")
        excluir = col_excluir.form_submit_button("Excluir produto")

    if recalcular_salvar:
        try:
            resultado = produto_service.calcular_preco(e_filamento_id, e_peso, e_tempo, e_lucro_padrao)
            dados = ProdutoData(
                nome=e_nome,
                filamento_id=e_filamento_id,
                peso=e_peso,
                tempo=e_tempo,
                lucro_padrao=e_lucro_padrao,
                observacao=e_observacao,
                foto=e_foto_arquivo.getvalue() if e_foto_arquivo else produto_atual.foto,
            )
            produto_service.atualizar(selecionado_id, dados, resultado)
            st.success("Produto atualizado com sucesso!")
            st.rerun()
        except ValueError as erro:
            st.error(str(erro))

    if excluir:
        produto_service.excluir(selecionado_id)
        st.success("Produto excluído.")
        st.rerun()
