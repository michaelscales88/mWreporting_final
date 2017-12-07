import os


class Config(object):
    SECRET_KEY = os.urandom(24)     # Generate a random session key

    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    PACKAGEDIR = os.path.dirname(BASEDIR)
    PACKAGE_NAME = os.path.basename(PACKAGEDIR)

    # email server
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

    # administrator list
    ADMINS = ['your-gmail-username@gmail.com']


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
