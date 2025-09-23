from datetime import datetime
from models import db, InfoArguments
from typing import Optional
from logger import setup_logger

logger = setup_logger()


class InfoArgumentsDAO:
    @staticmethod
    def create_info_arguments(enable: bool,
                              source: int,
                              understanding_id: int,
                              path_xai: str,
                              xai_base: str,
                              library: str,
                              version: str) -> Optional[InfoArguments]:
        try:
            new_info_arguments = InfoArguments(
                enable=enable,
                source=source,
                understanding_id=understanding_id,
                path_xai=path_xai,
                xai_base=xai_base,
                library=library,
                version=version
            )
            db.session.add(new_info_arguments)
            db.session.commit()
            logger.info(f"[{InfoArgumentsDAO.__name__}] Created info arguments: {new_info_arguments}")
            return new_info_arguments
        except Exception as e:
            db.session.rollback()
            logger.error(f"[{InfoArgumentsDAO.__name__}] Failed to create info arguments: {e}")
            raise e

    @staticmethod
    def get_info_arguments_by_id(info_arguments_id: int) -> Optional[InfoArguments]:
        try:
            info_arguments = InfoArguments.query.get(info_arguments_id)
            logger.info(f"[{InfoArgumentsDAO.__name__}] Retrieved info arguments with ID {info_arguments_id}: {info_arguments}")
            return info_arguments
        except Exception as e:
            logger.error(f"[{InfoArgumentsDAO.__name__}] Failed to retrieve info arguments with ID {info_arguments_id}: {e}")
            raise e

    @staticmethod
    def update_info_arguments(info_arguments_id: int, **kwargs) -> Optional[InfoArguments]:
        try:
            info_arguments = InfoArguments.query.get(info_arguments_id)
            if not info_arguments:
                logger.warning(f"[{InfoArgumentsDAO.__name__}] Info arguments with ID {info_arguments_id} not found.")
                return None
            for key, value in kwargs.items():
                setattr(info_arguments, key, value)
            db.session.commit()
            logger.info(f"[{InfoArgumentsDAO.__name__}] Updated info arguments with ID {info_arguments_id}")
            return info_arguments
        except Exception as e:
            db.session.rollback()
            logger.error(f"[{InfoArgumentsDAO.__name__}] Failed to update info arguments with ID {info_arguments_id}: {e}")
            raise e

    @staticmethod
    def delete_info_arguments(info_arguments_id: int) -> bool:
        try:
            info_arguments = InfoArguments.query.get(info_arguments_id)
            if not info_arguments:
                logger.warning(f"[{InfoArgumentsDAO.__name__}] Info arguments with ID {info_arguments_id} not found.")
                return False
            db.session.delete(info_arguments)
            db.session.commit()
            logger.info(f"[{InfoArgumentsDAO.__name__}] Deleted info arguments with ID {info_arguments_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"[{InfoArgumentsDAO.__name__}] Failed to delete info arguments with ID {info_arguments_id}: {e}")
            raise e
