"""
disqus.frontend
~~~~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""
from datetime import datetime, timedelta
from flask import session, render_template, flash, redirect, url_for
from flaskext.wtf import Form, Required, TextField, TextAreaField

from disqus import app, disqusapi
from disqus.oauth import login_required, api_call


@app.context_processor
def inject_auth():
    return dict(user=session.get('auth'))


@app.context_processor
def inject_config():
    return dict(SITE_NAME=app.config['SITE_NAME'])


@app.template_filter('is_new')
def is_new_filter(date):
    return date > datetime.now() - timedelta(days=1)


@app.route('/', methods=['GET'])
def landing_page():
    active_thread_list = list(api_call(disqusapi.threads.listHot, forum=app.config['DISQUS_FORUM'], method='GET', limit=5))
    active_thread_ids = set(t['id'] for t in active_thread_list)
    thread_list = list(api_call(disqusapi.threads.listByDate, forum=app.config['DISQUS_FORUM'], method='GET', limit=10))
    thread_list = [t for t in thread_list if t['id'] not in active_thread_ids]

    for thread in thread_list:
        thread['createdAt'] = datetime.strptime(thread['createdAt'], '%Y-%m-%dT%H:%M:%S')

    return render_template('landing.html', thread_list=thread_list, active_thread_list=active_thread_list)


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


@app.route('/threads/updated', methods=['GET'])
def threads_by_date():
    thread_list = api_call(disqusapi.threads.listByDate, forum=app.config['DISQUS_FORUM'], method='GET')

    for thread in thread_list:
        thread['createdAt'] = datetime.strptime(thread['createdAt'], '%Y-%m-%dT%H:%M:%S')

    return render_template('threads/by_date.html', thread_list=thread_list)


@app.route('/threads/liked', methods=['GET'])
def threads_by_likes():
    thread_list = api_call(disqusapi.threads.listMostLiked, forum=app.config['DISQUS_FORUM'], method='GET')

    for thread in thread_list:
        thread['createdAt'] = datetime.strptime(thread['createdAt'], '%Y-%m-%dT%H:%M:%S')

    return render_template('threads/by_likes.html', thread_list=thread_list)


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

    return render_template('threads/details.html', thread=thread, post_list=post_list, form=form)


@app.route('/threads/<thread_id>/reply', methods=['GET', 'POST'])
@login_required
def new_post(thread_id):
    form = NewPostForm()
    if form.validate_on_submit():
        post = api_call(disqusapi.posts.create, thread=thread_id, message=form.message.data)

    return redirect(url_for('thread_details', thread_id=thread_id))
