---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: 'Thursday, January 29, 2026'
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
  - docs/api-contracts.md
  - docs/architecture-backend.md
  - docs/architecture-web.md
  - docs/component-inventory-web.md
  - docs/data-models.md
  - docs/deployment-guide.md
  - docs/development-guide.md
  - docs/index.md
  - docs/integration-architecture.md
  - docs/project-overview.md
  - docs/source-tree-analysis.md
workflowType: 'architecture'
project_name: 'trore'
user_name: 'Minh'
date: 'Thursday, January 29, 2026'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together.

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
The architecture must support a dual-tier system: a **GCP Importer** for bulk data acquisition and normalization, and a **Vercel/Supabase App Tier** for high-velocity user interaction. Key features include UUID-based navigation, advanced filtering, and a robust Review Dashboard for human verification.

**Non-Functional Requirements:**
Performance is paramount, with specific sub-second targets for ID lookup and navigation. Security involves active bot defense and rate limiting. Reliability focuses on data consistency and audit logging.

**Scale & Complexity:**
The project is highly complex due to its hybrid cloud nature, the integration of LLMs for data normalization, and the requirement for a robust audit logging system.

- Primary domain: **Full-Stack / Data Engineering**
- Complexity level: **High**
- Estimated architectural components: **6+** (Importer, Normalizer, API Gateway, Auth/Store, Search Dispatcher, Review UI)

### Technical Constraints & Dependencies

- **Multi-Cloud:** GCP for processing, Vercel/Supabase for delivery.
- **Language:** Python (FastAPI/Cloud Run) for backend, TypeScript (React 19) for web.
- **Data Model:** JSONB pattern in PostgreSQL for listing attributes.

### Cross-Cutting Concerns Identified

- **Identity Management:** Standard UUID generation across tiers.
- **State Consistency:** Ensuring audit logs accurately reflect all changes.
- **Mobile Ergonomics:** 60fps interactions and touch-optimized navigation across all interfaces.

## Starter Template Evaluation

### Primary Technology Domain

Full-Stack / Hybrid Cloud (Custom Monorepo) based on project requirements analysis.

### Starter Options Considered

1. **`vercel/nextjs-fastapi-starter`**: Provides Vercel-optimized monorepo support for React+Python. *Rejected* because it enforces Next.js, while you specifically requested **React + Vite**.
2. **`create-t3-app`**: Excellent type-safety but lacks native Python integration and is Next.js-centric.
3. **Custom Turborepo Construction**: Using `pnpm` workspaces to manually wire React (Vite), FastAPI, and a standalone Docker importer. *Selected* as it perfectly fits your specific multi-deployment needs.

### Rejected Alternatives & Rationale

**1. Next.js (Full Stack)**
*   **Evaluation:** Considered for its integrated API routes and Server Components.
*   **Rejection Reason:** While powerful, the "App Router" model introduces complexity for a Python-heavy team. We need the backend logic (Importer/Normalizer) to be in Python to leverage Pandas and LangChain/Gemini SDKs natively. Splitting Next.js (Frontend) and Python (Backend) often leads to "two monorepos" anti-pattern unless orchestrated by Turborepo.

**2. Django (Backend)**
*   **Evaluation:** The "batteries-included" standard for Python web apps.
*   **Rejection Reason:** Too heavy for serverless. Django's startup time is suboptimal for Vercel functions (cold starts). FastAPI provides the necessary Pydantic validation speed and async support required for our high-throughput importer.

**3. Go (Golang)**
*   **Evaluation:** Excellent for the high-throughput importer service.
*   **Rejection Reason:** Team expertise constraint. Introducing a third language (TS, Python, Go) complicates the build pipeline and cognitive load. Python 3.12 is sufficiently performant for our I/O-bound tasks.

### Selected Starter: TroRe Hybrid Monorepo (Custom Construction)

