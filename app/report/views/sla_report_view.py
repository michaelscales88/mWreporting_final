from flask import Markup
from pandas import DataFrame
from app.base_view import BaseView


class SLAReportView(BaseView):
    column_exclude_list = ['data']
    column_details_list = ['data']

    def _data_formatter(view, context, model, name):
        if model.data:
            df = DataFrame(model.data)
            return Markup(df.T.to_html())
        else:
            return ""

    column_formatters = {
        'data': _data_formatter
    }

