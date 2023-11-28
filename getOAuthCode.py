from flask import Flask, redirect, request, jsonify, session
import threading
import webbrowser
import requests
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong, random secret key

client_id = '9337e364-3c78-444a-be21-24809866b45d'
client_secret = 'wbE8Q~nyYTqOoUl06u0L.E5_WgJUTGEOQ~2v0avr'
redirect_uri = 'http://localhost:8000/auth/oauth/azure-ad/callback'  # Change to your chat app's callback URL
scopes = ['https://graph.microsoft.com/User.Read']
tenant_id = 'your_tenant_id'  # Replace with your Azure AD tenant ID

authorization_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize'
token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'

def run_oauth_flow():
    auth_url = f"{authorization_url}?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={' '.join(scopes)}"
    
    # Open the authorization URL in the browser
    webbrowser.open(auth_url, new=2)

    # Wait for the user to complete sign-in
    input("Press Enter after signing in: ")

    # Redirect to the chat app running on port 8000
    redirect_url = 'http://localhost:8000'
    webbrowser.open(redirect_url, new=2)

@app.route('/')
def home():
    return 'Hello, <a href="/auth/login">Login with Azure AD</a>'

@app.route('/auth/login')
def login():
    # Run the OAuth flow in a separate thread
    threading.Thread(target=run_oauth_flow).start()
    return 'OAuth flow initiated. Check your browser.'

@app.route('/auth/oauth/azure-ad/callback')
def callback():
    code = request.args.get('code')
    token_params = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    token_response = requests.post(token_url, data=token_params)
    token_data = token_response.json()

    # Store the token_data in session or database, handle user authentication
    session['oauth_token'] = token_data['access_token']

    # Optionally, fetch user data using the access token
    user_response = requests.get('https://graph.microsoft.com/v1.0/me', headers={'Authorization': f'Bearer {token_data["access_token"]}'})
    user_data = user_response.json()

    # Perform additional tasks with user_data if needed
    return jsonify(user_data)

if __name__ == '__main__':
    app.run(debug=True, port=8001)
