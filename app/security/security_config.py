import os


SECURITY_MODULE_ROUTES = {
    "Authorize": {
        "url": "/api/security/get-token",
        "methods": {}
    },
    "RefreshToken": {
        "url": "/api/security/refresh-token",
        "methods": {}
    }
}

SECURITY_INTERVAL = os.getenv("SECURITY_INTERVAL", 90)

# Flask-Security config
SECURITY_URL_PREFIX = os.getenv("SECURITY_URL_PREFIX", "/admin")
SECURITY_PASSWORD_HASH = os.getenv("SECURITY_PASSWORD_HASH", "pbkdf2_sha512")
SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "AJBOELjvisLDkvzi")
SECURITY_USER_IDENTITY_ATTRIBUTES = ("username", "email")

# Flask-Security URLs, overridden because they don't put a / at the end
SECURITY_LOGIN_URL = os.getenv("SECURITY_LOGIN_URL", "/login/")
SECURITY_LOGOUT_URL = os.getenv("SECURITY_LOGOUT_URL", "/logout/")
SECURITY_REGISTER_URL = os.getenv("SECURITY_REGISTER_URL", "/register/")
SECURITY_RESET_URL = os.getenv("SECURITY_RESET_URL", "/reset/")

SECURITY_POST_LOGIN_VIEW = os.getenv("SECURITY_POST_LOGIN_VIEW", "/admin/")
SECURITY_POST_LOGOUT_VIEW = os.getenv("SECURITY_POST_LOGOUT_VIEW", "/admin/")
SECURITY_POST_REGISTER_VIEW = os.getenv("SECURITY_POST_REGISTER_VIEW", "/admin/")
SECURITY_POST_RESET_VIEW = os.getenv("SECURITY_POST_RESET_VIEW", "/admin/")

# Flask-Security features
SECURITY_REGISTERABLE = os.getenv("SECURITY_REGISTERABLE", True)
SECURITY_SEND_REGISTER_EMAIL = os.getenv("SECURITY_SEND_REGISTER_EMAIL", False)
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", False)
SECURITY_RECOVERABLE = os.getenv("SECURITY_RECOVERABLE", True)
