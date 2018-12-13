# tasks/views.py
import logging

from celery.schedules import crontab
from flask import current_app
from wtforms.validators import DataRequired

from modules.base.base_view import BaseView
from .forms import CustomSelectField
from .utilities import scheduled_time_options, task_type_options

logger = logging.getLogger("app")


class ScheduleDispatchItemView(BaseView):
    column_list = [
        'name', 'task_type', 'scheduled_time', 'start_time',
        'end_time', 'date_created', 'active'
    ]
    form_columns = [
        'name', 'model_type', 'description', 'when_to_run', 'time_to_run',
        'start_time', 'end_time', 'active'
    ]
    form_extra_fields = dict(
        when_to_run=CustomSelectField(
            'Schedule Type',
            choices=scheduled_time_options(),
            validators=[DataRequired()]
        ),
        model_type=CustomSelectField(
            'Task Type',
            choices=task_type_options(),
            validators=[DataRequired()]
        )
    )

    def on_model_change(self, form, model, is_created):
        if is_created:
            current_app.config['CELERYBEAT_SCHEDULE'][form.data['name']] = {
                'task': '{type}.custom.{name}'.format(
                    type=form.data['model_type'],
                    name=form.data['name']
                ),
                'schedule': crontab(
                    **{current_app.config['BEAT_PERIOD']: current_app.config['BEAT_RATE']}
                )
            }
        else:
            # Update if there's a change
            if form.data.get("name") != model.name:
                del current_app.config['CELERYBEAT_SCHEDULE'][form.data['name']]
                current_app.config['CELERYBEAT_SCHEDULE'][form.data['name']] = {
                    'task': '{type}.custom.{name}'.format(
                        type=form.data['model_type'],
                        name=form.data['name']
                    ),
                    'schedule': crontab(
                        **{current_app.config['BEAT_PERIOD']: current_app.config['BEAT_RATE']}
                    )
                }
        super().on_model_change(form, model, is_created)

    def delete_model(self, model):
        del current_app.config['CELERYBEAT_SCHEDULE'][model.name]
        super().delete_model(model)
