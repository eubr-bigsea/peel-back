from xai_api.algorithms import ns as algorithms_ns
from xai_api.datasource_api import ns as datasource_ns
from xai_api.uploader_api import ns as uploader_ns
from xai_api.model_api import ns as model_ns
from xai_api.understanding_api import ns as understanding_ns
from xai_api.explanation import ns as explanation_ns
from .celery_config.celery_setup import celery_instance

xai_namespaces = [
    (algorithms_ns, "/xai/algorithms"),
    (datasource_ns, "/xai/datasource"),
    (uploader_ns, "/xai/upload"),
    (model_ns, "/xai/model"),
    (understanding_ns, "/xai/understanding"),
    (explanation_ns, "/xai/explanation"),
]

__all__ = [
    'algorithms_ns', 'datasource_ns', 'model_ns', 'uploader_ns',
    'understanding_ns', 'xai_namespaces', 'celery_instance', 'explanation_ns'
]


