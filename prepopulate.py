import yaml
from modules import app, db
from modules.core import get_model_by_tablename


def seed_db():
    # Creates the database, tables, and seeds defaults
    with app.app_context():
        # Init security for the application
        from modules.core.security import user_datastore

        user_model = get_model_by_tablename("user")

        # Create the Admin user
        if user_model and not user_model.find(1):
            user_datastore.create_role(name='superuser')
            user_datastore.create_role(name='manager')
            user_datastore.create_role(name='user')
            user_datastore.create_user(
                username='admin',
                email='admin@email.com',
                password='password',
                first_name='Super',
                last_name='Admin',
                roles=['superuser']
            )
            db.session.commit()

        # Add clients
        client_model = get_model_by_tablename("client_model")

        with open("client_list.yml", "r") as client_list:
            file = dict(list(yaml.load_all(client_list))[0])
            clients = file.get("clients")
            if clients:
                for name, ext in clients.items():
                    client_model.create(name=name, ext=ext)
            db.session.commit()


if __name__ == '__main__':
    seed_db()
