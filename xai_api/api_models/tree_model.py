from flask_restx import fields
from xai_api.main_api import api
from .model_datasource_model import analysis_input

tree_arguments = api.model('tree_features', {
    'max_depth': fields.Integer(description="Number of features"),
    },
    strict=True
)

tree_input = api.model('tree_input', {
    'arguments': fields.Nested(tree_arguments, description='Arguments for Decision Tree algorithm'),
    'metadata': fields.Nested(analysis_input, description='Metadata for analysis'),
    },
    strict=True
)