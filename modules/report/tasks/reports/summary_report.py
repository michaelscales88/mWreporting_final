# report/services/sla_report.py
from modules.celery_tasks import task_logger as logger
from modules.report.models import SlaReportModel


def build_summary_sla_data(start_time, end_time, interval):
    logger.info(
        "Started: Building SLA summary report data {start} to {end}".format(
            start=start_time, end=end_time
        )
    )

    if not SlaReportModel.interval_is_loaded(start_time, end_time, interval):
        logger.warning("Data not loaded for report interval.\n"
                       "Attempting to load data.")
        # TODO: implement scheduling the reports needed for the interval
        return "Exiting: Need to create reports first"

    summary_sla_data = {}
    while start_time < end_time:
        end_dt = start_time + interval
        report = SlaReportModel.get(start_time, end_dt)
        if not report:
            logger.warning("Report not created for report interval.\n"
                           "Attempting to load data.")
            SlaReportModel.create(start_time=start_time, end_time=end_dt)
            SlaReportModel.session.commit()
            SlaReportModel.session.remove()

            # TODO: implement this
            return "Error: a SLA report could not be located for {start} to {end}.".format(
                start=start_time, end=end_dt
            )

        if not report.data:
            logger.warning(
                "Error: a SLA report with finished data could not "
                "be located for {start} to {end}.".format(
                    start=start_time, end=end_dt
                )
            )
            # TODO: implement this
            return "Error: data is not loaded for report"

        dt_row_name = "{date} {start} to {end}".format(
            date=start_time.date(), start=start_time.time(), end=end_dt.time()
        )
        for row_name in report.data.keys():
            summary = summary_sla_data.get(row_name, {})
            summary[dt_row_name] = report.data[row_name]
            summary_sla_data[row_name] = summary

        start_time = end_dt

    logger.info(
        "Completed: Building SLA report data {start} to {end}".format(
            start=start_time, end=end_time
        )
    )
    return summary_sla_data
