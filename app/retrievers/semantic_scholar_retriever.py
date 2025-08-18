"""
Semantic Scholar API retriever for academic papers.
Free tier: 100 requests/5 minutes, 1000 requests/day.
"""
from __future__ import annotations
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime


async def search_semantic_scholar(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Search papers using Semantic Scholar API."""
    base_url = "https://api.semanticscholar.org/graph/v1"
    fields = [
        "paperId", "title", "abstract", "authors", "year", 
        "publicationDate", "journal", "citationCount", "url"
    ]
    
    params = {
        "query": query,
        "limit": min(max_results, 100),  # API limit
        "fields": ",".join(fields)
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                f"{base_url}/paper/search",
                params=params,
                headers={"User-Agent": "AutoResearcher/0.1.0"}
            )
            response.raise_for_status()
            data = response.json()
            
            documents = []
            for paper in data.get("data", []):
                doc = _format_paper(paper)
                if doc:
                    documents.append(doc)
            
            return {
                "query_used": query,
                "documents": documents,
                "total_found": data.get("total", len(documents))
            }
            
        except Exception as e:
            return {
                "query_used": query,
                "documents": [],
                "error": str(e)
            }


def _format_paper(paper: Dict) -> Optional[Dict[str, Any]]:
    """Format Semantic Scholar paper to our Document schema."""
    try:
        # Extract authors
        authors = []
        for author in paper.get("authors", []):
            if isinstance(author, dict) and "name" in author:
                authors.append(author["name"])
            elif isinstance(author, str):
                authors.append(author)
        
        # Handle publication date
        pub_date = paper.get("publicationDate", "")
        year = paper.get("year", 0)
        if not year and pub_date:
            try:
                year = int(pub_date[:4])
            except:
                year = 0
        
        # Format publication date as ISO string
        if pub_date and len(pub_date) >= 4:
            try:
                if len(pub_date) == 4:  # Just year
                    iso_date = f"{pub_date}-01-01T00:00:00Z"
                elif len(pub_date) == 10:  # YYYY-MM-DD
                    iso_date = f"{pub_date}T00:00:00Z"
                else:
                    iso_date = pub_date
            except:
                iso_date = f"{year}-01-01T00:00:00Z" if year else ""
        else:
            iso_date = f"{year}-01-01T00:00:00Z" if year else ""
        
        return {
            "id": paper.get("paperId", ""),
            "title": paper.get("title", "").strip(),
            "authors": authors,
            "abstract": paper.get("abstract", "").strip(),
            "published": iso_date,
            "year": year,
            "source": "Semantic Scholar",
            "categories": [paper.get("journal", {}).get("name", "")] if paper.get("journal") else [],
            "link_pdf": None,  # S2 doesn't provide direct PDF links
            "link_abs": paper.get("url", ""),
            "citation_count": paper.get("citationCount", 0)
        }
    except Exception:
        return None
