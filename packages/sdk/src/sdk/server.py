import json, http.server, socketserver
from dataclasses import dataclass, field

@dataclass
class Server:
    routes: dict = field(default_factory=dict)
    port: int = 8080
    def __post_init__(self):
        pass
    def add(self, path, handler):
        self.routes[path] = handler
        return handler
    def handle(self, path, body):
        h = self.routes.get(path)
        if h is None:
            return 404, {"error": "not found", "path": path}
        try:
            result = h(body)
            return 200, result
        except Exception as e:
            return 500, {"error": str(e)}

def route(server, path):
    def deco(fn):
        server.add(path, fn)
        return fn
    return deco
