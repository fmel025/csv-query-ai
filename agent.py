from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from duckdb import DuckDBPyConnection
from dotenv import load_dotenv
from langchain_core.tools import tool

import os

load_dotenv()

api_url = os.getenv("OPENROUTER_API_URL")
api_key = os.getenv("OPENROUTER_API_KEY")
model_name = os.getenv("OPENROUTER_MODEL")


def build_agent(duck_db_connection: DuckDBPyConnection):
    pass


system_prompt = f"""
You are a data assistant querying a DuckDB table called `data`.
And also you can check weather.

Rules:
- Always use SQL via the tool for data questions
- Never hallucinate results
- Use LIMIT by default
"""

model = ChatOpenAI(model=model_name, api_key=api_key, base_url=api_url, temperature=0.5)


@tool
def get_weather():
    """Gives the current weather information"""
    return "The weather is rainy"


agent = create_agent(model=model, system_prompt=system_prompt, tools=[get_weather])
