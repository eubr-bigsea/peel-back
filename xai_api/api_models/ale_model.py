from flask_restx import fields
from xai_api.main_api import api
from .model_datasource_model import analysis_input

ale_arguments = api.model('ale_features', {
    'which_feature': fields.String(description='Feature name to be analyzed'),
    },
    strict=True)

ale_input = api.model('ale_input', {
    'arguments': fields.Nested(ale_arguments, description='Arguments for ALE algorithm'),
    'metadata': fields.Nested(analysis_input, description='Metadata for analysis'),
    },
    strict=True)
