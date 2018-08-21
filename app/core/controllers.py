# security/controllers.py
from datetime import datetime, timedelta

import jwt
from flask import jsonify, current_app, abort
from flask_restful import Resource, reqparse

from .models import RolesModel
from .utilities import authenticate


class Authorize(Resource):

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username")
        parser.add_argument("password")
        self.args = parser.parse_args()
        super().__init__()

    def post(self):
        try:
            user = authenticate(self.args['username'], self.args['password'])
        except ConnectionError as err:
            abort(502, err)
        else:
            user_id = user.id
            roles = RolesModel.query.filter(RolesModel.users.any(id=user_id)).all()
            payload = {
                'identity': user_id,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(minutes=int(current_app.config['SECURITY_INTERVAL'])),
                'nbf': datetime.utcnow(),
            }

            for role in roles:
                pipe = str(role.name).find('|')

                if pipe == -1 or len(str(role.name)) == pipe + 1:
                    print('ERROR: INVALID PERMISSIONS: ' + str(role.name))
                else:
                    role_name = role.name[1:pipe - 1] + '_access'

                    if role_name not in payload:
                        payload[role_name] = str(role.name)
                    elif 'admin' not in payload[role_name]:
                        payload[role_name] = str(role.name)

            token = jwt.encode(payload, current_app.config['SECRET_KEY'])
            return jsonify(
                access_token=token.decode('UTF - 8')
            )


class RefreshToken(Resource):

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument("Authorization", location="headers")
        self.args = parser.parse_args()
        super().__init__()

    def get(self):
        try:
            payload = jwt.decode(self.args['Authorization'], current_app.config['SECRET_KEY'])
        except jwt.InvalidTokenError as err:
            return abort(401, err)
        else:
            new_payload = {
                'identity': payload['identity'],
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(minutes=50),
                'nbf': datetime.utcnow(),
            }

            roles = RolesModel.query.filter(RolesModel.users.any(id=payload['identity'])).all()
            for role in roles:
                pipe = str(role.name).find('|')

                if pipe == -1 or len(str(role.name)) == pipe + 1:
                    print('ERROR: INVALID PERMISSIONS: ' + str(role.name))
                else:
                    role_name = role.name[1:pipe - 1] + '_access'

                    if role_name not in new_payload:
                        new_payload[role_name] = str(role.name)
                    elif 'admin' not in new_payload[role_name]:
                        new_payload[role_name] = str(role.name)

            token = jwt.encode(new_payload, current_app.config['SECRET_KEY'])
            return jsonify(
                access_token=token.decode('UTF - 8')
            )
