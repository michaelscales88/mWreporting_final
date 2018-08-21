# tasks/views.py
from app.base_view import BaseView
from flask_security import current_user


class ScheduledItemsView(BaseView):

    def is_accessible(self):
        if super().is_accessible():
            return True

        if current_user.has_role('_permissions | manager'):
            self.can_create = True
            self.can_edit = True
            self.can_delete = True
            return True

        return False
