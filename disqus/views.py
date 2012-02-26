from disqus import db


class View(object):
    def __init__(self, redis, name, datekey='createdAt'):
        self.ns = 'view:%s' % name
        self.redis = redis
        self.datekey = datekey

    def add(self, data, score, **kwargs):
        self.redis.zadd(self.get_key(**kwargs), data['id'], float(score))

    def remove(self, data, **kwargs):
        self.redis.zrem(self.get_key(**kwargs), data['id'])

    def list(self, offset=0, limit=-1, **kwargs):
        id_list = self.redis.zrevrange(self.get_key(**kwargs), offset, limit)
        obj_cache = {}
        with self.redis.map() as conn:
            for id in id_list:
                key = self.get_obj_key(id)
                obj_cache[id] = conn.get(key)

        results = filter(None, [obj_cache.get(t) for t in id_list])

        return results

    def flush(self, **kwargs):
        self.redis.delete(self.get_key(**kwargs))

    def get_key(self, **kwargs):
        kwarg_str = '&'.join('%s=%s' % (k, v) for k, v in sorted(kwargs.items()))

        return '%s:%s' % (self.ns, kwarg_str)

    def get_obj_key(self, id):
        return '%s:objects:%s' % (self.ns, id)

posts = View(db, 'posts')
