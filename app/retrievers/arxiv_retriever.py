from __future__ import annotations
import arxiv
from datetime import datetime, timezone
from typing import List, Dict, Any

# A tiny list of filler words to downweight in queries
STOPWORDS = {
    "latest", "recent", "developments", "the", "a", "an", "for", "in", "of",
    "and", "to", "on", "with", "towards", "into", "about", "overview", "state", "art"
}

def _clean_goal_to_query(goal: str) -> str:
    """
    Turn a user goal into a reasonable arXiv query using fielded search.
    Strategy:
      - Keep key tokens (length>2, not stopwords).
      - If both 'swarm' and 'robotics' appear, add the phrase "swarm robotics".
      - Build an AND query across tokens using arXiv's 'all:' field.
    """
    g = goal.lower().strip()
    tokens = [t for t in _tokenize(g) if t not in STOPWORDS and len(t) > 2]

    phrases = []
    if "swarm" in tokens and "robotics" in tokens:
        phrases.append('"swarm robotics"')
        # keep tokens but remove duplicates of phrase words to avoid over-constraining
        tokens = [t for t in tokens if t not in {"swarm", "robotics"}]

    # Prefer a short, focused query
    # Take up to first 6 tokens after cleaning
    tokens = tokens[:6]

    parts = []
    if phrases:
        parts.extend([f'all:{p}' for p in phrases])
    parts.extend([f'all:"{t}"' for t in tokens])

    if not parts:
        parts = [f'all:"{goal.strip()}"']

    return " AND ".join(parts)

def _tokenize(text: str):
    return [t for t in "".join([c if c.isalnum() else " " for c in text]).split() if t]

def search_arxiv(goal: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Query arXiv and return normalized document dicts.
    """
    query = _clean_goal_to_query(goal)

    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    documents: List[Dict[str, Any]] = []
    for result in search.results():
        # result is arxiv.Result
        published_dt = result.published.replace(tzinfo=timezone.utc) if result.published.tzinfo is None else result.published
        year = published_dt.year

        # pick links
        link_abs = result.entry_id
        link_pdf = None
        try:
            link_pdf = result.pdf_url
        except Exception:
            # Some results may not have a PDF link
            link_pdf = None

        doc = {
            "id": result.entry_id,
            "title": result.title.strip(),
            "authors": [a.name for a in result.authors],
            "abstract": result.summary.strip(),
            "published": published_dt.isoformat(),
            "year": year,
            "source": "arXiv",
            "categories": list(result.categories) if getattr(result, "categories", None) else [],
            "link_pdf": link_pdf,
            "link_abs": link_abs,
        }
        documents.append(doc)

    return {"query_used": query, "documents": documents}
