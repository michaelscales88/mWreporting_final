# report/services/sla_report.py
from datetime import timedelta

import numpy as np
import pandas as pd
from sqlalchemy.sql import and_

from app.utilities.helpers import query_to_frame, get_model_by_tablename


def get_td(interval, period):
    time_delta = {}
    if interval == 'D':
        time_delta['days'] = period
    elif interval == 'H':
        time_delta['hours'] = period
    elif interval == 'M':
        time_delta['minutes'] = period

    return timedelta(**time_delta)


def check_src_data_loaded(start_time, end_time, tables=("c_call", "c_event")):
    """
    Return True if the data is loaded for the date interval for all tables. Return False
    if not.
    :return:
    """
    table_loader = get_model_by_tablename("loaded_tables")
    for table_name in tables:
        if not table_loader.check_date_interval(start_time, end_time, table_name):
            print("Data not loaded:", start_time, end_time, table_name)
            return False
    return True


def make_summary(df):
    # Create row of sums
    sum_cols = [
        'I/C Presented',
        'I/C Live Answered',
        'I/C Lost',
        'Voice Mails',
        'Answered Incoming Duration',
        'Answered Wait Duration',
        'Lost Wait Duration',
        'Calls Ans Within 15',
        'Calls Ans Within 30',
        'Calls Ans Within 45',
        'Calls Ans Within 60',
        'Calls Ans Within 999',
        'Call Ans + 999'
    ]
    summary_frame = pd.DataFrame(
        [df[sum_cols].sum()], columns=sum_cols, index=['Summary']
    )
    summary_frame.insert(0, 'Client', ['Summary'])

    # Append column with max timedelta
    summary_frame['Longest Waiting Answered'] = pd.Series(
        df['Longest Waiting Answered'].max(), index=summary_frame.index
    )
    return df.append(summary_frame, sort=False)


def compute_avgs(df):
    print("starting compute avgs")
    print(df.dtypes)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(df)
    df['Incoming Live Answered (%)'] = np.where(
        df['I/C Live Answered'] < 1,
        df['I/C Live Answered'],
        df['I/C Live Answered'] / df['I/C Presented']
    )
    print("1")
    df['Incoming Received (%)'] = np.where(
        (df['I/C Live Answered'] + df['Voice Mails']) < 1,
        df['I/C Live Answered'],
        (df['I/C Live Answered'] + df['Voice Mails']) / df['I/C Presented']
    )
    print("2")
    df['Incoming Abandoned (%)'] = np.where(
        df['I/C Lost'] < 1,
        df['I/C Lost'],
        df['I/C Lost'] / df['I/C Presented']
    )
    print("3")
    # print(df['Answered Incoming Duration'] / df['I/C Live Answered'])
    # df['Average Incoming Duration'] = df['Average Incoming Duration'].values.astype('datetime64[s]')
    print(df['Answered Incoming Duration'])
    print(df['I/C Live Answered'])
    # df['Average Incoming Duration'] = np.where(
    #     df['I/C Live Answered'] < 1,
    #     df['Answered Incoming Duration'],
    #     df['Answered Incoming Duration'] / df['I/C Live Answered']
    # )
    print("4")
    # df['Average Wait Answered'] = df['Average Wait Answered'].apply(lambda x: x.replace(microsecond=0))
    # df['Average Wait Answered'] = pd.DataFrame(
    #     df['I/C Live Answered'] < 1,
    #     df['Answered Wait Duration'],
    #     df['Answered Wait Duration'] / df['I/C Live Answered']
    # )
    print("5")
    # df['Average Wait Lost'] = np.where(
    #     (df['I/C Lost'] + df['Voice Mails']) < 1,
    #     df['Lost Wait Duration'],
    #     df['Lost Wait Duration'] / (df['I/C Lost'] + df['Voice Mails'])
    # )
    # print("6")
    # df['PCA'] = np.where(
    #     df['I/C Presented'] < 1,
    #     df['I/C Presented'],
    #     (df['Calls Ans Within 15'] + df['Calls Ans Within 30']) / df['I/C Presented']
    # )
    print("computed avgs")
    return df


def format_df(cell):
    if isinstance(cell, float):
        return "{:.0%}".format(cell)
    else:
        return cell


def empty_report():
    empty_model = get_report_model('sla_report')
    return query_to_frame(empty_model, is_report=True)


def report_exists_by_name(table_name, start_time, end_time):
    report_table = get_model_by_tablename(table_name)
    return hasattr(report_table, "exists") and report_table.exists(start_time, end_time)


def get_report_model(table_name, start_time=None, end_time=None):
    report_table = get_model_by_tablename(table_name)
    if start_time and end_time and hasattr(report_table, "get"):
        return report_table.get(start_time, end_time)
    else:
        return report_table.set_empty(report_table())


def get_calls_by_direction(table_name, start_time, end_time, call_direction=1):
    table = get_model_by_tablename(table_name)
    return table.query.filter(
        and_(
            table.start_time >= start_time,
            table.end_time <= end_time,
            table.call_direction == call_direction
        )
    )


def add_frame_alias(table_name, frame):
    # Show the clients as row names
    table = get_model_by_tablename(table_name)
    if not frame.empty and hasattr(table, "name"):
        aliases = []
        for index in list(frame.index):
            client = table.query.filter(table.ext == index).first()
            if client:
                # aliases.append("{name} ({ext})".format(name=client.name, ext=client.ext))
                aliases.append("{name}".format(name=client.name))
            else:
                aliases.append(index)
        frame.insert(0, "Client", aliases)
    else:
        frame.insert(0, "Client", list(frame.index))
    return frame
