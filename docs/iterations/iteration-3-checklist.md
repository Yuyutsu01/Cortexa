# Iteration 3 — Definition of Done: Core Data & Domain Layer

**Git Tag:** `v0.3.0-data-layer`

---

## 1. Infrastructure
- [x] Clean database migration (`0002_core_data_and_domain_layer.py`) creates all domain tables, constraints, foreign keys, and indexes.
- [x] Reproducible from a clean checkout (`docker compose down -v && docker compose up -d && alembic upgrade head`).
- [x] PostgreSQL connection pooling with async SQLAlchemy 2.0 engine.

## 2. Architecture & Functionality
- [x] Strict 4-layer architecture enforced: **Route $\rightarrow$ Service $\rightarrow$ Domain / Repository $\rightarrow$ Database**. Zero raw DB queries in FastAPI route handlers.
- [x] **Repository Layer:** `BaseRepository[T]` for generic CRUD and `TenantRepository[T]` for multi-tenant data access automatically scoped by `organization_id`.
- [x] **Service Layer:** `BaseService` orchestrating business rules, authorization, domain events, and transaction boundaries.
- [x] **Atomic Transactions:** `service.transaction()` context manager supporting nested savepoints and automatic rollback on failure.
- [x] **Domain Events:** Async `EventDispatcher` supporting typed domain events and decoupled event handler subscriptions.
- [x] **Standard Pagination:** Uniform `PaginatedResponse[T]` metadata (`page`, `page_size`, `total`, `pages`) with bounded maximum page sizes (e.g. max 100).
- [x] **Safe Filtering & Sorting:** Strict Pydantic schema validation preventing raw SQL injection and invalid column sorting.

## 3. Data Integrity & Security
- [x] Database constraints enforced: Primary keys (UUIDv4), Foreign keys (`CASCADE` / `RESTRICT`), Unique constraints, Not-Null constraints, Timestamps (UTC).
- [x] Soft delete lifecycle: `is_deleted`, `deleted_at` fields with automated query filtering in repositories.
- [x] Mandatory tenant scoping: All tenant-owned records require `organization_id` and are filtered via `TenantRepository`.
- [x] Membership invariants: Prevents deleting the last active OWNER of an organization.

## 4. Tests
- [x] **Unit Tests:**
  - [x] Domain event dispatching & subscription (`test_domain_events.py`).
  - [x] Pagination parameter validation, max limits, and metadata calculation (`test_pagination_and_sorting.py`).
  - [x] Password hashing and token security (`test_security.py`).
- [x] **Integration Tests:**
  - [x] Repository CRUD and tenant-scoping operations (`test_repositories.py`).
  - [x] Atomic transaction rollback upon mid-operation failure (`test_transactions.py`).
  - [x] Multi-tenant data isolation and leakage prevention (`test_tenant_isolation.py`).
- [x] **API Route Tests:**
  - [x] Authentication & token lifecycle (`test_auth_api.py`).
  - [x] Organization lifecycle and listing (`test_organizations_api.py`).
  - [x] Membership management and RBAC rules (`test_memberships_api.py`).
  - [x] Audit log retrieval with pagination and filtering (`test_audit_api.py`).

## 5. Quality & Static Analysis
- [x] Unit, integration, and API test suite: 100% pass (`pytest`).
- [x] Ruff linter: 0 errors (`ruff check .`).
- [x] Ruff formatter: 100% compliant (`ruff format --check .`).
- [x] MyPy static type analysis: 0 errors in strict mode (`mypy apps/api/app`).

## 6. Documentation
- [x] `docs/data-model.md` detailing entities, ER relationships, mixins, and indexing strategy.
- [x] `docs/architecture.md` updated with 4-layer architecture, transaction handling, and domain event patterns.
- [x] `README.md` updated with Iteration 3 status and architectural principles.

## 7. CI/CD & Regression
- [x] GitHub Actions workflow passes all backend, frontend, and Docker validation jobs.
- [x] Iteration 1 regression check: Health and readiness probes verified.
- [x] Iteration 2 regression check: Authentication, RBAC, and tenant boundaries verified.

## 8. Final Verification
- [x] All Iteration 3 checks pass.
