# Story 1.2: Admin Manual Listing Creation

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an Admin,
I want to manually input a new property listing via a form,
so that I can seed the platform with high-quality, verified data.

## Acceptance Criteria

1. **Scenario 1: Successful Creation**
   - **Given** I am authenticated as an Admin (Note: Auth is not fully implemented, assume open or basic mock for now if needed, but requirements imply Admin role).
   - **When** I fill out the "New Listing" form with valid data:
     - Title: "Sunny Studio in D1"
     - Price: 5,000,000 (Positive Number)
     - Area: 30 (Positive Number)
     - Address: "123 Le Loi"
   - **And** click "Create"
   - **Then** the system validates the input via Pydantic
   - **And** a new record is inserted into `listings` table
   - **And** I am redirected to the "Listing Detail" page
   - **And** a success toast "Listing Created Successfully" appears

2. **Scenario 2: Validation Failure**
   - **Given** I am on the "New Listing" form
   - **When** I enter a negative price (e.g., -100)
   - **Then** the form submission is blocked
   - **And** an inline error message "Price must be a positive number" is displayed
   - **And** no API request is sent

3. **Scenario 3: Server Error Handling**
   - **Given** the database is temporarily unreachable
   - **When** I submit a valid form
   - **Then** the API returns a 503 Service Unavailable
   - **And** the UI displays a generic error "System is currently busy, please try again later"
   - **And** the form data is NOT cleared (so I don't lose my work)

## Tasks / Subtasks

- [ ] **Backend: Implement Listing Creation API** (AC: 1, 3)
  - [ ] Create Pydantic schema `ListingCreate` in `apps/api/app/schemas.py` (or similar) with validation for `price` (>0) and `area` (>0).
  - [ ] Implement DB model changes if `listings` table is missing (check `alembic` versions).
  - [ ] Create API endpoint `POST /listings` in `apps/api/app/main.py` (or routers).
  - [ ] Handle DB insertion and error cases (return 503 on DB connect failure).
- [ ] **Frontend: Implement New Listing Page** (AC: 1, 2, 3)
  - [ ] Create `apps/web/src/pages/NewListingPage.tsx`.
  - [ ] Create UI form with fields: Title, Price, Area, Address.
  - [ ] Implement client-side validation (Price > 0) to prevent submission.
  - [ ] Integrate with API `POST /listings`.
  - [ ] Implement redirection to Detail page on success.
  - [ ] Implement Toast notification on success.
  - [ ] Implement Error display without clearing form.
- [ ] **Integration Testing**
  - [ ] Verify flow from Form -> API -> DB -> UI Response.

## Dev Notes

- **Architecture Patterns:**
  - **Backend:** FastAPI + SQLAlchemy. Use Pydantic models for request/response validation.
  - **Frontend:** React 19 + Vite. Use functional components. Check if a Router is established; if not, use simple conditional rendering or basic routing if present.
  - **Database:** PostgreSQL. Table `listings` should exist or be created via Alembic.

- **Source Tree Components:**
  - `apps/api/app/` (main logic)
  - `apps/web/src/` (UI logic)
  - `packages/types/` (Shared types if applicable, but currently Pydantic is Python and Web is TS, so manual sync or generation needed. Keep separate for now unless shared generator exists).

- **Constraints:**
  - `price` must be >= 0.
  - `area_sqm` must be > 0.
  - Use `uuid` for IDs.

### Project Structure Notes

- Monorepo with `apps/api` and `apps/web`.
- Use `pnpm` for node modules.
- Use `uv` for python dependencies.

### References

- **Epic:** [Story 1.2 in Epics File](../planning-artifacts/epics.md#story-1-2-admin-manual-listing-creation)
- **UX:** [UX Design Specification](../planning-artifacts/ux-design-specification.md) (Palette: Trust Blue #0066CC)
- **DB Schema:** [Implementation Artifact 1.1](1-1-project-scaffolding-database-foundation.md#database-schema-details)

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash (Simulated)

### Debug Log References

- None

### Completion Notes List

- None

### File List
- `_bmad-output/implementation-artifacts/1-2-admin-manual-listing-creation.md`
