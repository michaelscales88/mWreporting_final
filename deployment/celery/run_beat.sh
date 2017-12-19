#!/bin/bash

celery -A app.celery beat -l info