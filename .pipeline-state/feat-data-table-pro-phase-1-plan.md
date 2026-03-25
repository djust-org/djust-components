# Data Table Pro Phase 1 — Core Interactivity Plan

## Current State Analysis

### Three Rendering Paths Exist Today

1. **Rust handler** (`rust_handlers.py:DataTableHandler`, line 828) — registered as `data_table` inline tag. Renders a minimal `<div class="data-table-wrapper"><table>` with sort headers (`dj-click` on every `<th>`) and cell values. No search, no selection, no empty state beyond missing rows, no ARIA. All headers are always sortable.

2. **Template tag** (`templatetags/djust_components.py:data_table`, line 431) — `@register.inclusion_tag` rendering `djust_components/table.html`. Passes `sort_event`, `page`, `total_pages`, `prev_event`, `next_event`. The template has its own inline prev/next pagination but no per-page jump.

3. **Include template** (`components/templates/components/data_table.html`) — older standalone template with `search_enabled`, `search_event`, `search_query`, `pagination_template`, `empty_message`, and `getattr` filter for row values. Has `<style>` block with hardcoded colors. This appears to be a legacy/demo artifact.

### Existing CSS
`components.css` lines 121-131 define `.data-table-wrapper`, `.data-table`, `.data-table th`, `.data-table td`, `.sortable`, `.table-search` using CSS custom properties.

### djust Framework's Own TableComponent
`djust.components.data.table.TableComponent` (LiveComponent) already has `selectable`, `sort_column`, `sort_direction`, `sort_by()`, multi-framework rendering. This is the framework's built-in — we are building the *djust-components* equivalent that works with template tags and rust handlers.

---

## Design Decisions

### D1: Backward Compatibility
The existing `DataTableHandler.render()` signature and output must not break. New features are opt-in via additional keyword args. If no new args are passed, output is identical to today.

### D2: Single Source of Truth
We will enhance the **Rust handler** (`DataTableHandler`) as the primary rendering path, since that's what the Rust template engine uses. The **template tag** (`data_table`) will gain the same parameters and delegate context to an updated `table.html`. Both paths produce equivalent HTML structure.

### D3: CSS Class Naming
Follow existing convention: `.data-table-*` prefix for new elements. New classes:
- `.data-table-search` (global search wrapper)
- `.data-table-filter` (per-column filter)
- `.data-table-checkbox` (selection checkbox)
- `.data-table-select-all` (select-all checkbox)
- `.data-table-loading` (loading state modifier)
- `.data-table-empty` (empty state container)
- `.data-table-header-cell` (header cell with sort + filter)

### D4: DataTableMixin Lives in a New Module
`src/djust_components/mixins/data_table.py` — a Python mixin class for LiveViews that auto-generates sort/search/filter/select/paginate event handlers from a model or queryset.

### D5: No Client-Side JS Required
All interactivity is server-driven via djust's `dj-click`, `dj-input` directives. No custom JS hooks needed for Phase 1.

---

## Implementation Plan

### 1. Enhanced DataTableHandler (rust_handlers.py)

**File:** `src/djust_components/rust_handlers.py` (modify `DataTableHandler`)

**New parameters** (all optional, preserving existing defaults):

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `rows` | list[dict] | `[]` | Row data (existing) |
| `columns` | list[dict] | `[]` | Column definitions (existing) |
| `sort_by` | str | `""` | Current sort column (existing) |
| `sort_desc` | bool | `False` | Sort direction (existing) |
| `sort_event` | str | `"table_sort"` | Sort event name (existing) |
| `selectable` | bool | `False` | **NEW** Enable row selection checkboxes |
| `selected_rows` | list | `[]` | **NEW** List of selected row IDs/keys |
| `select_event` | str | `"table_select"` | **NEW** Selection event name |
| `row_key` | str | `"id"` | **NEW** Key field for row identity |
| `search` | bool | `False` | **NEW** Show global search box |
| `search_query` | str | `""` | **NEW** Current search value |
| `search_event` | str | `"table_search"` | **NEW** Search event name |
| `search_debounce` | int | `300` | **NEW** Debounce ms for search input |
| `filters` | dict | `{}` | **NEW** Per-column filter values `{col_key: value}` |
| `filter_event` | str | `"table_filter"` | **NEW** Filter event name |
| `loading` | bool | `False` | **NEW** Show skeleton loading state |
| `empty_title` | str | `"No data"` | **NEW** Empty state title |
| `empty_description` | str | `""` | **NEW** Empty state description |
| `empty_icon` | str | `""` | **NEW** Empty state icon |
| `paginate` | bool | `False` | **NEW** Show pagination |
| `page` | int | `1` | Page number (existing in templatetag) |
| `total_pages` | int | `1` | Total pages (existing in templatetag) |
| `page_event` | str | `"table_page"` | **NEW** Pagination event name |
| `striped` | bool | `False` | **NEW** Alternating row backgrounds |
| `compact` | bool | `False` | **NEW** Reduced padding |

