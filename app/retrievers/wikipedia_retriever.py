"""
Wikipedia API retriever for background information and definitions.
Uses the free MediaWiki API.
"""
from __future__ import annotations
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
import re


async def search_wikipedia(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Search Wikipedia articles using MediaWiki API."""
    base_url = "https://en.wikipedia.org/api/rest_v1"
    
    # First, search for relevant articles
    search_params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": max_results,
        "srprop": "snippet|titlesnippet|size"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Search for articles
            search_response = await client.get(
                "https://en.wikipedia.org/w/api.php",
                params=search_params,
                headers={"User-Agent": "AutoResearcher/0.1.0"}
            )
            search_response.raise_for_status()
            search_data = search_response.json()
            
            documents = []
            for article in search_data.get("query", {}).get("search", []):
                # Get full article content
                title = article["title"]
                try:
                    content_response = await client.get(
                        f"{base_url}/page/summary/{title.replace(' ', '_')}",
                        headers={"User-Agent": "AutoResearcher/0.1.0"}
                    )
                    content_response.raise_for_status()
                    content_data = content_response.json()
                    
                    doc = _format_wikipedia_article(article, content_data)
                    if doc:
                        documents.append(doc)
                        
                except Exception as e:
                    # If we can't get full content, use search snippet
                    doc = _format_search_result(article)
                    if doc:
                        documents.append(doc)
            
            return {
                "query_used": query,
                "documents": documents,
                "total_found": len(documents)
            }
            
        except Exception as e:
            return {
                "query_used": query,
                "documents": [],
                "error": str(e)
            }


def _format_wikipedia_article(search_result: Dict, content: Dict) -> Optional[Dict[str, Any]]:
    """Format Wikipedia article to our Document schema."""
    try:
        title = content.get("title", search_result.get("title", ""))
        extract = content.get("extract", "")
        
        # Clean HTML from snippet if extract is empty
        if not extract:
            snippet = search_result.get("snippet", "")
            extract = re.sub(r'<[^>]+>', '', snippet)
        
        # Get publication info
        timestamp = content.get("timestamp", "")
        if timestamp:
            try:
                pub_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                iso_date = pub_date.isoformat()
                year = pub_date.year
            except:
                iso_date = datetime.now().isoformat()
                year = datetime.now().year
        else:
            iso_date = datetime.now().isoformat()
            year = datetime.now().year
        
        return {
            "id": f"wikipedia_{title.replace(' ', '_')}",
            "title": title,
            "authors": ["Wikipedia Contributors"],
            "abstract": extract[:500] + "..." if len(extract) > 500 else extract,
            "published": iso_date,
            "year": year,
            "source": "Wikipedia",
            "categories": ["Encyclopedia"],
            "link_pdf": None,
            "link_abs": content.get("content_urls", {}).get("desktop", {}).get("page", ""),
            "page_id": content.get("pageid", search_result.get("pageid", ""))
        }
    except Exception:
        return None


def _format_search_result(search_result: Dict) -> Optional[Dict[str, Any]]:
    """Format Wikipedia search result when full content unavailable."""
    try:
        title = search_result.get("title", "")
        snippet = search_result.get("snippet", "")
        
        # Clean HTML from snippet
        clean_snippet = re.sub(r'<[^>]+>', '', snippet)
        
        return {
            "id": f"wikipedia_{title.replace(' ', '_')}",
            "title": title,
            "authors": ["Wikipedia Contributors"],
            "abstract": clean_snippet,
            "published": datetime.now().isoformat(),
            "year": datetime.now().year,
            "source": "Wikipedia",
            "categories": ["Encyclopedia"],
            "link_pdf": None,
            "link_abs": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
            "page_id": search_result.get("pageid", "")
        }
    except Exception:
        return None
