
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENVIRONMENT = 'development'
    SQLALCHEMY_MIGRATE_REPO = 'migrations'

class AmbientConfig(Config):
    DB_HOST=os.getenv('DB_HOST')
    DB_PORT=os.getenv('DB_PORT')
    DB_USERNAME=os.getenv('DB_USERNAME')
    DB_PASSWORD=os.getenv('DB_PASSWORD')
    DB_NAME=os.getenv('DB_NAME')
    
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"