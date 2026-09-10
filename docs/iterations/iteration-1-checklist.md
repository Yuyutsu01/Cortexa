# Iteration 1 — Definition of Done: Production Engineering Foundation

**Git Tag:** `v0.1.0-foundation`

---

## 1. Infrastructure
- [x] Docker Compose starts API, Web, PostgreSQL, and Redis with health checks.
- [x] PostgreSQL runs with persistent volume.
- [x] Redis runs with persistent volume.
- [x] Multi-stage Dockerfiles (`Dockerfile.api`, `Dockerfile.web`) with non-root security.
- [x] `.env.example` provided with documented defaults; secrets excluded in `.gitignore`.

## 2. Functionality
- [x] FastAPI async application with clean lifespan lifecycle.
- [x] `GET /health` (Liveness) returns 200 OK (`{"status": "ok"}`).
- [x] `GET /health/ready` (Readiness) probes PostgreSQL (`SELECT 1`) and Redis (`PING`).
- [x] Structured JSON logging with correlation IDs (`X-Request-ID`, `X-Process-Time-Ms`).
- [x] Uniform API error envelope format.
- [x] Next.js frontend communicates with backend API and renders system health.

## 3. Security
- [x] CORS middleware configured securely.
- [x] Secrets isolated in `.env` (never committed to git).
- [x] Non-root container users in Dockerfiles.

## 4. Tests
- [x] Pytest unit and integration tests for health endpoints and configuration.
- [x] Readiness test validates PostgreSQL and Redis connection failures gracefully.

## 5. Documentation
- [x] Root `README.md` with quickstart instructions.
- [x] `CONTRIBUTING.md` and `LICENSE`.
- [x] Initial `docs/architecture.md` outlining system architecture.

## 6. CI/CD
- [x] GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push and PR.
- [x] Linting, typechecking, tests, and build validation in CI.

## 7. Regression
- [x] Clean environment startup verified (`docker compose down -v && docker compose up --build -d`).

## 8. Final Verification
- [x] All Iteration 1 checks pass.
