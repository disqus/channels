import urllib
import simplejson as json
import datetime
from disqus import app, disqusapi
from disqusapi import Paginator
from disqus.oauth import api_call
import codecs

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


for existing_category in api(disqusapi.categories.list):
    if existing_category['title'] == TALK_CATEGORY_NAME:
        talk_category_id = existing_category['id']

if not talk_category_id:
    new_category = api(disqusapi.categories.create, title=TALK_CATEGORY_NAME)
    talk_category_id = new_category['id']


paginator = Paginator(disqusapi.threads.list, **api_args(category=talk_category_id))
existing_urls = [thread['link'] for thread in paginator]

try:
    io = open('schedule.json')
except IOError:
    url = urllib.urlopen('https://us.pycon.org/2012/schedule/json/')
    io = open('schedule.json', 'w')
    io.write(url.read())
    io.close()
    io = open('schedule.json')


schedule = json.loads(io.read())

for talk in schedule:
    if not talk['url'] or talk['url'] in existing_urls:
        continue

    datetime_args = map(int, talk['start'][0:6])

    args = dict(
        forum=app.config['DISQUS_FORUM'],
        title=talk['title'].encode('utf-8'),
        url=talk['url'],
        date=datetime.datetime(*datetime_args).isoformat(),
        category=talk_category_id,
        message=talk['description'].encode('utf-8')
    )

    api(disqusapi.threads.create, **args)
