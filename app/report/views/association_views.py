from app.base_view import BaseView
from flask_security import current_user


class TablesLoadedView(BaseView):
    form_excluded_columns = ["date_downloaded", "date_requested", "is_loaded"]


class ClientManagerView(BaseView):
    def is_accessible(self):
        if super().is_accessible():
            return True

        if current_user.has_role('_permissions | manager'):
            self.can_create = False
            self.can_edit = True
            self.can_delete = False
            return True

        return False
