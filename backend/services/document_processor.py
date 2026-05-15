"""
Document Processing Service
Handles PDF/TXT/DOCX ingestion, text extraction, chunking, and embedding storage
"""
import os
import io
import re
import uuid
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any

import fitz  # PyMuPDF
from loguru import logger
from PIL import Image

from utils.config import settings
from services.vector_store import VectorStoreService
from services.embeddings import EmbeddingService

# ─── Ayurveda Domain Terms ─────────────────────────────────────────
AYURVEDA_HERBS = [
    "ashwagandha", "turmeric", "neem", "tulsi", "brahmi", "shatavari",
    "triphala", "guggul", "giloy", "amla", "haritaki", "bibhitaki",
    "licorice", "ginger", "cardamom", "cinnamon", "cumin", "coriander",
    "fennel", "fenugreek", "black pepper", "long pepper", "pippali",
    "manjistha", "kutki", "punarnava", "vidanga", "vacha", "jatamansi",
    "shankhpushpi", "bala", "mulethi", "arjuna", "chitraka", "datura",
    "bhringaraj", "kalmegh", "kutaja", "devadaru", "rasna", "sarpagandha",
]

AYURVEDA_DISEASES = [
    "diabetes", "hypertension", "arthritis", "asthma", "fever", "cold",
    "cough", "indigestion", "constipation", "diarrhea", "skin disease",
    "liver disease", "kidney disease", "anemia", "obesity", "anxiety",
    "depression", "insomnia", "migraine", "ulcer", "gastritis",
    "prameha", "jwara", "atisara", "arsha", "shotha", "raktapitta",
    "rajayakshma", "kasa", "shwasa", "vatavyadhi", "amavata",
]

AYURVEDA_DOSHAS = [
    "vata", "pitta", "kapha", "tridosha", "prakriti", "vikriti",
    "vataja", "pittaja", "kaphaja", "vata-pitta", "pitta-kapha",
]

AYURVEDA_CONCEPTS = [
    "agni", "ama", "ojas", "tejas", "prana", "rasa", "rakta", "mamsa",
    "meda", "asthi", "majja", "shukra", "dhatu", "mala", "dosha",
    "srotas", "dravyaguna", "panchakarma", "shodhana", "shamana",
    "rasayana", "vajikarana", "panchamahabhuta", "satva", "rajas", "tamas",
    "samhita", "charaka", "sushruta", "ashtanga hridaya", "vagbhata",
    "ayurveda", "dinacharya", "ritucharya", "sadvritta", "achara rasayana",
]


# ─── Progress Store (in-memory) ────────────────────────────────────
processing_status: Dict[str, Dict] = {}
documents_metadata: Dict[str, Dict] = {}


