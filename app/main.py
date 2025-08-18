from fastapi import FastAPI, HTTPException
from app.schemas import PlanRequest, PlanResponse, Subtopic, CollectRequest, CollectResponse
from app.planner import make_plan
from app.retrievers.arxiv_retriever import search_arxiv
from app.retrievers.multi_source_retriever import collect_from_all_sources, rank_documents_by_relevance
from app.processors.document_processor import DocumentProcessor
from app.generators.report_generator import ReportGenerator
import asyncio

app = FastAPI(title="AutoResearcher", version="0.1.0")

# Initialize document processor and report generator
doc_processor = DocumentProcessor()
report_generator = ReportGenerator(doc_processor)

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
        stats = doc_processor.get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {e}")


@app.post("/generate-report")
async def generate_research_report(req: PlanRequest):
    """Generate a comprehensive research report for a given goal."""
    goal = req.goal.strip()
    if len(goal) < 8:
        raise HTTPException(status_code=400, detail="Goal is too short.")
    
    try:
        # Step 1: Create research plan
        plan_result = make_plan(goal)
        subtopics = plan_result.get("subtopics", [])
        
        # Step 2: Collect documents from all sources
        collection_result = await collect_from_all_sources(goal, max_results_per_source=15)
        documents = collection_result.get("documents", [])
        
        if not documents:
            return {
                "goal": goal,
                "report": f"# Research Report: {goal}\n\nNo relevant documents found for this research goal.",
                "plan": plan_result,
                "collection_stats": collection_result
            }
        
        # Step 3: Process and store documents for vector search
        processing_result = doc_processor.embed_and_store(documents)
        
        # Step 4: Generate comprehensive report
        report_markdown = report_generator.generate_report(goal, documents, subtopics)
        
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