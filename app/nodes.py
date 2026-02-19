import json
from time import sleep
from app.db import engine
from sqlalchemy import inspect, text
from pydantic_models.agentState import AgentState, SQLOutput, NaturalLanguageOutput
from app.llm import llm
from langchain_core.messages import SystemMessage, HumanMessage

blocked_keywords = [
    "DROP",
    "DELETE",
    "ALTER",
    "UPDATE",
    "INSERT",
    "CREATE",
    "TRUNCATE",
    "EXEC",
    "GRANT",
    "REVOKE",
    "MERGE",
    "CALL",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "VACUUM",
    "ANALYZE",
]

MAX_ATTEMPTS = 3


def is_safe_query(query: str) -> bool:
    """
    Check if the SQL query is safe to execute by ensuring it does not contain any blocked keywords.
    """
    query_upper = query.upper()
    if not query_upper.startswith("SELECT"):
        return False

    for keyword in blocked_keywords:
        if keyword in query_upper:
            return False
    return True


def route_after_execution(state: AgentState) -> str:
    """Determine the next node based on the execution result."""
    if state.error and state.attempts < MAX_ATTEMPTS:
        return "retry"
    return "finish"


def get_schema(state: AgentState) -> AgentState:
    """
    Get the schema for the nodes.
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        db_schema = {}
        for table in tables:
            columns = inspector.get_columns(table)
            db_schema[table] = [column["name"] for column in columns]

        state.db_schema = json.dumps(db_schema)
    except Exception as e:
        state.error = str(e)
    return state


def sql_generator(state: AgentState):
    structured_llm = llm.with_structured_output(SQLOutput)

    system_prompt = f"""You are an SQL assistant. Given a database schema and a user question, generate a syntactically correct SQL query.
    Database Schema:
    {state.db_schema}
    Rules:
    - Use only table and column names from the schema
    - Return only the SQL query, no explanations or comments
    """
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state.question),
    ]

    try:
        response = structured_llm.invoke(messages)
        state.sql_query = response.sql_query.strip()
        state.error = None
    except Exception as e:
        state.error = str(e)

    return state


def execute_query(state: AgentState):
    """
    Execute the SQL query and store the result in the state.
    """
    if not state.sql_query or not is_safe_query(state.sql_query):
        state.error = "The generated SQL query is not safe to execute."
        state.attempts += 1
        return state

    with engine.connect() as conn:
        try:
            result = conn.execute(text(state.sql_query))
            rows = result.fetchall()
            state.result = str(rows)
            state.error = None
        except Exception as e:
            state.error = str(e)
            state.attempts += 1
    return state


def convert_query_to_text(state: AgentState):
    system_prompt = """You are a helpful data analyst assistant. Explain SQL query results in plain English that anyone can understand.
    Your summary should:
    - Directly answer what the data shows
    - Highlight key numbers, trends, or insights
    - Use natural language (avoid mentioning SQL, tables, or columns by name)
    - Be formatted for easy reading (use bullet points or short paragraphs where appropriate)
    Respond with only the summary. Do not explain what the query does technically — focus on what the data means."""

    user_message = f"""SQL Query:
    {state.sql_query}
    Query Results:
    {state.result}"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    try:
        structured_llm = llm.with_structured_output(NaturalLanguageOutput)
        response = structured_llm.invoke(messages)
        state.natural_language_output = response.natural_language_output.strip()
        state.error = None
    except Exception as e:
        state.error = str(e)

    return state