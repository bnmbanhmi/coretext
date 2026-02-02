---
project_name: 'trore'
user_name: 'Minh'
date: 'Thursday, January 29, 2026'
sections_completed:
  ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'quality_rules', 'workflow_rules', 'anti_patterns']
status: 'complete'
rule_count: 27
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

- **Frontend:** React 19, Vite, Tailwind CSS (v3.4+), TypeScript 5.x
- **Backend:** Python 3.12, FastAPI (v0.109+), Pydantic v2
- **Database:** PostgreSQL 16 (via Supabase), SQLAlchemy 2.0+ (Async), Alembic (v1.13+)
- **Importer:** Python 3.12, Pandas (CSV Processing)
- **Infrastructure:** Docker, Turborepo, uv (Python pkg manager)
- **State/Data:** TanStack Query v5, Zustand v4
- **Auth:** Supabase Auth (Client & Admin)
- **AI:** Gemini Flash 2.0 (via Vertex AI SDK)

## Critical Implementation Rules

### Language-Specific Rules

- **TypeScript:** Strict mode enabled. No `any` type usage. Use absolute imports (`~/`).
- **Python:** Mandatory type hints for all arguments and return values. Use `uv` for dependency management.
- **Async:** FastAPI routes and SQLAlchemy sessions must be asynchronous.

### Framework-Specific Rules

- **React:** Functional components only with named exports. Custom hooks for complex logic. Use `queryOptions` for TanStack Query.
- **FastAPI:** Use `APIRouter` pattern. Strictly separate Pydantic schemas (Request/Response) from SQLAlchemy models.

### Testing Rules

- **Web:** Co-located `*.test.tsx` files with Vitest.
- **API:** `tests/` directory mirroring `app/` structure with Pytest.
- **Importer:** Integration tests running against mock files in Docker.

### Code Quality & Style Rules

- **Naming:** Plural `snake_case` for DB tables, `camelCase` for JSON APIs (enforced via Pydantic aliases).
- **Exports:** No default exports. Use named exports exclusively for consistency and better tooling support.

### Development Workflow Rules

- **Package Management:** Use `pnpm` for JS/TS and `uv` for Python.
- **Deployment:** Vercel for Frontend/API; Docker-based VPS for Importer.
- **Local Dev:** Use `pnpm dev` for the monorepo and `docker compose` for the local importer environment.

### Critical Don't-Miss Rules (Anti-Patterns)

- **Do NOT:** Use raw SQL strings; always use SQLAlchemy's expression language or ORM.
- **Do NOT:** Mix Pydantic v1 and v2 syntax. Strictly use v2 (`model_validate`, etc.).
- **Do NOT:** Hardcode secrets or credentials; use environment variables.
- **Do NOT:** Skip automated type generation for the frontend when backend schemas change.

---

## Usage Guidelines

**For AI Agents:**
- Read this file before implementing any code.
- Follow ALL rules exactly as documented.
- When in doubt, prefer the more restrictive option.
- Update this file if new patterns emerge.

**For Humans:**
- Keep this file lean and focused on agent needs.
- Update when technology stack changes.
- Review quarterly for outdated rules.
- Remove rules that become obvious over time.

Last Updated: Thursday, January 29, 2026