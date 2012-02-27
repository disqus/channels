"""
disqus.views
~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
import simplejson

from disqus import db, publisher


class View(object):
    def __init__(self, redis, publisher, name):
        self.ns = 'view:%s' % name
        self.pns = 'channel:%s' % name
        self.redis = redis

    def add(self, data, score, **kwargs):
        """
        Adds an object.

        This will serialize it into the shared object cache, as well
        as add it to the materialized view designated with ``kwargs``.
        """
        json_data = simplejson.dumps(data)

        # Immediately update this object in the shared object cache
        self.redis.set(self.get_obj_key(data['id']), json_data)

        # Update the filtered sorted set (based on kwargs)
        self.add_to_set(data['id'], score, json_data, **kwargs)

    def add_to_set(self, id, score, _data=None, **kwargs):
        """
        Adds an object to a materialized view.
        """
        self.redis.zadd(self.get_key(**kwargs), id, float(score))

        if _data is None:
            _data = self.get(id)

        # Send the notice out to our subscribers that this data
        # was added
        publisher.publish(self.get_channel_key(**kwargs), _data)

    def remove(self, data, **kwargs):
        """
        Removes an object.

        This will only remove it from the materialized view as passed with
        ``kwargs``.
        """
        self.redis.zrem(self.get_key(**kwargs), data['id'])
        self.redis.remove(self.get_obj_key(data['id']))

    def remove_from_set(self, id, **kwargs):
        """
        Removes an object from its materialized view.
        """
        self.redis.zrem(self.get_key(**kwargs), id)

    def get(self, id):
        """
        Fetchs an object from the shared object cache.
        """
        result = self.redis.get(self.get_obj_key(id))
        if result is None:
            return
        return simplejson.loads(result)

    def list(self, offset=0, limit=-1, desc=True, **kwargs):
        """
        Returns a list of objects from the given materialized view.
        """
        if desc:
            func = self.redis.zrevrange
        else:
            func = self.redis.zrange
        id_list = func(self.get_key(**kwargs), offset, limit)
        obj_cache = {}
        with self.redis.map() as conn:
            for id in id_list:
                key = self.get_obj_key(id)
                obj_cache[id] = conn.get(key)

        results = filter(bool, [simplejson.loads(unicode(obj_cache[t])) for t in id_list if obj_cache])

        return results

    def get_key(self, **kwargs):
        kwarg_str = '&'.join('%s=%s' % (k, v) for k, v in sorted(kwargs.items()))

        return '%s:%s' % (self.ns, kwarg_str)

    def get_channel_key(self, **kwargs):
        kwarg_str = '&'.join('%s=%s' % (k, v) for k, v in sorted(kwargs.items()))

        return '%s:%s' % (self.pns, kwarg_str)

    def get_obj_key(self, id):
        return '%s:objects:%s' % (self.ns, id)

posts = View(db, publisher, 'posts')
threads = View(db, publisher, 'threads')
users = View(db, publisher, 'users')
