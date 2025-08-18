"""
Multi-source retriever that aggregates results from all available sources.
"""
from __future__ import annotations
import asyncio
from typing import List, Dict, Any
from .arxiv_retriever import search_arxiv
from .semantic_scholar_retriever import search_semantic_scholar
from .wikipedia_retriever import search_wikipedia


async def collect_from_all_sources(
    goal: str, 
    max_results_per_source: int = 10,
    sources: List[str] = None
) -> Dict[str, Any]:
    """Collect documents from all available sources asynchronously."""
    
    if sources is None:
        sources = ["arxiv", "semantic_scholar", "wikipedia"]
    
    # Prepare async tasks
    tasks = []
    source_names = []
    
    if "arxiv" in sources:
        # arXiv is synchronous, wrap in async
        async def arxiv_task():
            return search_arxiv(goal, max_results_per_source)
        tasks.append(arxiv_task())
        source_names.append("arxiv")
    
    if "semantic_scholar" in sources:
        tasks.append(search_semantic_scholar(goal, max_results_per_source))
        source_names.append("semantic_scholar")
    
    if "wikipedia" in sources:
        tasks.append(search_wikipedia(goal, max_results_per_source))
        source_names.append("wikipedia")
    
    # Execute all searches concurrently
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        return {
            "goal": goal,
            "total_documents": 0,
            "sources": {},
            "error": f"Failed to execute searches: {str(e)}"
        }
    
    # Aggregate results
    all_documents = []
    source_results = {}
    total_found = 0
    
    for i, result in enumerate(results):
        source_name = source_names[i]
        
        if isinstance(result, Exception):
            source_results[source_name] = {
                "documents": [],
                "error": str(result),
                "count": 0
            }
        elif isinstance(result, dict) and "documents" in result:
            documents = result["documents"]
            all_documents.extend(documents)
            source_results[source_name] = {
                "documents": documents,
                "query_used": result.get("query_used", goal),
                "count": len(documents),
                "total_found": result.get("total_found", len(documents))
            }
            total_found += len(documents)
        else:
            source_results[source_name] = {
                "documents": [],
                "error": "Invalid response format",
                "count": 0
            }
    
    # Remove duplicates based on title similarity
    unique_documents = _deduplicate_documents(all_documents)
    
    return {
        "goal": goal,
        "total_documents": len(unique_documents),
        "unique_documents": len(unique_documents),
        "total_found_across_sources": total_found,
        "documents": unique_documents,
        "sources": source_results
    }


def _deduplicate_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicate documents based on title similarity."""
    if not documents:
        return []
    
    unique_docs = []
    seen_titles = set()
    
    for doc in documents:
        title = doc.get("title", "").lower().strip()
        
        # Simple deduplication based on title
        title_words = set(title.split())
        is_duplicate = False
        
        for seen_title in seen_titles:
            seen_words = set(seen_title.split())
            # If 80% of words overlap, consider it a duplicate
            if title_words and seen_words:
                overlap = len(title_words & seen_words)
                similarity = overlap / max(len(title_words), len(seen_words))
                if similarity > 0.8:
                    is_duplicate = True
                    break
        
        if not is_duplicate and title:
            unique_docs.append(doc)
            seen_titles.add(title)
    
    # Sort by year (newest first) and source priority
    source_priority = {"arXiv": 3, "Semantic Scholar": 2, "Wikipedia": 1}
    
    unique_docs.sort(
        key=lambda x: (
            x.get("year", 0),
            source_priority.get(x.get("source", ""), 0)
        ),
        reverse=True
    )
    
    return unique_docs


def rank_documents_by_relevance(
    documents: List[Dict[str, Any]], 
    goal: str,
    boost_recent: bool = True
) -> List[Dict[str, Any]]:
    """Rank documents by relevance to the goal."""
    import re
    from datetime import datetime
    
    goal_words = set(re.findall(r'\w+', goal.lower()))
    current_year = datetime.now().year
    
    scored_docs = []
    
    for doc in documents:
        score = 0
        
        # Title relevance (highest weight)
        title_words = set(re.findall(r'\w+', doc.get("title", "").lower()))
        title_overlap = len(goal_words & title_words)
        score += title_overlap * 3
        
        # Abstract relevance
        abstract_words = set(re.findall(r'\w+', doc.get("abstract", "").lower()))
        abstract_overlap = len(goal_words & abstract_words)
        score += abstract_overlap * 1
        
        # Recency boost
        if boost_recent:
            year = doc.get("year", 0)
            if year:
                year_diff = current_year - year
                if year_diff <= 2:
                    score += 5  # Very recent
                elif year_diff <= 5:
                    score += 3  # Recent
                elif year_diff <= 10:
                    score += 1  # Somewhat recent
        
        # Source credibility
        source = doc.get("source", "")
        if source == "arXiv":
            score += 2
        elif source == "Semantic Scholar":
            score += 2
        elif source == "Wikipedia":
            score += 1
        
        # Citation count (if available)
        citations = doc.get("citation_count", 0)
        if citations:
            score += min(citations / 100, 5)  # Max 5 points from citations
        
        scored_docs.append((score, doc))
    
    # Sort by score (highest first)
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    
    return [doc for score, doc in scored_docs]
