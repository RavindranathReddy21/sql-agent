"""
pipelines/deep_analysis/graph.py — Wiring for the multi-query analysis pipeline.

Flow:
  get_schema → decompose_question → generate_and_execute_all
             → synthesize_insights → build_chart_data → END

No logic here. Sequence only.
Uses its own AnalysisState (not AgentState) since the data shape is different.
"""

from langgraph.graph import StateGraph, END
from pydantic_models.analysisState import AnalysisState
from mcp_server.shared.nodes import get_schema
from mcp_server.pipelines.deep_analysis.nodes import (
    decompose_question,
    generate_and_execute_all,
    synthesize_insights,
    build_chart_data,
)

builder = StateGraph(AnalysisState)

builder.add_node("get_schema",              get_schema)
builder.add_node("decompose_question",      decompose_question)
builder.add_node("generate_and_execute_all", generate_and_execute_all)
builder.add_node("synthesize_insights",     synthesize_insights)
builder.add_node("build_chart_data",        build_chart_data)

builder.set_entry_point("get_schema")
builder.add_edge("get_schema",               "decompose_question")
builder.add_edge("decompose_question",        "generate_and_execute_all")
builder.add_edge("generate_and_execute_all", "synthesize_insights")
builder.add_edge("synthesize_insights",      "build_chart_data")
builder.add_edge("build_chart_data",         END)

graph = builder.compile()