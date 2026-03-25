# Changelog

All notable changes to djust-components will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Component Classes**: 7 new Python component classes for programmatic use in LiveViews — `Alert` (dismissible notifications with info/success/warning/danger factory methods), `StatCard` (KPI display with label/value/trend/icon), `Tag` (compact label chips with color variants and dismiss), `Toast` (transient notifications with success/error/warning/info factories and auto-dismiss duration), `Progress` (progress bars with percentage, label, ARIA, and variant support), `Spinner` (loading indicator with size variants and screen-reader label), `Switch` (toggle with `.toggle()` method, dj-change event, and accessible checkbox markup)
- **Test Coverage Expansion**: 226 new tests covering all 52 Rust handler classes in 4 batches — (1) rendering and CSS class verification for 33 previously untested handlers (CardHandler, AlertHandler, FormGroupHandler, TimelineHandler, DjButtonHandler, DjInputHandler, DjSelectHandler, DjTextareaHandler, DjCheckboxHandler, DjRadioHandler, SwitchHandler, StatCardHandler, TagChipHandler, StepperHandler, SkeletonHandler, BreadcrumbHandler, EmptyStateHandler, DividerHandler, SpinnerHandler, PaginationHandler, AvatarHandler, BadgeHandler, ProgressHandler, ToastContainerHandler, TooltipHandler, DropdownHandler, AccordionHandler, AccordionItemHandler, TabsHandler, DataTableHandler, plus 17 delegating handlers); (2) form component interaction testing verifying dj-input, dj-change, and dj-click event attribute emission across all form handlers; (3) complex component state tests for DataTable sort indicators/selection/pagination/search, Stepper active/complete states, and Breadcrumb active items; (4) edge case tests including empty/missing parameters for all handlers and XSS payload injection tests for every handler accepting user text
- **Data Table Pro Phase 3**: 13 advanced features completing the P0 Data Table Pro work — row expansion with detail rows (`expandable=True`, `expand_event`, `expanded_rows`); bulk actions toolbar with selected count and action buttons (`bulk_actions`, `bulk_action_event`); CSV/JSON export buttons (`exportable=True`, `export_event`, `export_formats`); row grouping by column value with collapse/expand and counts (`group_by`, `group_toggle_event`, `collapsible_groups`, `collapsed_groups`); custom cell renderers for badges, progress bars, and avatars (`cell_template` column config); keyboard navigation between cells with arrow keys, Enter to edit, Escape to cancel (`keyboard_nav=True`); virtual scrolling for 50+ row datasets (`virtual_scroll=True`, `virtual_row_height`, `virtual_buffer`); explicit server-side mode that skips client queryset pipeline (`server_mode=True`, `refresh_table_server()`); faceted filtering with value counts (`facets=True`, `facet_counts`, `get_facet_counts()`); state persistence to localStorage (`persist_key`); column pinning via per-column config (`pinned="left"|"right"`); print-friendly mode hiding interactive chrome (`printable=True`, `@media print` rules); column statistics footer with min/max/avg per numeric column (`stats=True` column config, `column_stats`, `get_column_stats()`)
- **DataTableMixin Phase 3**: New event handlers — `on_table_expand`, `on_table_bulk_action`, `on_table_export`, `on_table_group`, `on_table_group_toggle`; override hooks `handle_bulk_action()`, `handle_export()`, `refresh_table_server()`; computed helpers `get_facet_counts()`, `get_column_stats()`, `_group_rows()`; new state: `table_expanded_rows`, `table_collapsed_groups`, `table_current_group_by`, `table_facet_counts`, `table_column_stats`
- **Client-side JS Phase 3**: Keyboard navigation (arrow keys, Enter/Escape), virtual scrolling with viewport-based row rendering, state persistence via localStorage with MutationObserver auto-save
- **CSS Phase 3**: 50+ lines — `.data-table-expand-*`, `.data-table-bulk-*`, `.data-table-export-*`, `.data-table-group-*`, `.cell-renderer-badge/progress/avatar`, `.data-table-pinned-left/right`, `.data-table-stats-*`, `@media print` rules for `.data-table-printable`

