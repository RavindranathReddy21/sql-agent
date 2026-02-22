"""
shared/nodes.py — Nodes that are reused across multiple pipelines.

Any node that more than one pipeline needs lives here.
Pipeline-specific nodes live in pipelines/<name>/nodes.py.

Currently shared:
  - get_schema      (used by: query, deep_analysis, and any future pipeline)
  - is_safe_query   (used by: query, deep_analysis)
"""

import json
from app.db import engine
from sqlalchemy import inspect
from pydantic_models.agentState import AgentState


# ---------------------------------------------------------------------------
# Safety — shared utility used by any pipeline that executes SQL
# ---------------------------------------------------------------------------
BLOCKED_KEYWORDS = [
    "DROP", "DELETE", "ALTER", "UPDATE", "INSERT", "CREATE",
    "TRUNCATE", "EXEC", "GRANT", "REVOKE", "MERGE", "CALL",
    "ATTACH", "DETACH", "PRAGMA", "VACUUM", "ANALYZE",
]


def is_safe_query(query: str) -> bool:
    """Returns True only if the query is a pure SELECT with no dangerous keywords."""
    query_upper = query.upper().strip()
    if not query_upper.startswith("SELECT"):
        return False
    return not any(kw in query_upper for kw in BLOCKED_KEYWORDS)


# ---------------------------------------------------------------------------
# get_schema — single source of truth for reading the DB structure
#
# Used by:
#   - pipelines/query/graph.py       (first node in query pipeline)
#   - pipelines/deep_analysis/graph.py (first node in deep_analysis pipeline)
#   - tools/database_tools.py        (for the describe_data tool)
# ---------------------------------------------------------------------------
def get_schema(state: AgentState) -> AgentState:
    """
    Inspects the database and stores the full schema in state.db_schema.
    Every table, every column, every foreign key — as a JSON string.
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        schema = {}

        for table in tables:
            columns = inspector.get_columns(table)
            foreign_keys = inspector.get_foreign_keys(table)
            schema[table] = {
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

        state.db_schema = json.dumps(schema, indent=2)
        state.error = None

    except Exception as e:
        state.error = str(e)

    return state


def get_schema_dict() -> dict:
    """
    Helper that returns the raw schema as a Python dict.
    Used by database_tools.py for the describe_data tool
    without needing to create a dummy AgentState.
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        schema = {}

        for table in tables:
            columns = inspector.get_columns(table)
            foreign_keys = inspector.get_foreign_keys(table)
            schema[table] = {
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
        return {"success": True, "schema": schema}
    except Exception as e:
        return {"success": False, "error": str(e), "schema": None}