class DocumentProcessor:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.embedder = EmbeddingService()

    # ─── Main Entry Point ──────────────────────────────────────────
    async def process_document(
        self,
        file_path: str,
        document_id: str,
        filename: str,
        file_size_mb: float,
    ) -> bool:
        """Full pipeline: extract → chunk → embed → store"""
        try:
            self._update_status(document_id, "processing", 0, filename)
            logger.info(f"Processing document: {filename} ({document_id})")

            # Step 1: Extract text
            self._update_status(document_id, "processing", 10, filename)
            pages = await self._extract_text(file_path, filename)
            total_pages = len(pages)
            logger.info(f"Extracted {total_pages} pages from {filename}")

            self._update_status(document_id, "processing", 30, filename, total_pages=total_pages)

            # Step 2: Chunk text
            chunks = self._chunk_pages(pages, document_id, filename)
            logger.info(f"Created {len(chunks)} chunks from {filename}")

            self._update_status(document_id, "processing", 50, filename,
                                total_pages=total_pages, chunks_created=len(chunks))

            # Step 3: Embed and store in ChromaDB
            await self._embed_and_store(chunks, document_id)
            self._update_status(document_id, "processing", 85, filename,
                                total_pages=total_pages, chunks_created=len(chunks))

            # Step 4: Analyze content
            all_text = " ".join([p["text"] for p in pages])
            top_herbs = self._extract_terms(all_text, AYURVEDA_HERBS)
            top_concepts = self._extract_terms(all_text, AYURVEDA_CONCEPTS)

            # Step 5: Save metadata
            documents_metadata[document_id] = {
                "document_id": document_id,
                "filename": filename,
                "file_type": Path(filename).suffix.lower().strip("."),
                "file_size_mb": file_size_mb,
                "total_pages": total_pages,
                "total_chunks": len(chunks),
                "status": "completed",
                "uploaded_at": datetime.utcnow().isoformat(),
                "processed_at": datetime.utcnow().isoformat(),
                "top_herbs": top_herbs[:10],
                "top_concepts": top_concepts[:10],
                "language": "en",
            }

            self._update_status(document_id, "completed", 100, filename,
                                total_pages=total_pages, chunks_created=len(chunks))
            logger.success(f"Document {filename} processed successfully!")
            return True

        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            self._update_status(document_id, "failed", 0, filename, error=str(e))
            if document_id in documents_metadata:
                documents_metadata[document_id]["status"] = "failed"
            return False

    # ─── Text Extraction ───────────────────────────────────────────
    async def _extract_text(self, file_path: str, filename: str) -> List[Dict]:
        """Extract text page-by-page from PDF, TXT, or DOCX"""
        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            pages = await asyncio.to_thread(self._extract_pdf, file_path)
        elif ext == ".txt":
            pages = self._extract_txt(file_path)
        elif ext in [".docx", ".doc"]:
            pages = await asyncio.to_thread(self._extract_docx, file_path)
        elif ext in [".png", ".jpg", ".jpeg"]:
            pages = await asyncio.to_thread(self._extract_image, file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        # Translate to English if needed
        for page in pages:
            if page.get("text"):
                page["text"] = await asyncio.to_thread(self._translate_to_english, page["text"])
        
        return pages

    def _extract_pdf(self, file_path: str) -> List[Dict]:
        pages = []
        doc = fitz.open(file_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if not text.strip():
                # Try OCR-like text extraction via blocks
                blocks = page.get_text("blocks")
                text = " ".join([b[4] for b in blocks if isinstance(b[4], str)])
            if text.strip():
                pages.append({
                    "page_number": page_num + 1,
                    "text": self._clean_text(text),
                })
        doc.close()
        return pages

    def _extract_txt(self, file_path: str) -> List[Dict]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        # Split into virtual "pages" of ~2000 chars
        lines = content.split("\n")
        pages, current_page, page_num = [], [], 1
        char_count = 0
        for line in lines:
            current_page.append(line)
            char_count += len(line)
            if char_count >= 2000:
                pages.append({"page_number": page_num, "text": self._clean_text("\n".join(current_page))})
                current_page, char_count, page_num = [], 0, page_num + 1
        if current_page:
            pages.append({"page_number": page_num, "text": self._clean_text("\n".join(current_page))})
        return pages

    def _extract_docx(self, file_path: str) -> List[Dict]:
        try:
            from docx import Document
            doc = Document(file_path)
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            # Split into virtual pages
            chunks_2000 = [full_text[i:i+2000] for i in range(0, len(full_text), 2000)]
            return [{"page_number": i+1, "text": self._clean_text(c)} for i, c in enumerate(chunks_2000)]
        except Exception as e:
            logger.error(f"DOCX extraction error: {e}")
            return []

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        # We removed non-ASCII stripping here to preserve other languages before translation
        text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)  # fix hyphenation
        return text.strip()

    def _extract_image(self, file_path: str) -> List[Dict]:
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(file_path)
            
            # OCR Text
            text = pytesseract.image_to_string(img)
            
            # Picture Analyses
            from services.picture_analyses import PictureAnalysesService
            analyzer = PictureAnalysesService()
            caption = analyzer.analyze_picture(file_path)
            
            combined_text = ""
            if caption:
                combined_text += f"[Image Description: {caption}]\n"
            if text.strip():
                combined_text += f"[Extracted Text]\n{text.strip()}"
                
            combined_text = self._clean_text(combined_text)
            
            if combined_text:
                return [{"page_number": 1, "text": combined_text}]
            return []
        except Exception as e:
            logger.error(f"Image extraction error: {e}")
            return []

    def _translate_to_english(self, text: str) -> str:
        """Translate text to English if it is in another language."""
        try:
            from deep_translator import GoogleTranslator
            translator = GoogleTranslator(source='auto', target='en')
            translated_chunks = []
            # Google Translate API has a 5000 character limit
            for i in range(0, len(text), 4500):
                chunk = text[i:i+4500]
                translated = translator.translate(chunk)
                if translated:
                    translated_chunks.append(translated)
                else:
                    translated_chunks.append(chunk)
            return " ".join(translated_chunks)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    # ─── Chunking ─────────────────────────────────────────────────
    def _chunk_pages(self, pages: List[Dict], document_id: str, filename: str) -> List[Dict]:
        """Split pages into overlapping semantic chunks"""
        chunks = []
        chunk_size = settings.chunk_size
        chunk_overlap = settings.chunk_overlap

        for page in pages:
            text = page["text"]
            page_num = page["page_number"]
            if len(text) < 50:
                continue

            # Sliding window chunking
            start = 0
            while start < len(text):
                end = min(start + chunk_size, len(text))
                chunk_text = text[start:end].strip()
                if len(chunk_text) > 50:
                    chunk_id = f"{document_id}_p{page_num}_c{len(chunks)}"
                    chunks.append({
                        "id": chunk_id,
                        "text": chunk_text,
                        "metadata": {
                            "document_id": document_id,
                            "document_name": filename,
                            "page_number": page_num,
                            "chunk_index": len(chunks),
                        },
                    })
                start += chunk_size - chunk_overlap
        return chunks

    # ─── Embed & Store ─────────────────────────────────────────────
    async def _embed_and_store(self, chunks: List[Dict], document_id: str):
        """Generate embeddings and store in ChromaDB"""
        batch_size = 32
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            texts = [c["text"] for c in batch]
            ids = [c["id"] for c in batch]
            metadatas = [c["metadata"] for c in batch]
            embeddings = await asyncio.to_thread(self.embedder.embed_texts, texts)
            await asyncio.to_thread(
                self.vector_store.add_documents,
                ids=ids, texts=texts, embeddings=embeddings, metadatas=metadatas
            )

    # ─── Term Extraction ───────────────────────────────────────────
    def _extract_terms(self, text: str, term_list: List[str]) -> List[str]:
        text_lower = text.lower()
        found = [(t, text_lower.count(t)) for t in term_list if t in text_lower]
        found.sort(key=lambda x: x[1], reverse=True)
        return [t[0] for t in found if t[1] > 0]

    # ─── Status Helpers ────────────────────────────────────────────
    def _update_status(self, doc_id: str, status: str, progress: int,
                       filename: str, total_pages: int = 0,
                       chunks_created: int = 0, error: str = None):
        processing_status[doc_id] = {
            "document_id": doc_id,
            "filename": filename,
            "status": status,
            "progress": progress,
            "total_pages": total_pages,
            "chunks_created": chunks_created,
            "error_message": error,
            "completed_at": datetime.utcnow().isoformat() if status in ["completed", "failed"] else None,
        }

    def get_status(self, doc_id: str) -> Optional[Dict]:
        return processing_status.get(doc_id)

    def get_all_documents(self) -> List[Dict]:
        return list(documents_metadata.values())

    def get_document(self, doc_id: str) -> Optional[Dict]:
        return documents_metadata.get(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        try:
            self.vector_store.delete_document(doc_id)
            documents_metadata.pop(doc_id, None)
            processing_status.pop(doc_id, None)
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False

    def get_analytics(self) -> Dict:
        docs = list(documents_metadata.values())
        all_herbs = {}
        all_diseases = {}
        total_chunks = sum(d.get("total_chunks", 0) for d in docs)
        total_pages = sum(d.get("total_pages", 0) for d in docs)

        for doc in docs:
            for herb in doc.get("top_herbs", []):
                all_herbs[herb] = all_herbs.get(herb, 0) + 1
            for concept in doc.get("top_concepts", []):
                all_diseases[concept] = all_diseases.get(concept, 0) + 1

        top_herbs = sorted(all_herbs.items(), key=lambda x: x[1], reverse=True)
        top_diseases = sorted(all_diseases.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_documents": len(docs),
            "total_chunks": total_chunks,
            "total_pages": total_pages,
            "top_herbs": [{"herb": h, "count": c, "documents": []} for h, c in top_herbs[:10]],
            "top_diseases": [{"concept": d, "count": c} for d, c in top_diseases[:10]],
            "most_queried": [],
        }
