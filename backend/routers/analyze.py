"""
Analyze Router
Handles picture analysis requests.
"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from loguru import logger

from services.picture_analyses import PictureAnalysesService
from utils.config import settings


router = APIRouter(prefix="/analyze", tags=["Analyze"])
picture_analyzer = PictureAnalysesService()

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


@router.post("/picture")
async def analyze_picture(file: UploadFile = File(...)):
    """Analyze an uploaded plant or herb image."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}",
        )

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({file_size_mb:.1f} MB). Max: {settings.max_file_size_mb} MB",
        )

    os.makedirs(settings.upload_dir, exist_ok=True)
    safe_name = f"analysis-{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.upload_dir, safe_name)

    try:
        with open(file_path, "wb") as uploaded_file:
            uploaded_file.write(content)

        return picture_analyzer.analyze(file_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Picture analysis failed: {exc}")
        raise HTTPException(status_code=500, detail="Picture analysis failed") from exc
