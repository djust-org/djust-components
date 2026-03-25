# Data Table Pro Phase 3 — Advanced Features Plan

## Overview
Build on Phases 1+2 (sort/search/filter/select/paginate + editing/resize/reorder/frozen/visibility/density/responsive/row-edit) to add 13 advanced features. All opt-in via params.

## Features

### 1. Row Expansion
- **Param**: `expandable=True`, `expand_event="table_expand"`, `expanded_rows=[]`
- **Renderer**: Adds expand toggle cell (first col), detail `<tr>` with `colspan` after each row
- **Mixin**: `on_table_expand(value)` toggles row in `table_expanded_rows`
- **Context key**: `expand_content` callback or `expand_template` name

### 2. Bulk Actions
- **Param**: `bulk_actions=[{"key":"delete","label":"Delete"},...]`
- **Renderer**: Toolbar appears when `selected_rows` is non-empty, renders action buttons
- **Mixin**: `on_table_bulk_action(value)` dispatches to `handle_bulk_action(action, selected)`

### 3. Export
- **Param**: `exportable=True`, `export_event="table_export"`, `export_formats=["csv","json"]`
- **Renderer**: Export button(s) in toolbar
- **Mixin**: `on_table_export(value)` calls `handle_export(format)` which generates file data

### 4. Row Grouping
- **Param**: `group_by=""`, `group_event="table_group"`, `collapsible_groups=True`, `collapsed_groups=[]`
- **Renderer**: Group header rows with colspan, collapse toggle
- **Mixin**: `on_table_group(value)` sets group column, `on_table_group_toggle(value)` toggles collapse

### 5. Custom Cell Renderers
- **Param**: Column-level `cell_template` key in column config dict
- **Renderer**: Wraps cell content in `<span class="cell-renderer cell-renderer-{type}">` with data attrs
- **Types**: badge, progress, avatar (detected from `cell_template` value)

### 6. Keyboard Navigation
- **Param**: `keyboard_nav=True`
- **Renderer**: Adds `tabindex="0"` to wrapper, `data-keyboard-nav="true"` attr
- **JS**: Arrow key navigation between cells, Enter to activate edit, Escape to cancel

### 7. Virtual Scrolling
- **Param**: `virtual_scroll=True`, `virtual_row_height=40`, `virtual_buffer=5`
- **Renderer**: Adds `data-virtual-scroll="true"` wrapper attrs with row height/buffer
- **JS**: Viewport-based row rendering for large datasets

### 8. Server-Side Mode
- **Param**: `server_mode=True`
- **Renderer**: Adds `data-server-mode="true"` attr; all events send full state
- **Mixin**: `table_server_mode=True` skips client-side queryset pipeline, calls `refresh_table_server()`

### 9. Faceted Filtering
- **Param**: `facets=True`, `facet_counts={}`
- **Renderer**: Shows filter value counts next to filter options
- **Mixin**: `get_facet_counts()` computes value counts per filterable column

### 10. State Persistence
- **Param**: `persist_key=""`
- **Renderer**: Adds `data-persist-key="..."` attr on wrapper
- **JS**: Save/restore sort, filters, page, column visibility, density to localStorage

### 11. Column Pinning
- **Param**: Column-level `pinned="left"|"right"` in column config
- **Renderer**: Applies `data-table-pinned-left`/`data-table-pinned-right` CSS classes
- Builds on frozen column CSS but driven by per-column config rather than count

### 12. Print-Friendly Mode
- **Param**: `printable=True`
- **Renderer**: Adds `data-table-printable` class
- **CSS**: `@media print` rules hide search, toolbar, pagination, checkboxes

### 13. Column Statistics
- **Param**: Column-level `stats=True` in column config
- **Renderer**: Stats row in `<tfoot>` with min/max/avg/sum/count per numeric column
- **Mixin**: `get_column_stats()` computes stats from current rows

## Files Modified
1. `src/djust_components/rust_handlers.py` — DataTableHandler.render()
2. `src/djust_components/mixins/data_table.py` — DataTableMixin
3. `src/djust_components/templatetags/djust_components.py` — data_table() function
4. `src/djust_components/static/djust_components/data-table.js` — Client-side JS
5. `src/djust_components/static/djust_components/components.css` — CSS
6. `tests/test_data_table_pro.py` — Tests for all 13 features
7. `CHANGELOG.md` — Release notes

## Implementation Order
1. Rust handler params + rendering (all 13)
2. Mixin state + event handlers (all 13)
3. Template tag params (all 13)
4. CSS styles
5. JS enhancements (keyboard nav, virtual scroll, state persistence)
6. Tests
7. Changelog
