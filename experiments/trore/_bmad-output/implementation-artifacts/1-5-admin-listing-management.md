# Story 1.5: Admin Listing Management

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

**As an** Admin,
**I want to** edit existing property listings and manage their status,
**So that** I can correct errors, update information, and maintain high data quality for the platform.

## Acceptance Criteria

### Scenario 1: Edit Form Population
*   **Given** I am an authenticated Admin viewing the "Admin Dashboard" or "Listing Detail" page
*   **When** I click the "Edit" button for listing `L1`
*   **Then** I am navigated to `/admin/listings/edit/{L1_UUID}`
*   **And** the form is pre-filled with `L1`'s current data (Title, Price, Area, Address, Description, Attributes)
*   **And** the "Status" dropdown shows the current status (e.g., "AVAILABLE")

### Scenario 2: Successful Update
*   **Given** I am on the Edit Listing page for `L1`
*   **When** I change the Price from `5,000,000` to `5,500,000`
*   **And** I click "Save Changes"
*   **Then** the system validates the input
*   **And** sends a PATCH request to `/api/v1/listings/{L1_UUID}`
*   **And** the database is updated
*   **And** I see a success toast "Listing Updated Successfully"
*   **And** I am redirected back to the Listing Detail or Dashboard view

### Scenario 3: Status Lifecycle Management
*   **Given** a listing is currently "AVAILABLE"
*   **When** I change the status to "RENTED" or "ARCHIVED" via the dropdown
*   **And** I save
*   **Then** the listing's `status` field in the DB is updated
*   **And** the listing is immediately removed from the public "Seeker Discovery Grid" (which filters for AVAILABLE)

### Scenario 4: Validation Enforcement
*   **Given** I am editing a listing
*   **When** I clear the "Title" field (making it empty) or set "Price" to `-50`
*   **And** I attempt to save
*   **Then** the system blocks the request
*   **And** displays inline error messages (e.g., "Title is required", "Price must be positive")
*   **And** no API request is sent

## Tasks / Subtasks

- [x] **Frontend: Edit Listing Feature**
    - [x] Create `EditListingPage` component in `apps/web/src/features/dashboard`
    - [x] Create `useListingDetails` hook (if not exists) to fetch single listing data by ID
    - [x] Create `useUpdateListing` mutation hook using TanStack Query
    - [x] Reuse `ListingForm` component (refactor from Story 1.2 to be reusable for Create/Edit)
    - [x] Implement form population logic
    - [x] Add "Edit" button to Admin Dashboard row actions or Listing Detail view

- [x] **Backend: Update API Endpoint**
    - [x] Implement `PATCH /api/v1/listings/{id}` endpoint in `apps/api/app/api/v1/listings.py`
    - [x] Create `ListingUpdate` Pydantic schema (all fields optional) in `apps/api/app/schemas`
    - [x] Add service logic to handle partial updates in `apps/api/app/services`
    - [x] Ensure `updated_at` timestamp is refreshed automatically

- [x] **Integration & Testing**
    - [x] Verify Pydantic validation catches invalid inputs on update
    - [x] Verify status changes reflect immediately in public views (Seeker Grid)
    - [x] Add unit tests for `PATCH` endpoint

## Dev Notes

### Architecture Patterns & Constraints
*   **State Management:** Use `TanStack Query` for the update mutation (`useMutation`). Invalidate the `['listing', id]` and `['listings']` queries upon success to ensure fresh data.
*   **Form Reusability:** The "Create Listing" form (Story 1.2) should be refactored into a shared `ListingForm` that accepts `initialValues`. If `initialValues` are present, it's "Edit Mode".
*   **API Design:** Use `PATCH` for updates, not `PUT`, to allow partial updates (though the UI might send the whole object). The Pydantic model `ListingUpdate` should have all fields as `Optional`.
*   **Routing:** Admin routes should be protected. Ensure the user has the `admin` role (check Supabase Auth metadata or RBAC logic).

### Project Structure Alignment
*   **Frontend:** `apps/web/src/features/dashboard/pages/EditListingPage.tsx`
*   **Backend:** `apps/api/app/api/v1/listings.py` (add `update_listing` function)
*   **Schemas:** `apps/api/app/schemas/listing.py` (add `ListingUpdate`)

### References
*   [Architecture: Frontend State](_bmad-output/planning-artifacts/architecture.md#state-management-patterns)
*   [Architecture: API Patterns](_bmad-output/planning-artifacts/architecture.md#api--communication-patterns)
*   [UX: Feedback Patterns](_bmad-output/planning-artifacts/ux-design-specification.md#feedback-patterns)

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### Debug Log References
- No debug logs yet.

### Completion Notes List
- Validated against FR20 and FR27.
- Aligned with Architecture constraints for React/FastAPI/Supabase.
- Implemented `EditListingPage` with `ListingForm` refactored for reuse.
- Added `PATCH` endpoint for listing updates with partial update support (`ListingUpdate` schema).
- Implemented `useListingDetails` and `useUpdateListing` hooks using TanStack Query.
- Added "Edit Listing" button to `ListingDetail` view.
- Added comprehensive backend tests for update scenarios including validation, 404, and search index updates (status change).
- Refactored `NewListingPage` to use updated form component.

### File List
- apps/web/src/features/dashboard/pages/EditListingPage.tsx
- apps/web/src/features/admin/api/useListingDetails.ts
- apps/web/src/features/admin/api/useUpdateListing.ts
- apps/web/src/features/admin/components/ListingForm.tsx
- apps/web/src/features/admin/components/ListingForm.test.tsx
- apps/web/src/features/admin/api/useCreateListing.ts
- apps/web/src/features/admin/pages/NewListingPage.tsx
- apps/web/src/features/listing/components/ListingDetail.tsx
- apps/web/src/features/listing/pages/ListingDetailPage.tsx
- apps/web/src/App.tsx
- apps/api/app/schemas/listing.py
- apps/api/app/api/v1/listings.py
- apps/api/tests/api/v1/test_listings.py
- apps/web/src/lib/api.ts