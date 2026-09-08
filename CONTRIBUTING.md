# Contributing to Cortexa

Thank you for your interest in contributing to Cortexa!

## Development Guidelines

1. **Follow Layer Separation**:
   - Keep API endpoints thin.
   - Separate domain logic from data access and route handlers.
   - Never hardcode environment variables or database URLs.

2. **Code Quality Requirements**:
   - **Backend**:
     - Lint: `ruff check .`
     - Format: `ruff format .`
     - Typecheck: `mypy apps/api/app`
     - Tests: `pytest`
   - **Frontend**:
     - Lint: `npm run lint`
     - Format: `npm run format`
     - Typecheck: `npm run type-check`

3. **Running the Stack Locally**:
   ```bash
   cp .env.example .env
   docker compose up --build
   ```

4. **Pull Requests**:
   - Ensure all CI quality checks pass on your branch.
   - Include unit/integration tests for any new endpoints or models.
