#!/usr/bin/env python
from backend.factories.application import create_application
from backend.factories.celery import create_celery


app = create_application()
app.app_context().push()
celery = create_celery(app)
