"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Leaf, MessageCircle, Upload, Star, ChevronRight,
  BookOpen, Zap, Shield, Brain, Microscope , Database, Code2
} from "lucide-react";

const features = [
  { icon: Brain, title: "RAG-Powered Answers", desc: "Retrieval-Augmented Generation ensures every answer is grounded in uploaded Ayurvedic texts — no hallucinations." },
  { icon: BookOpen, title: "Classical Text Support", desc: "Upload Charaka Samhita, Sushruta Samhita, Ashtanga Hridaya and any Ayurveda PDFs up to 400+ pages." },
  { icon: Microscope, title: "Semantic Retrieval", desc: "State-of-the-art sentence embeddings find the most relevant passages with semantic understanding." },
  { icon: Shield, title: "Citation-Backed", desc: "Every answer includes source document, page number, and extracted snippet for full transparency." },
  { icon: Zap, title: "Knowledge Graph", desc: "Visual relationship graph between herbs, doshas, diseases, and treatments extracted from your documents." },
  { icon: Star, title: "Voice AI", desc: "Ask questions with your voice and hear AI Vaidya speak back the answer in natural language." },
];

const exampleQuestions = [
  "What are the three doshas in Ayurveda?",
  "How does turmeric help in wound healing?",
  "Explain the concept of Agni (digestive fire)",
  "Which herbs are useful for cough and cold?",
  "What is Panchakarma therapy?",
  "Describe the properties of Ashwagandha",
];

const stats = [
  { value: "400+", label: "Pages Supported" },
  { value: "< 2s", label: "Answer Time" },
  { value: "100%", label: "Citation Backed" },
  { value: "Free", label: "Open Source" },
];

