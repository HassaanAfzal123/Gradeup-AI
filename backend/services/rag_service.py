"""
Enhanced RAG Service with Chr

omaDB, embeddings, and multi-user isolation
"""
import os
import uuid
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from config import settings


class RAGService:
    def __init__(self):
        """Initialize RAG service with ChromaDB and embeddings"""
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Upload directory
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        print(f"[OK] RAG Service initialized with {settings.EMBEDDING_MODEL}")
    
    def _get_user_collection(self, user_id: str):
        """Get or create collection for user"""
        collection_name = f"user_{user_id}"
        return self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"user_id": user_id}
        )
    
    async def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract all text from PDF"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error extracting PDF: {e}")
            return ""
    
    def _chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Chunk text with overlap"""
        words = text.split()
        chunks = []
        chunk_size = settings.CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP
        
        i = 0
        chunk_id = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "start_index": i,
                "end_index": min(i + chunk_size, len(words))
            })
            
            chunk_id += 1
            i += (chunk_size - overlap)  # Move forward with overlap
        
        return chunks
    
    async def index_document(
        self,
        user_id: str,
        file_id: str,
        file_path: str
    ) -> Dict[str, Any]:
        """Extract, chunk, and index PDF into ChromaDB"""
        try:
            # Extract text
            text = await self.extract_text_from_pdf(file_path)
            
            if not text or len(text) < 50:
                return {"success": False, "error": "No text extracted from PDF"}
            
            # Chunk text
            chunks = self._chunk_text(text)
            
            # Generate embeddings
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_model.encode(chunk_texts).tolist()
            
            # Get user collection
            collection = self._get_user_collection(user_id)
            
            # Store in ChromaDB
            collection.add(
                ids=[f"{file_id}_chunk_{i}" for i in range(len(chunks))],
                embeddings=embeddings,
                documents=chunk_texts,
                metadatas=[
                    {
                        "file_id": file_id,
                        "chunk_index": chunk["id"],
                        "user_id": user_id
                    }
                    for chunk in chunks
                ]
            )
            
            return {
                "success": True,
                "total_chunks": len(chunks),
                "total_chars": len(text)
            }
            
        except Exception as e:
            print(f"Error indexing document: {e}")
            return {"success": False, "error": str(e)}
    
    async def query_document(
        self,
        user_id: str,
        file_id: str,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Query document using cosine similarity"""
        try:
            # Get user collection
            collection = self._get_user_collection(user_id)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # Query ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"file_id": file_id}
            )
            
            # Format results
            chunks = []
            if results["documents"] and len(results["documents"][0]) > 0:
                for i in range(len(results["documents"][0])):
                    chunks.append({
                        "text": results["documents"][0][i],
                        "score": 1 - results["distances"][0][i],  # Convert distance to similarity
                        "metadata": results["metadatas"][0][i]
                    })
            
            return {
                "chunks": chunks,
                "query": query,
                "total_results": len(chunks)
            }
            
        except Exception as e:
            print(f"Error querying document: {e}")
            return {"chunks": [], "error": str(e)}
    
    async def get_document_context(
        self,
        user_id: str,
        file_id: str,
        topic: str = None,
        top_k: int = 10
    ) -> str:
        """Get relevant context for quiz generation or summarization"""
        if topic:
            result = await self.query_document(user_id, file_id, topic, top_k=top_k)
        else:
            # Get first N chunks for general context
            collection = self._get_user_collection(user_id)
            results = collection.get(
                where={"file_id": file_id},
                limit=top_k
            )
            
            chunks = results.get("documents", [])
            return "\n\n".join(chunks)
        
        chunks = result.get("chunks", [])
        return "\n\n".join([chunk["text"] for chunk in chunks])
    
    async def delete_document(self, user_id: str, file_id: str) -> bool:
        """Delete all chunks of a document from ChromaDB"""
        try:
            collection = self._get_user_collection(user_id)
            # Delete all chunks with this file_id
            collection.delete(where={"file_id": file_id})
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False


# Singleton instance
rag_service = RAGService()
