from .server import Server

class Client:
    def __init__(self, server):
        if not isinstance(server, Server):
            raise TypeError("server must be a Server")
        self.server = server
    def get(self, path):
        return self.server.handle(path, None)
    def post(self, path, body):
        return self.server.handle(path, body)
