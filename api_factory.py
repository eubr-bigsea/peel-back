from xai_api.main_api import api
from xai_api import xai_namespaces


def create_api():

    for ns, route in xai_namespaces:
        api.add_namespace(ns, path=route)

    return api
