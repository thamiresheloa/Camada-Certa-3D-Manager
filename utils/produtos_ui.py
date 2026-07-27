import streamlit as st

TAMANHO_MINIATURA = 140
LIMITE_NOME_EXIBICAO = 36


def renderizar_miniatura(foto_url: str | None, tamanho: int = TAMANHO_MINIATURA):
    """Mostra a foto do produto (ou um placeholder) sempre no mesmo tamanho quadrado.

    Usa a URL pública do Supabase Storage em vez de embutir os bytes na página,
    para o navegador poder cachear a imagem e a navegação ficar mais rápida.
    """
    if foto_url:
        st.markdown(
            f'<img src="{foto_url}" loading="lazy" '
            f'style="width:100%;max-width:{tamanho}px;aspect-ratio:1/1;object-fit:cover;'
            f'border-radius:8px;display:block;" />',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="width:100%;max-width:{tamanho}px;aspect-ratio:1/1;display:flex;'
            f'align-items:center;justify-content:center;background:#f0f0f0;border-radius:8px;'
            f'font-size:2rem;">🖼️</div>',
            unsafe_allow_html=True,
        )


def truncar_nome(nome: str | None, limite: int = LIMITE_NOME_EXIBICAO) -> str:
    """Encurta o nome para exibição no card, mantendo a altura do card previsível."""
    if not nome:
        return "-"
    return nome if len(nome) <= limite else nome[: limite - 1].rstrip() + "…"
