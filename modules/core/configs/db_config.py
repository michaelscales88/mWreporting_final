import os

BASE_DIR = os.path.abspath(
    os.path.dirname(os.getenv("FLASK_APP", "app"))  # Find the root path

)

# SQLAlchemy Settings
DB_TYPE = os.getenv("DB_TYPE", "")
DB_USER = os.getenv('DB_USER', '')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', '')
DB_NAME = os.getenv('DB_NAME', '')
DB_PORT = os.getenv('DB_PORT', '')

SQLALCHEMY_DATABASE_URI = '{type}://{user}:{pwd}@{host}:{port}/{name}?charset=utf8mb4'.format(
    type=DB_TYPE, user=DB_USER, pwd=DB_PASSWORD, host=DB_HOST, name=DB_NAME, port=DB_PORT
) if DB_TYPE else 'sqlite:///' + os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    os.path.join(BASE_DIR, 'instance/development_app.db')
)

SQLALCHEMY_MIGRATE_REPO = os.environ.get(
    'SQLALCHEMY_MIGRATE_FOLDER', os.path.join(BASE_DIR, '..', 'instance/db_repository')
)
# Turn this off to reduce overhead
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", False)

EXTERNAL_DATABASE_URI = os.getenv("EXTERNAL_DATABASE_URI", "")
