"""
AI Vaidya - FastAPI Backend
Main application entry point
"""
import os
from contextlib import asynccontextmanager
from loguru import logger

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from utils.config import settings
from routers import upload, query, analyze


# ─── Startup / Shutdown ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🌿 AI Vaidya starting up...")
    # Pre-warm embedding model and vector store
    try:
        from services.embeddings import EmbeddingService
        from services.vector_store import VectorStoreService
        from services.picture_analyses import PictureAnalysesService
        emb = EmbeddingService()
        vs = VectorStoreService()
        pic_analyzer = PictureAnalysesService()
        logger.success("✅ Embedding model, vector store, and picture analyses model ready")
    except Exception as e:
        logger.error(f"Startup warning: {e}")
    yield
    logger.info("🌿 AI Vaidya shutting down...")


# ─── App Instance ──────────────────────────────────────────────────
app = FastAPI(
    title="AI Vaidya API",
    description="Intelligent Ayurveda Q&A Assistant powered by RAG",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────
app.include_router(upload.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")
app.include_router(analyze.router, prefix="/api/v1")


# ─── Health Check ─────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {"message": "AI Vaidya API is running 🌿", "version": settings.app_version}


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    from services.embeddings import EmbeddingService
    from services.vector_store import VectorStoreService
    from services.document_processor import documents_metadata

    try:
        emb = EmbeddingService()
        vs = VectorStoreService()
        stats = vs.get_collection_stats()
        return {
            "status": "healthy",
            "version": settings.app_version,
            "vector_db_status": stats["status"],
            "llm_provider": settings.llm_provider,
            "total_documents": len(documents_metadata),
            "total_chunks": stats["total_chunks"],
            "embedding_model": settings.embedding_model,
            "has_llm_api": settings.has_llm,
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again."}
    )


# ─── Run ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info",
    )
