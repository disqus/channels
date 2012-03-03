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
        return cls.cache[name]

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
            'posts': thread['posts'],
        }

    @classmethod
    def save(cls, thread):
        dt = datestr_to_datetime(thread['createdAt'])
        thread['createdAt'] = dt
        result = cls.format(thread)
        score = dt.strftime('%s.%m')
        threads.add(result, score)
        threads.add_to_set(result['id'], score, category_id=thread['category'])
        threads.add_to_set(result['id'], thread['posts'], _key='posts', category_id=thread['category'])
        return result

    @classmethod
    def get(cls, thread_id):
        result = threads.get(thread_id)
        if result is None:
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
                score = thread['createdAt'].strftime('%s.%m')
                threads.add_to_set(thread['id'], score, author_id=author_id)
            result.reverse()

        return result

    @classmethod
    def list(cls, offset=0, limit=100):
        result = threads.list(category_id=Category.get('General')['id'], offset=offset, limit=limit)
        if result is None:
            result = []
            for thread in disqusapi.threads.list(forum=app.config['DISQUS_FORUM'], category=Category.get('General')['id'], method='GET'):
                result.append(Thread.save(thread))
            result.reverse()

        return result


class Session:
    @classmethod
    def list_active(cls, offset=0, limit=100):
        start = datetime.utcnow() - timedelta(minutes=10)
        end = start + timedelta(minutes=20)
        thread_ids = []
        for talk in sorted(schedule.itervalues(), key=lambda x: x['start']):
            if talk['start'] > start and talk['start'] < end:
                thread_ids.append(talk['disqus:thread']['id'])

        if not thread_ids:
            return []

        thread_ids = thread_ids[:limit]

        result = threads.get_many(thread_ids)
        missing_thread_ids = [t for t, v in result.iteritems() if not v]
        if missing_thread_ids:
            thread_list = disqusapi.threads.list(thread=missing_thread_ids, forum=app.config['DISQUS_FORUM'])
            for thread in thread_list:
                result[thread['id']] = Thread.save(thread)

        return [result[t] for t in thread_ids if t in result]

    @classmethod
    def list_upcoming(cls, offset=0, limit=100):
        start = datetime.utcnow() + timedelta(minutes=15)
        # end = start + timedelta(minutes=30)
        thread_ids = []
        for talk in schedule.itervalues():
            if talk['start'] > start:  # and talk['start'] < end:
                thread_ids.append(talk['disqus:thread']['id'])

        if not thread_ids:
            return []

        thread_ids = thread_ids[:limit]

        result = threads.get_many(thread_ids)
        missing_thread_ids = [t for t, v in result.iteritems() if not v]
        if missing_thread_ids:
            thread_list = disqusapi.threads.list(thread=missing_thread_ids, forum=app.config['DISQUS_FORUM'])
            for thread in thread_list:
                result[thread['id']] = Thread.save(thread)

        return [result[t] for t in thread_ids if t in result]


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
    def save(cls, post, incr_posts=True):
        dt = datestr_to_datetime(post['createdAt'])
        post['createdAt'] = dt
        result = cls.format(post)
        score = dt.strftime('%s.%m')

        posts.add(result, score, thread_id=post['thread'])

        if incr_posts:
            threads.incr_counter(post['thread'], 'posts', 1)
            threads.incr_in_set(post['thread'], 1, _key='posts', category_id=Thread.get(post['thread'])['category'])

        user = User.save(post['author'])
        users.add_to_set(user['id'], score, thread_id=post['thread'])
        threads.add_to_set(post['thread'], score, author_id=post['author'])

        return result

    @classmethod
    def list_by_thread(cls, thread_id, offset=0, limit=100):
        result = posts.list(thread_id=thread_id, offset=offset, limit=limit)
        if result is None:
            result = []
            paginator = Paginator(disqusapi.threads.listPosts, thread=thread_id)
            for idx, post in enumerate(paginator):
                result.append(cls.save(post, incr_posts=False))

        return result
