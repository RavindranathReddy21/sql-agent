from langgraph.graph import StateGraph, END
from pydantic_models.agentState import AgentState
from app.nodes import get_schema, sql_generator, execute_query, route_after_execution

builder = StateGraph(AgentState)

builder.add_node("get_schema", get_schema)
builder.add_node("sql_generator", sql_generator)
builder.add_node("execute_query", execute_query)

builder.set_entry_point("get_schema")

builder.add_edge("get_schema", "sql_generator")
builder.add_edge("sql_generator", "execute_query")

builder.add_conditional_edges(
    "execute_query",
    route_after_execution,
    {
        "retry": "sql_generator",
        "finish": END
    }
)

graph = builder.compile()
