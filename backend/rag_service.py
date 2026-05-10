"""
Enhanced RAG Service with PDF text extraction and summarization
"""
import os
from pathlib import Path
from typing import List, Dict, Any
import re


class RAGService:
    def __init__(self, chroma_host: str = "localhost", chroma_port: int = 8001):
        """Initialize RAG service with PDF processing"""
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        self.documents = {}  # Store extracted text by file_id
        print("✅ RAG Service initialized (Lightweight mode)")
        
    async def index_document(self, file_id: str, file_path: str) -> bool:
        """Extract and index PDF text"""
        try:
            # Extract text from PDF
            text = await self._extract_pdf_text(file_path)
            self.documents[file_id] = text
            print(f"✅ Indexed document {file_id} ({len(text)} characters)")
            return True
        except Exception as e:
            print(f"Error indexing: {e}")
            return False
    
    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            # Try using pypdf if available
            try:
                import pypdf
                with open(file_path, 'rb') as file:
                    reader = pypdf.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                # Fallback: return placeholder text
                return f"PDF content placeholder. Install pypdf for actual extraction."
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"
    
    async def summarize_document(self, file_id: str) -> Dict[str, Any]:
        """Generate a summary of the document"""
        if file_id not in self.documents:
            return {"error": "Document not found"}
        
        text = self.documents[file_id]
        
        # Extract key info
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 20]
        word_count = len(text.split())
        
        # Find key topics (capitalized words appearing multiple times)
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        from collections import Counter
        common_topics = [word for word, count in Counter(words).most_common(10) if count > 1]
        
        # Create summary
        summary = {
            "word_count": word_count,
            "total_sentences": len(sentences),
            "key_topics": common_topics[:5],
            "first_sentences": sentences[:3] if sentences else [],
            "overview": " ".join(sentences[:3]) if sentences else "No content available"
        }
        
        return summary
    
    async def query_document(
        self, 
        file_id: str, 
        query: str, 
        top_k: int = 3
    ) -> Dict[str, Any]:
        """Query document for relevant content"""
        if file_id not in self.documents:
            return {"error": "Document not indexed"}
        
        text = self.documents[file_id]
        
        # Simple keyword-based retrieval
        query_words = set(query.lower().split())
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 20]
        
        # Score sentences by keyword matches
        scored_sentences = []
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            score = len(query_words.intersection(sentence_words))
            if score > 0:
                scored_sentences.append((sentence, score))
        
        # Get top matches
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        top_matches = scored_sentences[:top_k]
        
        sources = [
            {
                "text": sent,
                "score": score / len(query_words) if query_words else 0,
                "metadata": {}
            }
            for sent, score in top_matches
        ]
        
        response = " ".join([s["text"] for s in sources])
        
        return {
            "response": response or f"Information about {query}",
            "sources": sources
        }
    
    async def get_document_context(self, file_id: str, topic: str = None) -> str:
        """Get relevant document context"""
        if file_id not in self.documents:
            return ""
        
        text = self.documents[file_id]
        
        if topic:
            # Find topic-relevant sections
            result = await self.query_document(file_id, topic, top_k=5)
            return result.get("response", text[:1000])
        
        # Return first 1000 chars
        return text[:1000]


# Singleton instance
rag_service = RAGService()
