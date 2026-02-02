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
**TroRe** is a modern, verified rental housing platform for Vietnam. It acts as a definitive listing directory to connect tenants with landlords efficiently through a design philosophy of "Radical Clarity."
*   **Philosophy:** Clean, Verified, and Direct. We reject clutter in favor of high-density, structured information.

### Target Users
*   **The Seeker:** High-intent users looking for verified rental listings who prioritize speed and data accuracy over visual flair.
*   **The Admin:** Power users verifying data quality using high-throughput dashboards.
*   **The Landlord:** Users sharing their listings who need simple, shareable assets.

### Key Design Challenges
*   **Search Efficiency:** designing a unified search experience that gracefully handles both precise ID lookups (for known items) and broad attribute filters (for discovery).
*   **Data Density:** Presenting specifications (Amenities, Pricing, Location) clearly on small mobile screens without overwhelming the user.

### Design Opportunities
*   **Modern Palette:** Using a clean, accessible Blue/White palette (`#0066CC`) to establish professionalism and trust.
*   **Responsive Cards:** Developing a modular `ListingCard` component that adapts its layout from vertical (mobile) to horizontal (desktop) seamlessly.

## Core User Experience

### Defining Experience
The core experience centers on **"Clarity."** It presents verified information in a structured, consistent grid, minimizing cognitive load for users scanning dozens of listings.

### Platform Strategy
*   **Mobile-First SPA:** The interface is optimized primarily for touch interactions on 360px-420px viewports.
*   **Standard Navigation:** Usage of industry-standard patterns (Bottom Navigation for mobile, Sticky Top Bar for desktop) to reduce the learning curve.

### Interactions
*   **ID Lookup:** Pasting a valid UUID into the search bar triggers an immediate navigation event to the listing detail page ("Teleportation").
*   **Filtering:** Standard multi-select filters for Price, Area, and Location, implemented as accessible dropdowns or bottom sheets.

### Critical Success Moments
*   **Finding a Room:** Quickly narrowing down a dataset of 1000+ listings to 5 relevant options via intuitive filters.
*   **Trust:** Seeing the "Verified" badge and "Last Updated" timestamp on a listing card, reinforcing data freshness.

## Desired Emotional Response

### Primary Emotional Goals
**"Confidence."** Users should feel they are looking at real, verified data. The interface should feel stable, fast, and professional.

### Design Implications
*   **Clean Lines:** Professional aesthetic with ample whitespace and strict alignment.
*   **Blue/White:** A color scheme associated with established financial and data services.

## UX Pattern Analysis & Inspiration

### Inspiring Products Analysis
*   **Rightmove/Zillow:** Standard listing directory patterns that users are already familiar with. We will adopt their effective use of map-list toggles and photo carousels.

### Transferable UX Patterns
*   **Grid View:** Standard cards with the image at the top and critical details (Price, Address) at the bottom.
*   **Filter Bar:** A sticky filter bar that remains accessible as the user scrolls through results.

## Design System Foundation

### 1.1 Design System Choice
**Tailwind CSS** paired with **Radix UI** primitives for accessible, unstyled interactive components.

### Rationale for Selection
*   **Flexibility:** Utility-first classes allow for rapid iteration and custom layout construction without fighting framework opinions.
*   **Performance:** Tailwind's purge capability ensures a minimal CSS bundle size, critical for mobile performance.

### Customization Strategy
*   **Colors:** "Trust Blue" (`#0066CC`) as the primary brand color, supported by a neutral scale of Grays (`#1E293B` to `#F8FAFC`).
*   **Radius:** Standard `rounded-md` (6px) for a crisp, modern feel.

## 2. Core User Experience

### 2.1 Defining Experience
The **"Search Dashboard"** is the primary view, offering immediate access to filters and a keyword input.

### 2.2 User Mental Model
*   "I filter by price and area, then scroll through results until I see a photo I like."

## Visual Design Foundation

### Color System
**"Trust Blue"** - A palette designed for accessibility and professionalism.

| Token Name | Hex Value | Usage |
| :--- | :--- | :--- |
| `primary-500` | `#0066CC` | Main Buttons, Links, Active States |
| `primary-600` | `#0052A3` | Hover States for Primary |
| `surface-50` | `#F8FAFC` | Page Background |
| `surface-100` | `#FFFFFF` | Card Backgrounds |
| `text-900` | `#0F172A` | Headings, Primary Text |
| `text-500` | `#64748B` | Meta data, Labels |
| `state-error` | `#EF4444` | Validation Errors, Destructive Actions |
| `state-success` | `#22C55E` | Verification Badges, Success Toasts |

