# Senior Navigator Skeleton — Redline v2025.10.1

This document supersedes any prior “Dashboard” guidance. It codifies the current architecture so hubs, tiles, and cross-cutting services stay consistent across the app.

---

## 0. Executive Summary

- **Delete** the legacy **Dashboard** concept. Layout shells now belong to `BaseHub`.
- **Add** two cross-cutting components:
  - **Hub Guide** – state-aware CTA bar rendered inside the hub header.
  - **Additional Services** – ordered, hub-scoped partner tile rail.
- **Promote** tiles to first-class primitives: `ProductTileHub` (large) and `ModuleTileCompact` (compact). Both accept `order`, `visible`, and `locked`.
- **Consolidate CSS**: a single `.dashboard-grid` under `.dashboard-shell`. Target Streamlit wrappers as grid children; remove invalid/duplicate rules.
- **Trusted Partners**: maintain a single implementation (`hubs/trusted_partners.py`). Remove `_new` variants.

---

## 1. Hub Layout Ownership

- `BaseHub` is the only component that opens layout containers. It renders:
  - `.dashboard-shell` outer wrapper
  - `.dashboard-head` header region (title, subtitle, chips, Hub Guide)
  - `.dashboard-grid` for product/module tiles
  - Optional Additional Services footer section
- Individual hub files (e.g., `concierge.py`, `waiting_room.py`) **must not** open shell/head/grid containers. Hubs only compose data and call `render_dashboard`.
- **Removed:** any legacy “Dashboard” layer or helper that previously emitted layout shells.

---

## 2. Cross-Cutting Components

### 2.1 Hub Guide

- **Purpose:** contextual, state-aware callout that presents next-best actions.
- **Contract:**

  ```python
  GuideBlock = {
      "eyebrow": str,
      "title": str,
      "body": str,
      "actions": [
          {"label": str, "route": str, "variant": "primary|ghost|neutral"}
      ],
      "variant": "brand|success|warn|teal|violet"  # optional
  }

  compute_hub_guide(hub: str) -> Optional[GuideBlock]
  render_hub_guide(block: GuideBlock) -> None
  ```

- **Behavior:** rendered inside `.dashboard-head` beneath title/subtitle/chips; never opens layout containers within hub files.

### 2.2 Additional Services

- **Purpose:** ordered registry of partner/service cards, scoped per hub.
- **Tile schema:**

  ```python
  Tile = {
      "key": str,
      "title": str,
      "subtitle": str,     # {name} placeholder supported
      "cta": str,
      "go": str,
      "order": int,        # e.g., 10, 20, 30
      "hubs": list[str],   # ["concierge", "waiting_room"]
      "visible_when": list[Rule],  # equals/includes/exists/min_progress/role_in
  }

  get_additional_services(hub: str, limit: Optional[int]) -> list[Tile]
  ```

- Filters by `hubs` and rule engine, sorts by `order` then `title`.

---

## 3. Product Tiles

### 3.1 Primitives

- **`ProductTileHub`** – large, gradient-capable tile used for top-level products in hubs (Guided Care Plan, Cost Planner, PFMA, FAQs & Answers, etc.).
- **`ModuleTileCompact`** – compact tile for sub-modules within products (Cost Planner modules, GCP sub-steps, etc.).

### 3.2 Canonical Attributes

Shared attributes (unless noted):

```python
# Shared
key: str
title: str
desc: str | None
blurb: str | None
badge_text: str | None
meta_lines: list[str] | None
primary_label: str
primary_go: str
secondary_label: str | None
secondary_go: str | None
progress: float | int  # 0..100
order: int             # ordering for 2x2 stacking
visible: bool = True
locked: bool = False

# Product-only
variant: "brand|success|warn|teal|violet" | None
bg_from: str | None
bg_to: str | None
border_color: str | None
```

- **Ordering:** server-side sort by `order`, then title. Render in a 2×2 grid on desktop, 1-up on mobile.
- **Locking:** renders lock icon, disables CTAs, leaves tile visible.
- **Visibility:** `visible=False` removes the tile from render.
- **Gradients:** set via `variant` or inline CSS custom properties (`--tile-from|to|border`).

