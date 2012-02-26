import cPickle as pickle
import datetime
import pytz
import simplejson as json
import urllib
from disqus import app, disqusapi
from disqusapi import Paginator

TALK_CATEGORY_NAME = 'Talk'
talk_category_id = False


def api_args(**kwargs):
    base = dict(
        forum=app.config['DISQUS_FORUM'],
        access_token=app.config['DISQUS_ACCESS_TOKEN']
    )
    return dict(base.items() + kwargs.items())


def api(method, *args, **kwargs):
    return method(*args, **api_args(**kwargs))


print 'Trying to find %s category in existing categories...' % TALK_CATEGORY_NAME
for existing_category in api(disqusapi.categories.list):
    if existing_category['title'] == TALK_CATEGORY_NAME:
        talk_category_id = existing_category['id']

if not talk_category_id:
    print "Couldn't find it, adding it..."
    new_category = api(disqusapi.categories.create, title=TALK_CATEGORY_NAME)
    talk_category_id = new_category['id']


print "Downloading list of existing threads..."
paginator = Paginator(disqusapi.threads.list, **api_args(category=talk_category_id))
existing_urls = dict((t['link'], t) for t in paginator)

print "%s existing threads found!" % len(existing_urls)

print 'Downloading and processing sessionlist...'
schedule = json.loads(urllib.urlopen('https://us.pycon.org/2012/schedule/json/').read())
schedule = [s for s in schedule if s.get('url')]

for talk in schedule:
    print ' - Processing session %s' % talk['title']

    for key in ('start', 'end', 'last_updated'):
        talk[key] = datetime.datetime(*map(int, talk[key][0:6]))

    if talk['url'] not in existing_urls:
        args = dict(
            forum=app.config['DISQUS_FORUM'],
            title=talk['title'].encode('utf-8'),
            url=talk['url'],
            date=talk['start'].isoformat(),
            category=talk_category_id,
            message=talk['description'].encode('utf-8')
        )

        thread = api(disqusapi.threads.create, **args)
    else:
        thread = existing_urls[talk['url']]
    talk['disqus:thread'] = thread

print 'Saving sessions to disk'
with open('sessions.pickle', 'wb') as f:
    pickle.dump(schedule, f, pickle.HIGHEST_PROTOCOL)


print "ALL DONE!"
