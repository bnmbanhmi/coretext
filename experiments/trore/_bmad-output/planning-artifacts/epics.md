---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
---

# TroRe - Epic Breakdown

## Overview

This document provides the detailed epic and story breakdown for **TroRe**, the verified rental listing platform. This document serves as the **Single Source of Truth** for the development team. All implementation details must adhere strictly to the acceptance criteria defined herein.

## Epic List

### Epic 1: The MVP (Core Listing & Viewing)
**Goal:** Build the foundational platform enabling manual listing creation by Admins and public discovery by Seekers.
**Scope:** Project scaffolding, Database initialization, Admin Dashboard (Basic), Public Listing Grid, Detail Views.
**Key Success Metric:** System can successfully store and retrieve a listing with 100% data fidelity.

### Epic 2: Advanced Search & Filtering
**Goal:** Implement robust, high-performance search capabilities catering to both power users (ID Lookup) and browsers (Filtering).
**Scope:** UUID Lookup Service, Multi-faceted Filter Logic, Deep Linking, Map View.
**Key Success Metric:** <300ms latency for ID resolution.

### Epic 3: Data Import & Normalization
**Goal:** Implement a scalable ingestion pipeline to bulk-import listings from legacy systems (CSV) and normalize unstructured text.
**Scope:** CSV Parsing Service, Validation Layer, AI Summarization Integration, Duplicate Detection.
**Key Success Metric:** 100% successful import of valid CSV rows; 100% rejection of invalid rows with detailed error reports.

### Epic 4: Audit Logging & Compliance
**Goal:** Implement a comprehensive audit trail for all sensitive data modifications to ensure system integrity and accountability.
**Scope:** Price Change Logging, Status Change Logging, Admin Activity Dashboard.
**Key Success Metric:** Every `UPDATE` operation on the `listings` table triggers an immutable log entry.

---

## Epic 1: The MVP (Core Listing & Viewing)

### Story 1.1: Project Scaffolding & Database Foundation

**As a** Lead Developer,
**I want to** initialize the monorepo structure and core database schema,
**So that** the development team has a standardized, type-safe environment for feature implementation.

**Acceptance Criteria:**

**Scenario 1: Monorepo Initialization**
*   **Given** a clean working directory
*   **When** the initialization script is executed
*   **Then** a `Turborepo` workspace is created containing:
    *   `apps/web`: React 19 + Vite + TypeScript
    *   `apps/api`: FastAPI + Python 3.12 + Pydantic v2
    *   `packages/importer`: Python 3.12 + Pandas (Dockerized)
    *   `packages/types`: Shared TypeScript definitions
*   **And** `pnpm` workspace constraints are configured correctly
*   **And** `uv` is initialized for Python dependency management

**Scenario 2: Database Schema Migration**
*   **Given** a connection to the Supabase PostgreSQL instance
*   **When** `alembic upgrade head` is run
*   **Then** the `listings` table is created with the following schema:
    *   `id`: UUID (Primary Key, Default: `uuid_generate_v4()`)
    *   `title`: String (Not Null)
    *   `description`: Text
    *   `price`: Integer (Not Null, Check: `price >= 0`)
    *   `area_sqm`: Float (Not Null, Check: `area_sqm > 0`)
    *   `address`: String (Not Null)
    *   `status`: Enum ('DRAFT', 'AVAILABLE', 'RENTED', 'ARCHIVED')
    *   `attributes`: JSONB (Default: `{}`)
    *   `created_at`: Timestamptz (Default: `now()`)
    *   `updated_at`: Timestamptz (Default: `now()`)

**Scenario 3: Developer Experience**
*   **Given** the repo is cloned
*   **When** a developer runs `pnpm dev`
*   **Then** both the Frontend (localhost:5173) and Backend (localhost:8000) start concurrently
*   **And** Hot Module Replacement (HMR) is active for the frontend

### Story 1.2: Admin Manual Listing Creation

**As an** Admin,
**I want to** manually input a new property listing via a form,
**So that** I can seed the platform with high-quality, verified data.

**Acceptance Criteria:**

**Scenario 1: Successful Creation**
*   **Given** I am authenticated as an Admin
*   **When** I fill out the "New Listing" form with valid data:
    *   Title: "Sunny Studio in D1"
    *   Price: 5,000,000
    *   Area: 30
    *   Address: "123 Le Loi"
*   **And** click "Create"
*   **Then** the system validates the input via Pydantic
*   **And** a new record is inserted into `listings`
*   **And** I am redirected to the "Listing Detail" page
*   **And** a success toast "Listing Created Successfully" appears

