

import json
from marshmallow import Schema, post_dump, post_load, fields, EXCLUDE, pre_dump
from models import Algorithm, Datasource, InfoArguments, Model, Understanding, TaskType
from xai_api.main_api import api
from xai_api.util import changeTimezone

def load_json(str_value):
    try:
        return json.loads(str_value)
    except BaseException:
        return None

class BaseSchema(Schema):
    @pre_dump
    def handle_timezone(self, data, **kwargs):
        changeTimezone(data) # all BaseSchema to be dumped have created/updated attributes
        return data

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None  # Empty lists must be kept!
        }
    
class DatasourceCreateRequestSchema(BaseSchema):
    """ JSON serialization schema """
    #id = fields.Integer(allow_none=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    enabled = fields.Boolean()
    uri = fields.String(required=True)
    target = fields.String()
    task_type = fields.Enum(enum=TaskType)
    data_format = fields.String()
    estimated_rows = fields.Integer()
    estimated_size_mb = fields.Integer()

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Cluster"""
        return Datasource(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE

class DatasourceUpdateRequestSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    name = fields.String()
    description = fields.String()
    enabled = fields.Boolean()
    uri = fields.String()
    task_type = fields.Enum(enum=TaskType)
    data_format = fields.String()
    estimated_rows = fields.Integer()
    estimated_size_mb = fields.Integer()

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        print("bbbb")
        """ Deserialize data into an instance of Cluster"""
        return Datasource(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE

class DataSourceItemResponseSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer()
    name = fields.String()
    description = fields.String()
    enabled = fields.Boolean()
    uri = fields.String()
    features = fields.String()
    target = fields.String()
    task_type = fields.Enum(enum=TaskType)
    data_format = fields.String()
    estimated_rows = fields.Integer()
    estimated_size_mb = fields.Integer()
    
    created = fields.DateTime()
    updated = fields.DateTime()

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Cluster"""
        return Datasource(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE

# ===========  MODELS ==================

class ModelItemResponseSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer()
    name = fields.String()
    description = fields.String()
    enabled = fields.Boolean()
    uri = fields.String()
    
    created = fields.DateTime()
    updated = fields.DateTime()

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Cluster"""
        return Model(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE

class ModelCreateRequestSchema(BaseSchema):
    """ JSON serialization schema """
    name = fields.String(required=True)
    description = fields.String(required=True)
    enabled = fields.Boolean()
    uri = fields.String(required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Cluster"""
        return Model(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE


class ModelUpdateRequestSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    name = fields.String()
    description = fields.String()
    enabled = fields.Boolean()
    uri = fields.String()

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Cluster"""
        return Model(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE

# ===========  Understanding ==================

class UnderstandingItemResponseSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer()
    #id_datasource = fields.Integer()
    #id_model = fields.Integer()
    name = fields.String()
    description = fields.String()
    enabled = fields.Boolean()
    
    datasource = fields.Nested(
        'xai_api.schema.DataSourceItemResponseSchema',
        required=True)
    
    model = fields.Nested(
        'xai_api.schema.ModelItemResponseSchema',
        required=True)


    created = fields.DateTime()
    updated = fields.DateTime()

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Cluster"""
        return Understanding(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE

class UnderstandingCreateRequestSchema(BaseSchema):
    """ JSON serialization schema """
    id_datasource = fields.Integer(required=True)
    id_model = fields.Integer(required=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    enabled = fields.Boolean(required=True)
    
    created = fields.DateTime()
    updated = fields.DateTime()

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Cluster"""
        return Understanding(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE


class UnderstandingUpdateRequestSchema(BaseSchema):
    """ JSON serialization schema """
    #id = fields.Integer(required=True)
    id_datasource = fields.Integer()
    id_model = fields.Integer()
    name = fields.String()
    description = fields.String()
    enabled = fields.Boolean()
    
    created = fields.DateTime()
    updated = fields.DateTime()

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Cluster"""
        return Understanding(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE


# ===========  InfoArguments ==================

class InfoArgumentsItemResponseSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer()
    understanding_id = fields.Integer()
    name = fields.String()
    description = fields.String()
    enabled = fields.Boolean()
    
    algorithm = fields.Enum(enum=Algorithm)
    arguments = fields.String()
    result = fields.String()
    result_type = fields.String()
    celery_task_id = fields.String()
    
    version = fields.String()

    created = fields.DateTime()
    updated = fields.DateTime()

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Cluster"""
        return InfoArguments(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE


class InfoArgumentsCreateRequestSchema(BaseSchema):
    """ JSON serialization schema """
    understanding_id = fields.Integer(required=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    enabled = fields.Boolean(required=True)
    
    algorithm = fields.Enum(enum=Algorithm)
    arguments = fields.String()

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Cluster"""
        return InfoArguments(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE
