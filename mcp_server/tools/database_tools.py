import json
from mcp_server.graph import graph
from app.db import engine
from pydantic_models.agentState import AgentState
from sqlalchemy import inspect


def run_query_database(question: str) -> dict:
    """
    Runs the full LangGraph pipeline:
    get_schema → sql_generator → execute_query → convert_query_to_text
    Returns a structured result dict.
    """
    state = AgentState(question=question)

    try:
        raw = graph.invoke(state)
        final = AgentState(**raw)
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "sql_query": None,
            "result": None,
            "explanation": None,
            "attempts": 0,
        }

    return {
        "success": final.error is None,
        "error": final.error,
        "sql_query": final.sql_query,
        "result": final.result,
        "explanation": final.natural_language_output,
        "attempts": final.attempts,
    }


def run_get_schema() -> dict:
    """
    Returns the full database schema as a structured dict.
    """
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
        return {"success": True, "schema": db_schema}
    except Exception as e:
        return {"success": False, "error": str(e), "schema": None}