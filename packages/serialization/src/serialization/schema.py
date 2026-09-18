class SchemaError(Exception):
    pass

class Schema:
    def __init__(self, required=None, types=None):
        self.required = list(required or [])
        self.types = dict(types or {})
    def validate(self, obj):
        if not isinstance(obj, dict):
            raise SchemaError("not a dict")
        for r in self.required:
            if r not in obj:
                raise SchemaError("missing: " + r)
        for k, t in self.types.items():
            if k in obj and not isinstance(obj[k], t):
                raise SchemaError("bad type for " + k)
        return True
