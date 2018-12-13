# config/config_runner.py
import os
from modules import app


def get_log_dir(log_name):
    log_dir = os.path.join(app.config["LOGS_DIR"], log_name)
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


for root, dirs, files in os.walk("."):
    # Venv should be the last directory
    # Don't read any of the configs from the virtual env
    if 'venv' in root.split("/"):
        continue

    for file in files:
        if file.endswith("_config.py"):
            module, *d = file.split("_")
            try:
                path = os.path.abspath(os.path.join(root, file))
                app.config.from_pyfile(path)
            except FileNotFoundError:
                print("Failed to load [ {module_name} ] settings.".format(module_name=module))
            else:
                print("Loaded [ {module_name} ] settings.".format(module_name=module))
