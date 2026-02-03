# Story 1.1: Project Scaffolding & Database Foundation

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

**As a** Lead Developer,
**I want to** initialize the monorepo structure and core database schema,
**So that** the development team has a standardized, type-safe environment for feature implementation.

## Acceptance Criteria

### Scenario 1: Monorepo Initialization
*   **Given** a clean working directory
*   **When** the initialization script is executed
*   **Then** a `Turborepo` workspace is created containing:
    *   `apps/web`: React 19 + Vite + TypeScript
    *   `apps/api`: FastAPI + Python 3.12 + Pydantic v2
    *   `packages/importer`: Python 3.12 + Pandas (Dockerized)
    *   `packages/types`: Shared TypeScript definitions
*   **And** `pnpm` workspace constraints are configured correctly
*   **And** `uv` is initialized for Python dependency management

### Scenario 2: Database Schema Migration
*   **Given** a connection to the Supabase PostgreSQL instance
*   **When** `alembic upgrade head` is run
*   **Then** the `listings` table is created with the following schema:
    *   `id`: UUID (Primary Key, Default: `uuid_generate_v4()`)
    *   `title`: String (Not Null)
    *   `description`: Text
    *   `price`: Integer (Not Null, Check: `price >= 0`)
    *   `area_sqm`: Float (Not Null, Check: `area_sqm > 0`)
    *   `address`: String (Not Null)
    *   `status`: Enum ('DRAFT', 'AVAILABLE', 'RENTED', 'ARCHIVED')
    *   `attributes`: JSONB (Default: `{}`)
    *   `created_at`: Timestamptz (Default: `now()`)
    *   `updated_at`: Timestamptz (Default: `now()`)

### Scenario 3: Developer Experience
*   **Given** the repo is cloned
*   **When** a developer runs `pnpm dev`
*   **Then** both the Frontend (localhost:5173) and Backend (localhost:8000) start concurrently
*   **And** Hot Module Replacement (HMR) is active for the frontend

## Tasks / Subtasks

- [ ] Initialize Monorepo Root
  - [ ] Create `package.json`, `turbo.json`, `pnpm-workspace.yaml`.
  - [ ] Initialize `uv` workspace (`pyproject.toml`) and lockfile.
  - [ ] Configure `git` (ignore files).
- [ ] Scaffold `apps/web` (Frontend)
  - [ ] Initialize Vite + React 19 + TypeScript.
  - [ ] Install & Configure Tailwind CSS.
  - [ ] Install Zustand, TanStack Query, React Router.
  - [ ] Setup folder structure (`features/`, `components/`, `lib/`).
- [ ] Scaffold `apps/api` (Backend)
  - [ ] Create directory structure (`app/core`, `app/db`, `app/models`, `app/schemas`, `app/api`).
  - [ ] Install FastAPI, Pydantic v2, SQLAlchemy, Alembic via `uv`.
  - [ ] Configure `main.py` entry point.
  - [ ] Setup `vercel.json` for deployment.
- [ ] Scaffold `packages/importer` (Data Ingestion)
  - [ ] Create `Dockerfile` (Python 3.12 Slim).
  - [ ] Create `main.py` skeleton and `src/` structure.
  - [ ] Install Pandas, Tenacity, HTTPX via `uv`.
- [ ] Scaffold `packages/types` (Shared)
  - [ ] Initialize generic TS package.
  - [ ] Create placeholder `index.d.ts`.
- [ ] Database & Migrations
  - [ ] Initialize Alembic in `apps/api`.
  - [ ] Define `listings` table model in SQLAlchemy.
  - [ ] Generate and verify initial migration script.
- [ ] Developer Experience
  - [ ] Configure `turbo dev` to run web and api concurrently.
  - [ ] Verify `pnpm dev` starts everything correctly.

## Developer Context

### Tech Stack Rules
- **Monorepo:** Turborepo managed with `pnpm`.
- **Python Deps:** Managed globally and per-package using `uv`.
- **Frontend:** React 19, Vite, TypeScript, Tailwind CSS.
- **Backend:** FastAPI, Python 3.12, Pydantic v2 (strict schemas).
- **Database:** PostgreSQL (Supabase) via SQLAlchemy (ORM) and Alembic (Migrations).
- **Naming:**
  - JSON/API: **camelCase** (Enforced by Pydantic `alias_generator`).
  - Python: **snake_case**.
  - Components: **PascalCase**.

### Architecture Compliance
- **Folder Structure:** MUST strictly follow the architecture document.
  - `apps/web/src/features/{featureName}`
  - `apps/api/app/{layer}/{module}.py`
- **Secrets:** NO hardcoded secrets. Use `python-dotenv` or `dotenv` for local dev.
- **Type Safety:** Ensure Pydantic models are the source of truth.

### File Structure Requirements
```
trore/
├── package.json
├── turbo.json
├── pnpm-workspace.yaml
├── pyproject.toml
├── apps/
│   ├── web/ (Vite)
│   └── api/ (FastAPI)
└── packages/
    ├── importer/ (Docker)
    └── types/
```

### Testing Requirements
- **Web:** Vitest configuration (setup only, tests not required for scaffolding).
- **API:** Pytest configuration (setup only).

## Latest Tech Information
- **React 19:** Ensure strictly using `react@rc` or latest stable if released, otherwise `react@18.3` if 19 is unstable. *Architecture says React 19, verify stability or use latest stable.*
- **FastAPI:** Use `fastapi>=0.109.0` for Pydantic v2 support.
- **Pydantic:** Use `pydantic>=2.5.0`.
- **UV:** Use latest `uv` version for pip replacement.

## Project Context Reference
- **Architecture:** `_bmad-output/planning-artifacts/architecture.md`
- **Design:** `_bmad-output/planning-artifacts/ux-design-specification.md` (for checking structure compatibility)

## Dev Agent Record

### Agent Model Used
Gemini Pro

### Completion Notes List
- Comprehensive tasks derived from Architecture and Epics.
- Tech stack locked to Architecture decisions.
