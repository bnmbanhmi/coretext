---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
  - _bmad-output/planning-artifacts/ux-design-specification.md
---

# TroRe - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for TroRe, decomposing the requirements from the PRD and Architecture requirements into implementable generic listing platform stories.

## Epic List

### Epic 1: The MVP (Core Listing & Viewing)
Build the essential manual platform where Admins can create listings by hand and Seekers can discover and view them. Validates the core data model and user experience.

### Epic 2: Advanced Search & Filtering
Implement robust ID-based lookup and advanced filtering capabilities for power users.

### Epic 3: Data Import & Normalization
Implement a system to bulk import listings from external sources (CSV) and normalize their descriptions using simple AI summarization.

### Epic 4: Audit Logging
Implement comprehensive audit logging for sensitive data changes, specifically price updates.

## Epic 1: The MVP (Core Listing & Viewing)

Build the essential manual platform where Admins can create listings by hand and Seekers can discover and view them.

### Story 1.1: Project Scaffolding & Database Foundation

As a Developer,
I want to set up the monorepo and core database schema,
So that I have a solid foundation for implementing features.

**Acceptance Criteria:**

**Given** a clean project directory
**When** I run the initialization commands
**Then** a Turborepo monorepo is created with apps/web (Vite/React), apps/api (FastAPI), and packages/importer
**And** pnpm and uv are configured for dependency management
**And** the project directory structure matches the architectural design document

**Given** a Supabase project
**When** I apply the initial Alembic migrations
**Then** the listings and rooms tables are created with standard UUID primary keys and JSONB attributes

### Story 1.2: Admin Manual Listing Creation

As an Admin,
I want to manually input a new property listing,
So that I can start building the platform's data.

**Acceptance Criteria:**

**Given** I am logged into the Admin interface
**When** I enter a property address and details
**Then** the system assigns a standard UUID
**And** creates a new Listing record in the database
**And** the new listing is saved with status "Available"

### Story 1.3: Seeker Discovery Grid & Keyword Search

As a Seeker,
I want to browse available listings and search by keywords,
So that I can find properties that match my criteria.

**Acceptance Criteria:**

**Given** I am on the home page
**When** I enter a keyword or select filters
**Then** the grid updates to show matching "Available" listings
**And** each card displays the Price, Location, and key specs

### Story 1.4: Property Detail View

As a Seeker,
I want to view the full details of a property,
So that I can make an informed decision.

**Acceptance Criteria:**

**Given** I click on a listing card
**When** the detail page loads
**Then** I see the full address, specs, and images
**And** the URL is shareable

### Story 1.5: Admin Listing Management

As an Admin,
I want to edit existing listing attributes and manage their status,
So that I can keep the platform data accurate.

**Acceptance Criteria:**

**Given** I am viewing a listing in the Admin interface
**When** I update a field or toggle status
**Then** the change is saved immediately to the database

## Epic 2: Advanced Search & Filtering

Implement robust ID-based lookup and advanced filtering capabilities.

### Story 2.1: ID Lookup Service

As a User,
I want to paste a listing UUID to find a specific property,
So that I can quickly access a known listing.

**Acceptance Criteria:**

**Given** I paste a valid UUID in the search bar
**When** I submit
**Then** the system redirects me to the specific listing page

### Story 2.2: Advanced Filtering UI

As a User,
I want to filter by multiple criteria simultaneously,
So that I can narrow down results effectively.

**Acceptance Criteria:**

**Given** I am on the search page
**When** I select multiple filters (Price, Area, Rooms)
**Then** the results update to match the intersection of all filters

### Story 2.3: Direct Link Navigation

As a User,
I want deep links to specific searches or listings,
So that I can bookmark or share them.

**Acceptance Criteria:**

**Given** I have a URL with query parameters
**When** I load the page
**Then** the search state is restored exactly

### Story 2.4: Secure Contact Gate

As an Admin,
I want to require login before viewing owner contact info,
So that I can prevent unauthorized access.

**Acceptance Criteria:**

**Given** I am viewing a listing
**When** I click "Show Contact"
**Then** I am prompted to log in if not authenticated

### Story 2.5: Contact Rate Limiting

As a System,
I want to limit how many contacts a user can view per day,
So that I can prevent abuse.

**Acceptance Criteria:**

**Given** a user views contact info
**When** they exceed the daily limit (e.g., 10)
**Then** they are blocked from viewing more until the next day

### Story 2.6: Basic Map View

As a User,
I want to see listings on a map,
So that I can judge their location.

**Acceptance Criteria:**

**Given** listings have coordinates
**When** I switch to map view
**Then** pins are displayed for each listing

## Epic 3: Data Import & Normalization

Implement a system to bulk import listings and normalize descriptions.

### Story 3.1: Bulk CSV Importer Service

As an Admin,
I want to upload a CSV of listings,
So that I can populate the database quickly.

**Acceptance Criteria:**

**Given** a CSV file matching the schema
**When** I upload it via the Admin panel
**Then** the system parses the rows and creates pending listings

### Story 3.2: Listing Description Normalizer

As an Admin,
I want the system to standardize listing descriptions,
So that the tone is consistent.

**Acceptance Criteria:**

**Given** a raw description from the CSV
**When** the normalizer runs (using a simple LLM prompt)
**Then** a standardized summary is generated

### Story 3.3: Duplicate Detection (Basic)

As a System,
I want to flag potential duplicates during import,
So that I avoid redundant listings.

**Acceptance Criteria:**

**Given** a new import row
**When** the address matches an existing listing
**Then** it is flagged as a potential duplicate

### Story 3.4: Address Verification Service

As a System,
I want to verify addresses exist,
So that listings are accurate.

**Acceptance Criteria:**

**Given** an address string
**When** the service runs
**Then** it queries a standard map API to confirm existence

### Story 3.5: Data Review Dashboard

As an Admin,
I want to review imported data before publishing,
So that I can ensure quality.

**Acceptance Criteria:**

**Given** pending imported listings
**When** I open the dashboard
**Then** I can approve or reject them

### Story 3.6: Bot Access Protection

As a System,
I want to block automated scrapers,
So that the data remains exclusive.

**Acceptance Criteria:**

**Given** a known bot user agent
**When** it requests a page
**Then** access is denied

## Epic 4: Audit Logging

Implement comprehensive audit logging.

### Story 4.1: Price Change Logging

As a System,
I want to log every price change,
So that there is an audit trail.

**Acceptance Criteria:**

**Given** a price update
**When** it is saved
**Then** a record is written to the audit log with timestamp and user ID

### Story 4.2: Audit Log Viewer

As an Admin,
I want to view the history of changes for a listing,
So that I can track its evolution.

**Acceptance Criteria:**

**Given** a listing
**When** I view its logs
**Then** I see a chronological list of changes
