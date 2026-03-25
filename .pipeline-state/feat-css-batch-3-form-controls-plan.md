# CSS Batch 3 — Form Control Components Plan

## Components

### 1. Combobox (#31)
**HTML structure** (from `combobox()` in templatetags):
- `.form-group` > `.combobox` wrapper
- `.combobox-input.form-input` — text input for search
- `.combobox-dropdown` — option list container
- `.combobox-option` / `.combobox-option-selected` — individual options
- Multi-select: `.combobox-tags` > `.combobox-tag` (already styled in batch prior)

**CSS needed**: `.combobox` container, `.combobox-input` focus behavior, `.combobox-dropdown` positioned below input, `.combobox-option` hover/selected states.

### 2. Color Picker (#40)
**HTML structure** (from `color_picker()`):
- `.form-group` > `.color-picker` wrapper
- `.color-preview` — swatch showing current color
- `.color-swatches` — grid of preset buttons
- `.color-swatch` / `.color-swatch-active` — individual swatch buttons
- `.color-hex-input.form-input` — hex text input

**CSS needed**: `.color-picker` layout, `.color-preview` swatch, `.color-swatches` grid, `.color-swatch` circle buttons with active ring.

### 3. Date Picker (#46)
**HTML structure** (from `date_picker()`):
- `.form-group` > `.date-picker` wrapper
- `.dp-header` — month/year nav row
- `.dp-nav-btn` — prev/next arrows
- `.dp-month-label` — month name
- `.dp-grid` — 7-column calendar grid
- `.dp-weekday` — header cells (Mo Tu We...)
- `.dp-day` / `.dp-day-empty` / `.dp-day-today` / `.dp-day-selected` — day cells
- `.dp-selected-value` — display of selected date
- Range classes already styled: `.dp-day-range-start`, `.dp-day-range-end`, `.dp-day-in-range`

**CSS needed**: `.date-picker` card, `.dp-header` flexbox, `.dp-nav-btn`, `.dp-month-label`, `.dp-grid` 7-col grid, `.dp-weekday`, `.dp-day` states (empty, today, selected, hover).

### 4. File Dropzone (#47)
**HTML structure** (from `file_dropzone()`):
- `.dropzone` wrapper (with drag events)
- `.dropzone-input` — hidden file input
- `.dz-icon` — upload icon
- `.dz-text` > `.dz-browse` — instruction text with clickable browse link
- `.dz-hint` — size/type hint
- `.dz-file-count` — shows count after selection
- `.dropzone-over` — drag-over state class
- `.dropzone-has-file` — file selected state class

**CSS needed**: `.dropzone` dashed border area, `.dropzone-input` hidden, `.dz-icon` large centered, `.dz-text`/`.dz-browse`, `.dz-hint`, drag-over highlight, has-file state.

## Conventions
- One-line rules, theme tokens only (`hsl(var(--token))`, `var(--space-N)`, etc.)
- BEM-ish flat class names
- Transitions use `var(--duration-fast)` or `var(--duration-normal)`
- Section comments: `/* Component Name */`

## Test approach
- Render each component via templatetag function
- Assert CSS class names appear in output HTML
- Verify state classes (selected, active, hover targets, drag-over)
