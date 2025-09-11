import os
import requests
import secrets

from flask import Blueprint, redirect, request, url_for, jsonify, session

from functools import wraps

from urllib.parse import quote

from dotenv import load_dotenv

import urllib3

load_dotenv()

KEYCLOAK_REALM         = os.getenv("KEYCLOAK_REALM")
KEYCLOAK_CLIENT_ID     = os.getenv("KEYCLOAK_CLIENT_ID")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET")
KEYCLOAK_SERVER_URL    = os.getenv("KEYCLOAK_SERVER_URL")
KEYCLOAK_REDIRECT_URI  = os.getenv("KEYCLOAK_REDIRECT_URI")
ENABLE_KEYCLOAK_AUTH   = str(os.getenv("ENABLE_KEYCLOAK_AUTH", "true")).lower() == "true"

# Base endpoint for OpenID Connect
keycloak_openid_endpoint = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect"
# Keycloak endpoints
authorization_endpoint = f"{keycloak_openid_endpoint}/auth"
token_endpoint         = f"{keycloak_openid_endpoint}/token"
userinfo_endpoint      = f"{keycloak_openid_endpoint}/userinfo"
logout_endpoint        = f"{keycloak_openid_endpoint}/logout"

#app = Flask(__name__)
#app.secret_key = secrets.token_hex(16)  # Used for session management

# Define Blueprint
# The first argument is the blueprint's name, which Flask uses for routing and templating.
# The second argument is the import name, which Flask uses to locate the blueprint's resources.
auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If auth is disabled via environment flag, bypass login checks
        if not ENABLE_KEYCLOAK_AUTH:
            return f(*args, **kwargs)
        if 'access_token' not in session:
            # User is not logged in, redirect to login page
            return redirect(url_for('auth.login'))
        
        # Check if token is valid (optional additional security)
        # You could implement token validation here if needed
        
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login')
def login():
    """Redirect to Keycloak login page"""
    # Generate state parameter to prevent CSRF
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    
    # Build authorization URL
    # Prefer dynamically generated callback URL to avoid mismatches; fall back to env if needed
    redirect_uri = url_for('auth.callback', _external=True)
    if not redirect_uri:
        redirect_uri = KEYCLOAK_REDIRECT_URI

    auth_url_params = {
        'client_id': KEYCLOAK_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state
    }
    
    auth_url = f"{authorization_endpoint}?"
    auth_url += "&".join([f"{key}={quote(value)}" for key, value in auth_url_params.items()])
    # TEMP: debug to help diagnose redirect URI mismatches
    print(f"[Keycloak] Using redirect_uri: {redirect_uri}")
    print(f"[Keycloak] Authorization URL: {auth_url}")
    
    return redirect(auth_url)

@auth_bp.route('/callback')
def callback():
    """Handle the OAuth callback from Keycloak"""
    # Check state parameter to prevent CSRF attacks
    if 'oauth_state' not in session or session['oauth_state'] != request.args.get('state'):
        return jsonify({'error': 'Invalid state parameter'}), 400
    
    # Get authorization code from query parameters
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code received'}), 400
    
    # Exchange authorization code for tokens
    # Use the exact same redirect_uri as when initiating the login
    redirect_uri = url_for('auth.callback', _external=True) or KEYCLOAK_REDIRECT_URI
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': KEYCLOAK_CLIENT_ID,
        'client_secret': KEYCLOAK_CLIENT_SECRET,
        'redirect_uri': redirect_uri
    }
    
    # Make request to token endpoint
    # token_response = requests.post(
    #     token_endpoint,
    #     data=token_data,
    #     headers={'Content-Type': 'application/x-www-form-urlencoded'}
    # )

    DISABLE_SSL_VERIFY = str(os.getenv("DISABLE_SSL_VERIFY", "false")).lower() == "true"
    if DISABLE_SSL_VERIFY:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    token_response = requests.post(
        token_endpoint,
        data=token_data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        verify=not DISABLE_SSL_VERIFY
    )
    
    if token_response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve token'}), 500
    
    # Parse token response
    token_json = token_response.json()
    
    # Store tokens in session
    session['access_token'] = token_json['access_token']
    session['refresh_token'] = token_json['refresh_token']
    session['id_token'] = token_json.get('id_token')  # May not be present depending on scope
    
    # Redirect to home page
    return redirect(url_for('index_leaflet'))

@auth_bp.route('/logout')
def logout():
    """Log out from the application and Keycloak"""
    # Prepare for Keycloak logout
    redirect_url = url_for('index_leaflet', _external=True)
    
    # Clear session
    refresh_token = session.get('refresh_token')
    session.clear()
    
    if not refresh_token:
        return redirect(url_for('index_leaflet'))
    
    # Build logout URL (front-channel logout)
    logout_url = (
        f"{logout_endpoint}"
        f"?client_id={KEYCLOAK_CLIENT_ID}"
        f"&post_logout_redirect_uri={quote(url_for('index_leaflet', _external=True))}"
    )
    
    # You could also implement back-channel logout by making a POST request to the logout endpoint
    # This would revoke the refresh token server-side
    try:
        requests.post(
            logout_endpoint,
            data={
                'client_id': KEYCLOAK_CLIENT_ID,
                'client_secret': KEYCLOAK_CLIENT_SECRET,
                'refresh_token': refresh_token
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
    except:
        # If back-channel logout fails, continue with front-channel
        pass
    
    # Redirect to Keycloak logout page
    return redirect(logout_url)