- **Data Table Pro Phase 2**: Editing and layout enhancements for the data table component — inline cell editing (`editable_columns`, `edit_event`) with click-to-edit, Enter/Escape save/cancel; column resize via drag handles (`resizable=True`, client-side JS); column reorder via drag-and-drop (`reorderable=True`, `reorder_event`); frozen left/right columns with CSS sticky positioning (`frozen_left`, `frozen_right`); column visibility dropdown toggle (`column_visibility=True`, `visibility_event`); density toggle between compact/comfortable/spacious (`density_toggle=True`, `density_event`); responsive card collapse on narrow viewports (`responsive_cards=True`, CSS `@container` with `@media` fallback); editable row mode with Edit/Save/Cancel buttons (`editable_rows=True`, `edit_row_event`, `save_row_event`, `cancel_row_event`, `editing_rows`)
- **DataTableMixin Phase 2**: New event handlers — `on_table_cell_edit`, `on_table_reorder`, `on_table_visibility`, `on_table_density`, `on_table_row_edit`, `on_table_row_save`, `on_table_row_cancel`; override hooks `handle_cell_edit()` and `handle_row_save()` for persistence; new state: `table_editing_rows`, `table_column_order`, `table_visible_columns`, `table_current_density`
- **Client-side JS module**: `static/djust_components/data-table.js` — auto-initializing script for column resize drag handles, column reorder drag-and-drop, column visibility menu toggle, density toggle, and inline cell editing activation; uses MutationObserver for LiveView compatibility
- **CSS**: 60+ lines of Phase 2 data table styles — `.data-table-cell-editing`, `.data-table-frozen-left/right`, `.data-table-spacious`, `.data-table-resize-handle`, `.data-table-toolbar`, `.data-table-visibility-*`, `.data-table-density-*`, `.data-table-row-actions`, `.data-table-row-editing`, `.data-table-responsive` with `@container` and `@media` card collapse

- **Data Table Pro Phase 1**: Core interactivity for the data table component — row selection with checkboxes (`selectable`, `selected_rows`, `select_event`, `row_key`), global search with debounce (`search`, `search_query`, `search_event`, `search_debounce`), per-column text and select filters (`filterable`, `filter_type`, `filter_options`, `filter_event`), built-in pagination (`paginate`, `page_event`), loading/skeleton state (`loading`), empty state with customizable title/description/icon, per-column `sortable` flag, column `width`, and `striped`/`compact` styling variants
- **DataTableMixin**: New mixin class for LiveViews (`djust_components.mixins.data_table`) that auto-generates sort, search, filter, select, and paginate event handlers from a model or queryset — includes `init_table_state()`, `refresh_table()`, `get_table_context()`, and full queryset pipeline (`_apply_table_search`, `_apply_table_filters`, `_apply_table_sort`, `_apply_table_pagination`)
- **ARIA accessibility**: Data table now renders `role="grid"`, `aria-label`, `aria-sort` on sortable headers, `aria-selected` on selectable rows, `aria-busy` during loading, `role="searchbox"` on search input, `role="status"` on empty state, and `role="navigation"` on pagination
- **CSS**: 24 new data table styles — `.data-table-container`, `.data-table-search`, `.data-table-filter`, `.data-table-checkbox`, `.data-table-select-all`, `.data-table-header-cell`, `.data-table-striped`, `.data-table-compact`, `.data-table-loading`, `.data-table-empty`, `.data-table-pagination`, `tr[aria-selected="true"]` highlight, and `th[aria-sort]` cursor styling

