from app import build_server


if __name__ == '__main__':
    server = build_server("", "Starting")
    server.run(host='0.0.0.0')
