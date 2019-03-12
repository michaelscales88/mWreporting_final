from flask import flash
from flask_admin.actions import action
from flask_admin.babel import gettext

from modules.base.base_view import BaseView
from modules.report.utilities import signals as s


class TablesLoadedView(BaseView):
    column_list = ('loaded_date', 'complete')
    form_create_rules = ('loaded_date',)
    form_edit_rules = ('reload',)
    column_default_sort = ('loaded_date', True)
    column_sortable_list = ('loaded_date',)
    column_searchable_list = ('loaded_date',)

    @action('reload', 'Reload Selected', 'Do you want to reload this data?')
    def action_approve(self, ids):
        try:
            query = self.model.query.filter(self.model.id.in_(ids))
            for model in query.all():
                s.load_calls(model.loaded_date, with_events=True)
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(gettext('Failed to reload data. %(error)s', error=str(ex)), 'error')
        else:
            flash(gettext('Data is being reloaded. Please wait :)'), 'info')

    def after_model_change(self, form, model, is_created):
        if is_created:
            s.load_calls(model.loaded_date, with_events=True)

    def after_model_delete(self, model):
        print("scrubbing data for", model)

    def is_accessible(self):
        status = super().is_accessible()
        self.can_edit = False  # Reports can only be viewed after creation
        return status


class CallDataView(BaseView):
    column_searchable_list = (
        'call_id', 'calling_party_number', 'dialed_party_number',
        'start_time', 'end_time', 'caller_id'
    )

    def is_accessible(self):
        # Use the TablesLoaded view to remove data
        accessible = super().is_accessible()
        self.can_edit = False
        self.can_delete = False
        return accessible


class EventDataView(BaseView):
    column_searchable_list = (
        'event_id', 'calling_party', 'receiving_party',
        'start_time', 'end_time', 'call_id'
    )

    def is_accessible(self):
        # Use the TablesLoaded view to remove data
        accessible = super().is_accessible()
        self.can_edit = False
        self.can_delete = False
        return accessible
