from pydantic import BaseModel, Field
from typing import List

class PlanRequest(BaseModel):
    goal: str = Field(..., min_length=8, description="High-level research goal")

class Subtopic(BaseModel):
    name: str
    rationale: str

class PlanResponse(BaseModel):
    normalized_goal: str
    subtopics: List[Subtopic]
    suggested_queries: List[str]
    suggested_sources: List[str]
    next_actions: List[str]
