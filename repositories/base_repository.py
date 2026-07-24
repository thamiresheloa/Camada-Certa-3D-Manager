from database.connection import SessionLocal


class BaseRepository:
    model = None

    def get_all(self):
        with SessionLocal() as session:
            return session.query(self.model).order_by(self.model.id).all()

    def get_by_id(self, id_):
        with SessionLocal() as session:
            return session.get(self.model, id_)

    def create(self, **kwargs):
        with SessionLocal() as session:
            obj = self.model(**kwargs)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def update(self, id_, **kwargs):
        with SessionLocal() as session:
            obj = session.get(self.model, id_)
            if obj is None:
                return None
            for key, value in kwargs.items():
                setattr(obj, key, value)
            session.commit()
            session.refresh(obj)
            return obj

    def delete(self, id_):
        with SessionLocal() as session:
            obj = session.get(self.model, id_)
            if obj is None:
                return False
            session.delete(obj)
            session.commit()
            return True
