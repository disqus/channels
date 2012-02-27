"""
disqus.models
~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from datetime import datetime, timedelta
from disqusapi import Paginator
from flask import session

from disqus import app, disqusapi, schedule
from disqus.oauth import api_call
from disqus.utils import datestr_to_datetime, from_cache
from disqus.views import threads, posts


class Category:
    @staticmethod
    def list():
        return list(disqusapi.categories.list(forum=app.config['DISQUS_FORUM'], method='GET', limit=100))

    @staticmethod
    def get(name):
        return Category.cache['General']

Category.cache = dict((c['title'], c) for c in from_cache(Category.list))


class Thread:
    @staticmethod
    def format(thread):
        return {
            'id': thread['id'],
            'title': thread['title'],
            'createdAtISO': thread['createdAt'].isoformat(),
            'category': thread['category'],
            'link': thread['link'],
        }

    @staticmethod
    def save(thread):
        dt = datestr_to_datetime(thread['createdAt'])
        thread['createdAt'] = dt
        result = Thread.format(thread)
        score = dt.strftime('%s.%m')
        threads.add(result, score)
        threads.add_to_set(result['id'], score, author_id=thread['author'])
        threads.add_to_set(result['id'], score, category_id=thread['category'])
        return result

    @staticmethod
    def get_thread(thread_id):
        result = threads.get(thread_id)
        if not result:
            thread = disqusapi.threads.details(thread=thread_id, forum=app.config['DISQUS_FORUM'])
            result = Thread.save(thread)
        return result

    @staticmethod
    def list_by_author(author_id, offset=0, limit=100):
        assert author_id == session['auth']['id']
        result = threads.list(author_id=author_id, offset=offset, limit=limit)
        if not result:
            result = []
            for thread in api_call(disqusapi.users.listActiveThreads, forum=app.config['DISQUS_FORUM'], method='GET'):
                result.append(Thread.save(thread))
            result.reverse()

        return result

    @staticmethod
    def list_active():
        return list(disqusapi.threads.listHot(forum=app.config['DISQUS_FORUM'], category=Category.get('General')['id'], method='GET', limit=10))


class Session:
    @staticmethod
    def list_active():
        start = datetime.utcnow() - timedelta(minutes=10)
        end = start + timedelta(minutes=20)
        talk_urls = []
        for talk in sorted(schedule.itervalues(), key=lambda x: x['start']):
            if talk['start'] > start and talk['start'] < end:
                talk_urls.append(talk['url'])

        if not talk_urls:
            return []

        return list(disqusapi.threads.list(forum=app.config['DISQUS_FORUM'], thread=['link:%s' % s for s in talk_urls]))

    @staticmethod
    def list_upcoming():
        start = datetime.utcnow() + timedelta(minutes=15)
        # end = start + timedelta(minutes=30)
        talk_urls = []
        for talk in schedule.itervalues():
            if talk['start'] > start:  # and talk['start'] < end:
                talk_urls.append(talk['url'])

        if not talk_urls:
            return []

        return list(disqusapi.threads.list(forum=app.config['DISQUS_FORUM'], thread=['link:%s' % s for s in talk_urls[:10]]))


class Post:
    @staticmethod
    def format(post):
        return {
            'id': post['id'],
            'avatar': post['author']['avatar']['cache'],
            'name': post['author']['username'],
            'createdAtISO': post['createdAt'].isoformat(),
            'message': post['message']
        }

    @staticmethod
    def save(post):
        dt = datestr_to_datetime(post['createdAt'])
        post['createdAt'] = dt
        result = Post.format(post)
        posts.add(result, dt.strftime('%s.%m'), thread_id=post['thread'])
        return result

    @staticmethod
    def list_by_thread(thread_id, offset=0, limit=100):
        result = posts.list(thread_id=thread_id, offset=offset, limit=limit)
        if not result:
            result = []
            paginator = Paginator(disqusapi.threads.listPosts, thread=thread_id)
            for idx, post in enumerate(paginator):
                result.append(Post.save(post))

        return result
