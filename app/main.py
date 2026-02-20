from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from app.graph import graph
from pydantic_models.agentState import AgentState

from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
from typing import Optional, Any

class QueryResponse(BaseModel):
    question: Optional[str] = None
    sql_query: Optional[str] = None
    result: Optional[Any] = None
    human_readable_result: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest) -> QueryResponse:
    state = AgentState(question=request.question)

    try:
        raw_result = graph.invoke(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    final_state = AgentState(**raw_result)

    return QueryResponse(
        question=final_state.question,
        sql_query=final_state.sql_query,
        result=final_state.result,
        human_readable_result=final_state.natural_language_output,
        error=final_state.error,
        attempts=final_state.attempts
    )


