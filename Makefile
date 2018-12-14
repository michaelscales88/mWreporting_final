# This makefile starts and stops a rabbit broker and celery worker.
# Must be run with sudo for rabbitmq-server.

# include environment variables for worker
include nginx-uwsgi/envs/app.env
export

.PHONY: start_worker stop_worker \
        start_rabbit stop_rabbit refresh_worker \
        start_beat stop_beat refresh_beat

# Rabbit broker start up commands
start_rabbit:
	rabbitmq-server -detached

stop_rabbit:
	rabbitmqctl stop

start_worker:
	celery worker -A modules.celery_worker.celery -beat -Ofair --concurrency=10 -l info

stop_worker:
	pkill -9 -f 'celery worker'

refresh_worker: stop_worker start_worker
