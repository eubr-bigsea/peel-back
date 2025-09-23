from flask_restx import fields
from xai_api.main_api import api
from .model_datasource_model import analysis_input

linear_arguments = api.model('linear_features', {
    'n_feature': fields.Integer(description='Number of features to be analyzed'),
    },
    strict=True)

linear_input = api.model('linear_input', {
    'arguments': fields.Nested(linear_arguments, description='Arguments for Linear algorithm'),
    'metadata': fields.Nested(analysis_input, description='Metadata for analysis'),
    },
    strict=True)
