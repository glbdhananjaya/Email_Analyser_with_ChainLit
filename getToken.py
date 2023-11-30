import webbrowser
from flask import Flask, request
from msal import ConfidentialClientApplication
import json

app = Flask(__name__)
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

client_id = config['client_id']
client_secret = config['client_secret']
redirect_uri = config['redirect_uri']
tenant_id = config['tenant_id']
SCOPES = ['User.Read']

client = ConfidentialClientApplication(client_id=client_id, client_credential=client_secret)
authorization_url = client.get_authorization_request_url(SCOPES, redirect_uri=redirect_uri)

@app.route('/auth/oauth/azure-ad/callback')
def callback():
    authorization_code = request.args.get('code')
    print(f'Authorization code received: {authorization_code}')

    result = client.acquire_token_by_authorization_code(
        authorization_code,
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )

    if "error" in result:
        print(f"Failed to retrieve OAuth access token. Error: {result['error']}")
        print(f"Error description: {result.get('error_description', 'N/A')}")
        return 'Failed to retrieve access token.'

    access_token = result.get("access_token")
    print("Access token:", access_token)

    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    config["authorization_code"] = authorization_code
    config["OAuth_access_token"] = access_token

    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

    print("Authorization code and access token have been saved to the configuration file.")
    return 'Authorization code and access token received successfully. You can close this window.'

if __name__ == '__main__':
    webbrowser.open(authorization_url)
    app.run(port=8000)
