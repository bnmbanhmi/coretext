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
**Version:** 2.0 (High-Volume Specification)

## Executive Summary

**TroRe** is a modern, enterprise-grade rental housing platform for Vietnam, strategically designed to connect high-intent seekers with verified landlords through a clean, transparent listing interface. The platform utilizes a **Hybrid Multi-Cloud Strategy**: **Google Cloud Platform (GCP)** serves as the high-throughput "Importer" for bulk data acquisition, normalization, and cleansing, while **Supabase and Vercel** provide the high-velocity "App Tier" for secure data storage, human-in-the-loop validation, and the responsive public user experience.

### The Hybrid Data Importer (GCP Tier)

- **Bulk Import:** A stateless, scalable Python-based pipeline executes asynchronous processing of large CSV files to capture and consolidate bulk leads from external legacy sources and partner feeds.
- **AI-Driven Normalization:** Gemini 2.5 Flash Lite serves as the intelligence layer, normalizing description text, correcting grammatical errors, and extracting structured attributes to ensure consistent listing quality across the platform.
- **Standard Identification:** The system assigns standard, version-4 Universally Unique Identifiers (UUIDs) to all listings to ensure unique, collision-free identification across the distributed architecture.

### The App & Identity Tier (Vercel + Supabase Tier)

- **Audit Logging:** A robust PostgreSQL storage strategy using **Immutable Audit Logs** to preserve a legally defensible history of price changes, status updates, and property modifications.
- **Direct Access UX:** A frictionless, "Google-like" search bar that accepts UUIDs for direct navigation, combined with a comprehensive **Review Dashboard** for final human-in-the-loop verification of imported data.
- **Secure Interaction:** Integrated secure contact forms and smart gating (login walls/rate limiting) to protect sensitive owner data integrity while facilitating seamless, verified user-to-owner connections.

## Project Classification

**Technical Type:** Hybrid Multi-Cloud SPA (React 19 + FastAPI + GCP Importer)
**Domain:** Real Estate (PropTech) / Data Engineering
**Complexity:** **High** (Event-driven pipeline, UUID Logic, Audit History)
**Project Context:** Brownfield - Consolidating legacy data logic into a GCP Importer while implementing the modern vision on Supabase/Vercel.

## Success Criteria

### User Success

- **Single-Entry Simplicity:** Users rely on a single, omnipotent smart search bar for all navigation needs, experiencing an intuitive flow that helps them build complex queries or jump directly to known listings.
- **Guided Construction:** Users find matching properties significantly faster because the search bar actively suggests "UI tokens" (chips) to build logical queries as they type.
- **Instant Result:** Direct UUID entry results in a <300ms "teleport" directly to the property page, bypassing the friction of traditional search results grids.
- **Trust:** Users walk away feeling confident that the data is verified, up-to-date, and accurate, reducing the "trust tax" of the current market.

### Business Success

- **Development Velocity:** Achieving operational efficiency and rapid feature deployment through a lightweight LLM bridge (Gemini Flash) for automated data normalization.
- **Operational Mastery:** The Admin processes 50+ listings daily in under 30 minutes of review time, ensuring the public feed remains the "Cleanest Source of Truth" in the market.
- **Search Satisfaction:** High "Success-to-Search" ratio—users find a relevant listing within their first few queries, minimizing bounce rates.

### Technical Success

- **Dispatcher Logic:** 100% reliable routing between UUID regex jumps, UI token building, and keyword search intent parsing within the search bar.
- **Normalization Accuracy:** >90% accuracy in standardizing natural language descriptions via the LLM bridge, minimizing the need for manual corrections.
- **Importer Resilience:** The import pipeline maintains high throughput with robust error handling, ensuring no data loss during CSV ingestion.

## Product Scope

### MVP - Minimum Viable Product

- **Smart Search Bar:** Input handling for (1) UUID Lookup, (2) Manual Filters, and (3) Keyword Search.
- **Advanced Filtering:** A specific interface that helps users apply multiple criteria (Price, Area, Location).
- **GCP Data Factory:** Deployed stateless importer and Gemini normalizer for core data processing.
- **Identity Storage:** Supabase PostgreSQL with UUID generation and comprehensive Audit Logging.
- **Review Dashboard:** High-throughput interface for human-in-the-loop verification of imported data.
- **Discovery UI:** Mobile-first listing grid and detail pages with responsive design.

### Growth Features (Post-MVP)

- **Bulk CSV Upload:** Admin capability to upload listings in bulk from partner dashboards.
- **Smart Gating:** Login walls for contact info and rate-limiting protection to prevent scraping.
- **Owner Claiming:** Workflow for landlords to verify their own portfolios and claim ownership of imported listings.

## User Journeys

**Journey 1: The Seeker (Alex - The Busy Student)**
Alex is a busy university student looking for a room near campus. He receives a specific listing ID from a friend. He pastes the UUID (e.g., `550e8400-e29b...`) into the main search bar. The system recognizes the format immediately and "teleports" him directly to the detail page, bypassing the search grid. He reviews the verified specs, checks the price history log to ensure stability, and clicks "Contact". The system prompts him to log in to view the landlord's phone number, ensuring security.

**Journey 2: The Admin (Sarah - The Meticulous Verifier)**
Sarah manages data quality for the platform. She receives a batch of raw listings in a CSV file. She uploads the file to the Admin Dashboard. The GCP pipeline processes the file asynchronously, assigning UUIDs and normalizing the messy descriptions using Gemini AI. Sarah opens the **Review Dashboard** and sees a queue of "Pending" items. She compares the AI-normalized text against the original, makes a quick edit to fix a typo, and hits **"Approve"**. The listing is instantly published to the live site.

