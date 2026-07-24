from dataclasses import dataclass


@dataclass
class ResultadoPrecificacao:
    custo_filamento: float
    custo_energia: float
    custo_desgaste: float
    custo_total: float
    preco_sugerido: float
    lucro: float
    margem: float


class PrecificacaoService:
    def calcular(
        self,
        peso: float,
        tempo: float,
        valor_kg: float,
        potencia_impressora: float,
        energia_kwh: float,
        percentual_desgaste: float,
        lucro_padrao: float,
    ) -> ResultadoPrecificacao:
        custo_filamento = (peso / 1000) * valor_kg
        custo_energia = (potencia_impressora / 1000) * tempo * energia_kwh
        custo_operacional = custo_filamento + custo_energia
        custo_desgaste = custo_operacional * (percentual_desgaste / 100)
        custo_total = custo_operacional + custo_desgaste
        preco_sugerido = custo_total * (1 + lucro_padrao / 100)
        lucro = preco_sugerido - custo_total
        margem = (lucro / preco_sugerido * 100) if preco_sugerido else 0.0

        return ResultadoPrecificacao(
            custo_filamento=round(custo_filamento, 2),
            custo_energia=round(custo_energia, 2),
            custo_desgaste=round(custo_desgaste, 2),
            custo_total=round(custo_total, 2),
            preco_sugerido=round(preco_sugerido, 2),
            lucro=round(lucro, 2),
            margem=round(margem, 2),
        )
