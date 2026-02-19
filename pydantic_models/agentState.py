from pydantic import BaseModel
from typing import Optional

class AgentState(BaseModel):
    question: str
    db_schema: Optional[str] = None
    sql_query: Optional[str] = None
    result: Optional[str] = None
    natural_language_output: Optional[str] = None
    error: Optional[str] = None
    attempts: int = 0

class SQLOutput(BaseModel):
    sql_query: str
    explanation: str | None = None
    
class NaturalLanguageOutput(BaseModel):
    natural_language_output: str