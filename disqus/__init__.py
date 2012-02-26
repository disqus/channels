"""
disqus
~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

__all__ = ('app', 'db')

from flask import Flask
import cPickle as pickle
from disqus.coffee import coffee


def init_database(app):
    from nydus.db import create_cluster

    app.config.setdefault('DB', {})

    return create_cluster(app.config['DB'])


def init_disqus(app):
    import disqusapi

    return disqusapi.DisqusAPI(app.config['DISQUS_SECRET'], app.config['DISQUS_PUBLIC'])


def init_publisher(app):
    from redis import Redis

    server = Redis(**app.config['PUBLISHER'])

    return server

# Init Flask app
app = Flask(__name__)

# Build configuration
app.config.from_object('disqus.conf.DefaultConfig')
app.config.from_pyfile('local_settings.py', silent=True)
app.config.from_envvar('DISQUS_SETTINGS', silent=True)

if app.config.get('USE_NODE'):
    coffee(app)

# Init database (Redis)
db = init_database(app)

# Init API bindings
disqusapi = init_disqus(app)

# Init Redis publisher
publisher = init_publisher(app)

schedule = dict((s['url'], s) for s in pickle.load(open('sessions.pickle')))
print ' * Schedule loaded'

from disqus.frontend import *
from disqus.oauth import *

if __name__ == '__main__':
    app.run()
