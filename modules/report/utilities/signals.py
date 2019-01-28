from flask import current_app
from flask.signals import Namespace
from modules.report.worker import call_data_task, event_data_task, report_task

namespace = Namespace()
signal_load_calls = namespace.signal('load_calls')
signal_load_events = namespace.signal('load_events')
signal_load_report = namespace.signal('load_report')


def load_calls(load_date, with_events=False):
    signal_load_calls.send(
        current_app._get_current_object(),
        load_date=load_date,
        with_events=with_events
    )


def load_events(load_date):
    signal_load_events.send(
        current_app._get_current_object(),
        load_date=load_date
    )


def load_report(start_time, end_time):
    signal_load_report.send(
        current_app._get_current_object(),
        start_time=start_time,
        end_time=end_time
    )


@signal_load_calls.connect
def dispatch_load_calls(app, load_date, with_events):
    call_data_task.delay(load_date=load_date, with_events=with_events)


@signal_load_events.connect
def dispatch_load_events(app, load_date):
    event_data_task.delay(load_date=load_date)


@signal_load_report.connect
def dispatch_load_report(app, start_time, end_time):
    report_task.delay(start_time=start_time, end_time=end_time)
