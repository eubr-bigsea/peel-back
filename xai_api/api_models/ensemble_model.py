from flask_restx import fields
from xai_api.main_api import api
from .model_datasource_model import analysis_input

ensemble_arguments = api.model('ensemble_features', {
    'n_feature': fields.Integer(description='Number of features to be analyzed'),
    },
    strict=True)

ensemble_input = api.model('ensemble_input', {
    'arguments': fields.Nested(ensemble_arguments, description='Arguments for Ensemble algorithm'),
    'metadata': fields.Nested(analysis_input, description='Metadata for analysis'),
    },
    strict=True)

