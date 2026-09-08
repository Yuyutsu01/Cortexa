# Cortexa — AI-Native Sales Automation Platform

> **Status:** Iteration 1: Production Engineering Foundation  
> **License:** MIT

Cortexa is a production-grade, open-source AI-native sales automation platform built around a swarm of specialized AI agents. The long-term system captures and enriches leads, qualifies prospects, understands conversational context, automates follow-ups, schedules meetings, synchronizes CRM data, and delivers revenue intelligence.

---

## 🎯 Current Iteration: Iteration 1 — Engineering Foundation

This release establishes the clean, modular, production-oriented repository and infrastructure foundation for Cortexa. It verifies:
- FastAPI asynchronous backend with SQLAlchemy 2.0 and Alembic migrations.
- Redis asynchronous client connection and health probes.
- Next.js 14+ TypeScript web frontend with real-time connectivity status.
- Docker Compose multi-container environment with automated health checks.
- GitHub Actions CI pipeline running linters (Ruff, ESLint), type-checkers (MyPy, tsc), and automated test suites (Pytest).

---

## 🏗️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, Pydantic Settings, SQLAlchemy 2.0 (Async), Alembic, AsyncPG |
| **Frontend** | Next.js 14+, React 18+, TypeScript (Strict Mode), Vanilla CSS Tokens |
| **Infrastructure** | PostgreSQL 16, Redis 7, Docker, Docker Compose |
| **Quality & Tests** | Pytest, Pytest-Asyncio, Ruff, MyPy, ESLint, Prettier |
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
│   │   ├── app/                # Application Source Code
│   │   │   ├── api/            # Route Handlers & Routers
│   │   │   ├── core/           # Config, DB, Redis, Logging, Middleware, Exceptions
│   │   │   ├── models/         # SQLAlchemy ORM Models
│   │   │   └── schemas/        # Pydantic Schemas
│   │   ├── tests/              # Pytest Test Suite
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
│   └── architecture.md         # System Architecture & Design Decisions
├── .env.example                # Environment Variable Template
├── .gitignore                  # Git Ignore Specifications
├── docker-compose.yml          # Complete Multi-Container Stack
├── Makefile                    # Developer Workflow Commands
├── pyproject.toml              # Ruff, MyPy, and Pytest Configuration
├── README.md                   # Project Overview & Setup Guide
├── CONTRIBUTING.md             # Contribution Guidelines
└── LICENSE                     # MIT License
```

---

## 🚀 Quick Start with Docker Compose

The simplest way to run the entire Cortexa stack:

### 1. Clone & Configure
```bash
git clone https://github.com/your-org/cortexa.git
cd cortexa
cp .env.example .env
```

### 2. Start Services
```bash
docker compose up --build -d
```

### 3. Access Services
- **Web Frontend:** [http://localhost:3000](http://localhost:3000)
- **API Health Liveness:** [http://localhost:8000/health](http://localhost:8000/health)
- **API Readiness Check:** [http://localhost:8000/health/ready](http://localhost:8000/health/ready)
- **Interactive OpenAPI Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Stop Services
```bash
docker compose down
```

---

## 💻 Local Development (Without Docker)

### Backend Setup
```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r apps/api/requirements.txt

# 3. Run database migrations
cd apps/api && alembic upgrade head && cd ../..

# 4. Start backend development server
uvicorn app.main:app --app-dir apps/api --reload --port 8000
```

### Frontend Setup
```bash
cd apps/web
npm install
npm run dev
```

---

## 🧪 Testing & Code Quality

Run tests and quality checks using either the `Makefile` or direct commands:

### Backend Testing & Quality Checks
```bash
# Run test suite
pytest

# Run Ruff linter
ruff check .

# Run Ruff code formatter check
ruff format --check .

# Run MyPy strict static type analysis
mypy apps/api/app
```

### Frontend Checks
```bash
cd apps/web

# Run ESLint
npm run lint

# Run TypeScript compilation check
npm run type-check

# Build production bundle
npm run build
```

---

## 🗺️ Roadmap

- [x] **Iteration 1**: Production Engineering Foundation (FastAPI, Next.js, PostgreSQL, Redis, Docker, CI/CD)
- [ ] **Iteration 2**: Authentication, Multi-Tenancy & User Identity
- [ ] **Iteration 3**: Core CRM Domain Models & Data Access Layer
- [ ] **Iteration 4**: Agent Runtime & Task State Machine
- [ ] **Iteration 5**: Agent Swarm Orchestrator & Tool Registry
- [ ] **Iteration 6**: Context Management, Vector Store & RAG Pipeline
- [ ] **Iteration 7**: Multi-Channel Integrations & Revenue Intelligence
