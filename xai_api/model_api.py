import math
from flask_restx import Resource, Namespace, inputs
from logger import setup_logger
from xai_api.api_models.model_datasource_model import model_input
from http import HTTPStatus

from xai_api.schema import ModelItemResponseSchema, ModelCreateRequestSchema, ModelUpdateRequestSchema
from models import db, Model as model_model

from sqlalchemy import func, or_
import os.path

ns = Namespace('Modelos', description='Configurações de Modelos de IA')

parser = ns.parser()
parser.add_argument('id', type=int, location='args')

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

@ns.route('/list')
class ModelList(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "ModelList"
        
    @ns.expect(list_parser)
    def get(self):
        """
        Retorna listagem de models cadastrados
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST

        args = list_parser.parse_args()

        models_query = model_model.query

        enabled_filter = args["enabled"] # true or false
        name_filter = args["name"] # name or id
        limit = args["limit"]
        page = args["page"]
        sort = args["sort"]
        
        
        if enabled_filter is not None:
            models_query = models_query.filter(model_model.enabled == enabled_filter)


        if name_filter:
            if name_filter.isdigit():
                models_query = models_query.filter(
                    or_(
                        model_model.name.ilike(f"%{name_filter}%"),
                        model_model.uri.ilike(f"%{name_filter}%"),
                        model_model.id == int(name_filter)
                    )
                )
            else:
                models_query = models_query.filter(
                    or_(
                        model_model.name.ilike(f"%{name_filter}%"),
                        model_model.uri.ilike(f"%{name_filter}%")
                    )
                )

        models_query = models_query.order_by(*(getattr(model_model,i) for i in sort))
        total_rows = models_query.count()

        if limit:
            models_query = models_query.limit(limit)

        if page:
            models_query = models_query.offset(page*limit)

        logger.debug(f"[{self.__class__.__name__}] Returning {self.human_name}")

        result = {"data":ModelItemResponseSchema(many=True).dump(models_query.all()),
                  "totalNumberPages": math.ceil(total_rows/limit),
                  "totalRows": total_rows}
        
        result_code = HTTPStatus.CREATED
        
        return result, result_code

@ns.route('/')
class Model(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "Model"

    @ns.expect(parser, validate=True)
    def get(self):
        """
        Retorna model cadastrado com id específico
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST

        args = parser.parse_args()
        model_id = args['id']
        response_schema = ModelItemResponseSchema()

        try:
            model_obj = db.session.execute(db.select(model_model).filter_by(id=model_id)).scalar_one()
            logger.debug(f"[{self.__class__.__name__}] Returning {self.human_name}")

            result = response_schema.dump(model_obj)
            result_code = HTTPStatus.CREATED
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Um erro ocorreu: {e}")
            return {"error": f"[{self.__class__.__name__}] Um erro ocorreu ao processar a requisição.", "message": str(e)}, 500

        return result, result_code

    @ns.expect(model_input)
    def post(self): 
        """
        Cria novo model apontando para uma URI de arquivo já no sistema
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST
        
        request = ns.payload

        if request is not None:
            request_schema = ModelCreateRequestSchema()
            response_schema = ModelItemResponseSchema()
            model = request_schema.load(request)
            
            if not os.path.isfile(model.uri):
                result['message'] = "URI passed doesn't correspond to a file in the system."
                return result, result_code

            logger.debug(f"[{self.__class__.__name__}] Adding {self.human_name}")

            db.session.add(model)
            db.session.commit()

            result = response_schema.dump(model)
            result_code = HTTPStatus.CREATED
            
        return result, result_code
    
    @ns.expect(model_input)
    def patch(self): 
        """
        Edita model já cadastrado com id específico
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST
        
        request = ns.payload

        if request is not None:
            request_schema = ModelUpdateRequestSchema()
            response_schema = ModelItemResponseSchema()
            model = request_schema.load(request)

            if model.id is None:
                result['message'] = "The ID field is mandatory."
                return result, result_code
            

            model_obj = db.session.execute(db.select(model_model).filter_by(id=model.id)).scalar_one()

            for key, value in vars(model).items():
                if hasattr(model_obj, key) and key != '_sa_instance_state':
                    setattr(model_obj, key, value)

            model_obj.updated = func.now()

            logger.debug(f"[{self.__class__.__name__}] Updating {self.human_name}")
            
            db.session.commit()
            result = response_schema.dump(model_obj)
            result_code = HTTPStatus.CREATED
            
        return result, result_code