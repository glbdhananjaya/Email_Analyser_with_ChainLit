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

async def process_and_continue_chat():
    # subprocess.run(["python", "getemails.py"])

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
        "response based on the content. These are the emails list: {email_array}"
    )

    # Use the AI model to continue the chat
    model = ChatOpenAI(streaming=True)
    prompt_template = ChatPromptTemplate.from_messages([("human", prompt)])
    runnable = prompt_template | model | StrOutputParser()

    msg = cl.Message(content="")
    
    async for chunk in runnable.astream({"email_array": email_array}, config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()])):
        await msg.stream_token(chunk)

    await msg.send()

@cl.on_chat_start
async def on_chat_start():
    model = ChatOpenAI(streaming=True)
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
        runnable = cl.user_session.get("runnable")  # type: Runnable

        msg = cl.Message(content="")

        async for chunk in runnable.astream(
            {"question": message.content},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
        ):
            await msg.stream_token(chunk)

        await msg.send()
