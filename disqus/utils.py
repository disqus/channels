import logging
import simplejson
from disqus import db

logger = logging.getLogger(__name__)


def from_cache(callback, cache_key=None, expires=60):
    if cache_key is None:
        cache_key = '%s.%s' % (callback.__module__, callback.__name__)
    conn = db.get_conn(cache_key)
    result = conn.get(cache_key)
    if result:
        try:
            result = simplejson.loads(result)
        except Exception, e:
            logger.exception(e)
            result = None

    if result is None:
        result = callback()
        pipe = conn.pipeline()
        pipe.set(cache_key, simplejson.dumps(result))
        pipe.expire(cache_key, 60)
        pipe.execute()
    return result
