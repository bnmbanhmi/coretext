# Story 1.1: Project Scaffolding & Database Foundation

Status: ready-for-dev

## Story

**As a** Lead Developer,
**I want to** initialize the monorepo structure and core database schema,
**So that** the development team has a standardized, type-safe environment for feature implementation.

## Acceptance Criteria

### Scenario 1: Monorepo Initialization
**Given** a clean working directory
**When** the initialization script is executed
**Then** a `Turborepo` workspace is created containing:
- `apps/web`: React 19 + Vite + TypeScript
- `apps/api`: FastAPI + Python 3.12 + Pydantic v2
- `packages/importer`: Python 3.12 + Pandas (Dockerized)
- `packages/types`: Shared TypeScript definitions
**And** `pnpm` workspace constraints are configured correctly
**And** `uv` is initialized for Python dependency management

### Scenario 2: Database Schema Migration
**Given** a connection to the Supabase PostgreSQL instance
**When** `alembic upgrade head` is run
**Then** the `listings` table is created with the following schema:
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

### Scenario 3: Developer Experience
**Given** the repo is cloned
**When** a developer runs `pnpm dev`
**Then** both the Frontend (localhost:5173) and Backend (localhost:8000) start concurrently
**And** Hot Module Replacement (HMR) is active for the frontend

## Technical Requirements & Developer Context

### Architecture Compliance
- **Monorepo Strategy:** Use **Turborepo** (v2.8.1+) for orchestration.
- **Dependency Management:**
  - **Node.js:** `pnpm` (latest) for `apps/web` and `packages/types`.
  - **Python:** `uv` (latest stable) for `apps/api` and `packages/importer`. Ensure `pyproject.toml` workspaces are configured if supported, or individual configs.
- **Type Safety Pipeline:** Initialize the structure where `apps/api/app/schemas` (Pydantic) will eventually generate types to `packages/types`, which are then consumed by `apps/web`.
- **Auth Foundation:** Scaffold the files `apps/web/src/lib/supabase.ts` (Client) and `apps/api/app/core/security.py` (Verify Token placeholder).

### Library & Framework Requirements (Latest Stable)
Ensure the following specific versions (or newer) are used to prevent "outdated stack" issues:
- **Frontend:**
  - **React:** v19.2.4 (Stable)
  - **Vite:** v7.3.1
  - **Supabase JS:** v2.93.3
- **Backend (API):**
  - **FastAPI:** v0.124.4
  - **Pydantic:** v2.12.5 (Ensure v2 usage for schemas)
  - **Python:** 3.12
  - **Alembic:** v1.18.3
- **Build/Tools:**
  - **Turborepo:** v2.8.1

### File Structure Requirements
Ensure the following directory structure is established:

```
/
├── apps/
│   ├── web/              # React 19, Vite
│   └── api/              # FastAPI, Python 3.12
├── packages/
│   ├── importer/         # Python 3.12, Pandas
│   └── types/            # Shared TypeScript definitions
├── turbo.json            # Turborepo config
├── pnpm-workspace.yaml   # pnpm workspace config
└── pyproject.toml        # uv workspace config (if applicable) or root config
```

### Database Schema Details
- **Table:** `listings`
- **Extensions:** Ensure `uuid-ossp` is enabled for `uuid_generate_v4()`.
- **Columns:**
  - `price` and `area_sqm` must have Check Constraints (`price >= 0`, `area_sqm > 0`).
  - `status` should be a PostgreSQL ENUM type.
  - `attributes` is JSONB for flexibility (future-proofing).

## Testing Requirements
- **Frontend:** Install **Vitest** configuration in `apps/web`.
- **Backend:** Install **Pytest** configuration in `apps/api`.
- **CI/CD Prep:** Ensure `pnpm build` and `pnpm test` commands are wired up in `package.json` scripts for the root and packages.

## Latest Tech Information (Research Findings)
- **React 19:** Released Jan 2026. Use the new Hooks and Server Components paradigms where applicable (though this is a SPA, React 19 features are relevant).
- **FastAPI:** Recent versions have improved Pydantic v2 integration. Ensure `model_config` is used instead of the old `Config` class.
- **uv:** This is the preferred Python package manager. Use `uv pip install` or `uv sync` patterns.

## References
- **Epic:** Story 1.1 in Epics File
- **Architecture:** Requirements to Structure Mapping, Implementation Handoff
- **PRD:** Project Classification (Hybrid Multi-Cloud SPA)

## Completion Status
- [x] Context Analysis
- [x] Architecture Alignment
- [x] Tech Stack Verification
- [x] Story File Created
- [ ] Implementation (Next Step)
