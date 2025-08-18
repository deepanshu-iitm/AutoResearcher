from pydantic import BaseModel, Field
from typing import List, Optional

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

class Document(BaseModel):
    id: str
    title: str
    authors: List[str]
    abstract: str
    published: str  # ISO date string
    year: int
    source: str = "arXiv"
    categories: List[str] = []
    link_pdf: Optional[str] = None
    link_abs: Optional[str] = None

class CollectRequest(BaseModel):
    goal: str = Field(..., min_length=8)
    max_results: int = Field(10, ge=1, le=50)

class CollectResponse(BaseModel):
    query_used: str
    documents: List[Document]

class MultiSourceResponse(BaseModel):
    goal: str
    total_documents: int
    unique_documents: int
    total_found_across_sources: int
    documents: List[Document]
    sources: dict
