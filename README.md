# AI SQL Assistant

A natural language data assistant built with FastAPI, LangGraph, and Groq (Llama 3.3 70B). Ask questions in plain English — the system figures out the right approach, queries your database, and explains the results conversationally.

---

## Architecture Overview

```
User message
    │
    ▼
FastAPI  /chat  (app/main.py)
    │
    ▼
Intent Classifier  (app/mcp_client.py)
    │  Structured LLM call — which tool is needed?
    │
    ├── "none"           → direct conversational reply
    ├── "describe_data"  → run_describe_data()
    ├── "query_database" → run_query_database()
    └── "deep_analysis"  → run_deep_analysis()
                │
                ▼
        database_tools.py  (mcp_server/tools/)
                │  calls the right LangGraph pipeline
                │
                ├── pipelines/query/graph.py
                │     get_schema → sql_generator → execute_query → explain_results
                │     (with auto-retry up to 3 times on SQL errors)
                │
                └── pipelines/deep_analysis/graph.py
                      get_schema → decompose_question → generate_and_execute_all
                      → synthesize_insights → build_chart_data
                │
                ▼
        Tool result returned to mcp_client.py
                │
                ▼
        Final LLM call — forms natural conversational reply
                │
                ▼
        FastAPI returns ChatResponse
```

---

## Project Structure

```
project/
│
├── app/                            # FastAPI — public-facing API
│   ├── main.py                     # Endpoints: GET /health, POST /chat
│   ├── mcp_client.py               # Intent classifier + tool dispatcher + reply formation
│   ├── llm.py                      # Groq LLM setup (shared by app and mcp_server)
│   ├── db.py                       # SQLAlchemy engine (shared by app and mcp_server)
│   └── __init__.py
│
├── mcp_server/                     # Tool server — all database and pipeline logic
│   │
│   ├── shared/
│   │   └── nodes.py                # Shared nodes: get_schema, is_safe_query
│   │                               # Used by ALL pipelines — single source of truth
│   │
│   ├── pipelines/
│   │   ├── query/
│   │   │   ├── nodes.py            # sql_generator, execute_query, explain_results
│   │   │   └── graph.py            # Wires the query pipeline
│   │   │
│   │   └── deep_analysis/
│   │       ├── nodes.py            # decompose_question, generate_and_execute_all,
│   │       │                       # synthesize_insights, build_chart_data
│   │       └── graph.py            # Wires the deep_analysis pipeline
│   │
│   ├── tools/
│   │   └── database_tools.py       # Bridge: one function per tool, calls the right graph
│   │
│   ├── server.py                   # FastMCP server — exposes tools for external MCP clients
│   │                               # (Claude Desktop, Cursor, etc.) on port 8001
│   └── __init__.py
│
├── pydantic_models/
│   ├── agentState.py               # AgentState, SQLOutput — used by query pipeline
│   ├── analysisState.py            # AnalysisState — used by deep_analysis pipeline
│   └── __init__.py
│
├── .env
├── pyproject.toml
└── README.md
```

---

## File Responsibilities

Each file has one job. If you're unsure where something belongs:

| File | One question it answers |
|---|---|
| `shared/nodes.py` | How do I read the DB schema? (one place, used everywhere) |
| `pipelines/query/nodes.py` | What does each step of the query pipeline do? |
| `pipelines/query/graph.py` | In what order do query pipeline nodes run? |
| `pipelines/deep_analysis/nodes.py` | What does each step of deep analysis do? |
| `pipelines/deep_analysis/graph.py` | In what order do deep analysis nodes run? |
| `tools/database_tools.py` | How do I call a graph and package its result? |
| `server.py` | What tools does an external MCP client see? |
| `app/mcp_client.py` | Which tool should run for this message? |
| `app/main.py` | What HTTP endpoints exist? |

---

## Tools

### `query_database`
Single data question answered with one SQL query. Handles auto-retry (up to 3 attempts) if the generated SQL fails.

