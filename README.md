# AI SQL Assistant — MCP Architecture

## Project Structure

```
project/
├── app/                        # FastAPI app (the client)
│   ├── main.py                 # API endpoints — /health, /chat
│   ├── mcp_client.py           # Connects to MCP server, runs agentic loop
│   ├── nodes.py                # LangGraph pipeline nodes (unchanged)
│   ├── graph.py                # LangGraph graph definition (unchanged)
│   ├── llm.py                  # Groq LLM setup (unchanged)
│   ├── db.py                   # SQLAlchemy engine (unchanged)
│   └── __init__.py
│
├── mcp_server/                 # MCP server (the toolbox)
│   ├── server.py               # FastMCP server — exposes tools over HTTP/SSE
│   ├── tools/
│   │   ├── database_tools.py   # Core logic for each tool
│   │   └── __init__.py
│   └── __init__.py
│
├── pydantic_models/
│   ├── agentState.py           # AgentState, SQLOutput, NaturalLanguageOutput
│   └── __init__.py
│
├── requirements.txt
└── .env
```

## How It Works

```
User message
    │
    ▼
FastAPI /chat  (app/main.py)
    │
    ▼
MCP Client  (app/mcp_client.py)
    │  Sends: message + tool definitions
    ▼
LLM (Llama 3.3 70B via Groq)
    │  Decides: do I need a tool?
    ├─── NO  → reply directly (e.g. "hi" → "Hello!")
    │
    └─── YES → tool_call: { name, args }
                    │
                    ▼
             MCP Server  (mcp_server/server.py on :8001)
                    │  Runs the right tool
                    ├── query_database → LangGraph pipeline → SQL → result → explanation
                    └── get_schema     → SQLAlchemy inspector → schema JSON
                    │
                    ▼
             Tool result returned to MCP Client
                    │
                    ▼
             LLM forms final reply using tool result
                    │
                    ▼
             FastAPI returns ChatResponse
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env file
```
DATABASE_URL=sqlite:///./your_database.db
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Start the MCP server (Terminal 1)
```bash
python -m mcp_server.server
```
MCP server runs on http://localhost:8001

### 4. Start the FastAPI app (Terminal 2)
```bash
python run.py
```
FastAPI runs on http://localhost:8000

## API Usage

### POST /chat
```json
// Request
{
  "message": "What were total sales in 2023?",
  "history": []
}

// Response
{
  "reply": "Total sales in 2023 were $4.2M across 1,847 orders...",
  "tool_used": "query_database",
  "sql_query": "SELECT SUM(amount) AS total_revenue FROM orders WHERE strftime('%Y', order_date) = '2023'"
}
```

### With chat history (multi-turn)
```json
{
  "message": "Which month was the best?",
  "history": [
    { "role": "user", "content": "What were total sales in 2023?" },
    { "role": "assistant", "content": "Total sales in 2023 were $4.2M..." }
  ]
}
```

### Non-data message (no tool called)
```json
// Request
{ "message": "hi", "history": [] }

// Response
{
  "reply": "Hello! I'm your data assistant. Ask me anything about your database — sales, customers, orders, and more.",
  "tool_used": null,
  "sql_query": null
}
```

## Adding a New Tool

1. Add the logic function in `mcp_server/tools/database_tools.py`
2. Add the `@mcp.tool()` decorated function in `mcp_server/server.py`
3. Add the tool definition to the `TOOLS` list in `app/mcp_client.py`

That's it — the LLM will automatically start using the new tool when appropriate.