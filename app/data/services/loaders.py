# data/services/loaders.py
from flask import current_app
from sqlalchemy.sql import and_


from app.services import get_session
from app.services.app_tasks import get_model, get_pk, get_foreign_id


def load_data_for_table(table_name, start_time, end_time):
    table = get_model(table_name)
    if table is not None:
        ext_session = get_session(current_app.config['EXTERNAL_DATABASE_URI'], readonly=True)
        try:
            results = ext_session.query(table).filter(
                and_(
                    table.start_time >= start_time,
                    table.end_time <= end_time
                )
            )
            foreign_key = get_pk(table)
            for r in results.all():
                record = table.find(get_foreign_id(r, foreign_key))
                if record is None:
                    table.create(
                        **{i: r.__dict__[i] for i in r.__dict__ if i != '_sa_instance_state'}
                    )
        except Exception as e:
            print('Exceptional', e)
            ext_session.rollback()
        else:
            print("didn't break")
        finally:
            ext_session.close()
    return True
