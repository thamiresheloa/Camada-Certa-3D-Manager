from models.configuracao import Configuracao
from repositories.base_repository import BaseRepository


class ConfiguracaoRepository(BaseRepository):
    model = Configuracao
