
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(metaclass=SingletonMeta):
    def __init__(self, config_data=None):
        if not hasattr(self, '_initialized'):
            self._config = config_data or {}
            self._initialized = True

    def get_or(self, key, fallback=None):
        return self._config.get(key, fallback)
