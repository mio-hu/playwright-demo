class GlobalMap:
    _data = {}

    @classmethod
    def set(cls, key, value):
        cls._data[key] = value

    @classmethod
    def get(cls, key, default=None):
        return cls._data.get(key, default)

    @classmethod
    def delete(cls, key):
        if key in cls._data:
            del cls._data[key]

    @classmethod
    def clear(cls):
        cls._data.clear()
