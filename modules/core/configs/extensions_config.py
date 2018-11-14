import os

SITE_NAME = os.getenv("SITE_NAME", "MW_REPORTING")

# Flask-Bootstrap Settings
BOOTSTRAP_SERVE_LOCAL = True
BOOTSTRAP_USE_MINIFIED = False

# Flask-Mail settings
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'youremail@example.com')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'yourpassword')
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