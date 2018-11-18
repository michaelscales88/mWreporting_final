# This makefile starts and stops a rabbit broker and celery worker.
# Must be run with sudo for rabbitmq-server.

# include environment variables for worker
include nginx-uwsgi/envs/dev.env
export

.PHONY: start_worker stop_worker \
        start_rabbit stop_rabbit refresh_worker \
        start_beat stop_beat refresh_beat

# Rabbit broker start up commands
start_rabbit:
	rabbitmq-server -detached

stop_rabbit:
	rabbitmqctl stop

start_worker1:
	celery worker -A modules.celery_worker.celery -E --beat --concurrency=10 -l info -n worker1@%h

start_worker2:
	celery worker -A modules.celery_worker.celery -E --concurrency=10 -l info -n worker2@%h

start_worker3:
	celery worker -A modules.celery_worker.celery -E --concurrency=10 -l info -n worker3@%h

stop_worker:
	pkill -9 -f 'celery worker'

refresh_worker: stop_worker start_worker
