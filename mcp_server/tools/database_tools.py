"""
database_tools.py — Bridge between MCP server and the pipelines.

One function per MCP tool. Each function:
  1. Calls the right graph
  2. Packages the result into a clean dict

No logic here. No SQL here. No LLM calls here.
"""

from mcp_server.pipelines.query.graph import graph as query_graph
from mcp_server.pipelines.deep_analysis.graph import graph as deep_analysis_graph
from mcp_server.shared.nodes import get_schema_dict
from pydantic_models.agentState import AgentState
from pydantic_models.analysisState import AnalysisState


# ---------------------------------------------------------------------------
# Tool: query_database — single question, single SQL query
# ---------------------------------------------------------------------------
def run_query_database(question: str) -> dict:
    initial_state = AgentState(question=question)

    try:
        raw = query_graph.invoke(initial_state)
        final = AgentState(**raw)
    except Exception as e:
        return {"success": False, "error": str(e),
                "sql_query": None, "explanation": None, "attempts": 0}

    return {
        "success": final.error is None,
        "error": final.error,
        "sql_query": final.sql_query,
        "explanation": final.natural_language_output,
        "attempts": final.attempts,
    }


# ---------------------------------------------------------------------------
# Tool: deep_analysis — complex question, multiple queries, chart data
# ---------------------------------------------------------------------------
def run_deep_analysis(question: str) -> dict:
    initial_state = AnalysisState(question=question)

    try:
        raw = deep_analysis_graph.invoke(initial_state)
        final = AnalysisState(**raw)
    except Exception as e:
        return {"success": False, "error": str(e),
                "insights": None, "chart_data": None, "queries": []}

    return {
        "success": final.error is None,
        "error": final.error,
        "sub_questions": final.sub_questions,
        "queries": final.queries,
        "insights": final.insights,
        "chart_data": final.chart_data,
    }


# ---------------------------------------------------------------------------
# Tool: describe_data — human-friendly description of what's in the DB
# (NOT a raw schema dump — that's an internal concern)
# ---------------------------------------------------------------------------
def run_describe_data() -> dict:
    return get_schema_dict()