---

## 4. CSS Single Source of Truth

```css
.dashboard-shell .dashboard-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--space-6);
}

.dashboard-shell .dashboard-grid > [data-testid="stMarkdownContainer"],
.dashboard-shell .dashboard-grid > [data-testid="stMarkdown"],
.dashboard-shell .dashboard-grid > div[data-testid="stMarkdown"] {
  grid-column: span 6 !important;
}

@media (max-width: 900px) {
  .dashboard-shell .dashboard-grid > [data-testid="stMarkdownContainer"],
  .dashboard-shell .dashboard-grid > [data-testid="stMarkdown"],
  .dashboard-shell .dashboard-grid > div[data-testid="stMarkdown"] {
    grid-column: span 12 !important;
  }
}

.dashboard-grid .ptile { grid-column: span 6; }
.dashboard-grid .mtile { grid-column: span 12; }
@media (max-width: 900px) {
  .dashboard-grid .ptile,
  .dashboard-grid .mtile { grid-column: span 12; }
}
```

Supporting rules:

```css
.dashboard-shell { min-height: auto; }
.dashboard-head  { padding: 0; margin: 0; }
.dashboard-grid > div[data-testid="stMarkdownContainer"],
.dashboard-grid > div[data-testid="stMarkdown"] {
  display: contents;
}
```

**Do not** set `grid-column` on `.dashboard-card` or duplicate `.dashboard-grid` definitions elsewhere.

---

## 5. Hub Structure

Every hub must:

1. Compose `ProductTileHub` (and `ModuleTileCompact` if necessary) with canonical fields.
2. Compute a contextual `Hub Guide` block via `compute_hub_guide(hub_key)`.
3. Fetch hub-specific additional services via `get_additional_services(hub_key)`.
4. Call `render_dashboard(...)` (owned by `BaseHub`) with title, subtitle, chips, guide, cards, and additional services.

Example pattern:

```python
person = st.session_state.get("person_name", "John")
progress_gcp = float(st.session_state.get("gcp", {}).get("progress", 0))
progress_cost = float(st.session_state.get("cost", {}).get("progress", 0))

cards = [
    ProductTileHub(key="gcp",  order=10, progress=progress_gcp,  variant="brand", ...),
    ProductTileHub(key="cost", order=20, progress=progress_cost, variant="brand", ...),
    ProductTileHub(key="pfma", order=30, variant="brand", ...),
    ProductTileHub(key="faqs", order=40, variant="teal", ...),
]

guide = compute_hub_guide("concierge")
additional = get_additional_services("concierge")

render_dashboard(
    title="Concierge Care Hub",
    subtitle="Finish the essentials, then unlock curated next steps with your advisor.",
    chips=[
        {"label": "Concierge journey"},
        {"label": f"For {person}", "variant": "muted"},
        {"label": "Advisor & AI blended"},
    ],
    hub_guide_block=guide,
    cards=cards,
    additional_services=additional,
)
```

---

## 6. IA Updates & Deletions

- Core product flow remains **Guided Care Plan → Cost Planner → Plan for My Advisor**. The Hub Guide now handles “next action” CTAs.
- **Trusted Partners:** retain a single page; delete any `_new` variants.
- Remove references/examples of the legacy dashboard layer throughout documentation.

---

## 7. Acceptance Checklist

- Hubs render in this sequence: Title / Subtitle / Chips → **Hub Guide** → **2×2 Tile Grid** → **Additional Services**.
- Tiles respect `order`, `visible`, and `locked`.
- Hubs never open layout containers; `BaseHub` does.
- Exactly one `.dashboard-grid` definition; Streamlit wrappers get span rules; no invalid `grid-template-columns`.
- Only one Trusted Partners page exists.

---

## 8. Migration Notes

- Remove legacy `ui/dashboard.py` if it only emitted layout; keep layout-agnostic helpers by relocating to `core/`.
- Grep and remove manual `<div class="dashboard-grid">` usage, top-level `st.divider()` in hubs, and duplicate `.dashboard-grid` CSS blocks.
- After updates, instruct QA to **Empty Caches** in Safari (Develop → Empty Caches) to pull fresh CSS.
