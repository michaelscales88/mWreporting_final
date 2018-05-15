#!/usr/bin/env python
from backend.factories import create_celery, create_application

app = create_application()
app.app_context().push()
celery = create_celery(app)
