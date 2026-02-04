# Story 1.4: Property Detail View Metadata

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

**As a** Seeker,
**I want to** see the full details of a property,
**So that** I can decide whether to contact the landlord.

## Acceptance Criteria

1.  **Scenario 1: Full Data Rendering**
    -   **Given** I click on a listing with UUID `123e4567-e89b...`
    -   **When** the detail page loads
    -   **Then** all fields from the `listings` table are rendered
    -   **And** the `attributes` JSONB data is parsed and displayed as a "Features" list (e.g., "AC: Yes", "Balcony: No")

2.  **Scenario 2: Invalid ID**
    -   **Given** I navigate to `/listing/invalid-uuid-string`
    -   **Then** the system detects the malformed UUID
    -   **And** redirects me to a 404 Not Found page
    -   **And** suggests "Return to Home"

## Tasks / Subtasks

- [ ] **Task 1: Backend - Listing Detail Endpoint** (AC: 1, 2)
    - [ ] Update `apps/api/app/schemas/listing.py`: Ensure `Listing` (or new `ListingDetail`) schema covers `attributes` (JSONB) and all DB fields.
    - [ ] Implement `GET /api/v1/listings/{id}` in `apps/api/app/api/v1/listings.py`.
        -   Use `UUID` type hint for `id` to auto-validate format (FastAPI feature).
        -   Query DB by ID.
        -   Raise `HTTPException(status_code=404, detail="Listing not found")` if missing.
    - [ ] Add tests in `apps/api/tests/api/v1/test_listings.py` for valid ID, invalid ID (422), and non-existent ID (404).

- [ ] **Task 2: Shared - Sync Types** (AC: 1)
    - [ ] Manually update `packages/types/index.d.ts` to include the exact `Listing` interface matching the API response.
    - [ ] Ensure `attributes` is typed as `Record<string, any>` or specific shape if known.

- [ ] **Task 3: Frontend - API & State** (AC: 1)
    - [ ] Create `useListing` hook in `apps/web/src/features/listing/api/useListing.ts`.
        -   Use `useQuery` with key `['listings', id]`.
        -   Fetcher function should call `/api/v1/listings/{id}`.

- [ ] **Task 4: Frontend - Components & Page** (AC: 1, 2)
    - [ ] Create `ListingDetail` component in `apps/web/src/features/listing/components/ListingDetail.tsx`.
        -   Display Title, Price, Area, Address, Description.
        -   Iterate over `attributes` to display "Features" list.
        -   Handle styling (Tailwind).
    - [ ] Create `ListingDetailPage` in `apps/web/src/features/listing/pages/ListingDetailPage.tsx`.
        -   Use `useListing` hook.
        -   Handle `isLoading` (Skeleton).
        -   Handle `isError`: Check if error is 404 or invalid UUID -> Render `NotFoundPage` (or simple 404 component).
    - [ ] Create/Ensure `NotFoundPage` exists (or simple component).
    - [ ] Update `apps/web/src/App.tsx`: Add route `/listings/:id` pointing to `ListingDetailPage`.

## Developer Context & Guardrails

### Technical Requirements
-   **UUID Validation:** Rely on FastAPI's `id: UUID` path parameter type for automatic validation (returns 422 for invalid strings).
-   **JSONB Handling:** `attributes` field in DB is JSONB. Pydantic schema should type this as `Dict[str, Any]` or `Json`. In Frontend, render as key-value pairs.
-   **404 Handling:** Frontend should gracefully handle 404s from API. If `error.response.status === 404`, show "Listing Not Found".

### Architecture Compliance
-   **Backend:**
    -   Keep logic in `apps/api/app/api/v1/listings.py` (or service layer if established).
    -   Use `SQLAlchemy` async session.
-   **Frontend:**
    -   Feature-based: `apps/web/src/features/listing/`.
    -   State: `TanStack Query` for data fetching.
    -   Styling: `Tailwind CSS`.
    -   Routing: `React Router` (ensure usage matches existing app router).

### Library/Framework Requirements
-   **FastAPI:** Use `HTTPException` for errors.
-   **React:** Functional components, Hooks.
-   **TanStack Query:** Use `useQuery` options object syntax.

### File Structure Requirements
-   `apps/api/app/api/v1/listings.py` (Modify)
-   `apps/web/src/features/listing/api/useListing.ts` (New)
-   `apps/web/src/features/listing/components/ListingDetail.tsx` (New)
-   `apps/web/src/features/listing/pages/ListingDetailPage.tsx` (New)

### Testing Requirements
-   **Backend:** `pytest apps/api/tests/api/v1/test_listings.py`. Coverage: Success case, 404 case, 422 (invalid UUID) case.
-   **Frontend:** `vitest`. Test `ListingDetail` component rendering.

### Previous Story Intelligence
-   **Type Sync:** **Manual Action Required.** Backend Pydantic changes do NOT auto-sync to Frontend Types. You must copy the interface to `packages/types/index.d.ts`.
-   **Testing:** Remember `PYTHONPATH=.` for backend tests.

### Git Intelligence
-   Follow existing patterns in `apps/web/src/features/listing/`.

## Story Completion Status
- [x] Story created
- [x] Requirements analyzed
- [x] Tasks defined
- [x] Context populated
