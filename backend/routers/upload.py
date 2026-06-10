"""
Upload Router
Handles document upload, processing, status tracking, and deletion
"""
import os
import uuid
import shutil
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from functools import lru_cache

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from loguru import logger

from utils.config import settings
from models.schemas import (
    DocumentUploadResponse, DocumentProcessingStatus,
    DocumentListResponse, DocumentMetadata, DocumentStatus
)
from services.document_processor import DocumentProcessor

router = APIRouter(prefix="/upload", tags=["Upload"])
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".doc", ".png", ".jpg", ".jpeg"}


@lru_cache(maxsize=1)
def get_processor() -> DocumentProcessor:
    return DocumentProcessor()

@router.post("/", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload an Ayurveda document for processing"""
    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Validate size
    file_content = await file.read()
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({file_size_mb:.1f} MB). Max: {settings.max_file_size_mb} MB"
        )

    # Save file
    document_id = str(uuid.uuid4())
    safe_filename = f"{document_id}{ext}"
    file_path = os.path.join(settings.upload_dir, safe_filename)

    os.makedirs(settings.upload_dir, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file_content)

    logger.info(f"File saved: {file.filename} ({file_size_mb:.2f} MB) → {file_path}")

    # Queue background processing
    processor = get_processor()
    background_tasks.add_task(
        processor.process_document,
        file_path=file_path,
        document_id=document_id,
        filename=file.filename,
        file_size_mb=round(file_size_mb, 3),
    )

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        status=DocumentStatus.PENDING,
        message="Document uploaded successfully. Processing started in background.",
        file_size_mb=round(file_size_mb, 3),
    )


@router.get("/status/{document_id}", response_model=DocumentProcessingStatus)
async def get_processing_status(document_id: str):
    """Get processing status for a document"""
    processor = get_processor()
    status = processor.get_status(document_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return status


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """List all uploaded and processed documents"""
    processor = get_processor()
    docs = processor.get_all_documents()
    total_chunks = sum(d.get("total_chunks", 0) for d in docs)
    return DocumentListResponse(
        documents=[DocumentMetadata(**d) for d in docs],
        total_count=len(docs),
        total_chunks=total_chunks,
    )


@router.get("/documents/{document_id}", response_model=DocumentMetadata)
async def get_document(document_id: str):
    """Get metadata for a specific document"""
    processor = get_processor()
    doc = processor.get_document(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentMetadata(**doc)


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its vector embeddings"""
    processor = get_processor()
    doc = processor.get_document(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    success = processor.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete document")

    return {"message": f"Document '{doc['filename']}' deleted successfully", "document_id": document_id}


@router.get("/analytics")
async def get_analytics():
    """Get analytics across all documents"""
    return get_processor().get_analytics()
