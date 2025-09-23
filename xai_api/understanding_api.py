from enum import Enum
import math
from flask_restx import Resource, Namespace, inputs
from logger import setup_logger
from xai_api.api_models.model_datasource_model import understanding_input
from http import HTTPStatus

from xai_api.schema import UnderstandingItemResponseSchema, UnderstandingCreateRequestSchema, UnderstandingUpdateRequestSchema
from models import db, Understanding as understanding_model

from sqlalchemy import func, or_
import os.path
import psycopg2.errors as driver_errors

ns = Namespace('Entendimento', description='Recursos para página de Entendimento')


list_parser = ns.parser()
list_parser.add_argument('enabled', help="Retorna instâncias habilitadas ou não habilitadas",
                          type=inputs.boolean, location='args')

list_parser.add_argument('name', help="Filtra o retorno de acordo com substring nos campos de ID, name e URI",
                         type=str, location='args')

list_parser.add_argument('datasource_id', help="Filtra o retorno de instâncias de entendimento de acordo com datasource_id", 
                         type=int, location='args')

list_parser.add_argument('model_id', help="Filtra o retorno de instâncias de entendimento de acordo com model_id",
                         type=int, location='args')

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
class UnderstandingList(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "UnderstandingList"

    @ns.expect(list_parser)
    def get(self):
        """
        Retorna listagem de Entendimentos cadastrados
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST

        args = list_parser.parse_args()

        understandings_query = understanding_model.query

        enabled_filter = args["enabled"] # true or false
        name_filter = args["name"] # name or id
        limit = args["limit"]
        page = args["page"]
        sort = args["sort"]
        datasource_id = args["datasource_id"]
        model_id = args["model_id"]
        
        if model_id:
            understandings_query = understandings_query.filter(understanding_model.id_model == model_id)

        if datasource_id:
            understandings_query = understandings_query.filter(understanding_model.id_datasource == datasource_id)

        if enabled_filter is not None:
            understandings_query = understandings_query.filter(understanding_model.enabled == enabled_filter)


        if name_filter:
            if name_filter.isdigit():
                understandings_query = understandings_query.filter(
                    or_(
                        understanding_model.name.ilike(f"%{name_filter}%"),
                        understanding_model.id == int(name_filter)
                    )
                )
            else:
                understandings_query = understandings_query.filter(
                    understanding_model.name.ilike(f"%{name_filter}%")
                )

        understandings_query = understandings_query.order_by(*(getattr(understanding_model,i) for i in sort))
        total_rows = understandings_query.count()

        if limit:
            understandings_query = understandings_query.limit(limit)
        
        if page:
            understandings_query = understandings_query.offset(page*limit)

        logger.debug(f"[{self.__class__.__name__}] Returning {self.human_name}")

        result = {"data":UnderstandingItemResponseSchema(many=True).dump(understandings_query.all()),
                  "totalNumberPages": math.ceil(total_rows/limit),
                  "totalRows": total_rows}

        result_code = HTTPStatus.CREATED
        
        return result, result_code

@ns.route('/')
class Understanding(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "Understanding"

    @ns.expect(understanding_input)
    def post(self): 
        """
        Cria novo Entendimento utilizando IDs de datasource e modelo já cadastrados
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST
        
        request = ns.payload

        if request is not None:
            request_schema = UnderstandingCreateRequestSchema()
            response_schema = UnderstandingItemResponseSchema()
            understanding = request_schema.load(request)

            logger.debug(f"[{self.__class__.__name__}] Adding {self.human_name}")

            try:
                db.session.add(understanding)
                db.session.commit()

                result = response_schema.dump(understanding)
                result_code = HTTPStatus.CREATED

            except Exception as e:

                db.session.rollback()
                logger.error(f"[{self.__class__.__name__}] Um erro ocorreu: {e}")
                return {"error": f"[{self.__class__.__name__}] Um erro ocorreu ao processar a requisição.", "message": str(e)}, 500


        return result, result_code
    
    
@ns.route('/<int:understanding_id>')
class UnderstandingDetail(Resource):
    
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "UnderstandingDetail"

    def get(self, understanding_id):
        """
        Retorna Entendimento cadastrado com id específico
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST

        response_schema = UnderstandingItemResponseSchema()

        try:
            understanding_obj = db.session.execute(db.select(understanding_model).filter_by(id=understanding_id)).scalar_one()
            logger.debug(f"[{self.__class__.__name__}] Returning {self.human_name}")

            result = response_schema.dump(understanding_obj)
            result_code = HTTPStatus.CREATED
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Um erro ocorreu: {e}")
            return {"error": f"[{self.__class__.__name__}] Um erro ocorreu ao processar a requisição.", "message": str(e)}, 500

        return result, result_code
    
    @ns.expect(understanding_input)
    def patch(self, understanding_id): 
        """
        Edita Entendimento já cadastrado com id específico
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST
        
        request = ns.payload

        if request is not None:
            request_schema = UnderstandingUpdateRequestSchema()
            response_schema = UnderstandingItemResponseSchema()
            understanding = request_schema.load(request)            

            understanding_obj = db.session.execute(db.select(understanding_model).filter_by(id=understanding_id)).scalar_one()

            for key, value in vars(understanding).items():
                if hasattr(understanding_obj, key) and key != '_sa_instance_state':
                    setattr(understanding_obj, key, value)

            understanding_obj.updated = func.now()

            logger.debug(f"[{self.__class__.__name__}] Updating {self.human_name}")
            
            db.session.commit()
            result = response_schema.dump(understanding_obj)
            result_code = HTTPStatus.CREATED
            
        return result, result_code