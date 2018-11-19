from flask_restful import Resource, reqparse
from flask_security import current_user

from .utilities import to_datetime, to_list, to_bool


class BaseResource(Resource):

    def __init__(self):
        parser = reqparse.RequestParser()
        # Core
        parser.add_argument("Authorization", location="headers")
        parser.add_argument("username")
        parser.add_argument("password")
        # Report
        parser.add_argument('start_time', type=to_datetime)
        parser.add_argument('end_time', type=to_datetime)
        parser.add_argument('clients', type=to_list)
        parser.add_argument("active", type=to_bool, default=True)
        self.args = parser.parse_args()
        # Security
        self.current_user = int(current_user.id) if current_user else None
        super().__init__()
