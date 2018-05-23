# report/api.py
from flask_restful import Resource, reqparse
from sqlalchemy.exc import DatabaseError
from flask_user import login_required, current_user


from app.services.app_tasks import return_task, to_list
from .models import UserModel, ClientUserSchema
from app.client.models import ClientModel


class UserAPI(Resource):

    decorators = [
        login_required,
        return_task
    ]

    def __init__(self):
        parser = reqparse.RequestParser()
        parser.add_argument('my_clients', location='form', type=to_list)
        self.args = parser.parse_args()
        self.client_schema = ClientUserSchema(many=True)
        super().__init__()

    def __del__(self):
        try:
            UserModel.session.commit()
        # Rollback a bad session
        except DatabaseError:
            UserModel.session.rollback()

    def get(self):
        """

        :return:
        """
        if current_user and current_user.is_authenticated:
            user = UserModel.get(current_user.id)
            user_clients = self.client_schema.dump(UserModel.get(user.id).clients).data
            return user_clients
        return []

    def put(self):
        """

        :return:
        """
        if current_user and current_user.is_authenticated:
            user = UserModel.get(current_user.id)
            # Reset current clients
            for cur_client in [client for client in user.clients]:
                user.clients.remove(cur_client)

            # Update given selection
            for new_client in self.args["my_clients"]:
                user.clients.append(ClientModel.get(int(new_client)))
        return True
