"""
Document processing and embedding system using sentence-transformers.
Handles chunking, embedding, and ChromaDB storage.
"""
from __future__ import annotations
import re
import hashlib
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import os


class DocumentProcessor:
    """Processes documents for embedding and storage in ChromaDB."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", db_path: str = "./chroma_db"):
        """Initialize with embedding model and ChromaDB client."""
        self.model = SentenceTransformer(model_name)
        self.db_path = db_path
        
        # Initialize ChromaDB
        os.makedirs(db_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name="research_documents",
            metadata={"description": "AutoResearcher document embeddings"}
        )
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks for better embedding."""
        if not text or len(text) < chunk_size:
            return [text] if text else []
        
        # Split by sentences first
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed chunk size, save current chunk
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap
                words = current_chunk.split()
                overlap_text = " ".join(words[-overlap:]) if len(words) > overlap else ""
                current_chunk = overlap_text + " " + sentence if overlap_text else sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def process_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a single document into chunks with embeddings."""
        doc_id = document.get("id", "")
        title = document.get("title", "")
        abstract = document.get("abstract", "")
        
        # Combine title and abstract for processing
        full_text = f"{title}. {abstract}" if abstract else title
        
        if not full_text.strip():
            return []
        
        # Create chunks
        chunks = self.chunk_text(full_text)
        processed_chunks = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
            
            processed_chunk = {
                "chunk_id": chunk_id,
                "document_id": doc_id,
                "chunk_index": i,
                "text": chunk,
                "hash": chunk_hash,
                "metadata": {
                    "title": title,
                    "source": document.get("source", ""),
                    "year": document.get("year", 0),
                    "authors": document.get("authors", []),
                    "categories": document.get("categories", []),
                    "link_abs": document.get("link_abs", ""),
                    "link_pdf": document.get("link_pdf", "")
                }
            }
            processed_chunks.append(processed_chunk)
        
        return processed_chunks
    
    def embed_and_store(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process documents, create embeddings, and store in ChromaDB."""
        all_chunks = []
        
        # Process all documents into chunks
        for doc in documents:
            chunks = self.process_document(doc)
            all_chunks.extend(chunks)
        
        if not all_chunks:
            return {"stored_count": 0, "error": "No valid chunks to process"}
        
        # Check for existing chunks to avoid duplicates
        existing_ids = set()
        try:
            existing_data = self.collection.get()
            existing_ids = set(existing_data.get("ids", []))
        except:
            pass
        
        # Filter out existing chunks
        new_chunks = [chunk for chunk in all_chunks if chunk["chunk_id"] not in existing_ids]
        
        if not new_chunks:
            return {"stored_count": 0, "message": "All chunks already exist"}
        
        # Create embeddings
        texts = [chunk["text"] for chunk in new_chunks]
        embeddings = self.model.encode(texts, convert_to_tensor=False).tolist()
        
        # Prepare data for ChromaDB
        ids = [chunk["chunk_id"] for chunk in new_chunks]
        metadatas = [chunk["metadata"] for chunk in new_chunks]
        
        # Add chunk-specific metadata
        for i, chunk in enumerate(new_chunks):
            metadatas[i].update({
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"],
                "hash": chunk["hash"]
            })
        
        try:
            # Store in ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            return {
                "stored_count": len(new_chunks),
                "total_processed": len(all_chunks),
                "skipped_existing": len(all_chunks) - len(new_chunks)
            }
            
        except Exception as e:
            return {"stored_count": 0, "error": str(e)}
    
    def search_similar(self, query: str, n_results: int = 10, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity."""
        try:
            # Create query embedding
            query_embedding = self.model.encode([query], convert_to_tensor=False).tolist()[0]
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                result = {
                    "chunk_id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "distance": results["distances"][0][i],
                    "metadata": results["metadatas"][0][i]
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection."""
        try:
            data = self.collection.get()
            total_chunks = len(data.get("ids", []))
            
            # Count unique documents
            doc_ids = set()
            sources = {}
            years = {}
            
            for metadata in data.get("metadatas", []):
                doc_id = metadata.get("document_id", "")
                if doc_id:
                    doc_ids.add(doc_id)
                
                source = metadata.get("source", "Unknown")
                sources[source] = sources.get(source, 0) + 1
                
                year = metadata.get("year", 0)
                if year:
                    years[year] = years.get(year, 0) + 1
            
            return {
                "total_chunks": total_chunks,
                "unique_documents": len(doc_ids),
                "sources": sources,
                "years": dict(sorted(years.items(), reverse=True)[:10])  # Top 10 years
            }
            
        except Exception as e:
            return {"error": str(e)}
