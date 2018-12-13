from modules.base.base_view import BaseView
from ..models import RolesModel


class RolesView(BaseView):
    column_searchable_list = ('name', RolesModel.name)
    form_columns = ('name', 'users')
