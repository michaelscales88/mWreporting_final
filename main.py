import atexit


@atexit.register
def shutdown():
    print("Starting server shutdown procedure.")
    # Handle cleanup
    print("Server shutdown procedure completed.")


if __name__ == '__main__':
    from backend import build_server
    # TODO: finish server startup runner
    # from backend.tasks import start_runner
    # try:
    #     start_runner.delay(max_retries=1)
    # except:
    #     print("start runner e")
    server = build_server()
    server.run(port=8080)
