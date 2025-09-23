from models import db, Understanding
from datetime import datetime

class UnderstandingDAO:
    @staticmethod
    def create_understanding(id_datasource, id_model, understanding_type, xai_class, sample, enable=True):
        try:
            new_understanding = Understanding(
                id_datasource=id_datasource,
                id_model=id_model,
                understanding_type=understanding_type,
                xai_class=xai_class,
                sample=sample,
                enable=enable
            )
            db.session.add(new_understanding)
            db.session.commit()
            return new_understanding
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_understanding_by_id(understanding_id):
        try:
            return Understanding.query.get(understanding_id)
        except Exception as e:
            raise e

    @staticmethod
    def update_understanding(understanding_id, **kwargs):
        try:
            understanding = Understanding.query.get(understanding_id)
            if not understanding:
                return None

            for key, value in kwargs.items():
                if hasattr(understanding, key):
                    setattr(understanding, key, value)

            db.session.commit()
            return understanding
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_understanding(understanding_id):
        try:
            understanding = Understanding.query.get(understanding_id)
            if not understanding:
                return False
            db.session.delete(understanding)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
