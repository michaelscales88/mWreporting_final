#!/usr/bin/env bash

# Start the worker + scheduler
celery worker -A modules.celery_worker.celery -beat -Ofair --concurrency=10 -l info