import yaml

from modules import app
from modules.core import security
from modules.utilities.helpers import get_model_by_tablename
from flask_security.utils import hash_password


def seed_db():
    # Creates the database, tables, and seeds defaults
    with app.app_context():

        user_model = get_model_by_tablename("user")

        # Add superuser
        if not user_model.find(1):
            security.user_datastore.create_role(name="user")
            security.user_datastore.create_role(name='manager')
            su = security.user_datastore.create_role(name="superuser")

            user_model.session.commit()

            security.user_datastore.create_user(
                username='admin',
                first_name="Super",
                last_name="User",
                password=hash_password(app.config['DEFAULT_PASSWORD']),
                roles=[su]
            )

            security.user_datastore.create_user(
                username='keith',
                first_name="Keith",
                last_name="Clark",
                password=hash_password('secretpassword'),
                roles=[su]
            )

            user_model.session.commit()

        # Add clients
        client_model = get_model_by_tablename("client_model")

        with open("client_list.yml", "r") as client_list:
            file = dict(list(yaml.load_all(client_list))[0])
            clients = file.get("clients")
            if clients:
                for name, ext in clients.items():
                    if not client_model.find_by_name(name):
                        client_model.create(name=name, ext=ext)

            client_model.session.commit()

        manager = get_model_by_tablename("client_manager")
        mng = manager.create(name='superuser')

        for client in client_model.all():
            mng.clients.append(client)

        mng.session.commit()
        mng.session.remove()


if __name__ == '__main__':
    seed_db()
