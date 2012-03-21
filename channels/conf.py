"""
channels.conf
~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""


class DefaultConfig(object):
    # Redis data store (Nydus compatible settings)
    DB = {
        'engine': 'nydus.db.backends.redis.Redis',
        'router': 'nydus.db.routers.redis.PartitionRouter',
        'hosts': {
            0: {},
        },
    }
    # Redis pub sub settings
    PUBLISHER = {

    }
    SITE_NAME = 'Channels'
    SECRET_KEY = None
    DISQUS_PUBLIC = None
    DISQUS_SECRET = None
    DISQUS_FORUM = None
    USE_NODE = False
    DEBUG = True
    TALK_CATEGORY_ID = 1330567
    CSRF_ENABLED = False
    REALTIME_HOST = 'http://localhost:3000'
    USE_MARKDOWN = True
    DING_ENABLED = True

    DEPLOY_HOSTS = []
    DEPLOY_KEY = ''
    DEPLOY_USER = 'channels'
