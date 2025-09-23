from celery import Celery
import os
from dotenv import load_dotenv
from db_config import AmbientConfig

load_dotenv()

def make_celery(app_name):

    topic_name = os.getenv('BROKER_TOPIC')

    broker_links = os.getenv('BROKER_LINKS')
    broker_links = broker_links.split(';')
    broker_list = [f"kafka://{address}" for address in broker_links]
    broker_links = ";".join(broker_list)

    celery_app = Celery(app_name,
                        broker=broker_links,
                        backend='db+'+AmbientConfig.SQLALCHEMY_DATABASE_URI,
                        broker_transport_options={
                            'topic': topic_name,
                            'queue_name_prefix': topic_name + '.',
                            'allow_create_topics': True
                        })

    celery_app.conf.task_default_queue = topic_name
    celery_app.conf.task_queues = {
        topic_name: {
            'exchange': topic_name,
            'routing_key': topic_name,
        },
    }

    return celery_app


celery_instance = make_celery('xai')
