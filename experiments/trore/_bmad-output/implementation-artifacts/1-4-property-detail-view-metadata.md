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

- [ ] Backend: Verify `GET /listings/{id}` endpoint functionality (AC: 1)
  - [ ] Ensure `attributes` JSONB column is included in response schema
  - [ ] Ensure proper error handling for non-existent IDs (404)
- [ ] Frontend: Create Listing Detail Route & Page (AC: 1)
  - [ ] Add route `/listing/:id` in React Router
  - [ ] Create `ListingDetailPage` component
- [ ] Frontend: Implement Data Fetching (AC: 1)
  - [ ] Create or update `useListing` hook to fetch by ID
  - [ ] Handle loading and error states
- [ ] Frontend: Implement Features List Component (AC: 1)
  - [ ] Create `FeaturesList` component to parse and display `attributes` JSONB
  - [ ] Style using Tailwind CSS (Grid/Flex)
- [ ] Frontend: Implement Error Handling (AC: 2)
  - [ ] Catch 404 errors from API
  - [ ] Redirect or show 404 UI with "Return to Home" link
- [ ] Testing (AC: 1, 2)
  - [ ] Unit tests for `FeaturesList` parsing logic
  - [ ] Integration test for `ListingDetailPage` rendering

## Dev Notes

- **Architecture:** Standard SPA pattern. Fetch data on mount.
- **Components:**
  - `apps/web/src/pages/ListingDetail.tsx` (New)
  - `apps/web/src/components/FeaturesList.tsx` (New)
  - `apps/api/app/routers/listings.py` (Verify/Update)
- **Styling:** Tailwind CSS. Use `grid` for feature list.
- **JSONB Attributes:** The `attributes` field is a flexible JSON object. The UI should robustly handle various keys/values.
- **Source:** [Story 1.4 in Epics](_bmad-output/planning-artifacts/epics.md#story-1-4-property-detail-view)

### Project Structure Notes

- Follows standard `apps/web` and `apps/api` structure.
- Component placement in `apps/web/src/components` or `apps/web/src/features/listing` if feature-sliced design is used.

### References

- [Epics - Story 1.4](_bmad-output/planning-artifacts/epics.md#story-1-4-property-detail-view)
- [UX Design - Transferable Patterns](_bmad-output/planning-artifacts/ux-design-specification.md#transferable-ux-patterns)

## Dev Agent Record

### Agent Model Used

Gemini-Pro-2.0-Flash

### Debug Log References

- None

### Completion Notes List

- Story file created based on Epics and UX Context.

### File List

- `_bmad-output/implementation-artifacts/1-4-property-detail-view-metadata.md`