**Rationale for Selection:**
No single "off-the-shelf" starter supports the specific combination of **Vite (Web)**, **FastAPI (Serverless API)**, and **Docker (VPS Importer)**. A custom construction using **Turborepo** provides the build orchestration needed to manage these distinct environments while maintaining a unified developer experience.

**Initialization Command:**

```bash
# 1. Initialize Turborepo (Custom)
npx create-turbo@latest trore --package-manager pnpm --design-system

# 2. Scaffold Web App (Vite + React + TS)
cd trore/apps
npm create vite@latest web -- --template react-ts

# 3. Scaffold API (FastAPI)
mkdir api && cd api
# (Manually add main.py, requirements.txt, and vercel.json)

# 4. Scaffold Importer (Python + Pandas + Docker)
cd ../..
mkdir packages/importer
# (Manually add Dockerfile, main.py, and requirements.txt)
```

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
- **Web:** TypeScript 5.x (React 19)
- **Backend:** Python 3.10+ (FastAPI)
- **Importer:** Python 3.10+ (Pandas)

**Styling Solution:**
- **Web:** Tailwind CSS (configured manually in Vite)

**Build Tooling:**
- **Monorepo:** Turborepo (High-performance build caching)
- **Web:** Vite (Fast HMR)
- **Importer:** Docker (Portable execution for VPS/Mac)

**Testing Framework:**
- **Web:** Vitest (matches Vite ecosystem)
- **Backend:** Pytest

**Code Organization:**
- `apps/web`: Vercel Deployment (Frontend)
- `apps/api`: Vercel Deployment (Serverless Functions)
- `packages/importer`: VPS Deployment (Docker Container)

## Core Architectural Decisions

### Component Anatomy & Responsibility

**1. The Importer Service (`packages/importer`)**
*   **Type:** Long-running Docker Container (Daemon).
*   **Runtime:** Python 3.12 Slim on Debian Bookworm.
*   **Responsibility:** Monitors a filesystem or S3 bucket for new `.csv` files. Validates headers against a schema. Emits processing events to the API.
*   **Key Libraries:** `pandas` (ETL), `tenacity` (Retry Logic), `httpx` (API Communication).
*   **Resource Constraints:** 512MB RAM Limit (Hard), 1 vCPU.

**2. The API Gateway (`apps/api`)**
*   **Type:** Serverless Function (Vercel).
*   **Runtime:** Python 3.12 (AWS Lambda / Vercel Runtime).
*   **Responsibility:** Authenticates users, validates Pydantic schemas, routes requests to Supabase, and serves as the bridge to the LLM.
*   **Key Libraries:** `fastapi`, `pydantic`, `sqlalchemy`, `google-cloud-aiplatform`.

**3. The Frontend App (`apps/web`)**
*   **Type:** Static SPA (Vercel Edge).
*   **Runtime:** Browser (ES2022+).
*   **Responsibility:** Renders the UI, manages client state (Zustand), handles routing (React Router), and caches server data (TanStack Query).

### Security Compliance Checklist

*   **[S-01] TLS Enforcement:** All internal service-to-service communication (Importer -> API) must occur over HTTPS, even within the same VPC, validating certificates.
*   **[S-02] Secrets Management:** No secrets in code. All credentials (DB URLs, API Keys) must be injected via `process.env` (Node) or `os.environ` (Python) at runtime.
*   **[S-03] Input Sanitization:** All user inputs must be stripped of HTML tags to prevent XSS. All SQL parameters must be bound to prevent SQL Injection (handled by SQLAlchemy).
*   **[S-04] Dependency Scanning:** CI/CD pipeline must run `pip-audit` and `npm audit` to block known CVEs.

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- **Data Modeling:** Transitioned to **JSONB** for property attributes. This simplifies the schema while maintaining flexibility. Strict application-layer validation will be enforced via **Pydantic v2**.
- **Migrations:** **Alembic (v1.18.2)** will manage PostgreSQL schema evolution.
- **Identity & Auth:** **Supabase Auth** for user-facing services; **Shared API Secret** for Importer-to-API communication.

