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
        pedidos = len(vendas)
        ticket_medio = round(receita_total / pedidos, 2) if pedidos else 0.0

        lucro_total = 0.0
        horas_impressas = 0.0
        consumo_material = 0.0
        ranking_produtos: dict[str, int] = {}
        ranking_filamento: dict[str, float] = {}
        receita_por_dia: dict[date, float] = {}

        for v in vendas:
            for item in v.itens:
                if not item.produto:
                    continue
                quantidade = item.quantidade or 0
                lucro_total += (item.produto.lucro or 0) * quantidade
                horas_impressas += (item.produto.tempo or 0) * quantidade
                consumo_material += (item.produto.peso or 0) * quantidade
                ranking_produtos[item.produto.nome] = ranking_produtos.get(item.produto.nome, 0) + quantidade
                if item.produto.filamento:
                    consumo = (item.produto.peso or 0) * quantidade
                    descricao_filamento = item.produto.filamento.descricao
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
