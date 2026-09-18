import json

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()

def parse(b):
    if isinstance(b, str): b = b.encode()
    return json.loads(b.decode())
