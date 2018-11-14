import os

BASE_DIR = os.path.abspath(
    os.path.dirname(os.getenv("FLASK_APP", "app"))  # Find the root path

)

# SQLAlchemy Settings
DB_TYPE = os.getenv("DB_TYPE", "")
POSTGRES_USER = os.getenv('POSTGRES_USER', '')
POSTGRES_PW = os.getenv('POSTGRES_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', '')
POSTGRES_DB = os.getenv('POSTGRES_DB', '')
DB_PORT = os.getenv('DB_PORT', '')

SQLALCHEMY_DATABASE_URI = '{type}://{user}:{pwd}@{host}:{port}/{name}'.format(
    type=DB_TYPE, user=POSTGRES_USER, pwd=POSTGRES_PW, host=DB_HOST, name=POSTGRES_DB, port=DB_PORT
) if DB_TYPE else 'sqlite:///' + os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    os.path.join(BASE_DIR, 'instance/development_app.db')
)

SQLALCHEMY_MIGRATE_REPO = os.environ.get(
    'SQLALCHEMY_MIGRATE_FOLDER', os.path.join(BASE_DIR, '..', 'instance/db_repository')
)
# Turn this off to reduce overhead
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", False)