#!/usr/bin/env python
from app.factories.application import create_application
from app.factories.celery import create_celery


app = create_application()
app.app_context().push()
celery = create_celery(app)
