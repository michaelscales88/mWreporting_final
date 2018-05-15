import requests
import threading
import time

from backend.factories.server import mail
from backend.factories import create_celery
from backend.factories import create_application


celery = create_celery(create_application())


@celery.task(name="tasks.start_runner")
def start_runner(host="0.0.0.0", port=8080, max_retries=5):
    print("start running")

    def start_loop(retries_remaining):
        not_started = True

        while not_started and retries_remaining > 0:
            try:
                if requests.get(
                    'http://{host}:{port}/'.format(host=host, port=port)
                ).status_code == 200:
                    print('Server startup complete. Quitting start_runner.')
                    not_started = False

            except requests.exceptions.ConnectionError:
                print('Server startup is not yet completed.')

            time.sleep(2)
            retries_remaining -= 1

        if retries_remaining > 0:
            print("Server is ready to handle requests.")
        else:
            print("There was a problem starting up the server. Securing operations.")
            raise SystemExit("Could not run server.")

    print("Server is starting up. Waiting for server response.")
    thread = threading.Thread(target=start_loop, args=(max_retries,))

    try:
        thread.start()
    except SystemExit as e:
        print("inside system exit handler")
        if e == "Could not run server.":
            print("raising exit")
            raise SystemExit("Securing server operations.")
    print("outside thread")


@celery.task(name="tasks.send_async_mail")
def send_async_email(msg):
    """Background task to send an email with Flask-Mail."""
    mail.send(msg)