**Important Decisions (Shape Architecture):**
- **Type Safety:** Automated TypeScript interface generation from Pydantic models using an **OpenAPI-to-TypeScript** bridge.
- **Frontend State:** **TanStack Query (v5.x)** for server-state/data-fetching; **Zustand (v5.x)** for lightweight client-side state.
- **Deployment:** **Docker-First** strategy for the Importer; **Vercel** for App Tier auto-deployment.

### Data Architecture

- **PostgreSQL JSONB Strategy:** Attributes are stored in a single `attributes` JSONB column.
- **Validation:** Pydantic models in the FastAPI layer will act as the "Gatekeeper," ensuring only valid keys and types are committed to the JSONB field.
- **Audit Logs:** Price changes and critical updates are stored in a `listing_audit_log` table.

### Authentication & Security

- **User Auth:** Supabase Auth (JWT-based).
- **Service Security:** The VPS Importer identifies itself via a `X-TRORE-SECRET` header. The API rejects any `POST /import` requests lacking this valid secret.
- **Rate Limiting:** Managed at the Vercel Edge layer to protect public endpoints.

### API & Communication Patterns

- **Pattern:** RESTful API via FastAPI.
- **Type Synchronization:** A shared `packages/types` directory in the monorepo will house the auto-generated TS types derived from the Python backend, ensuring the Frontend is always in sync with Backend changes.

### Frontend Architecture

- **Framework:** React 19 (Vite).
- **Data Management:** TanStack Query handles the caching of search results and listing details.
- **UI Logic:** Zustand manages the search and filtering state.

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
5 areas where AI agents could make different choices (Naming, Structure, API Formats, Error Handling, State Management).

### Naming Patterns

**Database Naming Conventions:**
- **Tables:** Plural snake_case (e.g., `listings`, `user_profiles`).
- **Columns:** snake_case (e.g., `is_active`, `created_at`).
- **Foreign Keys:** `singular_table_id` (e.g., `user_id`).
- **Indexes:** `idx_{table}_{columns}` (e.g., `idx_listings_uuid`).

**API Naming Conventions:**
- **Endpoints:** RESTful Plural (e.g., `/api/v1/listings`).
- **Parameters:** snake_case in URL (e.g., `?min_price=`), but **camelCase** in JSON bodies.
- **Header Keys:** Kebab-Case (e.g., `X-Trore-Secret`).

**Code Naming Conventions:**
- **TS Components:** PascalCase (`ListingCard.tsx`).
- **TS Variables/Functions:** camelCase.
- **Python Modules:** snake_case.
- **Python Classes:** PascalCase.

### Structure Patterns

**Project Organization:**
- **Tests:** Co-located `*.test.tsx` (Web) or `test_*.py` (Backend) next to source files.
- **Shared Code:** `packages/types` (Auto-generated TS interfaces), `packages/shared` (Common logic).
- **Features:** Group by Feature, not Type (e.g., `apps/web/src/features/search/` contains components, hooks, and types for Search).

**File Structure Patterns:**
- **Exports:** Named exports preferred over default exports.
- **Barrels:** `index.ts` files used only for public API of a feature module.

### Format Patterns

**API Response Formats:**
- **Success (Single):** Direct Object JSON (`{ "id": "..." }`).
- **Success (List):** Wrapped Object (`{ "items": [...], "meta": { "total": 100 } }`).
- **Error:** Standardized Error Object:
  ```json
  {
    "code": "INVALID_UUID",
    "message": "The UUID format is incorrect.",
    "details": { "input": "..." }
  }
  ```

**Data Exchange Formats:**
- **JSON Fields:** **camelCase** everywhere. Pydantic configured with `alias_generator=to_camel` and `populate_by_name=True`.
- **Dates:** ISO 8601 Strings (`2025-01-29T...Z`) exclusively.

### Communication Patterns

