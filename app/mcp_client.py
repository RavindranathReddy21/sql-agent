import json
import httpx
from typing import Any
from app.llm import llm
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

# MCP Server base URL
MCP_SERVER_URL = "http://localhost:8001"

# ---------------------------------------------------------------------------
# Tool definitions — these are sent to the LLM so it knows what's available.
# The descriptions here MUST match the intent of the MCP server tools.
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": (
                "Query the database using a natural language question. "
                "Use this tool when the user asks about data, numbers, statistics, "
                "sales, revenue, customers, orders, products, or any analytical "
                "question that requires looking up information from the database. "
                "Do NOT use this for greetings, general conversation, or non-data questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The user's question in plain English"
                    }
                },
                "required": ["question"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_schema",
            "description": (
                "Returns the full database schema — all tables, columns, data types, "
                "and relationships. Use this when the user asks what data is available, "
                "what tables exist, or what kinds of questions can be answered."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# ---------------------------------------------------------------------------
# Call a tool on the MCP server
# ---------------------------------------------------------------------------
async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    """
    Sends a tool call to the MCP server and returns the result as a string.
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{MCP_SERVER_URL}/tools/{tool_name}",
                json={"arguments": arguments}
            )
            response.raise_for_status()
            data = response.json()
            # MCP tool responses come back as a list of content blocks
            content = data.get("content", [])
            return " ".join(block.get("text", "") for block in content if block.get("type") == "text")
        except httpx.HTTPError as e:
            return f"Error calling tool '{tool_name}': {str(e)}"


# ---------------------------------------------------------------------------
# Main agent function — given a user message, decide whether to use a tool
# or just reply, then return the final answer.
# ---------------------------------------------------------------------------
async def run_agent(user_message: str, chat_history: list[dict] = None) -> dict:
    """
    Runs the agentic loop:
    1. Send message + tools to LLM
    2. If LLM wants to call a tool → call MCP server → send result back to LLM
    3. If LLM replies directly → return that reply
    Returns a dict with: reply, tool_used, sql_query (if any)
    """
    chat_history = chat_history or []

    system_prompt = """You are a helpful data assistant. You have access to tools that let you query a database.

    - For data questions (sales, customers, orders, numbers, reports) → use the query_database tool
    - For schema questions (what tables exist, what data is available) → use the get_schema tool  
    - For greetings, general chat, or non-data questions → reply directly, do NOT use any tools

    Always be friendly and concise."""

    # Build messages list
    messages = [SystemMessage(content=system_prompt)]
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=user_message))

    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(TOOLS)

    # --- First LLM call ---
    response = await llm_with_tools.ainvoke(messages)

    tool_used = None
    sql_query = None

    # Check if the LLM wants to call a tool
    if response.tool_calls:
        tool_call = response.tool_calls[0]  # handle first tool call
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_used = tool_name

        # Call the MCP server
        tool_result = await call_mcp_tool(tool_name, tool_args)

        # Extract SQL from result if present (for returning to the API caller)
        if "```sql" in tool_result:
            start = tool_result.find("```sql") + 6
            end = tool_result.find("```", start)
            sql_query = tool_result[start:end].strip()

        # Add tool interaction to messages and call LLM again for final answer
        messages.append(response)
        messages.append(ToolMessage(content=tool_result, tool_call_id=tool_call["id"]))

        # --- Second LLM call — formulate final reply ---
        final_response = await llm_with_tools.ainvoke(messages)
        reply = final_response.content

    else:
        # LLM replied directly — no tool needed (e.g. "hi" → "Hello! How can I help?")
        reply = response.content

    return {
        "reply": reply,
        "tool_used": tool_used,
        "sql_query": sql_query,
    }