**Column dict enhanced fields:**
```python
{
    "key": "name",           # existing
    "label": "Name",         # existing
    "sortable": True,        # NEW: default True (preserves existing behavior where all are sortable)
    "filterable": False,     # NEW: show per-column filter
    "filter_type": "text",   # NEW: text | select | date_range
    "filter_options": [],    # NEW: options for select filter type
    "width": "",             # NEW: optional column width
}
```

**Rendering changes:**
- Wrap everything in `<div class="data-table-container" role="grid" aria-label="Data table">`
- If `search=True`: render search input before table with `dj-input="{search_event}"` and `dj-debounce="{search_debounce}"`
- If `selectable=True`: add checkbox column as first `<th>` with select-all and first `<td>` per row
- Header cells: add `aria-sort="ascending|descending|none"` based on sort state
- If column has `filterable=True`: render filter input below header label inside `<th>`
- If `loading=True`: render skeleton table (reuse `SkeletonHandler` output for type="table")
- If no rows and not loading: render empty state (reuse `EmptyStateHandler` pattern)
- If `paginate=True` and `total_pages > 1`: render pagination below table (reuse `PaginationHandler`)
- If `selectable=True`: rows get `aria-selected="true|false"`, checkboxes get `dj-click="{select_event}"` with `data-value="{row[row_key]}"`
- If `striped=True`: add `.data-table-striped` class
- If `compact=True`: add `.data-table-compact` class

### 2. Enhanced Template Tag (templatetags/djust_components.py)

**File:** `src/djust_components/templatetags/djust_components.py` (modify `data_table`)

Add all new parameters to the `@register.inclusion_tag` function signature with matching defaults. Pass them through to the template context.

### 3. Enhanced Template (table.html)

**File:** `src/djust_components/templates/djust_components/table.html`

Rewrite to support all new features with conditional blocks:
- `{% if search %}` block for global search
- `{% if selectable %}` blocks for checkbox column
- `{% if col.filterable %}` blocks for per-column filters
- `{% if loading %}` / `{% elif rows %}` / `{% else %}` for state handling
- `{% if paginate and total_pages > 1 %}` for pagination
- ARIA attributes throughout

### 4. CSS Additions (components.css)

**File:** `src/djust_components/static/djust_components/components.css`

Add styles for new elements:
```
.data-table-container     — outer wrapper
.data-table-search        — search input wrapper
.data-table-filter        — per-column filter input
.data-table-checkbox      — checkbox styling
.data-table-striped tr:nth-child(even) — striped rows
.data-table-compact td    — reduced padding
.data-table-loading       — loading overlay/skeleton
.data-table-empty         — empty state inside table
.data-table th[aria-sort] — sort indicator styling
.data-table tr[aria-selected="true"] — selected row highlight
```

All using existing CSS custom properties (`--border`, `--muted`, `--accent`, etc.).

### 5. DataTableMixin (new file)

**File:** `src/djust_components/mixins/__init__.py` (new directory)
**File:** `src/djust_components/mixins/data_table.py` (new file)

```python
class DataTableMixin:
    """
    Mixin for LiveViews that provides automatic data table event handlers.

    Usage:
        class UserListView(DataTableMixin, LiveView):
            table_model = User
            table_columns = [
                {"key": "username", "label": "Username", "sortable": True, "filterable": True},
                {"key": "email", "label": "Email", "sortable": True},
                {"key": "is_active", "label": "Active", "filter_type": "select",
                 "filter_options": [{"value": "true", "label": "Yes"}, {"value": "false", "label": "No"}]},
            ]
            table_page_size = 25
            table_default_sort = "username"
            table_searchable_fields = ["username", "email"]
    """

    # Class-level configuration
    table_model = None                    # Django model class
    table_queryset = None                 # Or provide a queryset directly
    table_columns = []                    # Column definitions
    table_page_size = 25                  # Rows per page
    table_default_sort = ""               # Default sort column
    table_default_sort_desc = False       # Default sort direction
    table_searchable_fields = []          # Fields for global search
    table_row_key = "id"                  # Row identity field
    table_selectable = False              # Enable row selection

    # Event name configuration (overridable)
    table_sort_event = "table_sort"
    table_search_event = "table_search"
    table_filter_event = "table_filter"
    table_select_event = "table_select"
    table_page_event = "table_page"
```

**Methods provided by the mixin:**

