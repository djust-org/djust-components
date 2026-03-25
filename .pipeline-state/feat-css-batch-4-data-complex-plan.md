# CSS Batch 4 — Data & Complex Interactive Components

## Components & CSS Classes

### 1. Notification Center (#35)
HTML classes from `notification_center()`:
- `.notif-center` — wrapper
- `.notif-trigger` — bell button
- `.notif-bell` — bell icon span
- `.notif-badge` — unread count badge
- `.notif-dropdown` — dropdown panel
- `.notif-header` / `.notif-title` — dropdown header
- `.notif-list` — scrollable list
- `.notif-item` / `.notif-item-unread` — individual notifications
- `.notif-item-msg` / `.notif-item-time` — message and timestamp
- `.notif-empty` — empty state
- `.notif-footer` — footer with clear button

### 2. Tree View (#33)
HTML classes from `tree_view()`:
- `.tree` — wrapper
- `.tree-node` / `.tree-node-selected` / `.tree-node-expanded` / `.tree-node-has-children` / `.tree-node-leaf`
- `.tree-node-row` — row with toggle + label
- `.tree-toggle` — expand/collapse button
- `.tree-toggle-placeholder` — spacer for leaf nodes
- `.tree-node-label` — clickable label
- `.tree-children` — nested children container

### 3. Gauge / Donut (#43)
HTML classes from `gauge()`:
- `.gauge` / `.gauge-{color}` — wrapper with size
- `.gauge-track` — SVG background circle
- `.gauge-fill` / `.gauge-fill-{color}` — SVG progress arc
- `.gauge-value-text` — percentage text
- `.gauge-label` — label below

### 4. Image Carousel (#44)
HTML classes from `carousel()`:
- `.carousel` / `.carousel-empty` — wrapper
- `.carousel-track` — slides container
- `.carousel-slide` / `.carousel-slide-active` — individual slides
- `.carousel-img` — image element
- `.carousel-caption` — slide caption
- `.carousel-btn` / `.carousel-btn-prev` / `.carousel-btn-next` — nav buttons
- `.carousel-dots` — dot indicators container
- `.carousel-dot` / `.carousel-dot-active` — individual dots
- `.carousel-counter` — "1 / 5" text counter

### 5. Virtual List (#50)
HTML classes from `virtual_list()`:
- `.virtual-list` — wrapper
- `.vl-info` — "Showing X of Y" text
- `.vl-scroll` — scrollable viewport
- `.vl-item` — individual row
- `.vl-item-label` / `.vl-item-sub` — primary/secondary text
- `.vl-load-more` — load more sentinel

### 6. Kanban Board (#52)
HTML classes from `kanban_board()`:
- `.kanban` — wrapper (horizontal scroll)
- `.kanban-col` / `.kanban-col-over` — columns, drag-over state
- `.kanban-col-header` — column header with color border
- `.kanban-col-title` / `.kanban-col-count` — title and card count
- `.kanban-cards` — card list
- `.kanban-card` / `.dragging` — cards with drag state
- `.kanban-card-title` / `.kanban-card-sub` / `.kanban-card-label` — card content
- `.kanban-add-card` — add card button

### 7. Table of Contents (#49)
HTML classes from `table_of_contents()`:
- `.toc` — nav wrapper
- `.toc-title` — heading
- `.toc-list` — items container
- `.toc-item` / `.toc-item-active` — individual links
- `.toc-level-1` / `.toc-level-2` / `.toc-level-3` — nesting levels

### 8. Split Pane (#48)
HTML classes from `SplitPaneNode.render()`:
- `.split-pane` / `.split-pane-horizontal` / `.split-pane-vertical` — wrapper
- `.sp-pane` / `.sp-pane-1` / `.sp-pane-2` — pane containers
- `.sp-handle` / `.sp-handle-horizontal` / `.sp-handle-vertical` — resize handle

### 9. Rich Text Editor (#51)
HTML classes from `rich_text_editor()`:
- `.rte` — wrapper
- `.rte-toolbar` — toolbar container
- `.rte-btn` — toolbar buttons
- `.rte-sep` — toolbar separator
- `.rte-editor` — contenteditable area

## Conventions (from existing CSS)
- Use `hsl(var(--token))` for colors
- Use `var(--space-N)` for spacing, `var(--text-*)` for font sizes
- Use `var(--radius-*)` for border-radius, `var(--shadow-*)` for shadows
- Use `var(--duration-*)` for transitions
- One-line rules, section comments like `/* Component Name */`
- Place under new section header: `/* Batch 4 — Data & Complex Components */`

## Test Plan
- One test class per component, each test asserts a CSS class appears in rendered HTML
- Follow pattern from `test_css_batch3_form_controls.py`
- File: `tests/test_css_batch4_data_complex.py`
