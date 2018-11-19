from modules.utilities import get_schedulable_models


def scheduled_time_options():
    options = (
        # 'Hourly',
        'Daily',
        # 'Monthly'
    )
    return list((item, item) for item in options)


def task_type_options():
    return list((item.opt_name(), item.opt_name()) for item in get_schedulable_models())
