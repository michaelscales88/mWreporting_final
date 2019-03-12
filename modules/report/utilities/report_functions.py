# report/services/sla_report.py
from datetime import timedelta

import pandas as pd

from modules.report.models import ClientModel, SlaReportModel


def get_td(interval, period):
    time_delta = {}
    if interval == 'D':
        time_delta['days'] = period
    elif interval == 'H':
        time_delta['hours'] = period
    elif interval == 'M':
        time_delta['minutes'] = period

    return timedelta(**time_delta)


def make_summary(df):
    # Create summary row
    summary_frame = pd.DataFrame(
        [df[SlaReportModel.data_headers()].sum()],
        columns=SlaReportModel.data_headers(),
        index=['Summary']
    )

    # Add summary label to row names (clients)
    summary_frame.insert(0, 'Client', ['Summary'])

    # Add the max timedelta to the summary
    summary_frame['Longest Waiting Answered'] = pd.Series(
        df['Longest Waiting Answered'].max(), index=summary_frame.index
    )
    return df.append(summary_frame, sort=False)


def compute_avgs(df):
    # Defaults
    df['Incoming Live Answered (%)'] = 1.0
    df['Incoming Received (%)'] = 1.0
    df['Incoming Abandoned (%)'] = 0.0
    df['PCA'] = 1.0

    # Calculate the percentages by row
    df['Incoming Live Answered (%)'] = df['Incoming Live Answered (%)'].where(
        df['I/C Presented'] == 0,
        other=df['I/C Live Answered'].divide(df['I/C Presented'], fill_value=0),
        axis=0
    )
    df['Incoming Received (%)'] = df['Incoming Received (%)'].where(
        df['I/C Presented'] == 0,
        (df['I/C Live Answered'].add(df['Voice Mails'])).divide(df['I/C Presented'], fill_value=0),
        axis=0
    )
    df['Incoming Abandoned (%)'] = df['Incoming Abandoned (%)'].where(
        df['I/C Presented'] == 0,
        df['I/C Lost'].divide(df['I/C Presented'], fill_value=0),
        axis=0
    )
    df['PCA'] = df['PCA'].where(
        df['I/C Presented'] == 0,
        df['Calls Ans Within 15'].add(df['Calls Ans Within 30']).divide(df['I/C Presented'], fill_value=0),
        axis=0
    )

    # TimeStamps
    df['Average Incoming Duration'] = df['Answered Incoming Duration']
    df['Average Wait Answered'] = df['Answered Wait Duration']
    df['Average Wait Lost'] = df['Lost Wait Duration']

    df['Average Incoming Duration'] = df['Average Incoming Duration'].where(
        df['I/C Live Answered'] < 1,
        df['Answered Incoming Duration'].divide(df['I/C Live Answered']),
        axis=0
    ).astype("timedelta64[ns]")
    df['Average Wait Answered'] = df['Average Wait Answered'].where(
        df['I/C Live Answered'] < 1,
        df['Answered Wait Duration'].divide(df['I/C Live Answered']),
        axis=0
    ).astype("timedelta64[ns]")
    df['Total Lost'] = df['I/C Lost'].add(df['Voice Mails'], fill_value=0)
    df['Average Wait Lost'] = df['Average Wait Lost'].where(
        df['Total Lost'] == 0,
        df['Average Wait Lost'].divide(df['Total Lost']),
        axis=0
    ).astype("timedelta64[ns]")
    return df


def format_df(cell):
    if isinstance(cell, float):
        return "{:.0%}".format(cell)
    if isinstance(cell, timedelta):
        hours, remainder = divmod(cell.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return '%02d:%02d:%02d' % (hours, minutes, seconds)
    else:
        return cell


def add_client_names(frame):
    # Show the client names as row names
    if not frame.empty:
        aliases = []
        for index in list(frame.index):
            client = ClientModel.query.filter(ClientModel.ext == index).first()
            if client:
                aliases.append("{name}".format(name=client.name))
            else:
                aliases.append(index)
        frame.insert(0, "Client", aliases)
    else:
        frame.insert(0, "Client", list(frame.index))
    return frame


def print_df(df):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)
