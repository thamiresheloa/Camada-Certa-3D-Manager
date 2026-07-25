from dataclasses import dataclass
from datetime import date

from repositories.venda_repository import VendaRepository


@dataclass
class Relatorio:
    receita_total: float
    lucro_total: float
    ticket_medio: float
    pedidos: int
    horas_impressas: float
    consumo_material: float
    produtos_mais_vendidos: list
    filamento_mais_utilizado: list
    receita_por_dia: list


class RelatorioService:
    def __init__(self, venda_repository: VendaRepository | None = None):
        self.venda_repository = venda_repository or VendaRepository()

    def gerar(self, data_inicio: date | None = None, data_fim: date | None = None) -> Relatorio:
        vendas = self.venda_repository.get_all()

        if data_inicio:
            vendas = [v for v in vendas if v.data_venda and v.data_venda >= data_inicio]
        if data_fim:
            vendas = [v for v in vendas if v.data_venda and v.data_venda <= data_fim]

        receita_total = sum(v.valor_venda or 0 for v in vendas)
        lucro_total = sum((v.produto.lucro or 0) * (v.quantidade or 0) for v in vendas if v.produto)
        pedidos = len(vendas)
        ticket_medio = round(receita_total / pedidos, 2) if pedidos else 0.0
        horas_impressas = sum((v.produto.tempo or 0) * (v.quantidade or 0) for v in vendas if v.produto)
        consumo_material = sum((v.produto.peso or 0) * (v.quantidade or 0) for v in vendas if v.produto)

        ranking_produtos: dict[str, int] = {}
        ranking_filamento: dict[str, float] = {}
        receita_por_dia: dict[date, float] = {}

        for v in vendas:
            if v.produto:
                ranking_produtos[v.produto.nome] = ranking_produtos.get(v.produto.nome, 0) + (v.quantidade or 0)
                if v.produto.filamento:
                    consumo = (v.produto.peso or 0) * (v.quantidade or 0)
                    descricao_filamento = v.produto.filamento.descricao
                    ranking_filamento[descricao_filamento] = ranking_filamento.get(descricao_filamento, 0) + consumo
            if v.data_venda:
                receita_por_dia[v.data_venda] = receita_por_dia.get(v.data_venda, 0) + (v.valor_venda or 0)

        return Relatorio(
            receita_total=round(receita_total, 2),
            lucro_total=round(lucro_total, 2),
            ticket_medio=ticket_medio,
            pedidos=pedidos,
            horas_impressas=round(horas_impressas, 2),
            consumo_material=round(consumo_material, 2),
            produtos_mais_vendidos=sorted(ranking_produtos.items(), key=lambda i: i[1], reverse=True),
            filamento_mais_utilizado=sorted(ranking_filamento.items(), key=lambda i: i[1], reverse=True),
            receita_por_dia=sorted(receita_por_dia.items()),
        )
