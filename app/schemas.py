from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PlanRequest(BaseModel):
    goal: str = Field(..., min_length=8, description="High-level research goal")
    max_results: Optional[int] = Field(15, description="Maximum documents per source")

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

# New schemas for conversational research features
class ResearchQuestionsRequest(BaseModel):
    goal: str = Field(..., min_length=8, description="Research goal to generate questions for")

class ResearchQuestionsResponse(BaseModel):
    goal: str
    questions: List[str]
    domain: str

class Answer(BaseModel):
    question: str
    answer: str

class RefineResearchRequest(BaseModel):
    original_goal: str = Field(..., min_length=8)
    answers: List[Answer]

class RefineResearchResponse(BaseModel):
    original_goal: str
    refined_goal: str
    refinements: Dict[str, Any]

class RefinedReportRequest(BaseModel):
    original_goal: str = Field(..., min_length=8)
    answers: List[Answer]

class RefinedReportResponse(BaseModel):
    original_goal: str
    refined_goal: str
    report: str
    refinements: Dict[str, Any]
    plan: Dict[str, Any]
    collection_stats: Dict[str, Any]
    processing_stats: Dict[str, Any]
    document_count: int
