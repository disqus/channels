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

from disqus import app, disqusapi, schedule
from disqus.forms import NewThreadForm, NewPostForm
from disqus.models import Thread, Post, Session, Category, User
from disqus.oauth import login_required, api_call
from disqus.utils import from_cache, timesince, format_datetime, datestr_to_datetime, better_jsonify


logger = logging.getLogger(__name__)


def get_form_from_session():
    if 'postauth' in session:
        postauth = session['postauth']
        del session['postauth']
        return postauth['form']


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
    active_thread_list = from_cache(Thread.list_active)
    active_thread_ids = set(t['id'] for t in active_thread_list)

    thread_list = list(api_call(disqusapi.threads.listByDate,
        category=Category.get('Generaly')['id'],
        method='GET',
        limit=20,
    ))
    thread_list = [t for t in thread_list if t['id'] not in active_thread_ids][:10]

    # category=category_map['General']
    active_talk_list = from_cache(Session.list_active)
    upcoming_talk_list = from_cache(Session.list_upcoming)

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
        Thread.save(thread)
        return redirect(url_for('thread_details', thread_id=thread['id']))

    return render_template('threads/new.html', form=form)


@app.route('/threads/mine', methods=['GET'])
@login_required
def my_threads():
    thread_list = Thread.by_author(author_id=session['auth']['id'])

    return render_template('threads/mine.html', thread_list=thread_list)


@app.route('/threads/<thread_id>', methods=['GET', 'POST'])
def thread_details(thread_id):
    form = NewPostForm(get_form_from_session())

    thread = Thread.get(thread_id)

    if int(thread['category']) == app.config['TALK_CATEGORY_ID']:
        pycon_session = schedule[thread['link']]
    else:
        pycon_session = False

    if 'auth' in session:
        my_threads = Thread.list_by_author(author_id=session['auth']['user_id'])[:5]
    else:
        my_threads = None

    post_list = Post.list_by_thread(thread_id)[::-1]

    return render_template('threads/details.html', **{
        'thread': thread,
        'form': form,
        'pycon_session': pycon_session,
        'user_list': User.list_by_thread(thread_id),
        'my_thread_list': my_threads,
        'active_talk_list': from_cache(Session.list_active)[:5],
        'active_thread_list': from_cache(Thread.list_active)[:5],
        'post_list': post_list,
    })


@app.route('/posts/<thread_id>.json', methods=['GET'])
def get_posts(thread_id):
    return jsonify({
        'post_list': Post.list_by_thread(thread_id)[::-1]
    })


@app.route('/threads/<thread_id>/reply', methods=['GET', 'POST'])
@login_required
def new_post(thread_id):
    form = NewPostForm()
    if form.validate_on_submit():
        post = api_call(disqusapi.posts.create, thread=thread_id, message=form.message.data)
        formatted = Post.save(post)
        new_form = NewPostForm()
        return better_jsonify({
            'token': new_form.csrf.data,
            'post': formatted
        }, status=201)
    return better_jsonify({'message': "invalid request"}, status=400)
