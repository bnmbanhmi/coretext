# Story 1.3: Seeker Discovery Grid & Keyword Search

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Seeker,
I want to view a grid of available listings and search them by keyword,
so that I can scan for properties that interest me and find specific ones.

## Acceptance Criteria

1.  **Scenario 1: Default View (Grid)**
    -   **Given** there are multiple listings in the database with different statuses (AVAILABLE, RENTED, DRAFT).
    -   **When** I load the home page (root URL `/`).
    -   **Then** I see a grid of listings.
    -   **And** ONLY listings with status `AVAILABLE` are displayed.
    -   **And** the grid displays up to 20 listings per page (Pagination).

2.  **Scenario 2: Listing Card Content**
    -   **Given** a listing card is rendered in the grid.
    -   **Then** it must display:
        -   **Image:** A placeholder image (since image upload is not yet implemented).
        -   **Title:** Truncated to 2 lines if too long.
        -   **Price:** Formatted as "X.X million/month" (e.g., 5,000,000 -> "5.0 million/month").
        -   **Area:** Formatted as "XX m²".
        -   **Location:** Display the address (or District if parsed, but Address is sufficient for now).

3.  **Scenario 3: Keyword Search**
    -   **Given** I see a search bar at the top of the grid.
    -   **When** I type a keyword (e.g., "Studio") and hit Enter or Search.
    -   **Then** the grid updates to show only `AVAILABLE` listings where the `title` OR `description` contains the keyword (case-insensitive).
    -   **And** if no results found, show "No properties found".

4.  **Scenario 4: Pagination**
    -   **Given** there are more than 20 results.
    -   **When** I scroll to the bottom (or click "Next Page").
    -   **Then** the next set of listings loads.

## Tasks / Subtasks

-   [x] **Backend: Implement Public Listings API** (AC: 1, 3, 4)
    -   [x] Update `apps/api/app/schemas.py`: Add `ListingListResponse` (items list + total count) if needed, or just return list. Pagination usually needs total count.
    -   [x] Update `apps/api/app/routers/listings.py`: Add `GET /listings` endpoint.
        -   [x] Parameters: `skip` (int, default 0), `limit` (int, default 20), `q` (str, optional).
        -   [x] Logic: Query `Listing` table.
        -   [x] Filter: `status == ListingStatus.AVAILABLE`.
        -   [x] Filter (if `q`): `title.ilike(f"%{q}%") | description.ilike(f"%{q}%")`.
        -   [x] Sort: Created desc (newest first).
    -   [x] Add tests in `apps/api/tests/test_listings.py` for pagination and search filters.

-   [x] **Frontend: Implement Discovery Grid** (AC: 1, 2, 3, 4)
    -   [x] Create component `ListingCard` in `apps/web/src/components/ListingCard.tsx`.
        -   [x] Use a reliable placeholder image service (e.g., `https://placehold.co/600x400?text=Property`) or local asset.
        -   [x] Format price helper function.
    -   [x] Create page `HomePage` in `apps/web/src/pages/HomePage.tsx`.
        -   [x] Implement Search Bar UI.
        -   [x] Implement Grid Layout (CSS Grid).
        -   [x] Fetch data from `GET /listings` with query params.
        -   [x] Handle "Loading", "Error", and "Empty" states.
    -   [x] Update `apps/web/src/App.tsx` to set `HomePage` as the root route (`/`).

-   [x] **Data: Seed Data Update**
    -   [x] Ensure `test_listings.py` or a seed script creates listings with status `AVAILABLE` so the UI has something to show. (Note: Default is DRAFT).

## Dev Notes

-   **Architecture Patterns:**
    -   **FastAPI:** Use `Query` for optional parameters.
    -   **SQLAlchemy:** Use `or_` for the search query (`from sqlalchemy import or_`).
    -   **React:** Use `useEffect` for fetching. Keep state simple.

-   **Source Tree Components:**
    -   `apps/api/app/routers/listings.py`
    -   `apps/web/src/pages/HomePage.tsx`
    -   `apps/web/src/components/ListingCard.tsx`

-   **Dependencies:**
    -   Existing `Listing` model in `apps/api/app/models.py`.

### Project Structure Notes

-   Continue using `pnpm` and `uv` commands.
-   Ensure strictly typed interfaces in TS matching the API response.

### References

-   **Epic:** [Story 1.3 in Epics File](../planning-artifacts/epics.md#story-1-3-seeker-discovery-grid)
-   **UX:** [UX Design Specification](../planning-artifacts/ux-design-specification.md) (Card Layout)
-   **Previous Story:** [1-2 Admin Manual Listing Creation](1-2-admin-manual-listing-creation.md)

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

- Implemented Backend API `GET /listings` with pagination and search in `apps/api/app/routers/listings.py`.
- Added tests for API in `apps/api/tests/test_listings.py` covering pagination, filtering, and search.
- Created `ListingCard` component with tests.
- Created `HomePage` with search bar and grid layout, connected to API.
- Updated `App.tsx` to render `HomePage` at root.
- Verified all Acceptance Criteria with tests.

### File List

apps/api/app/routers/listings.py
apps/api/tests/test_listings.py
apps/web/src/components/ListingCard.tsx
apps/web/src/components/ListingCard.test.tsx
apps/web/src/pages/HomePage.tsx
apps/web/src/pages/HomePage.css
apps/web/src/pages/HomePage.test.tsx
apps/web/src/App.tsx
