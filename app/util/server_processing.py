import pandas as pd
from sqlalchemy.inspection import inspect

from app.data.tasks import _mmap as model_map
from app.report.tasks import _mmap as report_map


all_map = {
    **model_map,
    **report_map
}


def server_side_processing(
        query,  # Unmodified query object
        query_params,
        model_name=None,
        ascending=False
):
    try:
        model = all_map.get(model_name)
        if model:
            pk = inspect(model).primary_key[0]
            query = query.order_by(pk.asc()) if ascending else query.order_by(pk.desc())

        # Offset if we are going beyond the initial ROWS_PER_PAGE
        if query_params['start'] > 0:
            query = query.offset(query_params['start'])

        # Limit the number of rows to the page
        query = query.limit(query_params['length'])

        frame = pd.read_sql(query.statement, query.session.bind)
    except AttributeError:
        frame = pd.DataFrame.from_dict(query)
        return frame, len(frame.index)
    else:
        return frame[model.__repr_attrs__], len(frame.index)
