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
from disqus.views import threads, posts, users


class User:
    @classmethod
    def format(cls, user):
        return {
            'id': user['id'],
            'avatar': user['avatar']['cache'],
            'name': user['username'],
        }

    @classmethod
    def save(cls, user):
        result = cls.format(user)
        users.add(result, datetime.utcnow().strftime('%s.%m'))
        return result

    @classmethod
    def list_by_thread(cls, thread_id, offset=0, limit=100):
        return users.list(thread_id=thread_id, offset=offset, limit=limit)


class Category:
    @classmethod
    def list(cls):
        return list(disqusapi.categories.list(forum=app.config['DISQUS_FORUM'], method='GET', limit=100))

    @classmethod
    def get(cls, name):
        return cls.cache['General']

Category.cache = dict((c['title'], c) for c in from_cache(Category.list))


class Thread:
    @classmethod
    def format(cls, thread):
        return {
            'id': thread['id'],
            'title': thread['title'],
            'createdAtISO': thread['createdAt'].isoformat(),
            'category': thread['category'],
            'link': thread['link'],
        }

    @classmethod
    def save(cls, thread):
        dt = datestr_to_datetime(thread['createdAt'])
        thread['createdAt'] = dt
        result = cls.format(thread)
        score = dt.strftime('%s.%m')
        threads.add(result, score)
        threads.add_to_set(result['id'], score, author_id=thread['author'])
        threads.add_to_set(result['id'], score, category_id=thread['category'])
        return result

    @classmethod
    def get(cls, thread_id):
        result = threads.get(thread_id)
        if not result:
            thread = disqusapi.threads.details(thread=thread_id, forum=app.config['DISQUS_FORUM'])
            result = cls.save(thread)
        return result

    @classmethod
    def list_by_author(cls, author_id, offset=0, limit=100):
        assert author_id == session['auth']['user_id']
        result = threads.list(author_id=author_id, offset=offset, limit=limit)
        if result is None:
            result = []
            for thread in api_call(disqusapi.users.listActiveThreads, forum=app.config['DISQUS_FORUM'], method='GET'):
                result.append(Thread.save(thread))
            result.reverse()

        return result

    @classmethod
    def list_active(cls):
        return list(disqusapi.threads.listHot(forum=app.config['DISQUS_FORUM'], category=Category.get('General')['id'], method='GET', limit=10))


class Session:
    @classmethod
    def list_active(cls):
        start = datetime.utcnow() - timedelta(minutes=10)
        end = start + timedelta(minutes=20)
        talk_urls = []
        for talk in sorted(schedule.itervalues(), key=lambda x: x['start']):
            if talk['start'] > start and talk['start'] < end:
                talk_urls.append(talk['url'])

        if not talk_urls:
            return []

        return list(disqusapi.threads.list(forum=app.config['DISQUS_FORUM'], thread=['link:%s' % s for s in talk_urls]))

    @classmethod
    def list_upcoming(cls):
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
    @classmethod
    def format(cls, post):
        return {
            'id': post['id'],
            'avatar': post['author']['avatar']['cache'],
            'name': post['author']['username'],
            'createdAtISO': post['createdAt'].isoformat(),
            'message': post['message']
        }

    @classmethod
    def save(cls, post):
        dt = datestr_to_datetime(post['createdAt'])
        post['createdAt'] = dt
        result = cls.format(post)
        score = dt.strftime('%s.%m')
        posts.add(result, score, thread_id=post['thread'])
        user = User.save(post['author'])
        users.add_to_set(user['id'], score, thread_id=post['thread'])
        return result

    @classmethod
    def list_by_thread(cls, thread_id, offset=0, limit=100):
        result = posts.list(thread_id=thread_id, offset=offset, limit=limit)
        if not result:
            result = []
            paginator = Paginator(disqusapi.threads.listPosts, thread=thread_id)
            for idx, post in enumerate(paginator):
                result.append(cls.save(post))

        return result
