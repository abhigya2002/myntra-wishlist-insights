---
name: Fashion Retail Intelligence
colors:
  surface: '#fbf8ff'
  surface-dim: '#d6d8f2'
  surface-bright: '#fbf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f2ff'
  surface-container: '#ececff'
  surface-container-high: '#e4e7ff'
  surface-container-highest: '#dee1fa'
  on-surface: '#161b2d'
  on-surface-variant: '#5b4042'
  inverse-surface: '#2b2f43'
  inverse-on-surface: '#efefff'
  outline: '#8f6f72'
  outline-variant: '#e4bdc0'
  surface-tint: '#bd0043'
  primary: '#b90041'
  on-primary: '#ffffff'
  primary-container: '#df2357'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb2ba'
  secondary: '#a73a00'
  on-secondary: '#ffffff'
  secondary-container: '#ff7438'
  on-secondary-container: '#621f00'
  tertiary: '#715d00'
  on-tertiary: '#ffffff'
  tertiary-container: '#cba800'
  on-tertiary-container: '#4c3e00'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffd9dc'
  primary-fixed-dim: '#ffb2ba'
  on-primary-fixed: '#400011'
  on-primary-fixed-variant: '#910031'
  secondary-fixed: '#ffdbce'
  secondary-fixed-dim: '#ffb599'
  on-secondary-fixed: '#370e00'
  on-secondary-fixed-variant: '#7f2b00'
  tertiary-fixed: '#ffe177'
  tertiary-fixed-dim: '#ebc300'
  on-tertiary-fixed: '#231b00'
  on-tertiary-fixed-variant: '#554500'
  background: '#fbf8ff'
  on-background: '#161b2d'
  surface-variant: '#dee1fa'
typography:
  display-lg:
    fontFamily: montserrat
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: montserrat
    fontSize: 30px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: montserrat
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: montserrat
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.005em
  headline-sm:
    fontFamily: montserrat
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  body-md:
    fontFamily: inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  body-sm:
    fontFamily: inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-caps:
    fontFamily: montserrat
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.1em
  label-md:
    fontFamily: montserrat
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
  label-sm:
    fontFamily: montserrat
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  space-2xs: 0.25rem
  space-xs: 0.5rem
  space-sm: 0.75rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
  space-3xl: 4rem
  layout-margin-desktop: 2.5rem
  layout-margin-tablet: 1.5rem
  layout-margin-mobile: 1rem
  gutter-desktop: 1.5rem
  gutter-mobile: 0.75rem
---

## Brand & Style

This design system powers an internal product-research Retrieval-Augmented Generation (RAG) assistant tailored for senior fashion merchandisers, buyers, and retail directors. It translates high-velocity e-commerce consumer energy into an authoritative, executive-grade analytical tool.

### Design Movement & Aesthetic
The visual style fuses **Editorial Retail Modernism** with **High-Precision Enterprise SaaS**. It completely rejects generic generative AI tropes (such as hazy indigo/purple glows, starry sparkles, and nebulous cosmic gradients) in favor of the razor-sharp, energetic lifestyle vernacular of top-tier fashion commerce. 

- **Crisp Editorial Discipline:** Generous white space, architectural structural lines, and decisive typography that presents complex cross-category wishlist telemetry with immediate executive clarity.
- **Dynamic Fashion Warmth:** High-vibrancy sunset gradients (hot pink into sharp orange) punctuate actionable insights, cohort sentiment shifts, and inventory predictions without compromising enterprise ergonomics.
- **Analytical Authority:** Deep charcoal typography and structured data density keep outputs grounded, serious, and decision-ready.

## Colors

The palette directly anchors to high-energy fashion e-commerce while serving the strict functional hierarchy demanded by senior leadership dashboards.

