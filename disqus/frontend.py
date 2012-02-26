"""
disqus.frontend
~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
import itertools
import logging

from datetime import datetime, timedelta
from flask import session, render_template, flash, redirect, url_for

from disqusapi import Paginator
from disqus import app, disqusapi, schedule
from disqus.forms import NewThreadForm, NewPostForm
from disqus.oauth import login_required, api_call
from disqus.utils import from_cache, timesince, format_datetime, datestr_to_datetime
from disqus.views import posts


logger = logging.getLogger(__name__)


def get_form_from_session():
    if 'postauth' in session:
        postauth = session['postauth']
        del session['postauth']
        return postauth['form']


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
            posts.add(post, dt.strftime('%s.%m'), thread_id=thread_id)
            if idx < limit:
                post['createdAt'] = dt
                result.append(post)
    else:
        for post in result:
            post['createdAt'] = datestr_to_datetime(post['createdAt'])

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
        flash("Success")
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

    thread = from_cache(lambda: api_call(disqusapi.threads.details, thread=thread_id),
                        'disqus.frontend.get_thread:%s' % (thread_id,))

    thread['createdAt'] = datestr_to_datetime(thread['createdAt'])

    post_list = get_thread_posts(thread_id)[::-1]

    if int(thread['category']) == app.config['TALK_CATEGORY_ID']:
        pycon_session = schedule[thread['link']]
    else:
        pycon_session = False

    return render_template('threads/details.html', **{
        'thread': thread,
        'post_list': post_list,
        'form': form,
        'pycon_session': pycon_session,
        'active_talk_list': from_cache(get_active_talks)[:5],
        'active_thread_list': from_cache(get_active_threads)[:5],
    })


@app.route('/threads/<thread_id>/reply', methods=['GET', 'POST'])
@login_required
def new_post(thread_id):
    form = NewPostForm()
    if form.validate_on_submit():
        post = api_call(disqusapi.posts.create, thread=thread_id, message=form.message.data)
        dt = datestr_to_datetime(post['createdAt'])
        posts.add(post, dt.strftime('%s.%m'), thread_id=thread_id)

    return redirect(url_for('thread_details', thread_id=thread_id))
