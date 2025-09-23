from http import HTTPStatus
from flask_restx import Namespace, Resource, inputs
from logger import setup_logger
from xai_api.api_models.lime_model import lime_input
from xai_api.api_models.knn_model import features_model_knn as knn_input
from xai_api.api_models.tree_model import tree_input
from xai_api.api_models.gpx_model import gpx_input
from xai_api.api_models.ale_model import ale_input
from xai_api.api_models.ensemble_model import ensemble_input
from xai_api.api_models.logit_model import logit_input
from xai_api.api_models.linear_model import linear_input

from xai_api.api_models.shap_model import shap_input

from xai_api.celery_config.celery_setup import celery_instance
from models import db
from xai_api.schema import InfoArgumentsCreateRequestSchema, InfoArgumentsItemResponseSchema
import json
from psycopg2.errors import ForeignKeyViolation
from sqlalchemy.exc import IntegrityError

ns = Namespace('Algoritmos', description='Crie instâncias de explicações com algoritmos de explicabilidade')

logger = setup_logger()

def _structure_request(request:dict, understanding_id: int, algorithm:str):
    structured_request = {'arguments': str(request['arguments']),
            **request['metadata']
    }
    structured_request['understanding_id'] = understanding_id
    structured_request['algorithm'] = algorithm.lower()
    return structured_request

def _generic_algorithm_post(payload:dict, understanding_id: int, algorithm:str):

    result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST
        
    request = payload
    request = _structure_request(request=request, 
                                    understanding_id=understanding_id,
                                    algorithm=algorithm)

    if request is not None:
        request_schema = InfoArgumentsCreateRequestSchema()
        response_schema = InfoArgumentsItemResponseSchema()
        info_arguments = request_schema.load(request)

        logger.debug(f"[{algorithm}] Adding {algorithm}")

        try:
            db.session.add(info_arguments)
            db.session.commit()

            result = response_schema.dump(info_arguments)
            result_code = HTTPStatus.CREATED

        except IntegrityError as e:
            if isinstance(e.orig, ForeignKeyViolation):
                logger.error(f"[{algorithm}] Chave estrangeira (understanding_id) nao existente: {e}")
                result, result_code = {
                    "error": f"[{algorithm}] Erro de chave estrangeira inexistente.",
                    "message": f"A instância de entendimento (understanding_id = {understanding_id}) nao existe no banco."
                }, 500
            else:
                # Trata outros IntegrityError
                logger.error(f"[{algorithm}] Erro de integridade: {e}")
                result, result_code = {
                    "error": f"[{algorithm}] Erro de integridade.",
                    "message": str(e)
                }, 500
            
            db.session.rollback()
        except Exception as e:
            logger.error(f"[{algorithm}] Um erro ocorreu: {e}")
            result, result_code = {
                "error": f"[{algorithm}] Um erro ocorreu ao processar a requisição.", 
                "message": str(e)
            }, 500
        
            db.session.rollback()
            
    return result, result_code

@ns.route('/<int:understanding_id>/algorithm/shap')
class SHAP(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "SHAP"

    @ns.expect(shap_input, validate=True)
    def post(self, understanding_id): 
        """
        ================ FEITO ===================== (IMAGE,RAW)
        """
        result, result_code = _generic_algorithm_post(payload=ns.payload, 
                                                      understanding_id=understanding_id,
                                                      algorithm=self.human_name)
        return result, result_code
    

@ns.route('/<int:understanding_id>/algorithm/tree')
class Tree(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "Tree"

    @ns.expect(tree_input, validate=True)
    def post(self, understanding_id): 
        """
        ================ FEITO ===================== (RAW)
        """
        result, result_code = _generic_algorithm_post(payload=ns.payload, 
                                                      understanding_id=understanding_id,
                                                      algorithm=self.human_name)
        return result, result_code

@ns.route('/<int:understanding_id>/algorithm/gpx')
class GPX(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "GPX"

    @ns.expect(gpx_input, validate=True)
    def post(self, understanding_id): 
        """
        ================ FEITO ===================== (RAW) todo: lidar com 2 imagens
        """
        result, result_code = _generic_algorithm_post(payload=ns.payload, 
                                                      understanding_id=understanding_id,
                                                      algorithm=self.human_name)
        return result, result_code

@ns.route('/<int:understanding_id>/algorithm/ale')
class ALE(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "ALE"

    @ns.expect(ale_input, validate=True)
    def post(self, understanding_id): 
        """
        ================ FEITO ===================== (IMAGE)
        """
        result, result_code = _generic_algorithm_post(payload=ns.payload, 
                                                      understanding_id=understanding_id,
                                                      algorithm=self.human_name)
        return result, result_code

@ns.route('/<int:understanding_id>/algorithm/ensemble')
class Ensemble(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "Ensemble"

    @ns.expect(ensemble_input, validate=True)
    def post(self, understanding_id): 
        """
        ================ FEITO ===================== (RAW)
        """
        result, result_code = _generic_algorithm_post(payload=ns.payload, 
                                                      understanding_id=understanding_id,
                                                      algorithm=self.human_name)
        return result, result_code

@ns.route('/<int:understanding_id>/algorithm/logit')
class Logit(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "Logit"

    @ns.expect(logit_input, validate=True)
    def post(self, understanding_id): 
        """
        ================ FEITO ===================== (RAW)
        """
        result, result_code = _generic_algorithm_post(payload=ns.payload, 
                                                      understanding_id=understanding_id,
                                                      algorithm=self.human_name)
        return result, result_code


@ns.route('/<int:understanding_id>/algorithm/linear')
class Linear(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "Linear"

    @ns.expect(linear_input, validate=True)
    def post(self, understanding_id): 
        """
        ================ FEITO ===================== (RAW)
        """
        result, result_code = _generic_algorithm_post(payload=ns.payload, 
                                                      understanding_id=understanding_id,
                                                      algorithm=self.human_name)
        return result, result_code

@ns.route('/<int:understanding_id>/algorithm/lime')
class LIME(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "LIME"

    @ns.expect(lime_input)
    def post(self, understanding_id): 
        """
        # ================ FEITO ===================== (RAW)
        """
        result, result_code = _generic_algorithm_post(payload=ns.payload, 
                                                      understanding_id=understanding_id,
                                                      algorithm=self.human_name)
        return result, result_code
 
@ns.route('/<int:understanding_id>/algorithm/knn')
class KNN(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "KNN"

    @ns.expect(knn_input)
    def post(self, understanding_id): 
        """
        # aparentemente sem implementação
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST
        
        request = ns.payload
        
        return result, result_code