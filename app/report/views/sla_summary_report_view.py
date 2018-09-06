import datetime

from flask import Markup
from flask_security import current_user
from pandas import DataFrame
from wtforms.validators import DataRequired

from app.base_view import BaseView


class SLASummaryReportView(BaseView):
    column_searchable_list = ("start_time", "end_time",)
    column_details_list = ['data']
    form_excluded_columns = ('last_updated', 'completed_on')
    column_list = ('start_time', 'end_time', 'interval', 'last_updated', 'completed_on')
    column_default_sort = ('start_time', True)
    form_args = dict(
        start_time=dict(
            label='Start Time',
            default=(
                    datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
                    - datetime.timedelta(days=1)
            ),
            validators=[DataRequired()]
        ),
        end_time=dict(
            label='End Time',
            default=(
                datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
            ),
            validators=[DataRequired()]
        )

    )

    def _data_formatter(view, context, model, name):
        if model.data:
            df = DataFrame(model.data)
            return Markup(df.T.to_html())
        else:
            return ""

    column_formatters = {
        'data': _data_formatter
    }

    def is_accessible(self):
        if super().is_accessible():
            return True

        if current_user.has_role('_permissions | manager'):
            self.can_create = False
            self.can_edit = True
            self.can_delete = False
            return True

        return False
