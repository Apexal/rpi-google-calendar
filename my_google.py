from constants import PERIOD_TYPES
import json
import os
from typing import Dict, Tuple
from google.oauth2 import credentials
import google.oauth2.credentials
import google_auth_oauthlib.flow

# https://googleapis.github.io/google-api-python-client/docs/dyn/calendar_v3.html

client_config = json.loads(os.environ['GOOGLE_CLIENT_SECRETS_JSON'])
scopes = ['openid', 'https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/calendar.events']
redirect_uri = os.environ['GOOGLE_REDIRECT_URI']


def start_google_flow() -> str:
    '''Start Google flow and generate authorization url.'''
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config,
        scopes=scopes,
        redirect_uri=redirect_uri)

    return flow.authorization_url()


def finish_google_flow(code: str) -> Tuple[Dict, credentials.Credentials]:
    '''Finish Google flow by exchanging auth code for tokens. Returns (tokens, credentials)'''
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config,
        scopes=scopes,
        redirect_uri=redirect_uri)

    tokens = flow.fetch_token(code=code)
    credentials = flow.credentials

    return tokens, credentials


def create_google_credentials(credentials: Dict) -> credentials.Credentials:
    '''Create a Google Credentials object from a dictionary of required properties.'''
    return google.oauth2.credentials.Credentials(**credentials)


def credentials_to_dict(credentials: credentials.Credentials) -> Dict:
    '''Turn a Google Credentials object into a serializable dictionary.'''
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def period_to_calendar_event(period):
    return {
        'recurrence': [],
        'id': '',
        # Event title
        'summary': period['courseTitle'] + ' ' + PERIOD_TYPES[period['type']],
        'location': period['location'],
        # Can have HTML
        'description': f'<b>{period["courseSubjectPrefix"]}-{period["courseSubjectCode"]}</b> {period["courseTitle"]} {period["type"]}',
        'colorId': '',
        'start': {
            'timeZone': 'America/New_York',
            'dateTime': ''
        },
        'end': {
            'timeZone': 'America/New_York',
            'dateTime': ''
        },
        'source': {
            'url': '',
            'title': 'RPI Course Schedule Importer'
        }
    }
