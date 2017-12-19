#!/bin/bash

celery -A app.celery worker -l info