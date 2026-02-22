"""
server.py — MCP Server. Exposes tools to the LLM.

Three tools:
  query_database  — single question, single SQL answer
  deep_analysis   — complex question, multi-query, optional chart
  describe_data   — what data is available (replaces get_schema tool)

Tool DESCRIPTIONS are critical — the LLM reads them to decide which
tool to call. Write them like instructions to a smart person.
"""

from fastmcp import FastMCP
from mcp_server.tools.database_tools import (
    run_query_database,
    run_deep_analysis,
    run_describe_data,
)

mcp = FastMCP(
    name="SQL Assistant",
    instructions="""You are a helpful data assistant connected to a business database.
- For simple data questions → use query_database
- For complex analytical questions needing multiple angles → use deep_analysis
- For questions about what data exists → use describe_data
- For greetings and general conversation → reply directly, no tools needed"""
)


# ---------------------------------------------------------------------------
# Tool 1 — Simple data question
# ---------------------------------------------------------------------------
@mcp.tool()
def query_database(question: str) -> str:
    """
    Answer a single data question using the database.
    Use for straightforward questions about numbers, totals, counts,
    or simple comparisons — anything answerable with one SQL query.
    Examples: total sales, top customers, orders last month.
    Do NOT use for complex multi-angle analysis — use deep_analysis instead.
    """
    result = run_query_database(question)

    if not result["success"]:
        return f"I couldn't answer that. Error: {result['error']}"

    lines = []
    if result["explanation"]:
        lines.append(result["explanation"])
    if result["sql_query"]:
        lines.append(f"\n**Query used:**\n```sql\n{result['sql_query']}\n```")
    if result["attempts"] > 1:
        lines.append(f"*(took {result['attempts']} attempts)*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 2 — Complex analytical question
# ---------------------------------------------------------------------------
@mcp.tool()
def deep_analysis(question: str) -> str:
    """
    Answer a complex analytical question that requires multiple queries
    and synthesized insights. Use when the question involves:
    - Multiple dimensions or angles (e.g. segments AND products AND time)
    - Correlations or comparisons across different data areas
    - Trend analysis with underlying breakdowns
    - Any question where one SQL query clearly won't be enough
    Returns insights in plain English, plus a chart if the data supports it.
    """
    result = run_deep_analysis(question)

    if not result["success"]:
        return f"Analysis failed. Error: {result['error']}"

    lines = []

    if result["insights"]:
        lines.append(result["insights"])

    if result["sub_questions"]:
        lines.append("\n**This analysis ran the following sub-queries:**")
        for i, (sub_q, sql) in enumerate(zip(result["sub_questions"], result["queries"]), 1):
            lines.append(f"{i}. {sub_q}")
            if sql and not sql.startswith("ERROR"):
                lines.append(f"```sql\n{sql}\n```")

    # chart_data is passed back for the frontend — included as JSON marker
    if result["chart_data"]:
        import json
        lines.append(f"\n**CHART_DATA:**\n```json\n{json.dumps(result['chart_data'])}\n```")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tool 3 — What data is available
# ---------------------------------------------------------------------------
@mcp.tool()
def describe_data() -> str:
    """
    Describe what data is available in the database and what kinds
    of questions can be answered. Use when the user asks:
    - "what data do you have?"
    - "what can I ask you?"
    - "what tables are there?"
    - "what information is available?"
    Returns a friendly, human-readable description (not raw schema).
    """
    result = run_describe_data()

    if not result["success"]:
        return f"Could not read database structure. Error: {result['error']}"

    schema = result["schema"]

    lines = [
        "Here's what data I have access to:\n"
    ]

    for table_name, info in schema.items():
        col_names = [col["name"] for col in info["columns"]]
        fk_refs = [fk["references"] for fk in info["foreign_keys"]]

        lines.append(f"**{table_name.replace('_', ' ').title()}**")
        lines.append(f"  Fields: {', '.join(col_names)}")

        if fk_refs:
            lines.append(f"  Linked to: {', '.join(fk_refs)}")

        lines.append("")

    lines.append("You can ask me anything about this data — totals, trends, breakdowns, comparisons, and more.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8001)