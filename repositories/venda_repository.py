from models.venda import Venda
from repositories.base_repository import BaseRepository


class VendaRepository(BaseRepository):
    model = Venda
