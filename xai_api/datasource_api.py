from flask_restx import Resource, Namespace, inputs
from logger import setup_logger
from xai_api.api_models.model_datasource_model import datasource_input
from http import HTTPStatus

from xai_api.schema import DataSourceItemResponseSchema, DatasourceCreateRequestSchema, DatasourceUpdateRequestSchema
from models import db, Datasource as datasource_model

from sqlalchemy import func, or_
import os.path
import csv
import math
import pandas as pd
import numpy as np


ns = Namespace('Fontes de Dados', description='Configurações de dados')

parser = ns.parser()
parser.add_argument('id', help="ID da instância",type=int, location='args')

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
class DatasourceList(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "DatasourceList"

    @ns.expect(list_parser)
    def get(self):
        """
        Retorna listagem de datasources cadastrados
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST

        args = list_parser.parse_args()

        datasources_query = datasource_model.query

        enabled_filter = args["enabled"] # true or false
        name_filter = args["name"] # name or id
        limit = args["limit"]
        page = args["page"]
        sort = args["sort"]
        
        if enabled_filter is not None:
            datasources_query = datasources_query.filter(datasource_model.enabled == enabled_filter)


        if name_filter:
            if name_filter.isdigit():
                datasources_query = datasources_query.filter(
                    or_(
                        datasource_model.name.ilike(f"%{name_filter}%"),
                        datasource_model.uri.ilike(f"%{name_filter}%"),
                        datasource_model.id == int(name_filter)
                    )
                )
            else:
                datasources_query = datasources_query.filter(
                    or_(
                        datasource_model.name.ilike(f"%{name_filter}%"),
                        datasource_model.uri.ilike(f"%{name_filter}%")
                    )
                )

        datasources_query = datasources_query.order_by(*(getattr(datasource_model,i) for i in sort))
        total_rows = datasources_query.count()
        if limit:
            datasources_query = datasources_query.limit(limit)
        
        if page:
            datasources_query = datasources_query.offset(page*limit)

        logger.debug(f"[{self.__class__.__name__}] Returning {self.human_name}")

        result = {"data":DataSourceItemResponseSchema(many=True).dump(datasources_query.all()),
                  "totalNumberPages": math.ceil(total_rows/limit),
                  "totalRows": total_rows}
        result_code = HTTPStatus.CREATED
        
        return result, result_code

@ns.route('/')
class Datasource(Resource):

    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self.human_name = "Datasource"

    @ns.expect(parser, validate=True)
    def get(self):
        """
        Retorna datasource cadastrado com id específico
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST

        args = parser.parse_args()
        datasource_id = args['id']
        response_schema = DataSourceItemResponseSchema()

        try:
            datasource_obj = db.session.execute(db.select(datasource_model).filter_by(id=datasource_id)).scalar_one()
            logger.debug(f"[{self.__class__.__name__}] Returning {self.human_name}")

            result = response_schema.dump(datasource_obj)
            result_code = HTTPStatus.CREATED
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Um erro ocorreu: {e}")
            return {"error": f"[{self.__class__.__name__}] Um erro ocorreu ao processar a requisição.", "message": str(e)}, 500

        return result, result_code

    @ns.expect(datasource_input)
    def post(self): 
        """
        Cria novo datasource apontando para uma URI de arquivo já no sistema
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST
        
        request = ns.payload

        if request is not None:
            request_schema = DatasourceCreateRequestSchema()
            response_schema = DataSourceItemResponseSchema()
            datasource = request_schema.load(request)
            
            if not os.path.isfile(datasource.uri):
                result['message'] = "URI passed doesn't correspond to a file in the system."
                return result, result_code

            datasource.data_format = datasource.uri.split('.')[-1]
            datasource.estimated_size_mb = os.path.getsize(datasource.uri)/1024

            myfile = pd.read_csv(datasource.uri)
            datasource.estimated_rows = myfile.shape[0]

            # converte todos os tipos para string
            dtypes_dict = {col: str(dtype) for col, dtype in myfile.dtypes.to_dict().items()}

            # seta o target certo
            if datasource.target and datasource.target in dtypes_dict.keys():
                datasource.target = {datasource.target: dtypes_dict[datasource.target]}
            else:
                datasource.target = dict([list(dtypes_dict.items())[-1]])

            if datasource.task_type is None:
                datasource.task_type = "classification" if list(datasource.target.values())[0] == "object" else "regression"

            datasource.features = str({col: dtype for col, dtype in dtypes_dict.items() if col not in datasource.target})
            datasource.target = str(datasource.target)

            logger.debug(f"[{self.__class__.__name__}] Adding {self.human_name}")

            db.session.add(datasource)
            db.session.commit()

            result = response_schema.dump(datasource)
            result_code = HTTPStatus.CREATED
            
        return result, result_code
    
    @ns.expect(datasource_input)
    def patch(self): 
        """
        Edita datasource já cadastrado com id específico
        """
        result, result_code = {
            "status": "ERROR",
            "message": "Missing json in the request body"
        }, HTTPStatus.BAD_REQUEST
        
        request = ns.payload

        if request is not None:
            request_schema = DatasourceUpdateRequestSchema()
            response_schema = DataSourceItemResponseSchema()
            datasource = request_schema.load(request)

            if datasource.id is None:
                result['message'] = "The ID field is mandatory."
                return result, result_code

            datasource_obj = db.session.execute(db.select(datasource_model).filter_by(id=datasource.id)).scalar_one()

            for key, value in vars(datasource).items():
                if hasattr(datasource_obj, key) and key != '_sa_instance_state':
                    setattr(datasource_obj, key, value)

            datasource_obj.updated = func.now()

            logger.debug(f"[{self.__class__.__name__}] Updating {self.human_name}")
            
            db.session.commit()
            result = response_schema.dump(datasource_obj)
            result_code = HTTPStatus.CREATED
            
        return result, result_code