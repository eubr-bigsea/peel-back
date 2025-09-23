from models import db, Model
from typing import Optional
from logger import setup_logger

logger = setup_logger()


class ModelDAO:
    @staticmethod
    def create_model(name: str,
                     description: str,
                     enable: bool,
                     path: str,
                     model_type: str,
                     version: str,
                     class_name: str,
                     digest: str) -> Optional[Model]:
        try:
            new_model = Model(
                name=name,
                description=description,
                enable=enable,
                path=path,
                model_type=model_type,
                version=version,
                class_name=class_name,
                digest=digest
            )
            db.session.add(new_model)
            db.session.commit()
            logger.info(f"[ModelDAO] Created model: {new_model} with id {new_model.id}")
            return new_model
        except Exception as e:
            db.session.rollback()
            logger.error(f"[ModelDAO] Failed to create model: {e}")
            raise e

    @staticmethod
    def get_model_by_id(model_id: int) -> Optional[Model]:
        try:
            model = Model.query.get(model_id)
            logger.info(f"[ModelDAO] Retrieved model with ID {model_id}: {model}")
            return model
        except Exception as e:
            logger.error(f"[ModelDAO] Failed to retrieve model with ID {model_id}: {e}")
            raise e

    @staticmethod
    def update_model(model_id: int, **kwargs) -> Optional[Model]:
        try:
            model = Model.query.get(model_id)
            if not model:
                logger.warning(f"Model with ID {model_id} not found.")
                return None

            for key, value in kwargs.items():
                if hasattr(model, key):
                    setattr(model, key, value)

            db.session.commit()
            logger.info(f"Updated model with ID {model_id}")
            return model
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update model with ID {model_id}: {e}")
            raise e

    @staticmethod
    def delete_model(model_id: int) -> bool:
        try:
            model = Model.query.get(model_id)
            if not model:
                logger.warning(f"[ModelDAO] Model with ID {model_id} not found.")
                return False
            db.session.delete(model)
            db.session.commit()
            logger.info(f"[ModelDAO] Deleted model with ID {model_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"[ModelDAO] Failed to delete model with ID {model_id}: {e}")
            raise e
