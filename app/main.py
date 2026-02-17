from fastapi import FastAPI, HTTPException
from app.graph import graph
from pydantic_models.agentState import AgentState

from pydantic import BaseModel

class QueryRequest(BaseModel):
    question: str
from typing import Optional, Any

class QueryResponse(BaseModel):
    answer: Optional[str] = None
    sql_query: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    attempts: int

app = FastAPI()

@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest) -> QueryResponse:
    state = AgentState(question=request.question)

    try:
        raw_result = graph.invoke(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    final_state = AgentState(**raw_result)

    return QueryResponse(
        answer=final_state.result,
        sql_query=final_state.sql_query,
        result=final_state.result,
        error=final_state.error,
        attempts=final_state.attempts
    )


