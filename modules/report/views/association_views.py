from modules.base_view import BaseView


class TablesLoadedView(BaseView):
    form_excluded_columns = ('last_updated', 'date_requested', 'calls_loaded', "events_loaded")
    column_list = ('loaded_date', 'last_updated', 'complete')
    column_default_sort = ('loaded_date', True)


class ClientManagerView(BaseView):
    pass
