---
name: Master Gateway System
colors:
  surface: '#fcf8ff'
  surface-dim: '#dbd9e1'
  surface-bright: '#fcf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f2fb'
  surface-container: '#f0ecf5'
  surface-container-high: '#eae7f0'
  surface-container-highest: '#e4e1ea'
  on-surface: '#1b1b21'
  on-surface-variant: '#464652'
  inverse-surface: '#303036'
  inverse-on-surface: '#f2eff8'
  outline: '#777683'
  outline-variant: '#c7c5d4'
  surface-tint: '#4f54b4'
  primary: '#15157d'
  on-primary: '#ffffff'
  primary-container: '#2e3192'
  on-primary-container: '#9da1ff'
  inverse-primary: '#c0c1ff'
  secondary: '#505f76'
  on-secondary: '#ffffff'
  secondary-container: '#d0e1fb'
  on-secondary-container: '#54647a'
  tertiary: '#002f1e'
  on-tertiary: '#ffffff'
  tertiary-container: '#004830'
  on-tertiary-container: '#22c087'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e1e0ff'
  primary-fixed-dim: '#c0c1ff'
  on-primary-fixed: '#04006d'
  on-primary-fixed-variant: '#373a9b'
  secondary-fixed: '#d3e4fe'
  secondary-fixed-dim: '#b7c8e1'
  on-secondary-fixed: '#0b1c30'
  on-secondary-fixed-variant: '#38485d'
  tertiary-fixed: '#6ffbbe'
  tertiary-fixed-dim: '#4edea3'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#fcf8ff'
  on-background: '#1b1b21'
  surface-variant: '#e4e1ea'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  mono-label:
    fontFamily: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  sidebar-width: 280px
  sidebar-collapsed: 64px
  gutter: 24px
  margin-page: 32px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 24px
---

## Brand & Style
The design system is engineered for high-stakes enterprise environments managing microservices architecture. The personality is authoritative, precise, and impenetrable, evoking a sense of "Zero Trust" security while maintaining high operational efficiency.

The visual style is **Corporate Modern with a Focus on Information Density**. It prioritizes clarity over decoration, using a structured grid, purposeful whitespace, and a sophisticated color palette to guide users through complex technical workflows. The aesthetic avoids unnecessary flourishes, opting instead for a "glass-box" approach where system states are transparent, legible, and immediately actionable.

## Colors
This design system utilizes a structured palette to communicate hierarchy and system health:

- **Primary (Deep Indigo):** Used for primary actions, active navigation states, and branding. It represents the "Gateway" authority.
- **Secondary (Slate Gray):** Reserved for supporting text, icons, and inactive UI elements to reduce cognitive load.
- **Success (Emerald Green):** Indicates secure connections, active microservices, and validated configurations.
- **Alert (Rose Red):** Reserved strictly for critical errors, security breaches, or service downtime.
- **Neutral (Gray & White):** The background logic uses a layered approach. The application background is a cool off-white to reduce glare, while interactive surfaces (cards, modals) are pure white to create a clear "object" hierarchy.

## Typography
Inter is the foundation of this design system, chosen for its exceptional legibility in data-heavy interfaces. 

- **Hierarchy:** Use `headline-lg` sparingly for dashboard overviews. `headline-sm` is the default for card titles.
- **Data Display:** For microservice IDs, IP addresses, or terminal outputs, use the `mono-label` to ensure character distinction (e.g., 0 vs O).
- **Labels:** Use `label-md` for table headers and small metadata categories to create a clear distinction from interactive body text.
- **Mobile scaling:** On mobile devices, `headline-lg` should downscale to 24px to maintain readability within smaller viewports.

## Layout & Spacing
The layout follows a **Fixed-Fluid Hybrid** model. The sidebar remains fixed to the left, while the main content area utilizes a fluid 12-column grid.

- **Sidebar:** Features a nested hierarchy. Top-level categories use larger icons; sub-items are indented by 12px with a vertical connector line.
- **Grid:** Use a 24px gutter between columns. For data-dense tables, use an 8px "compact" vertical spacing.
- **Breakpoints:**
  - **Desktop (1440px+):** Full sidebar, 32px page margins.
  - **Tablet (768px - 1439px):** Sidebar collapses to icons only, 24px page margins.
  - **Mobile (<767px):** Sidebar moves to a hidden drawer, 16px page margins, cards stack vertically.

## Elevation & Depth
Depth is used functionally to indicate interactability and focus. The design system avoids heavy shadows in favor of **Tonal Layers and Precision Outlines**.

- **Level 0 (Background):** #F8FAFC. The lowest layer.
- **Level 1 (Cards/Sidebar):** White background with a 1px border (#E2E8F0). No shadow.
- **Level 2 (Hover/Active):** When a user interacts with a card, apply a subtle ambient shadow: `0px 4px 6px -1px rgba(0, 0, 0, 0.1), 0px 2px 4px -2px rgba(0, 0, 0, 0.1)`.
- **Level 3 (Modals/Popovers):** Standard 1px border with a more pronounced shadow to separate the element from the blurred background overlay.

## Shapes
The shape language is **Soft (0.25rem)**, conveying a balance between rigid technical precision and modern usability.

- **Small Elements:** Buttons, inputs, and tags use the base `rounded` (4px).
- **Large Elements:** Workspace cards and modal containers use `rounded-lg` (8px).
- **Status Indicators:** Use full pill-shaped rounding for status badges (e.g., "Online", "Error") to distinguish them from clickable buttons.

## Components
- **Buttons:** Primary buttons use Deep Indigo with white text. High-contrast hover states should darken the Indigo by 10%. Danger actions use Rose Red.
- **Inputs:** Use a 1px border (#CBD5E1). On focus, the border transitions to Deep Indigo with a 2px outer glow (Primary color at 10% opacity).
- **Cards:** Cards are the primary container for workspace selection. They must include a title, a "Service Status" badge in the top right, and a "Zero Trust" lock icon if the service requires elevated permissions.
- **Status Chips:** Small, semi-transparent backgrounds with high-contrast text. 
  - *Success:* Emerald Green 10% BG / Emerald Green 100% Text.
  - *Error:* Rose Red 10% BG / Rose Red 100% Text.
- **Data Tables:** Use zebra-striping (alternating #F8FAFC) for rows. The header must be "Sticky" and use the `label-md` typography.
- **Navigation:** Sidebar links use a 4px vertical "indicator bar" on the left edge when active, colored in Primary Indigo.