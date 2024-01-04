#-----------------------------------------------------------------------
# auth.py
# Author: Bob Dondero, Taylan Aydin
#-----------------------------------------------------------------------

import flask
import os

#-----------------------------------------------------------------------

def _valid_key(passkey):
    stored_admin_key = os.environ.get('ADMIN_KEY')
    if stored_admin_key is None:
        return False
    return passkey == stored_admin_key

#-----------------------------------------------------------------------

def login():
    error_msg = flask.request.args.get('error_msg')
    if error_msg is None:
        error_msg = ''

    html = flask.render_template('login.html',
        error_msg=error_msg)
    response = flask.make_response(html)
    return response

#-----------------------------------------------------------------------

def handle_login():
    passkey = flask.request.form.get('passkey')
    if passkey is None:
        return flask.redirect(
            flask.url_for('login', error_msg='Invalid login'))
    if not _valid_key(passkey):
        return flask.redirect(
            flask.url_for('login', error_msg='Invalid login'))
    original_url = flask.session.get('original_url', '/index')
    response = flask.redirect(original_url)
    flask.session['username'] = 'admin_talentsiv'
    return response

#-----------------------------------------------------------------------

def logout():
    flask.session.clear()
    html_code = flask.render_template('loggedout.html')
    response = flask.make_response(html_code)
    return response

#-----------------------------------------------------------------------

def authenticate():
    username = flask.session.get('username')
    if username is None:
        response = flask.redirect(flask.url_for('login'))
        flask.session['original_url'] = flask.request.url
        flask.abort(response)
    return username
