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
from flaskext.wtf import Form, Required, TextField, TextAreaField

from disqus import app, disqusapi, schedule
from disqus.oauth import login_required, api_call
from disqus.utils import from_cache, timesince

logger = logging.getLogger(__name__)


def get_active_threads():
    return list(disqusapi.threads.listHot(forum=app.config['DISQUS_FORUM'], category=category_map['General']['id'], method='GET', limit=10))


def get_categories():
    return list(disqusapi.categories.list(forum=app.config['DISQUS_FORUM'], method='GET', limit=100))

category_map = dict((c['title'], c) for c in from_cache(get_categories))


def get_active_talks():
    start = datetime.now() - timedelta(minutes=10)
    end = start + timedelta(minutes=20)
    talk_urls = []
    for talk in sorted(schedule.itervalues(), key=lambda x: x['start']):
        if talk['start'] > start and talk['start'] < end:
            talk_urls.append(talk['url'])

    if not talk_urls:
        return []

    return list(disqusapi.threads.list(forum=app.config['DISQUS_FORUM'], thread=['link:%s' % s for s in talk_urls]))


def get_upcoming_talks():
    start = datetime.now() + timedelta(minutes=15)
    # end = start + timedelta(minutes=30)
    talk_urls = []
    for talk in schedule.itervalues():
        if talk['start'] > start:  # and talk['start'] < end:
            talk_urls.append(talk['url'])

    if not talk_urls:
        return []

    return list(disqusapi.threads.list(forum=app.config['DISQUS_FORUM'], thread=['link:%s' % s for s in talk_urls[:10]]))


@app.context_processor
def inject_auth():
    return dict(user=session.get('auth'))


@app.context_processor
def inject_config():
    return dict(SITE_NAME=app.config['SITE_NAME'])


@app.template_filter('is_new')
def is_new_filter(date):
    return date > datetime.now() - timedelta(days=1)

app.template_filter('timesince')(timesince)


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
        thread['createdAt'] = datetime.strptime(thread['createdAt'], '%Y-%m-%dT%H:%M:%S')

    return render_template('landing.html', **{
        'thread_list': thread_list,
        'active_thread_list': active_thread_list,
        'active_talk_list': active_talk_list,
        'upcoming_talk_list': upcoming_talk_list,
    })


class NewThreadForm(Form):
    subject = TextField('Subject', [Required()])


class NewPostForm(Form):
    message = TextAreaField('Message', [Required()])


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
        thread['createdAt'] = datetime.strptime(thread['createdAt'], '%Y-%m-%dT%H:%M:%S')

    return render_template('threads/by_date.html', thread_list=thread_list)


@app.route('/threads/by/activity', methods=['GET'])
def threads_by_activity():
    thread_list = api_call(disqusapi.threads.listHot, forum=app.config['DISQUS_FORUM'], method='GET')

    for thread in thread_list:
        thread['createdAt'] = datetime.strptime(thread['createdAt'], '%Y-%m-%dT%H:%M:%S')

    return render_template('threads/by_activity.html', thread_list=thread_list)


@app.route('/threads/mine', methods=['GET'])
@login_required
def my_threads():
    thread_list = api_call(disqusapi.users.listActiveThreads, forum=app.config['DISQUS_FORUM'], method='GET')

    for thread in thread_list:
        thread['createdAt'] = datetime.strptime(thread['createdAt'], '%Y-%m-%dT%H:%M:%S')

    return render_template('threads/mine.html', thread_list=thread_list)


@app.route('/threads/<thread_id>', methods=['GET', 'POST'])
def thread_details(thread_id):
    form = NewPostForm()

    thread = api_call(disqusapi.threads.details, thread=thread_id)

    thread['createdAt'] = datetime.strptime(thread['createdAt'], '%Y-%m-%dT%H:%M:%S')

    post_list = api_call(disqusapi.threads.listPosts, thread=thread_id)[::-1]
    for post in post_list:
        post['createdAt'] = datetime.strptime(post['createdAt'], '%Y-%m-%dT%H:%M:%S')

    if int(thread['category']) == app.config['TALK_CATEGORY_ID']:
        pycon_session = schedule[thread['link']]
    else:
        pycon_session = False

    return render_template('threads/details.html', thread=thread, post_list=post_list, form=form, pycon_session=pycon_session)


@app.route('/threads/<thread_id>/reply', methods=['GET', 'POST'])
@login_required
def new_post(thread_id):
    form = NewPostForm()
    if form.validate_on_submit():
        post = api_call(disqusapi.posts.create, thread=thread_id, message=form.message.data)

    return redirect(url_for('thread_details', thread_id=thread_id))
