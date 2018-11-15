import yaml
from modules import app, db
from modules.core import get_model_by_tablename


def seed_db():
    # Creates the database, tables, and seeds defaults
    with app.app_context():

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
