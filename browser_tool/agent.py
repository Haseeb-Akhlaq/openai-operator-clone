from browser_use import Agent, Browser, BrowserConfig
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import asyncio


async def use_browser(task: str):

    """
    Function to initialize an Agent and run a browser-based task.
    Can be imported and called from other files.

    :param task: The task description for the agent to execute.
    """
    load_dotenv()
    google_api_key = os.getenv("GEMINI_API_KEY")

    # llm = ChatOpenAI(model="gpt-4o")

    llm2 = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp", api_key=SecretStr(google_api_key)
    )

    agent = Agent(task=task, llm=llm2)
    result = await agent.run()
    return result.final_result()
