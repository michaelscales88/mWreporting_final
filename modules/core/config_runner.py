# config/config_runner.py
import os
from modules import app


def get_log_dir(log_name):
    log_dir = os.path.join(app.config["LOGS_DIR"], log_name)
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


for root, dirs, files in os.walk("modules/"):
    for file in files:
        if file.endswith("_config.py"):
            module, *d = file.split("_")
            try:
                app.config.from_pyfile(os.path.join(os.path.basename(root), file))
            except FileNotFoundError:
                print("Failed to load [ {module_name} ] module settings.".format(module_name=module))
            else:
                print("Loaded [ {module_name} ] module settings.".format(module_name=module))

""" Make a folder for non-production dBs """
os.makedirs("instance/", exist_ok=True)

for root, dirs, files in os.walk("instance/"):
    """
    Load optional instance settings for the application.
    """
    for file in files:
        if file.endswith("_config.py"):
            module, *d = file.split("_")
            try:
                file_path = os.path.abspath(os.path.join("instance/", file))
                app.config.from_pyfile(file_path)
            except FileNotFoundError:
                print(
                    "Failed to load [ {module_name} ] "
                    "file's instance settings.".format(module_name=module)
                )
            else:
                print(
                    "Loaded [ {module_name} ] file's "
                    "instance settings.".format(module_name=module)
                )
