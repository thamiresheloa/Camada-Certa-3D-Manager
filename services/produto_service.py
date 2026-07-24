from dataclasses import dataclass

from repositories.configuracao_repository import ConfiguracaoRepository
from repositories.filamento_repository import FilamentoRepository
from repositories.produto_repository import ProdutoRepository
from services.precificacao_service import PrecificacaoService, ResultadoPrecificacao


@dataclass
class ProdutoData:
    nome: str
    filamento_id: int
    peso: float
    tempo: float
    observacao: str | None = None
    foto: str | None = None


class ProdutoService:
    def __init__(
        self,
        repository: ProdutoRepository | None = None,
        filamento_repository: FilamentoRepository | None = None,
        configuracao_repository: ConfiguracaoRepository | None = None,
        precificacao_service: PrecificacaoService | None = None,
    ):
        self.repository = repository or ProdutoRepository()
        self.filamento_repository = filamento_repository or FilamentoRepository()
        self.configuracao_repository = configuracao_repository or ConfiguracaoRepository()
        self.precificacao_service = precificacao_service or PrecificacaoService()

    def listar(self):
        return sorted(self.repository.get_all(), key=lambda p: (p.nome or "").lower())

    def obter(self, id_):
        return self.repository.get_by_id(id_)

    def calcular_preco(self, filamento_id: int, peso: float, tempo: float) -> ResultadoPrecificacao:
        filamento = self.filamento_repository.get_by_id(filamento_id)
        if filamento is None:
            raise ValueError("Filamento não encontrado.")

        configuracao = self._obter_configuracao()

        return self.precificacao_service.calcular(
            peso=peso,
            tempo=tempo,
            valor_kg=filamento.valor_kg,
            potencia_impressora=configuracao.potencia_impressora,
            energia_kwh=configuracao.energia_kwh,
            percentual_desgaste=configuracao.percentual_desgaste,
            lucro_padrao=configuracao.lucro_padrao,
        )

    def criar(self, dados: ProdutoData, resultado: ResultadoPrecificacao):
        self._validar(dados)
        return self.repository.create(**self._campos(dados, resultado))

    def atualizar(self, id_, dados: ProdutoData, resultado: ResultadoPrecificacao):
        self._validar(dados)
        return self.repository.update(id_, **self._campos(dados, resultado))

    def excluir(self, id_):
        return self.repository.delete(id_)

    def _obter_configuracao(self):
        configuracoes = self.configuracao_repository.get_all()
        if not configuracoes:
            raise ValueError("Cadastre as Configurações (tarifa, potência, desgaste, lucro) antes de precificar um produto.")
        return configuracoes[0]

    def _campos(self, dados: ProdutoData, resultado: ResultadoPrecificacao):
        return {
            "nome": dados.nome.strip(),
            "filamento_id": dados.filamento_id,
            "peso": dados.peso,
            "tempo": dados.tempo,
            "observacao": dados.observacao.strip() if dados.observacao else None,
            "foto": dados.foto.strip() if dados.foto else None,
            "custo_filamento": resultado.custo_filamento,
            "custo_energia": resultado.custo_energia,
            "custo_desgaste": resultado.custo_desgaste,
            "custo_total": resultado.custo_total,
            "preco_sugerido": resultado.preco_sugerido,
            "lucro": resultado.lucro,
        }

    def _validar(self, dados: ProdutoData):
        if not dados.nome or not dados.nome.strip():
            raise ValueError("Nome do produto é obrigatório.")
        if dados.filamento_id is None:
            raise ValueError("Selecione um filamento.")
        if dados.peso <= 0:
            raise ValueError("Peso deve ser maior que zero.")
        if dados.tempo <= 0:
            raise ValueError("Tempo de impressão deve ser maior que zero.")
