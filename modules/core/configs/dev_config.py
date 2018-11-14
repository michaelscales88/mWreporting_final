import os

# Development Settings
PRODUCTION_MODE = os.getenv("FLASK_ENV", "development") == 'production'
DEBUG = not PRODUCTION_MODE  # Toggle off during release
DEBUG_TOOLBAR_ENABLED = not PRODUCTION_MODE  # Gives information about routes
NOISY_ERROR = PRODUCTION_MODE
USE_LOGGERS = os.getenv("USE_LOGGERS", False) or PRODUCTION_MODE
LOGS_DIR = os.getenv("LOGS_DIR", "instance/logs")
