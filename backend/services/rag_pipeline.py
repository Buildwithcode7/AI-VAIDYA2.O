"""
RAG Pipeline Service
Orchestrates retrieval-augmented generation for Ayurveda Q&A
"""
import time
import re
from typing import List, Dict, Optional, Tuple
from loguru import logger

from utils.config import settings
from services.embeddings import EmbeddingService
from services.vector_store import VectorStoreService


# ─── Ayurveda System Prompt ────────────────────────────────────────
SYSTEM_PROMPT = """You are AI Vaidya, an expert Ayurvedic knowledge assistant. 
You ONLY answer questions based on the provided context from Ayurvedic texts, documents, and supplementary Web Search Results.

Rules:
1. ONLY use information from the provided context passages and Web Search Results.
2. If the context doesn't contain enough information, say: "The knowledge base and web search do not contain enough information to answer this question."
3. Always cite which document/page or web source the information comes from.
4. Use clear, structured, educational language.
5. When mentioning herbs or treatments, include Sanskrit terms where applicable.
6. NEVER fabricate information or use knowledge outside the provided context.
7. Keep answers comprehensive but focused on the question.

Format your answer as:
- Direct answer to the question
- Key points (if multiple aspects)
- Sanskrit terms and their meanings (if relevant)
- Safety notes (if applicable)"""

AYURVEDA_RELATED_CONCEPTS = {
    "dosha": ["vata", "pitta", "kapha", "tridosha", "prakriti"],
    "herb": ["ashwagandha", "turmeric", "neem", "brahmi", "tulsi"],
    "treatment": ["panchakarma", "rasayana", "shodhana", "shamana"],
    "concept": ["agni", "ama", "ojas", "dhatu", "srotas"],
}


