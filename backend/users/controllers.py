# report/api.py
from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import DatabaseError
from flask_user import login_required


from backend.services.app_tasks import return_task, to_list
from .models import User


class UserAPI(Resource):

    decorators = [
        # login_required,
        return_task
    ]

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument('my_clients', location='form', type=to_list)
        self.args = parser.parse_args()
        super().__init__()

    def __del__(self):
        print("ending request")
        try:
            User.session.commit()
        # Rollback a bad session
        except DatabaseError:
            User.session.rollback()

    def get(self):
        return True

    def put(self):
        print("hit PUT USER", self.args["my_clients"])
        return True