export default function LandingPage() {
  return (
    <div className="page-container" style={{ background: "var(--bg-primary)" }}>
      {/* ── Hero ───────────────────────────────────────────── */}
      <section style={{ position: "relative", overflow: "hidden", padding: "80px 24px 100px" }}>
        {/* Background grid */}
        <div className="bg-grid" style={{ position: "absolute", inset: 0, opacity: 0.5 }} />

        {/* Ambient glow orbs */}
        <div style={{
          position: "absolute", top: "10%", left: "15%",
          width: 400, height: 400,
          background: "radial-gradient(circle, rgba(0,137,123,0.12) 0%, transparent 70%)",
          filter: "blur(40px)", pointerEvents: "none",
        }} />
        <div style={{
          position: "absolute", bottom: "10%", right: "10%",
          width: 300, height: 300,
          background: "radial-gradient(circle, rgba(104,159,56,0.1) 0%, transparent 70%)",
          filter: "blur(40px)", pointerEvents: "none",
        }} />

        <div style={{ maxWidth: 900, margin: "0 auto", textAlign: "center", position: "relative" }}>
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            style={{
              display: "inline-flex", alignItems: "center", gap: 8,
              padding: "6px 16px",
              background: "rgba(0, 137, 123, 0.1)",
              border: "1px solid rgba(0, 137, 123, 0.3)",
              borderRadius: 999,
              marginBottom: 24,
              fontSize: "0.85rem", color: "var(--teal-300)",
              fontWeight: 600,
            }}
          >
            <Leaf size={14} />
            Hackathon Project — AI-Powered Ayurveda Intelligence
          </motion.div>

          {/* Headline */}
          <motion.h1
            className="heading-serif"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            style={{ fontSize: "clamp(2.5rem, 6vw, 4.5rem)", marginBottom: 20 }}
          >
            <span className="text-gradient">AI Vaidya</span>
            <br />
            <span style={{ color: "var(--text-primary)", fontStyle: "italic" }}>
              Ancient Wisdom,
            </span>{" "}
            <span style={{ color: "var(--text-secondary)" }}>Modern AI</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            style={{
              fontSize: "clamp(1rem, 2vw, 1.25rem)",
              color: "var(--text-secondary)",
              maxWidth: 680,
              margin: "0 auto 40px",
              lineHeight: 1.7,
            }}
          >
            Upload Ayurvedic texts, research papers, and classical Samhitas.
            Ask questions in plain English and receive grounded, citation-backed
            answers from your own knowledge base — powered by RAG.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            style={{ display: "flex", gap: 16, justifyContent: "center", flexWrap: "wrap" }}
          >
            <Link href="/chat" className="btn-primary" style={{ fontSize: "1rem", padding: "14px 32px" }}>
              <MessageCircle size={18} />
              Start Asking Questions
            </Link>
            <Link href="/analyze" className="btn-secondary" style={{ fontSize: "1rem", padding: "14px 32px", borderColor: "var(--teal-500)", color: "var(--teal-300)" }}>
              <Upload size={18} />
              Picture Analyse
            </Link>
          </motion.div>

          {/* Stats row */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            style={{
              display: "flex", gap: 32, justifyContent: "center",
              flexWrap: "wrap", marginTop: 64,
            }}
          >
            {stats.map(({ value, label }) => (
              <div key={label} style={{ textAlign: "center" }}>
                <div style={{
                  fontSize: "1.8rem", fontWeight: 700,
                  fontFamily: "var(--font-playfair)",
                  color: "var(--teal-300)",
                }}>
                  {value}
                </div>
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: 2 }}>
                  {label}
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── Example Questions ───────────────────────────────── */}
      <section style={{ padding: "60px 24px", background: "rgba(0,0,0,0.2)" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            style={{ textAlign: "center", marginBottom: 40 }}
          >
            <h2 className="heading-serif" style={{ fontSize: "1.8rem", marginBottom: 8 }}>
              Questions AI Vaidya Can Answer
            </h2>
            <p style={{ color: "var(--text-secondary)" }}>
              Ask anything from your uploaded Ayurveda knowledge base
            </p>
          </motion.div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 12 }}>
            {exampleQuestions.map((q, i) => (
              <motion.div
                key={q}
                initial={{ opacity: 0, x: -10 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
              >
                <Link href={`/chat?q=${encodeURIComponent(q)}`}
                  style={{ textDecoration: "none", display: "block" }}>
                  <div className="glass-card-light" style={{
                    padding: "14px 16px", cursor: "pointer",
                    display: "flex", alignItems: "center", gap: 12,
                    transition: "all 0.2s",
                  }}
                    onMouseEnter={e => (e.currentTarget.style.borderColor = "rgba(0,137,123,0.4)")}
                    onMouseLeave={e => (e.currentTarget.style.borderColor = "")}
                  >
                    <ChevronRight size={16} style={{ color: "var(--teal-400)", flexShrink: 0 }} />
                    <span style={{ fontSize: "0.9rem", color: "var(--text-secondary)" }}>{q}</span>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ────────────────────────────────────────── */}
      <section style={{ padding: "80px 24px" }}>
        <div style={{ maxWidth: 1200, margin: "0 auto" }}>
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            style={{ textAlign: "center", marginBottom: 60 }}
          >
            <h2 className="heading-serif" style={{ fontSize: "2rem", marginBottom: 10 }}>
              Built for <span className="text-gradient">Serious Research</span>
            </h2>
            <p style={{ color: "var(--text-secondary)", maxWidth: 500, margin: "0 auto" }}>
              Production-ready RAG architecture with advanced NLP and a premium UI
            </p>
          </motion.div>

          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
            gap: 24,
          }}>
            {features.map(({ icon: Icon, title, desc }, i) => (
              <motion.div
                key={title}
                className="glass-card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.07 }}
                style={{ padding: "28px 24px" }}
                whileHover={{ scale: 1.01, transition: { duration: 0.15 } }}
              >
                <div style={{
                  width: 44, height: 44,
                  background: "linear-gradient(135deg, rgba(0,137,123,0.2), rgba(104,159,56,0.15))",
                  border: "1px solid rgba(0,137,123,0.3)",
                  borderRadius: 12,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  marginBottom: 16,
                }}>
                  <Icon size={22} style={{ color: "var(--teal-300)" }} />
                </div>
                <h3 style={{
                  fontFamily: "var(--font-playfair)",
                  fontSize: "1.05rem", fontWeight: 600,
                  color: "var(--text-primary)", marginBottom: 8,
                }}>
                  {title}
                </h3>
                <p style={{ fontSize: "0.875rem", color: "var(--text-secondary)", lineHeight: 1.65 }}>
                  {desc}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Banner ───────────────────────────────────────── */}
      <section style={{ padding: "60px 24px" }}>
        <div style={{ maxWidth: 800, margin: "0 auto" }}>
          <motion.div
            initial={{ opacity: 0, scale: 0.97 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="glass-card"
            style={{
              padding: "48px 40px", textAlign: "center",
              background: "linear-gradient(135deg, rgba(0,69,59,0.4), rgba(0,43,35,0.6))",
              borderColor: "rgba(0,137,123,0.3)",
            }}
          >
            <Leaf size={40} style={{ color: "var(--teal-400)", margin: "0 auto 16px" }} />
            <h2 className="heading-serif" style={{ fontSize: "1.8rem", marginBottom: 12 }}>
              Ready to explore Ayurvedic wisdom?
            </h2>
            <p style={{ color: "var(--text-secondary)", marginBottom: 28, maxWidth: 500, margin: "0 auto 28px" }}>
              Upload a classical Ayurveda text and start asking questions. The AI will answer only from what you've uploaded.
            </p>
            <div style={{ display: "flex", gap: 16, justifyContent: "center", flexWrap: "wrap" }}>
              <Link href="/upload" className="btn-gold" style={{ padding: "14px 32px", fontSize: "0.95rem" }}>
                Upload Your First Document
              </Link>
              <Link href="/about" className="btn-secondary">
                Learn More
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        borderTop: "1px solid var(--border-subtle)",
        padding: "24px",
        textAlign: "center",
        color: "var(--text-muted)",
        fontSize: "0.8rem",
      }}>
        <p>AI Vaidya © 2025 · Built with ❤️ for healthcare innovation · MIT License</p>
      </footer>
    </div>
  );
}
