from flask_restx import fields
from xai_api.main_api import api
from .model_datasource_model import analysis_input

lime_arguments = api.model('lime_features', {
    'instance': fields.List(fields.Float(description='Instance data')),
    'n_feature': fields.Integer(description='Number of features to be analyzed'),
    },
    strict=True)

lime_input = api.model('lime_input', {
    'arguments': fields.Nested(lime_arguments, description='Arguments for LIME algorithm'),
    'metadata': fields.Nested(analysis_input, description='Metadata for analysis'),
    },
    strict=True)
