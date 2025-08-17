from __future__ import annotations
from typing import List, Dict
import re

# domain keyword → extra subtopics to include
DOMAIN_HINTS: Dict[str, List[str]] = {
    "robot": ["Multi-agent coordination", "Swarm communication protocols", "Real-world deployment & logistics"],
    "disaster": ["Incident command systems", "Search & rescue case studies", "Evaluation in constrained environments"],
    "health": ["Clinical validation & safety", "Data privacy & compliance"],
    "finance": ["Risk & compliance", "Market datasets & backtesting"],
    "llm": ["Retrieval-Augmented Generation (RAG)", "Evaluation & hallucination mitigation"],
    "climate": ["Impact pathways", "Datasets & geospatial layers"],
    "education": ["Learning outcomes & pedagogy", "Ethical use & bias"],
}

CORE_SUBTOPICS: List[str] = [
    "Background & definitions",
    "State of the art & key breakthroughs",
    "Methods & approaches",
    "Datasets & benchmarks",
    "Evaluation metrics",
    "Applications & case studies",
    "Challenges, risks & limitations",
    "Open problems & research gaps",
    "Tooling & ecosystem",
]

FREE_SOURCES: List[str] = [
    "arXiv API",
    "Crossref API",
    "Semantic Scholar (free endpoints; rate limits apply)",
    "PubMed / Europe PMC",
    "Wikipedia / MediaWiki API",
    "Hugging Face Datasets",
    "Google Patents (scrape/search; no official free API)",
    "DOAJ (open access journals)",
]

def _normalize_goal(goal: str) -> str:
    g = re.sub(r"\s+", " ", goal).strip()
    # Capitalize first letter, keep rest as-is
    return g[:1].upper() + g[1:] if g else g

def _domain_subtopics(goal: str) -> List[str]:
    g = goal.lower()
    extras: List[str] = []
    for kw, subs in DOMAIN_HINTS.items():
        if kw in g:
            extras.extend(subs)
    # De-dup while preserving order
    seen = set()
    uniq = []
    for s in extras:
        if s not in seen:
            seen.add(s)
            uniq.append(s)
    return uniq

def _rationale(name: str, goal: str) -> str:
    base = {
        "Background & definitions": "Establish common terminology and scope to avoid ambiguity when surveying literature.",
        "State of the art & key breakthroughs": "Identify seminal papers and recent advances that define the field.",
        "Methods & approaches": "Map techniques and architectures used to tackle the goal.",
        "Datasets & benchmarks": "List public datasets and benchmarks used for comparison.",
        "Evaluation metrics": "Clarify how progress is measured to compare methods fairly.",
        "Applications & case studies": "Show real-world usage and lessons learned.",
        "Challenges, risks & limitations": "Surface practical blockers, ethical issues, and failure modes.",
        "Open problems & research gaps": "Highlight under-explored areas and unanswered questions.",
        "Tooling & ecosystem": "Collect libraries, frameworks, and tooling to reproduce results.",
        "Multi-agent coordination": "Essential for scaling to large teams/agents in complex tasks.",
        "Swarm communication protocols": "Covers robustness, latency, and topology effects in coordination.",
        "Real-world deployment & logistics": "Bridges simulation-to-reality and operational constraints.",
        "Incident command systems": "Interfaces with established response workflows and standards.",
        "Search & rescue case studies": "Grounds methods in practical disaster scenarios.",
        "Evaluation in constrained environments": "Captures power, connectivity, and safety constraints.",
        "Clinical validation & safety": "Mandatory evidence for healthcare deployment.",
        "Data privacy & compliance": "Regulatory alignment (HIPAA/GDPR etc.) is crucial.",
        "Risk & compliance": "Financial systems require governance and auditability.",
        "Market datasets & backtesting": "Empirical validation with realistic data splits.",
        "Retrieval-Augmented Generation (RAG)": "Improves correctness by grounding generation in sources.",
        "Evaluation & hallucination mitigation": "Ensures reliability of LLM-based systems.",
        "Impact pathways": "Connect interventions to measurable climate outcomes.",
        "Datasets & geospatial layers": "Spatial data is core for climate & environment analyses.",
        "Learning outcomes & pedagogy": "Ties methods to measurable educational impact.",
        "Ethical use & bias": "Mitigates harms and inequity in learning contexts.",
    }
    return base.get(name, f"Relevant to the goal: {goal}")

def _suggest_queries(goal: str, subtopics: List[str]) -> List[str]:
    def q(x: str) -> str:
        return x.replace("  ", " ").strip()

    basics = [
        f"{goal} literature review",
        f"{goal} survey 2023..2025",
        f"{goal} state of the art",
        f"{goal} open problems",
        f"{goal} datasets AND benchmarks",
        f"{goal} evaluation metrics",
        f"{goal} applications case studies",
    ]

    operators = [
        f'site:arxiv.org "{goal}"',
        f'site:ieeexplore.ieee.org "{goal}"',
        f'site:nature.com "{goal}" review',
        f'site:aclanthology.org "{goal}"',
        f'site:ncbi.nlm.nih.gov "{goal}"',
    ]

    by_topic = [q(f'{goal} "{t}"') for t in subtopics[:6]]  # keep it short
    return [*basics, *operators, *by_topic]

def _next_actions() -> List[str]:
    return [
        "Collect sources from arXiv, Crossref, PubMed and scrape selected open webpages.",
        "Deduplicate and rank by relevance, recency, and credibility.",
        "Chunk, embed (SentenceTransformers), and index in ChromaDB.",
        "Retrieve top-k per subtopic and draft section summaries with citations.",
        "Build knowledge graph (papers↔concepts↔datasets) and render visualization.",
        "Generate a structured report (Markdown/HTML) with references.",
    ]

def make_plan(goal: str):
    ng = _normalize_goal(goal)
    domain = _domain_subtopics(ng)
    subtopics = CORE_SUBTOPICS + domain
    # Create (name, rationale) objects
    st_objs = [{"name": s, "rationale": _rationale(s, ng)} for s in subtopics]
    queries = _suggest_queries(ng, subtopics)
    return {
        "normalized_goal": ng,
        "subtopics": st_objs,
        "suggested_queries": queries,
        "suggested_sources": FREE_SOURCES,
        "next_actions": _next_actions(),
    }
