"""
app/mcp_client.py — Connects FastAPI to the MCP server.

Sends the user message + tool definitions to the LLM.
If the LLM picks a tool → calls the MCP server → gets the result.
Then calls the LLM again to form a natural final reply.
"""

import json
import httpx
from app.llm import llm
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

MCP_SERVER_URL = "http://localhost:8001"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": (
                "Answer a single data question using the database. "
                "Use for straightforward questions about numbers, totals, counts, "
                "or simple comparisons — anything answerable with one SQL query. "
                "Examples: total sales, top customers, orders last month. "
                "Do NOT use for complex multi-angle analysis — use deep_analysis instead."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The data question in plain English"}
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "deep_analysis",
            "description": (
                "Answer a complex analytical question requiring multiple queries and synthesized insights. "
                "Use when the question involves multiple dimensions, correlations, trend analysis, "
                "or anything where one SQL query clearly won't be enough. "
                "Returns insights in plain English plus a chart if the data supports it."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The complex analytical question"}
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "describe_data",
            "description": (
                "Describe what data is available and what kinds of questions can be answered. "
                "Use when the user asks 'what data do you have?', 'what can I ask?', "
                "'what tables are there?', or similar questions about data availability."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{MCP_SERVER_URL}/tools/{tool_name}",
                json={"arguments": arguments}
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("content", [])
            return " ".join(block.get("text", "") for block in content if block.get("type") == "text")
        except httpx.HTTPError as e:
            return f"Error calling tool '{tool_name}': {str(e)}"


async def run_agent(user_message: str, chat_history: list[dict] = None) -> dict:
    chat_history = chat_history or []

    system_prompt = """You are a helpful data assistant. You have tools to query a business database.

- Simple data questions (totals, counts, top N) → query_database
- Complex analytical questions (multi-dimensional, correlations, trends) → deep_analysis
- Questions about what data exists → describe_data
- Greetings and general conversation → reply directly, no tools

Always be friendly and concise."""

    messages = [SystemMessage(content=system_prompt)]
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=user_message))

    llm_with_tools = llm.bind_tools(TOOLS)
    response = await llm_with_tools.ainvoke(messages)

    tool_used = None
    sql_query = None
    chart_data = None

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_used = tool_name

        tool_result = await call_mcp_tool(tool_name, tool_args)

        # Extract SQL if present
        if "```sql" in tool_result:
            start = tool_result.find("```sql") + 6
            end = tool_result.find("```", start)
            sql_query = tool_result[start:end].strip()

        # Extract chart data if present
        if "CHART_DATA:" in tool_result:
            try:
                start = tool_result.find("```json\n", tool_result.find("CHART_DATA:")) + 8
                end = tool_result.find("```", start)
                chart_data = json.loads(tool_result[start:end].strip())
            except Exception:
                chart_data = None

        messages.append(response)
        messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))

        final_response = await llm_with_tools.ainvoke(messages)
        reply = final_response.content
    else:
        reply = response.content

    return {
        "reply": reply,
        "tool_used": tool_used,
        "sql_query": sql_query,
        "chart_data": chart_data,
    }