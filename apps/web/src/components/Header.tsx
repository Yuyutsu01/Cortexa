import React from "react";
import { Activity, ShieldCheck } from "lucide-react";

export function Header() {
  return (
    <header className="header">
      <div className="container header-content">
        <div className="brand">
          <div className="brand-logo">C</div>
          <div>
            <div className="brand-text">CORTEXA</div>
            <div style={{ fontSize: "11px", color: "var(--text-muted)", letterSpacing: "0.5px" }}>
              AI-NATIVE SALES AUTOMATION PLATFORM
            </div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span className="badge badge-iteration">
            <ShieldCheck size={14} />
            ITERATION 1: FOUNDATION
          </span>
          <span className="badge" style={{ background: "rgba(255,255,255,0.05)", color: "var(--text-secondary)" }}>
            <Activity size={14} />
            DEVELOPMENT
          </span>
        </div>
      </div>
    </header>
  );
}
