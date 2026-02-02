---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
lastStep: 14
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - docs/project-overview.md
  - docs/architecture-web.md
  - docs/component-inventory-web.md
  - packages/web/tailwind.config.js
---

# UX Design Specification TroRe

**Author:** Minh
**Date:** 2025-12-29

---

<!-- UX design content will be appended sequentially through collaborative workflow steps -->

## Executive Summary

### Project Vision
**TroRe** is a modern rental housing platform for Vietnam. It acts as a verified listing directory to connect tenants with landlords efficiently.
*   **Philosophy:** Clean, Verified, and Direct.

### Target Users
*   **The Seeker:** Users looking for verified rental listings.
*   **The Admin:** Power users verifying data quality.
*   **The Landlord:** Users sharing their listings.

### Key Design Challenges
*   **Search Efficiency:** designing a search experience that handles both ID lookups and filters.
*   **Data Density:** Presenting specifications clearly.

### Design Opportunities
*   **Modern Palette:** Using a clean Blue/White palette for professionalism.
*   **Responsive Cards:** Clear listing cards that work on mobile.

## Core User Experience

### Defining Experience
The core experience centers on **"Clarity."** It presents verified information in a structured grid.

### Platform Strategy
*   **Mobile-First SPA:** Optimized for mobile devices.
*   **Standard Navigation:** Bottom navigation for mobile, top bar for desktop.

### Interactions
*   **ID Lookup:** Pasting a UUID navigates to the listing.
*   **Filtering:** Standard multi-select filters for price and area.

### Critical Success Moments
*   **Finding a Room:** Quickly narrowing down results via filters.
*   **Trust:** Seeing the "Verified" badge on a listing.

## Desired Emotional Response

### Primary Emotional Goals
**"Confidence."** Users should feel they are looking at real, verified data.

### Design Implications
*   **Clean Lines:** Professional aesthetic.
*   **Blue/White:** Trustworthy color scheme.

## UX Pattern Analysis & Inspiration

### Inspiring Products Analysis
*   **Rightmove/Zillow:** Standard listing directory patterns.

### Transferable UX Patterns
*   **Grid View:** Standard cards with image and price.
*   **Filter Bar:** Sticky filter bar on top/bottom.

## Design System Foundation

### 1.1 Design System Choice
**Tailwind CSS** with **Radix UI** or **Headless UI** for accessible components.

### Rationale for Selection
*   **Flexibility:** Utility-first classes for custom layouts.
*   **Performance:** Lightweight bundle size.

### Customization Strategy
*   **Colors:** Brand Blue (`#0066CC`) and Neutral Grays.
*   **Radius:** Standard `rounded-md` (6px).

## 2. Core User Experience

### 2.1 Defining Experience
The **"Search Dashboard"** is the primary view, offering filters and a keyword input.

### 2.2 User Mental Model
*   "I filter by price and area, then scroll through results."

## Visual Design Foundation

### Color System
**"Trust Blue"**
*   **Primary:** #0066CC
*   **Background:** #F8FAFC
*   **Surface:** #FFFFFF

### Typography System
*   **Typeface:** **Inter** or **Roboto**.
*   **Hierarchy:** Standard H1-H6.

### Spacing & Layout Foundation
*   **Grid:** 4px base unit.
*   **Cards:** Consistent padding and borders.

## Component Strategy

### Core Components
*   **`SearchInput`:** Standard text input with icon.
*   **`ListingCard`:** Image top, details bottom.
*   **`FilterGroup`:** Dropdowns or modal for filters.

### Component Implementation Strategy
*   **React Components:** Functional components with typed props.
*   **Tailwind:** Used for all styling.

## User Journey Flows

### Journey 1: ID Lookup
**Goal:** Find a specific listing.
1.  Paste UUID.
2.  Hit Enter.
3.  Redirect to Detail Page.

### Journey 2: Filtering
**Goal:** Find cheap rooms.
1.  Open Filters.
2.  Set Max Price.
3.  View Results.

## UX Consistency Patterns

### Button Hierarchy
*   **Primary:** Solid Blue.
*   **Secondary:** Outline Blue.
*   **Tertiary:** Text only.

### Feedback Patterns
*   **Toasts:** For success/error messages.
*   **Empty States:** "No results found" with reset button.

## Responsive Design & Accessibility

### Responsive Strategy
*   **Mobile:** Single column.
*   **Desktop:** Multi-column grid.

### Accessibility Strategy
*   **WCAG 2.1 AA:** Ensure color contrast and keyboard navigation.
*   **Touch Targets:** 44px min height.