- **CSS**: Styles for 9 complex data/interactive components — Notification Center (bell trigger, badge, dropdown list, read/unread states, timestamps), Tree View (nested indentation, expand/collapse toggle, selected node highlight), Gauge/Donut (SVG arc with color variants and value display), Image Carousel (slides, prev/next buttons, dot indicators, caption overlay), Virtual List (scrollable viewport, item rows, load-more sentinel), Kanban Board (columns with drag-over state, draggable cards, label colors), Table of Contents (nav with active link highlighting and level indentation), Split Pane (horizontal/vertical layout, draggable resize handle), Rich Text Editor (toolbar with buttons/separators, contenteditable area, placeholder)
- **CSS**: Styles for Combobox, Color Picker, Date Picker, and File Dropzone form control components — combobox with searchable dropdown and option hover/selected states, color picker with swatch grid/preview/hex input, date picker with calendar grid/nav/today/selected/range states, file dropzone with dashed border/drag-over highlight/file-count feedback
- **CSS**: Styles for Popover, Sheet/Drawer, Context Menu, and Command Palette components — popover with positioned placement arrows and fade-scale transition, sheet/drawer with slide-in from left/right/bottom and backdrop overlay, context menu with absolute positioning and scale transition, command palette with modal overlay, search input, and scrollable results list
- **CSS**: Styles for Kbd, Copy Button, Rating, Code Block, and Collapsible components — keyboard shortcut keys with raised-border look, star ratings with gold/muted coloring and hover effects, code blocks with header/filename/language/copy-button layout, and collapsible panels with animated icon and toggle visibility

### Fixed
- **Virtual List**: Rust handler now deserializes JSON strings for `items` when the Rust engine passes list-of-dicts as serialized JSON
- **Kanban Board**: Rust handler now deserializes JSON strings for `columns` (same fix as Virtual List)

### Added
- **Combobox**: Multi-select mode with `multiple=True` and `selected` list — renders removable tag chips, hidden inputs for form submission, and per-option selected state
- **Date Picker**: Date range selection with `range=True`, `range_start`, and `range_end` — adds range highlighting CSS classes and dual hidden inputs for form submission
- **Code Block**: Syntax highlighting via highlight.js CDN lazy-loading with `highlight=True` (default) and configurable `theme` parameter
- **Component Gallery**: `python manage.py component_gallery` management command renders every component for visual QA — auto-discovers all template tags and component classes, groups by category, supports light/dark mode toggle and responsive preview (mobile/tablet/desktop), includes `--dry-run` to list components without starting the server
- **Rust engine handlers**: 40+ component tag handlers for the Rust template engine — components now work without `{% load djust_components %}` when using Rust-rendered templates
- **Tier 1 handlers**: Modal, Tabs, Accordion, Dropdown, Toast, Tooltip, Progress, Badge, Card, DataTable, Pagination, Avatar, Alert, Switch, Divider, Breadcrumb, Skeleton, StatusDot, Button, Stepper, Timeline
- **Tier 2/3 handlers**: CodeBlock, Combobox, Rating, CopyButton, Kbd, Gauge, NotificationCenter, TreeView, ColorPicker, Carousel, Popover, Collapsible, Sheet, CommandPalette, ContextMenu, PaletteItem, ContextMenuItem
- **v1.3 handlers**: DatePicker, FileDropzone, VirtualList, KanbanBoard, TableOfContents, RichTextEditor, SplitPane
- **CSS**: 206 lines of component styles for Tier 2/3 and v1.3 components
- **Auto-registration**: Components register with the Rust engine automatically via `AppConfig.ready()`

### Fixed
- **Combobox**: Fixed `onmousedown` event handler preventing item selection
- **Switch**: Fixed HTML structure to use `<span class="switch">` wrapper
- **Divider**: Fixed CSS class generation for divider variants
- **TableOfContents**: Fixed item rendering for nested headings
- **`_parse_args`**: Fixed parsing of `"1"` and `"0"` string values being treated as booleans

### Changed
- **Dependencies**: Removed `djust-theming` as a hard dependency. The previous constraint was `djust-theming>=0.3.0,<1.0`, which required an unreleased version and blocked installation. djust-theming is now optional — install it separately if you want automatic theme adaptation.