### Core Color Roles
- **Primary (`#FF3E6C`, Deep Tone `#E31C79`):** Hot Magenta/Pink. Used for active navigation anchors, primary system calls-to-action, key analytical tags, and leading brand accents.
- **Secondary (`#F26A2E`, Light Tone `#FF905A`):** Warm Bright Orange. Deployed as a secondary interactive anchor, trend-acceleration indicators, and in synergy with the primary color to form the signature brand gradient (`linear-gradient(90deg, #FF3E6C 0%, #F26A2E 100%)`).
- **Tertiary (`#FFD400`):** Sunny Warm Yellow. Exclusively reserved for micro-accents: confidence score badges, wishlist velocity pings, and high-priority insight stars. It is never used for broad surface fills or critical text.
- **Neutral Core (`#282C3F`):** Deep Charcoal Navy. Grounds the UI with editorial weight. Applied to high-emphasis text, structural icons, and authoritative executive action buttons.
- **Neutral Meta (`#696B79`, Muted Meta `#94969F`):** Calibrated for secondary metrics, source citations, timestamps, and subtle field guidance.

### Surfaces & Structural Tones
- **Base Canvas:** `#F5F5F6` with card-level canvas layering at `#FAFAFA`.
- **Card Surface:** Pure crisp `#FFFFFF`.
- **Divider & Border Tones:** `#EAEAEA` for subtle dividers, `#E0E0E0` for interactive containment and component bounds.

## Typography

The type system pairs the architectural punch of **Montserrat** for display, headlines, and uppercase editorial tracking with the systematic legibility of **Inter** for high-volume RAG synthesized responses and tabular intelligence.

### Structural Typographic Rules
- **Editorial Tracking:** Navigation elements, section headers, meta tabs, and table category pills must use `label-caps` (`letter-spacing: 0.1em`, uppercase). This injects fashion-magazine structure into an analytical dashboard.
- **Narrative Syntheses:** Assistant output streams utilize `body-lg` (16px/26px) in deep neutral `#282C3F` to maximize scannability during lengthy product telemetry briefings.
- **Source Attributions & Microdata:** Subordinate telemetry, RAG citations, SKUs, and confidence indices are locked to `body-sm` using muted `#696B79` or `#94969F`.

## Layout & Spacing

The layout model is driven by an 8pt architectural rhythm tailored for data density balanced against intentional editorial breathing room.

### Layout Philosophy
- **Three-Tier Workspace:** The interface operates across three functional vertical divisions:
  1. *Global Navigation & Category Filters:* Compact, 64px collapsed or 240px expanded navigation rail.
  2. *Research Thread & Synthesized RAG Stream:* Primary conversational canvas, constrained to a maximum reading width of 860px for conversational outputs to maintain optimal optical tracking.
  3. *Telemetry & Visual SKU Inspector:* Side-docked 400px panel for real-time SKU wishlist graphs, trend distributions, and source document validation.
- **Grid Structure:** A 12-column responsive fluid grid with 24px desktop gutters and 40px external page margins. Breakpoints scale across Mobile (0–599px), Tablet (600–1023px), Desktop (1024–1439px), and Ultra-wide Research Displays (1440px+). On tablet and mobile viewports, the third telemetry panel shifts to an off-canvas bottom drawer.

## Elevation & Depth

Visual hierarchy relies on crisp surface separation rather than heavy skeuomorphic shadows or dark-mode luminescence. 

### Elevation Tiers
- **Tier 0 (Base Canvas):** `#F5F5F6`. Flat, non-elevated ground plane.
- **Tier 1 (Cards & Query Containers):** Pure `#FFFFFF` surface with a crisp structural border (`1px solid #EAEAEA`) supported by a diffused signature shadow:
  `box-shadow: 0 2px 8px rgba(40, 44, 63, 0.06);`
- **Tier 2 (Floating Action Dock & Query Input):** Crisp `#FFFFFF` surface accompanied by a dual-stage shadow for floating interaction:
  `box-shadow: 0 4px 16px rgba(40, 44, 63, 0.08), 0 1px 2px rgba(40, 44, 63, 0.04);`
- **Tier 3 (Modals, Overlays & Category Select Flyouts):** High-focus elevated surfaces featuring:
  `box-shadow: 0 12px 32px rgba(40, 44, 63, 0.12);`

