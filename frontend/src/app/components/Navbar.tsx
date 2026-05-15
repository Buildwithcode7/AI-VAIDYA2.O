"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Leaf, MessageCircle, Upload, Database, Info,
  Search, Activity, Menu, X, LogIn, LogOut, User
} from "lucide-react";
import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";

const navItems = [
  { href: "/", label: "Home", icon: Leaf },
  { href: "/chat", label: "Ask AI", icon: MessageCircle },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/knowledge", label: "Knowledge Base", icon: Database },
  { href: "/search", label: "Search", icon: Search },
  { href: "/analyze", label: "Picture Analyse", icon: Activity },
  { href: "/about", label: "About", icon: Info },
];

export default function Navbar() {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, logout } = useAuth();

  return (
    <nav
      style={{
        background: "rgba(7, 26, 21, 0.85)",
        backdropFilter: "blur(20px)",
        borderBottom: "1px solid rgba(0, 137, 123, 0.2)",
        position: "sticky",
        top: 0,
        zIndex: 100,
      }}
    >
      <div style={{ maxWidth: 1400, margin: "0 auto", padding: "0 24px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", height: 64 }}>
          {/* Logo */}
          <Link href="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 38, height: 38,
              background: "linear-gradient(135deg, #00897b, #558b2f)",
              borderRadius: 10,
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: "0 0 16px rgba(0, 137, 123, 0.4)",
            }}>
              <Leaf size={20} color="#fff" />
            </div>
            <div>
              <span style={{
                fontFamily: "var(--font-playfair, serif)",
                fontWeight: 700,
                fontSize: "1.15rem",
                background: "linear-gradient(135deg, #80cbc4, #8bc34a)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}>
                AI Vaidya
              </span>
              <div style={{ fontSize: "0.65rem", color: "var(--text-muted)", marginTop: -2, letterSpacing: "0.1em" }}>
                AYURVEDA Q&A
              </div>
            </div>
          </Link>

          {/* Desktop Nav */}
          <div style={{ display: "flex", alignItems: "center", gap: 4 }} className="hidden md:flex">
            {navItems.map(({ href, label, icon: Icon }) => {
              const active = pathname === href || (href !== "/" && pathname.startsWith(href));
              return (
                <Link key={href} href={href} className={`nav-link ${active ? "active" : ""}`}>
                  <Icon size={16} />
                  {label}
                </Link>
              );
            })}
          </div>

          {/* Actions & Status */}
          <div style={{ display: "flex", alignItems: "center", gap: 16 }} className="hidden md:flex">
            <div style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "6px 12px",
              background: "rgba(104, 159, 56, 0.1)",
              border: "1px solid rgba(104, 159, 56, 0.3)",
              borderRadius: 999,
            }}>
              <div style={{
                width: 7, height: 7, borderRadius: "50%",
                background: "#689f38",
                boxShadow: "0 0 6px #689f38",
              }} />
              <span style={{ fontSize: "0.75rem", color: "#8bc34a", fontWeight: 600 }}>Live</span>
            </div>
            {user ? (
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--text-secondary)", fontSize: "0.85rem", background: "rgba(0,137,123,0.1)", padding: "4px 12px", borderRadius: 999, border: "1px solid var(--border-subtle)" }}>
                  <User size={14} />
                  {user.email.split('@')[0]}
                </div>
                <button onClick={logout} className="btn-secondary" style={{ padding: "6px 12px", fontSize: "0.85rem" }}>
                  <LogOut size={16} />
                </button>
              </div>
            ) : (
              <Link href="/login" className="btn-primary" style={{ padding: "8px 16px", fontSize: "0.85rem" }}>
                Sign In
              </Link>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-secondary)", display: "flex" }}
            className="md:hidden"
          >
            {menuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            style={{
              background: "rgba(7, 26, 21, 0.98)",
              borderTop: "1px solid rgba(0, 137, 123, 0.15)",
              padding: "12px 24px 20px",
            }}
          >
            {navItems.map(({ href, label, icon: Icon }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className={`nav-link ${active ? "active" : ""}`}
                  style={{ display: "flex", marginBottom: 4 }}
                  onClick={() => setMenuOpen(false)}
                >
                  <Icon size={16} />
                  {label}
                </Link>
              );
            })}
            <div style={{ height: "1px", background: "var(--border-subtle)", margin: "8px 0" }} />
            {user ? (
              <button
                onClick={() => { logout(); setMenuOpen(false); }}
                className="nav-link"
                style={{ display: "flex", width: "100%", background: "none", border: "none", textAlign: "left", cursor: "pointer", marginBottom: 4 }}
              >
                <LogOut size={16} />
                Logout ({user.email.split('@')[0]})
              </button>
            ) : (
              <Link
                href="/login"
                className={`nav-link ${pathname === "/login" ? "active" : ""}`}
                style={{ display: "flex", marginBottom: 4 }}
                onClick={() => setMenuOpen(false)}
              >
                <LogIn size={16} />
                Sign In
              </Link>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
