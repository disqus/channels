import logging
import simplejson
from datetime import datetime
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


# http://flask.pocoo.org/snippets/33/
def timesince(dt, past_="ago", future_="from now", default="just now"):
    """
    Returns string representing "time since" or "time until" e.g.
    3 days ago, 5 hours from now etc.
    """

    now = datetime.utcnow()
    if now > dt:
        diff = now - dt
        dt_is_past = True
    else:
        diff = dt - now
        dt_is_past = False

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:

        if period:
            return "%d %s %s" % (period, \
                singular if period == 1 else plural, \
                past_ if dt_is_past else future_)

    return default
