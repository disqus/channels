class DefaultConfig(object):
    DB = {
        'engine': 'nydus.db.backends.redis.Redis',
        'router': 'nydus.db.routers.redis.PartitionRouter',
        'hosts': {
            0: {},
        },
    }
    SITE_NAME = 'PyCon 2012'
    SECRET_KEY = '\x92\x99\x1d\x9c\x95\xb8~\x8b\xf8k{\x90oX\t\x87\xd9)2i\xf5\x0c\xd4k'
    DISQUS_PUBLIC = None
    DISQUS_SECRET = None
    DISQUS_FORUM = None
    DEBUG = True
    TALK_CATEGORY_ID = 1330567