**Event System Patterns:**
- **Event Names:** `resource.action` (e.g., `listing.verified`, `import.completed`).
- **Payloads:** Must include `trace_id` for observability.

### State Management Patterns

**State Management Patterns:**
- **Server State:** TanStack Query keys as arrays: `['listings', { filter: ... }]`.
- **Client State:** Zustand stores named `use{StoreName}Store` (e.g., `useSearchStore`).

### Process Patterns

**Error Handling Patterns:**
- **Frontend:** API Errors -> Toast Notifications (via QueryObserver). Validation Errors -> Inline Field Errors.
- **Backend:** Raise `HTTPException` with standardized `code` strings, never raw strings.

**Loading State Patterns:**
- **Skeleton UI:** Use for initial loads (`isLoading`).
- **Spinner/Progress:** Use for background refetches or mutations (`isFetching`).

### Enforcement Guidelines

**All AI Agents MUST:**
- Use **camelCase** for all JSON keys, even when writing Python.
- Generate TypeScript types from Pydantic models before writing frontend code.
- Place tests next to the code they test.

## Project Structure & Boundaries

### Complete Project Directory Structure

```
trore/
├── package.json               # Root Monorepo Config
├── turbo.json                 # Turborepo Pipeline Config
├── pnpm-workspace.yaml        # Workspace Definition
├── uv.lock                    # [UV] Python Dependency Lockfile
├── pyproject.toml             # [UV] Root Python Workspace Config
├── .gitignore
├── .npmrc
├── README.md
├── apps/
│   ├── web/                   # [React 19 + Vite] Vercel Frontend
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.js
│   │   ├── tsconfig.json
│   │   ├── index.html
│   │   └── src/
│   │       ├── main.tsx
│   │       ├── App.tsx
│   │       ├── features/      # Feature-based Architecture
│   │       │   ├── search/
│   │       │   │   ├── components/  # SearchBar, FilterChips
│   │       │   │   ├── hooks/       # useSearchStore (Zustand)
│   │       │   │   └── api/         # queryOptions (TanStack)
│   │       │   ├── listing/
│   │       │   │   ├── components/  # ListingCard, DetailView
│   │       │   │   └── api/
│   │       │   └── dashboard/       # Admin Features
│   │       │       └── components/  # ReviewTable
│   │       ├── components/    # Shared UI (Buttons, Layouts)
│   │       │   ├── ui/
│   │       │   └── layout/
│   │       ├── lib/           # Core Utilities
│   │       │   ├── supabase.ts
│   │       │   └── api-client.ts
│   │       └── assets/
│   └── api/                   # [FastAPI] Vercel Serverless
│       ├── package.json       # For Vercel Build Scripts
│       ├── vercel.json        # Python Runtime Config
│       ├── pyproject.toml     # [UV] App Dependency Config
│       ├── main.py            # Entry Point
│       └── app/
│           ├── __init__.py
│           ├── core/          # Config, Security
│           ├── db/            # Database & Migrations
│           │   ├── session.py
│           │   └── migrations/ # Alembic
│           ├── models/        # SQLAlchemy Models
│           ├── schemas/       # Pydantic Models (Source of Truth)
│           ├── api/           # Route Handlers
│           │   └── v1/
│           │       ├── listings.py
│           │       └── import.py
│           └── services/      # Business Logic
│               ├── normalizer.py
│               └── audit.py
├── packages/
│   ├── importer/              # [Python + Pandas] VPS Worker
│   │   ├── Dockerfile         # Production Image
│   │   ├── docker-compose.yml # Local Dev Parity
│   │   ├── pyproject.toml     # [UV] Importer Dependency Config
│   │   ├── main.py            # Scheduler/Runner
│   │   └── src/
│   │       ├── pipelines/     # CSV Logic
│   │       └── utils/         # File Management
│   └── types/                 # [Shared] Generated Types
│       ├── package.json
│       └── index.d.ts         # Generated via openapi-typescript
└── .github/
    └── workflows/
        ├── deploy-web-api.yml # Vercel Deploy
        └── deploy-importer.yml # VPS Docker Deploy
```

