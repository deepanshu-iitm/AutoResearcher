"""
Report generation system for AutoResearcher.
Creates structured markdown reports with citations.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime
import re


class ReportGenerator:
    """Generates structured research reports from collected documents."""
    
    def __init__(self, doc_processor=None):
        self.doc_processor = doc_processor
    
    def generate_report(
        self, 
        goal: str, 
        documents: List[Dict[str, Any]], 
        subtopics: List[Dict[str, str]] = None
    ) -> str:
        """Generate a comprehensive markdown report."""
        
        # Header
        report = f"# Research Report: {goal}\n\n"
        report += f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"**Total Sources:** {len(documents)}\n\n"
        
        # Executive Summary
        report += self._generate_executive_summary(goal, documents)
        
        # Source Overview
        report += self._generate_source_overview(documents)
        
        # Key Findings by Subtopic
        if subtopics and self.doc_processor:
            report += self._generate_subtopic_analysis(goal, subtopics, documents)
        
        # Recent Developments
        report += self._generate_recent_developments(documents)
        
        # Knowledge Gaps
        report += self._generate_knowledge_gaps(goal, documents)
        
        # References
        report += self._generate_references(documents)
        
        return report
    
    def _generate_executive_summary(self, goal: str, documents: List[Dict[str, Any]]) -> str:
        """Generate executive summary section."""
        summary = "## Executive Summary\n\n"
        
        if not documents:
            summary += "No relevant documents were found for this research goal.\n\n"
            return summary
        
        # Basic statistics
        years = [doc.get("year", 0) for doc in documents if doc.get("year", 0) > 0]
        sources = {}
        for doc in documents:
            source = doc.get("source", "Unknown")
            sources[source] = sources.get(source, 0) + 1
        
        summary += f"This report analyzes **{len(documents)} documents** related to {goal}. "
        
        if years:
            latest_year = max(years)
            earliest_year = min(years)
            summary += f"The research spans from {earliest_year} to {latest_year}, "
            summary += f"with the most recent publications from {latest_year}. "
        
        summary += f"Sources include: {', '.join([f'{k} ({v})' for k, v in sources.items()])}.\n\n"
        
        # Key themes (simple keyword extraction)
        all_text = " ".join([doc.get("title", "") + " " + doc.get("abstract", "") for doc in documents])
        keywords = self._extract_keywords(all_text, goal)
        if keywords:
            summary += f"**Key themes identified:** {', '.join(keywords[:10])}\n\n"
        
        return summary
    
    def _generate_source_overview(self, documents: List[Dict[str, Any]]) -> str:
        """Generate source overview section."""
        overview = "## Source Overview\n\n"
        
        # Group by source
        by_source = {}
        for doc in documents:
            source = doc.get("source", "Unknown")
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(doc)
        
        for source, docs in by_source.items():
            overview += f"### {source} ({len(docs)} documents)\n\n"
            
            # Sort by year (newest first)
            sorted_docs = sorted(docs, key=lambda x: x.get("year", 0), reverse=True)
            
            for doc in sorted_docs[:5]:  # Show top 5 per source
                title = doc.get("title", "Untitled")
                authors = doc.get("authors", [])
                year = doc.get("year", "Unknown")
                
                author_str = ", ".join(authors[:3])  # First 3 authors
                if len(authors) > 3:
                    author_str += " et al."
                
                overview += f"- **{title}** ({year})\n"
                if author_str:
                    overview += f"  - Authors: {author_str}\n"
                
                # Add link if available
                link = doc.get("link_abs") or doc.get("link_pdf")
                if link:
                    overview += f"  - [View Source]({link})\n"
                
                overview += "\n"
            
            if len(docs) > 5:
                overview += f"*... and {len(docs) - 5} more documents*\n\n"
        
        return overview
    
    def _generate_subtopic_analysis(
        self, 
        goal: str, 
        subtopics: List[Dict[str, str]], 
        documents: List[Dict[str, Any]]
    ) -> str:
        """Generate analysis by research subtopics using vector search."""
        analysis = "## Analysis by Research Areas\n\n"
        
        if not self.doc_processor:
            analysis += "*Subtopic analysis requires document processing to be enabled.*\n\n"
            return analysis
        
        for subtopic in subtopics[:8]:  # Limit to top 8 subtopics
            name = subtopic.get("name", "")
            rationale = subtopic.get("rationale", "")
            
            analysis += f"### {name}\n\n"
            analysis += f"*{rationale}*\n\n"
            
            # Search for relevant documents
            relevant_docs = self.doc_processor.search_similar(name, n_results=5)
            
            if relevant_docs:
                analysis += "**Key findings:**\n\n"
                for doc in relevant_docs:
                    metadata = doc.get("metadata", {})
                    title = metadata.get("title", "")
                    source = metadata.get("source", "")
                    
                    if title:
                        analysis += f"- **{title}** ({source})\n"
                        # Add snippet of relevant text
                        text_snippet = doc.get("text", "")[:200]
                        if text_snippet:
                            analysis += f"  - {text_snippet}...\n"
                        analysis += "\n"
            else:
                analysis += "*No specific documents found for this subtopic. This may represent a research gap.*\n\n"
        
        return analysis
    
    def _generate_recent_developments(self, documents: List[Dict[str, Any]]) -> str:
        """Generate recent developments section."""
        developments = "## Recent Developments (Last 3 Years)\n\n"
        
        current_year = datetime.now().year
        recent_docs = [
            doc for doc in documents 
            if doc.get("year", 0) >= current_year - 3
        ]
        
        if not recent_docs:
            developments += "No recent developments found in the collected sources.\n\n"
            return developments
        
        # Sort by year (newest first)
        recent_docs.sort(key=lambda x: x.get("year", 0), reverse=True)
        
        for doc in recent_docs[:10]:  # Top 10 recent papers
            title = doc.get("title", "")
            year = doc.get("year", "")
            authors = doc.get("authors", [])
            abstract = doc.get("abstract", "")
            
            developments += f"### {title} ({year})\n\n"
            
            if authors:
                author_str = ", ".join(authors[:3])
                if len(authors) > 3:
                    author_str += " et al."
                developments += f"**Authors:** {author_str}\n\n"
            
            if abstract:
                # Extract key sentences from abstract
                sentences = re.split(r'[.!?]+', abstract)
                key_sentences = [s.strip() for s in sentences[:2] if s.strip()]
                if key_sentences:
                    developments += f"**Key contribution:** {'. '.join(key_sentences)}.\n\n"
            
            link = doc.get("link_abs") or doc.get("link_pdf")
            if link:
                developments += f"[Read more]({link})\n\n"
            
            developments += "---\n\n"
        
        return developments
    
    def _generate_knowledge_gaps(self, goal: str, documents: List[Dict[str, Any]]) -> str:
        """Identify potential knowledge gaps."""
        gaps = "## Potential Knowledge Gaps\n\n"
        
        # Simple gap identification based on missing keywords and sparse coverage
        all_text = " ".join([doc.get("title", "") + " " + doc.get("abstract", "") for doc in documents])
        
        # Common research areas that might be missing
        potential_gaps = [
            "ethical considerations",
            "real-world deployment",
            "scalability challenges",
            "cost analysis",
            "user studies",
            "comparative evaluation",
            "failure modes",
            "limitations",
            "future work",
            "open problems"
        ]
        
        missing_areas = []
        for gap in potential_gaps:
            if gap.lower() not in all_text.lower():
                missing_areas.append(gap)
        
        if missing_areas:
            gaps += "Based on the collected literature, the following areas may need more research:\n\n"
            for area in missing_areas[:5]:  # Top 5 gaps
                gaps += f"- **{area.title()}**: Limited coverage in current sources\n"
            gaps += "\n"
        
        # Check for temporal gaps
        years = [doc.get("year", 0) for doc in documents if doc.get("year", 0) > 0]
        if years:
            year_range = max(years) - min(years)
            if year_range > 5:
                gaps += f"**Temporal coverage:** Research spans {year_range} years, "
                gaps += "but there may be gaps in certain time periods.\n\n"
        
        gaps += "*Note: These gaps are identified automatically and may not represent actual research needs.*\n\n"
        
        return gaps
    
    def _generate_references(self, documents: List[Dict[str, Any]]) -> str:
        """Generate references section."""
        references = "## References\n\n"
        
        # Sort documents by author last name, then year
        sorted_docs = sorted(documents, key=lambda x: (
            x.get("authors", [""])[0].split()[-1] if x.get("authors") else "",
            x.get("year", 0)
        ))
        
        for i, doc in enumerate(sorted_docs, 1):
            title = doc.get("title", "Untitled")
            authors = doc.get("authors", [])
            year = doc.get("year", "n.d.")
            source = doc.get("source", "")
            
            # Format authors
            if authors:
                if len(authors) == 1:
                    author_str = authors[0]
                elif len(authors) <= 3:
                    author_str = ", ".join(authors[:-1]) + f" & {authors[-1]}"
                else:
                    author_str = f"{authors[0]} et al."
            else:
                author_str = "Unknown Author"
            
            references += f"{i}. {author_str} ({year}). *{title}*. {source}."
            
            # Add link if available
            link = doc.get("link_abs") or doc.get("link_pdf")
            if link:
                references += f" Available at: {link}"
            
            references += "\n\n"
        
        return references
    
    def _extract_keywords(self, text: str, goal: str, max_keywords: int = 20) -> List[str]:
        """Extract key terms from text (simple implementation)."""
        # Remove goal words to avoid bias
        goal_words = set(goal.lower().split())
        
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Common stopwords to exclude
        stopwords = {
            "this", "that", "with", "have", "will", "from", "they", "been", 
            "were", "said", "each", "which", "their", "time", "more", "very",
            "when", "come", "here", "could", "than", "like", "other", "into",
            "after", "first", "well", "also", "where", "much", "before", "through",
            "these", "such", "only", "over", "think", "most", "even", "find",
            "work", "life", "without", "should", "made", "while", "make", "right",
            "still", "being", "now", "may", "never", "down", "way", "too", "any",
            "same", "tell", "does", "set", "three", "want", "air", "well", "also",
            "play", "small", "end", "put", "home", "read", "hand", "port", "large",
            "spell", "add", "even", "land", "here", "must", "big", "high", "such",
            "follow", "act", "why", "ask", "men", "change", "went", "light", "kind",
            "off", "need", "house", "picture", "try", "us", "again", "animal",
            "point", "mother", "world", "near", "build", "self", "earth", "father"
        }
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            if word not in stopwords and word not in goal_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_keywords] if freq > 1]
