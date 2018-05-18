# backend/celery_config.py
import os


class Config(object):
    SITE_NAME = "mW Reporting"
    SECRET_KEY = os.urandom(24)  # Generate a random session key
    CSRF_ENABLED = True

    NOISY_ERROR = True

    BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    PACKAGEDIR = os.path.dirname(BASEDIR)
    TMP_DIR = os.path.join(PACKAGEDIR, 'instance')
    PACKAGE_NAME = os.path.basename(PACKAGEDIR)

    ROWS_PER_PAGE = 50

    """
    Use flask-bootstrap cdns    
    """
    BOOTSTRAP_SERVE_LOCAL = True
    BOOTSTRAP_USE_MINIFIED = False

    """
    DB Config
    """

    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}'.format(
        user=os.environ.get('POSTGRES_USER', ''),
        pwd=os.environ.get('POSTGRES_PASSWORD', ''),
        host=os.environ.get('POSTGRES_HOST', ''),
        port=os.environ.get('POSTGRES_PORT', 9999),
        name=os.environ.get('POSTGRES_DB', '')
    )

    EXTERNAL_DATABASE_URI = 'postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}'.format(
        user=os.environ.get('DBUSER', ''),
        pwd=os.environ.get('DBPASS', ''),
        host=os.environ.get('DBHOST', ''),
        port=os.environ.get('DBPORT', 9999),
        name=os.environ.get('DBNAME', '')
    )
    SQLALCHEMY_MIGRATE_REPO = os.environ.get('SQLALCHEMY_MIGRATE_FOLDER',
                                             os.path.join(PACKAGEDIR, 'instance/db_repository'))

    # Flask-Mail settings
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'youremail@example.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'yourpassword')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '"mWReporting" <noreply@example.com>')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '465'))
    MAIL_USE_SSL = int(os.getenv('MAIL_USE_SSL', True))

    # Flask-User settings
    USER_APP_NAME = "Flask-User QuickStart App"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False  # Simplify register form
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Mike1234")

    # administrator list
    ADMINS = ['mindwirelessreporting@gmail.com', 'michael.scales@g.austincc.edu']

    # settings for data source loader
    MAX_INTERVAL = 2


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = os.getenv('DEBUG_APP', True)
    USE_DEBUGGER = True
    TEST_MODE = os.getenv('TEST_MODE', False)
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # Turn this off to reduce overhead
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.environ.get(
        'SQLALCHEMY_DATABASE_URI', os.path.join(Config.PACKAGEDIR, 'instance/local_test.sqlite')
    )
