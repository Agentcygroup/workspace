from sdk import Client, Server, route

def test_add_and_get():
    s = Server()
    @route(s, "/ping")
    def ping(body): return {"pong": True}
    c = Client(s)
    code, body = c.get("/ping")
    assert code == 200
    assert body == {"pong": True}

def test_not_found():
    s = Server()
    c = Client(s)
    code, body = c.get("/nope")
    assert code == 404

def test_handler_error():
    s = Server()
    @route(s, "/boom")
    def boom(body): raise RuntimeError("x")
    c = Client(s)
    code, body = c.get("/boom")
    assert code == 500
    assert "x" in body["error"]

def test_post_body():
    s = Server()
    @route(s, "/echo")
    def echo(body): return {"got": body}
    c = Client(s)
    code, body = c.post("/echo", {"a": 1})
    assert body == {"got": {"a": 1}}
