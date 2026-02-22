"""
pipelines/query/graph.py — Wiring for the single-question query pipeline.

Flow:
  get_schema → sql_generator → execute_query → explain_results
                                    ↑ retry ↙

No logic here. Sequence and routing only.
"""

from langgraph.graph import StateGraph, END
from pydantic_models.agentState import AgentState
from mcp_server.shared.nodes import get_schema
from mcp_server.pipelines.query.nodes import (
    sql_generator,
    execute_query,
    explain_results,
    route_after_execution,
)

builder = StateGraph(AgentState)

builder.add_node("get_schema",      get_schema)
builder.add_node("sql_generator",   sql_generator)
builder.add_node("execute_query",   execute_query)
builder.add_node("explain_results", explain_results)

builder.set_entry_point("get_schema")
builder.add_edge("get_schema",    "sql_generator")
builder.add_edge("sql_generator", "execute_query")

builder.add_conditional_edges(
    "execute_query",
    route_after_execution,
    {
        "retry":  "sql_generator",
        "finish": "explain_results",
    }
)

builder.add_edge("explain_results", END)

graph = builder.compile()