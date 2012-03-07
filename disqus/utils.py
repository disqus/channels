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
from disqus.app import db
from flask import make_response

logger = logging.getLogger(__name__)

ALPHABET = "_-^~0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


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


pacific = pytz.timezone('America/Los_Angeles')


def convert_pycon_dt(value):
    return value.replace(tzinfo=pytz.UTC).astimezone(pacific)


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


def base62_encode(num, alphabet=ALPHABET):
    """Encode a number in Base X

    `num`: The number to encode
    `alphabet`: The alphabet to use for encoding
    """
    num = int(num)
    if (num == 0):
        return alphabet[0]
    arr = []
    base = len(alphabet)
    while num:
        rem = num % base
        num = num // base
        arr.append(alphabet[rem])
    arr.reverse()
    return ''.join(arr)


def base62_decode(string, alphabet=ALPHABET):
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1

    return num
