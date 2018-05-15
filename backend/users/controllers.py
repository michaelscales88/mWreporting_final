# report/api.py
from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy.exc import DatabaseError
from flask_user import login_required, current_user

from backend.services.extensions import user_manager
from .models import User


class UserAPI(Resource):

    decorators = [login_required]

    def __init__(self):
        parser = reqparse.RequestParser()
        self.args = parser.parse_args()
        super().__init__()

    def __del__(self):
        try:
            User.session.commit()
        # Rollback a bad session
        except DatabaseError:
            User.session.rollback()

    def get(self):
        if current_user and current_user.is_authenticated:
            return jsonify(
                api_key=user_manager.generate_token(int(current_user.get_id()))
            )
