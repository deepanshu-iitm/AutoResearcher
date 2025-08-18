"""
Test script to demonstrate AutoResearcher functionality.
Run this after starting the FastAPI server with: uvicorn app.main:app --reload
"""
import asyncio
import httpx
import json


async def test_autoresearcher():
    """Test the complete AutoResearcher workflow."""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("🚀 Testing AutoResearcher...")
        
        # Test 1: Health check
        print("\n1. Health Check...")
        response = await client.get(f"{base_url}/healthz")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test 2: Create research plan
        print("\n2. Creating Research Plan...")
        goal = "swarm robotics coordination algorithms"
        plan_response = await client.post(
            f"{base_url}/plan",
            json={"goal": goal}
        )
        print(f"Status: {plan_response.status_code}")
        plan_data = plan_response.json()
        print(f"Normalized Goal: {plan_data.get('normalized_goal')}")
        print(f"Subtopics: {len(plan_data.get('subtopics', []))}")
        print(f"Suggested Queries: {len(plan_data.get('suggested_queries', []))}")
        
        # Test 3: Collect documents from all sources
        print("\n3. Collecting Documents from All Sources...")
        collect_response = await client.post(
            f"{base_url}/collect",
            json={"goal": goal, "max_results": 5}
        )
        print(f"Status: {collect_response.status_code}")
        collect_data = collect_response.json()
        print(f"Total Documents: {collect_data.get('total_documents', 0)}")
        print(f"Sources: {list(collect_data.get('sources', {}).keys())}")
        
        # Test 4: Process documents (embed and store)
        print("\n4. Processing Documents...")
        process_response = await client.post(
            f"{base_url}/process",
            json={"goal": goal, "max_results": 5}
        )
        print(f"Status: {process_response.status_code}")
        process_data = process_response.json()
        processing_result = process_data.get("processing_result", {})
        print(f"Stored Documents: {processing_result.get('stored_count', 0)}")
        
        # Test 5: Search knowledge base
        print("\n5. Searching Knowledge Base...")
        search_response = await client.get(
            f"{base_url}/search",
            params={"query": "coordination algorithms", "max_results": 3}
        )
        print(f"Status: {search_response.status_code}")
        search_data = search_response.json()
        print(f"Search Results: {search_data.get('count', 0)}")
        
        # Test 6: Get collection statistics
        print("\n6. Getting Collection Statistics...")
        stats_response = await client.get(f"{base_url}/stats")
        print(f"Status: {stats_response.status_code}")
        stats_data = stats_response.json()
        print(f"Total Chunks: {stats_data.get('total_chunks', 0)}")
        print(f"Unique Documents: {stats_data.get('unique_documents', 0)}")
        
        # Test 7: Generate comprehensive report
        print("\n7. Generating Comprehensive Report...")
        report_response = await client.post(
            f"{base_url}/generate-report",
            json={"goal": goal}
        )
        print(f"Status: {report_response.status_code}")
        
        if report_response.status_code == 200:
            report_data = report_response.json()
            report_markdown = report_data.get("report", "")
            
            # Save report to file
            with open("research_report.md", "w", encoding="utf-8") as f:
                f.write(report_markdown)
            
            print(f"✅ Report generated successfully!")
            print(f"📄 Report saved to: research_report.md")
            print(f"📊 Documents processed: {report_data.get('document_count', 0)}")
            print(f"📝 Report length: {len(report_markdown)} characters")
        else:
            print(f"❌ Report generation failed: {report_response.text}")


async def test_individual_retrievers():
    """Test individual retriever modules."""
    print("\n🔍 Testing Individual Retrievers...")
    
    # Test arXiv retriever
    print("\n- Testing arXiv retriever...")
    from app.retrievers.arxiv_retriever import search_arxiv
    arxiv_result = search_arxiv("machine learning", max_results=3)
    print(f"  arXiv documents: {len(arxiv_result.get('documents', []))}")
    
    # Test Semantic Scholar retriever
    print("\n- Testing Semantic Scholar retriever...")
    from app.retrievers.semantic_scholar_retriever import search_semantic_scholar
    ss_result = await search_semantic_scholar("neural networks", max_results=3)
    print(f"  Semantic Scholar documents: {len(ss_result.get('documents', []))}")
    
    # Test Wikipedia retriever
    print("\n- Testing Wikipedia retriever...")
    from app.retrievers.wikipedia_retriever import search_wikipedia
    wiki_result = await search_wikipedia("artificial intelligence", max_results=3)
    print(f"  Wikipedia documents: {len(wiki_result.get('documents', []))}")


if __name__ == "__main__":
    print("AutoResearcher Test Suite")
    print("=" * 50)
    
    # Test individual components first
    asyncio.run(test_individual_retrievers())
    
    print("\n" + "=" * 50)
    print("Testing Full API Workflow...")
    print("Make sure the server is running: uvicorn app.main:app --reload")
    print("=" * 50)
    
    # Test full API workflow
    asyncio.run(test_autoresearcher())
    
    print("\n🎉 All tests completed!")
    print("\nNext steps:")
    print("1. Check the generated research_report.md file")
    print("2. Visit http://localhost:8000/docs for API documentation")
    print("3. Try different research goals and explore the results")