- `get_table_queryset()` — returns base queryset (from `table_model.objects.all()` or `table_queryset`)
- `get_table_context()` — returns full dict of template context vars for the data_table tag
- `_apply_table_search(qs)` — applies `Q` filter across `table_searchable_fields`
- `_apply_table_filters(qs)` — applies per-column filters from `self.table_filters`
- `_apply_table_sort(qs)` — applies `order_by` from `self.table_sort_by` / `self.table_sort_desc`
- `_apply_table_pagination(qs)` — slices queryset, sets `self.table_total_pages`

**Auto-generated event handlers** (decorated with `@event_handler`):

- `on_table_sort(value, **kwargs)` — cycles sort: none -> asc -> desc -> none
- `on_table_search(value, **kwargs)` — sets `self.table_search_query`, resets to page 1
- `on_table_filter(value, **kwargs)` — expects `data-column` + value, updates `self.table_filters[column]`, resets to page 1
- `on_table_select(value, **kwargs)` — toggles row in `self.table_selected_rows`; handles "all" value for select-all
- `on_table_page(value, **kwargs)` — sets `self.table_page`

All handlers call `self._refresh_table()` which runs the full pipeline: queryset -> search -> filter -> sort -> paginate -> serialize to rows.

**Instance state** (set during mount/refresh):

- `self.table_sort_by: str`
- `self.table_sort_desc: bool`
- `self.table_search_query: str`
- `self.table_filters: dict`
- `self.table_selected_rows: list`
- `self.table_page: int`
- `self.table_total_pages: int`
- `self.table_rows: list[dict]`
- `self.table_loading: bool`

### 6. Export Updates

**File:** `src/djust_components/__init__.py`
- Add `DataTableMixin` to imports and `__all__`

**File:** `src/djust_components/mixins/__init__.py`
- Export `DataTableMixin`

### 7. Update Include Template

**File:** `components/templates/components/data_table.html`
- This legacy template should be updated to match the new feature set, or marked as deprecated in favor of the templatetag/rust handler approach. Recommend deprecation comment + redirect to `{% data_table %}`.

---

## ARIA / Accessibility Plan

| Element | Attribute | Value |
|---------|-----------|-------|
| Table wrapper | `role="grid"` | Identifies as data grid |
| Table wrapper | `aria-label` | Configurable label |
| Table wrapper | `aria-busy="true"` | When loading |
| `<th>` (sortable) | `aria-sort` | `ascending` / `descending` / `none` |
| `<th>` (sortable) | `role="columnheader"` | Semantic role |
| `<tr>` (selectable) | `aria-selected` | `true` / `false` |
| Search input | `role="searchbox"` | Semantic role |
| Search input | `aria-label="Search table"` | Accessible label |
| Filter input | `aria-label="Filter {column}"` | Per-column label |
| Empty state | `role="status"` | Live region |
| Loading state | `aria-live="polite"` | Announces loading |
| Pagination | `role="navigation"` | Already in PaginationHandler |
| Pagination | `aria-label="Table pagination"` | Identifies purpose |
| Select-all checkbox | `aria-label="Select all rows"` | Accessible label |
| Row checkbox | `aria-label="Select row"` | Accessible label |

**Keyboard navigation** (handled by browser defaults + djust):
- Tab moves between interactive elements (search, filters, checkboxes, sort headers, pagination)
- Enter/Space on sort header triggers sort
- Enter/Space on checkbox toggles selection
- No custom JS keyboard handling needed in Phase 1 (shift-click range selection deferred to Phase 2 or handled via JS hook)

**Note on shift-click range selection:** This requires client-side state tracking (last-clicked index). Options:
- Phase 1: Skip shift-click, support only individual toggle + select-all
- Phase 1 stretch: Add a small JS hook that tracks last-clicked and sends range to server

Recommendation: **Phase 1 skips shift-click range selection.** Individual select + select-all covers 90% of use cases. Shift-click can be Phase 2 with a JS hook.

---

## Backward Compatibility Checklist

1. `{% data_table rows=rows columns=columns %}` with no other args produces identical output
2. `DataTableHandler` with only `rows`, `columns`, `sort_by`, `sort_desc`, `sort_event` produces identical HTML
3. All existing CSS classes (`.data-table-wrapper`, `.data-table`, `.sortable`, etc.) are preserved
4. The `components/templates/components/data_table.html` include template still works but is soft-deprecated
5. No breaking changes to the `data_table` templatetag signature (all new params have defaults)

---

## File Change Summary

| File | Action | Scope |
|------|--------|-------|
| `src/djust_components/rust_handlers.py` | Modify | Expand `DataTableHandler.render()` (~150 lines) |
| `src/djust_components/templatetags/djust_components.py` | Modify | Expand `data_table()` signature (~20 lines) |
| `src/djust_components/templates/djust_components/table.html` | Rewrite | Full template with conditionals (~80 lines) |
| `src/djust_components/static/djust_components/components.css` | Modify | Add ~40 lines of new CSS |
| `src/djust_components/mixins/__init__.py` | **Create** | 1-line export |
| `src/djust_components/mixins/data_table.py` | **Create** | DataTableMixin class (~250 lines) |
| `src/djust_components/__init__.py` | Modify | Add DataTableMixin export |
| `components/templates/components/data_table.html` | Modify | Add deprecation notice |

