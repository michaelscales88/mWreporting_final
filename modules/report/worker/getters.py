# report/tasks.py
import logging

import pandas as pd

from modules.utilities.helpers import save_xls
from modules.report.models import SlaReportModel, SummarySLAReportModel
from modules.report.utilities.report_functions import (
    add_client_names, compute_avgs, format_df, make_summary
)
from modules.report.utilities import signals as s

# from .loaders import report_loader

logger = logging.getLogger("app")


def get_sla_report(start_time, end_time, clients=()):
    # Check if report model exists
    report = SlaReportModel.find(start_time, end_time)
    msg = None

    # If the report does not exist make a report.
    if not report:
        logger.info(
            "Report does not exist for {start} to {end}.\n"
            "Attempting to make the report.".format(
                start=start_time, end=end_time
            )
        )
        report = SlaReportModel.set_empty(SlaReportModel())
        msg = {
            'msg': "Building Report",
            "timeout": 30
        }
        print("calling load report")
        s.load_report(start_time, end_time)
        print("called load report")
    else:
        logger.info(
            "Report exists for {start} to {end}.\n".format(
                start=start_time, end=end_time
            )
        )
        report = SlaReportModel.find(start_time, end_time)

    if report.data:
        df = pd.DataFrame.from_dict(report.data, orient='index')

        # Filter the report to only include desired clients
        if clients and len(clients) > 0:
            df = df.filter(items=clients, axis=0)

        # Make the visible index the DID extension + client name,
        # or just DID extension if no name exists
        df = add_client_names(df)

        # Create programmatic columns and rows
        df = make_summary(df)
        df = compute_avgs(df)

        # Filter out columns containing raw data
        df = df[['Client'] + SlaReportModel.view_headers()]

        # Prettify percentages
        df = df.applymap(format_df)
    else:
        df = pd.DataFrame(columns=['Client'] + SlaReportModel.view_headers())

    return df, msg


def get_summary_sla_report(start_time, end_time, clients=()):

    # Check if summary model exists
    report = SummarySLAReportModel.get(start_time, end_time, frequency=43200)

    # If the report does not exist make a report.
    if not report:
        pass
        # logger.info(
        #     "Report for: {start} and {end} over interval {interval} "
        #     "does not exist.\n".format(
        #         start=start_time, end=end_time, interval=report.interval
        #     )
        # )
        # report_made = make_summary_sla_report(start_time=start_time, end_time=end_time)
        # if not report_made:
        #     logger.error(
        #         "Report for: {start} and {end} over interval {interval} "
        #         "could not be made.\n".format(
        #             start=start_time, end=end_time, interval=report.interval
        #         )
        #     )
        #     report = SummarySLAReportModel.set_empty(SummarySLAReportModel())
        # else:
        #     report = SummarySLAReportModel.get(start_time, end_time, frequency=43200)
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

    list_of_dfs = []
    for col in df.keys():
        # Convert each column cell into a row with columns: preserving row_name
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
        t_df = t_df[SlaReportModel.view_headers()]

        # Prettify percentages
        t_df = t_df.applymap(format_df)

        t_df.name = col

        list_of_dfs.append(t_df)

    save_xls(list_of_dfs, "test.xls")

    return df.T.to_html()