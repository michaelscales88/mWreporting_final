from .base import BaseView
from ..models import RolesModel


class RolesView(BaseView):
    can_delete = False  # disable model deletion
    can_edit = False
    can_create = False
    column_searchable_list = ('name', RolesModel.name)
    form_columns = ('name', 'users')
    edit_template = '/admin/edit_roles.html'
