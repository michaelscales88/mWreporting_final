# report/tasks.py
import logging
import pandas as pd
from celery.schedules import crontab

from app.core import save_xls
from .models import SlaReportModel, SummarySLAReportModel
from .utilities import (
    report_loader, make_summary_sla_report,
    # run_reports, email_reports,
    make_sla_report, add_client_names, compute_avgs,
    format_df, make_summary,
)

logger = logging.getLogger("app")


def register_tasks(server_instance):
    server_instance.config['CELERYBEAT_SCHEDULE']['loading_task'] = {
        'task': 'report.utilities.data_loader',
        'schedule': crontab(
            **{server_instance.config['BEAT_PERIOD']: server_instance.config['BEAT_RATE']}
        )
    }
    server_instance.config['CELERYBEAT_SCHEDULE']['report_task'] = {
        'task': 'report.utilities.report_loader',
        'schedule': crontab(
            **{server_instance.config['BEAT_PERIOD']: server_instance.config['BEAT_RATE']}
        )
    }
    server_instance.config['CELERYBEAT_SCHEDULE']['make_loading_tasks'] = {
        'task': 'report.utilities.data_scheduler',
        'schedule': crontab(
            **{server_instance.config['BEAT_PERIOD']: server_instance.config['BEAT_RATE']}
        )
    }
    server_instance.config['CELERYBEAT_SCHEDULE']['make_report_task'] = {
        'task': 'report.utilities.report_scheduler',
        'schedule': crontab(
            **{server_instance.config['BEAT_PERIOD']: server_instance.config['BEAT_RATE']}
        )
    }
    server_instance.config['CELERYBEAT_SCHEDULE']['make_summary_report_task'] = {
        'task': 'report.utilities.summary_report_scheduler',
        'schedule': crontab(
            **{server_instance.config['BEAT_PERIOD']: server_instance.config['BEAT_RATE']}
        )
    }


def report_task(report_name, start_time=None, end_time=None, clients=None):
    if start_time and end_time:
        if report_name == 'sla_report':
            return report_loader(start_time, end_time, clients)
        elif report_name == 'run_series':
            return run_reports(start_time, end_time, interval='H', period=12)
        elif report_name == 'get_summary':
            return get_summary_sla_report(start_time, end_time, clients)
        elif report_name == 'email_series':
            return email_reports(start_time, end_time, interval='H', period=12)
        else:
            return SlaReportModel.set_empty(SlaReportModel())
    else:
        logger.error(
            "Error: Report times: {start} and {end} are"
            "not both provided.\n".format(
                start=start_time, end=end_time
            )
        )


def get_sla_report(start_time, end_time, clients=()):
    # Check if report model exists
    report = SlaReportModel.get(start_time, end_time)

    # If the report does not exist make a report.
    if not report:
        logger.info(
            "Report does not exist for {start} to {end}.\n"
            "Attempting to make the report.".format(
                start=start_time, end=end_time
            )
        )
        report_made = make_sla_report(start_time=start_time, end_time=end_time)
        if not report_made:
            logger.error(
                "Report could not be made for {start}"
                "to {end}.\n".format(
                    start=start_time, end=end_time
                )
            )
            report = SlaReportModel.set_empty(SlaReportModel())
        else:
            report = SlaReportModel.get(start_time, end_time)
    else:
        logger.info(
            "Report exists for {start} to {end}.\n".format(
                start=start_time, end=end_time
            )
        )

    df = pd.DataFrame.from_dict(report.data, orient='index')

    # Filter the report to only include desired clients
    if clients and len(clients) > 0:
        df = df.filter(items=clients, axis=0)

    # Make the visible index the DID extension + client name,
    # or just DID extension if no name exists
    df = add_client_names(df)

    if not df.empty:
        # Create programmatic columns and rows
        df = make_summary(df)
        df = compute_avgs(df)
        # Filter out columns containing raw data
        df = df[['Client'] + SlaReportModel.headers()]

    # Prettify percentages
    return df.applymap(format_df)


def get_summary_sla_report(start_time, end_time, clients=()):
    if not clients:
        clients = ("7559",)

    # Check if summary model exists
    report = SummarySLAReportModel.get(start_time, end_time, frequency=43200)

    # If the report does not exist make a report.
    if not report:
        logger.info(
            "Report for: {start} and {end} over interval {interval} "
            "does not exist.\n".format(
                start=start_time, end=end_time, interval=report.interval
            )
        )
        report_made = make_summary_sla_report(start_time=start_time, end_time=end_time)
        if not report_made:
            logger.error(
                "Report for: {start} and {end} over interval {interval} "
                "could not be made.\n".format(
                    start=start_time, end=end_time, interval=report.interval
                )
            )
            report = SummarySLAReportModel.set_empty(SummarySLAReportModel())
        else:
            report = SummarySLAReportModel.get(start_time, end_time, frequency=43200)
    else:
        logger.info(
            "Report for: {start} and {end} over interval {interval} "
            "already exist.\n".format(
                start=start_time, end=end_time, interval=report.interval
            )
        )

    df = pd.DataFrame.from_dict(report.data)

    # Filter the report to only include desired clients
    if clients and len(clients) > 0:
        df = df.filter(items=clients, axis=1)
        print("filtered")

    list_of_dfs = []
    for col in df.keys():
        # Convert each column into a separate frame ->
        # Convert each column cell into a row with columns: preserving row_name
        # for row_name in df[col].keys():
            # print((row_name, df[col][row_name]))
            # print()

        t_df = pd.DataFrame.from_dict(
            dict(
                (row_name, df[col][row_name])
                for row_name in df[col].keys() if not pd.isna(df[col][row_name])
            ), columns=list(df[col][0].keys()), orient='index'
        )

        # Create programmatic columns and rows
        t_df = make_summary(t_df)
        t_df = compute_avgs(t_df)

        # Filter out columns containing raw data
        t_df = t_df[SlaReportModel.headers()]

        # Prettify percentages
        t_df = t_df.applymap(format_df)

        t_df.name = col

        list_of_dfs.append(t_df)

    for t_df in list_of_dfs:
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(t_df)

    save_xls(list_of_dfs, "test.xls")

    return df.T.to_html()
