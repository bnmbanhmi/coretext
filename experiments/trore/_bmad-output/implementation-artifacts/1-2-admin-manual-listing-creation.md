# Story 1.2: Admin Manual Listing Creation

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an Admin,
I want to manually input a new property listing via a form,
so that I can seed the platform with high-quality, verified data.

## Acceptance Criteria

1. **Scenario 1: Successful Creation**
   - **Given** I am authenticated as an Admin
   - **When** I fill out the "New Listing" form with valid data:
     - Title: "Sunny Studio in D1"
     - Price: 5,000,000
     - Area: 30
     - Address: "123 Le Loi"
   - **And** click "Create"
   - **Then** the system validates the input via Pydantic
   - **And** a new record is inserted into `listings`
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

- [x] Task 1: Backend - Define Listing Schemas & API Endpoint (AC: 1, 2)
  - [x] Define `ListingCreate` Pydantic model in `apps/api/app/schemas/listing.py` (fields: title, description, price, area, address, status, attributes).
  - [x] Implement `POST /api/v1/listings` endpoint in `apps/api/app/api/v1/listings.py`.
  - [x] Ensure DB session handling and Pydantic validation.
  - [x] Add unit tests for successful creation and validation errors in `apps/api/tests/api/v1/test_listings.py`.

- [x] Task 2: Shared - Sync Types (AC: 1)
  - [x] Run type generation script to update `packages/types/index.d.ts` with the new `ListingCreate` and `Listing` interfaces.

- [x] Task 3: Frontend - Create Listing Form (AC: 1, 2)
  - [x] Create `ListingForm` component in `apps/web/src/features/admin/components/ListingForm.tsx`.
  - [x] Implement form validation (client-side mirroring Pydantic rules) using `react-hook-form`.
  - [x] Implement `useCreateListing` mutation using TanStack Query.
  - [x] Handle error states (display inline errors).

- [x] Task 4: Frontend - Admin Page Integration (AC: 1, 3)
  - [x] Create `NewListingPage` in `apps/web/src/features/admin/pages/NewListingPage.tsx`.
  - [x] Add route `/admin/listings/new` protected by Admin auth (mock auth if needed for MVP).
  - [x] Implement success toast and redirection logic.
  - [x] Implement server error handling (toast + preserve form data).

## Dev Notes

- **Architecture Patterns:**
  - **Backend:** Use `Pydantic v2` for all validation. The `ListingCreate` schema is the source of truth.
  - **Frontend:** Use `react-hook-form` for uncontrolled form inputs to minimize re-renders.
  - **State:** Use `TanStack Query` for the mutation. Invalidating `['listings']` query key after success is crucial.
  - **Styling:** Use Tailwind CSS. Components should use `apps/web/src/components/ui` primitives if available (Button, Input).

- **Testing Standards:**
  - Backend: `pytest` with `TestClient`. Mock DB session.
  - Frontend: `vitest` + `testing-library/react`. specific test for `ListingForm` validation logic.

### Project Structure Notes

- **API:** Place schema in `apps/api/app/schemas/listing.py` (singular 'listing' vs plural file name convention - check existing). Architecture says `schemas/` folder.
- **Web:** Feature folder `apps/web/src/features/admin` does not exist yet? Check `apps/web/src/features`. If not, create it. `dashboard` was mentioned in architecture map for "Admin Features". Maybe use `apps/web/src/features/dashboard` instead of `admin` if that aligns better. Architecture says: "Dashboard: apps/web/src/features/dashboard". Let's stick to `dashboard` or `admin` - `dashboard` implies viewing, `listing-management` might be better, but let's use `dashboard` as the Admin Hub.

### References

- [Epics: Story 1.2](_bmad-output/planning-artifacts/epics.md#story-12-admin-manual-listing-creation)
- [Architecture: API Patterns](_bmad-output/planning-artifacts/architecture.md#api-naming-conventions)
- [UX: Button Hierarchy](_bmad-output/planning-artifacts/ux-design-specification.md#button-hierarchy)

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- Encountered `ModuleNotFoundError: No module named 'app'` when running backend tests. Resolved by setting `PYTHONPATH=.`.
- `apps/web` lacked testing configuration. Installed `vitest`, `jsdom`, `@testing-library/react` and configured `vite.config.ts`.
- Manually updated `packages/types/index.d.ts` as no generation script exists.

### Completion Notes List

- Implemented `ListingCreate` Pydantic model and `Listing` model in backend.
- Created `POST /api/v1/listings` endpoint with validation and DB insertion.
- Added comprehensive unit tests for backend endpoint.
- Updated `packages/types` with shared interfaces.
- Implemented `ListingForm` with `react-hook-form` and `zod` validation.
- Implemented `useCreateListing` hook with TanStack Query.
- Created `NewListingPage` with toast notification and redirection logic.
- Protected admin route with `AdminRoute` mock auth wrapper.
- Verified all acceptance criteria with tests.

### File List

- apps/api/app/schemas/listing.py
- apps/api/app/api/v1/listings.py
- apps/api/app/api/v1/__init__.py
- apps/api/app/main.py
- apps/api/tests/api/v1/test_listings.py
- apps/api/app/db/session.py
- packages/types/index.d.ts
- apps/web/src/features/admin/components/ListingForm.tsx
- apps/web/src/features/admin/components/ListingForm.test.tsx
- apps/web/src/features/admin/api/useCreateListing.ts
- apps/web/src/features/admin/pages/NewListingPage.tsx
- apps/web/src/lib/api.ts
- apps/web/src/lib/auth.tsx
- apps/web/src/App.tsx
- apps/web/src/setupTests.ts
- apps/web/vite.config.ts
- apps/web/package.json