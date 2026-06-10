"""
Embedding Service using sentence-transformers
Handles text embedding generation for RAG pipeline
"""
import numpy as np
import hashlib
import re
from typing import List, Optional
from loguru import logger

from utils.config import settings


class EmbeddingService:
    _instance: Optional["EmbeddingService"] = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if settings.embedding_backend.lower() == "hash":
            self._model = "hash"
            logger.info("Using low-memory hash embeddings.")
        elif self._model is None:
            self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            self._model = SentenceTransformer(settings.embedding_model)
            logger.success(f"Embedding model loaded: {settings.embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self._model = None
            raise

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        if not texts:
            return []
        if self._model == "hash":
            return [self._hash_embed(text) for text in texts]
        if self._model is None:
            raise RuntimeError("Embedding model not loaded")
        try:
            embeddings = self._model.encode(
                texts,
                batch_size=32,
                show_progress_bar=False,
                normalize_embeddings=True,
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query"""
        return self.embed_texts([query])[0]

    @property
    def dimension(self) -> int:
        """Return embedding dimension"""
        if self._model:
            return self._model.get_sentence_embedding_dimension()
        return 384  # default for all-MiniLM-L6-v2

    def is_ready(self) -> bool:
        return self._model is not None

    def _hash_embed(self, text: str) -> List[float]:
        vector = np.zeros(384, dtype=np.float32)
        tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())

        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "little") % vector.size
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector /= norm

        return vector.tolist()
