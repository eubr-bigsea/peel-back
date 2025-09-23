from enum import Enum
from http import HTTPStatus
import json
import math
from flask_restx import Namespace, Resource, inputs
from sqlalchemy import or_
from xai_api.api_models.model_datasource_model import understanding_input
from models import Algorithm, db, InfoArguments as infoarguments_model
from models import Understanding as understanding_model
from models import Model as model_model
from models import Datasource as datasource_model
from models import CeleryTaskmeta as taskmeta_model
from logger import setup_logger
from xai_api.schema import InfoArgumentsItemResponseSchema
from xai_api.celery_config.celery_setup import celery_instance
from sqlalchemy.orm import joinedload
import ast
from flask import send_file
import pickle
import numpy

feature_types_parser = {'float64':numpy.float64,
                        'int64':int,
                        'object':str
                        }

ns = Namespace('Explicação', description='Recursos para Explicações')

list_parser = ns.parser()
list_parser.add_argument('enabled', help="Retorna instâncias habilitadas ou não habilitadas",
                          type=inputs.boolean, location='args')

list_parser.add_argument('name', help="Filtra o retorno de acordo com substring nos campos de ID, name e URI",
                         type=str, location='args')

list_parser.add_argument('limit', help="Limita a quantidade de retorno na lista", 
                         default=10, type=int, location='args')

list_parser.add_argument('page', help="Seleciona página de retorno de acordo com limite de instâncias",
                         default=0, type=int, location='args')

list_parser.add_argument('sort', default=['name','id'], 
                         help="Opções disponíveis: id, name, description, enabled, uri,\
                              created, updated, estimated_rows, estimated_size_mb", 
                         action="append", location="args")

logger = setup_logger()

task_ids = {Algorithm.shap : 'task_manager.shap_tasks.shap_exec',
            Algorithm.tree: 'task_manager.tree_tasks.tree_exec',
            Algorithm.gpx: 'task_manager.gpx_tasks.gp_xai_exec',
            Algorithm.ale: 'task_manager.ale_tasks.ale_exec',
            Algorithm.ensemble: 'task_manager.ensemble_tasks.ensemble_exec',
            Algorithm.logit: 'task_manager.logit_tasks.logit_exec',
            Algorithm.linear: 'task_manager.linear_tasks.linear_exec',
            Algorithm.lime: 'task_manager.lime_tasks.lime_exec'}

