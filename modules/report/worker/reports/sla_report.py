# report/services/sla_report.py
import datetime

from collections import OrderedDict, defaultdict
from sqlalchemy.sql import and_

from modules.worker import task_logger as logger
from modules.report.models import CallTableModel, SlaReportModel


class CallEntry(object):

    def __init__(self):
        self.inb_presented = 0
        self.inb_live_answered = 0
        self.inb_lost = 0
        self.voice_mails = 0
        self.avg_inc_duration = datetime.timedelta(0)
        self.avg_wait_ans = datetime.timedelta(0)
        self.avg_wait_lost = datetime.timedelta(0)
        self.calls_in_15 = 0
        self.calls_in_30 = 0
        self.calls_in_45 = 0
        self.calls_in_60 = 0
        self.calls_in_999 = 0
        self.calls_in_999plus = 0
        self.longest_wait_answered = datetime.timedelta(0)

    def call_answered(
        self,
        inb_presented=0,
        inb_live_answered=0,
        avg_inc_duration=datetime.timedelta(0),
        avg_wait_ans=datetime.timedelta(0),
        calls_in_15=0,
        calls_in_30=0,
        calls_in_45=0,
        calls_in_60=0,
        calls_in_999=0,
        calls_in_999plus=0,
        longest_wait_answered=datetime.timedelta(0)
    ):
        self.inb_presented = inb_presented
        self.inb_live_answered = inb_live_answered
        self.avg_inc_duration = avg_inc_duration
        self.avg_wait_ans = avg_wait_ans
        self.calls_in_15 = calls_in_15
        self.calls_in_30 = calls_in_30
        self.calls_in_45 = calls_in_45
        self.calls_in_60 = calls_in_60
        self.calls_in_999 = calls_in_999
        self.calls_in_999plus = calls_in_999plus
        self.longest_wait_answered = longest_wait_answered

    def call_lost(
        self,
        inb_presented=0,
        inb_lost=0,
        avg_wait_lost=datetime.timedelta(0)
    ):
        self.inb_presented = inb_presented
        self.inb_lost = inb_lost
        self.avg_wait_lost = avg_wait_lost

    def voice_mail(
        self,
        inb_presented=0,
        voice_mails=0,
        avg_wait_lost=datetime.timedelta(0),
    ):
        self.inb_presented = inb_presented
        self.voice_mails = voice_mails
        self.avg_wait_lost = avg_wait_lost

    def __dict__(self):
        return {
            'I/C Presented': self.inb_presented,
            'I/C Live Answered': self.inb_live_answered,
            'I/C Lost': self.inb_lost,
            'Voice Mails': self.voice_mails,
            'Answered Incoming Duration': self.avg_inc_duration,
            'Answered Wait Duration': self.avg_wait_ans,
            'Lost Wait Duration': self.avg_wait_lost,
            'Calls Ans Within 15': self.calls_in_15,
            'Calls Ans Within 30': self.calls_in_30,
            'Calls Ans Within 45': self.calls_in_45,
            'Calls Ans Within 60': self.calls_in_60,
            'Calls Ans Within 999': self.calls_in_999,
            'Call Ans + 999': self.calls_in_999plus,
            'Longest Waiting Answered': self.longest_wait_answered
        }

    def add(self, next_entry):
        self.inb_presented += next_entry.inb_presented
        self.inb_live_answered += next_entry.inb_live_answered
        self.inb_lost += next_entry.inb_lost
        self.voice_mails += next_entry.voice_mails
        self.avg_inc_duration += next_entry.avg_inc_duration
        self.avg_wait_ans += next_entry.avg_wait_ans
        self.avg_wait_lost += next_entry.avg_wait_lost
        self.calls_in_15 += next_entry.calls_in_15
        self.calls_in_30 += next_entry.calls_in_30
        self.calls_in_45 += next_entry.calls_in_45
        self.calls_in_60 += next_entry.calls_in_60
        self.calls_in_999 += next_entry.calls_in_999
        self.calls_in_999plus += next_entry.calls_in_999plus
        self.longest_wait_answered += next_entry.longest_wait_answered

    def __str__(self):
        return str(self.__dict__())

    def get_ordered_dict(self):
        return OrderedDict(self.__dict__())


