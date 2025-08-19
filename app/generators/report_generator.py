"""
Report generation system for AutoResearcher.
Creates structured markdown reports with citations.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import asyncio


class ReportGenerator:
    """Generates structured research reports from collected documents."""
    
    def __init__(self, doc_processor=None, ai_service=None):
        self.doc_processor = doc_processor
        self.ai_service = ai_service
    
    async def generate_report(
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
        if subtopics:
            report += self._generate_subtopic_analysis(subtopics, documents)
        
        # Recent Developments
        report += self._generate_recent_developments(documents)
        
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
        subtopics: List[Dict[str, str]], 
        documents: List[Dict[str, Any]]
    ) -> str:
        """Generate analysis by research subtopics using direct document mapping."""
        analysis = "## Analysis by Research Areas\n\n"
        
        for subtopic in subtopics[:8]:  # Limit to top 8 subtopics
            name = subtopic.get("name", "")
            rationale = subtopic.get("rationale", "")
            
            analysis += f"### {name}\n\n"
            analysis += f"*{rationale}*\n\n"
            
            # Find relevant documents using keyword matching
            relevant_docs = self._find_relevant_documents(name, documents, max_docs=3)
            
            if relevant_docs:
                analysis += "**Key findings:**\n\n"
                for doc in relevant_docs:
                    title = doc.get("title", "")
                    source = doc.get("source", "")
                    authors = doc.get("authors", [])
                    
                    if title:
                        author_str = ", ".join(authors[:3]) if authors else "Unknown"
                        if len(authors) > 3:
                            author_str += " et al."
                        
                        analysis += f"- **{title}** ({source})\n"
                        analysis += f"  - Authors: {author_str}\n"
                        
                        # Add snippet from abstract
                        abstract = doc.get("abstract", "")[:300]
                        if abstract:
                            analysis += f"  - {abstract}...\n"
                        analysis += "\n"
            else:
                analysis += "*No specific documents found for this subtopic. This may represent a research gap.*\n\n"
        
        return analysis
    
    def _find_relevant_documents(self, subtopic: str, documents: List[Dict[str, Any]], max_docs: int = 3) -> List[Dict[str, Any]]:
        """Find documents relevant to a subtopic using keyword matching."""
        relevant = []
        subtopic_keywords = subtopic.lower().split()
        
        for doc in documents:
            title = doc.get("title", "").lower()
            abstract = doc.get("abstract", "").lower()
            categories = " ".join(doc.get("categories", [])).lower()
            
            # Calculate relevance score based on keyword matches
            score = 0
            for keyword in subtopic_keywords:
                if keyword in title:
                    score += 3  # Title matches are most important
                if keyword in abstract:
                    score += 2  # Abstract matches are important
                if keyword in categories:
                    score += 1  # Category matches are least important
            
            if score > 0:
                doc_with_score = doc.copy()
                doc_with_score["relevance_score"] = score
                relevant.append(doc_with_score)
        
        # Sort by relevance score and return top documents
        relevant.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return relevant[:max_docs]
    
    def _analyze_temporal_gaps(self, documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Identify temporal gaps in research coverage."""
        gaps = []
        current_year = datetime.now().year
        
        # Analyze publication years
        years = [doc.get("year", 0) for doc in documents if doc.get("year", 0) > 0]
        if not years:
            return gaps
        
        latest_year = max(years)
        year_counts = {}
        for year in years:
            year_counts[year] = year_counts.get(year, 0) + 1
        
        # Check for recent research gaps
        if latest_year < current_year - 1:
            gaps.append({
                "area": "Recent Research",
                "description": f"Limited research from {current_year-1}-{current_year}. Most recent papers are from {latest_year}."
            })
        
        # Check for historical gaps
        year_range = current_year - min(years)
        if year_range > 5:
            missing_years = []
            for year in range(min(years), current_year):
                if year not in year_counts:
                    missing_years.append(year)
            
            if len(missing_years) > 2:
                gaps.append({
                    "area": "Historical Coverage",
                    "description": f"Limited research coverage in {len(missing_years)} years between {min(years)} and {current_year}."
                })
        
        return gaps
    
    def _analyze_coverage_gaps(self, goal: str, documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Identify coverage gaps in research topics."""
        gaps = []
        
        # Analyze common research aspects that might be missing
        aspects_to_check = {
            "evaluation": ["evaluation", "benchmark", "metric", "performance", "assessment"],
            "implementation": ["implementation", "deployment", "system", "architecture", "framework"],
            "ethics": ["ethics", "ethical", "bias", "fairness", "responsibility", "privacy"],
            "scalability": ["scalability", "scale", "large-scale", "distributed", "parallel"],
            "real-world": ["real-world", "practical", "industry", "production", "deployment"],
            "comparison": ["comparison", "comparative", "versus", "vs", "benchmark"],
            "limitations": ["limitation", "challenge", "problem", "issue", "difficulty"],
            "future": ["future", "direction", "trend", "outlook", "next"]
        }
        
        # Count mentions of each aspect
        aspect_counts = {aspect: 0 for aspect in aspects_to_check}
        
        for doc in documents:
            title = doc.get("title", "").lower()
            abstract = doc.get("abstract", "").lower()
            content = f"{title} {abstract}"
            
            for aspect, keywords in aspects_to_check.items():
                for keyword in keywords:
                    if keyword in content:
                        aspect_counts[aspect] += 1
                        break
        
        total_docs = len(documents)
        
        # Identify under-represented aspects
        for aspect, count in aspect_counts.items():
            coverage_ratio = count / total_docs if total_docs > 0 else 0
            
            if coverage_ratio < 0.2:  # Less than 20% coverage
                aspect_name = aspect.replace("_", " ").title()
                if aspect == "evaluation":
                    gaps.append({
                        "area": f"{aspect_name} Studies",
                        "description": f"Limited evaluation and benchmarking studies found ({count}/{total_docs} documents).",
                        "suggestion": "Comprehensive evaluation frameworks and standardized benchmarks needed."
                    })
                elif aspect == "ethics":
                    gaps.append({
                        "area": f"Ethical Considerations",
                        "description": f"Minimal discussion of ethical implications ({count}/{total_docs} documents).",
                        "suggestion": "Research on bias, fairness, and responsible deployment needed."
                    })
                elif aspect == "real-world":
                    gaps.append({
                        "area": f"Practical Applications",
                        "description": f"Limited real-world deployment studies ({count}/{total_docs} documents).",
                        "suggestion": "Industry case studies and production deployment research needed."
                    })
        
        return gaps
    
    def _analyze_methodological_gaps(self, documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Identify methodological gaps in research approaches."""
        gaps = []
        
        # Analyze research methodologies
        methodologies = {
            "experimental": ["experiment", "experimental", "empirical", "study"],
            "theoretical": ["theoretical", "theory", "mathematical", "formal"],
            "survey": ["survey", "review", "systematic", "meta-analysis"],
            "simulation": ["simulation", "simulate", "model", "modeling"],
            "case_study": ["case study", "case-study", "real-world", "practical"]
        }
        
        method_counts = {method: 0 for method in methodologies}
        
        for doc in documents:
            title = doc.get("title", "").lower()
            abstract = doc.get("abstract", "").lower()
            content = f"{title} {abstract}"
            
            for method, keywords in methodologies.items():
                for keyword in keywords:
                    if keyword in content:
                        method_counts[method] += 1
                        break
        
        total_docs = len(documents)
        
        # Identify methodological gaps
        for method, count in method_counts.items():
            coverage_ratio = count / total_docs if total_docs > 0 else 0
            
            if coverage_ratio < 0.15:  # Less than 15% coverage
                method_name = method.replace("_", " ").title()
                if method == "experimental":
                    gaps.append({
                        "area": f"{method_name} Validation",
                        "description": f"Limited experimental validation studies ({count}/{total_docs} documents)."
                    })
                elif method == "case_study":
                    gaps.append({
                        "area": f"Case Studies",
                        "description": f"Few real-world case studies available ({count}/{total_docs} documents)."
                    })
        
        return gaps
    
    def _analyze_cross_domain_gaps(self, goal: str, documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Identify cross-domain research opportunities."""
        gaps = []
        
        # Extract domains from categories and titles
        domains = set()
        for doc in documents:
            categories = doc.get("categories", [])
            for cat in categories:
                if isinstance(cat, str):
                    domains.add(cat.split(".")[0])  # Get main category
        
        # Identify potential cross-domain opportunities
        common_domains = ["cs", "physics", "math", "stat", "bio", "econ", "q-fin"]
        present_domains = domains.intersection(common_domains)
        
        if len(present_domains) < 2:
            gaps.append({
                "area": "Interdisciplinary Research",
                "description": "Limited cross-domain collaboration evident in current literature.",
                "potential": "Opportunities for interdisciplinary approaches combining multiple fields."
            })
        
        # Check for specific cross-domain opportunities based on goal
        goal_lower = goal.lower()
        if "machine learning" in goal_lower or "ai" in goal_lower:
            if "bio" not in domains and "physics" not in domains:
                gaps.append({
                    "area": "AI Applications",
                    "description": "Potential for applying AI methods to other scientific domains.",
                    "potential": "Cross-pollination with biology, physics, or other sciences."
                })
        
        return gaps
    
    def _generate_research_recommendations(self, goal: str, documents: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate specific research recommendations based on gap analysis."""
        recommendations = []
        
        # Analyze current research trends
        recent_docs = [doc for doc in documents if doc.get("year", 0) >= datetime.now().year - 2]
        
        if len(recent_docs) < len(documents) * 0.3:  # Less than 30% recent
            recommendations.append({
                "title": "Contemporary Research Update",
                "rationale": "Current literature review shows limited recent publications. Field may benefit from updated research.",
                "methods": "Systematic literature review, expert interviews, trend analysis",
                "impact": "Establish current state-of-the-art and identify emerging directions"
            })
        
        # Check for evaluation gaps
        eval_keywords = ["evaluation", "benchmark", "metric", "performance"]
        eval_docs = []
        for doc in documents:
            content = f"{doc.get('title', '')} {doc.get('abstract', '')}".lower()
            if any(keyword in content for keyword in eval_keywords):
                eval_docs.append(doc)
        
        if len(eval_docs) < len(documents) * 0.25:  # Less than 25% evaluation
            recommendations.append({
                "title": "Comprehensive Evaluation Framework",
                "rationale": "Limited evaluation studies found. Standardized assessment methods needed.",
                "methods": "Benchmark development, comparative studies, metric validation",
                "impact": "Enable fair comparison and accelerate field progress"
            })
        
        # Domain-specific recommendations
        goal_lower = goal.lower()
        if "quantum" in goal_lower:
            recommendations.append({
                "title": "Quantum-Classical Hybrid Approaches",
                "rationale": "Opportunity to bridge quantum and classical computing paradigms.",
                "methods": "Hybrid algorithm development, performance comparison studies",
                "impact": "Practical quantum computing applications in near-term devices"
            })
        elif "climate" in goal_lower or "environment" in goal_lower:
            recommendations.append({
                "title": "Policy-Technology Integration Studies",
                "rationale": "Technical solutions need policy framework integration for real-world impact.",
                "methods": "Policy analysis, stakeholder interviews, implementation case studies",
                "impact": "Bridge gap between technical research and practical deployment"
            })
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
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
    

    async def _generate_knowledge_gaps(self, goal: str, documents: List[Dict[str, Any]]) -> str:
        """Generate AI-powered knowledge gaps analysis."""
        gaps = "## Knowledge Gap Analysis\n\n"
        
        if not documents:
            gaps += "No documents available for gap analysis.\n\n"
            return gaps
        
        # Use AI analysis service if available
        if self.ai_service:
            try:
                ai_analysis = await self.ai_service.analyze_knowledge_gaps(goal, documents)
                gaps += "**Our AI analysis has identified the following research gaps and opportunities:**\n\n"
                
                # Temporal gaps
                if ai_analysis.get("temporal_gaps"):
                    gaps += "### ⏰ Temporal Research Gaps\n\n"
                    for gap in ai_analysis["temporal_gaps"][:5]:  # Limit to top 5
                        gaps += f"- {gap}\n"
                    gaps += "\n"
                
                # Coverage gaps
                if ai_analysis.get("coverage_gaps"):
                    gaps += "### 🎯 Coverage Gaps\n\n"
                    for gap in ai_analysis["coverage_gaps"][:5]:
                        gaps += f"- {gap}\n"
                    gaps += "\n"
                
                # Methodological gaps
                if ai_analysis.get("methodological_gaps"):
                    gaps += "### 🔬 Methodological Gaps\n\n"
                    for gap in ai_analysis["methodological_gaps"][:5]:
                        gaps += f"- {gap}\n"
                    gaps += "\n"
                
                # Cross-domain opportunities
                if ai_analysis.get("cross_domain_opportunities"):
                    gaps += "### 🌐 Cross-Domain Opportunities\n\n"
                    for opp in ai_analysis["cross_domain_opportunities"][:5]:
                        gaps += f"- {opp}\n"
                    gaps += "\n"
                
                # Research recommendations
                if ai_analysis.get("research_recommendations"):
                    gaps += "### 💡 AI-Generated Research Recommendations\n\n"
                    for i, rec in enumerate(ai_analysis["research_recommendations"][:5], 1):
                        gaps += f"{i}. {rec}\n"
                    gaps += "\n"
                
                # Add confidence score
                confidence = ai_analysis.get("confidence_score", 0.8)
                gaps += f"*AI Analysis Confidence: {confidence:.1%}*\n\n"
                
                return gaps
                
            except Exception as e:
                gaps += f"*AI analysis temporarily unavailable. Using fallback analysis. Error: {str(e)}*\n\n"
        
        # Fallback to original heuristic analysis
        temporal_gaps = self._analyze_temporal_gaps(documents)
        coverage_gaps = self._analyze_coverage_gaps(goal, documents)
        methodological_gaps = self._analyze_methodological_gaps(documents)
        cross_domain_gaps = self._analyze_cross_domain_gaps(goal, documents)
        
        gaps += "**Heuristic analysis has identified the following research gaps:**\n\n"
        
        # Temporal gaps
        if temporal_gaps:
            gaps += "### 📅 Temporal Research Gaps\n\n"
            for gap in temporal_gaps:
                gaps += f"• **{gap['area']}**: {gap['description']}\n"
            gaps += "\n"
        
        # Coverage gaps
        if coverage_gaps:
            gaps += "### 🔍 Coverage Gaps\n\n"
            for gap in coverage_gaps:
                gaps += f"• **{gap['area']}**: {gap['description']}\n"
                if gap.get('suggestion'):
                    gaps += f"  - *Suggested research direction*: {gap['suggestion']}\n"
            gaps += "\n"
        
        # Methodological gaps
        if methodological_gaps:
            gaps += "### 🔬 Methodological Gaps\n\n"
            for gap in methodological_gaps:
                gaps += f"• **{gap['area']}**: {gap['description']}\n"
            gaps += "\n"
        
        # Cross-domain opportunities
        if cross_domain_gaps:
            gaps += "### 🌐 Cross-Domain Opportunities\n\n"
            for gap in cross_domain_gaps:
                gaps += f"• **{gap['area']}**: {gap['description']}\n"
                if gap.get('potential'):
                    gaps += f"  - *Potential impact*: {gap['potential']}\n"
            gaps += "\n"
        
        # Research recommendations
        recommendations = self._generate_research_recommendations(goal, documents)
        if recommendations:
            gaps += "### 💡 Recommended Research Directions\n\n"
            for i, rec in enumerate(recommendations, 1):
                gaps += f"{i}. **{rec['title']}**\n"
                gaps += f"   - *Rationale*: {rec['rationale']}\n"
                gaps += f"   - *Potential methods*: {rec['methods']}\n"
                gaps += f"   - *Expected impact*: {rec['impact']}\n\n"
        
        gaps += "*Note: This analysis is generated by AI and represents potential research opportunities based on the collected literature.*\n\n"
        
        return gaps
    
    def _generate_references(self, documents: List[Dict[str, Any]]) -> str:
        """Generate references section."""
        if not documents:
            return "## References\n\nNo references available.\n"
        
        references = "## References\n"
        
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
