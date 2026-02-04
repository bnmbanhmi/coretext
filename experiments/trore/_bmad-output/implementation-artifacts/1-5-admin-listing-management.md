# Story 1.5: Admin Listing Management

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an Admin,
I want to view a comprehensive list of all property listings and have the ability to edit or delete them,
so that I can maintain the quality, accuracy, and freshness of the platform's data.

## Acceptance Criteria

1. **Scenario 1: Admin Listings Dashboard**
   - **Given** I am logged in as an Admin (or accessing the Admin route)
   - **When** I navigate to `/admin/listings`
   - **Then** I see a tabular view of all listings in the system
   - **And** the table displays key columns: UUID (shortened), Title, Price, Area, Address, Created At
   - **And** each row has "Edit" and "Delete" actions

2. **Scenario 2: Edit Listing Flow**
   - **Given** I click the "Edit" button for a listing
   - **When** the Edit page loads (e.g., `/admin/listings/:id/edit`)
   - **Then** the form is pre-filled with the existing data
   - **When** I modify fields (e.g., change Price or Title) and click "Save"
   - **Then** the system updates the record in the database
   - **And** I am redirected back to the Dashboard with a success toast

3. **Scenario 3: Delete Listing Flow**
   - **Given** I click the "Delete" button for a listing
   - **When** the confirmation dialog appears "Are you sure you want to delete this listing?"
   - **And** I confirm
   - **Then** the listing is permanently removed from the database
   - **And** the Dashboard refreshes to show the listing is gone
   - **And** a success toast is displayed

## Tasks / Subtasks

- [x] **Backend: Implement Management Endpoints** (AC: 1, 2, 3)
  - [x] `GET /listings` (Admin view) - Ensure it returns all fields needed for the table. Support basic pagination if possible (limit/offset).
  - [x] `PUT /listings/{id}` - Update endpoint. Create Pydantic model `ListingUpdate` (all fields optional).
  - [x] `DELETE /listings/{id}` - Delete endpoint.
- [x] **Frontend: Setup Admin Layout & State** (AC: 1)
  - [x] Install `@tanstack/react-query` (Required by Architecture).
  - [x] Create `useListings` hook using React Query for fetching the list.
  - [x] Create `useDeleteListing` mutation.
  - [x] Create `useUpdateListing` mutation.
- [x] **Frontend: Implement Dashboard Page** (AC: 1, 3)
  - [x] Create `apps/web/src/pages/admin/AdminDashboard.tsx`.
  - [x] Implement a Table component using Tailwind CSS (Header, Rows, Actions).
  - [x] Integrate `useListings` to populate the table.
  - [x] Implement "Delete" action with `window.confirm` or a simple modal.
- [x] **Frontend: Implement Edit Page** (AC: 2)
  - [x] Create `apps/web/src/pages/admin/EditListingPage.tsx`.
  - [x] Reuse or adapt the Form from Story 1.2 (`NewListingPage`).
  - [x] specific: Ensure the form handles "Loading" state while fetching existing data.
  - [x] Connect to `useUpdateListing` mutation.
- [x] **Testing**
  - [x] Backend: Unit tests for PUT and DELETE endpoints.
  - [x] Frontend: Integration test for the Dashboard rendering and Edit flow.

## Dev Notes

- **Architecture Alignment:**
  - **State Management:** The architecture specifies `TanStack Query` for server state. Since it is missing from `package.json`, **you must install it**: `npm install @tanstack/react-query` (or pnpm).
  - **Router:** Use `react-router-dom` (already installed).
  - **Styling:** Tailwind CSS.

- **Code Reuse:**
  - The "New Listing" form from Story 1.2 is likely reusable. Refactor it into a `ListingForm` component that accepts `initialValues` and an `onSubmit` handler to support both Create and Edit modes.

- **Security:**
  - While full Auth is not yet implemented, organize Admin routes under a common path (`/admin`) to make future protection easier.

### Project Structure Notes

- `apps/api/app/routers/listings.py`: Add the new endpoints here.
- `apps/web/src/pages/admin/`: Create this folder for admin-specific pages.
- `apps/web/src/components/`: Check for reusable form components.

### References

- [Epics - FR20, FR27](../planning-artifacts/epics.md)
- [Architecture - State Management](../planning-artifacts/architecture.md#state-management-patterns)
- [Story 1.2 - Admin Manual Listing Creation](1-2-admin-manual-listing-creation.md)

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

- Fixed Backend DELETE endpoint 204 error.
- Restored client-side validation in NewListingPage after refactor.

### Completion Notes List

- Implemented Admin Listing Management (Story 1.5).
- Added `GET /listings?admin_view=true`, `PUT /listings/{id}`, `DELETE /listings/{id}` in API.
- Integrated `@tanstack/react-query` for state management.
- Created Admin Dashboard with list, delete, and edit capabilities.
- Refactored `NewListingPage` to use reusable `ListingForm` component.
- Implemented `EditListingPage` reusing `ListingForm`.
- Added backend unit tests and frontend integration tests.
- All 15 tests passed.

### File List
apps/api/app/routers/listings.py
apps/api/app/schemas.py
apps/api/tests/test_listings.py
apps/web/package.json
apps/web/src/main.tsx
apps/web/src/App.tsx
apps/web/src/pages/NewListingPage.tsx
apps/web/src/components/ListingForm.tsx
apps/web/src/features/admin/hooks/useAdminListings.ts
apps/web/src/pages/admin/AdminDashboard.tsx
apps/web/src/pages/admin/EditListingPage.tsx
apps/web/src/pages/admin/AdminDashboard.test.tsx
apps/web/src/pages/admin/EditListingPage.test.tsx
