---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
inputDocuments:
  - docs/api-contracts.md
  - docs/architecture-backend.md
  - docs/architecture-web.md
  - docs/component-inventory-web.md
  - docs/data-models.md
  - docs/deployment-guide.md
  - docs/development-guide.md
  - docs/index.md
  - docs/integration-architecture.md
  - docs/project-overview.md
  - docs/source-tree-analysis.md
workflowType: 'prd'
lastStep: 11
---

# Product Requirements Document - TroRe

**Author:** Minh
**Date:** 2025-12-29

## Executive Summary

**TroRe** is a modern rental housing platform for Vietnam, designed to connect seekers with landlords through a clean, verified listing interface. The platform utilizes a **Hybrid Multi-Cloud Strategy**: **Google Cloud Platform (GCP)** serves as the "Importer" for bulk data acquisition and normalization, while **Supabase and Vercel** provide the high-velocity "App Tier" for data storage, human validation, and the public user experience.

### The Hybrid Data Importer (GCP Tier)

- **Bulk Import:** A stateless, Python-based pipeline executes processing of CSV files to capture bulk leads from external sources.
- **AI-Driven Normalization:** Gemini 2.5 Flash Lite normalizes description text and extracts structured attributes to ensure consistent listing quality.
- **Standard Identification:** System assigns standard UUIDs to all listings to ensure unique identification across the platform.

### The App & Identity Tier (Vercel + Supabase Tier)

- **Audit Logging:** A PostgreSQL storage strategy using **Audit Logs** to preserve price change history and property updates.
- **Direct Access UX:** A frictionless search bar that accepts UUIDs for direct navigation, combined with a **Review Dashboard** for final human-in-the-loop validation.
- **Secure Interaction:** Integrated contact forms and smart gating (login walls/rate limiting) to protect data integrity while facilitating user-to-owner connections.

## Project Classification

**Technical Type:** Hybrid Multi-Cloud SPA (React 19 + FastAPI + GCP Importer)
**Domain:** Real Estate (PropTech) / Data Engineering
**Complexity:** **High** (Event-driven pipeline, UUID Logic, Audit History)
**Project Context:** Brownfield - Consolidating legacy data logic into a GCP Importer while implementing the modern vision on Supabase/Vercel.

## Success Criteria

### User Success

- **Single-Entry Simplicity:** Users rely on a single smart search bar for all needs, experiencing an intuitive flow that helps them build queries or jump to listings.
- **Guided Construction:** Users find matching properties faster because the search bar provides clear options.
- **Instant Result:** Direct UUID entry results in immediate navigation to the property page.
- **Trust:** Users walk away feeling confident that the data is verified and accurate.

### Business Success

- **Development Velocity:** Achieving operational efficiency through a lightweight LLM bridge (Gemini Flash) for data normalization.
- **Operational Mastery:** The Admin processes 50+ listings daily in under 30 minutes of review time, ensuring the public feed remains clean.
- **Search Satisfaction:** High "Success-to-Search" ratio—users find a relevant listing within their first few queries.

### Technical Success

- **Dispatcher Logic:** Reliable routing between UUID jumps and keyword search.
- **Normalization Accuracy:** >90% accuracy in standardizing natural language descriptions via the LLM bridge.
- **Importer Resilience:** The import pipeline maintains high throughput with robust error handling.

## Product Scope

### MVP - Minimum Viable Product

- **Smart Search Bar:** Input handling for (1) UUID Lookup, (2) Manual Filters, and (3) Keyword Search.
- **Advanced Filtering:** A specific interface that helps users apply multiple criteria.
- **GCP Data Factory:** Deployed stateless importer and Gemini normalizer for core data.
- **Identity Storage:** Supabase PostgreSQL with UUID generation and Audit Logging.
- **Review Dashboard:** Interface for human-in-the-loop verification.
- **Discovery UI:** Mobile-first listing grid and detail pages.

### Growth Features (Post-MVP)

- **Bulk CSV Upload:** Admin capability to upload listings in bulk.
- **Smart Gating:** Login walls for contact info and rate-limiting protection.
- **Owner Claiming:** Workflow for landlords to verify their own portfolios.

## User Journeys

**Journey 1: The Seeker**
The seeker is looking for a room. They paste a UUID they received from a friend into the search bar. The system recognizes the format and navigates them directly to the detail page. They see verified specs and a price history log. They click "Contact" and are prompted to log in to view the phone number.

**Journey 2: The Admin**
The admin manages quality. They upload a CSV of new listings. The GCP pipeline processes the file, assigning UUIDs and normalizing descriptions. The admin opens the **Review Dashboard**. They see a list of pending items. They review the normalized text against the original, make quick edits, and hit **"Approve"**. The listing goes live.

**Journey 3: The Landlord**
The landlord wants to share their listing. They copy the direct URL with the UUID and post it on social media. Potential tenants click the link and see the professional listing page.

## Functional Requirements

### Property Discovery & Search
- **FR1:** Seekers can navigate directly to a specific property using a unique UUID.
- **FR2:** Seekers can filter property results by multiple criteria.
- **FR3:** Seekers can perform standard keyword searches across property descriptions.
- **FR4:** Seekers can view a map representation of property locations.

### Interaction & Communication
- **FR9:** Seekers can initiate contact with the Platform Admin regarding a specific property.
- **FR11:** Users can view property contact information only after passing a "Login Wall".

### Data Factory & Importer (GCP)
- **FR13:** The System can bulk ingest listings from CSV sources.
- **FR14:** The System can normalize unstructured text into structured property data.
- **FR16:** The System can automatically assign unique UUIDs for new properties.
- **FR18:** The System can summarize descriptions using AI.

### Quality Control & Administration
- **FR19:** Admins can review imported data in a dashboard.
- **FR20:** Admins can manually override and edit any attribute of a listing before approval.
- **FR21:** Admins can approve or reject pending listings.
- **FR27:** Admins can manually input new listings via the admin interface.

### Security & Integrity
- **FR24:** The System can block known bot user agents.
- **FR25:** The System can rate-limit the viewing of sensitive contact information per user.
- **FR26:** The System can enforce a "Login Wall" for accessing owner/admin contact details.

## Non-Functional Requirements

### Performance
- **ID Resolution:** Entering a UUID in the search bar must resolve to the property page in **< 300ms**.
- **First Contentful Paint (FCP):** The public landing page must load in **< 1.5s**.

### Security
- **Data Protection:** Owner contact information must be protected behind a rate-limiting gate.
- **Admin Security:** Admin access must be secured via authentication.

### Scalability
- **Horizontal Processing:** The GCP pipeline must support scaling to handle large CSV files.
- **Storage Strategy:** Supabase storage must handle up to **100,000 active listings** with audit logs.

### Reliability
- **Transactional Consistency:** 100% of listing creations must be **Atomic** to prevent partial data states.

