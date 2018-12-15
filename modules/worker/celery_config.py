# app/config.py
import os

TASKS_MODULE_ROUTES = {}

"""
Get Broker Information
"""
AMQP_USERNAME = os.getenv('AMQP_USERNAME', 'user')
AMQP_PASSWORD = os.getenv('AMQP_PASSWORD', 'password')
AMQP_HOST = os.getenv('AMQP_HOST', 'localhost')
AMQP_PORT = int(os.getenv('AMQP_PORT', '5672'))
BROKER_API_PORT = int(os.getenv('BROKER_API_PORT', '15672'))
accept_content = ['json']

"""
RabbitMQ Broker Management
"""
# RabbitMQ task broker
broker_url = 'amqp://{user}:{pw}@{host}:{port}'.format(
    user=AMQP_USERNAME,
    pw=AMQP_PASSWORD,
    host=AMQP_HOST,
    port=AMQP_PORT
)

# RabbitMQ management api
broker_api = 'amqp://{user}:{pw}@{host}:{port}/api/'.format(
    user=AMQP_USERNAME,
    pw=AMQP_PASSWORD,
    host=AMQP_HOST,
    port=BROKER_API_PORT
)

# Enable debug logging
logging = os.getenv('FLOWER_LOG_LEVEL', 'INFO')

"""
Celery Task Queue Management
"""
result_backend = 'rpc://{user}:{pw}@{host}:{port}'.format(
    user=AMQP_USERNAME,
    pw=AMQP_PASSWORD,
    host=AMQP_HOST,
    port=AMQP_PORT
)

"""
Celery Beat Persistent Task Scheduler
"""
beat_schedule = {}
BEAT_PERIOD = os.getenv('BEAT_PERIOD', 'minute')
BEAT_RATE = os.getenv('BEAT_RATE', '*/1')
