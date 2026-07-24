from models.produto import Produto
from repositories.base_repository import BaseRepository


class ProdutoRepository(BaseRepository):
    model = Produto
