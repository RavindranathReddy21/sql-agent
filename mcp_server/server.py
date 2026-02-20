import json
from fastmcp import FastMCP
from mcp_server.tools.database_tools import run_query_database, run_get_schema

# Create the MCP server instance
mcp = FastMCP(
    name="SQL Assistant MCP Server",
    instructions="""
    You are a helpful data assistant connected to a SQLite database.
    Use the available tools to answer questions about data, numbers, sales, 
    customers, orders, and reports. For casual conversation or greetings, 
    respond directly without using any tools.
    """
)


@mcp.tool()
def query_database(question: str) -> str:
    """
    Query the database using a natural language question. 
    Use this tool when the user asks about data, numbers, statistics, 
    sales, revenue, customers, orders, products, or any analytical question 
    that requires looking up information from the database.
    Do NOT use this for greetings, general conversation, or non-data questions.
    """
    result = run_query_database(question)

    if not result["success"]:
        return f"Sorry, I couldn't answer that question. Error: {result['error']}"

    response = []

    if result["explanation"]:
        response.append(result["explanation"])

    if result["sql_query"]:
        response.append(f"\n**SQL Query Used:**\n```sql\n{result['sql_query']}\n```")

    if result["attempts"] > 1:
        response.append(f"\n*(Took {result['attempts']} attempts to generate a working query)*")

    return "\n".join(response)


@mcp.tool()
def get_schema() -> str:
    """
    Returns the full database schema — all tables, columns, data types, 
    and relationships. Use this when the user asks what data is available, 
    what tables exist, what the database looks like, or before explaining 
    what kinds of questions can be answered.
    """
    result = run_get_schema()

    if not result["success"]:
        return f"Could not retrieve schema. Error: {result['error']}"

    schema = result["schema"]
    lines = ["**Database Schema:**\n"]

    for table_name, table_info in schema.items():
        lines.append(f"**Table: `{table_name}`**")
        lines.append("Columns:")
        for col in table_info["columns"]:
            lines.append(f"  - `{col['name']}` ({col['type']})")
        if table_info["foreign_keys"]:
            lines.append("Foreign Keys:")
            for fk in table_info["foreign_keys"]:
                lines.append(f"  - `{fk['column']}` → `{fk['references']}`")
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8001)