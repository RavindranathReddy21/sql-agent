"""
app/mcp_client.py — Agent that classifies intent and calls tools directly.

The MCP server protocol (SSE/JSON-RPC) is designed for external MCP clients
like Claude Desktop or Cursor. For internal use within the same Python process,
we call the tool logic functions directly — no HTTP needed.

Flow:
  1. classify_intent()  → which tool to call (or none)?
  2. call tool function directly from database_tools.py
  3. form_reply()       → turn raw result into a conversational response
"""

import json
from app.llm import llm
from pydantic import BaseModel
from typing import Literal, Optional
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# Import tool logic directly — no HTTP calls needed
from mcp_server.tools.database_tools import (
    run_query_database,
    run_deep_analysis,
    run_describe_data,
)

class IntentClassification(BaseModel):
    tool: Literal["query_database", "deep_analysis", "describe_data", "none"]


CLASSIFICATION_PROMPT = """You are a routing assistant. Given a user message, decide which tool to use.
Tools:
- query_database: simple data questions answerable with ONE SQL query
  (totals, counts, top N, filters, averages, single metric lookups)
- deep_analysis: complex questions needing MULTIPLE queries and synthesized insights
  (multi-dimensional, correlations, trends across different areas, "why" questions,
  questions asking for both highest AND lowest, comparisons across segments)
- describe_data: user asks what data exists, what tables there are, what can be asked
- none: greetings, general conversation, anything not data-related
When in doubt between query_database and deep_analysis:
- Single number or list → query_database
- Multiple angles or comparisons in one question → deep_analysis"""


async def classify_intent(user_message: str, chat_history: list[dict]) -> str:
    structured_llm = llm.with_structured_output(IntentClassification)

    history_text = ""
    if chat_history:
        recent = chat_history[-4:]
        history_text = "\nRecent conversation:\n" + "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in recent
        ) + "\n"

    messages = [
        SystemMessage(content=CLASSIFICATION_PROMPT),
        HumanMessage(content=f"{history_text}User message: {user_message}"),
    ]

    try:
        result = structured_llm.invoke(messages)
        return result.tool
    except Exception:
        return "query_database"

def call_tool(tool_name: str, question: str) -> dict:
    """Calls the right tool function and returns a standardized result dict."""
    if tool_name == "query_database":
        return run_query_database(question)
    elif tool_name == "deep_analysis":
        return run_deep_analysis(question)
    elif tool_name == "describe_data":
        return run_describe_data()
    else:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}


def format_tool_result(tool_name: str, result: dict) -> str:
    """Formats the raw tool result into a readable string for the LLM."""
    if not result.get("success"):
        return f"Tool failed: {result.get('error', 'Unknown error')}"

    if tool_name == "query_database":
        parts = []
        if result.get("explanation"):
            parts.append(result["explanation"])
        if result.get("sql_query"):
            parts.append(f"SQL used:\n```sql\n{result['sql_query']}\n```")
        return "\n\n".join(parts)

    elif tool_name == "deep_analysis":
        parts = []
        if result.get("insights"):
            parts.append(result["insights"])
        if result.get("sub_questions") and result.get("queries"):
            parts.append("Sub-queries run:")
            for i, (q, sql) in enumerate(zip(result["sub_questions"], result["queries"]), 1):
                parts.append(f"{i}. {q}")
                if sql and not sql.startswith("ERROR"):
                    parts.append(f"```sql\n{sql}\n```")
        return "\n\n".join(parts)

    elif tool_name == "describe_data":
        if not result.get("schema"):
            return "Could not retrieve schema."
        lines = ["Here's what data is available:\n"]
        for table_name, info in result["schema"].items():
            col_names = [col["name"] for col in info["columns"]]
            lines.append(f"**{table_name.replace('_', ' ').title()}**")
            lines.append(f"  Fields: {', '.join(col_names)}")
            if info["foreign_keys"]:
                refs = [fk["references"] for fk in info["foreign_keys"]]
                lines.append(f"  Linked to: {', '.join(refs)}")
            lines.append("")
        return "\n".join(lines)

    return str(result)

async def form_reply(
    user_message: str,
    tool_result_text: str,
    chat_history: list[dict],
) -> str:
    history_messages = []
    for msg in chat_history[-6:]:
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history_messages.append(AIMessage(content=msg["content"]))

    messages = [
        SystemMessage(content="""You are a helpful data assistant.
Present the data results clearly and conversationally.
Do not mention SQL, tools, or technical details unless asked.
Be concise and focus on what the data means."""),
        *history_messages,
        HumanMessage(content=f"User asked: {user_message}\n\nData retrieved:\n{tool_result_text}\n\nPresent this clearly."),
    ]

    try:
        response = await llm.ainvoke(messages)
        return response.content.strip()
    except Exception:
        return tool_result_text

async def run_agent(user_message: str, chat_history: list[dict] = None) -> dict:
    chat_history = chat_history or []

    # Step 1: classify
    tool_name = await classify_intent(user_message, chat_history)

    tool_used = None
    sql_query = None
    chart_data = None

    if tool_name == "none":
        # Direct conversational reply
        history_messages = []
        for msg in chat_history[-6:]:
            if msg["role"] == "user":
                history_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                history_messages.append(AIMessage(content=msg["content"]))

        messages = [
            SystemMessage(content="You are a helpful data assistant. Answer conversationally. For data questions, let the user know you can query the database."),
            *history_messages,
            HumanMessage(content=user_message),
        ]
        response = await llm.ainvoke(messages)
        reply = response.content.strip()

    else:
        # Step 2: call tool directly
        tool_used = tool_name
        raw_result = call_tool(tool_name, user_message)

        # Extract SQL for the response metadata
        if tool_name == "query_database" and raw_result.get("sql_query"):
            sql_query = raw_result["sql_query"]
        elif tool_name == "deep_analysis" and raw_result.get("queries"):
            sql_query = "\n---\n".join(
                q for q in raw_result["queries"] if q and not q.startswith("ERROR")
            )

        # Extract chart data if present
        if tool_name == "deep_analysis" and raw_result.get("chart_data"):
            chart_data = raw_result["chart_data"]

        # Format result for LLM
        tool_result_text = format_tool_result(tool_name, raw_result)

        # Step 3: form natural reply
        reply = await form_reply(user_message, tool_result_text, chat_history)

    return {
        "reply": reply,
        "tool_used": tool_used,
        "sql_query": sql_query,
        "chart_data": chart_data,
    }