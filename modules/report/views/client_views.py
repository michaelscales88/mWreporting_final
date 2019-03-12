from modules.base.base_view import BaseView


class ClientManagerView(BaseView):
    pass


class ClientView(BaseView):
    column_default_sort = 'name'
    column_searchable_list = (
        'name', 'ext', 'active', 'notes'
    )
