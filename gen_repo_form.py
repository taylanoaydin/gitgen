from flask import Flask, render_template, redirect, url_for, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from dotenv import load_dotenv
import os
import createrepo
import secrets
import auth

app = Flask(__name__, template_folder='templates/')
load_dotenv()
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

tokens = {}

class UsernameForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Routes for authentication.

@app.route('/login', methods=['GET'])
def login():
    return auth.login()

@app.route('/handlelogin', methods=['POST'])
def handle_login():
    return auth.handle_login()

@app.route('/logout', methods=['GET'])
def logout():
    return auth.logout()
#---------------------------------------------

def generate_token(testname):
    token = secrets.token_urlsafe()
    tokens[token] = testname
    return token

def validate_token(token, testname):
    return (tokens.pop(token, False) == testname)

@app.route('/get_link', methods=['GET'])
def get_link():
    username = auth.authenticate()
    if username == 'admin_talentsiv':
        testname = request.args.get('testname', '')
        token = generate_token(testname)
        link = url_for('index', token=token, testname=testname, _external=True)
        return link
    else:
        return "You are not authorized to access this page."

def is_token_valid(token):
    """ Check if the token is valid without removing it """
    return token in tokens

@app.route('/', methods=['GET', 'POST'])
def index():
    token = request.args.get('token', '')
    testname = request.args.get('testname', '')
    if not is_token_valid(token):
        return "Invalid or expired link."

    form = UsernameForm()
    if form.validate_on_submit():
        # Only invalidate the token after form is successfully submitted
        if validate_token(token, testname):
            giturl = createrepo.main(testname, form.username.data)
            session['giturl'] = giturl
            return redirect(url_for('success'))
        else:
            return "Invalid or expired link."

    return render_template('index.html', form=form)

@app.route('/success', methods=['GET', 'POST'])
def success():
    giturl = session.get('giturl', None)
    return render_template('success.html', giturl=giturl)


if __name__ == '__main__':
    app.run(host='localhost', debug=True, port=8888)