### Architectural Boundaries

**API Boundaries:**
- **External:** `/api/v1/*` exposed via Vercel.
- **Internal:** `packages/importer` talks to `/api/v1/import` using `X-TRORE-SECRET`.

**Component Boundaries:**
- **Features:** Self-contained logic (Components + Hooks + API) in `apps/web/src/features`.
- **Shared UI:** Dumb, reusable components in `apps/web/src/components/ui`.

**Data Boundaries:**
- **Schema:** Defined in `apps/api/app/models` (SQLAlchemy).
- **Validation:** Enforced at `apps/api/app/schemas` (Pydantic).
- **Migrations:** Managed solely by Alembic in `apps/api`.

### Requirements to Structure Mapping

**Feature/Epic Mapping:**
- **Search & Discovery:** `apps/web/src/features/search`
- **Data Normalization:** `apps/api/app/services/normalizer.py`
- **Import Pipeline:** `packages/importer/src/pipelines`
- **Dashboard:** `apps/web/src/features/dashboard`

**Cross-Cutting Concerns:**
- **Type Safety:** Source of truth `apps/api/app/schemas` -> generated to `packages/types` -> consumed by `apps/web`.
- **Auth:** `apps/web/src/lib/supabase.ts` (Client) and `apps/api/app/core/security.py` (Verify Token).
- **Package Management:** **uv** is used for all Python projects (`api`, `importer`) via `pyproject.toml` workspaces (if supported) or individual configs.

### Integration Points

**Internal Communication:**
- **Web -> API:** REST calls typed via `packages/types`.
- **Importer -> API:** REST calls secured by Shared Secret.

**External Integrations:**
- **Supabase:** Auth & Database (Postgres).
- **Gemini Flash:** AI Normalization Service.

### File Organization Patterns

**Configuration:**
- **Root:** `package.json`, `turbo.json`, `pyproject.toml` (UV Workspace).
- **App-Level:** `vite.config.ts`, `vercel.json`.

**Source Organization:**
- **Web:** Feature-folder architecture.
- **API:** Service-layer pattern (Router -> Service -> DB).

**Test Organization:**
- **Web:** Co-located `ComponentName.test.tsx`.
- **API:** `tests/` directory mirroring `app/` structure.

### Development Workflow Integration

**Development Server Structure:**
- `pnpm dev` triggers `turbo dev` -> runs `vite` (Web) and `fastapi dev` (API).
- `docker compose up` runs the local Importer instance.

**Build Process Structure:**
- `turbo build` caches build artifacts for Web and API.
- `uv sync` ensures consistent Python environments across machines.

**Deployment Structure:**
- **Vercel:** Deploys `apps/web` and `apps/api`.
- **VPS:** Pulls Docker image built from `packages/importer`.

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
The mix of **Vite** (Web), **FastAPI** (API), and **Docker** (Importer) is orchestrated by **Turborepo** and **pnpm workspaces**, with **uv** for robust Python dependency management. This ensures a unified developer experience.

**Pattern Consistency:**
Enforcing **camelCase** for JSON fields ensures a seamless React frontend experience, while Pydantic handles the snake_case conversion transparently on the backend.

**Structure Alignment:**
The split between `apps/` (Vercel) and `packages/importer` (Docker) clearly defines deployment boundaries while maintaining a clean Monorepo flow.

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:**
- **Search:** `apps/web/src/features/search` + Zustand.
- **Normalization:** `apps/api/app/services/normalizer.py`.
- **Importer:** `packages/importer` (Dockerized).
- **Dashboard:** `apps/web/src/features/dashboard`.

**Non-Functional Requirements Coverage:**
- **Performance:** TanStack Query caching + Vercel Edge.
- **Security:** Shared Secret for Ingestion + Supabase Auth for Humans.
- **Reliability:** Docker parity between Mac (Dev) and VPS (Prod).

