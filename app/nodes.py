import json
from time import sleep
from app.db import engine
from sqlalchemy import inspect, text
from pydantic_models.agentState import AgentState
from app.llm import llm

blocked_keywords = [
    "DROP", "DELETE", "ALTER", "UPDATE", "INSERT",
    "CREATE", "TRUNCATE", "EXEC", "GRANT", "REVOKE",
    "MERGE", "CALL", "ATTACH", "DETACH", "PRAGMA",
    "VACUUM", "ANALYZE"
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
    """ Determine the next node based on the execution result."""
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
    """
    Generate SQL query based on the question and schema.
    """

    system_prompt = f"""You are an SQL assistant. You will be given a question and a database schema. Your task is to generate a SQL query that answers the question based on the provided schema. 
    The database schema is in JSON format and contains table names as keys and a list of column names as values.
    Here is the database schema:
    {state.db_schema}
    Here is the question:
    {state.question}
    Generate a SQL query that answers the question based on the provided schema. 
    Make sure to use the correct table and column names from the schema. 
    The SQL query should be syntactically correct and should be able to run on the database without errors. 
    Do not include any explanations or comments in the SQL query, just provide the query itself.
    """
    
    try:
        response = llm.invoke(system_prompt)
        content = response.content.strip("```sql\n").strip("```")
        state.sql_query = content
        state.error = None

    except Exception as e:
        print("Error generating SQL query:", str(e))
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
            print("Query executed successfully. Fetching results...")
            
            rows = result.fetchall()
            print(f"{isinstance(rows, list)}: {rows}")
            state.result =  str(rows)
            state.error = None
        except Exception as e:
            state.error = str(e)
            state.attempts += 1
    return state

def convert_query_to_text(state: AgentState):
    """
    Convert the SQL query and result to text format for better readability.
    """
    system_prompt = f"""You are an assistant that converts SQL queries and their results into a more human-readable format.
    Here is the SQL query:
    {state.sql_query}
    Here is the result of the SQL query:
    {state.result}
    Convert the SQL query and its result into a more human-readable format.
    """
    try:
        response = llm.invoke(system_prompt)
        state.natural_language_output = response.content.strip()    
        state.error = None
    except Exception as e:
        state.error = str(e)
    return state