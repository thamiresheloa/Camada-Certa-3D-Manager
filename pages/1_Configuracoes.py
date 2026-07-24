import streamlit as st

from services.configuracao_service import ConfiguracaoData, ConfiguracaoService

st.set_page_config(page_title="Configurações", page_icon="⚙️")
st.title("⚙️ Configurações")
st.caption("Parâmetros globais usados automaticamente nos cálculos de precificação.")

service = ConfiguracaoService()
config_atual = service.obter()

with st.form("form_configuracoes"):
    energia_kwh = st.number_input(
        "Tarifa de energia (R$/kWh)",
        min_value=0.0,
        value=float(config_atual.energia_kwh) if config_atual else 0.0,
        step=0.01,
        format="%.4f",
    )
    potencia_impressora = st.number_input(
        "Potência média da impressora (W)",
        min_value=0.0,
        value=float(config_atual.potencia_impressora) if config_atual else 0.0,
        step=1.0,
    )
    percentual_desgaste = st.number_input(
        "Percentual de desgaste (%)",
        min_value=0.0,
        max_value=100.0,
        value=float(config_atual.percentual_desgaste) if config_atual else 0.0,
        step=0.5,
    )
    lucro_padrao = st.number_input(
        "Lucro padrão (%)",
        min_value=0.0,
        value=float(config_atual.lucro_padrao) if config_atual else 0.0,
        step=1.0,
    )

    salvar = st.form_submit_button("Salvar")

if salvar:
    try:
        dados = ConfiguracaoData(
            energia_kwh=energia_kwh,
            potencia_impressora=potencia_impressora,
            percentual_desgaste=percentual_desgaste,
            lucro_padrao=lucro_padrao,
        )
        service.salvar(dados)
        st.success("Configurações salvas com sucesso!")
        st.rerun()
    except ValueError as erro:
        st.error(str(erro))
