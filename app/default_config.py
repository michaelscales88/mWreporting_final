import os


class Config(object):
    SECRET_KEY = os.urandom(24)  # Generate a random session key

    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    PACKAGEDIR = os.path.dirname(BASEDIR)
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
                                             os.path.join(PACKAGEDIR, 'tmp/db_repository'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Keep this off to reduce overhead

    # email server
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # administrator list
    ADMINS = ['mindwirelessreporting@gmail.com', 'michael.scales@g.austincc.edu']


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    USE_DEBUGGER = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # Turn this off to reduce overhead
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.environ.get('SQLALCHEMY_DATABASE_URI',
                                                            os.path.join(Config.PACKAGEDIR, 'tmp/local_app.db'))
