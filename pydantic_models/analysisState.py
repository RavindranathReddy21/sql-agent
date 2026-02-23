"""
pydantic_models/analysisState.py — State for the deep_analysis pipeline.

Different from AgentState because this pipeline holds multiple
queries and results, not just one.
"""

from pydantic import BaseModel
from typing import Optional


class AnalysisState(BaseModel):
    # Input
    question: str

    # Set by get_schema node (shared)
    db_schema: Optional[str] = None

    # Set by decompose_question node
    sub_questions: list[str] = []

    # Set by generate_and_execute_all node (parallel lists — index N matches)
    queries: list[str] = []
    results: list[str] = []

    # Set by synthesize_insights node
    insights: Optional[str] = None

    # Set by build_chart_data node (None if no chart is appropriate)
    chart_data: Optional[dict] = None

    # Error tracking
    error: Optional[str] = None
    
