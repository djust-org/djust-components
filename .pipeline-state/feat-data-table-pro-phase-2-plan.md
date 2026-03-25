# Data Table Pro Phase 2 — Editing & Layout

## Overview
Add 8 opt-in features to the existing DataTableHandler and DataTableMixin.
All features default to off, preserving Phase 1 behavior.

## Features

### 1. Inline Cell Editing
- **Params**: `editable_columns` (list of column keys), `edit_event` (default "table_cell_edit")
- **Behavior**: Click cell -> shows input, Enter saves (fires edit_event with row_key, column, value), Escape cancels
- **HTML**: `dj-click` on `<td>` to activate edit mode (client-side JS toggles input visibility), `dj-keyup` on input for Enter/Escape
- **Mixin**: `on_table_cell_edit(value, row_key=None, column=None)` handler

### 2. Column Resize
- **Params**: `resizable=False`
- **Behavior**: Pure client-side JS. Drag handle on column border resizes column width.
- **HTML**: `data-resizable="true"` attribute on wrapper; JS module handles drag
- **No server round-trip**

### 3. Column Reorder
- **Params**: `reorderable=False`, `reorder_event` (default "table_reorder")
- **Behavior**: Drag header to reorder. Client-side JS for visual drag. On drop, fires `dj-click` with new column order to persist.
- **HTML**: `data-reorderable="true"` on wrapper; draggable headers
- **Mixin**: `on_table_reorder(value)` handler — value is comma-separated column keys

### 4. Frozen Columns
- **Params**: `frozen_left` (int, default 0), `frozen_right` (int, default 0)
- **Behavior**: CSS `position: sticky` on first N / last N columns with appropriate z-index
- **HTML**: `style="position:sticky;left:0;z-index:2"` etc. on frozen `<th>` and `<td>`
- **CSS**: `.data-table-frozen-left`, `.data-table-frozen-right` classes; wrapper gets `overflow-x: auto`

### 5. Column Visibility
- **Params**: `column_visibility=False`, `visibility_event` (default "table_visibility")
- **Behavior**: Dropdown toggle in toolbar to show/hide columns. Client-side JS toggles display. On toggle, fires event to persist.
- **HTML**: Dropdown before table with checkboxes per column
- **Mixin**: `on_table_visibility(value)` handler — value is comma-separated visible column keys

### 6. Density Toggle
- **Params**: `density` (str: "comfortable"|"compact"|"spacious", default "comfortable"), `density_toggle=False`, `density_event` (default "table_density")
- **Behavior**: Toggle button group switches CSS class on table
- **HTML**: Button group in toolbar; `data-density` attribute
- **CSS**: `.data-table-spacious td` with extra padding; comfortable is default; compact already exists
- **Mixin**: `on_table_density(value)` handler

### 7. Responsive Card Collapse
- **Params**: `responsive_cards=False`
- **Behavior**: On narrow viewports, table rows render as stacked cards with column labels
- **CSS**: `@container` query (with `@media` fallback) switches table layout to card layout
- **HTML**: `data-label` attributes on `<td>` cells for card mode labels

### 8. Editable Row Mode
- **Params**: `editable_rows=False`, `edit_row_event` (default "table_row_edit"), `save_row_event` (default "table_row_save"), `cancel_row_event` (default "table_row_cancel")
- **Behavior**: "Edit" button per row -> all cells become inputs -> Save/Cancel buttons
- **HTML**: Extra `<td>` with Edit/Save/Cancel buttons; `dj-click` events
- **Mixin**: `on_table_row_edit(value)`, `on_table_row_save(value)`, `on_table_row_cancel(value)` handlers; `table_editing_rows` state (set of row keys)

## Files Modified

1. `src/djust_components/rust_handlers.py` — DataTableHandler.render() adds all 8 features
2. `src/djust_components/templatetags/djust_components.py` — data_table() tag gets new params
3. `src/djust_components/mixins/data_table.py` — DataTableMixin gets new event handlers + state
4. `src/djust_components/static/djust_components/components.css` — New CSS for frozen, density, responsive cards
5. `src/djust_components/static/djust_components/data-table.js` — NEW: Client-side JS for resize, reorder, visibility
6. `tests/test_data_table_pro.py` — Phase 2 test classes
7. `CHANGELOG.md` — Phase 2 entry

## Implementation Order

1. CSS additions (frozen, density, responsive cards)
2. JS module (resize, reorder, visibility)
3. Rust handler updates (all 8 features in render())
4. Template tag updates (new params)
5. Mixin updates (new handlers + state)
6. Tests
7. CHANGELOG
