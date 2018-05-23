from app import build_server

server = build_server()
if __name__ == '__main__':
    server.run(host='0.0.0.0')
