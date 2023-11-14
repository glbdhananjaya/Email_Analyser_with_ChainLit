from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl
import json
import subprocess
import os

os.environ["OPENAI_API_KEY"] = "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"

async def process_and_continue_chat(question=None):
    subprocess.run(["python", "getemails.py"])

    result = subprocess.check_output(["python", "getContents.py"])
    emails_json = json.loads(result.decode("utf-8"))

    email_array = json.dumps(emails_json)
    prompt = (
        f"Please categorize all the provided emails into three categories: 'urgent,' 'important,' and 'normal.' "
        "For each email, provide the email subject, category, and sender. Additionally, after categorizing, provide "
        "a brief response or action for each category: If the content of an email is null or empty, please categorize "
        "it as 'Not Provided' For 'urgent' emails, specify the immediate action required. For 'important' emails, describe "
        "the significance and the timely response expected. For 'normal' emails, mention any standard follow-up or handling "
        "required. If an email doesn't fit into any of these categories, mark it as 'normal' and suggest the appropriate "
        "response based on the content. Please assist the user knowledgeably to any question directed regarding the emails, please go through the emails. These are the emails list: {email_array}"
    )

    if question:
        prompt += f"\n{question}"

    
    model = ChatOpenAI(streaming=True)
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
    model = ChatOpenAI(streaming=True, model="gpt-3.5-turbo")
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
