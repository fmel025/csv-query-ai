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


    # 1. Obtener la estructura
    df_schema = duck_db_connection.execute("DESCRIBE data").df()

    # 2. Crear una representación tipo SQL (más fácil de entender para GPT-3.5)
    ddl_columns = ",\n  ".join([f"{row['column_name']} {row['column_type']}" for _, row in df_schema.iterrows()])

    # 3. Obtener una muestra representativa (esto es VITAL para modelos menores)
    sample_rows = duck_db_connection.execute("SELECT * FROM data LIMIT 3").df().to_markdown(index=False)

    schema_context = f"""
    ### ESTRUCTURA DE LA TABLA `data`:
    CREATE TABLE data (
    {ddl_columns}
    );

    ### EJEMPLO DE DATOS (Primeras 3 filas):
    {sample_rows}
    """
    
    system_prompt = prompts["system_prompt"].format(schema=schema_context)

    model = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=api_url,
        temperature=0.5,
        max_tokens=1000,
    )

    @tool(response_format="content_and_artifact")
    def run_sql(query: str):
        """Run a SQL query against the DuckDB database."""
        print(f"Running SQL query: {query}")
        result = duck_db_connection.execute(query).df()
        return "Here is the result of the query:", { "result": result.to_markdown(index=False) }

    agent = create_agent(model=model, system_prompt=system_prompt, tools=[run_sql])

    return agent
