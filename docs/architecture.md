# Cortexa — Architecture & Engineering Blueprint

This document outlines the core architectural boundaries, design patterns, and engineering principles established in **Iteration 1: Production Engineering Foundation** and provides the blueprint for future agent-oriented expansions.

---

## 1. High-Level System Architecture

```mermaid
graph TD
    Client[Browser / Client Apps] -->|HTTP / REST| Web[Next.js Frontend (apps/web)]
    Client -->|Direct API / REST| API[FastAPI Backend (apps/api)]
    Web -->|Internal Proxy / Rewrite| API

    subgraph Backend Infrastructure
        API -->|Async Pool / SQLAlchemy 2.0| Postgres[(PostgreSQL 16)]
        API -->|Async Client / redis.asyncio| Redis[(Redis 7)]
    end

    subgraph Future Swarm Layer [Iteration 2+]
        API -.-> Orchestrator[Agent Orchestrator]
        Orchestrator -.-> Swarm[Agent Swarm]
        Swarm -.-> Tools[Tool Registry]
        Swarm -.-> Memory[Context & Memory Layer]
    end
```

---

## 2. Monorepo Organization

The codebase is organized as a modular monorepo:

| Directory | Responsibility |
| :--- | :--- |
| `apps/api/` | FastAPI asynchronous backend service, database models, session management, migrations, configuration, and API endpoints. |
| `apps/web/` | Next.js TypeScript application shell, UI components, and real-time connectivity dashboards. |
| `packages/shared/` | Shared TypeScript interfaces, Python data schemas, and domain constants. |
| `infrastructure/docker/` | Production-grade multi-stage Dockerfiles for both services. |
| `docs/` | System architecture, design decisions, and future iteration specifications. |
| `.github/workflows/` | CI/CD automation enforcing linting, formatting, type safety, and test suites. |

---

## 3. Backend Subsystem Architecture (`apps/api`)

### 3.1 Layered Separation of Concerns
1. **API Layer (`app/api/`)**: Pure route handlers, request validation, response serialization, and status codes. Business and data access logic are strictly separated.
2. **Core Layer (`app/core/`)**:
   - `config.py`: Runtime configuration powered by `pydantic-settings` reading from `.env`.
   - `database.py`: Asynchronous connection pooling using `SQLAlchemy 2.0` and `asyncpg`.
   - `redis.py`: Async connection management using `redis.asyncio`.
   - `logging.py` & `middleware.py`: Structured logging and correlation IDs (`X-Request-ID`).
   - `exceptions.py`: Centralized error definitions and standardized JSON error formatting.
3. **Data Layer (`app/models/` & `alembic/`)**:
   - Declarative mapped SQLAlchemy ORM models.
   - Database migrations managed via Alembic.

### 3.2 Health & Probes
- **`/health` (Liveness)**: Fast HTTP 200 probe confirming process liveness.
- **`/health/ready` (Readiness)**: Active probe that concurrently tests downstream dependencies (PostgreSQL `SELECT 1` and Redis `PING`). Returns HTTP 200 when ready or HTTP 503 when degraded.

---

## 4. Frontend Subsystem Architecture (`apps/web`)

- Built with **Next.js 14+ (App Router)** and **TypeScript** in strict mode.
- Designed with high-performance CSS tokens, responsive glassmorphism aesthetic, and real-time polling to backend probes.
- Standalone multi-stage Docker build producing a minimal footprint production image.

---

## 5. Security & Secret Management

- **Zero hardcoded secrets**: All credentials, hostnames, and database strings are supplied via environment variables.
- `.env` is explicitly ignored by version control. `.env.example` provides validated baseline defaults for local testing.
- CORS is strictly configurable with typed origin parsing.

---

## 6. Extensibility Blueprint for Future Iterations

The foundation is deliberately structured to support future AI agent capabilities without architectural refactoring:

1. **Agent Runtime & Orchestration**:
   - Background job processing and event streaming can seamlessly attach to the existing Redis instance.
   - Agent state machines and telemetry can bind directly to PostgreSQL using isolated migration versions.
2. **Tool Registry**:
   - Modular Python subpackages under `app/tools/` can plug into FastAPI dependencies.
3. **Memory & RAG Layer**:
   - Vector extensions (`pgvector`) can be added via an Alembic migration on the existing PostgreSQL instance.
