# services/app_health_tests.py
from sqlalchemy.exc import DatabaseError


class DbCnxCheck(object):

    def __init__(self, db_session):
        self._engine = db_session
        self.is_database_working = True
        self.output = 'Connection: [ {session} ] is [ {status} ].'
        super().__init__()

    def status(self):
        return self.output.format(
            session=self._engine,
            status="Ok!" if self.is_database_working else "Not Okay."
        )

    def __call__(self, *args, **kwargs):
        with self._engine.connect() as con:
            try:
                # to check database we will execute raw query
                con.execute('SELECT 1')
            except DatabaseError:
                self.is_database_working = False
                return self.is_database_working, self.status()
            else:
                return self.is_database_working, self.status()


def check_local_db():
    from app.extensions import db
    local_check = DbCnxCheck(db.engine)
    return local_check()
