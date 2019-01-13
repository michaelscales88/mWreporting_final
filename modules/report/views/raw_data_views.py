from wtforms import RadioField
from modules.base.base_view import BaseView
from modules.report.tasks import call_data_task, event_data_task


class TablesLoadedView(BaseView):
    column_list = ('loaded_date', 'complete')
    form_create_rules = ('loaded_date',)
    form_edit_rules = ('reload',)
    column_default_sort = ('loaded_date', True)

    form_extra_fields = dict(
        reload=RadioField('Reload:', choices=[('both', 'Both'), ('calls', 'Calls'), ('events', "Events")])
    )

    def after_model_change(self, form, model, is_created):
        if is_created:
            call_data_task.delay(load_date=model.loaded_date)
            event_data_task.delay(load_date=model.loaded_date)
        else:
            reload = form.reload.data
            if reload:
                if reload == 'both':
                    call_data_task.delay(load_date=model.loaded_date)
                    event_data_task.delay(load_date=model.loaded_date)
                if reload == 'calls':
                    call_data_task.delay(load_date=model.loaded_date)
                if reload == 'events':
                    event_data_task.delay(load_date=model.loaded_date)


class CallDataView(BaseView):
    pass


class EventDataView(BaseView):
    pass
