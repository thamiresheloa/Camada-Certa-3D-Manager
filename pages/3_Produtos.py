import io

import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

from services.filamento_service import FilamentoService
from services.produto_service import ProdutoData, ProdutoService
from utils.auth import exigir_login

exigir_login()

st.title("📦 Produtos")
st.caption("Ficha técnica e precificação automática dos produtos.")

produto_service = ProdutoService()
filamento_service = FilamentoService()

produtos = produto_service.listar()
filamentos = filamento_service.listar()
opcoes_filamento = {f.id: f.descricao for f in filamentos}


def editor_foto(arquivo, chave):
    """Mostra controles de girar e recortar para um arquivo de imagem recém enviado. Retorna os bytes finais (PNG)."""
    if arquivo is None:
        return None

    chave_rotacao = f"rotacao_{chave}"
    if chave_rotacao not in st.session_state:
        st.session_state[chave_rotacao] = 0

    col_esq, col_dir = st.columns(2)
    if col_esq.button("↺ Girar à esquerda", key=f"girar_esq_{chave}"):
        st.session_state[chave_rotacao] = (st.session_state[chave_rotacao] + 90) % 360
    if col_dir.button("↻ Girar à direita", key=f"girar_dir_{chave}"):
        st.session_state[chave_rotacao] = (st.session_state[chave_rotacao] - 90) % 360

    imagem = Image.open(arquivo)
    if st.session_state[chave_rotacao]:
        imagem = imagem.rotate(st.session_state[chave_rotacao], expand=True)

    imagem_cortada = st_cropper(
        imagem, realtime_update=True, box_color="#4CAF50", aspect_ratio=None, key=f"cropper_{chave}"
    )
    st.image(imagem_cortada, caption="Pré-visualização", width=200)

    buffer = io.BytesIO()
    imagem_cortada.convert("RGB").save(buffer, format="PNG")
    return buffer.getvalue()


st.subheader("Produtos cadastrados")

busca = st.text_input("🔍 Buscar produto", placeholder="Digite o nome do produto...")
produtos_filtrados = (
    [p for p in produtos if busca.strip().lower() in (p.nome or "").lower()] if busca else produtos
)

if not produtos:
    st.info("Nenhum produto cadastrado ainda.")
elif not produtos_filtrados:
    st.info("Nenhum produto encontrado para essa busca.")
else:
    for inicio in range(0, len(produtos_filtrados), 4):
        colunas = st.columns(4)
        for coluna, produto in zip(colunas, produtos_filtrados[inicio : inicio + 4]):
            with coluna:
                with st.container(border=True):
                    if produto.foto:
                        st.image(produto.foto, width=120)
                    else:
                        st.markdown("🖼️ *(sem foto)*")
                    st.markdown(f"**{produto.nome}**")
                    cor = produto.filamento.cor if produto.filamento else "-"
                    st.caption(f"Cor: {cor}")
                    preco_texto = f"R\\$ {produto.preco_sugerido:.2f}" if produto.preco_sugerido is not None else "-"
                    st.write(preco_texto)
                    if st.button("🗑️ Excluir", key=f"excluir_card_{produto.id}", use_container_width=True):
                        with st.spinner("Excluindo..."):
                            produto_service.excluir(produto.id)
                        st.toast("Produto excluído.", icon="🗑️")
                        st.rerun()

st.divider()
st.subheader("Novo produto")

if "upload_nonce" not in st.session_state:
    st.session_state["upload_nonce"] = 0

if not filamentos:
    st.warning("Cadastre um filamento antes de criar um produto.")
