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
    """Smart deduplication that preserves source diversity and chooses best versions."""
    if not documents:
        return []
    
    # Group potentially duplicate documents
    duplicate_groups = []
    processed = set()
    
    for i, doc1 in enumerate(documents):
        if i in processed:
            continue
            
        title1 = doc1.get("title", "").lower().strip()
        if not title1:
            continue
            
        # Start a new group with this document
        group = [doc1]
        processed.add(i)
        
        # Find similar documents
        for j, doc2 in enumerate(documents[i+1:], i+1):
            if j in processed:
                continue
                
            title2 = doc2.get("title", "").lower().strip()
            if not title2:
                continue
            
            # Check similarity using multiple methods
            similarity = _calculate_title_similarity(title1, title2)
            
            # More conservative threshold - only remove clear duplicates
            if similarity > 0.9:  # Increased from 0.8 to 0.9
                group.append(doc2)
                processed.add(j)
        
        duplicate_groups.append(group)
    
    # Select best document from each group
    unique_docs = []
    source_counts = {"arXiv": 0, "Semantic Scholar": 0, "Wikipedia": 0}
    
    for group in duplicate_groups:
        if len(group) == 1:
            # No duplicates found
            unique_docs.append(group[0])
            source = group[0].get("source", "Unknown")
            source_counts[source] = source_counts.get(source, 0) + 1
        else:
            # Choose best document from duplicates
            best_doc = _select_best_duplicate(group, source_counts)
            unique_docs.append(best_doc)
            source = best_doc.get("source", "Unknown")
            source_counts[source] = source_counts.get(source, 0) + 1
    
    # Sort by relevance and recency
    unique_docs.sort(
        key=lambda x: (
            x.get("year", 0),
            _get_source_priority(x.get("source", "")),
            len(x.get("abstract", ""))  # Prefer documents with abstracts
        ),
        reverse=True
    )
    
    return unique_docs


def _calculate_title_similarity(title1: str, title2: str) -> float:
    """Calculate similarity between two titles using multiple methods."""
    # Method 1: Word overlap (Jaccard similarity)
    words1 = set(title1.split())
    words2 = set(title2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    jaccard = intersection / union if union > 0 else 0.0
    
    # Method 2: Longest common subsequence ratio
    lcs_ratio = _lcs_ratio(title1, title2)
    
    # Method 3: Check for exact substring matches (handles different formatting)
    substring_match = 0.0
    if len(title1) > 20 and len(title2) > 20:  # Only for longer titles
        # Remove common prefixes/suffixes and check core similarity
        core1 = _extract_core_title(title1)
        core2 = _extract_core_title(title2)
        if core1 in core2 or core2 in core1:
            substring_match = 0.3
    
    # Combine methods with weights
    final_similarity = (jaccard * 0.6) + (lcs_ratio * 0.3) + (substring_match * 0.1)
    return final_similarity


def _lcs_ratio(s1: str, s2: str) -> float:
    """Calculate longest common subsequence ratio."""
    def lcs_length(x, y):
        m, n = len(x), len(y)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if x[i-1] == y[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        return dp[m][n]
    
    lcs_len = lcs_length(s1, s2)
    max_len = max(len(s1), len(s2))
    return lcs_len / max_len if max_len > 0 else 0.0


def _extract_core_title(title: str) -> str:
    """Extract core part of title by removing common prefixes/suffixes."""
    # Remove common academic prefixes
    prefixes = ["a study of", "an analysis of", "on the", "towards", "toward"]
    title_lower = title.lower()
    
    for prefix in prefixes:
        if title_lower.startswith(prefix):
            title = title[len(prefix):].strip()
            break
    
    # Remove version numbers, years in parentheses, etc.
    import re
    title = re.sub(r'\([^)]*\d{4}[^)]*\)', '', title)  # Remove years in parentheses
    title = re.sub(r'v\d+(\.\d+)*', '', title)  # Remove version numbers
    
    return title.strip()


def _select_best_duplicate(group: List[Dict[str, Any]], source_counts: Dict[str, int]) -> Dict[str, Any]:
    """Select the best document from a group of duplicates."""
    # Scoring criteria
    def score_document(doc):
        score = 0
        
        # Prefer sources with fewer documents (diversity)
        source = doc.get("source", "Unknown")
        source_count = source_counts.get(source, 0)
        if source_count == 0:
            score += 10  # Strong preference for new sources
        elif source_count < 3:
            score += 5   # Moderate preference for underrepresented sources
        
        # Prefer more recent papers
        year = doc.get("year", 0)
        if year >= 2020:
            score += 5
        elif year >= 2015:
            score += 3
        elif year >= 2010:
            score += 1
        
        # Prefer papers with abstracts
        if doc.get("abstract"):
            score += 3
            # Longer abstracts are often more informative
            abstract_len = len(doc.get("abstract", ""))
            if abstract_len > 500:
                score += 2
            elif abstract_len > 200:
                score += 1
        
        # Prefer papers with author information
        if doc.get("authors"):
            score += 2
        
        # Source quality preference (but lower weight to preserve diversity)
        source_quality = {"arXiv": 2, "Semantic Scholar": 2, "Wikipedia": 1}
        score += source_quality.get(source, 0)
        
        return score
    
    # Select document with highest score
    best_doc = max(group, key=score_document)
    return best_doc


def _get_source_priority(source: str) -> int:
    """Get source priority for sorting."""
    priorities = {"arXiv": 3, "Semantic Scholar": 2, "Wikipedia": 1}
    return priorities.get(source, 0)


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
