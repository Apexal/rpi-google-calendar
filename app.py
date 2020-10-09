from db import get_section
from my_google import create_google_credentials, credentials_to_dict, finish_google_flow, start_google_flow
import googleapiclient.discovery
import os
from flask import Flask, abort, flash, g, session, request, render_template, redirect, url_for
from flask_cas import CAS, login_required
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException

# Loads any variables from the .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Initialize CAS authentication on the /cas endpoint
# Adds the /cas/login and /cas/logout routes
cas = CAS(app, '/cas')

# This must be a RANDOM string you generate once and keep secret
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

# Used in templates
app.config['APP_TITLE'] = 'RPI Schedule Google Calendar Importer'

# Must be set to this to use RPI CAS
app.config['CAS_SERVER'] = 'https://cas-auth.rpi.edu/cas'

# What route to go to after logging in
app.config['CAS_AFTER_LOGIN'] = 'index'


@app.before_request
def before_request():
    '''Runs before every request.'''

    # Everything added to g can be accessed during the request
    g.logged_in = cas.username is not None


@app.context_processor
def add_template_locals():
    '''Add values to be available to every rendered template.'''

    # Add keys here
    return {
        'logged_in': g.logged_in,
        'username': cas.username
    }


@app.route('/')
@login_required
def index():
    '''The homepage.'''
    if 'sections' not in session:
        session['sections'] = dict()

    print(session['sections'])

    return render_template('index.html', crns=session['sections'].keys(), sections=session['sections'])


@app.route('/add')
@login_required
def add_section():
    crn = request.args.get('crn')

    if crn in session['sections'].keys():
        flash('Already added that CRN', 'warning')
    else:
        # Get section
        section = get_section('202009', crn)
        if section is None:
            # Invalid CRN
            flash('Invalid crn', 'danger')
        else:
            session['sections'][crn] = section
            session.modified = True

    return redirect('/')


@app.route('/remove')
@login_required
def remove_section():
    crn = request.args.get('crn')
    del session['sections'][crn]
    session.modified = True

    return redirect('/')


@app.route('/contact')
def about():
    '''Page with my contact info.'''
    return render_template('contact.html')


@app.route('/google/login')
@login_required
def google_login():
    google_authorization_url, state = start_google_flow()
    return redirect(google_authorization_url)


@app.route('/google/callback')
@login_required
def google_callback():
    state = request.args.get('state')
    tokens, credentials = finish_google_flow(request.args.get('code'))
    session['google_credentials'] = credentials_to_dict(credentials)
    flash('Logged into Google!')
    return redirect('/')


@app.route('/calendar')
@login_required
def list_calendars():
    if 'google_credentials' not in session:
        return redirect(url_for('google_login'))

    calendar = googleapiclient.discovery.build(
        'calendar', 'v3', credentials=create_google_credentials(session['google_credentials']))

    return 'We have access to your Google Calendar.'


@app.errorhandler(404)
def page_not_found(e):
    '''Render 404 page.'''
    return render_template('404.html'), 404


@app.errorhandler(Exception)
def handle_exception(e):
    '''Handles all other exceptions.'''

    # Handle HTTP errors
    if isinstance(e, HTTPException):
        return render_template('error.html', error=e), e.code

    # Handle non-HTTP errors
    app.logger.exception(e)

    # Hide error details in production
    if app.env == 'production':
        e = 'Something went wrong... Please try again later.'

    return render_template("error.html", error=e), 500
