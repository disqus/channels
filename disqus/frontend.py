"""
disqus.frontend
~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
import logging
import simplejson

from datetime import datetime, timedelta
from flask import session, render_template, redirect, url_for, jsonify
from jinja2 import Markup

from disqus import app, disqusapi, schedule
from disqus.forms import NewThreadForm, NewPostForm
from disqus.models import Thread, Post, Session, User, Category
from disqus.oauth import login_required, api_call
from disqus.utils import timesince, format_datetime, better_jsonify
from disqus.views import posts, users, threads

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
    thread_list = Thread.list(limit=15)

    # category=category_map['General']
    active_talk_list = Session.list_active(limit=10)
    upcoming_talk_list = Session.list_upcoming(limit=10)

    # for thread in thread_list:
    #     thread['createdAt'] = datestr_to_datetime(thread['createdAt'])

    return render_template('landing.html', **{
        'thread_list': thread_list,
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
    thread_list = Thread.list_by_author(author_id=session['auth']['user_id'])

    return render_template('threads/mine.html', thread_list=thread_list)


@app.route('/threads/<thread_id>', methods=['GET', 'POST'])
def thread_details(thread_id):
    form = NewPostForm(get_form_from_session())

    thread = Thread.get(thread_id)

    channel_list = {
        'posts': posts.get_channel_key(posts.get_key(thread_id=thread_id)),
        'participants': users.get_channel_key(users.get_key(thread_id=thread_id)),
        'active_thread_list': threads.get_channel_key(threads.get_key(category_id=Category.get('General')['id'])),
    }

    if int(thread['category']) == app.config['TALK_CATEGORY_ID']:
        pycon_session = schedule[thread['link']]
    else:
        pycon_session = False

    if 'auth' in session:
        my_threads = Thread.list_by_author(author_id=session['auth']['user_id'])[:5]
        channel_list['my_thread_list'] = threads.get_channel_key(threads.get_key(author_id=thread_id))
    else:
        my_threads = None

    post_list = Post.list_by_thread(thread_id)[::-1]

    return render_template('threads/details.html', **{
        'thread': thread,
        'form': form,
        'pycon_session': pycon_session,
        'participant_list': User.list_by_thread(thread_id),
        'my_thread_list': my_threads,
        'active_talk_list': Session.list_active(limit=5),
        'active_thread_list': Thread.list(limit=5),
        'post_list': post_list,
        'channel_list': channel_list,
        'realtime_host': app.config.get('REALTIME_HOST'),
        'current_user': User.get_by_id(session['auth']['user_id'])
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
        return better_jsonify({
            'post': formatted
        }, status=201)
    return better_jsonify({'message': "invalid request"}, status=400)
