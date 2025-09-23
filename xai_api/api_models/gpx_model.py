from flask_restx import fields
from xai_api.main_api import api
from .model_datasource_model import analysis_input

gpx_arguments = api.model('gpx_features', {
    'instance': fields.List(fields.Float(description='Instance data')),
    },
    strict=True) 

gpx_input = api.model('gpx_input', {
    'arguments': fields.Nested(gpx_arguments, description='Arguments for GPX algorithm'),
    'metadata': fields.Nested(analysis_input, description='Metadata for analysis'),
    },
    strict=True)
