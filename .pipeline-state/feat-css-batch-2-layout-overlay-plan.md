# CSS Batch 2 — Layout & Overlay Components Plan

## Components

### 1. Popover (#32)
- **Classes emitted**: `.popover-wrapper`, `.popover-trigger` (reuses `.btn .btn-outline .btn-sm`), `.popover .popover-{placement}`, `.popover-title`, `.popover-content`
- **Toggle mechanism**: `.popover-open` class toggled on `.popover-wrapper` via inline JS
- **Placements**: top, bottom (default), left, right
- **CSS needs**: Hidden by default, visible when parent has `.popover-open`, positioned relative to trigger, arrow pseudo-element, fade transition, z-index

### 2. Sheet / Drawer (#41)
- **Classes emitted**: `.sheet-overlay`, `.sheet .sheet-{side}`, `.sheet-header`, `.sheet-title`, `.sheet-close`, `.sheet-header-close`, `.sheet-body`
- **Sides**: left, right (default), bottom
- **Toggle mechanism**: `data-open="true"` attribute
- **CSS needs**: Fixed overlay with backdrop, sheet panel slides in from side, z-index layering, smooth slide transition

### 3. Context Menu (#42)
- **Classes emitted**: `.ctx-wrapper`, `.ctx-trigger`, `.ctx-menu`, `.ctx-item`, `.ctx-item-danger`, `.ctx-item-icon`, `.ctx-divider`
- **Toggle mechanism**: `data-open` attribute on `.ctx-menu`, positioned via inline `style.left`/`style.top`
- **CSS needs**: Hidden by default, shown with `data-open`, absolute positioning, menu styling similar to dropdown, item hover states

### 4. Command Palette (#45)
- **Classes emitted**: `.palette-overlay`, `.palette`, `.palette-search`, `.palette-search-icon`, `.palette-input`, `.palette-close`, `.palette-results`, `.palette-item`, `.palette-item-icon`, `.palette-item-body`, `.palette-item-label`, `.palette-item-desc`
- **Toggle mechanism**: `data-open="true"` attribute
- **CSS needs**: Fixed overlay (like modal), centered panel at top of viewport, search input with icon, scrollable results list, item hover/focus states, keyboard-navigable appearance

## Design Conventions (from existing CSS)
- Colors: `hsl(var(--token))` or `hsl(var(--token) / opacity)`
- Spacing: `var(--space-N)`
- Typography: `var(--text-xs)`, `var(--font-semibold)`, etc.
- Borders: `1px solid hsl(var(--border))`
- Radius: `var(--radius-md)`, `var(--radius-lg)`, etc.
- Shadows: `var(--shadow-lg)`, etc.
- Transitions: `var(--duration-normal)`, `var(--duration-fast)`
- Backdrop: `backdrop-filter: blur(20px)` on overlays
- Z-index: 40 for dropdowns, 50 for modals/tooltips, 100 for toasts

## Implementation Order
1. Popover (extends tooltip pattern with click toggle)
2. Sheet (extends modal overlay pattern with slide-in)
3. Context Menu (extends dropdown pattern with absolute positioning)
4. Command Palette (extends modal pattern with search input)

## Tests
- CSS class presence tests in `tests/test_rust_handlers.py` verifying all emitted classes appear in rendered output
- One test class per component, following existing `TestKbdHandlerCSS` pattern
