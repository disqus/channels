"""
disqus.oauth
~~~~~~~~~~~~

:copyright: (c) 2012 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import functools
import simplejson
import urllib
import urllib2

from disqusapi import InvalidAccessToken
from flask import url_for, request, redirect, session

from disqus.app import app, disqusapi


class Logout(Exception):
    pass


def get_access_token():
    if 'auth' in session:
        return session['auth']['access_token']
    return None


def api_call(func, **kwargs):
    access_token = get_access_token()
    try:
        if access_token:
            result = func(access_token=access_token, **kwargs)
        else:
            result = func(**kwargs)
    except InvalidAccessToken:
        raise Logout
    return result


@app.errorhandler(Logout)
def logout_handler(error):
    try:
        del session['auth']
    except KeyError:
        pass
    return redirect(url_for('oauth_authorize'))


def login_required(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if 'auth' not in session:
            session['postauth'] = {
                'url': request.url,
                'form': request.form
            }
            return redirect(url_for('oauth_authorize'))
        return func(*args, **kwargs)
    return wrapped


@app.route('/logout', methods=['GET'])
def logout():
    if 'auth' in session:
        del session['auth']
    return redirect('/')


@app.route('/oauth/authorize/')
def oauth_authorize():
    return redirect('https://disqus.com/api/oauth/2.0/authorize/?%s' % (urllib.urlencode({
        'client_id': disqusapi.public_key,
        'scope': 'read,write',
        'response_type': 'code',
        'redirect_uri': url_for('oauth_callback', _external=True),
    }),))


@app.route('/oauth/callback/')
def oauth_callback():
    from disqus.models import User

    code = request.args.get('code')
    error = request.args.get('error')
    if error or not code:
        # TODO: show error
        return redirect('/?oauth_error=' + error)

    req = urllib2.Request('https://disqus.com/api/oauth/2.0/access_token/', urllib.urlencode({
        'grant_type': 'authorization_code',
        'client_id': disqusapi.public_key,
        'client_secret': disqusapi.secret_key,
        'redirect_uri': url_for('oauth_callback', _external=True),
        'code': code,
    }))

    resp = urllib2.urlopen(req).read()

    data = simplejson.loads(resp)

    session['auth'] = data
    session.permanent = True

    user = api_call(disqusapi.users.details, user=data['user_id'])
    User.save(user)

    if 'postauth' in session:
        url = session['postauth']['url']
        del session['postauth']
    else:
        url = '/'
    return redirect(url)
