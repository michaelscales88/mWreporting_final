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
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.environ.get('SQLALCHEMY_DATABASE_FILENAME',
                                                            os.path.join(PACKAGEDIR, 'tmp/local_app.db'))
    SQLALCHEMY_MIGRATE_REPO = os.environ.get('SQLALCHEMY_MIGRATE_FOLDER',
                                             os.path.join(PACKAGEDIR, 'tmp/db_repository'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Keep this off to reduce overhead
    # This connects to our source data
    EXT_DATA_PG_URI = 'postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}'.format(
        user=os.environ.get('DBUSER', 'Chronicall'), pwd=os.environ.get('DBPASS', 'ChR0n1c@ll1337'),
        host=os.environ.get('DBHOST', '10.1.3.17'), port=os.environ.get('DBPORT', '9086'), name=os.environ.get('DBNAME', 'chronicall')
    )

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
