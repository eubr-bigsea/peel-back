from flask_restx import fields
from xai_api.main_api import api
from .model_datasource_model import analysis_input

logit_arguments = api.model('logit_features', {
    'n_feature': fields.Integer(description='Number of features to be analyzed'),
    },
    strict=True)

logit_input = api.model('logit_input', {
    'arguments': fields.Nested(logit_arguments, description='Arguments for Logit algorithm'),
    'metadata': fields.Nested(analysis_input, description='Metadata for analysis'),
    },
    strict=True)