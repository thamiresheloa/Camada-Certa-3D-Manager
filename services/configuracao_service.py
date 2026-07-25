from dataclasses import dataclass

from repositories.configuracao_repository import ConfiguracaoRepository


@dataclass
class ConfiguracaoData:
    energia_kwh: float
    potencia_impressora: float
    percentual_desgaste: float


class ConfiguracaoService:
    def __init__(self, repository: ConfiguracaoRepository | None = None):
        self.repository = repository or ConfiguracaoRepository()

    def obter(self):
        configuracoes = self.repository.get_all()
        return configuracoes[0] if configuracoes else None

    def salvar(self, dados: ConfiguracaoData):
        self._validar(dados)
        campos = {
            "energia_kwh": dados.energia_kwh,
            "potencia_impressora": dados.potencia_impressora,
            "percentual_desgaste": dados.percentual_desgaste,
        }
        atual = self.obter()
        if atual is None:
            return self.repository.create(**campos)
        return self.repository.update(atual.id, **campos)

    def _validar(self, dados: ConfiguracaoData):
        if dados.energia_kwh < 0:
            raise ValueError("Tarifa de energia não pode ser negativa.")
        if dados.potencia_impressora <= 0:
            raise ValueError("Potência da impressora deve ser maior que zero.")
        if not (0 <= dados.percentual_desgaste <= 100):
            raise ValueError("Percentual de desgaste deve estar entre 0 e 100.")