Best for: totals, counts, top N, filters, averages, single-metric lookups.

### `deep_analysis`
Complex questions requiring multiple SQL queries, synthesized insights, and optional chart data. Breaks the question into sub-questions, runs each independently, then synthesizes all results together.

Best for: multi-dimensional analysis, correlations, trend comparisons, "why" questions, anything where one query isn't enough.

### `describe_data`
Returns a human-friendly description of what the database contains and what kinds of questions can be answered. Not a raw schema dump — a conversational summary.

Best for: "what data do you have?", "what can I ask?", onboarding new users.

---

## Setup

### 1. Install dependencies

```bash
pip install -e .
```

### 2. Create `.env`

```
DATABASE_URL=sqlite:///./your_database.db
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Run

```bash
# Terminal 1 — MCP server (for external MCP clients like Claude Desktop)
python -m mcp_server.server

# Terminal 2 — FastAPI
uvicorn app.main:app --reload --port 8000
```

> **Note:** The FastAPI app calls tool functions directly (not over HTTP), so it works without the MCP server running. The MCP server is only needed for external MCP clients.

---

## API

### `POST /chat`

**Simple data question:**
```json
// Request
{ "message": "What were total sales in 2023?", "history": [] }

// Response
{
  "reply": "Total sales in 2023 came to $18,432 across 22 delivered orders.",
  "tool_used": "query_database",
  "sql_query": "SELECT SUM(oi.unit_price * oi.quantity) AS total_revenue ...",
  "chart_data": null
}
```

**Complex analytical question:**
```json
// Request
{ "message": "Which categories are most profitable but also have the highest refund and complaint rates?", "history": [] }

// Response
{
  "reply": "Books (Fiction and Non-Fiction) have the highest margins at 64–66% with zero refunds...",
  "tool_used": "deep_analysis",
  "sql_query": "SELECT ... \n---\nSELECT ...",
  "chart_data": {
    "type": "bar",
    "title": "Profit Margin vs Refund Rate by Category",
    "labels": ["Fiction", "Non-Fiction", "Computers", "Mobile Phones"],
    "datasets": [
      { "label": "Profit Margin %", "data": [66, 64, 29, 38] },
      { "label": "Refund Rate %",   "data": [0, 0, 8, 12] }
    ]
  }
}
```

**Conversational (no tool called):**
```json
// Request
{ "message": "hi", "history": [] }

// Response
{
  "reply": "Hello! I'm your data assistant. Ask me anything about your business data.",
  "tool_used": null,
  "sql_query": null,
  "chart_data": null
}
```

**Multi-turn conversation:**
```json
{
  "message": "Which month had the highest sales?",
  "history": [
    { "role": "user",      "content": "What were total sales in 2023?" },
    { "role": "assistant", "content": "Total sales in 2023 came to $18,432..." }
  ]
}
```

### `GET /health`
```json
{ "status": "ok" }
```

---

## Adding a New Tool

1. Write node logic in `mcp_server/pipelines/<new_pipeline>/nodes.py`
2. Wire the graph in `mcp_server/pipelines/<new_pipeline>/graph.py`
3. Add a `run_<tool>()` bridge function in `mcp_server/tools/database_tools.py`
4. Add a `@mcp.tool()` in `mcp_server/server.py` (for external MCP clients)
5. Add the tool name to the `IntentClassification` Literal in `app/mcp_client.py`
6. Add routing logic for it in `call_tool()` and `classify_intent()` in `mcp_client.py`

If the new tool shares nodes with an existing pipeline (e.g. `get_schema`), import from `mcp_server/shared/nodes.py` — don't duplicate.

---

## Tech Stack

| Layer | Technology |
|---|---|
| API server | FastAPI + Uvicorn |
| LLM | Llama 3.3 70B via Groq |
| LLM framework | LangChain + LangGraph |
| MCP server | FastMCP |
| Database | SQLite (via SQLAlchemy) |
| Data validation | Pydantic |
| HTTP client | httpx |