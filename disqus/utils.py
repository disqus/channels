"""
disqus.utils
~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import logging
import pytz
import json
from datetime import datetime, timedelta
from disqus import db
from flask import make_response

logger = logging.getLogger(__name__)

def secure_avatar(avatar_url):
    return avatar_url.replace('http://mediacdn', 'https://securecdn')


def datestr_to_datetime(dt):
    return datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')


def from_cache(callback, cache_key=None, expires=60):
    if cache_key is None:
        if hasattr(callback, 'im_self'):
            cache_key = '.'.join([callback.__module__, callback.im_self.__name__, callback.__name__])
        else:
            cache_key = '%s.%s' % (callback.__module__, callback.__name__)
    conn = db.get_conn(cache_key)
    result = conn.get(cache_key)
    if result:
        try:
            result = json.loads(result)
        except Exception, e:
            logger.exception(e)
            result = None

    if result is None:
        result = callback()
        pipe = conn.pipeline()
        pipe.set(cache_key, json.dumps(result))
        pipe.expire(cache_key, 60)
        pipe.execute()
    return result


# http://flask.pocoo.org/snippets/33/
def timesince(dt):
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
            if dt_is_past:
                return "%d %s ago" % (period, singular if period == 1 else plural)
            return "in %d %s" % (period, singular if period == 1 else plural)

    return 'just now'


eastern = pytz.timezone('Antarctica/Rothera')


def convert_pycon_dt(value):
    return value.replace(tzinfo=pytz.UTC).astimezone(eastern)


def format_datetime(starts, ends):
    now = datetime.utcnow()
    if now > starts:
        if now < ends:
            return 'Ends in %s' % timeuntil(ends)
        return 'Ended %s' % timesince(ends)

    when = timeuntil(starts)
    if when == 'in 1 day':
        when = 'tomorrow'
    when += ', at %s' % convert_pycon_dt(starts).strftime('%I:%M %p')
    return 'Starts %s' % when


def timeuntil(value):
    if not value:
        return 'Never'
    if value > datetime.utcnow() + timedelta(days=5):
        return convert_pycon_dt(value).strftime('%A, %B %d')

    return timesince(value)


def better_jsonify(json_obj, status=200):
     response = make_response(json.dumps(json_obj), status)
     response.headers['content-type'] = 'application/json'
     return response