### Security
- **Rust handlers**: All block handlers (`PopoverHandler`, `CollapsibleHandler`, `SheetHandler`, `CommandPaletteHandler`, `ContextMenuHandler`, `SplitPaneHandler`) now wrap returns in `mark_safe()` to prevent double-escaping in the Rust engine
- **templatetags**: All user-controlled values interpolated inside `mark_safe(f"...")` strings are now wrapped with `conditional_escape()`, preventing XSS from attacker-controlled template tag arguments (modal `title`/`close_event`, tabs `id`/`event`, accordion `id`/`event`, dropdown `id`/`label`/`toggle_event`/`variant`, tooltip `text`/`position`, card `title`/`subtitle`/`variant`/`class`)
- **Markdown component**: Replaced regex-based post-render sanitizer with [`nh3`](https://nh3.readthedocs.io/) (Rust-backed, allowlist-based sanitizer). Explicitly allowed tags and attributes are now enumerated; URL schemes restricted to `http`, `https`, `mailto`; `javascript:`, `data:`, and `vbscript:` URLs are blocked

## [0.3.0] - 2026-02-19

### Added
- **Component Class API** — Python-first alternative to template tags for programmatic use in LiveViews
- `Badge` — status/priority badge with factory methods `Badge.status()` and `Badge.priority()` for auto-coloring
- `StatusDot` — animated dot indicator with built-in status → variant/animation mappings
- `Button` — action button with variants, icons, loading state, and djust event wiring
- `Card` — content container with image/header/content/footer sections and hover/click support
- `Markdown` — renders Markdown to sanitized HTML; strips dangerous tags and `on*` event attributes; wraps in `<div class="dj-prose">`
- `markdown>=3.0` added as a dependency (required by `Markdown` component)

### Fixed
- `Markdown`: post-render sanitization instead of pre-escaping source text, fixing code spans containing `&`, `<`, `>`

## [0.2.0] - 2026-02-17

### Added
- **djust-theming Integration**
  - All components now use djust-theming CSS variables for automatic theme adaptation
  - Components automatically adapt to theme preset (Default, Shadcn, Blue, Green, Purple, Orange, Rose)
  - Components automatically adapt to theme mode (light/dark/system)
  - Support for all 31 theme color tokens (including new info, link, code, selection colors)

- **Design Tokens**
  - Spacing: Uses djust-theming spacing scale (`--space-1` to `--space-24`)
  - Typography: Uses djust-theming type scale (`--text-xs` to `--text-4xl`, line heights, font weights)
  - Radius: Uses djust-theming radius tokens (`--radius-sm` to `--radius-full`)
  - Transitions: Uses djust-theming timing tokens (`--duration-fast`, `--duration-normal`)
  - Shadows: Uses djust-theming shadow tokens (`--shadow-sm`, `--shadow-md`, `--shadow-lg`)

### Changed
- **Complete CSS Refactor**
  - Replaced all hardcoded colors with theme CSS variables
  - Replaced all hardcoded spacing/sizing with design tokens
  - Replaced all hardcoded border radius values with design tokens
  - Replaced all hardcoded transition timings with design tokens
  - Replaced all hardcoded box-shadow values with design tokens

- **Dependencies**
  - Added `djust-theming>=1.1.0` as a required dependency

### Removed
- **Legacy CSS Custom Properties**
  - Removed `--dj-primary`, `--dj-success`, `--dj-warning`, `--dj-danger`, `--dj-info`
  - Removed `--dj-text`, `--dj-bg`, `--dj-bg-subtle`, `--dj-border`, `--dj-radius`
  - All replaced with djust-theming variables

### Migration Guide from 0.1.0 to 0.2.0

If you were using custom CSS variables to style components, you need to migrate to djust-theming:

1. Install djust-theming: `pip install djust-theming`
2. Add `djust_theming` to `INSTALLED_APPS`
3. Replace component CSS include with:
   ```html
   {% load djust_theming %}
   {% theme_head %}
   <link rel="stylesheet" href="{% static 'djust_components/components.css' %}">
   ```
4. Remove custom CSS variable overrides (components now use theme variables)
5. Use djust-theming's preset system for custom themes

**Breaking Change:** Components no longer support custom CSS variables. Use djust-theming presets instead.

## [0.1.0] - 2026-02-04

### Added
- Initial release with 12 pre-built components
- Modal, Tabs, Accordion, Dropdown, Toast, Tooltip, Progress, Badge, Card, DataTable, Pagination, Avatar
- Self-contained CSS with no JavaScript dependencies
- Full djust event system integration (`dj-click`, `dj-input`, etc.)
- Customizable via CSS custom properties

[Unreleased]: https://github.com/djust-org/djust-components/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/djust-org/djust-components/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/djust-org/djust-components/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/djust-org/djust-components/releases/tag/v0.1.0
