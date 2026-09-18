class PMap:
    def __init__(self, data=None):
        self._data = dict(data or {})

    def set(self, key, value):
        new = dict(self._data)
        new[key] = value
        return PMap(new)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def remove(self, key):
        new = dict(self._data)
        new.pop(key, None)
        return PMap(new)

    def contains(self, key):
        return key in self._data

    def keys(self):
        return list(self._data.keys())

    def size(self):
        return len(self._data)

    def merge(self, other):
        new = dict(self._data)
        new.update(other._data)
        return PMap(new)