@ns.route('/<int:understanding_id>/list')
class ExplanationList(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "ExplanationList"

    @ns.expect(list_parser)
    def get(self, understanding_id): 
        """
        Retorna listagem de Explicações cadastradas num Entendimento
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST
        
        args = list_parser.parse_args()

        explanation_query = infoarguments_model.query.filter(infoarguments_model.understanding_id == understanding_id)

        enabled_filter = args["enabled"] # true or false
        name_filter = args["name"] # name or id
        limit = args["limit"]
        page = args["page"]
        sort = args["sort"]

        if enabled_filter is not None:
            explanation_query = explanation_query.filter(infoarguments_model.enabled == enabled_filter)


        if name_filter:
            if name_filter.isdigit():
                explanation_query = explanation_query.filter(
                    or_(
                        infoarguments_model.name.ilike(f"%{name_filter}%"),
                        infoarguments_model.id == int(name_filter)
                    )
                )
            else:
                explanation_query = explanation_query.filter(
                    infoarguments_model.name.ilike(f"%{name_filter}%")
                )

        explanation_query = explanation_query.order_by(*(getattr(infoarguments_model,i) for i in sort))
        total_rows = explanation_query.count()

        if limit:
            explanation_query = explanation_query.limit(limit)
        
        if page:
            explanation_query = explanation_query.offset(page*limit)

        logger.debug(f"[{self.__class__.__name__}] Returning {self.human_name}")

        result = {"data":InfoArgumentsItemResponseSchema(many=True).dump(explanation_query.all()),
                  "totalNumberPages": math.ceil(total_rows/limit),
                  "totalRows": total_rows}

        result_code = HTTPStatus.OK
        
        return result, result_code
        

@ns.route('/<int:explanation_id>')
class ExplanationDetails(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "ExplanationDetails"

    def get(self, explanation_id): 
        """
        Retorna Explicação cadastrada com ID específico
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST
        
        try:
            explanation_query = infoarguments_model.query.filter(infoarguments_model.id == explanation_id)
            result, result_code = InfoArgumentsItemResponseSchema().dump(explanation_query.one()), 200
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Um erro ocorreu: {e}")
            result, result_code = {
                "error": f"[{self.__class__.__name__}] Um erro ocorreu ao processar a requisição.", 
                "message": str(e)
            }, 500
        
            db.session.rollback()

        return result, result_code

    def delete(self, explanation_id): 
        """
        Exclusão lógica de Explicação cadastrada com ID específico
        """
        result, result_code = {
            "status": "DELETED",
            "message": f"A instância de explicação {explanation_id} foi deletada com sucesso."
        }, 200
        
        try:

            explanation = infoarguments_model.query.filter(infoarguments_model.id == explanation_id).one()
            explanation.enabled = False

            db.session.commit()

        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Um erro ocorreu: {e}")
            result, result_code = {
                "error": f"[{self.__class__.__name__}] Um erro ocorreu ao processar a requisição.", 
                "message": str(e)
            }, 500
        
            db.session.rollback()

        return result, result_code

@ns.route('/<int:explanation_id>/run')
class ExplanationRun(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "ExplanationRun"

    def get(self, explanation_id): 
        """
        Dispara a execução de uma Explicação de ID específico para o backend
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST
        
        
        try:

            explanation_query = (
                infoarguments_model.query
                .filter(infoarguments_model.id == explanation_id)
                .join(understanding_model, infoarguments_model.understanding_id == understanding_model.id)
                .join(datasource_model, understanding_model.id_datasource == datasource_model.id)
                .join(model_model, understanding_model.id_model == model_model.id)
                .options(
                    joinedload(infoarguments_model.understanding)
                    .joinedload(understanding_model.datasource),
                    joinedload(infoarguments_model.understanding)
                    .joinedload(understanding_model.model)
                )
            )
            
            explanation = explanation_query.one()
            features_types = ast.literal_eval(explanation.understanding.datasource.features)
            algorithm_arguments = ast.literal_eval(explanation.arguments)

            if "instance" in algorithm_arguments.keys():
                algorithm_arguments["instance"] = [feature_types_parser[feature_type](feature_val) for feature_type, feature_val in list(zip(list(features_types.values()), algorithm_arguments['instance']))]


            explanation_run_info = {
                "explanation_id": explanation_id,
                "feature_importance": algorithm_arguments,
                "task_type": explanation.understanding.datasource.task_type.value,
                "uri_datasource": explanation.understanding.datasource.uri,
                "uri_model": explanation.understanding.model.uri,
            }

            task = celery_instance.send_task(
                task_ids[explanation.algorithm], 
                kwargs=explanation_run_info
            )
            
            infoarguments_model.query.filter(infoarguments_model.id == explanation_id).update({'celery_task_id': str(task)})
            db.session.commit()
            logger.debug(f"[{self.__class__.__name__}] {explanation.algorithm} task backend sent")
        
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Um erro ocorreu: {e}")
            return {"error": f"[{self.__class__.__name__}] Um erro ocorreu ao processar a requisição.", "message": str(e)}, 500
        # Return a success response
        return {"message": f"[{self.__class__.__name__}] Request processed successfully"}, 200

class ResultType(str, Enum):
    RAW = 'raw'
    IMAGE = 'image'

result_parser = ns.parser()
result_parser.add_argument('type', type=ResultType, help='Tipo de arquivo de retorno do resultado', 
                    choices=list(ResultType), location='args', required=True, default=ResultType.RAW)

@ns.route('/<int:explanation_id>/result')
class ExplanationResult(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "ExplanationResult"

    @ns.expect(result_parser, validate=True)
    def get(self, explanation_id): 
        """
        Exibe o status e resultado (se tarefa estiver pronta) de Explicação de ID específico
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST
        
        
        try:

            explanation_query = infoarguments_model.query.filter(infoarguments_model.id == explanation_id)
            explanation = InfoArgumentsItemResponseSchema().dump(explanation_query.one())

            explanation_task_id = explanation['celery_task_id']

            args = result_parser.parse_args()

            taskmeta_query = taskmeta_model.query.filter(taskmeta_model.task_id == explanation_task_id).one()

            if taskmeta_query.status == "SUCCESS":

                result_type = args['type']

                if result_type == ResultType.RAW:
                    return pickle.loads(taskmeta_query.result)
                elif result_type == ResultType.IMAGE:
                    return send_file(f"storage/output/{explanation_task_id}.png")
            
            elif taskmeta_query.status == "FAILURE":
                return {
                    "status": "FAILURE",
                    "message": "A task foi processada no backend, porém um conflito ocorreu."
                }, 500
            elif taskmeta_query.status == "STARTED":
                return {
                    "status": "PROCESSING",
                    "message": "A task está em processamento."
                }, 202
            else:
                return result, result_code
        except KeyError as e:
            result, result_code = {
                "status": "TASK NOT PROCESSED",
                "message": "A task ainda não foi enviada para processamento pelo usuário."
            }, HTTPStatus.NOT_FOUND
            return result, result_code
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Um erro ocorreu: {e}")
            return {"error": f"[{self.__class__.__name__}] Um erro ocorreu ao processar a requisição.", "message": str(e)}, 500