# modules/core/core_config.py
import os

# Application Settings
SITE_NAME = os.getenv("SITE_NAME", "MW_REPORTING")
BASE_DIR = os.path.abspath(
    os.path.dirname(os.getenv("FLASK_APP", "app"))  # Find the root path

)
SECRET_KEY = os.getenv("SECRET_KEY", "secret")  # Uses env variable in prod
CSRF_ENABLED = os.getenv("CSRF_ENABLED", True)
ROWS_PER_PAGE = 50

DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "Mike1234")
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'youremail@example.com')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '"Default" <{email}>'.format(email=MAIL_USERNAME))

# administrator list
ADMINS = [MAIL_DEFAULT_SENDER, '"Mike Scales" michael.scales88@gmail.com']

# Development Settings
PRODUCTION_MODE = os.getenv("FLASK_ENV", "development") == 'production'
DEBUG = not PRODUCTION_MODE  # Toggle off during release
DEBUG_TOOLBAR_ENABLED = not PRODUCTION_MODE  # Gives information about routes
NOISY_ERROR = PRODUCTION_MODE
USE_LOGGERS = os.getenv("USE_LOGGERS", False) or PRODUCTION_MODE
LOGS_DIR = os.getenv("LOGS_DIR", "instance/logs")