### Signature Accent Elevation
Key insight cards and executive RAG takeaway blocks incorporate an asymmetric 4px left-border highlight utilizing the signature brand gradient (`linear-gradient(180deg, #FF3E6C 0%, #F26A2E 100%)`), giving the card structural prominence without increasing blur depth.

## Shapes

The interface blends high-performance architectural precision with tactile pill components:

- **Buttons & Interactive Tags:** Formed using full-pill geometries (border-radius: `9999px`), imparting an approachable, consumer-app touchstone consistent with mobile fashion browsing.
- **Cards, Panels & Data Containers:** Defined with soft, structured bounds (`0.75rem` / `12px`), maintaining crisp alignment for multidimensional data matrices, bar charts, and conversational summaries.
- **Input Fields:** Styled as elongated soft-pills (`1.5rem` / `24px` to `9999px`) to emphasize conversational fluidness.

## Components

### Buttons
- **Primary Pill (Brand Gradient):** Background `linear-gradient(90deg, #FF3E6C 0%, #F26A2E 100%)`, text `#FFFFFF`, font `label-md`. Subtle hover state increases gradient brightness (+5%) with an ambient drop: `box-shadow: 0 4px 12px rgba(255, 62, 108, 0.35)`.
- **Executive Primary (Navy Pill):** Background `#282C3F`, text `#FFFFFF`, hover `#2D2D3A`. Used for corporate functions (Export Deck, Authorize Merchandising Action, Filter Lock).
- **Secondary Pill:** Background `#FFFFFF`, border `1px solid #E0E0E0`, text `#282C3F`. On hover: border `#282C3F` with background `#FAFAFA`.

### Input Fields & Query Console
- **Chat/Prompt Console:** Floating pill or soft rounded container (`rounded-2xl`), `#FFFFFF` surface, border `1px solid #E0E0E0`. On active focus: border transitions to `1px solid #FF3E6C` with zero blurry blue ring; instead uses a crisp `0 0 0 1px #FF3E6C`.
- **Integrated Action Icons:** Deep charcoal `#282C3F` icons within the input dock, transitioning to `#FF3E6C` when active.

### Chips & Filters
- **Category Filter Chips:** Full-pill geometry (`rounded-full`), height `32px`, typography `label-caps`.
- **Default State:** Background `#FFFFFF`, border `1px solid #E0E0E0`, text `#696B79`.
- **Active State:** Background `#282C3F`, border `1px solid #282C3F`, text `#FFFFFF`.
- **Trend Highlight Chip:** Background `#FFF0F3`, border `1px solid #FFD0DB`, text `#FF3E6C`.

### Cards & Analytical Panels
- **Insight Card:** Background `#FFFFFF`, border `1px solid #EAEAEA`, subtle shadow (`0 2px 8px rgba(40, 44, 63, 0.06)`), inner padding `20px`.
- **Strategic Insight Highlight Card:** Equipped with a `4px` left-edge gradient border (`linear-gradient(180deg, #FF3E6C 0%, #F26A2E 100%)`).
- **Telemetry Card Header:** Uppercase tracking (`label-caps`), text `#94969F`, border-bottom `1px solid #F5F5F6`.

### Lists & Citations
- **RAG Citation Source Tags:** Compact inline pills (`height: 20px`, `label-sm`), background `#F5F5F6`, text `#282C3F`, border `1px solid #EAEAEA`. Hover state swaps border to `#F26A2E` with text `#F26A2E`.
- **Key Takeaway Lists:** Custom check/bullet markers utilizing the sunny micro-accent `#FFD400` or `#FF3E6C` rather than standard unstyled bullets.

### Checkboxes & Radios
- **Checkbox:** 18px square with `rounded-sm` (4px). Active fill `#FF3E6C` with white checkmark. Unchecked: 1.5px border in `#696B79`.
- **Radio Button:** 18px circle. Active state features a 5px solid `#FF3E6C` inner dot inside a white ring encased in an `#FF3E6C` outer border.