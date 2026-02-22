"""
pipelines/query/nodes.py — Nodes specific to the query pipeline.

These nodes only make sense in the context of answering a single
natural language question with a single SQL query.

Shared nodes (get_schema, is_safe_query) live in shared/nodes.py.
"""

from app.llm import llm
from sqlalchemy import text
from app.db import engine
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic_models.agentState import AgentState, SQLOutput
from mcp_server.shared.nodes import is_safe_query

MAX_ATTEMPTS = 3

def sql_generator(state: AgentState) -> AgentState:
    """
    Calls the LLM with the schema + question → produces one SQL query.
    On retries, includes the previous error so the LLM can self-correct.
    """
    structured_llm = llm.with_structured_output(SQLOutput)

    error_context = ""
    if state.error and state.attempts > 0:
        error_context = f"""
The previous query failed with this error:
{state.error}

Failed query:
{state.sql_query}

Fix the query based on the error above.
"""

    system_prompt = f"""You are an expert SQL assistant. Generate a correct SQL query for the given question.

Database Schema:
{state.db_schema}

Rules:
- Use only tables and columns from the schema above
- This is a SQLite database
- Date columns are TEXT in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM'
- For date filtering use strftime(): strftime('%Y', date_col) = '2023'
- Always alias aggregated columns: SUM(amount) AS total_revenue
- Use JOINs based on the foreign key relationships in the schema
- Return only the SQL query, no explanation
{error_context}"""

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

def execute_query(state: AgentState) -> AgentState:
    """
    Safely executes state.sql_query against the database.
    Stores raw rows in state.result.
    Increments state.attempts on any failure.
    """
    if not state.sql_query or not is_safe_query(state.sql_query):
        state.error = "Query is not safe to execute (must be a pure SELECT statement)."
        state.attempts += 1
        return state

    with engine.connect() as conn:
        try:
            result = conn.execute(text(state.sql_query))
            rows = result.fetchall()
            state.result = str(rows)
            state.error = None
        except Exception as e:
            state.error = f"SQL execution error: {str(e)}"
            state.attempts += 1

    return state

def explain_results(state: AgentState) -> AgentState:
    """
    Calls the LLM with the raw SQL results → plain English explanation.
    Stored in state.natural_language_output.
    """
    system_prompt = """You are a helpful data analyst. Explain the SQL results in plain English.
- Directly answer what the data shows
- Highlight key numbers, trends, or insights
- Avoid mentioning SQL, table names, or column names
- Be concise and clear
Respond with only the explanation."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Question: {state.question}\n\nResults: {state.result}"),
    ]

    try:
        response = llm.invoke(messages)
        state.natural_language_output = response.content.strip()
        state.error = None
    except Exception as e:
        state.error = str(e)

    return state

def route_after_execution(state: AgentState) -> str:
    if state.error and state.attempts < MAX_ATTEMPTS:
        return "retry"
    return "finish"