from dataclasses import dataclass
from datetime import date

from repositories.filamento_repository import FilamentoRepository


@dataclass
class FilamentoData:
    nome: str
    marca: str
    cor: str
    tipo: str
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
        return sorted(self.repository.get_all(), key=lambda f: (f.nome or "").lower())

    def obter(self, id_):
        return self.repository.get_by_id(id_)

    def criar(self, dados: FilamentoData):
        self._validar(dados)
        return self.repository.create(**self._campos(dados))

    def atualizar(self, id_, dados: FilamentoData):
        self._validar(dados)
        return self.repository.update(id_, **self._campos(dados))

    def excluir(self, id_):
        return self.repository.delete(id_)

    def _campos(self, dados: FilamentoData):
        return {
            "nome": dados.nome.strip(),
            "marca": dados.marca.strip(),
            "cor": dados.cor.strip(),
            "tipo": dados.tipo.strip(),
            "valor_kg": dados.valor_kg,
            "peso_original": dados.peso_original,
            "peso_restante": dados.peso_restante,
            "fornecedor": dados.fornecedor.strip() if dados.fornecedor else None,
            "data_compra": dados.data_compra,
            "validade": dados.validade,
        }

    def _validar(self, dados: FilamentoData):
        if not dados.nome or not dados.nome.strip():
            raise ValueError("Nome do filamento é obrigatório.")
        if dados.valor_kg <= 0:
            raise ValueError("Valor por kg deve ser maior que zero.")
        if dados.peso_original <= 0:
            raise ValueError("Peso original deve ser maior que zero.")
        if dados.peso_restante < 0:
            raise ValueError("Peso restante não pode ser negativo.")
        if dados.peso_restante > dados.peso_original:
            raise ValueError("Peso restante não pode ser maior que o peso original.")
