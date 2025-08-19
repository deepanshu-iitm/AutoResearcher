from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from app.schemas import (
    PlanRequest, PlanResponse, CollectRequest, CollectResponse, MultiSourceResponse, Document, Subtopic
)
from app.planner import make_plan
from app.retrievers.multi_source_retriever import collect_from_all_sources, rank_documents_by_relevance
from app.processors.document_processor import DocumentProcessor
from app.generators.report_generator import ReportGenerator
# Removed AIAnalysisService and ResearchDialogueService - conversational features removed per user request
import asyncio

app = FastAPI(title="AutoResearcher", version="0.1.0")

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Startup event handler to ensure smooth server initialization."""
    print("🚀 AutoResearcher server starting up...")
    print("✅ Server ready! Available endpoints:")
    print("   - GET  /healthz - Health check")
    print("   - POST /plan - Generate research plan")
    print("   - POST /collect - Collect documents")
    print("   - POST /generate-report - Generate full research report")
    print("   - POST /research-questions - Get clarifying questions")
    print("   - POST /refine-research - Refine research based on answers")
    print("   - POST /interactive-research - Interactive research workflow")
    print("   - POST /refined-report - Generate refined research report")
    print("   - GET  /stats - Collection statistics")

# Global variables for lazy initialization
doc_processor = None
report_generator = None

# Removed service initializations - conversational features removed per user request

def get_doc_processor():
    """Lazy initialization of document processor to avoid startup delays."""
    global doc_processor
    if doc_processor is None:
        try:
            doc_processor = DocumentProcessor()
        except Exception as e:
            print(f"Warning: DocumentProcessor initialization failed: {e}")
            # Create a minimal fallback processor
            doc_processor = type('MockProcessor', (), {
                'embed_and_store': lambda self, docs: {"processed": len(docs), "error": "ChromaDB unavailable"},
                'get_collection_stats': lambda self: {"error": "ChromaDB unavailable"}
            })()
    return doc_processor

def get_report_generator():
    """Lazy initialization of report generator."""
    global report_generator
    if report_generator is None:
        report_generator = ReportGenerator(get_doc_processor())
    return report_generator

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "name": "AutoResearcher",
        "message": "Hello from the Self-Initiated Research Agent!",
        "next": "POST /plan with a JSON body: {\"goal\": \"...\"} (stub for now)"
    }

@app.post("/plan", response_model=PlanResponse)
def plan(req: PlanRequest):
    goal = req.goal.strip()
    if len(goal) < 8:
        raise HTTPException(status_code=400, detail="Goal is too short.")
    plan_dict = make_plan(goal)
    # Pydantic v2 will coerce dicts to response model automatically
    return plan_dict

@app.post("/collect")
async def collect(req: CollectRequest):
    goal = req.goal.strip()
    if len(goal) < 8:
        raise HTTPException(status_code=400, detail="Goal is too short.")
    try:
        # Collect from all sources
        result = await collect_from_all_sources(goal, max_results_per_source=req.max_results)
        
        # Rank documents by relevance
        if result.get("documents"):
            ranked_docs = rank_documents_by_relevance(result["documents"], goal)
            result["documents"] = ranked_docs
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-source retrieval failed: {e}")

@app.post("/process")
async def process_documents(req: CollectRequest):
    """Collect documents and process them into embeddings for storage."""
    goal = req.goal.strip()
    if len(goal) < 8:
        raise HTTPException(status_code=400, detail="Goal is too short.")
    
    try:
        # Collect documents
        collection_result = await collect_from_all_sources(goal, max_results_per_source=req.max_results)
        documents = collection_result.get("documents", [])
        
        if not documents:
            return {
                "goal": goal,
                "collection_result": collection_result,
                "processing_result": {"stored_count": 0, "message": "No documents to process"}
            }
        
        # Process and store documents
        processing_result = doc_processor.embed_and_store(documents)
        
        return {
            "goal": goal,
            "collection_result": collection_result,
            "processing_result": processing_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {e}")

@app.get("/search")
async def search_knowledge_base(query: str, max_results: int = 10):
    """Search the processed knowledge base using vector similarity."""
    try:
        results = doc_processor.search_similar(query, n_results=max_results)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge base search failed: {e}")

@app.get("/stats")
async def get_collection_stats():
    """Get statistics about the document collection."""
    try:
        stats = get_doc_processor().get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {e}")


@app.post("/generate-report")
async def generate_research_report(req: PlanRequest):
    """Generate a comprehensive research report for a given goal."""
    goal = req.goal.strip()
    max_results = req.max_results or 15
    if len(goal) < 8:
        raise HTTPException(status_code=400, detail="Goal is too short.")
    
    try:
        # Step 1: Create research plan
        plan_result = make_plan(goal)
        subtopics = plan_result.get("subtopics", [])
        
        # Step 2: Collect documents from all sources
        collection_result = await collect_from_all_sources(goal, max_results_per_source=max_results)
        documents = collection_result.get("documents", [])
        
        if not documents:
            return {
                "goal": goal,
                "report": f"# Research Report: {goal}\n\nNo relevant documents found for this research goal.",
                "plan": plan_result,
                "collection_stats": collection_result
            }
        
        # Step 3: Process and store documents for vector search
        processing_result = get_doc_processor().embed_and_store(documents)
        
        # Step 4: Generate comprehensive report with AI analysis
        report_markdown = await get_report_generator().generate_report(goal, documents, subtopics)
        
        return {
            "goal": goal,
            "report": report_markdown,
            "plan": plan_result,
            "collection_stats": collection_result,
            "processing_stats": processing_result,
            "document_count": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")


# Removed all conversational research endpoints per user request