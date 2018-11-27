from modules.base_view import BaseView


class TablesLoadedView(BaseView):
    column_list = ('loaded_date', 'last_updated', 'complete')
    form_columns = ('loaded_date',)
    column_default_sort = ('loaded_date', True)


class CallDataView(BaseView):
    pass


class EventDataView(BaseView):
    pass
