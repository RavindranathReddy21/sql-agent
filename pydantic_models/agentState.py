from pydantic import BaseModel
from typing import Optional

class AgentState(BaseModel):
    question: str
    db_schema: Optional[str] = None
    sql_query: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0
