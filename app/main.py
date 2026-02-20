from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any
from app.mcp_client import run_agent


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    history: Optional[list[dict]] = []   # [{"role": "user"|"assistant", "content": "..."}]


class ChatResponse(BaseModel):
    reply: str
    tool_used: Optional[str] = None      # which MCP tool was called (if any)
    sql_query: Optional[str] = None      # the generated SQL (if a DB query was made)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="AI SQL Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint. Accepts a message and optional chat history.
    The agent decides whether to call a database tool or reply directly.

    Examples:
      "hi"                        → plain reply, no tool
      "what tables exist?"        → calls get_schema tool
      "total sales in 2023?"      → calls query_database tool
    """
    try:
        result = await run_agent(
            user_message=request.message,
            chat_history=request.history,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(
        reply=result["reply"],
        tool_used=result["tool_used"],
        sql_query=result["sql_query"],
    )