---

## Test Strategy

### Test File: `tests/test_data_table_pro.py`

**Setup:** Same Django settings pattern as `test_rust_handlers.py`. Stub `djust` module for mixin tests.

#### A. Rust Handler Tests (~25 tests)

1. **Backward compat**: existing args produce identical output
2. **Sort rendering**: `aria-sort` attributes, sort arrows, active class
3. **Sort cycle**: none -> asc -> desc per column
4. **Selection checkbox column**: renders when `selectable=True`
5. **Select-all checkbox**: present in header
6. **Selected rows**: `aria-selected="true"` on matching rows
7. **Selection event**: `dj-click` with correct event name and data-value
8. **Global search**: renders search input when `search=True`
9. **Search debounce**: `dj-debounce` attribute present
10. **Search value**: pre-filled with `search_query`
11. **Per-column text filter**: renders input when `filterable=True`
12. **Per-column select filter**: renders `<select>` when `filter_type="select"`
13. **Filter event**: `dj-input` with correct event name
14. **Loading state**: renders skeleton, not rows
15. **Empty state**: renders empty message when no rows
16. **Empty state custom**: uses custom title/description/icon
17. **Pagination**: renders when `paginate=True` and `total_pages > 1`
18. **Pagination disabled states**: prev disabled on page 1, next disabled on last
19. **Striped class**: `.data-table-striped` when `striped=True`
20. **Compact class**: `.data-table-compact` when `compact=True`
21. **Row key**: selection uses correct key field
22. **Column width**: `style="width:..."` when width specified
23. **XSS escaping**: all user-controlled values escaped
24. **ARIA grid role**: `role="grid"` on wrapper
25. **ARIA busy**: `aria-busy="true"` when loading

#### B. Template Tag Tests (~8 tests)

1. **Context passthrough**: all new params appear in context
2. **Default values**: unspecified params get correct defaults
3. **Backward compat**: old-style call produces same context as before

#### C. DataTableMixin Tests (~15 tests)

1. **Default state initialization**: all instance vars set correctly
2. **Sort handler**: toggles sort direction correctly
3. **Sort handler**: resets to asc on new column
4. **Search handler**: sets query, resets page to 1
5. **Filter handler**: sets filter for column, resets page to 1
6. **Select handler**: toggles individual row selection
7. **Select handler**: select-all adds/removes all visible row keys
8. **Page handler**: sets page number
9. **get_table_context()**: returns complete dict matching tag params
10. **Queryset search**: `_apply_table_search` generates correct Q objects
11. **Queryset filter**: `_apply_table_filters` generates correct filter kwargs
12. **Queryset sort**: `_apply_table_sort` generates correct `order_by`
13. **Queryset paginate**: `_apply_table_pagination` slices correctly, sets total_pages
14. **Full refresh pipeline**: all steps chain correctly
15. **Custom queryset**: `table_queryset` overrides `table_model.objects.all()`

#### D. CSS Tests (~5 tests)

1. **New classes defined**: `.data-table-container`, `.data-table-search`, etc. present in CSS
2. **Striped rule**: `.data-table-striped` rule exists
3. **Compact rule**: `.data-table-compact` rule exists
4. **Selected row highlight**: `tr[aria-selected="true"]` rule exists
5. **No regressions**: existing `.data-table-wrapper` rules unchanged

### Total: ~53 tests

---

## Implementation Order

1. CSS additions (can be done independently)
2. Rust handler expansion (core rendering logic)
3. Template tag + template update (mirrors Rust handler)
4. DataTableMixin (depends on understanding final event names)
5. Exports update
6. Tests (alongside each step, but final integration pass at end)

---

## Open Questions / Risks

1. **Shift-click range selection** — Deferred to Phase 2. Requires JS hook.
2. **Date range filter** — The `filter_type="date_range"` needs two inputs (from/to). The Rust handler will render two `<input type="date">` side by side. The filter event will send `data-column="{key}_from"` and `data-column="{key}_to"`.
3. **Custom cell rendering** — Currently cells just show `row[col.key]` as text. Column dict could accept `"template"` or `"format"` for custom rendering, but that's Phase 2 scope.
4. **Large dataset performance** — The mixin uses Django ORM pagination, so it's fine. The Rust handler operates on pre-sliced data (caller is responsible for pagination before passing rows).
5. **Select-all semantics** — "Select all" means all *visible* rows (current page), not all rows in the dataset. This matches common UX patterns (Gmail, etc.).
