import requests
import json
from datetime import datetime
import os

def my_python_tool(input1: str) -> str:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    get_emails_endpoint = config['get_emails_endpoint']
    access_token = config['OAuth_access_token']

    get_daily_emails(get_emails_endpoint, access_token)

    return input1

def get_daily_emails(get_emails_endpoint, access_token):
    current_directory = os.path.dirname(__file__)
    config_path = os.path.join(current_directory, 'data.json')
    print(config_path)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    today = datetime.now()
    start_date = today.strftime('%Y-%m-%dT00:00:00Z')
    end_date = today.strftime('%Y-%m-%dT23:59:59Z')
    params = {
        '$filter': f'receivedDateTime ge {start_date} and receivedDateTime le {end_date}',
    }

    response = requests.get(get_emails_endpoint, headers=headers)

    if response.status_code == 200:
        emails = response.json()
        with open(config_path, 'w') as json_file:
            json.dump(emails, json_file, indent=4)
    else:
        print("Failed to retrieve emails. Status code:", response.status_code)
        print(response.text)

my_python_tool("Hello World")
