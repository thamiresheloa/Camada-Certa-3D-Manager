from dataclasses import dataclass
from datetime import date

from repositories.venda_repository import VendaRepository


@dataclass
class ResumoDashboard:
    receita_mes: float
    lucro_mes: float
    produtos_vendidos_mes: int
    pedidos_mes: int
    horas_impressao_mes: float
    filamento_consumido_mes: float
    ultimas_vendas: list
    produtos_mais_vendidos: list


class DashboardService:
    def __init__(self, venda_repository: VendaRepository | None = None):
        self.venda_repository = venda_repository or VendaRepository()

    def resumo(self, referencia: date | None = None) -> ResumoDashboard:
        referencia = referencia or date.today()
        vendas = self.venda_repository.get_all()

        vendas_mes = [
            v
            for v in vendas
            if v.data_venda and v.data_venda.year == referencia.year and v.data_venda.month == referencia.month
        ]

        receita_mes = sum(v.valor_venda or 0 for v in vendas_mes)
        lucro_mes = sum((v.produto.lucro or 0) * (v.quantidade or 0) for v in vendas_mes if v.produto)
        produtos_vendidos_mes = sum(v.quantidade or 0 for v in vendas_mes)
        pedidos_mes = len(vendas_mes)
        horas_impressao_mes = sum((v.produto.tempo or 0) * (v.quantidade or 0) for v in vendas_mes if v.produto)
        filamento_consumido_mes = sum((v.produto.peso or 0) * (v.quantidade or 0) for v in vendas_mes if v.produto)

        ultimas_vendas = sorted(vendas, key=lambda v: v.id, reverse=True)[:10]

        ranking: dict[str, int] = {}
        for v in vendas:
            if not v.produto:
                continue
            ranking[v.produto.nome] = ranking.get(v.produto.nome, 0) + (v.quantidade or 0)
        produtos_mais_vendidos = sorted(ranking.items(), key=lambda item: item[1], reverse=True)[:5]

        return ResumoDashboard(
            receita_mes=round(receita_mes, 2),
            lucro_mes=round(lucro_mes, 2),
            produtos_vendidos_mes=produtos_vendidos_mes,
            pedidos_mes=pedidos_mes,
            horas_impressao_mes=round(horas_impressao_mes, 2),
            filamento_consumido_mes=round(filamento_consumido_mes, 2),
            ultimas_vendas=ultimas_vendas,
            produtos_mais_vendidos=produtos_mais_vendidos,
        )
