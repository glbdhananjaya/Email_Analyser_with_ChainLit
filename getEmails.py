from promptflow import tool
import requests
import json
from datetime import datetime
import os

# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(input1: str) -> str:

  # Read the configuration file
  with open('config.json', 'r') as config_file:
    config = json.load(config_file)

  # Read Grapy API Configuration
  user_id = config['user_id']
  graph_api_endpoint = f"{config['graph_api_endpoint'].format(user_id=user_id)}"
  client_id = config['client_id']
  client_secret = config['client_secret']
  redirect_uri = config['redirect_uri']
  tenant_id = config['tenant_id']
  access_token = config['access_token']
  authorization_url = config['authorization_url']

  # Print the configuration
#   print("Configuration:")
#   print(f"User ID: {user_id}")
#   print(f"Graph API Endpoint: {graph_api_endpoint}")
#   print(f"Client ID: {client_id}")
#   print(f"Client Secret: {client_secret}")
#   print(f"Redirect URI: {redirect_uri}")
#   print(f"Tenant ID: {tenant_id}") 
#   print(f"Autorization URL: {authorization_url}")

  access_token = get_graph_api_accessToken(tenant_id, client_id, client_secret, redirect_uri)

  get_daily_emails(graph_api_endpoint, client_id, client_secret, redirect_uri, tenant_id, access_token)

  return input1

def get_daily_emails(graph_api_endpoint,client_id, client_secret, redirect_uri, tenant_id, access_token):

    current_directory = os.path.dirname(__file__)
    config_path = os.path.join(current_directory, 'data.json')
    print(config_path)

    # Set up the headers with the access token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Define the date range for daily emails (change as needed)
    today = datetime.now()
    start_date = today.strftime('%Y-%m-%dT00:00:00Z')
    end_date = today.strftime('%Y-%m-%dT23:59:59Z')
    params = {
        '$filter': f'receivedDateTime ge {start_date} and receivedDateTime le {end_date}',
    }

    # Make the request to the Microsoft Graph API to retrieve emails for the specified user
    response = requests.get(graph_api_endpoint, headers=headers, params=params)
    # Check if the request was successful
    if response.status_code == 200:
        emails = response.json()
        # Save the entire response to a JSON file
        with open(config_path, 'w') as json_file:
            json.dump(emails, json_file, indent=4)
        # for email in emails.get("value", []):
        #     print("------------------------------------------------------------------------------------------")
        #     #print(f"Subject: {email['subject']}")
        #     #print(f"From: {email['from']['emailAddress']['name']} ({email['from']['emailAddress']['address']})")
        #     print(f"Received: {email['receivedDateTime']}")
        #     print(f"Body: {email.get('body', {}).get('content')}")
        #     print("\n")
    else:
        print("Failed to retrieve emails. Status code:", response.status_code)
        print(response.text)


def get_graph_api_accessToken(tenant_id, client_id, client_secret, redirect_uri):
    config = None
    # Set up the headers and data for the token request
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": client_id,
        "scope": "https://graph.microsoft.com/.default",
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    # Make the request to the Microsoft Identity Platform to retrieve an access token
    response = requests.post(f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token", headers=headers, data=data)


    if response.status_code == 200:
        access_token = response.json().get("access_token", "")
        #print("Access token:", access_token)

        with open('config.json', 'r') as config_file:
          config = json.load(config_file)

        # Update the access_token field in the configuration
        config["access_token"] = access_token

        # Save the updated configuration back to the file
        with open('config.json', 'w') as config_file:
            json.dump(config, config_file, indent=4)

        #print("Access token has been saved to the configuration file.")

        return access_token
    else:
        print("Failed to retrieve access token. Status code:", response.status_code)
        print(response.text)
        return None

# Call the function to retrieve emails
my_python_tool("Hello World")