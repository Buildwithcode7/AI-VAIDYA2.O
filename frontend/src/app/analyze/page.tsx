"use client";
import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { Upload, ImageIcon, Loader2, Leaf, AlertCircle } from "lucide-react";
import Navbar from "../components/Navbar";

export default function PictureAnalysePage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ caption: string, details: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      setFile(f);
      setPreview(URL.createObjectURL(f));
      setResult(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://localhost:8000/api/v1/analyze/picture", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || "Analysis failed");
      }
      
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to analyze picture.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container" style={{ minHeight: "100vh", background: "var(--bg-primary)" }}>
      <Navbar />
      
      <div style={{ padding: "60px 24px" }}>
        <div style={{ maxWidth: 800, margin: "0 auto" }}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
              <div style={{ background: "rgba(0,137,123,0.1)", padding: 12, borderRadius: 12 }}>
                <ImageIcon size={28} style={{ color: "var(--teal-400)" }} />
              </div>
              <h1 className="heading-serif" style={{ fontSize: "2.5rem" }}>Picture Analyse</h1>
            </div>
            <p style={{ color: "var(--text-secondary)", marginBottom: 40, fontSize: "1.1rem" }}>
              Upload an image of a plant or herb. The AI vision model will recognize it and cross-reference with Ayurveda knowledge to give you medicinal properties and details.
            </p>
          </motion.div>

          <div className="glass-panel" style={{ padding: 32, borderRadius: 20, border: "1px solid rgba(0,137,123,0.2)", background: "rgba(0,0,0,0.2)" }}>
            {!preview ? (
              <div
                onClick={() => fileInputRef.current?.click()}
                style={{
                  border: "2px dashed var(--border-subtle)",
                  borderRadius: 16,
                  padding: "60px 20px",
                  textAlign: "center",
                  cursor: "pointer",
                  transition: "all 0.2s",
                  background: "rgba(0,0,0,0.1)"
                }}
                onMouseEnter={(e) => e.currentTarget.style.borderColor = "var(--teal-500)"}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = "var(--border-subtle)"}
              >
                <Upload size={48} style={{ color: "var(--teal-400)", margin: "0 auto 16px" }} />
                <h3 style={{ fontSize: "1.2rem", marginBottom: 8, color: "var(--text-primary)" }}>Click to upload plant image</h3>
                <p style={{ color: "var(--text-muted)" }}>Supports PNG, JPG, JPEG</p>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
                <div style={{ position: "relative", borderRadius: 12, overflow: "hidden", background: "rgba(0,0,0,0.3)" }}>
                  <img
                    src={preview}
                    alt="Preview"
                    style={{
                      width: "100%", maxHeight: 400, objectFit: "contain",
                      display: "block"
                    }}
                  />
                  {loading && (
                    <div style={{
                      position: "absolute", inset: 0,
                      background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)",
                      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                      gap: 16
                    }}>
                      <Loader2 className="animate-spin" size={48} style={{ color: "var(--brand-gold)" }} />
                      <div style={{ color: "#fff", fontWeight: 600, letterSpacing: 1 }}>Running Vision Analysis...</div>
                    </div>
                  )}
                </div>
                
                {error && (
                  <div style={{ padding: 16, background: "rgba(229,115,115,0.1)", border: "1px solid rgba(229,115,115,0.3)", borderRadius: 12, color: "#e57373", display: "flex", alignItems: "center", gap: 12 }}>
                    <AlertCircle size={20} />
                    {error}
                  </div>
                )}
                
                <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
                  <button className="btn-secondary" onClick={() => { setFile(null); setPreview(null); setResult(null); setError(null); }} disabled={loading}>
                    Choose Another
                  </button>
                  {!result && (
                    <button className="btn-primary" onClick={handleAnalyze} disabled={loading} style={{ background: "linear-gradient(135deg, #00897b, #558b2f)", border: "none" }}>
                      <ImageIcon size={18} />
                      Analyze Picture
                    </button>
                  )}
                </div>
              </div>
            )}

            <input
              type="file"
              accept=".jpg,.jpeg,.png"
              ref={fileInputRef}
              style={{ display: "none" }}
              onChange={handleFileChange}
            />

            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ marginTop: 32, paddingTop: 32, borderTop: "1px solid rgba(0,137,123,0.2)" }}
              >
                <div style={{ background: "rgba(0,0,0,0.3)", padding: 20, borderRadius: 12, marginBottom: 20, border: "1px solid rgba(255,255,255,0.05)" }}>
                  <div style={{ fontWeight: 600, marginBottom: 8, color: "var(--teal-300)" }}>Vision Model Output</div>
                  <div style={{ color: "var(--text-secondary)", fontSize: "1.05rem" }}>"{result.caption}"</div>
                </div>
                
                {result.details && (
                  <div style={{ background: "linear-gradient(135deg, rgba(104,159,56,0.1), rgba(0,137,123,0.1))", border: "1px solid rgba(104,159,56,0.3)", padding: 24, borderRadius: 12 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10, fontWeight: 600, marginBottom: 16, color: "var(--brand-gold)", fontSize: "1.1rem" }}>
                      <Leaf size={20} />
                      Ayurvedic Details
                    </div>
                    <div style={{ color: "var(--text-primary)", whiteSpace: "pre-wrap", lineHeight: 1.7 }}>
                      {result.details}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