**Scenario 2: Validation Failure**
*   **Given** I am on the "New Listing" form
*   **When** I enter a negative price (e.g., -100)
*   **Then** the form submission is blocked
*   **And** an inline error message "Price must be a positive number" is displayed
*   **And** no API request is sent

**Scenario 3: Server Error Handling**
*   **Given** the database is temporarily unreachable
*   **When** I submit a valid form
*   **Then** the API returns a 503 Service Unavailable
*   **And** the UI displays a generic error "System is currently busy, please try again later"
*   **And** the form data is NOT cleared (so I don't lose my work)

### Story 1.3: Seeker Discovery Grid

**As a** Seeker,
**I want to** view a grid of available listings,
**So that** I can scan for properties that interest me.

**Acceptance Criteria:**

**Scenario 1: Default View**
*   **Given** there are 50 "AVAILABLE" listings and 10 "RENTED" listings in the DB
*   **When** I load the home page
*   **Then** I see the 50 "AVAILABLE" listings displayed in a responsive grid
*   **And** the "RENTED" listings are hidden
*   **And** the grid uses infinite scroll or pagination (limit 20 per page)

**Scenario 2: Card Content**
*   **Given** a listing card is rendered
*   **Then** it must display:
    *   Primary Image (or placeholder)
    *   Title (Truncated to 2 lines)
    *   Price (Formatted as "X.X million/month")
    *   Area (Formatted as "XX m²")
    *   Location (District only)

### Story 1.4: Property Detail View

**As a** Seeker,
**I want to** see the full details of a property,
**So that** I can decide whether to contact the landlord.

**Acceptance Criteria:**

**Scenario 1: Full Data Rendering**
*   **Given** I click on a listing with UUID `123e4567-e89b...`
*   **When** the detail page loads
*   **Then** all fields from the `listings` table are rendered
*   **And** the `attributes` JSONB data is parsed and displayed as a "Features" list (e.g., "AC: Yes", "Balcony: No")

**Scenario 2: Invalid ID**
*   **Given** I navigate to `/listing/invalid-uuid-string`
*   **Then** the system detects the malformed UUID
*   **And** redirects me to a 404 Not Found page
*   **And** suggests "Return to Home"

---

## Epic 2: Advanced Search & Filtering

### Story 2.1: ID Lookup Service

**As a** Power User,
**I want to** paste a specific Listing UUID into the search bar,
**So that** I can navigate directly to that listing without browsing.

**Acceptance Criteria:**

**Scenario 1: Valid UUID Match**
*   **Given** the listing `a1b2c3d4...` exists and is "AVAILABLE"
*   **When** I paste `a1b2c3d4...` into the search bar and hit Enter
*   **Then** the system bypasses the search results page
*   **And** immediately redirects me to `/listings/a1b2c3d4...`

**Scenario 2: UUID Not Found**
*   **Given** the UUID `non-existent-id` is syntactically valid but not in the DB
*   **When** I search for it
*   **Then** the UI displays a "Listing Not Found" error state
*   **And** offers a button to "Search for similar listings"

**Scenario 3: Archived/Rented Listing**
*   **Given** listing `old-listing-id` is marked "RENTED"
*   **When** I search for it by ID
*   **Then** I am taken to the detail page
*   **But** a prominent "THIS PROPERTY IS NO LONGER AVAILABLE" banner is displayed
*   **And** the "Contact" buttons are disabled

### Story 2.2: Advanced Filtering UI

**As a** Seeker,
**I want to** filter results by multiple criteria,
**So that** I can narrow down the list to my specific needs.

**Acceptance Criteria:**

**Scenario 1: Multi-Select Logic**
*   **Given** I am on the search results page
*   **When** I set:
    *   Min Price: 3m
    *   Max Price: 5m
    *   District: "District 1" OR "District 3"
*   **Then** the results update to show listings that match (Price >= 3m AND Price <= 5m) AND (District IN [D1, D3])

**Scenario 2: Empty Result State**
*   **Given** I apply a filter combo that yields 0 results
*   **Then** the UI displays an illustration of an empty house
*   **And** displays text "No homes found matching your criteria"
*   **And** provides a "Clear Filters" button

### Story 2.6: Basic Map View

**As a** Visual User,
**I want to** see listing pins on a map,
**So that** I can understand the geographic distribution of rentals.

**Acceptance Criteria:**

**Scenario 1: Pin Rendering**
*   **Given** 20 listings with valid `lat/long` coordinates
*   **When** I toggle "Map View"
*   **Then** a map interface loads (Mapbox/Google Maps/Leaflet)
*   **And** 20 pins are rendered at the correct coordinates

**Scenario 2: Interaction**
*   **Given** I am on the Map View
*   **When** I click a pin
*   **Then** a "Mini Card" popover appears showing the Listing Title and Price
*   **And** clicking the popover navigates to the Detail View

---

## Epic 3: Data Import & Normalization

### Story 3.1: Bulk CSV Importer Service

**As an** Admin,
**I want to** upload a CSV file containing multiple listings,
**So that** I can populate the database in bulk from legacy Excel sheets.

**Acceptance Criteria:**

**Scenario 1: Valid CSV Structure**
*   **Given** I upload a CSV file.
*   **Then** the system MUST validate the file against the following strict schema:

| Column Header | Data Type | Requirement | Validation Rule |
| :--- | :--- | :--- | :--- |
| `ref_id` | String | Optional | Max 50 chars |
| `title` | String | **Required** | Min 10, Max 200 chars |
| `raw_price` | String | **Required** | Must contain digits |
| `raw_area` | String | **Required** | Must contain digits |
| `address_full` | String | **Required** | Min 10 chars |
| `description` | String | Optional | Max 2000 chars |
| `contact_phone`| String | **Required** | Vietnamese phone regex |
| `owner_name` | String | Optional | Alphabetic only |

**Scenario 2: Row-Level Validation**
*   **Given** a CSV with 100 rows
*   **And** Row 50 is missing the `raw_price` field
*   **When** the import runs
*   **Then** the system imports 99 valid rows
*   **And** generates an "Import Error Report" flagging Row 50 with "Missing Required Field: raw_price"

**Scenario 3: Large File Handling**
*   **Given** a CSV file with 10,000 rows (~5MB)
*   **When** I upload it
*   **Then** the request does not time out (processing happens asynchronously)
*   **And** I receive a "Processing ID" to track status

### Story 3.2: Listing Description Normalizer

**As an** Admin,
**I want** the system to automatically summarize and standardize the listing descriptions,
**So that** the public feed has a consistent, professional tone.

**Acceptance Criteria:**

**Scenario 1: AI Integration**
*   **Given** a raw description: "ROOM 4 RENT CHEAP!!! call me 090xxx full AC"
*   **When** the normalizer runs
*   **Then** it calls the LLM service (Gemini Flash) with a system prompt to "Summarize and Professionalize"
*   **And** outputs: "Affordable room available for rent. Features full air conditioning. Contact for details."

**Scenario 2: PII Stripping**
*   **Given** a description containing a phone number or email
*   **When** the normalizer runs
*   **Then** the output MUST NOT contain the phone number or email (as these should be stored in structured fields, not the text)

---

## Epic 4: Audit Logging & Compliance

### Story 4.1: Price Change Logging

**As a** Compliance Officer,
**I want** to track every modification to a listing's price,
**So that** we can resolve disputes and analyze market trends.

**Acceptance Criteria:**

**Scenario 1: Log Trigger**
*   **Given** listing `L1` has a price of 5,000,000
*   **When** Admin `A1` updates the price to 5,500,000 via the API
*   **Then** a new row is inserted into `listing_audit_logs`
*   **And** the row contains:
    *   `listing_id`: `L1`
    *   `actor_id`: `A1`
    *   `action`: 'UPDATE_PRICE'
    *   `old_value`: '5000000'
    *   `new_value`: '5500000'
    *   `timestamp`: UTC Now

**Scenario 2: Immutability**
*   **Given** an audit log record exists
*   **When** any user (including Admin) attempts to DELETE or UPDATE the log record via the API
*   **Then** the system returns 403 Forbidden
*   **And** the record remains unchanged (enforced via Database RLS or API Policy)

### Story 4.2: Audit Log Viewer

**As an** Admin,
**I want to** view the history of a listing,
**So that** I can see who changed what and when.

**Acceptance Criteria:**

**Scenario 1: Chronological Display**
*   **Given** a listing has 5 historical changes
*   **When** I view the "History" tab in the Admin Dashboard
*   **Then** I see a timeline sorted from Newest to Oldest
*   **And** each entry shows the Actor Name, Action Type, and the Diff (Old -> New)

**Scenario 2: Filter by User**
*   **Given** the audit log contains changes from multiple admins
*   **When** I filter by "Actor: Sarah"
*   **Then** I only see changes made by Sarah
