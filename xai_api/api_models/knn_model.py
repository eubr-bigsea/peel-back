from flask_restx import fields
from xai_api.main_api import api

features_model_knn = api.model('features_knn', {
    'which_feature': fields.String(description='Feature to analyze for importance'),
})

info_model_knn = api.model('info_knn', {
    'feature_importance': fields.Nested(features_model_knn, description='Feature importance details'),
})

knn_model_input = api.model('logit_knn', {
    'model_path': fields.String(description='Model location'),
    'data_path': fields.String(description='Data location'),
    'info_args': fields.Nested(info_model_knn, description='Additional information arguments'),
})
