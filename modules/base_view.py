# base_view.py
import logging
from flask import abort, redirect, url_for, request
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user


logger = logging.getLogger("app")


class BaseView(ModelView):
    can_delete = False  # disable model deletion
    can_edit = False
    can_create = False
    can_view_details = True
    page_size = 50
    can_set_page_size = True

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            self.can_edit = True
            self.can_create = True
            self.can_delete = True
            return True

        if current_user.has_role('manager'):
            self.can_edit = True
            self.can_create = True
            return True

        if current_user.has_role('user'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))
        else:
            logger.warning(
                "User: [ {username} ] accessed [ {resource} ] resource.".format(
                    username=current_user.username, resource=self.name
                )
            )

    # def after_model_change(self, form, model, is_created):
    #     """
    #         Perform some actions after a model was created or updated and
    #         committed to the database.
    #
    #         Called from create_model after successful database commit.
    #
    #         By default does nothing.
    #
    #         :param form:
    #             Form used to create/update model
    #         :param model:
    #             Model that was created/updated
    #         :param is_created:
    #             True if model was created, False if model was updated
    #     """
    #     # model.session.remove()
