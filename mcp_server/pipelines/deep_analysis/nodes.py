"""
pipelines/deep_analysis/nodes.py — Nodes for the multi-query analysis pipeline.

This pipeline handles complex questions that need multiple SQL queries,
cross-table analysis, and synthesized insights — optionally with chart data.

STATUS: Stubbed — ready to implement.

Each node is defined with its full docstring and return signature
so the graph wiring is clear before implementation begins.
"""

from app.llm import llm
from app.db import engine
from sqlalchemy import text
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic_models.analysisState import AnalysisState
from mcp_server.shared.nodes import is_safe_query

MAX_ATTEMPTS = 3

def decompose_question(state: AnalysisState) -> AnalysisState:
    """
    Calls the LLM with the question + schema.
    Breaks the question into 2-4 focused sub-questions, each answerable
    with a single SQL query.

    Stores result in: state.sub_questions (list of strings)

    Example:
      "Which customer segments are growing and how does that relate to top products?"
      →  [
           "What is revenue by customer segment for each of the last 3 years?",
           "What are the top 10 products by revenue?",
           "What products are most purchased by the fastest-growing segment?"
         ]
    """
    system_prompt = f"""You are an expert data analyst. Break the following complex question 
    into 2-4 focused sub-questions that can each be answered with a single SQL query.
    Database Schema:
    {state.db_schema}
    Return a JSON array of sub-question strings. Nothing else.
    Example: ["sub-question 1", "sub-question 2", "sub-question 3"]"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state.question),
    ]

    try:
        import json
        response = llm.invoke(messages)
        content = response.content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        state.sub_questions = json.loads(content.strip())
        state.error = None
    except Exception as e:
        state.error = f"Failed to decompose question: {str(e)}"

    return state

def generate_and_execute_all(state: AnalysisState) -> AnalysisState:
    """
    Loops through state.sub_questions.
    For each sub-question: generates a SQL query, executes it safely,
    stores the result.

    Stores results in:
      state.queries  (list of SQL strings, one per sub-question)
      state.results  (list of result strings, one per sub-question)

    Failed sub-queries store an error string in results rather than
    halting the whole pipeline — partial results are still valuable.
    """
    from pydantic_models.agentState import AgentState, SQLOutput

    queries = []
    results = []

    for sub_question in state.sub_questions:
        # Reuse the same prompt structure as the query pipeline
        system_prompt = f"""You are an expert SQL assistant. Generate a correct SQL query.
        Database Schema:
        {state.db_schema}
        Rules:
        - SQLite database
        - Date columns are TEXT: use strftime('%Y', date_col) = '2023'
        - Always alias aggregated columns
        - Use JOINs based on foreign keys in the schema
        - Return only the SQL query"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=sub_question),
        ]

        try:
            structured_llm = llm.with_structured_output(SQLOutput)
            response = structured_llm.invoke(messages)
            sql = response.sql_query.strip()
            queries.append(sql)

            # Execute safely
            if not is_safe_query(sql):
                results.append("ERROR: Unsafe query generated")
                continue

            with engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.fetchall()
                results.append(str(rows))

        except Exception as e:
            queries.append("ERROR: Could not generate query")
            results.append(f"ERROR: {str(e)}")

    state.queries = queries
    state.results = results
    return state

def synthesize_insights(state: AnalysisState) -> AnalysisState:
    """
    Calls the LLM with ALL sub-questions and their results together.
    Finds connections, trends, and correlations across them.
    Produces a unified analytical narrative.

    Stores result in: state.insights (string)
    """
    # Build a combined context of all sub-results
    context_parts = []
    for i, (sub_q, result) in enumerate(zip(state.sub_questions, state.results), 1):
        context_parts.append(f"Sub-question {i}: {sub_q}\nResult: {result}")
    combined_context = "\n\n".join(context_parts)

    system_prompt = """You are a senior data analyst. You have the results of multiple 
    database queries that together answer a complex business question.
    Synthesize ALL the results into a single coherent analytical response:
    - Answer the original question directly
    - Highlight connections and correlations between the different results
    - Call out the most important numbers, trends, and insights
    - Use plain English — no SQL, no column names, no table names
    - Structure with short paragraphs or bullet points for readability"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Original question: {state.question}\n\n{combined_context}"),
    ]

    try:
        response = llm.invoke(messages)
        state.insights = response.content.strip()
        state.error = None
    except Exception as e:
        state.error = f"Failed to synthesize insights: {str(e)}"

    return state

def build_chart_data(state: AnalysisState) -> AnalysisState:
    """
    Calls the LLM to decide if a chart would help, and if so,
    returns structured JSON that the frontend can render directly.

    Stores result in: state.chart_data (dict or None)

    Chart data format:
    {
      "type": "bar" | "line" | "pie",
      "title": "Chart title",
      "labels": ["Jan", "Feb", "Mar"],
      "datasets": [
        { "label": "Revenue", "data": [42000, 51000, 63000] }
      ]
    }
    If no chart is appropriate, stores None.
    """
    context_parts = []
    for i, (sub_q, result) in enumerate(zip(state.sub_questions, state.results), 1):
        context_parts.append(f"Sub-question {i}: {sub_q}\nResult: {result}")
    combined_context = "\n\n".join(context_parts)

    system_prompt = """You are a data visualization expert. Given query results, 
    decide if a chart would help communicate the insights.
    If YES: return a JSON object with this exact structure:
    {
    "type": "bar" | "line" | "pie",
    "title": "descriptive chart title",
    "labels": ["label1", "label2"],
    "datasets": [{ "label": "series name", "data": [num1, num2] }]
    }
    If NO chart is appropriate: return exactly the string "NO_CHART"
    Return only the JSON or "NO_CHART". Nothing else."""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=combined_context),
    ]

    try:
        import json
        response = llm.invoke(messages)
        content = response.content.strip()

        if content == "NO_CHART":
            state.chart_data = None
        else:
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            state.chart_data = json.loads(content.strip())

        state.error = None
    except Exception as e:
        # Chart failure is non-fatal — insights still get returned
        state.chart_data = None

    return state