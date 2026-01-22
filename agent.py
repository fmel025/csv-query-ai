from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from duckdb import DuckDBPyConnection
from dotenv import load_dotenv
from langchain_core.tools import tool

import yaml
import os

load_dotenv()


def build_agent(duck_db_connection: DuckDBPyConnection):
    api_url = os.getenv("OPENROUTER_API_URL")
    api_key = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("OPENROUTER_MODEL")

    # Load prompts from YAML file
    with open("prompts.yaml", "r") as f:
        prompts = yaml.safe_load(f)
        
    schema = duck_db_connection.execute("DESCRIBE data").df().to_markdown(index=False)

    system_prompt = prompts["system_prompt"].format(schema=schema)

    model = ChatOpenAI(
        model=model_name, api_key=api_key, base_url=api_url, temperature=0.5
    )

    @tool(response_format="content_and_artifact")
    def run_sql(query: str) -> dict[str, str]:
        """Run a SQL query against the DuckDB database."""
        result = duck_db_connection.execute(query).df()
        return {
            "content": "Here is the result of the query:",
            "artifact": result,
        }

    agent = create_agent(model=model, system_prompt=system_prompt, tools=[run_sql])

    response = agent.invoke({"messages": [("user", "What is your purpose?")]})
    print("Agent response:", response["messages"][-1].content)

    return agent