**Journey 3: The Landlord (Mr. Tan - The Traditional Owner)**
Mr. Tan wants to share his listing on social media but wants a professional presentation. He searches for his property on TroRe, copies the direct URL containing the UUID, and posts it on his Zalo status. Potential tenants click the link and are taken to a clean, professional listing page that showcases his property's best features, filtered from the noise of social media.

## Functional Requirements

### Property Discovery & Search
- **FR1:** Seekers can navigate directly to a specific property using a unique UUID. The system must validate the UUID format (v4) and execute a direct database lookup, redirecting the user to the detail page if a match is found.
- **FR2:** Seekers can filter property results by multiple criteria. The interface must support simultaneous filtering by Price Range (Min/Max), Area Range (Min/Max), and Location (District/Ward Selection).
- **FR3:** Seekers can perform standard keyword searches across property descriptions. The search engine must utilize full-text search capabilities to find matches within the title and description fields.
- **FR4:** Seekers can view a map representation of property locations. The system must render a visual map interface with interactive pins representing the geolocation of available listings.

### Interaction & Communication
- **FR9:** Seekers can initiate contact with the Platform Admin regarding a specific property. The system must provide a secure contact form or direct messaging link (e.g., Zalo) to facilitate communication.
- **FR11:** Users can view property contact information only after passing a "Login Wall". Unauthenticated users must be restricted from viewing sensitive phone numbers or email addresses until they successfully sign in.

### Data Factory & Importer (GCP)
- **FR13:** The System can bulk ingest listings from CSV sources. The importer service must parse CSV files, validate schema compliance, and process rows asynchronously to populate the database.
- **FR14:** The System can normalize unstructured text into structured property data. The AI service must process raw description text to extract key attributes and standardize the tone and formatting.
- **FR16:** The System can automatically assign unique UUIDs for new properties. Every new listing must be generated with a cryptographically secure Version 4 UUID as its primary key.
- **FR18:** The System can summarize descriptions using AI. The LLM must generate a concise, professional summary of the property features suitable for display in card previews.

### Quality Control & Administration
- **FR19:** Admins can review imported data in a dashboard. The interface must present "Pending" listings in a queue, allowing for side-by-side comparison of raw vs. processed data.
- **FR20:** Admins can manually override and edit any attribute of a listing before approval. The system must support full CRUD operations on pending listings to ensure data accuracy.
- **FR21:** Admins can approve or reject pending listings. Approved listings must be updated to "Available" status; rejected listings must be archived or deleted.
- **FR27:** Admins can manually input new listings via the admin interface. The system must provide a comprehensive form for entering all listing details for single-entry creation.

### Security & Integrity
- **FR24:** The System can block known bot user agents. The middleware must identify and reject requests from known scraper user-agents to protect platform data.
- **FR25:** The System can rate-limit the viewing of sensitive contact information per user. To prevent abuse, the system must enforce a daily limit on the number of contact details a single user can reveal.
- **FR26:** The System can enforce a "Login Wall" for accessing owner/admin contact details. Access to sensitive fields must be strictly gated behind an active authentication session.

## Non-Functional Requirements

### Performance
- **ID Resolution:** Entering a UUID in the search bar must resolve to the property page in **< 300ms** (network excluding) to ensure a "teleportation" feel.
- **First Contentful Paint (FCP):** The public landing page must load in **< 1.5s** on a standard 4G connection to maintain user engagement.

### Security
- **Data Protection:** Owner contact information must be protected behind a rate-limiting gate (e.g., max 5 views/day) to prevent bulk scraping.
- **Admin Security:** Admin access must be secured via robust authentication (Supabase Auth) and Role-Based Access Control (RBAC).

### Scalability
- **Horizontal Processing:** The GCP pipeline must support scaling to handle large CSV files (up to 100MB) without performance degradation.
- **Storage Strategy:** Supabase storage must handle up to **100,000 active listings** with comprehensive audit logs without query performance impact.

### Reliability
- **Transactional Consistency:** 100% of listing creations must be **Atomic** (Listing + Audit Log) to prevent partial data states or orphaned records.

## Glossary of Terms

| Term | Definition |
| :--- | :--- |
| **UUID** | Universally Unique Identifier (Version 4). A 128-bit label used for information in computer systems. We use this as the Primary Key for all entities. |
| **JWT** | JSON Web Token. An open standard (RFC 7519) that defines a compact and self-contained way for securely transmitting information between parties as a JSON object. |
| **RLS** | Row Level Security. A feature of PostgreSQL that allows you to define policies to restrict access to rows in a table based on the user executing the query. |
| **HMR** | Hot Module Replacement. A feature in Vite that exchanges, adds, or removes modules while an application is running, without a full reload. |
| **SPA** | Single Page Application. A web application or website that interacts with the user by dynamically rewriting the current web page with new data from the web server. |
| **Pydantic** | Data validation and settings management using Python type hints. We use Version 2 for performance. |
| **Edge Function** | Serverless functions that run at the network edge (Vercel), closer to the user, for lower latency. |
| **Supabase** | An open source Firebase alternative. Provides a hosted Postgres database, Authentication, instant APIs, Edge Functions, and Realtime subscriptions. |

