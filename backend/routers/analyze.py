import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from loguru import logger
from utils.config import settings
from services.picture_analyses import PictureAnalysesService

router = APIRouter(prefix="/analyze", tags=["Analyze"])
analyzer = PictureAnalysesService()
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

@router.post("/picture")
async def analyze_picture(file: UploadFile = File(...)):
    """Analyze a picture to extract description and optionally Ayurveda details"""
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PNG, JPG or JPEG.")
    
    file_content = await file.read()
    temp_id = str(uuid.uuid4())
    temp_path = os.path.join(settings.upload_dir, f"temp_{temp_id}{ext}")
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    with open(temp_path, "wb") as f:
        f.write(file_content)
        
    try:
        # Get image caption
        caption = analyzer.analyze_picture(temp_path)
        
        # Optional: Enrich with LLM for Ayurveda Context
        details = ""
        if settings.has_llm and caption:
            try:
                from langchain_core.messages import HumanMessage
                if settings.llm_provider == "groq":
                    from langchain_groq import ChatGroq
                    llm = ChatGroq(model_name="llama3-70b-8192", temperature=0.1)
                else:
                    from langchain_openai import ChatOpenAI
                    llm = ChatOpenAI(model_name="gpt-4-turbo", temperature=0.1)
                
                prompt = f"An image analysis system described a plant/image as: '{caption}'. Can you provide some Ayurvedic context, medicinal properties, or details about this if it is a recognizable plant? If it's too generic, just provide a general Ayurveda perspective on what it could be."
                response = llm.invoke([HumanMessage(content=prompt)])
                details = response.content
            except Exception as e:
                logger.error(f"LLM enrichment error: {e}")
                details = "Could not fetch extra Ayurvedic details."
        
        return {
            "caption": caption,
            "details": details
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
