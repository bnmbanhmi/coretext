# Story 1.4: Property Detail View & Metadata

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Seeker,
I want to see the full details of a property,
so that I can decide whether to contact the landlord.

## Acceptance Criteria

1. **Scenario 1: Full Data Rendering**
   - **Given** I click on a listing with UUID `123e4567-e89b...`
   - **When** the detail page loads
   - **Then** all fields from the `listings` table are rendered
   - **And** the `attributes` JSONB data is parsed and displayed as a "Features" list (e.g., "AC: Yes", "Balcony: No")

2. **Scenario 2: Invalid ID**
   - **Given** I navigate to `/listing/invalid-uuid-string`
   - **Then** the system detects the malformed UUID
   - **And** redirects me to a 404 Not Found page
   - **And** suggests "Return to Home"

## Tasks / Subtasks

- [x] Backend: Verify `GET /listings/{id}` endpoint functionality (AC: 1)
  - [x] Ensure `attributes` JSONB column is included in response schema
  - [x] Ensure proper error handling for non-existent IDs (404)
- [x] Frontend: Create Listing Detail Route & Page (AC: 1)
  - [x] Add route `/listing/:id` in React Router
  - [x] Create `ListingDetailPage` component
- [x] Frontend: Implement Data Fetching (AC: 1)
  - [x] Create or update `useListing` hook to fetch by ID
  - [x] Handle loading and error states
- [x] Frontend: Implement Features List Component (AC: 1)
  - [x] Create `FeaturesList` component to parse and display `attributes` JSONB
  - [x] Style using Tailwind CSS (Grid/Flex)
- [x] Frontend: Implement Error Handling (AC: 2)
  - [x] Catch 404 errors from API
  - [x] Redirect or show 404 UI with "Return to Home" link
- [x] Testing (AC: 1, 2)
  - [x] Unit tests for `FeaturesList` parsing logic
  - [x] Integration test for `ListingDetailPage` rendering

## Dev Notes

- **Architecture:** Standard SPA pattern. Fetch data on mount.
- **Components:**
  - `apps/web/src/pages/ListingDetail.tsx` (New)
  - `apps/web/src/components/FeaturesList.tsx` (New)
  - `apps/api/app/routers/listings.py` (Verify/Update)
- **Styling:** Tailwind CSS. Use `grid` for feature list.
- **JSONB Attributes:** The `attributes` field is a flexible JSON object. The UI should robustly handle various keys/values.
- **Source:** [Story 1.4 in Epics](../planning-artifacts/epics.md#story-1-4-property-detail-view)

### Project Structure Notes

- Follows standard `apps/web` and `apps/api` structure.
- Component placement in `apps/web/src/components` or `apps/web/src/features/listing` if feature-sliced design is used.

### References

- [Epics - Story 1.4](../planning-artifacts/epics.md#story-1-4-property-detail-view)
- [UX Design - Transferable Patterns](../planning-artifacts/ux-design-specification.md#transferable-ux-patterns)

## Dev Agent Record

### Agent Model Used

Gemini-Pro-2.0-Flash

### Debug Log References

- None

### Completion Notes List

- Story file created based on Epics and UX Context.
- Implemented `GET /listings/{id}` endpoint in `apps/api/app/routers/listings.py` with `attributes` support.
- Updated `ListingResponse` schema in `apps/api/app/schemas.py`.
- Added backend tests in `apps/api/tests/test_listings.py`.
- Installed `react-router-dom` and `tailwindcss` (v3) in `apps/web`.
- Refactored `App.tsx` to use `BrowserRouter`.
- Created `FeaturesList` component with Tailwind styling.
- Created `useListing` hook for fetching data.
- Created `ListingDetailPage` with error handling and loading states.
- Updated `ListingCard` to link to detail page.
- Added comprehensive unit and integration tests for frontend components and pages.

### File List

- `_bmad-output/implementation-artifacts/1-4-property-detail-view-metadata.md`
- `apps/api/app/schemas.py`
- `apps/api/app/routers/listings.py`
- `apps/api/tests/test_listings.py`
- `apps/web/package.json`
- `apps/web/src/App.tsx`
- `apps/web/src/components/FeaturesList.tsx`
- `apps/web/src/components/FeaturesList.test.tsx`
- `apps/web/src/hooks/useListing.ts`
- `apps/web/src/pages/ListingDetailPage.tsx`
- `apps/web/src/pages/ListingDetailPage.test.tsx`
- `apps/web/src/components/ListingCard.tsx`
- `apps/web/src/components/ListingCard.test.tsx`
- `apps/web/src/pages/HomePage.test.tsx`
- `apps/web/tailwind.config.js`
- `apps/web/src/index.css`
- `apps/web/postcss.config.js`
