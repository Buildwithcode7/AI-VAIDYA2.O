"""
Query Router
Handles Q&A, semantic search, and knowledge graph requests
"""
import time
from typing import Optional, List
from functools import lru_cache

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from models.schemas import (
    QueryRequest, QueryResponse, SearchRequest, SearchResponse,
    SearchResult, KnowledgeGraphResponse, GraphNode, GraphEdge,
    SourceChunk, ConfidenceLevel
)
from services.rag_pipeline import RAGPipeline
from services.embeddings import EmbeddingService

router = APIRouter(prefix="/query", tags=["Query"])


@lru_cache(maxsize=1)
def get_rag() -> RAGPipeline:
    return RAGPipeline()


@lru_cache(maxsize=1)
def get_embedder() -> EmbeddingService:
    return EmbeddingService()


@router.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Ask an Ayurveda question and get a RAG-powered answer"""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    logger.info(f"Query received: {request.question[:80]}...")

    try:
        rag = get_rag()
        result = await rag.query(
            question=request.question,
            top_k=request.top_k,
            document_ids=request.document_ids,
            chat_history=[m.model_dump() for m in (request.chat_history or [])],
        )

        # Map to response schema
        sources = [
            SourceChunk(
                document_id=s.get("document_id", ""),
                document_name=s.get("document_name", "Unknown"),
                page_number=s.get("page_number"),
                chunk_text=s.get("chunk_text", ""),
                relevance_score=s.get("relevance_score", 0.0),
                chunk_index=s.get("chunk_index", 0),
            )
            for s in result.get("sources", [])
        ]

        confidence_map = {"high": ConfidenceLevel.HIGH, "medium": ConfidenceLevel.MEDIUM, "low": ConfidenceLevel.LOW}

        return QueryResponse(
            question=result["question"],
            answer=result["answer"],
            confidence=confidence_map.get(result["confidence"], ConfidenceLevel.LOW),
            confidence_score=result["confidence_score"],
            sources=sources,
            related_concepts=result.get("related_concepts", []),
            related_herbs=result.get("related_herbs", []),
            processing_time_ms=result["processing_time_ms"],
            tokens_used=result.get("tokens_used"),
        )
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """Semantic search across the knowledge base"""
    start = time.time()
    try:
        embedder = get_embedder()
        query_embedding = embedder.embed_query(request.query)
        from services.vector_store import VectorStoreService
        vs = VectorStoreService()
        raw_results = vs.search_text(
            query_embedding=query_embedding,
            top_k=request.top_k,
            document_ids=request.document_ids,
        )
        elapsed_ms = int((time.time() - start) * 1000)

        results = [
            SearchResult(
                chunk_text=r["chunk_text"],
                document_name=r["document_name"],
                document_id=r["document_id"],
                page_number=r.get("page_number"),
                relevance_score=r["relevance_score"],
                highlight=r["chunk_text"][:200] + "..." if len(r["chunk_text"]) > 200 else r["chunk_text"],
            )
            for r in raw_results
        ]

        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_time_ms=elapsed_ms,
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/knowledge-graph", response_model=KnowledgeGraphResponse)
async def get_knowledge_graph(document_id: Optional[str] = Query(None)):
    """Get Ayurveda knowledge graph nodes and edges"""
    try:
        graph = get_rag().build_knowledge_graph(document_id=document_id)
        nodes = [GraphNode(**n) for n in graph["nodes"]]
        edges = [GraphEdge(**e) for e in graph["edges"]]
        return KnowledgeGraphResponse(nodes=nodes, edges=edges, document_id=document_id)
    except Exception as e:
        logger.error(f"Knowledge graph error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggest")
async def get_suggestions():
    """Get example question suggestions"""
    return {
        "suggestions": [
            "What are the three doshas in Ayurveda?",
            "How does turmeric help in wound healing?",
            "What are the properties of Ashwagandha?",
            "Explain the concept of Agni in Ayurveda",
            "Which herbs are useful for cough and cold?",
            "What is Panchakarma therapy?",
            "How does Ayurveda describe digestion?",
            "What are the three Gunas in Ayurveda?",
            "What is the role of Ojas in health?",
            "How is Triphala used in Ayurvedic medicine?",
        ]
    }
