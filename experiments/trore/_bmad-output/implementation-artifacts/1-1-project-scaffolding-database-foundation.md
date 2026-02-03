# Story 1.1: Project Scaffolding & Database Foundation

Status: ready-for-dev

## Story

**As a** Lead Developer,
**I want to** initialize the monorepo structure and core database schema,
**So that** the development team has a standardized, type-safe environment for feature implementation.

## Acceptance Criteria

**Scenario 1: Monorepo Initialization**
- **Given** a clean working directory
- **When** the initialization script is executed
- **Then** a `Turborepo` workspace is created containing:
  - `apps/web`: React 19 + Vite + TypeScript
  - `apps/api`: FastAPI + Python 3.12 + Pydantic v2
  - `packages/importer`: Python 3.12 + Pandas (Dockerized)
  - `packages/types`: Shared TypeScript definitions
- **And** `pnpm` workspace constraints are configured correctly
- **And** `uv` is initialized for Python dependency management

**Scenario 2: Database Schema Migration**
- **Given** a connection to the Supabase PostgreSQL instance
- **When** `alembic upgrade head` is run
- **Then** the `listings` table is created with the following schema:
  - `id`: UUID (Primary Key, Default: `uuid_generate_v4()`)
  - `title`: String (Not Null)
  - `description`: Text
  - `price`: Integer (Not Null, Check: `price >= 0`)
  - `area_sqm`: Float (Not Null, Check: `area_sqm > 0`)
  - `address`: String (Not Null)
  - `status`: Enum ('DRAFT', 'AVAILABLE', 'RENTED', 'ARCHIVED')
  - `attributes`: JSONB (Default: `{}`)
  - `created_at`: Timestamptz (Default: `now()`)
  - `updated_at`: Timestamptz (Default: `now()`)

**Scenario 3: Developer Experience**
- **Given** the repo is cloned
- **When** a developer runs `pnpm dev`
- **Then** both the Frontend (localhost:5173) and Backend (localhost:8000) start concurrently
- **And** Hot Module Replacement (HMR) is active for the frontend

## Developer Context & Technical Guardrails

### 🛠 Tech Stack & Version Specifics
- **Frontend:** **React 19** + Vite.
  - **Breaking Change Alert:** React 19 removes `propTypes` and `defaultProps`. Use TypeScript interfaces and ES6 default parameters.
  - **New Features:** Leverage `useTransition` for state updates if needed.
- **Backend:** **FastAPI** + **Pydantic v2**.
  - **Validation:** Use `model_dump()` (not `dict()`) and `@field_validator` (not `@validator`).
  - **Type Safety:** Use `Annotated` with `pydantic.Field` for domain constraints (e.g., `Annotated[int, Field(ge=0)]` for price).
- **Database:** **PostgreSQL** (Supabase) + **Alembic**.
  - **Async Required:** Alembic must be initialized with `async` template (`alembic init -t async`).
  - **Driver:** Use `asyncpg` for SQLAlchemy `create_async_engine`.
- **Package Management:**
  - **Node:** `pnpm` for `apps/web` and workspace management.
  - **Python:** `uv` for `apps/api` and `packages/importer`.

### 🏗 Architecture Compliance
- **Monorepo Structure:**
  - Root `package.json` manages workspaces.
  - `apps/api` and `packages/importer` are distinct Python projects. `uv` should be configured to handle them (either as a workspace or individual projects).
- **Data Modeling:**
  - **JSONB for Attributes:** The `attributes` column is critical for future flexibility.
  - **Enums:** `status` must be a proper PostgreSQL Enum type.
  - **Timestamps:** Use `Timestamptz` (timezone aware).

### 🧪 Testing & Validation Standards
- **Schema Validation:** Verify the table creation in Supabase/Postgres after migration.
- **Startup Validation:** Ensure `pnpm dev` launches all services without port conflicts.
- **Linting:** Ensure basic linting (ESLint for web, Ruff for python) is configured.

## Tasks / Subtasks

- [ ] **Task 1: Initialize Monorepo & Workspaces**
  - [ ] Initialize Turborepo.
  - [ ] Configure `pnpm-workspace.yaml`.
  - [ ] Initialize `uv` for Python projects.

- [ ] **Task 2: Backend Scaffold (FastAPI)**
  - [ ] Create `apps/api` directory.
  - [ ] Initialize FastAPI project with Pydantic v2.
  - [ ] Configure `uv` dependencies (fastapi, uvicorn, sqlalchemy, alembic, asyncpg).

- [ ] **Task 3: Database & Migrations**
  - [ ] Initialize Alembic (`alembic init -t async`).
  - [ ] Configure `alembic.ini` and `env.py` for async execution.
  - [ ] Define `listings` table model in SQLAlchemy.
  - [ ] Generate and run migration (`alembic revision --autogenerate`, `alembic upgrade head`).

- [ ] **Task 4: Frontend Scaffold (React 19)**
  - [ ] Create `apps/web` using Vite (React TS template).
  - [ ] Ensure React 19 dependencies.

- [ ] **Task 5: Importer Scaffold & Shared Types**
  - [ ] Create `packages/importer` (Python + Pandas).
  - [ ] Create `packages/types` (TypeScript).

- [ ] **Task 6: Developer Experience**
  - [ ] Configure `turbo.json` pipelines.
  - [ ] Create root `dev` script to run all apps.

## References
- Epics: `_bmad-output/planning-artifacts/epics.md` (Story 1.1)
- Architecture: `_bmad-output/planning-artifacts/architecture.md` (Stack & Structure)
- PRD: `_bmad-output/planning-artifacts/prd.md` (Classification)

## Dev Agent Record
- **Agent:** Gemini CLI (Auto-Generated Story)
- **Date:** 2026-02-03
