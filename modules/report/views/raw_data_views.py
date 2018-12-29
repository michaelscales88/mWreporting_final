from modules.base.base_view import BaseView
from modules.report.tasks import call_data_task, event_data_task


class TablesLoadedView(BaseView):
    column_list = ('loaded_date', 'last_updated', 'complete')
    form_columns = ('loaded_date',)
    column_default_sort = ('loaded_date', True)

    def after_model_change(self, form, model, is_created):
        if is_created:
            call_data_task.delay(load_date=model.loaded_date)
            event_data_task.delay(load_date=model.loaded_date)

    def is_accessible(self):
        status = super().is_accessible()
        self.can_edit = False  # Reports can only be viewed after creation
        return status


class CallDataView(BaseView):
    pass


class EventDataView(BaseView):
    pass
