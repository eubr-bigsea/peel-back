import hashlib

from DAO.model_dao import ModelDAO
from DAO.datasource_dao import DataSourceDAO
from logger import setup_logger

logging = setup_logger()
class CtrXAI:

    def __init__(self, type_off_xai):

        self.type_off_xai = type_off_xai


    @staticmethod
    def deal_post_model_datasource(**payload):
        try:
            model_data = payload.get("model")
            datasource_data = payload.get("datasource")

            if model_data:
                CtrXAI.create_model(model_data)
            else:
                logging.warning("[CtrXAI] No model data provided.")

            if datasource_data:
                CtrXAI.create_datasource(datasource_data)
            else:
                logging.warning("[CtrXAI] No datasource data provided.")

        except Exception as e:
            logging.error(f"[CtrXAI] An error occurred: {e}")

    @staticmethod
    def create_model(model_data):
        try:
            ModelDAO.create_model(**model_data)
            logging.info("[CtrXAI] Model created successfully.")
        except Exception as e:
            logging.error(f"[CtrXAI] Error creating model: {e}")

    @staticmethod
    def create_datasource(datasource_data):
        try:
            DataSourceDAO.create_datasource(**datasource_data)
            logging.info("[CtrXAI] Datasource created successfully.")
        except Exception as e:
            logging.error(f"[CtrXAI] Error creating datasource: {e}")


class DigestXAI:

    def __init__(self, file_path):
        self.file_path = file_path

    def create_digest(self):
        with open(self.file_path, 'rb') as f:
            binary_data = f.read()
        return hashlib.sha256(binary_data).hexdigest()

    def verify_model(self, original_digest):

        new_digest = self.create_digest()

        return new_digest == original_digest
