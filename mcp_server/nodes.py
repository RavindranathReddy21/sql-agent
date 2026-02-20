import json
from app.db import engine
from sqlalchemy import inspect, text
from pydantic_models.agentState import AgentState, SQLOutput
from app.llm import llm
from langchain_core.messages import SystemMessage, HumanMessage

blocked_keywords = [
    "DROP", "DELETE", "ALTER", "UPDATE", "INSERT", "CREATE",
    "TRUNCATE", "EXEC", "GRANT", "REVOKE", "MERGE", "CALL",
    "ATTACH", "DETACH", "PRAGMA", "VACUUM", "ANALYZE",
]

MAX_ATTEMPTS = 3


def is_safe_query(query: str) -> bool:
    query_upper = query.upper()
    if not query_upper.startswith("SELECT"):
        return False
    for keyword in blocked_keywords:
        if keyword in query_upper:
            return False
    return True


def route_after_execution(state: AgentState) -> str:
    if state.error and state.attempts < MAX_ATTEMPTS:
        return "retry"
    return "finish"


def get_schema(state: AgentState) -> AgentState:
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        db_schema = {}
        for table in tables:
            columns = inspector.get_columns(table)
            foreign_keys = inspector.get_foreign_keys(table)
            db_schema[table] = {
                "columns": [
                    {"name": col["name"], "type": str(col["type"])}
                    for col in columns
                ],
                "foreign_keys": [
                    {
                        "column": fk["constrained_columns"],
                        "references": f"{fk['referred_table']}.{fk['referred_columns']}"
                    }
                    for fk in foreign_keys
                ]
            }
        state.db_schema = json.dumps(db_schema, indent=2)
    except Exception as e:
        state.error = str(e)
    return state


def sql_generator(state: AgentState) -> AgentState:
    structured_llm = llm.with_structured_output(SQLOutput)

    error_context = ""
    if state.error and state.attempts > 0:
        error_context = f"""
    The previous SQL query failed with this error:
    {state.error}

    Previous query that failed:
    {state.sql_query}

    Please fix the query based on the error above.
    """

    system_prompt = f"""You are an expert SQL assistant. Given a database schema and a user question, generate a syntactically correct SQL query.
    Database Schema:
    {state.db_schema}
    Rules:
    - Use only table and column names from the schema
    - This is a SQLite database
    - All date/time columns are stored as TEXT in the format 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD'
    - For date filtering, always use string comparison or strftime():
        - Year filter:   strftime('%Y', order_date) = '2023'
        - Month filter:  strftime('%Y-%m', order_date) = '2023-07'
        - Past 30 days:  order_date >= date('now', '-30 days')
    - For aggregations use SUM(), COUNT(), AVG() with GROUP BY
    - JOIN tables using foreign key relationships in the schema
    - Always alias aggregated columns (e.g. SUM(amount) AS total_revenue)
    - Return only the SQL query, no explanation
    {error_context}
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


def execute_query(state: AgentState) -> AgentState:
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
            state.error = f"SQL execution error: {str(e)}"
            state.attempts += 1
    return state


def convert_query_to_text(state: AgentState) -> AgentState:
    system_prompt = """You are a helpful data analyst assistant. Explain SQL query results in plain English that anyone can understand.
    Your summary should:
    - Directly answer what the data shows
    - Highlight key numbers, trends, or insights
    - Use natural language (avoid mentioning SQL, tables, or columns by name)
    - Be formatted for easy reading
    Respond with only the summary."""

    user_message = f"""SQL Query:
    {state.sql_query}
    Query Results:
    {state.result}"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    try:
        response = llm.invoke(messages)
        state.natural_language_output = response.content.strip()
        state.error = None
    except Exception as e:
        state.error = str(e)

    return state