class RAGPipeline:
    def __init__(self):
        self.embedder = EmbeddingService()
        self.vector_store = VectorStoreService()
        self.llm_client = None
        self._init_llm()

    def _init_llm(self):
        """Initialize LLM client based on config"""
        provider = settings.llm_provider.lower()
        try:
            if provider == "groq" and settings.groq_api_key:
                from groq import Groq
                self.llm_client = Groq(api_key=settings.groq_api_key)
                self.llm_provider = "groq"
                logger.success(f"LLM: Groq ({settings.llm_model})")
            elif provider == "openai" and settings.openai_api_key:
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=settings.openai_api_key)
                self.llm_provider = "openai"
                logger.success("LLM: OpenAI")
            else:
                self.llm_client = None
                self.llm_provider = "fallback"
                logger.warning("No LLM API key found. Using context-only fallback mode.")
        except Exception as e:
            logger.error(f"LLM init error: {e}")
            self.llm_client = None
            self.llm_provider = "fallback"

    async def query(
        self,
        question: str,
        top_k: int = 5,
        document_ids: Optional[List[str]] = None,
        chat_history: Optional[List[Dict]] = None,
    ) -> Dict:
        """Main RAG query pipeline"""
        start_time = time.time()

        # Step 1: Embed the query
        query_embedding = self.embedder.embed_query(question)

        # Step 2: Retrieve relevant chunks
        retrieved = self.vector_store.search_text(
            query_embedding=query_embedding,
            top_k=top_k,
            document_ids=document_ids,
        )

        # Step 3: Compute confidence
        top_score = retrieved[0]["relevance_score"] if retrieved else 0.0
        confidence, confidence_level = self._compute_confidence(top_score, len(retrieved))

        # Step 4: Build context
        context = self._build_context(retrieved) if retrieved else ""
        
        # Step 4.5: Web search augmentation
        import asyncio
        web_context = await asyncio.to_thread(self._search_web, question)
        if web_context:
            context += f"\n\n--- Web Search Results ---\n{web_context}"

        if not context.strip():
            return self._no_context_response(question, start_time)

        # Step 5: Generate answer
        answer = await self._generate_answer(question, context, chat_history or [])

        # Step 6: Extract related concepts
        related_concepts = self._extract_related(question + " " + answer)

        elapsed_ms = int((time.time() - start_time) * 1000)

        return {
            "question": question,
            "answer": answer,
            "confidence": confidence_level,
            "confidence_score": round(confidence, 4),
            "sources": retrieved[:top_k],
            "related_concepts": related_concepts["concepts"][:5],
            "related_herbs": related_concepts["herbs"][:5],
            "processing_time_ms": elapsed_ms,
            "tokens_used": None,
        }

    def _build_context(self, chunks: List[Dict]) -> str:
        """Format retrieved chunks into a prompt context"""
        parts = []
        for i, chunk in enumerate(chunks, 1):
            doc_name = chunk.get("document_name", "Unknown Document")
            page = chunk.get("page_number", "N/A")
            text = chunk.get("chunk_text", "")
            parts.append(
                f"[Source {i}: {doc_name}, Page {page}]\n{text}"
            )
        return "\n\n---\n\n".join(parts)

    async def _generate_answer(
        self,
        question: str,
        context: str,
        chat_history: List[Dict],
    ) -> str:
        """Generate answer using LLM with retrieved context"""
        if self.llm_client is None:
            return self._fallback_answer(context, question)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add recent chat history (last 4 turns)
        for msg in chat_history[-4:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        # User query with context
        user_prompt = f"""Context from Ayurveda knowledge base:
{context}

Question: {question}

Please answer based ONLY on the above context. If the information is not in the context, say so clearly."""

        messages.append({"role": "user", "content": user_prompt})

        try:
            if self.llm_provider == "groq":
                response = self.llm_client.chat.completions.create(
                    model=settings.llm_model,
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.3,
                )
                return response.choices[0].message.content.strip()
            elif self.llm_provider == "openai":
                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.3,
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return self._fallback_answer(context, question)

    def _fallback_answer(self, context: str, question: str) -> str:
        """Return structured context when no LLM is available"""
        if not context:
            return "The uploaded Ayurveda knowledge base and web search do not contain enough information to answer this question."
        return (
            f"**Answer based on retrieved Ayurveda knowledge:**\n\n"
            f"The following relevant passages were found:\n\n{context[:1500]}\n\n"
            f"*Note: Configure a GROQ_API_KEY for AI-generated answers.*"
        )

    def _no_context_response(self, question: str, start_time: float) -> Dict:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "question": question,
            "answer": "The knowledge base and web search do not contain enough information to answer this question. Please upload relevant documents or rephrase.",
            "confidence": "low",
            "confidence_score": 0.0,
            "sources": [],
            "related_concepts": [],
            "related_herbs": [],
            "processing_time_ms": elapsed_ms,
            "tokens_used": None,
        }

    def _compute_confidence(self, top_score: float, num_results: int) -> Tuple[float, str]:
        """Compute confidence level from similarity scores"""
        if top_score >= 0.75 and num_results >= 3:
            return top_score, "high"
        elif top_score >= 0.50 and num_results >= 2:
            return top_score, "medium"
        else:
            return top_score, "low"

    def _extract_related(self, text: str) -> Dict[str, List[str]]:
        """Extract related Ayurvedic concepts from the answer"""
        text_lower = text.lower()
        herbs = [h for h in AYURVEDA_RELATED_CONCEPTS["herb"] if h in text_lower]
        concepts = [c for c in AYURVEDA_RELATED_CONCEPTS["concept"] if c in text_lower]
        concepts += [c for c in AYURVEDA_RELATED_CONCEPTS["dosha"] if c in text_lower]
        return {"herbs": list(set(herbs)), "concepts": list(set(concepts))}

    def _search_web(self, query: str) -> str:
        """Perform a web search using duckduckgo to augment the context"""
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                # Get top 3 search results
                results = list(ddgs.text(query, max_results=3))
                if not results:
                    return ""
                context = ""
                for i, r in enumerate(results, 1):
                    context += f"[Web Source {i}: {r.get('title')}]\n{r.get('body')}\n"
                return context
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return ""

    def build_knowledge_graph(self, document_id: Optional[str] = None) -> Dict:
        """Build a simple knowledge graph from stored chunks"""
        from services.document_processor import documents_metadata, AYURVEDA_HERBS, AYURVEDA_DOSHAS, AYURVEDA_DISEASES

        nodes = []
        edges = []
        node_ids = set()

        def add_node(node_id: str, label: str, node_type: str, description: str = ""):
            if node_id not in node_ids:
                nodes.append({
                    "id": node_id,
                    "label": label,
                    "type": node_type,
                    "description": description,
                    "size": 15 if node_type == "dosha" else 10,
                })
                node_ids.add(node_id)

        # Add dosha nodes
        for dosha in ["Vata", "Pitta", "Kapha"]:
            add_node(dosha.lower(), dosha, "dosha", f"One of the three primary doshas")

        # Add herb nodes from stored documents
        for doc in documents_metadata.values():
            if document_id and doc.get("document_id") != document_id:
                continue
            for herb in doc.get("top_herbs", [])[:8]:
                herb_id = herb.replace(" ", "_")
                add_node(herb_id, herb.title(), "herb", f"Ayurvedic herb")
                # Connect herbs to doshas with simple heuristics
                if herb in ["ashwagandha", "shatavari", "bala"]:
                    edges.append({"source": herb_id, "target": "vata", "label": "balances", "weight": 1.0})
                elif herb in ["turmeric", "neem", "amla"]:
                    edges.append({"source": herb_id, "target": "pitta", "label": "balances", "weight": 1.0})
                elif herb in ["guggul", "triphala", "ginger"]:
                    edges.append({"source": herb_id, "target": "kapha", "label": "balances", "weight": 1.0})

            for concept in doc.get("top_concepts", [])[:6]:
                concept_id = concept.replace(" ", "_")
                add_node(concept_id, concept.title(), "concept", f"Ayurvedic concept")

        # Add treatment nodes
        for treatment in ["Panchakarma", "Rasayana", "Shodhana"]:
            add_node(treatment.lower(), treatment, "treatment")
            for dosha in ["vata", "pitta", "kapha"]:
                edges.append({"source": treatment.lower(), "target": dosha, "label": "treats", "weight": 0.8})

        return {"nodes": nodes, "edges": edges}
