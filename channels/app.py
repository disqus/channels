"""
channels.app
~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

__all__ = ('app', 'db')

import cPickle as pickle
from channels.contrib.coffee import coffee
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix


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

app.wsgi_app = ProxyFix(app.wsgi_app)

# Build configuration
app.config.from_object('channels.conf.DefaultConfig')
app.config.from_pyfile('local_settings.py', silent=True)
app.config.from_envvar('CHANNELS_SETTINGS', silent=True)

if app.config.get('SENTRY_DSN'):
    from raven.contrib.flask import Sentry
    sentry = Sentry(app)
else:
    sentry = None

if app.config.get('USE_NODE'):
    import os.path

    coffee_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'node_modules/.bin/coffee')
    coffee(app, coffee_path)

# Init database (Redis)
db = init_database(app)

# Init API bindings
disqusapi = init_disqus(app)

# Init Redis publisher
publisher = init_publisher(app)

schedule = dict((s['url'], s) for s in pickle.load(open('sessions.pickle')))
print ' * Schedule loaded'

from embedly import Embedly


def get_client(key):
    if not key:
        return None
    return Embedly(key)

embedly = get_client(app.config.get('EMBEDLY_KEY'))


from channels.frontend import *
from channels.oauth import *

if __name__ == '__main__':
    app.run()
