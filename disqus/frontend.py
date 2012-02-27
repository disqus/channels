"""
disqus.frontend
~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
import itertools
import logging
import simplejson

from datetime import datetime, timedelta
from flask import session, render_template, redirect, url_for, jsonify
from jinja2 import Markup

from disqusapi import Paginator
from disqus import app, disqusapi, schedule
from disqus.forms import NewThreadForm, NewPostForm
from disqus.oauth import login_required, api_call
from disqus.utils import from_cache, timesince, format_datetime, datestr_to_datetime
from disqus.views import posts, threads


logger = logging.getLogger(__name__)


def get_form_from_session():
    if 'postauth' in session:
        postauth = session['postauth']
        del session['postauth']
        return postauth['form']


def format_thread(thread):
    return {
        'id': thread['id'],
        'title': thread['title'],
        'createdAtISO': thread['createdAt'].isoformat(),
        'category': thread['category'],
        'link': thread['link'],
    }


def format_post(post):
    return {
        'id': post['id'],
        'avatar': post['author']['avatar']['cache'],
        'name': post['author']['username'],
        'createdAtISO': post['createdAt'].isoformat(),
        'message': post['message']
    }


def get_active_threads():
    return list(disqusapi.threads.listHot(forum=app.config['DISQUS_FORUM'], category=category_map['General']['id'], method='GET', limit=10))


def get_categories():
    return list(disqusapi.categories.list(forum=app.config['DISQUS_FORUM'], method='GET', limit=100))

category_map = dict((c['title'], c) for c in from_cache(get_categories))


def get_active_talks():
    start = datetime.utcnow() - timedelta(minutes=10)
    end = start + timedelta(minutes=20)
    talk_urls = []
    for talk in sorted(schedule.itervalues(), key=lambda x: x['start']):
        if talk['start'] > start and talk['start'] < end:
            talk_urls.append(talk['url'])

    if not talk_urls:
        return []

    return list(disqusapi.threads.list(forum=app.config['DISQUS_FORUM'], thread=['link:%s' % s for s in talk_urls]))


def get_upcoming_talks():
    start = datetime.utcnow() + timedelta(minutes=15)
    # end = start + timedelta(minutes=30)
    talk_urls = []
    for talk in schedule.itervalues():
        if talk['start'] > start:  # and talk['start'] < end:
            talk_urls.append(talk['url'])

    if not talk_urls:
        return []

    return list(disqusapi.threads.list(forum=app.config['DISQUS_FORUM'], thread=['link:%s' % s for s in talk_urls[:10]]))


def get_thread_posts(thread_id, offset=0, limit=100):
    result = posts.list(thread_id=thread_id, offset=offset, limit=limit)
    if not result:
        result = []
        paginator = Paginator(disqusapi.threads.listPosts, thread=thread_id)
        for idx, post in enumerate(paginator):
            dt = datestr_to_datetime(post['createdAt'])
            post['createdAt'] = dt
            data = format_post(post)
            posts.add(data, dt.strftime('%s.%m'), thread_id=thread_id)
            result.append(data)

    return result


def get_thread(thread_id):
    result = threads.get(thread_id)
    if not result:
        thread = disqusapi.threads.details(thread=thread_id, forum=app.config['DISQUS_FORUM'])
        dt = datestr_to_datetime(thread['createdAt'])
        thread['createdAt'] = dt
        result = format_thread(thread)
        score = dt.strftime('%s.%m')
        threads.add(result, score)
        threads.add_to_set(result['id'], score, author_id=thread['author'])
        threads.add_to_set(result['id'], score, category_id=thread['category'])
    return result


@app.context_processor
def inject_auth():
    return dict(user=session.get('auth'))


@app.context_processor
def inject_config():
    return dict(SITE_NAME=app.config['SITE_NAME'])


@app.template_filter('is_new')
def is_new_filter(date):
    return date > datetime.utcnow() - timedelta(days=1)


@app.template_filter('as_json')
def as_json_filter(data):
    return Markup(simplejson.dumps(data))

app.template_filter('timesince')(timesince)
app.template_filter('format_datetime')(format_datetime)


@app.route('/', methods=['GET'])
def landing_page():
    active_thread_list = from_cache(get_active_threads)
    active_thread_ids = set(t['id'] for t in active_thread_list)

    thread_list = list(api_call(disqusapi.threads.listByDate, category=category_map['General']['id'], method='GET', limit=20))
    thread_list = [t for t in thread_list if t['id'] not in active_thread_ids][:10]

    # category=category_map['General']
    active_talk_list = from_cache(get_active_talks)
    upcoming_talk_list = from_cache(get_upcoming_talks)

    for thread in itertools.chain(active_thread_list, thread_list):
        thread['createdAt'] = datestr_to_datetime(thread['createdAt'])

    return render_template('landing.html', **{
        'thread_list': thread_list,
        'active_thread_list': active_thread_list,
        'active_talk_list': active_talk_list,
        'upcoming_talk_list': upcoming_talk_list,
    })


@app.route('/threads/new', methods=['GET', 'POST'])
@login_required
def new_thread():
    form = NewThreadForm()
    if form.validate_on_submit():
        thread = api_call(disqusapi.threads.create, title=form.subject.data, forum=app.config['DISQUS_FORUM'])
        dt = datestr_to_datetime(thread['createdAt'])
        thread['createdAt'] = dt
        score = dt.strftime('%s.%m')
        threads.add(format_thread(thread), score)
        threads.add_to_set(thread['id'], score, author_id=thread['author'])
        threads.add_to_set(thread['id'], score, category_id=thread['category'])
        return redirect(url_for('thread_details', thread_id=thread['id']))

    return render_template('threads/new.html', form=form)


@app.route('/threads/by/date', methods=['GET'])
def threads_by_date():
    thread_list = api_call(disqusapi.threads.listByDate, forum=app.config['DISQUS_FORUM'], method='GET')

    for thread in thread_list:
        thread['createdAt'] = datestr_to_datetime(thread['createdAt'])

    return render_template('threads/by_date.html', thread_list=thread_list)


@app.route('/threads/by/activity', methods=['GET'])
def threads_by_activity():
    thread_list = api_call(disqusapi.threads.listHot, forum=app.config['DISQUS_FORUM'], method='GET')

    for thread in thread_list:
        thread['createdAt'] = datestr_to_datetime(thread['createdAt'])

    return render_template('threads/by_activity.html', thread_list=thread_list)


@app.route('/threads/mine', methods=['GET'])
@login_required
def my_threads():
    thread_list = api_call(disqusapi.users.listActiveThreads, forum=app.config['DISQUS_FORUM'], method='GET')

    for thread in thread_list:
        thread['createdAt'] = datestr_to_datetime(thread['createdAt'])

    return render_template('threads/mine.html', thread_list=thread_list)


@app.route('/threads/<thread_id>', methods=['GET', 'POST'])
def thread_details(thread_id):
    form = NewPostForm(get_form_from_session())

    thread = get_thread(thread_id)

    if int(thread['category']) == app.config['TALK_CATEGORY_ID']:
        pycon_session = schedule[thread['link']]
    else:
        pycon_session = False

    return render_template('threads/details.html', **{
        'thread': thread,
        'form': form,
        'pycon_session': pycon_session,
        'active_talk_list': from_cache(get_active_talks)[:5],
        'active_thread_list': from_cache(get_active_threads)[:5],
        'post_list': get_thread_posts(thread_id)[::-1]
    })


@app.route('/posts/<thread_id>.json', methods=['GET'])
def get_posts(thread_id):
    return jsonify({
        'post_list': get_thread_posts(thread_id)[::-1]
    })


@app.route('/threads/<thread_id>/reply', methods=['GET', 'POST'])
@login_required
def new_post(thread_id):
    form = NewPostForm()
    if form.validate_on_submit():
        post = api_call(disqusapi.posts.create, thread=thread_id, message=form.message.data)
        dt = datestr_to_datetime(post['createdAt'])
        post['createdAt'] = dt
        posts.add(format_post(post), dt.strftime('%s.%m'), thread_id=thread_id)

    return redirect(url_for('thread_details', thread_id=thread_id))
