import subprocess
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl
import os

os.environ["OPENAI_API_KEY"] = "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"

@cl.on_chat_start
async def on_chat_start():
    model = ChatOpenAI(streaming=True)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a very knowledgeable AI to give answers by going through the uploaded video",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)

@cl.on_message
async def on_message(message: cl.Message):
    first_subprocess = subprocess.run(["python", "getEmails.py"])
    if first_subprocess.returncode == 0:
        subprocess.run(["python", "getContents.py"])

    runnable = cl.user_session.get("runnable")

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
