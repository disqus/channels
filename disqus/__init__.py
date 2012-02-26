"""
disqus
~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

__all__ = ('app', 'db')

from flask import Flask
import cPickle as pickle


def init_database(app):
    from nydus.db import create_cluster

    app.config.setdefault('DB', {})

    return create_cluster(app.config['DB'])


def init_disqus(app):
    import disqusapi

    return disqusapi.DisqusAPI(app.config['DISQUS_SECRET'], app.config['DISQUS_PUBLIC'])

# Init Flask app
app = Flask(__name__)

# Build configuration
app.config.from_object('disqus.conf.DefaultConfig')
app.config.from_pyfile('local_settings.py', silent=True)
app.config.from_envvar('DISQUS_SETTINGS', silent=True)

# Init database (Redis)
db = init_database(app)

# Init API bindings
disqusapi = init_disqus(app)

schedule = dict((s['url'], s) for s in pickle.load(open('sessions.pickle')))
print ' * Schedule loaded'

from disqus.frontend import *
from disqus.oauth import *

if __name__ == '__main__':
    app.run()