else:
    st.markdown("**Foto do produto (opcional)**")
    foto_arquivo_novo = st.file_uploader(
        "Selecione uma imagem",
        type=["png", "jpg", "jpeg", "webp"],
        key=f"upload_novo_{st.session_state['upload_nonce']}",
    )
    foto_bytes_novo = editor_foto(foto_arquivo_novo, "novo")

    with st.form("form_novo_produto", clear_on_submit=True):
        nome = st.text_input("Nome do produto", key="novo_nome")
        filamento_id = st.selectbox(
            "Filamento",
            options=list(opcoes_filamento.keys()),
            format_func=lambda id_: opcoes_filamento[id_],
            key="novo_filamento",
        )
        peso = st.number_input("Peso (g)", min_value=0.0, step=1.0, value=None, key="novo_peso")
        tempo = st.number_input(
            "Tempo de impressão (h)", min_value=0.0, step=0.5, value=None, key="novo_tempo"
        )
        lucro_padrao = st.number_input(
            "Lucro padrão (%)", min_value=0.0, max_value=99.0, step=1.0, value=40.0, key="novo_lucro"
        )
        observacao = st.text_area("Observações", key="novo_obs")

        calcular = st.form_submit_button("Calcular")

    if calcular:
        try:
            resultado = produto_service.calcular_preco(filamento_id, peso or 0.0, tempo or 0.0, lucro_padrao)
            st.session_state["novo_produto_resultado"] = resultado
            st.session_state["novo_produto_dados"] = ProdutoData(
                nome=nome,
                filamento_id=filamento_id,
                peso=peso or 0.0,
                tempo=tempo or 0.0,
                lucro_padrao=lucro_padrao,
                observacao=observacao,
                foto=foto_bytes_novo,
            )
        except ValueError as erro:
            st.session_state.pop("novo_produto_resultado", None)
            st.session_state.pop("novo_produto_dados", None)
            st.error(str(erro))

    resultado = st.session_state.get("novo_produto_resultado")
    dados_pendentes = st.session_state.get("novo_produto_dados")
    if resultado and dados_pendentes:
        st.markdown("**Resultado do cálculo**")
        col1, col2, col3 = st.columns(3)
        col1.metric("Custo filamento", f"R$ {resultado.custo_filamento:.2f}")
        col1.metric("Custo energia", f"R$ {resultado.custo_energia:.2f}")
        col2.metric("Custo desgaste", f"R$ {resultado.custo_desgaste:.2f}")
        col2.metric("Custo total", f"R$ {resultado.custo_total:.2f}")
        col3.metric("Preço sugerido", f"R$ {resultado.preco_sugerido:.2f}")
        col3.metric("Lucro", f"R$ {resultado.lucro:.2f}", f"{resultado.margem:.1f}% margem")

        if st.button("Salvar produto"):
            try:
                with st.spinner("Salvando..."):
                    produto_service.criar(dados_pendentes, resultado)
                st.session_state.pop("novo_produto_resultado", None)
                st.session_state.pop("novo_produto_dados", None)
                st.session_state.pop("rotacao_novo", None)
                st.session_state["upload_nonce"] += 1
                st.toast("Produto salvo com sucesso!", icon="✅")
                st.rerun()
            except ValueError as erro:
                st.error(str(erro))

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
        st.image(produto_atual.foto, caption="Foto atual", width=200)

    st.markdown("**Substituir foto (opcional)**")
    foto_arquivo_edicao = st.file_uploader(
        "Selecione uma nova imagem", type=["png", "jpg", "jpeg", "webp"], key=f"upload_edicao_{selecionado_id}"
    )
    foto_bytes_edicao = editor_foto(foto_arquivo_edicao, f"edicao_{selecionado_id}")

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
                foto=foto_bytes_edicao if foto_bytes_edicao else produto_atual.foto,
            )
            with st.spinner("Salvando..."):
                produto_service.atualizar(selecionado_id, dados, resultado)
            st.toast("Produto atualizado com sucesso!", icon="✅")
            st.rerun()
        except ValueError as erro:
            st.error(str(erro))

    if excluir:
        with st.spinner("Excluindo..."):
            produto_service.excluir(selecionado_id)
        st.toast("Produto excluído.", icon="🗑️")
        st.rerun()
