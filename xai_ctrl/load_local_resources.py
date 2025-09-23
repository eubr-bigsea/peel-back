from logger import setup_logger
import pandas as pd
from pathlib import Path

logger = setup_logger()


class XaiLoadLocalResources:

    def __init__(self, data_is_local=False, model_is_local=False):
        self.data_is_local = data_is_local
        self.model_is_local = model_is_local

    def get_model(self, model_name):
        if self.model_is_local:
            model_path = Path('./storage/models') / model_name
            #model_path = Path(model_name)
            if not model_path.is_file():
                logger.error(f'{self.__class__.__name__} tried to load model {model_name}, '
                             f'but this model doesn\'t exist!! {model_path}')
                raise ValueError(f'{self.__class__.__name__} tried to load model {model_name}, '
                                 f'but this model doesn\'t exist!!')
            return model_path.read_bytes()

        else:
            error_msg = f'{self.__class__.__name__} tried to load model {model_name}, ' \
                        f'but get_model is not implemented for non-local models!!'
            logger.error(error_msg)
            raise NotImplementedError(error_msg)


    def get_data(self, data_name):
        if self.data_is_local:
            if data_name.endswith(".csv"):
                data_path = Path('./storage/data') / data_name
                if not data_path.is_file():
                    logger.error(f'{self.__class__.__name__} doesn\'t know how to load {data_name}')
                    raise FileNotFoundError(f'{self.__class__.__name__} doesn\'t know how to load {data_name}')
                return pd.read_csv(data_path, index_col=False)
        else:
            logger.error(f'{self.__class__.__name__} doesn\'t know how to load {data_name}')
            raise NotImplementedError(f'{self.__class__.__name__} doesn\'t know how to load {data_name}')
