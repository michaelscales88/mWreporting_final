#!/usr/bin/env bash

# Start the worker + scheduler
celery worker -A modules.worker.celery_worker.celery -beat \
    -s /tmp/celerybeat-schedule -Ofair --concurrency=10 -l info