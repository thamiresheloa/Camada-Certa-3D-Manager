from database.connection import SessionLocal
from models.item_venda import ItemVenda
from models.venda import Venda
from repositories.base_repository import BaseRepository


class VendaRepository(BaseRepository):
    model = Venda

    def criar_com_itens(self, campos_venda: dict, itens: list[dict]):
        with SessionLocal() as session:
            venda = Venda(**campos_venda)
            session.add(venda)
            session.flush()
            for item in itens:
                session.add(ItemVenda(venda_id=venda.id, **item))
            session.commit()
            session.refresh(venda)
            return venda

    def atualizar_com_itens(self, id_, campos_venda: dict, itens: list[dict]):
        with SessionLocal() as session:
            venda = session.get(Venda, id_)
            if venda is None:
                return None
            for key, value in campos_venda.items():
                setattr(venda, key, value)
            session.query(ItemVenda).filter(ItemVenda.venda_id == id_).delete()
            session.flush()
            for item in itens:
                session.add(ItemVenda(venda_id=id_, **item))
            session.commit()
            session.refresh(venda)
            return venda