### Typography System
*   **Typeface:** **Inter** (Variable). Chosen for its excellent legibility on UI interfaces.
*   **Hierarchy:** Standard H1-H6 scale using Tailwind's `text-xl` through `text-sm` utilities.

### Spacing & Layout Foundation
*   **Grid:** 4px base unit. All padding and margins must be multiples of 4 (e.g., `p-4`, `m-8`).
*   **Cards:** Consistent 16px padding (`p-4`) and 1px borders (`border-slate-200`).

## Component Strategy

### Core Components Anatomy & States

**1. `SearchInput`**
*   **Anatomy:** Input field with left-aligned search icon and right-aligned "Clear" button.
*   **States:**
    *   `Idle`: Border `slate-300`, Placeholder "Search by ID or keyword".
    *   `Focus`: Ring `2px` `primary-500`, Border `primary-500`.
    *   `Typing`: Display "Clear" button (`x`).
    *   `Loading`: Right icon spins (Spinner).
    *   `Error`: Border `red-500`, red text explaining the error below.

**2. `ListingCard`**
*   **Anatomy:** Image Aspect Ratio 4:3, Title (Line Clamp 1), Price (Bold), Address (Gray), Specs Row (Icons).
*   **States:**
    *   `Idle`: White background, subtle shadow `shadow-sm`.
    *   `Hover`: Lift effect `translate-y-1`, shadow increase `shadow-md`.
    *   `Loading`: Skeleton pulse animation for image and text lines.

**3. `FilterGroup`**
*   **Anatomy:** Label, Trigger Button (Dropdown), Content Panel.
*   **States:**
    *   `Closed`: Trigger button gray.
    *   `Open`: Trigger button active blue, Panel visible.
    *   `Active Value`: Badge showing count of selected filters (e.g., "Price: <5m").

### Component Implementation Strategy
*   **React Components:** Functional components with strictly typed interfaces (`interface Props`).
*   **Tailwind:** Used exclusively for all styling. No external CSS files.

## User Journey Flows

### Journey 1: ID Lookup
**Goal:** Find a specific listing using a known UUID.
1.  User copies a UUID from Zalo.
2.  User pastes UUID into `SearchInput`.
3.  User presses "Enter".
4.  System validates UUID format.
5.  System redirects to `/listing/{uuid}`.

### Journey 2: Filtering
**Goal:** Find cheap rooms in District 1.
1.  User opens "Price" filter dropdown.
2.  User selects "Under 5 Million".
3.  User opens "Location" filter.
4.  User selects "District 1".
5.  List updates via client-side state (Zustand) to show filtered results.

## UX Consistency Patterns

### Button Hierarchy
*   **Primary:** Solid Blue (`bg-primary-500 text-white`). Used for "Contact", "Search", "Login".
*   **Secondary:** Outline Blue (`border-primary-500 text-primary-500`). Used for "Filter", "Cancel".
*   **Tertiary:** Text only (`text-slate-500 hover:text-slate-700`). Used for "Clear All", "Help".

### Feedback Patterns
*   **Toasts:** Bottom-right notifications for asynchronous actions ("Link Copied", "Saved").
*   **Empty States:** When 0 results are returned, display a friendly illustration and a "Reset Filters" button.

## Responsive Design & Accessibility

### Responsive Strategy
*   **Mobile (<768px):** Single column grid (`grid-cols-1`). Hamburger menu or Bottom Nav.
*   **Desktop (>768px):** Multi-column grid (`grid-cols-3` or `grid-cols-4`). Top Navigation Bar.

### Accessibility Strategy (Checklist)
*   **[A11Y-01] Contrast:** Ensure all text meets WCAG AA standards (4.5:1 ratio).
*   **[A11Y-02] Focus Indicators:** All interactive elements must have a visible focus ring (`focus:ring-2`).
*   **[A11Y-03] Screen Readers:** Images must have `alt` text. Icons must have `aria-hidden="true"`.
*   **[A11Y-04] Touch Targets:** All clickable areas must be at least 44x44px.