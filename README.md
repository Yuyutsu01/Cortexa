# Cortexa — AI-Native Sales Automation Platform

> **Status:** Iteration 3: Core Data & Domain Layer  
> **License:** MIT

Cortexa is a production-grade, open-source AI-native sales automation platform built around a swarm of specialized AI agents. The long-term system captures and enriches leads, qualifies prospects, understands conversational context, automates follow-ups, schedules meetings, synchronizes CRM data, and delivers revenue intelligence.

---

## 🎯 Current Status: Iteration 3 — Core Data & Domain Layer

This release builds the production-grade data, domain, repository, and service foundations for the platform:
- **Four-Layer Architecture**: API routes $\rightarrow$ Service layer $\rightarrow$ Domain & Repositories $\rightarrow$ PostgreSQL.
- **Strict Tenant Isolation**: `TenantRepository` and `TenantContext` guarantee tenant context (`organization_id`) is non-optional for tenant-owned data.
- **Domain Modeling**: Base entities (`BaseEntity`, `TenantAwareEntity`, `SoftDeleteMixin`), users, organizations, RBAC memberships, and immutable audit logging.
- **Transaction Safety**: Atomic multi-table operations with automatic rollback and savepoint support.
- **Standardized Conventions**: Consistent pagination (`PaginationParams`), safe dynamic sorting (`SortParams`), and response envelopes (`DataResponse`, `PaginatedResponse`).
- **Domain Events**: In-memory async `EventDispatcher` routing state transitions to audit loggers and future message brokers.
- **Full Test Coverage**: Unit tests, repository integration tests, tenant isolation tests, and authenticated API test suites.

---

## 🏗️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy 2.0 (Async), Alembic, AsyncPG, Bcrypt, PyJWT |
| **Frontend** | Next.js 14+, React 18+, TypeScript (Strict Mode), Vanilla CSS Tokens |
| **Infrastructure** | PostgreSQL 16, Redis 7, Docker, Docker Compose |
| **Quality & Tests** | Pytest, Pytest-Asyncio, Pytest-Cov, Ruff, MyPy, ESLint, Prettier |
| **CI/CD** | GitHub Actions |

---

## 📁 Repository Structure

```
cortexa/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions Multi-Stage CI
├── apps/
│   ├── api/                    # FastAPI Backend Application
│   │   ├── alembic/            # Database Migrations
│   │   │   └── versions/
│   │   │       ├── 0001_initial_system_foundation.py
│   │   │       └── 0002_core_data_and_domain_layer.py
│   │   ├── app/                # Application Source Code
│   │   │   ├── api/            # Route Handlers, Router, and Dependencies (TenantContext, Auth)
│   │   │   │   ├── routes/     # auth, organizations, members, audit, health
│   │   │   │   └── deps.py
│   │   │   ├── core/           # Config, DB, Redis, Logging, Auth, Security, Exceptions
│   │   │   ├── domain/         # Enums (UserRole, OrgStatus, AuditAction) & Events
│   │   │   ├── models/         # ORM Models (User, Organization, Membership, AuditLog)
│   │   │   ├── repositories/   # BaseRepository, TenantRepository, User, Org, Member, Audit
│   │   │   ├── schemas/        # DTOs & Response Wrappers (common, auth, user, org, member, audit)
│   │   │   └── services/       # UserService, OrganizationService, MembershipService, AuditService
│   │   ├── tests/              # Comprehensive Test Suites (Unit, Integration, API)
│   │   ├── alembic.ini         # Alembic Config
│   │   └── requirements.txt    # Backend Dependencies
│   └── web/                    # Next.js Web Frontend Application
│       ├── src/
│       │   ├── app/            # Next.js App Router (Layout, Page, CSS)
│       │   ├── components/     # UI Components (Header, SystemStatus)
│       │   └── lib/            # Typed API Client Utilities
│       ├── package.json        # Frontend Dependencies & Scripts
│       └── tsconfig.json       # TypeScript Configuration
├── packages/
│   └── shared/                 # Shared Types & Contracts
├── infrastructure/
│   └── docker/
│       ├── Dockerfile.api      # Multi-Stage Backend Dockerfile
│       └── Dockerfile.web      # Multi-Stage Frontend Dockerfile
├── docs/
│   ├── architecture.md         # System Architecture Blueprint
│   ├── data-model.md           # Entity Conventions, ER Diagram & Repository Patterns
│   └── security.md             # Security, Multi-Tenancy & RBAC Matrix
├── .env.example                # Environment Variable Template
├── .gitignore                  # Git Ignore Specifications
├── docker-compose.yml          # Multi-Container Compose Stack
├── Makefile                    # Developer Workflow Commands
├── pyproject.toml              # Ruff, MyPy, and Pytest Configuration
├── README.md                   # Project Overview & Setup Guide
├── CONTRIBUTING.md             # Contribution Guidelines
└── LICENSE                     # MIT License
```

---

## 🚀 Quick Start with Docker Compose

```bash
# 1. Clone & Configure
git clone https://github.com/your-org/cortexa.git
cd cortexa
cp .env.example .env

# 2. Start Services
docker compose up --build -d
```
- **Web Frontend:** [http://localhost:3000](http://localhost:3000)
- **API Health Liveness:** [http://localhost:8000/health](http://localhost:8000/health)
- **API Readiness Check:** [http://localhost:8000/health/ready](http://localhost:8000/health/ready)
- **Interactive OpenAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing & Code Quality

```bash
# Run entire test suite (33+ tests)
pytest

# Run Ruff linter
ruff check .

# Run Ruff code formatter check
ruff format --check .

# Run MyPy strict type checker
mypy apps/api/app

# Run Frontend checks
cd apps/web && npm run lint && npm run type-check && npm run build
```

---

## 🗺️ Roadmap

- [x] **Iteration 1**: Production Engineering Foundation (FastAPI, Next.js, PostgreSQL, Redis, Docker, CI/CD)
- [x] **Iteration 2**: Authentication, Multi-Tenancy & User Identity
- [x] **Iteration 3**: Core Data & Domain Layer (Base Models, Repositories, Services, Tenant Isolation, Events, Audit)
- [ ] **Iteration 4**: Agent Runtime & Task State Machine
- [ ] **Iteration 5**: Agent Swarm Orchestrator & Tool Registry
- [ ] **Iteration 6**: Context Management, Vector Store & RAG Pipeline
- [ ] **Iteration 7**: Multi-Channel Integrations & Revenue Intelligence
