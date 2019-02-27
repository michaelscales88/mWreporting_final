from flask import current_app
from flask.signals import Namespace
from modules.report.worker import load_call_data_task, load_event_data_task, load_report_task

namespace = Namespace()
signal_load_calls = namespace.signal('load_calls')
signal_load_events = namespace.signal('load_events')
signal_load_report = namespace.signal('load_report')


def load_calls(load_date, with_events=False):
    signal_load_calls.send(
        load_date=load_date,
        with_events=with_events
    )


def load_events(load_date):
    signal_load_events.send(
        load_date=load_date
    )


def load_report(start_time, end_time):
    signal_load_report.send(
        start_time=start_time,
        end_time=end_time
    )


@signal_load_calls.connect
def dispatch_load_calls_task(app, load_date, with_events):
    load_call_data_task.delay(load_date=load_date, with_events=with_events)


@signal_load_events.connect
def dispatch_load_events_task(app, load_date):
    load_event_data_task.delay(load_date=load_date)


@signal_load_report.connect
def dispatch_load_report_task(app, start_time, end_time):
    load_report_task.delay(start_time=start_time, end_time=end_time)
