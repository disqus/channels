import cPickle as pickle
import urllib
import simplejson as json
import datetime
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
existing_urls = [thread['link'] for thread in paginator]

print "%s existing threads found!" % len(existing_urls)

print 'Downloading and processing sessionlist...'
schedule = json.loads(urllib.urlopen('https://us.pycon.org/2012/schedule/json/').read())
f = open('sessions.pickle', 'w')
pickle.dump(schedule, f, pickle.HIGHEST_PROTOCOL)
f.close()

for talk in schedule:
    print ' - Processing session %s' % talk['title']

    if not talk['url'] or talk['url'] in existing_urls:
        continue

    for key in ('start', 'end', 'last_updated'):
        talk[key] = datetime.datetime(*map(int, talk['start'][0:6]))

    args = dict(
        forum=app.config['DISQUS_FORUM'],
        title=talk['title'].encode('utf-8'),
        url=talk['url'],
        date=talk['start'],
        category=talk_category_id,
        message=talk['description'].encode('utf-8')
    )

    api(disqusapi.threads.create, **args)

print "ALL DONE!"
