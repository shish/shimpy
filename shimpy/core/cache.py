from dogpile.cache import make_region
import structlog

log = structlog.get_logger()

_cache_region = make_region().configure(
    'dogpile.cache.pylibmc',
    expiration_time = 3600,
    arguments = {
        'url': ["127.0.0.1"],
    }
)


class Cache(object):
    def __init__(self):
        self.hit_count = 0
        self.miss_count = 0

    def get(self, key):
        try:
            data = _cache_region.get(key)
        except Exception:
            data = None

        if data:
            self.hit_count += 1
            #log.debug("Cache hit", key=key)
        else:
            self.miss_count += 1
            #log.debug("Cache miss", key=key)

        return data

    def set(self, key, value, timeout=300):
        #log.debug("Setting cache key", key=key)
        try:
            return _cache_region.set(key, value)
        except Exception:
            pass