def get_duration_bucket(wait_duration):
    # Qualify calls by duration
    if wait_duration <= datetime.timedelta(seconds=15):
        return {
            "calls_in_15": 1,
        }
    elif wait_duration <= datetime.timedelta(seconds=30):
        return {
            "calls_in_30": 1,
        }
    elif wait_duration <= datetime.timedelta(seconds=45):
        return {
            "calls_in_45": 1,
        }
    elif wait_duration <= datetime.timedelta(seconds=60):
        return {
            "calls_in_60": 1,
        }
    elif wait_duration <= datetime.timedelta(seconds=999):
        return {
            "calls_in_999": 1,
        }
    else:
        return {
            "calls_in_999plus": 1,
        }


def sum_events(call):
    event_dict = {}

    # Caching events by type makes report comparisons easier
    for ev in call.events:
        event_type = event_dict.get(ev.event_type, datetime.timedelta(seconds=0))
        event_dict[ev.event_type] = event_type + ev.length

    # Index on dialed party number
    call_index = str(call.dialed_party_number)

    # Event type 4 represents talking time with an agent
    talking_time = event_dict.get(4, datetime.timedelta(0))

    # Event type 10 represents a switch to voice mail
    voicemail_time = event_dict.get(10, datetime.timedelta(0))

    # Event type 5 = , 6 = , 7 =
    hold_time = sum(
        [event_dict.get(event_type, datetime.timedelta(0)) for event_type in (5, 6, 7)],
        datetime.timedelta(0)
    )
    wait_duration = call.length - talking_time - hold_time

    call_entry = CallEntry()

    # A live-answered call has > 0 seconds of agent talking time
    if talking_time > datetime.timedelta(0):
        call_entry.call_answered(
            inb_presented=1,
            inb_live_answered=1,
            avg_inc_duration=talking_time,
            avg_wait_ans=wait_duration,
            longest_wait_answered=wait_duration,
            **get_duration_bucket(wait_duration),
        )

    # A voice mail is not live answered and last longer than 20 seconds
    elif voicemail_time > datetime.timedelta(seconds=20):
        call_entry.voice_mail(
            inb_presented=1,
            voice_mails=1,
            avg_wait_lost=call.length
        )

    # An abandoned call is not live answered and last longer than 20 seconds
    elif call.length > datetime.timedelta(seconds=20):
        call_entry.call_lost(
            inb_presented=1,
            inb_lost=1,
            avg_wait_lost=call.length
        )

    return call_index, call_entry


def build_sla_data(session, start_time, end_time):
    logger.warning(
        "Started: Building SLA report data {start} to {end}".format(
            start=start_time, end=end_time
        )
    )

    calls_query = session.query(
        CallTableModel
    ).filter(
        and_(
            CallTableModel.start_time >= start_time.replace(microsecond=0),
            CallTableModel.start_time <= end_time.replace(microsecond=0),
            CallTableModel.call_direction == 1
        )
    ).all()

    # Combine all the data
    # TODO - reduce((lambda c: col_data[c[0]].add(**c[1])), list(map(sum_events, inb_calls_events)))
    combined_data = defaultdict(CallEntry)
    for (call_index, call_entry) in list(map(sum_events, calls_query)):
        combined_data[call_index].add(call_entry)

    final_report = {}
    clients = list(combined_data.keys())  # Consider a client to be a receiving party
    for client in clients:

        # Prune empty rows and convert to storage format
        if combined_data[client].inb_presented < 1:
            continue

        final_report[client] = combined_data[client].get_ordered_dict()

    logger.info(
        "Completed: Building SLA report data {start} to {end}".format(
            start=start_time, end=end_time
        )
    )
    return final_report
