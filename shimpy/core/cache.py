from dogpile.cache import make_region
import logging

log = logging.getLogger(__name__)

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
            self.hit_count += 1
            log.debug("Cache hit: %s" % key)
            return data
        except:
            self.hit_count -= 1
            log.debug("Cache miss: %s" % key)
            return None

    def set(self, key, value, timeout=300):
        log.debug("Setting cache key: %s" % key)
        return _cache_region.set(key, value)
