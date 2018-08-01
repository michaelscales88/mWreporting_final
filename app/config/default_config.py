# app/celery_config.py
import os

# Application Settings
SITE_NAME = os.getenv("SITE_NAME", "MW_REPORTING")
BASE_DIR = os.path.abspath(
    os.path.dirname(os.getenv("FLASK_APP", "app"))  # Find the root path

)
SECRET_KEY = os.getenv("SECRET_KEY", "secret")  # Uses env variable in prod
CSRF_ENABLED = os.getenv("CSRF_ENABLED", True)
ROWS_PER_PAGE = 50

# Development Settings
PRODUCTION_MODE = os.getenv("FLASK_ENV", "development") == 'production'
DEBUG = not PRODUCTION_MODE  # Toggle off during release
DEBUG_TOOLBAR_ENABLED = not PRODUCTION_MODE  # Gives information about routes
NOISY_ERROR = PRODUCTION_MODE
USE_LOGGERS = os.getenv("USE_LOGGERS", False) or PRODUCTION_MODE
LOGS_DIR = os.getenv("LOGS_DIR", "instance/logs")

# Flask-Bootstrap Settings
BOOTSTRAP_SERVE_LOCAL = True
BOOTSTRAP_USE_MINIFIED = False

# Flask-Mail settings
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'youremail@example.com')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'yourpassword')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '"Default" <{email}>'.format(email=MAIL_USERNAME))
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', '465'))
MAIL_USE_SSL = int(os.getenv('MAIL_USE_SSL', True))

# Flask-User settings
USER_APP_NAME = SITE_NAME  # Shown in and email templates and page footers
USER_ENABLE_EMAIL = True  # Enable email requirement
USER_ENABLE_CHANGE_PASSWORD = True  # Allow users to change their password
USER_ENABLE_CHANGE_USERNAME = False  # Allow users to change their username
USER_ENABLE_LOGIN_WITHOUT_CONFIRM_EMAIL = True  # Disable requirement for email verification
USER_ENABLE_USERNAME = True  # Enable username authentication
USER_REQUIRE_RETYPE_PASSWORD = False  # Simplify register form

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Mike1234")

# administrator list
ADMINS = [MAIL_DEFAULT_SENDER, '"Mike Scales" michael.scales88@gmail.com']

# SQLAlchemy Settings
DB_TYPE = os.getenv("DB_TYPE", "")
USER = os.getenv('DB_USER', '')
PWD = os.getenv('DB_PW', '')
DB_HOST = os.getenv('HOST', '')
DB_NAME = os.getenv('DB_NAME', '')
SQLALCHEMY_DATABASE_URI = '{type}://{user}:{pwd}@{host}/{name}'.format(
    type=DB_TYPE, user=USER, pwd=PWD, host=DB_HOST, name=DB_NAME
) if DB_TYPE else 'sqlite:///' + os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    os.path.join(BASE_DIR, 'instance/development_app.db')
)
SQLALCHEMY_MIGRATE_REPO = os.environ.get(
    'SQLALCHEMY_MIGRATE_FOLDER', os.path.join(BASE_DIR, '..', 'instance/db_repository')
)
SQLALCHEMY_TRACK_MODIFICATIONS = not PRODUCTION_MODE  # Turn this off to reduce overhead
