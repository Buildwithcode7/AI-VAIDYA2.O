"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { Variants } from "framer-motion";
import { Mail, Lock, User, LogIn, UserPlus, ArrowRight } from "lucide-react";
import { useRouter } from "next/navigation";
import { useAuth } from "../contexts/AuthContext";
import { toast } from "react-hot-toast";

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  
  const router = useRouter();
  const { login } = useAuth();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password || (!isLogin && !name)) {
      toast.error("Please fill in all required fields.");
      return;
    }
    
    // Simulate login/signup logic
    setTimeout(() => {
      login(email);
      toast.success(isLogin ? "Welcome back!" : "Account created successfully!");
      router.push("/");
    }, 500);
  };

  const containerVariants: Variants = {
    hidden: { opacity: 0, y: 30 },
    visible: { 
      opacity: 1, 
      y: 0, 
      transition: { 
        duration: 0.6, 
        ease: "linear",
        staggerChildren: 0.1 
      } 
    },
    exit: { opacity: 0, y: -30, transition: { duration: 0.4 } }
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4 } }
  };

  return (
    <div className="page-container bg-grid" style={{ position: "relative", overflow: "hidden", minHeight: "calc(100vh - 64px)" }}>
      {/* Decorative Background Elements */}
      <div style={{
        position: "absolute", top: "10%", left: "15%", width: 400, height: 400,
        background: "radial-gradient(circle, rgba(0, 137, 123, 0.15) 0%, transparent 70%)",
        borderRadius: "50%", zIndex: 0, filter: "blur(60px)",
      }} className="animate-pulse-glow" />
      <div style={{
        position: "absolute", bottom: "10%", right: "15%", width: 350, height: 350,
        background: "radial-gradient(circle, rgba(139, 195, 74, 0.1) 0%, transparent 70%)",
        borderRadius: "50%", zIndex: 0, filter: "blur(60px)",
      }} className="animate-pulse-glow" />

      <main className="main-content" style={{ position: "relative", zIndex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <motion.div 
          className="glass-card"
          style={{ width: "100%", maxWidth: 480, padding: "40px", position: "relative", overflow: "hidden" }}
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Top glowing accent */}
          <div style={{
            position: "absolute", top: 0, left: 0, right: 0, height: 3,
            background: "linear-gradient(90deg, var(--teal-400), var(--sage-400))"
          }} />

          <motion.div variants={itemVariants} style={{ textAlign: "center", marginBottom: "32px" }}>
            <h1 className="heading-serif text-gradient" style={{ fontSize: "2.5rem", marginBottom: "8px" }}>
              {isLogin ? "Welcome Back" : "Join AI Vaidya"}
            </h1>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>
              {isLogin 
                ? "Enter your Gmail ID and password to access your personalized Ayurveda insights." 
                : "Create an account to explore the ancient wisdom of Ayurveda."}
            </p>
          </motion.div>

          {/* Toggle Switch */}
          <motion.div variants={itemVariants} style={{
            display: "flex", background: "rgba(0, 0, 0, 0.2)", borderRadius: "var(--radius-md)",
            padding: "4px", marginBottom: "32px", border: "1px solid var(--border-subtle)"
          }}>
            <button
              onClick={() => setIsLogin(true)}
              style={{
                flex: 1, padding: "10px 0", borderRadius: "var(--radius-sm)",
                background: isLogin ? "rgba(0, 137, 123, 0.2)" : "transparent",
                color: isLogin ? "var(--text-primary)" : "var(--text-secondary)",
                border: isLogin ? "1px solid var(--border-medium)" : "1px solid transparent",
                fontWeight: 600, fontSize: "0.9rem", transition: "all 0.3s", cursor: "pointer",
                display: "flex", alignItems: "center", justifyContent: "center", gap: "8px"
              }}
            >
              <LogIn size={16} /> Login
            </button>
            <button
              onClick={() => setIsLogin(false)}
              style={{
                flex: 1, padding: "10px 0", borderRadius: "var(--radius-sm)",
                background: !isLogin ? "rgba(0, 137, 123, 0.2)" : "transparent",
                color: !isLogin ? "var(--text-primary)" : "var(--text-secondary)",
                border: !isLogin ? "1px solid var(--border-medium)" : "1px solid transparent",
                fontWeight: 600, fontSize: "0.9rem", transition: "all 0.3s", cursor: "pointer",
                display: "flex", alignItems: "center", justifyContent: "center", gap: "8px"
              }}
            >
              <UserPlus size={16} /> Sign Up
            </button>
          </motion.div>

          <AnimatePresence mode="wait">
            <motion.form
              key={isLogin ? "login" : "signup"}
              initial={{ opacity: 0, x: isLogin ? -20 : 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: isLogin ? 20 : -20 }}
              transition={{ duration: 0.3 }}
              style={{ display: "flex", flexDirection: "column", gap: "20px" }}
              onSubmit={handleSubmit}
            >
              {!isLogin && (
                <div>
                  <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "8px", fontWeight: 500 }}>
                    Full Name
                  </label>
                  <div style={{ position: "relative" }}>
                    <User size={18} style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
                    <input 
                      type="text" 
                      className="input-field" 
                      placeholder="Dr. Sushruta"
                      style={{ paddingLeft: "42px" }}
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                    />
                  </div>
                </div>
              )}

              <div>
                <label style={{ display: "block", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "8px", fontWeight: 500 }}>
                  Gmail ID
                </label>
                <div style={{ position: "relative" }}>
                  <Mail size={18} style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
                  <input 
                    type="email" 
                    className="input-field" 
                    placeholder="your.name@gmail.com"
                    style={{ paddingLeft: "42px" }}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              <div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
                  <label style={{ fontSize: "0.85rem", color: "var(--text-secondary)", fontWeight: 500 }}>
                    Password
                  </label>
                  {isLogin && (
                    <a href="#" style={{ fontSize: "0.8rem", color: "var(--teal-300)", textDecoration: "none" }}>
                      Forgot password?
                    </a>
                  )}
                </div>
                <div style={{ position: "relative" }}>
                  <Lock size={18} style={{ position: "absolute", left: "14px", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }} />
                  <input 
                    type="password" 
                    className="input-field" 
                    placeholder="••••••••"
                    style={{ paddingLeft: "42px" }}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
              </div>

              <button 
                type="submit" 
                className="btn-primary" 
                style={{ width: "100%", marginTop: "12px", padding: "14px", fontSize: "1rem" }}
              >
                {isLogin ? "Sign In" : "Create Account"}
                <ArrowRight size={18} />
              </button>
            </motion.form>
          </AnimatePresence>

          <motion.div variants={itemVariants} style={{ marginTop: "32px", textAlign: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "24px" }}>
              <div style={{ flex: 1, height: "1px", background: "var(--border-subtle)" }} />
              <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>or continue with</span>
              <div style={{ flex: 1, height: "1px", background: "var(--border-subtle)" }} />
            </div>

            <button style={{
              width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: "12px",
              padding: "12px", background: "rgba(255, 255, 255, 0.05)", border: "1px solid var(--border-medium)",
              borderRadius: "var(--radius-md)", color: "var(--text-primary)", fontWeight: 500, fontSize: "0.95rem",
              cursor: "pointer", transition: "all 0.2s"
            }} className="hover:bg-white/10">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25C22.56 11.47 22.49 10.72 22.36 10H12V14.26H17.92C17.66 15.63 16.88 16.8 15.72 17.58V20.34H19.28C21.36 18.42 22.56 15.6 22.56 12.25Z" fill="#4285F4"/>
                <path d="M12 23C14.97 23 17.46 22.02 19.28 20.34L15.72 17.58C14.74 18.24 13.48 18.64 12 18.64C9.13 18.64 6.7 16.7 5.83 14.12H2.15V16.97C3.96 20.57 7.68 23 12 23Z" fill="#34A853"/>
                <path d="M5.83 14.12C5.61 13.46 5.48 12.75 5.48 12C5.48 11.25 5.61 10.54 5.83 9.88V7.03H2.15C1.4 8.52 1 10.21 1 12C1 13.79 1.4 15.48 2.15 16.97L5.83 14.12Z" fill="#FBBC05"/>
                <path d="M12 5.36C13.62 5.36 15.07 5.92 16.22 7.02L19.35 3.89C17.45 2.12 14.97 1 12 1C7.68 1 3.96 3.43 2.15 7.03L5.83 9.88C6.7 7.3 9.13 5.36 12 5.36Z" fill="#EA4335"/>
              </svg>
              Google
            </button>
          </motion.div>
        </motion.div>
      </main>
    </div>
  );
}
