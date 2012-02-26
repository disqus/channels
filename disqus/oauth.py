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

from disqus import app, disqusapi


class Logout(Exception):
    pass


def api_call(func, **kwargs):
    try:
        if 'auth' in session:
            result = func(access_token=session['auth']['access_token'], **kwargs)
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
            session['auth-redirect'] = request.url
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
    code = request.args.get('code')
    error = request.args.get('error')
    if error or not code:
        # TODO: show error
        return redirect('/')

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

    url = session.get('auth-redirect')
    if url:
        del session['auth-redirect']
    else:
        url = '/'
    return redirect(url)
