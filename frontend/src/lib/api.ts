/**
 * AI Vaidya - API Client
 * Centralized Axios instance for all backend calls
 */
import axios from "axios";

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: { "Content-Type": "application/json" },
});

// Request interceptor
api.interceptors.request.use((config) => {
  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "An unexpected error occurred";
    return Promise.reject(new Error(message));
  }
);

// ─── Upload API ──────────────────────────────────────────────────
export const uploadAPI = {
  uploadFile: (file: File, onProgress?: (pct: number) => void) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/upload/", form, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total));
        }
      },
    });
  },

  getStatus: (docId: string) => api.get(`/upload/status/${docId}`),

  listDocuments: () => api.get("/upload/documents"),

  getDocument: (docId: string) => api.get(`/upload/documents/${docId}`),

  deleteDocument: (docId: string) => api.delete(`/upload/documents/${docId}`),

  getAnalytics: () => api.get("/upload/analytics"),
};

// ─── Query API ───────────────────────────────────────────────────
export const queryAPI = {
  ask: (payload: {
    question: string;
    top_k?: number;
    document_ids?: string[];
    chat_history?: Array<{ role: string; content: string }>;
  }) => api.post("/query/ask", payload),

  search: (payload: {
    query: string;
    top_k?: number;
    document_ids?: string[];
  }) => api.post("/query/search", payload),

  getKnowledgeGraph: (documentId?: string) =>
    api.get("/query/knowledge-graph", {
      params: documentId ? { document_id: documentId } : {},
    }),

  getSuggestions: () => api.get("/query/suggest"),
};

// Picture analysis API
export const analyzeAPI = {
  picture: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/analyze/picture", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

// ─── Health API ──────────────────────────────────────────────────
export const healthAPI = {
  check: () => api.get("/health"),
};

// ─── Types ───────────────────────────────────────────────────────
export interface DocumentMetadata {
  document_id: string;
  filename: string;
  file_type: string;
  file_size_mb: number;
  total_pages: number;
  total_chunks: number;
  status: "pending" | "processing" | "completed" | "failed";
  uploaded_at: string;
  processed_at?: string;
  top_herbs: string[];
  top_concepts: string[];
}

export interface SourceChunk {
  document_id: string;
  document_name: string;
  page_number?: number;
  chunk_text: string;
  relevance_score: number;
  chunk_index: number;
}

export interface QueryResponse {
  question: string;
  answer: string;
  confidence: "high" | "medium" | "low";
  confidence_score: number;
  sources: SourceChunk[];
  related_concepts: string[];
  related_herbs: string[];
  processing_time_ms: number;
}

export interface SearchResult {
  chunk_text: string;
  document_name: string;
  document_id: string;
  page_number?: number;
  relevance_score: number;
  highlight?: string;
}

export interface GraphNode {
  id: string;
  label: string;
  type: "herb" | "disease" | "dosha" | "treatment" | "concept";
  description?: string;
  size: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  label: string;
  weight: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  queryResponse?: QueryResponse;
}
