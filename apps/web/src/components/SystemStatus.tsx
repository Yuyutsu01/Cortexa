"use client";

import React, { useEffect, useState, useCallback } from "react";
import { 
  Database, 
  Server, 
  Layers, 
  RefreshCw, 
  CheckCircle2, 
  XCircle, 
  Cpu,
  Clock,
  ExternalLink
} from "lucide-react";
import { fetchHealth, fetchReadiness, HealthResponse, ReadinessResponse } from "../lib/api";

export function SystemStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [lastRefreshed, setLastRefreshed] = useState<Date | null>(null);

  const refreshStatus = useCallback(async () => {
    setLoading(true);
    const [h, r] = await Promise.all([fetchHealth(), fetchReadiness()]);
    setHealth(h);
    setReadiness(r);
    setLastRefreshed(new Date());
    setLoading(false);
  }, []);

  useEffect(() => {
    refreshStatus();
    // Poll status every 10 seconds
    const interval = setInterval(refreshStatus, 10000);
    return () => clearInterval(interval);
  }, [refreshStatus]);

  const isApiHealthy = health?.status === "ok";
  const isDbHealthy = readiness?.components?.database?.status === "healthy";
  const isRedisHealthy = readiness?.components?.redis?.status === "healthy";
  const isStackReady = readiness?.status === "ready";

  return (
    <div style={{ padding: "40px 0" }}>
      {/* Hero Welcome Banner */}
      <div className="glass-card card-padding" style={{ marginBottom: "32px", position: "relative", overflow: "hidden" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "20px" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
              <span className={`dot ${isStackReady ? "dot-healthy" : "dot-unhealthy"}`} />
              <span style={{ fontSize: "14px", fontWeight: 700, color: isStackReady ? "var(--success)" : "var(--danger)", textTransform: "uppercase", letterSpacing: "1px" }}>
                {isStackReady ? "All Core Systems Operational" : "System Dependencies Degraded"}
              </span>
            </div>
            <h1 style={{ fontSize: "32px", fontWeight: 800, letterSpacing: "-1px", marginBottom: "8px" }}>
              Cortexa Engineering Foundation
            </h1>
            <p style={{ color: "var(--text-secondary)", maxWidth: "680px", fontSize: "15px" }}>
              Production foundation for the AI-native sales automation platform. This stack verifies seamless communication across FastAPI, PostgreSQL, Redis, Docker, and Next.js.
            </p>
          </div>

          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <button 
              className="btn btn-secondary" 
              onClick={refreshStatus} 
              disabled={loading}
              title="Refresh health checks"
            >
              <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
              {loading ? "Checking..." : "Refresh"}
            </button>
            <a 
              href="http://localhost:8000/docs" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="btn"
            >
              API Docs
              <ExternalLink size={16} />
            </a>
          </div>
        </div>

        {lastRefreshed && (
          <div style={{ marginTop: "16px", fontSize: "12px", color: "var(--text-muted)", display: "flex", alignItems: "center", gap: "6px" }}>
            <Clock size={13} />
            Last checked: {lastRefreshed.toLocaleTimeString()} (auto-refreshing every 10s)
          </div>
        )}
      </div>

      {/* Connectivity Status Grid */}
      <h2 style={{ fontSize: "20px", fontWeight: 700, marginBottom: "16px", letterSpacing: "-0.5px" }}>
        Infrastructure Health & Connectivity Probes
      </h2>

      <div className="status-grid">
        {/* Backend API Service */}
        <div className="glass-card card-padding">
          <div className="card-header">
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <div style={{ padding: "8px", borderRadius: "8px", background: "rgba(99, 102, 241, 0.15)", color: "var(--accent-primary)" }}>
                <Server size={20} />
              </div>
              <div>
                <div className="card-title">FastAPI Backend</div>
                <div className="card-desc">Liveness Probe (/health)</div>
              </div>
            </div>
            <span className={`badge ${isApiHealthy ? "badge-healthy" : "badge-unhealthy"}`}>
              {isApiHealthy ? <CheckCircle2 size={13} /> : <XCircle size={13} />}
              {isApiHealthy ? "ONLINE" : "OFFLINE"}
            </span>
          </div>

          <div className="card-value">
            {health?.version ? `v${health.version}` : "Unavailable"}
          </div>
          <div className="card-desc" style={{ marginBottom: "12px" }}>
            Environment: <strong style={{ color: "var(--text-primary)" }}>{health?.environment || "unknown"}</strong>
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", justifyContent: "space-between" }}>
            <span>Round-trip latency:</span>
            <span style={{ fontFamily: "var(--font-mono)", color: "var(--accent-primary)", fontWeight: 600 }}>
              {health?.latencyMs !== undefined ? `${health.latencyMs}ms` : "-"}
            </span>
          </div>
        </div>

        {/* PostgreSQL Database */}
        <div className="glass-card card-padding">
          <div className="card-header">
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <div style={{ padding: "8px", borderRadius: "8px", background: "rgba(16, 185, 129, 0.15)", color: "var(--success)" }}>
                <Database size={20} />
              </div>
              <div>
                <div className="card-title">PostgreSQL Database</div>
                <div className="card-desc">Async Connection Pool</div>
              </div>
            </div>
            <span className={`badge ${isDbHealthy ? "badge-healthy" : "badge-unhealthy"}`}>
              {isDbHealthy ? <CheckCircle2 size={13} /> : <XCircle size={13} />}
              {isDbHealthy ? "CONNECTED" : "FAILED"}
            </span>
          </div>

          <div className="card-value">
            {isDbHealthy ? "Operational" : "Unavailable"}
          </div>
          <div className="card-desc" style={{ marginBottom: "12px" }}>
            {readiness?.components?.database?.message || "Checking database ping..."}
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", justifyContent: "space-between" }}>
            <span>Engine Driver:</span>
            <span style={{ fontFamily: "var(--font-mono)", color: "var(--text-primary)" }}>asyncpg + SQLAlchemy 2.0</span>
          </div>
        </div>

        {/* Redis Cache & Events */}
        <div className="glass-card card-padding">
          <div className="card-header">
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <div style={{ padding: "8px", borderRadius: "8px", background: "rgba(245, 158, 11, 0.15)", color: "var(--warning)" }}>
                <Layers size={20} />
              </div>
              <div>
                <div className="card-title">Redis Infrastructure</div>
                <div className="card-desc">Async Client Connection</div>
              </div>
            </div>
            <span className={`badge ${isRedisHealthy ? "badge-healthy" : "badge-unhealthy"}`}>
              {isRedisHealthy ? <CheckCircle2 size={13} /> : <XCircle size={13} />}
              {isRedisHealthy ? "CONNECTED" : "FAILED"}
            </span>
          </div>

          <div className="card-value">
            {isRedisHealthy ? "Operational" : "Unavailable"}
          </div>
          <div className="card-desc" style={{ marginBottom: "12px" }}>
            {readiness?.components?.redis?.message || "Checking Redis ping..."}
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-secondary)", display: "flex", justifyContent: "space-between" }}>
            <span>Client Driver:</span>
            <span style={{ fontFamily: "var(--font-mono)", color: "var(--text-primary)" }}>redis.asyncio</span>
          </div>
        </div>
      </div>

      {/* Live Probe Diagnostics */}
      <div style={{ marginTop: "36px" }}>
        <h2 style={{ fontSize: "20px", fontWeight: 700, marginBottom: "16px", letterSpacing: "-0.5px", display: "flex", alignItems: "center", gap: "8px" }}>
          <Cpu size={20} style={{ color: "var(--accent-primary)" }} />
          Live Probe Payload Diagnostics
        </h2>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))", gap: "20px" }}>
          <div>
            <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px" }}>
              GET /health (Liveness)
            </div>
            <pre className="code-block">
              {health ? JSON.stringify(health, null, 2) : "// Loading..."}
            </pre>
          </div>

          <div>
            <div style={{ fontSize: "13px", fontWeight: 600, color: "var(--text-secondary)", marginBottom: "8px" }}>
              GET /health/ready (Readiness)
            </div>
            <pre className="code-block">
              {readiness ? JSON.stringify(readiness, null, 2) : "// Loading..."}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
