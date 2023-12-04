from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from msal import ConfidentialClientApplication

import chainlit as cl
import json
import subprocess
import os
from typing import Dict, Optional
import webbrowser
import json

api_key = os.environ.get("OPENAI_API_KEY")

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

client_id = config['client_id']
client_secret = config['client_secret']
redirect_uri = config['redirect_uri']
tenant_id = config['tenant_id']
SCOPES = ['User.Read']

client = ConfidentialClientApplication(client_id=client_id, client_credential=client_secret)
authorization_url = client.get_authorization_request_url(SCOPES, redirect_uri=redirect_uri)
webbrowser.open(authorization_url)

@cl.oauth_callback
def oauth_callback(
        provider_id: str,
        token: str,
        raw_user_data: Dict[str, str],
        default_app_user: cl.AppUser,
) -> Optional[cl.AppUser]:
    with open('config.json', 'w') as config_file:
        config = {
            "OAuth_access_token": token,
        }
        json.dump(config, config_file, indent=4)

    print("OAuth callback executed successfully.")
    return default_app_user

async def process_and_continue_chat(question=None):
    # subprocess.run(["python", "getToken.py"])
    subprocess.run(["python", "getemails.py"])

    result = subprocess.check_output(["python", "getContents.py"])
    emails_json = json.loads(result.decode("utf-8"))

    email_array = json.dumps(emails_json)
    prompt = (
    f"Please analyze the provided emails and categorize them into three groups: 'urgent,' 'important,' and 'normal.' "
    "For each email, provide the subject, category, and sender. If the content is null or empty, categorize it as 'Not Provided.' "
    "Using the emails provided within curly brackets like this: {{Email}}, generate informative content. Each set of curly brackets contains an email message"
    "For 'urgent' emails, specify the immediate action required. For 'important' emails, describe their significance and the timely response expected. "
    "For 'normal' emails, mention any standard follow-up or handling required. If an email doesn't fit these categories, mark it as 'normal' and suggest "
    "the appropriate response based on the content. Additionally, assist the user with any questions about the emails. Please go through the following emails: {email_array}"
)


    if question:
        prompt += f"\n{question}"

    
    model = ChatOpenAI(streaming=True, model="gpt-4-1106-preview", temperature=0.8)
    prompt_template = ChatPromptTemplate.from_messages([("human", prompt)])
    runnable = prompt_template | model | StrOutputParser()

    msg = cl.Message(content="")
    
    suggestions = []

    async for chunk in runnable.astream({"email_array": email_array}, config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()])):
        if "suggestion" in chunk:
            suggestions.append(chunk["suggestion"])
        await msg.stream_token(chunk)

    await msg.send()

    
    if suggestions:
        print("Suggestions:")
        for suggestion in suggestions:
            print(suggestion)

@cl.on_chat_start
async def on_chat_start():
    app_user = cl.user_session.get("user")
    await cl.Message(f"Hello {app_user.username}").send()
    model = ChatOpenAI(streaming=True, model="gpt-4-1106-preview", temperature=0.8)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions.",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)

@cl.on_message
async def on_message(message: cl.Message):
    if "how is my emails" in message.content.lower():
        await process_and_continue_chat()
    else:
        await process_and_continue_chat(question=message.content)
