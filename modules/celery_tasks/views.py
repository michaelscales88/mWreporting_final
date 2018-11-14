# tasks/views.py
from modules.base_view import BaseView
from flask_security import current_user


class ScheduleDispatchItemView(BaseView):
    column_exclude_list = ['active']
    form_excluded_columns = ['active']

    def is_accessible(self):
        if super().is_accessible():
            return True

        if current_user.has_role('_permissions | manager'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            return True

        return False
