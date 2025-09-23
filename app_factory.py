from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from models import db
from api_factory import create_api
from db_config import AmbientConfig


def create_app(config_class=AmbientConfig):
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(config_class)

    Migrate(app, db)

    api = create_api()
    api.init_app(app)
    db.init_app(app)

    return app
