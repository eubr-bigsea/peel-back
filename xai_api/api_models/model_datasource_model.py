from enum import Enum
from flask_restx import fields
from xai_api.main_api import api


model = api.model('model', {
    'id': fields.Integer(description='Model ID'),
    'name': fields.String(description='Name of the model'),
    'description': fields.String(description='Description of the model'),
    'enabled': fields.Boolean(description='Whether the model is enabled or not'),
    'uri': fields.String(description='Path of the model'),
    'model_type': fields.String(description='Type of the model'),
    'version': fields.String(description='Version of the model'),
    'class_name': fields.String(description='Class name of the model'),
    'digest': fields.String(description='Digest of the model'),
    #'created': fields.DateTime(description='Creation timestamp of the model', dt_format='iso8601'),
})

datasource = api.model('datasource', {
    'id': fields.Integer(description='Datasource ID'),
    'name': fields.String(description='Name of the datasource', required=True),
    'description': fields.String(description='Description of the datasource', required=True),
    'enabled': fields.Boolean(description='Whether the datasource is enabled or not'),
    'uri': fields.String(description='URL of the datasource', required=True),
    'data_format': fields.String(description='Format of the datasource data'),
    'estimated_rows': fields.Integer(description='Estimated number of rows in the datasource'),
    'estimated_size_mb': fields.Integer(description='Estimated size of the datasource in MB'),
    'attributed_delimiter': fields.String(description='Attributed delimiter of the datasource'),
    'record_delimiter': fields.String(description='Record delimiter of the datasource'),
    'encoding': fields.String(description='Encoding of the datasource data'),
    #'created': fields.DateTime(description='Creation timestamp of the datasource', dt_format='iso8601'),
    #'updated': fields.DateTime(description='Last updated timestamp of the datasource', dt_format='iso8601'),
    #'is_first_line_header': fields.Boolean(description='Whether the first line is a header'),
    #'read_only': fields.Boolean(description='Whether the datasource is read-only or not'),
    #'provenience': fields.String(description='Provenience of the datasource data'),
    #'text_delimiter': fields.String(description='Text delimiter of the datasource'),
    #'is_public': fields.Boolean(description='Whether the datasource is public or not'),
    #'treat_as_missing': fields.Boolean(description='Whether to treat certain values as missing'),
    #'is_multiline': fields.Boolean(description='Whether the datasource data is multiline'),
    #'command': fields.String(description='Command associated with the datasource'),
    #'is_lookup': fields.Boolean(description='Whether the datasource is a lookup'),
 })

model_datasource = api.model('model_datasource', {
    'model': fields.Nested(model, description='Model details'),
    'datasource': fields.Nested(datasource, description='Datasource details'),
})

datasource_input = api.model('datasource_input', {
    'id': fields.Integer(description='Datasource ID', required=True),
    'name': fields.String(description='Name of the datasource'),
    'description': fields.String(description='Description of the datasource'),
    'enabled': fields.Boolean(description='Whether the datasource is enabled or not'),
    'uri': fields.String(description='URL of the datasource'),
    'target': fields.String(description='Target column to consider as the target feature. Default is the last column.'),
    'task_type': fields.String(description='Type of prediction task, "classification" or "regression".'),
    'data_format': fields.String(description='Format of the datasource data')
 })

datasource_output = api.model('datasource_output', {
    'id': fields.Integer(description='Datasource ID'),
    'name': fields.String(description='Name of the datasource', required=True),
    'description': fields.String(description='Description of the datasource', required=True),
    'enabled': fields.Boolean(description='Whether the datasource is enabled or not'),
    'uri': fields.String(description='URL of the datasource', required=True),
    'features': fields.String(description='Feature fields on data'),
    'target': fields.String(description='Target column to consider as the target feature. Default is the last column.'),
    'task_type': fields.String(description='Type of prediction task, "classification" or "regression".'),
    'data_format': fields.String(description='Format of the datasource data'),
    'estimated_rows': fields.Integer(description='Estimated number of rows in the datasource'),
    'estimated_size_mb': fields.Integer(description='Estimated size of the datasource in MB'),
    'created': fields.DateTime(description='Creation timestamp of the datasource', dt_format='iso8601'),
    'updated': fields.DateTime(description='Last updated timestamp of the datasource', dt_format='iso8601')
 })

model_input = api.model('model', {
    'id': fields.Integer(description='Model ID'),
    'name': fields.String(description='Name of the model'),
    'description': fields.String(description='Description of the model'),
    'enabled': fields.Boolean(description='Whether the model is enabled or not'),
    'uri': fields.String(description='Path of the model')
    #'created': fields.DateTime(description='Creation timestamp of the model', dt_format='iso8601'),
})

understanding_input = api.model('understanding_input', {
    #'id': fields.Integer(description='Understanding ID'),
    'id_datasource': fields.Integer(description='Datasource ID'),
    'id_model': fields.Integer(description='Model ID'),
    'name': fields.String(description='Name'),
    'description': fields.String(description='Description'),
    'enabled': fields.Boolean(description='Whether the instance is enabled or not')
})

info_arguments_input = api.model('info_arguments_input', {
    'understanding_id': fields.Integer(description='Understanding ID'),
    'name': fields.String(description='Name'),
    'description': fields.String(description='Description'),
    'enabled': fields.Boolean(description='Whether the instance is enabled or not'),
    'algorithm': fields.String(description='Algorithm used for XAI'),
    'arguments': fields.String(description='JSON arguments used'),
    'result': fields.String(description='Result of the XAI'),
    'result_type': fields.String(description='Type of result, eg. uri, json.'),
})

analysis_input = api.model('analysis_input', {
    'name': fields.String(description='Name'),
    'description': fields.String(description='Description'),
    'enabled': fields.Boolean(description='Whether the instance is enabled or not')
    },
    strict=True)