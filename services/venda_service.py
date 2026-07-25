from dataclasses import dataclass
from datetime import date

from repositories.produto_repository import ProdutoRepository
from repositories.venda_repository import VendaRepository


@dataclass
class ItemVendaData:
    produto_id: int
    quantidade: int
    valor_unitario: float


@dataclass
class VendaData:
    itens: list[ItemVendaData]
    pago: bool
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

    def sugerir_valor_unitario(self, produto_id: int) -> float:
        produto = self.produto_repository.get_by_id(produto_id)
        if produto is None or produto.preco_sugerido is None:
            return 0.0
        return produto.preco_sugerido

    def criar(self, dados: VendaData):
        self._validar(dados)
        campos, itens = self._campos(dados)
        return self.repository.criar_com_itens(campos, itens)

    def atualizar(self, id_, dados: VendaData):
        self._validar(dados)
        campos, itens = self._campos(dados)
        return self.repository.atualizar_com_itens(id_, campos, itens)

    def excluir(self, id_):
        return self.repository.delete(id_)

    def _campos(self, dados: VendaData):
        valor_total = sum(item.quantidade * item.valor_unitario for item in dados.itens)
        campos = {
            "cliente": dados.cliente.strip() if dados.cliente else None,
            "canal": dados.canal.strip() if dados.canal else None,
            "forma_pagamento": dados.forma_pagamento.strip() if dados.forma_pagamento else None,
            "data_venda": dados.data_venda,
            "pago": dados.pago,
            "valor_venda": round(valor_total, 2),
        }
        itens = [
            {
                "produto_id": item.produto_id,
                "quantidade": item.quantidade,
                "valor_unitario": item.valor_unitario,
            }
            for item in dados.itens
        ]
        return campos, itens

    def _validar(self, dados: VendaData):
        if not dados.itens:
            raise ValueError("Adicione pelo menos um produto à venda.")
        for item in dados.itens:
            if item.produto_id is None:
                raise ValueError("Selecione um produto para cada item.")
            if item.quantidade <= 0:
                raise ValueError("Quantidade deve ser maior que zero em todos os itens.")
            if item.valor_unitario < 0:
                raise ValueError("Valor unitário não pode ser negativo.")
