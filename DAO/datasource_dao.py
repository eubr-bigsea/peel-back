from datetime import datetime
from models import db, Datasource
from typing import Optional
from logger import setup_logger

logger = setup_logger()


class DataSourceDAO:
    @staticmethod
    def create_datasource(name: str,
                          description: str,
                          enable: bool,
                          read_only: bool,
                          url: str,
                          data_format: str,
                          provenience: str,
                          estimated_rows: int,
                          estimated_size_mb: int,
                          attributed_delimiter: Optional[str] = None,
                          record_delimiter: Optional[str] = None,
                          text_delimiter: Optional[str] = None,
                          is_public: bool = None,
                          treat_as_missing: bool = None,
                          encoding: str = None,
                          is_first_line_header: bool = None,
                          is_multiline: bool = None,
                          command: str = None,
                          is_lookup: bool = None) -> Optional[Datasource]:
        try:
            new_datasource = Datasource(
                name=name,
                description=description,
                enable=enable,
                read_only=read_only,
                url=url,
                data_format=data_format,
                provenience=provenience,
                estimated_rows=estimated_rows,
                estimated_size_mb=estimated_size_mb,
                attributed_delimiter=attributed_delimiter,
                record_delimiter=record_delimiter,
                text_delimiter=text_delimiter,
                is_public=is_public,
                treat_as_missing=treat_as_missing,
                encoding=encoding,
                is_first_line_header=is_first_line_header,
                is_multiline=is_multiline,
                command=command,
                is_lookup=is_lookup
            )
            db.session.add(new_datasource)
            db.session.commit()
            logger.info(f"[{DataSourceDAO.__name__}] Created datasource: {new_datasource}")
            return new_datasource
        except Exception as e:
            db.session.rollback()
            logger.error(f"[{DataSourceDAO.__name__}] Failed to create datasource: {e}")
            raise e

    @staticmethod
    def get_datasource_by_id(datasource_id: int) -> Optional[Datasource]:
        try:
            datasource = Datasource.query.get(datasource_id)
            logger.info(f"[{DataSourceDAO.__name__}] Retrieved datasource with ID {datasource_id}: {datasource}")
            return datasource
        except Exception as e:
            logger.error(f"[{DataSourceDAO.__name__}] Failed to retrieve datasource with ID {datasource_id}: {e}")
            raise e

    @staticmethod
    def update_datasource(datasource_id: int, **kwargs) -> Optional[Datasource]:
        try:
            datasource = Datasource.query.get(datasource_id)
            if not datasource:
                logger.warning(f"[{DataSourceDAO.__name__}] Datasource with ID {datasource_id} not found.")
                return None
            for key, value in kwargs.items():
                setattr(datasource, key, value)
            db.session.commit()
            logger.info(f"[{DataSourceDAO.__name__}] Updated datasource with ID {datasource_id}")
            return datasource
        except Exception as e:
            db.session.rollback()
            logger.error(f"[{DataSourceDAO.__name__}] Failed to update datasource with ID {datasource_id}: {e}")
            raise e

    @staticmethod
    def delete_datasource(datasource_id: int) -> bool:
        try:
            datasource = Datasource.query.get(datasource_id)
            if not datasource:
                logger.warning(f"[{DataSourceDAO.__name__}] Datasource with ID {datasource_id} not found.")
                return False
            db.session.delete(datasource)
            db.session.commit()
            logger.info(f"[{DataSourceDAO.__name__}] Deleted datasource with ID {datasource_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"[{DataSourceDAO.__name__}] Failed to delete datasource with ID {datasource_id}: {e}")
            raise e
