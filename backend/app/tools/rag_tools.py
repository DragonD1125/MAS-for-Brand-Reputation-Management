"""
RAG (Retrieval-Augmented Generation) Tools for Brand Knowledge Management
This gives our AI system a searchable memory of brand facts, policies, and approved responses
"""

import asyncio
import time
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import json
import uuid

import chromadb
from sentence_transformers import SentenceTransformer
from langchain.tools import BaseTool
from loguru import logger

from app.core.config import settings


@dataclass
class KnowledgeDocument:
    """Structured knowledge document for the brand knowledge base"""
    id: str
    title: str
    content: str
    document_type: str  # policy, faq, response_template, brand_info, etc.
    brand_name: str
    category: str
    tags: List[str]
    confidence_level: float  # 0.0 to 1.0 - how confident we are in this information
    last_updated: datetime
    source: str
    metadata: Dict[str, Any]


class BrandKnowledgeRAG:
    """Advanced RAG system for brand knowledge management"""
    
    def __init__(self, collection_name: str = "brand_knowledge_base"):
        self.collection_name = collection_name
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.documents_cache = {}  # Cache for document metadata
        
        # Initialize the system
        self._initialize_rag_system()
        
        logger.info(f"🧠 Brand Knowledge RAG system initialized with collection: {collection_name}")
    
    def _initialize_rag_system(self):
        """Initialize the RAG system components"""
        try:
            # Initialize sentence transformer model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Embedding model loaded: all-MiniLM-L6-v2")
            
            # Initialize ChromaDB
            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Brand knowledge base for RAG system"}
            )
            logger.info(f"✅ ChromaDB collection initialized: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"❌ RAG system initialization failed: {e}")
            raise
    
    def add_knowledge_document(
        self, 
        document: KnowledgeDocument
    ) -> bool:
        """Add a knowledge document to the vector store"""
        try:
            # Generate embedding for the document content
            embedding = self.embedding_model.encode(document.content).tolist()
            
            # Prepare metadata
            metadata = {
                "title": document.title,
                "document_type": document.document_type,
                "brand_name": document.brand_name,
                "category": document.category,
                "confidence_level": document.confidence_level,
                "last_updated": document.last_updated.isoformat(),
                "source": document.source,
                "tags": json.dumps(document.tags)
            }
            metadata.update(document.metadata)
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[document.content],
                metadatas=[metadata],
                ids=[document.id]
            )
            
            # Cache the document
            self.documents_cache[document.id] = document
            
            logger.info(f"✅ Knowledge document added: {document.title} ({document.document_type})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add knowledge document {document.title}: {e}")
            return False
    
    def retrieve_relevant_knowledge(
        self, 
        query: str, 
        brand_name: str = None,
        document_types: List[str] = None,
        n_results: int = 5,
        confidence_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge documents for a query"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Prepare filters
            where_filter = {}
            if brand_name:
                where_filter["brand_name"] = {"$eq": brand_name}
            if document_types:
                where_filter["document_type"] = {"$in": document_types}
            if confidence_threshold > 0:
                where_filter["confidence_level"] = {"$gte": confidence_threshold}
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            # Process results
            relevant_docs = []
            if results['documents'][0]:  # Check if results exist
                for i, (doc_id, document, metadata, distance) in enumerate(zip(
                    results['ids'][0],
                    results['documents'][0], 
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    
                    # Calculate similarity score (ChromaDB returns distances, we want similarity)
                    similarity_score = 1.0 - distance
                    
                    relevant_doc = {
                        "id": doc_id,
                        "content": document,
                        "title": metadata.get("title", "Unknown"),
                        "document_type": metadata.get("document_type", "unknown"),
                        "brand_name": metadata.get("brand_name", ""),
                        "category": metadata.get("category", ""),
                        "confidence_level": metadata.get("confidence_level", 0.0),
                        "source": metadata.get("source", ""),
                        "similarity_score": similarity_score,
                        "last_updated": metadata.get("last_updated", ""),
                        "tags": json.loads(metadata.get("tags", "[]")),
                        "metadata": metadata
                    }
                    relevant_docs.append(relevant_doc)
            
            logger.info(f"🔍 Retrieved {len(relevant_docs)} relevant documents for query: '{query[:50]}...'")
            return relevant_docs
            
        except Exception as e:
            logger.error(f"❌ Knowledge retrieval failed for query '{query}': {e}")
            return []
    
    def update_knowledge_document(
        self, 
        document_id: str, 
        updated_document: KnowledgeDocument
    ) -> bool:
        """Update an existing knowledge document"""
        try:
            # Delete the old document
            self.collection.delete(ids=[document_id])
            
            # Add the updated document
            updated_document.id = document_id  # Keep the same ID
            return self.add_knowledge_document(updated_document)
            
        except Exception as e:
            logger.error(f"❌ Failed to update knowledge document {document_id}: {e}")
            return False
    
    def delete_knowledge_document(self, document_id: str) -> bool:
        """Delete a knowledge document"""
        try:
            self.collection.delete(ids=[document_id])
            if document_id in self.documents_cache:
                del self.documents_cache[document_id]
            
            logger.info(f"✅ Knowledge document deleted: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to delete knowledge document {document_id}: {e}")
            return False
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            # Get collection count
            collection_count = self.collection.count()
            
            # Analyze document types and brands
            all_docs = self.collection.get()
            
            document_types = {}
            brands = {}
            categories = {}
            
            if all_docs['metadatas']:
                for metadata in all_docs['metadatas']:
                    # Count document types
                    doc_type = metadata.get('document_type', 'unknown')
                    document_types[doc_type] = document_types.get(doc_type, 0) + 1
                    
                    # Count brands
                    brand = metadata.get('brand_name', 'unknown')
                    brands[brand] = brands.get(brand, 0) + 1
                    
                    # Count categories
                    category = metadata.get('category', 'unknown')
                    categories[category] = categories.get(category, 0) + 1
            
            return {
                "total_documents": collection_count,
                "document_types": document_types,
                "brands": brands,
                "categories": categories,
                "collection_name": self.collection_name,
                "embedding_model": "all-MiniLM-L6-v2",
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get knowledge base stats: {e}")
            return {"error": str(e)}


class KnowledgeRetrievalTool(BaseTool):
    """LangChain tool for retrieving brand knowledge"""
    
    name: str = "retrieve_brand_knowledge"
    description: str = "Retrieve relevant brand information, policies, FAQs, or approved responses from the knowledge base. Always use this before generating responses."
    
    def __init__(self, rag_system: BrandKnowledgeRAG):
        super().__init__()
        self.rag_system = rag_system
    
    def _run(self, query: str, brand_name: str = "", document_types: str = "", max_results: int = 5) -> str:
        """Retrieve knowledge synchronously"""
        try:
            # Parse document types
            doc_types = [dt.strip() for dt in document_types.split(",")] if document_types else None
            
            # Retrieve relevant documents
            relevant_docs = self.rag_system.retrieve_relevant_knowledge(
                query=query,
                brand_name=brand_name if brand_name else None,
                document_types=doc_types,
                n_results=max_results
            )
            
            if not relevant_docs:
                return json.dumps({
                    "status": "no_results",
                    "message": "No relevant brand knowledge found for this query.",
                    "query": query,
                    "suggestion": "Consider adding relevant brand information to the knowledge base."
                })
            
            # Format results for LLM consumption
            formatted_results = {
                "status": "success",
                "query": query,
                "results_count": len(relevant_docs),
                "relevant_knowledge": []
            }
            
            for doc in relevant_docs:
                formatted_doc = {
                    "title": doc["title"],
                    "content": doc["content"],
                    "document_type": doc["document_type"],
                    "confidence_level": doc["confidence_level"],
                    "similarity_score": doc["similarity_score"],
                    "source": doc["source"],
                    "category": doc["category"]
                }
                formatted_results["relevant_knowledge"].append(formatted_doc)
            
            return json.dumps(formatted_results, indent=2)
            
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e),
                "query": query
            })
    
    async def _arun(self, query: str, brand_name: str = "", document_types: str = "", max_results: int = 5) -> str:
        """Retrieve knowledge asynchronously"""
        return self._run(query, brand_name, document_types, max_results)


class KnowledgeAdditionTool(BaseTool):
    """LangChain tool for adding knowledge to the brand knowledge base"""
    
    name: str = "add_brand_knowledge"
    description: str = "Add new brand information, policies, FAQs, or approved responses to the knowledge base."
    
    def __init__(self, rag_system: BrandKnowledgeRAG):
        super().__init__()
        self.rag_system = rag_system
    
    def _run(
        self, 
        title: str, 
        content: str, 
        document_type: str = "general", 
        brand_name: str = "",
        category: str = "general",
        confidence_level: float = 0.8
    ) -> str:
        """Add knowledge synchronously"""
        try:
            # Create knowledge document
            document = KnowledgeDocument(
                id=str(uuid.uuid4()),
                title=title,
                content=content,
                document_type=document_type,
                brand_name=brand_name,
                category=category,
                tags=[],  # Could be extracted from content
                confidence_level=confidence_level,
                last_updated=datetime.utcnow(),
                source="agent_added",
                metadata={}
            )
            
            # Add to knowledge base
            success = self.rag_system.add_knowledge_document(document)
            
            if success:
                return json.dumps({
                    "status": "success",
                    "message": f"Knowledge document '{title}' added successfully.",
                    "document_id": document.id,
                    "document_type": document_type
                })
            else:
                return json.dumps({
                    "status": "error",
                    "message": "Failed to add knowledge document."
                })
                
        except Exception as e:
            return json.dumps({
                "status": "error",
                "error": str(e)
            })
    
    async def _arun(
        self, 
        title: str, 
        content: str, 
        document_type: str = "general", 
        brand_name: str = "",
        category: str = "general",
        confidence_level: float = 0.8
    ) -> str:
        """Add knowledge asynchronously"""
        return self._run(title, content, document_type, brand_name, category, confidence_level)


class BrandKnowledgeManager:
    """High-level manager for brand knowledge operations"""
    
    def __init__(self):
        self.rag_system = BrandKnowledgeRAG()
        self.knowledge_retrieval_tool = KnowledgeRetrievalTool(self.rag_system)
        self.knowledge_addition_tool = KnowledgeAdditionTool(self.rag_system)
        
        # Pre-populate with some essential knowledge types
        self._initialize_default_knowledge()
        
        logger.info("🧠 Brand Knowledge Manager initialized")
    
    def _initialize_default_knowledge(self):
        """Initialize with some default brand knowledge templates"""
        default_documents = [
            KnowledgeDocument(
                id="default_response_policy",
                title="Default Response Policy",
                content="Always be polite, professional, and helpful. Acknowledge concerns promptly. If you cannot provide a complete answer, offer to connect the customer with appropriate support. Never make promises about specific timelines or outcomes without authorization.",
                document_type="policy",
                brand_name="general",
                category="communication",
                tags=["policy", "response", "guidelines"],
                confidence_level=1.0,
                last_updated=datetime.utcnow(),
                source="system_default",
                metadata={"priority": "high"}
            ),
            KnowledgeDocument(
                id="escalation_guidelines",
                title="Escalation Guidelines",
                content="Escalate to human agents when: 1) Customer expresses extreme dissatisfaction, 2) Legal or compliance issues are mentioned, 3) Media or influencer inquiries, 4) Technical issues requiring specialized support, 5) Requests for refunds or compensation above standard limits.",
                document_type="policy",
                brand_name="general",
                category="escalation",
                tags=["escalation", "guidelines", "support"],
                confidence_level=1.0,
                last_updated=datetime.utcnow(),
                source="system_default",
                metadata={"priority": "critical"}
            ),
            KnowledgeDocument(
                id="brand_voice_guidelines",
                title="Brand Voice Guidelines",
                content="Maintain a friendly, professional, and empathetic tone. Use clear, simple language. Avoid jargon unless necessary. Show genuine care for customer concerns. Be transparent about limitations. Express gratitude for feedback and patience.",
                document_type="guidelines",
                brand_name="general",
                category="communication",
                tags=["brand_voice", "tone", "communication"],
                confidence_level=1.0,
                last_updated=datetime.utcnow(),
                source="system_default",
                metadata={"applies_to": "all_responses"}
            )
        ]
        
        # Add default documents
        for doc in default_documents:
            self.rag_system.add_knowledge_document(doc)
        
        logger.info(f"✅ Initialized {len(default_documents)} default knowledge documents")
    
    def get_rag_tools(self) -> List[BaseTool]:
        """Get RAG tools for use by LangChain agents"""
        return [
            self.knowledge_retrieval_tool,
            self.knowledge_addition_tool
        ]
    
    def add_brand_specific_knowledge(
        self, 
        brand_name: str, 
        knowledge_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Add brand-specific knowledge in bulk"""
        added_count = 0
        failed_count = 0
        
        for data in knowledge_data:
            try:
                document = KnowledgeDocument(
                    id=str(uuid.uuid4()),
                    title=data.get("title", "Untitled"),
                    content=data.get("content", ""),
                    document_type=data.get("document_type", "general"),
                    brand_name=brand_name,
                    category=data.get("category", "general"),
                    tags=data.get("tags", []),
                    confidence_level=data.get("confidence_level", 0.8),
                    last_updated=datetime.utcnow(),
                    source=data.get("source", "bulk_import"),
                    metadata=data.get("metadata", {})
                )
                
                if self.rag_system.add_knowledge_document(document):
                    added_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Failed to add knowledge item: {e}")
                failed_count += 1
        
        result = {
            "brand_name": brand_name,
            "total_items": len(knowledge_data),
            "added_successfully": added_count,
            "failed": failed_count,
            "success_rate": added_count / len(knowledge_data) if knowledge_data else 0
        }
        
        logger.info(f"📚 Bulk knowledge addition for {brand_name}: {added_count}/{len(knowledge_data)} successful")
        
        return result
    
    def search_knowledge_base(
        self, 
        query: str, 
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Search the knowledge base with advanced filters"""
        brand_name = filters.get("brand_name") if filters else None
        document_types = filters.get("document_types") if filters else None
        max_results = filters.get("max_results", 10) if filters else 10
        
        results = self.rag_system.retrieve_relevant_knowledge(
            query=query,
            brand_name=brand_name,
            document_types=document_types,
            n_results=max_results
        )
        
        return {
            "query": query,
            "filters_applied": filters or {},
            "results_count": len(results),
            "results": results
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "knowledge_base_stats": self.rag_system.get_knowledge_base_stats(),
            "system_health": "operational",
            "embedding_model": "all-MiniLM-L6-v2",
            "vector_store": "ChromaDB",
            "tools_available": len(self.get_rag_tools()),
            "last_check": datetime.utcnow().isoformat()
        }


# Export the main classes
__all__ = [
    "BrandKnowledgeRAG", 
    "KnowledgeDocument", 
    "BrandKnowledgeManager",
    "KnowledgeRetrievalTool",
    "KnowledgeAdditionTool"
]
