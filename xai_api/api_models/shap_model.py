from flask_restx import fields
from xai_api.main_api import api
from .model_datasource_model import analysis_input

shap_arguments = api.model('shap_features', {
    'shap_type_xai': fields.String(description='Type of SHAP for XAI'),
    'instance': fields.List(fields.Float(description='Instance data')),
    },
    strict=True)

shap_input = api.model('shap_input', {
    'arguments': fields.Nested(shap_arguments, description='Arguments for SHAP algorithm'),
    'metadata': fields.Nested(analysis_input, description='Metadata for analysis'),
    },
    strict=True)
