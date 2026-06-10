"""
Configuration management for AI Vaidya
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # --- LLM ---
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None

    llm_provider: str = "groq"
    llm_model: str = "llama3-70b-8192"

    # --- Embeddings ---
    embedding_backend: str = "hash"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # --- ChromaDB ---
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "ayurveda_knowledge"

    # --- RAG ---
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k_retrieval: int = 5

    # --- Server ---
    host: str = "0.0.0.0"
    port: int = 8000
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # --- Upload ---
    max_file_size_mb: int = 100
    upload_dir: str = "./data/uploads"

    # --- App ---
    app_version: str = "1.0.0"
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def has_llm(self) -> bool:
        return bool(self.groq_api_key or self.openai_api_key or self.huggingface_api_key)


settings = Settings()

# Ensure dirs exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.chroma_persist_dir, exist_ok=True)
