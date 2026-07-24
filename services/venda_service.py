from dataclasses import dataclass
from datetime import date

from repositories.produto_repository import ProdutoRepository
from repositories.venda_repository import VendaRepository


@dataclass
class VendaData:
    produto_id: int
    quantidade: int
    valor_venda: float
    cliente: str | None = None
    canal: str | None = None
    forma_pagamento: str | None = None
    data_venda: date | None = None


class VendaService:
    def __init__(
        self,
        repository: VendaRepository | None = None,
        produto_repository: ProdutoRepository | None = None,
    ):
        self.repository = repository or VendaRepository()
        self.produto_repository = produto_repository or ProdutoRepository()

    def listar(self):
        return sorted(self.repository.get_all(), key=lambda v: v.id, reverse=True)

    def obter(self, id_):
        return self.repository.get_by_id(id_)

    def sugerir_valor_total(self, produto_id: int, quantidade: int) -> float:
        produto = self.produto_repository.get_by_id(produto_id)
        if produto is None or produto.preco_sugerido is None:
            return 0.0
        return round(produto.preco_sugerido * quantidade, 2)

    def criar(self, dados: VendaData):
        self._validar(dados)
        return self.repository.create(**self._campos(dados))

    def atualizar(self, id_, dados: VendaData):
        self._validar(dados)
        return self.repository.update(id_, **self._campos(dados))

    def excluir(self, id_):
        return self.repository.delete(id_)

    def _campos(self, dados: VendaData):
        return {
            "produto_id": dados.produto_id,
            "quantidade": dados.quantidade,
            "valor_venda": dados.valor_venda,
            "cliente": dados.cliente.strip() if dados.cliente else None,
            "canal": dados.canal.strip() if dados.canal else None,
            "forma_pagamento": dados.forma_pagamento.strip() if dados.forma_pagamento else None,
            "data_venda": dados.data_venda,
        }

    def _validar(self, dados: VendaData):
        if dados.produto_id is None:
            raise ValueError("Selecione um produto.")
        if dados.quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero.")
        if dados.valor_venda < 0:
            raise ValueError("Valor da venda não pode ser negativo.")
