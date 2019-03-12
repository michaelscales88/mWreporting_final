from wtforms import RadioField
from modules.base.base_view import BaseView
from modules.report.utilities import signals as s


class TablesLoadedView(BaseView):
    column_list = ('loaded_date', 'complete')
    form_create_rules = ('loaded_date',)
    form_edit_rules = ('reload',)
    column_default_sort = ('loaded_date', True)
    column_sortable_list = ('loaded_date', 'complete')

    form_extra_fields = dict(
        reload=RadioField('Reload:', choices=[('both', 'Both'), ('calls', 'Calls'), ('events', "Events")])
    )

    def after_model_change(self, form, model, is_created):
        if is_created:
            s.load_calls(model.loaded_date)
            s.load_events(model.loaded_date)
        else:
            reload = form.reload.data
            if reload:
                if reload == 'both':
                    s.load_calls(model.loaded_date, with_events=True)
                if reload == 'calls':
                    s.load_calls(model.loaded_date)
                if reload == 'events':
                    s.load_events(model.loaded_date)

    def after_model_delete(self, model):
        print("scrubbing data for", model)


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
