import atexit
from app import app_instance


@atexit.register
def shutdown():
    pass


if __name__ == '__main__':
    app_instance.run(port=8080)
