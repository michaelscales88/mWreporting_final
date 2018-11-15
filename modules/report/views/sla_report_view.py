import datetime

import pytz
from flask import Markup, flash
from pandas import DataFrame
from wtforms.validators import DataRequired

from modules.base_view import BaseView


class SLAReportView(BaseView):
    column_searchable_list = ("start_time", "end_time",)
    column_exclude_list = ('date_requested', 'data',)
    column_details_list = ['data']
    form_excluded_columns = ('last_updated', 'completed_on')
    column_default_sort = ('start_time', True)
    form_args = dict(
        start_time=dict(
            label='Start Time',
            default=(
                datetime.datetime.today().replace(hour=7, minute=0, second=0, microsecond=0)
                - datetime.timedelta(days=1)
            ),
            validators=[DataRequired()]
        ),
        end_time=dict(
            label='End Time',
            default=(
                datetime.datetime.today().replace(hour=19, minute=0, second=0, microsecond=0)
                - datetime.timedelta(days=1)
            ),
            validators=[DataRequired()]
        )
    )
    form_widget_args = dict(date_requested=dict(disabled=True))
    column_formatters = {
        "data": lambda v, c, m, p:
        ""
        if m.data is None
        else Markup(DataFrame(m.data).T.to_html()),
        "last_updated": lambda v, c, m, p:
        ""
        if m.last_updated is None
        else m.last_updated.replace(tzinfo=pytz.utc).astimezone(
            tz=pytz.timezone("US/Central")),
        "completed_on": lambda v, c, m, p:
        ""
        if m.completed_on is None
        else m.completed_on.replace(tzinfo=pytz.utc).astimezone(
            tz=pytz.timezone("US/Central")),
    }

    def validate_form(self, form):
        """ Custom validation code that checks dates """
        if hasattr(form, "start_time") and form.start_time.data > form.end_time.data:
            flash("start time cannot be greater than end time!")
            return False
        return super().validate_form(form)
