import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Enum, Integer, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class TaskType(enum.Enum):
    classification = "classification"
    regression = "regression"

class Datasource(db.Model):
    """ Datasource persisted informations """
    __tablename__ = 'datasource'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, index=True)
    description = Column(String(512), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    uri = Column(String(512), nullable=False)
    features = Column(String(1024), nullable=False)
    target = Column(String(128), nullable=False)
    task_type = Column(Enum(TaskType), nullable=False)
    data_format = Column(String(128))
    estimated_rows = Column(Integer)
    estimated_size_mb = Column(Integer)
    created = Column(DateTime, default=func.now(), nullable=False)
    updated = Column(DateTime, default=func.now(), nullable=False, onupdate=func.now())

class Model(db.Model):
    """ Model persisted informations """
    __tablename__ = 'model'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(String(512), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    uri = Column(String(512), nullable=False)
    created = Column(DateTime, default=func.now(), nullable=False)
    updated = Column(DateTime, default=func.now(), nullable=False, onupdate=func.now())

class Understanding(db.Model):
    __tablename__ = 'understanding'

    id = Column(Integer, primary_key=True)
    id_datasource = Column(Integer, ForeignKey('datasource.id'))
    id_model = Column(Integer, ForeignKey('model.id'))
    name = Column(String(128), nullable=False)
    description = Column(String(512), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)

    datasource = relationship('Datasource', foreign_keys=[id_datasource])
    model = relationship('Model', foreign_keys=[id_model])

    created = Column(DateTime, default=func.now(), nullable=False)
    updated = Column(DateTime, default=func.now(), nullable=False, onupdate=func.now())

class Algorithm(enum.Enum):
    ale = "ale"
    ensemble = "ensemble"
    gpx = "gpx"
    knn = "knn"
    lime = "lime"
    linear = "linear"
    logit = "logit"
    shap = "shap"
    tree = "tree"

class InfoArguments(db.Model):
    __tablename__ = 'info_arguments'

    id = Column(Integer, primary_key=True)
    understanding_id = Column(Integer, ForeignKey('understanding.id'))
    name = Column(String(128), nullable=False)
    description = Column(String(512), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    algorithm = Column(Enum(Algorithm))
    arguments = Column(JSON)
    result = Column(String(512))
    result_type = Column(String(64))
    celery_task_id = Column(String(155))
    version = Column(String(128))
    
    created = Column(DateTime, default=func.now(), nullable=False)
    updated = Column(DateTime, default=func.now(), nullable=False, onupdate=func.now())

    # Associations

    understanding = relationship('Understanding', foreign_keys=[understanding_id])

class CeleryTaskmeta(db.Model):
    __tablename__ = 'celery_taskmeta'

    id = Column(Integer, primary_key=True)
    task_id = Column(String())
    status = Column(String())
    result = Column(String())
    date_done = Column(DateTime)
    traceback = Column(String())
    name = Column(String())
    args = Column(String())
    kwargs = Column(String())
    worker = Column(String())
    retries = Column(Integer)
    queue = Column(String())