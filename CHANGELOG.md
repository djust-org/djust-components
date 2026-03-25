# Changelog

All notable changes to djust-components will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
