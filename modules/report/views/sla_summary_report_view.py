import datetime

from flask import Markup
from pandas import DataFrame
from wtforms.validators import DataRequired

from modules.base_view import BaseView


def _data_formatter(view, context, model, name):
    if model.data:
        df = DataFrame(model.data)
        return Markup(df.T.to_html())
    else:
        return ""


class SLASummaryReportView(BaseView):
    column_searchable_list = ("start_time", "end_time", "last_updated", "completed_on")
    column_list = ('start_time', 'end_time', 'interval', "last_updated", "completed_on")
    form_columns = ('start_time', 'end_time')
    column_details_list = ['data']
    column_default_sort = ('start_time', True)
    column_formatters = {
        'data': _data_formatter
    }
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

    def is_accessible(self):
        status = super().is_accessible()
        self.can_edit = False   # Reports can only be viewed after creation
        return status
