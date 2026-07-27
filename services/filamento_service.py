from dataclasses import dataclass
from datetime import date

import streamlit as st

from repositories.filamento_repository import FilamentoRepository


@st.cache_data(ttl=30, show_spinner=False)
def _listar_filamentos_cache():
    return FilamentoRepository().get_all()


@dataclass
class FilamentoData:
    tipo: str
    especificacao: str
    cor: str
    marca: str
    valor_kg: float
    peso_original: float
    peso_restante: float
    fornecedor: str | None = None
    data_compra: date | None = None
    validade: date | None = None


class FilamentoService:
    def __init__(self, repository: FilamentoRepository | None = None):
        self.repository = repository or FilamentoRepository()

    def listar(self):
        return sorted(_listar_filamentos_cache(), key=lambda f: f.descricao.lower())

    def obter(self, id_):
        return self.repository.get_by_id(id_)

    def criar(self, dados: FilamentoData):
        self._validar(dados)
        filamento = self.repository.create(**self._campos(dados))
        _listar_filamentos_cache.clear()
        return filamento

    def atualizar(self, id_, dados: FilamentoData):
        self._validar(dados)
        filamento = self.repository.update(id_, **self._campos(dados))
        _listar_filamentos_cache.clear()
        return filamento

    def excluir(self, id_):
        resultado = self.repository.delete(id_)
        _listar_filamentos_cache.clear()
        return resultado

    def _campos(self, dados: FilamentoData):
        return {
            "tipo": dados.tipo.strip(),
            "especificacao": dados.especificacao.strip(),
            "cor": dados.cor.strip(),
            "marca": dados.marca.strip(),
            "valor_kg": dados.valor_kg,
            "peso_original": dados.peso_original,
            "peso_restante": dados.peso_restante,
            "fornecedor": dados.fornecedor.strip() if dados.fornecedor else None,
            "data_compra": dados.data_compra,
            "validade": dados.validade,
        }

    def _validar(self, dados: FilamentoData):
        if not dados.cor or not dados.cor.strip():
            raise ValueError("Cor do filamento é obrigatória.")
        if not dados.marca or not dados.marca.strip():
            raise ValueError("Marca do filamento é obrigatória.")
        if dados.valor_kg <= 0:
            raise ValueError("Valor por kg deve ser maior que zero.")
        if dados.peso_original <= 0:
            raise ValueError("Peso original deve ser maior que zero.")
        if dados.peso_restante < 0:
            raise ValueError("Peso restante não pode ser negativo.")
        if dados.peso_restante > dados.peso_original:
            raise ValueError("Peso restante não pode ser maior que o peso original.")
