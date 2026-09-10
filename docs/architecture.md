# Cortexa — Architecture & Engineering Blueprint

This document outlines the core architectural boundaries, design patterns, and engineering principles established across **Iteration 1 (Foundation)** and **Iteration 3 (Core Data & Domain Layer)**, providing the blueprint for future agent-oriented expansions.

---

## 1. High-Level System Architecture

```mermaid
graph TD
    Client[Browser / Client Apps] -->|HTTP / REST| Web[Next.js Frontend (apps/web)]
    Client -->|Direct API / REST| API[FastAPI Backend (apps/api)]
    Web -->|Internal Proxy / Rewrite| API

    subgraph Four-Layer Backend Architecture
        API[API Layer: Route Handlers & DTO Validation]
        Service[Service / Application Layer: Business Logic & Transactions]
        Domain[Domain & Repository Layer: Invariants & Data Access]
        DB[(PostgreSQL 16 Database)]

        API --> Service
        Service --> Domain
        Domain --> DB
    end

    subgraph Infrastructure & Events
        Service -->|Publish Events| Dispatcher[Domain Event Dispatcher]
        Dispatcher -->|Local Subscriptions| AuditService[Audit Logging Service]
        API -->|Async Client / redis.asyncio| Redis[(Redis 7)]
    end

    subgraph Future Swarm Layer [Iteration 4+]
        Service -.-> Orchestrator[Agent Orchestrator]
        Orchestrator -.-> Swarm[Agent Swarm]
        Swarm -.-> Tools[Tool Registry]
        Swarm -.-> Memory[Context & Memory Layer]
    end
```

---

## 2. Monorepo Organization

| Directory | Responsibility |
| :--- | :--- |
| `apps/api/` | FastAPI asynchronous backend service, domain models, services, repositories, migrations, and API endpoints. |
| `apps/web/` | Next.js TypeScript application shell, UI components, and real-time connectivity dashboards. |
| `packages/shared/` | Shared TypeScript interfaces, Python data schemas, and domain constants. |
| `infrastructure/docker/` | Production-grade multi-stage Dockerfiles for both services. |
| `docs/` | System architecture (`architecture.md`), data model (`data-model.md`), and security (`security.md`). |
| `.github/workflows/` | CI/CD automation enforcing linting, formatting, type safety, and test suites. |

---

## 3. Backend Subsystem Architecture (`apps/api`)

### 3.1 Four-Layer Separation of Concerns
1. **API Layer (`app/api/`)**:
   - Thin route handlers, request validation via Pydantic schemas, dependency injection (`TenantContext`, `current_user`, `db`), and response serialization.
   - Zero direct database queries in route handlers.
2. **Service Layer (`app/services/`)**:
   - Encapsulates business logic, coordinates repositories, manages transaction boundaries (`async with self.transaction()`), and publishes domain events.
3. **Domain Layer (`app/domain/` & `app/models/`)**:
   - Persistent ORM entities (`User`, `Organization`, `Membership`, `AuditLog`).
   - Domain enums (`UserRole`, `OrgStatus`, `AuditAction`) and domain events (`UserCreatedEvent`, `OrganizationCreatedEvent`, `MembershipCreatedEvent`).
4. **Repository Layer (`app/repositories/`)**:
   - Generic `BaseRepository` and `TenantRepository`.
   - Enforces tenant isolation: `TenantRepository` mandates `organization_id` on all read/write/list operations to prevent cross-tenant data leaks.

### 3.2 Health & Probes
- **`/health` (Liveness)**: Fast HTTP 200 probe confirming process liveness.
- **`/health/ready` (Readiness)**: Active probe concurrently testing downstream dependencies (PostgreSQL `SELECT 1` and Redis `PING`).

---

## 4. Frontend Subsystem Architecture (`apps/web`)

- Built with **Next.js 14+ (App Router)** and **TypeScript** in strict mode.
- Designed with high-performance CSS tokens, responsive glassmorphism aesthetic, and real-time polling to backend probes.
- Standalone multi-stage Docker build producing a minimal footprint production image.

---

## 5. Security & Multi-Tenancy

- Multi-tenant boundary isolation enforced through `TenantContext` route guards and `TenantRepository` query parameterization.
- RBAC roles (`OWNER`, `ADMIN`, `MEMBER`, `VIEWER`) strictly validated on sensitive operations.
- Salted password hashing with `bcrypt` and stateless JWT session authorization.
- Detailed in [docs/security.md](file:///c:/Users/shiva/OneDrive/Desktop/projects/Cortexa/docs/security.md).

---

## 6. Extensibility Blueprint for Future Iterations

The foundation is deliberately structured to support future AI agent capabilities without architectural refactoring:

1. **Agent Runtime & Orchestration**:
   - Background job processing and event streaming can attach directly to Redis and the `EventDispatcher`.
   - Agent state machines and execution histories will integrate seamlessly into the `TenantRepository` pattern.
2. **Tool Registry**:
   - Modular Python subpackages under `app/tools/` can plug into FastAPI dependencies and service layers.
3. **Memory & RAG Layer**:
   - Vector extensions (`pgvector`) can be added via an Alembic migration on the existing PostgreSQL instance.