### Implementation Readiness Validation ✅

**Decision Completeness:**
All technologies (React 19, FastAPI, Pandas) and versions are locked. uv-based dependency management is established.

**Structure Completeness:**
The granular tree down to `features/` and `services/` provides clear boundaries for implementation agents.

### Gap Analysis Results

**Critical Gaps:**
None identified.

**Important Gaps:**
- **Type Generation Script:** The specific script to bridge Pydantic to TS needs to be written during the first sprint.
- **Docker/VPS CI/CD:** The GitHub Action for VPS deployment needs careful setup of SSH keys.

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**✅ Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**✅ Implementation Patterns**
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**✅ Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High

**Key Strengths:**
- **Hybrid Efficiency:** Combines Vercel's serverless speed with VPS's persistent processing power.
- **Type Safety:** Automated Pydantic-to-TS bridge.
- **Modern Tooling:** Uses **uv** and **Turborepo** for a high-velocity development cycle.

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented.
- Use implementation patterns consistently across all components.
- Respect project structure and boundaries.
- Refer to this document for all architectural questions.

**First Implementation Priority:**
Initialize the Turborepo Monorepo and scaffold the three core workspaces (`web`, `api`, `importer`) using **pnpm** and **uv**.

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅
**Total Steps Completed:** 8
**Date Completed:** Thursday, January 29, 2026
**Document Location:** _bmad-output/planning-artifacts/architecture.md

### Final Architecture Deliverables

**📋 Complete Architecture Document**
- All architectural decisions documented with specific versions
- Implementation patterns ensuring AI agent consistency
- Complete project structure with all files and directories
- Requirements to architecture mapping
- Validation confirming coherence and completeness

**🏗️ Implementation Ready Foundation**
- **Critical** architectural decisions made
- **5** implementation patterns defined
- **6+** architectural components specified
- **4** requirements fully supported

**📚 AI Agent Implementation Guide**
- Technology stack with verified versions
- Consistency rules that prevent implementation conflicts
- Project structure with clear boundaries
- Integration patterns and communication standards

### Implementation Handoff

**For AI Agents:**
This architecture document is your complete guide for implementing trore. Follow all decisions, patterns, and structures exactly as documented.

**First Implementation Priority:**
Initialize the Turborepo Monorepo and scaffold the three core workspaces (`web`, `api`, `importer`) using **pnpm** and **uv**.

**Development Sequence:**
1. Initialize project using documented starter template
2. Set up development environment per architecture
3. Implement core architectural foundations
4. Build features following established patterns
5. Maintain consistency with documented rules

### Quality Assurance Checklist

**✅ Architecture Coherence**
- [x] All decisions work together without conflicts
- [x] Technology choices are compatible
- [x] Patterns support the architectural decisions
- [x] Structure aligns with all choices

**✅ Requirements Coverage**
- [x] All functional requirements are supported
- [x] All non-functional requirements are addressed
- [x] Cross-cutting concerns are handled
- [x] Integration points are defined

**✅ Implementation Readiness**
- [x] Decisions are specific and actionable
- [x] Patterns prevent agent conflicts
- [x] Structure is complete and unambiguous
- [x] Examples are provided for clarity

### Project Success Factors

**🎯 Clear Decision Framework**
Every technology choice was made collaboratively with clear rationale, ensuring all stakeholders understand the architectural direction.

**🔧 Consistency Guarantee**
Implementation patterns and rules ensure that multiple AI agents will produce compatible, consistent code that works together seamlessly.

**📋 Complete Coverage**
All project requirements are architecturally supported, with clear mapping from business needs to technical implementation.

**🏗️ Solid Foundation**
The chosen starter template and architectural patterns provide a production-ready foundation following current best practices.

---

**Architecture Status:** READY FOR IMPLEMENTATION ✅

**Next Phase:** Begin implementation using the architectural decisions and patterns documented herein.

**Document Maintenance:** Update this architecture when major technical decisions are made during implementation.