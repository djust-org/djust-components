# Changelog

All notable changes to djust-components will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **AI Trust/Transparency Components**: 4 new AI trust components with Django template tags, Rust engine handlers, Python component classes, CSS, and tests (including XSS coverage):
  - **Approval Gate** (`{% approval_gate message="Delete 47 records?" risk="high" approve_event="confirm" reject_event="cancel" %}`) — Inline confirmation card for AI agent actions. Risk levels: low/medium/high/critical with color-coded borders, icons (info circle for low/medium, warning triangle for high/critical), and approve/reject buttons. Supports `message`, `risk`, `approve_event`, `reject_event`, `approve_label`, `reject_label`, `class`. ARIA `role="alert"`. Also available as Python class `ApprovalGate(...)`. (#155)
  - **Source Citation** (`{% source_citation index=1 title="API Docs" url=url relevance=0.92 %}`) — Inline footnote marker with hover popover showing source details. Superscript `[N]` marker reveals popover with title, clickable URL, and relevance percentage on hover. Supports `index`, `title`, `url`, `relevance` (0-1 float), `class`. Also available as Python class `SourceCitation(...)`. (#156)
  - **Model Selector** (`{% model_selector name="model" options=models value=current %}`) — Rich select with model metadata. Each option displays name, description, context window size, and pricing tier badge (free/standard/premium/enterprise). Supports `name`, `options` (list of dicts), `value`, `event`, `placeholder`, `disabled`, `label`, `class`. ARIA `role="combobox"` and `role="listbox"`. Also available as Python class `ModelSelector(...)`. (#131)
  - **Token Counter** (`{% token_counter current=tokens max=max_tokens %}`) — Compact progress display showing token usage vs limit. Color transitions: green (ok, <60%), yellow (warn, 60-85%), red (danger, >85%). Auto-generated comma-formatted label. Supports `current`, `max`, `label`, `show_label`, `class`. ARIA `role="meter"`. Also available as Python class `TokenCounter(...)`. (#132)

### Added
- **AI Chat Interface Components**: 4 new AI chat components with Django template tags, Rust engine handlers, CSS, and tests (including XSS coverage):
  - **Conversation Thread** (`{% conversation_thread messages=messages stream_event="new_message" %}`) — Chat-style message thread with sender avatars (initial-based), timestamps, message grouping for consecutive same-sender messages, and animated streaming response indicator (bouncing dots). Supports `messages` (list of dicts with sender/name/text/time), `stream_event`, `streaming`, `class`. Also available as Python class `ConversationThread(messages=..., streaming=True)`. (#130)
  - **AI Thinking Indicator** (`{% thinking_indicator status="thinking" label="Analyzing data..." %}`) — Animated status indicator with 4 animation modes: `thinking` (bouncing dots), `searching` (pulse), `generating` (cursor blink), `tool_use` (spinner). Returns empty string for `idle` status. Invalid statuses default to `thinking`. ARIA `role="status"`. Supports `status`, `label`, `class`. Also available as Python class `ThinkingIndicator(status=..., label=...)`. (#160)
  - **Multimodal Input** (`{% multimodal_input name="message" accept_files=True accept_voice=True event="send" %}`) — Text area with optional file attachment button (paperclip icon, hidden file input), optional voice input button (microphone icon), and send button (arrow icon). Auto-resizing textarea. Supports `name`, `event`, `placeholder`, `accept_files`, `accept_voice`, `file_accept`, `disabled`, `class`. Also available as Python class `MultimodalInput(...)`. (#159)
  - **Feedback Widget** (`{% feedback event="rate_response" mode="thumbs" %}`) — Quick feedback for AI responses with 3 modes: `thumbs` (up/down SVG icons), `stars` (1-5 star rating with fill state), `emoji` (5 reaction emojis). Active state highlighting. ARIA `role="group"`. Supports `event`, `mode`, `value`, `class`. Also available as Python class `FeedbackWidget(event=..., mode=..., value=...)`. (#149)

### Added
- **Social / User-Facing Components**: 3 new social components with Django template tags, Rust engine handlers, CSS, and tests (including XSS coverage):
  - **Avatar Group** (`{% avatar_group users=users max=5 %}`) — Stacked overlapping avatar circles with "+N" overflow count. Supports dict users (name, avatar/src) or Django user objects. Renders initials fallback when no avatar URL. Configurable `max`, `size` (sm/md/lg), `class`. Z-index stacking for proper overlap. CSS custom properties for full theming. Also available as Python class `AvatarGroup(users=..., max_display=5)`. (#89)
  - **Hover Card** (`{% hover_card trigger="@user" %}...{% endhover_card %}`) — Rich content card on hover with configurable delay-in/delay-out. GitHub-style user hovercards. Supports `trigger`, `position` (top/bottom/left/right), `delay_in` (ms), `delay_out` (ms), `class`. Pure CSS show/hide with `data-delay-*` attributes for JS enhancement. Also available as Python class `HoverCard(trigger=..., content=...)`. (#91)
  - **Notification Popover** (`{% notification_popover notifications=notifs unread_count=count mark_read_event="mark_read" %}`) — Bell icon with unread badge count + toggleable popover notification list. Badge shows "99+" overflow. Renders notification items with title, body, time, read state. Unread items fire `mark_read_event` on click. Supports `toggle_event`, `open`, `title`, `class`. Empty state message. SVG bell icon. Also available as Python class `NotificationPopover(...)`. (#168)

### Added
- **Toolbar & Editing Components**: 3 new toolbar/editing components with Django template tags, Rust engine handlers, CSS, and tests (including XSS coverage):
  - **Toolbar** (`{% toolbar %}...{% endtoolbar %}`) — Horizontal action bar with grouped buttons, separators (`{% toolbar_separator %}`), overflow menu (`{% toolbar_overflow %}`). Supports `id`, `size` (sm/md/lg), `variant` (default/flat), `class`. Overflow menu reveals hidden actions on hover. ARIA `role="toolbar"` and `role="separator"`. Responsive wrapping on mobile. (#87)
  - **Inline Edit** (`{% inline_edit value=title event="update_title" %}`) — Click text to edit in-place. Display mode shows value with pencil icon on hover. Editing mode shows focused input with save on Enter/blur, cancel on Escape. Supports `value`, `event`, `field`, `type` (text/number/etc.), `placeholder`, `editing`, `class`. Uses `dj-keydown.enter`, `dj-blur`, `dj-keydown.escape` directives. (#88)
  - **Filter Bar** (`{% filter_bar %}...{% endfilter_bar %}`) — Horizontal bar composing filter controls with responsive collapse. Sub-tags: `{% filter_select name="status" options=statuses %}`, `{% filter_date_range name="dates" %}`, `{% filter_search name="q" %}`. Auto-shows "Clear filters" button when any filter has a value. Supports `id`, `event`, `clear_event`, `class`. Select supports `options` (list of strings or `{value, label}` dicts), `value`. Date range supports `start`, `end`, `label`. Search supports `placeholder`, `value`, `debounce`. ARIA `role="search"`. Responsive: stacks vertically on mobile. (#166)

### Added
- **App Chrome Components**: 3 new layout/navigation components with Django template tags, Rust engine handlers, CSS, and tests (including XSS coverage):
  - **Sidebar Nav** (`{% sidebar %}...{% endsidebar %}`) — Collapsible sidebar navigation with nested menu items (`{% sidebar_item %}`), section headers (`{% sidebar_section %}`), icons, active state highlighting, toggle event, mobile drawer with backdrop overlay. Supports `id`, `title`, `active`, `collapsed`, `toggle_event`, `class`. Items support `label`, `href`, `icon`, `event`, nested children. (#86)
  - **Navigation Menu** (`{% nav_menu %}...{% endnav_menu %}`) — Top horizontal navigation bar with brand logo, dropdown sub-menus, mega-menu support (`mega=True`), active route highlighting, mobile hamburger collapse. Uses `{% nav_item %}` for menu entries with optional dropdown children and descriptions. Supports `brand`, `brand_href`, `toggle_event`, `mobile_open`, `active`, `class`. (#90)
  - **App Shell** (`{% app_shell %}...{% endapp_shell %}`) — Complete responsive layout wrapper combining sidebar, header, and content regions. Uses `{% app_sidebar %}`, `{% app_header %}`, `{% app_content %}` sub-tags. Semantic HTML (`<aside>`, `<header>`, `<main>`). Supports `sidebar_collapsed`, `class`, `id`. Responsive: stacks vertically on mobile. (#167)

### Added
- **Django Integration Components**: 2 new template tags bridging Django's form/model system with djust-components:
  - **Django Form Renderer** (`{% dj_form form=form %}`) — Auto-renders any Django Form or ModelForm using djust-components. Maps field types to components: `CharField`->`dj_input`, `EmailField`->`email input`, `ChoiceField`/`ModelChoiceField`->`dj_select`, `BooleanField`->`dj_checkbox`, `Textarea` widget->`dj_textarea`, `RadioSelect`->radio group, `FileField`->file input, `PasswordInput`->password input, and more. Handles non-field errors, per-field errors, help text, required markers, disabled state, hidden fields. Supports `event_prefix`, `action`, `method`, `submit_label`, `submit_event`, `custom_class`, `show_errors`. All user values escaped via `conditional_escape()` (#73)
  - **Django ModelForm Table** (`{% model_table queryset=qs %}`) — Auto-generates a data table from a Django QuerySet. Introspects model `_meta` to infer columns with labels, sortable/filterable flags, and filter types. Converts QuerySet rows to table data. Supports `exclude`/`include` for column selection, sorting, search, pagination, row selection, loading state, filters (text/select/number), striped/compact styling, `custom_class`. Skips reverse relations, handles ForeignKey display via `str()`, choice fields with filter options. All output escaped (#74)

### Added
- **Data Table Pro Phase 5 — Data Import & Computed**: 5 new opt-in features for `DataTableHandler`, `DataTableMixin`, and `{% data_table %}`:
  - **CSV/JSON Import**: `importable=True` adds Import CSV/JSON toolbar buttons with file upload. Parsed rows are validated against table columns and staged for preview before confirming. `import_event` fires with parsed rows. Supports `import_formats`, `import_preview` (preview before confirm), and `handle_import()` override hook.
  - **Computed Columns**: `computed_columns` list of `{key, label, expression}` dicts defines virtual columns evaluated server-side. Expressions support basic arithmetic (`revenue - cost`, `qty * price`) with column references. `evaluate_computed_columns()` injects values into rows. Computed columns render with italic styling.
  - **Cell Merge / Colspan**: Rows with `_merge` key (configurable via `cell_merge_key`) specify horizontal cell merging. Format: `{_merge: {col_key: colspan_int}}`. Merged cells render with `colspan` attribute; absorbed cells are hidden.
  - **Column Expressions**: `column_expressions` dict enables advanced per-column filter inputs. Supports `> N`, `>= N`, `< N`, `<= N`, `= N`, `!= N`, `contains "text"`, `startswith "text"`, `endswith "text"`, `between N and M`, `empty`, `not empty`. Expression inputs render in a separate header row with debounced events.
  - **Conditional Formatting Presets**: `conditional_formatting` list of preset dicts. Three types: `data_bar` (percentage fill bar behind cell), `color_scale` (background color interpolated between 2-3 colors), `icon_set` (prepend icon based on threshold ranges). All types support configurable `min`/`max` range.

### Added
- **Data Table Pro Phase 4 — Data Presentation**: 6 new opt-in features for `DataTableHandler`, `DataTableMixin`, and `{% data_table %}`:
  - **Column Type Formatters**: Declare `type` on column config (`number`, `currency`, `date`, `percentage`, `boolean`) for automatic display formatting. Supports `decimals`, `currency_symbol`, `true_label`/`false_label`, `date_format`. Type-specific CSS classes (`data-table-type-number`, etc.) for alignment.
  - **Footer Aggregation Row**: Optional `footer_aggregations` dict (`{col_key: "sum"|"avg"|"count"|"min"|"max"}`) renders a `<tfoot>` row with computed values per column.
  - **Conditional Row/Cell Styling**: `row_class_map` (dict or callable) applies CSS classes to `<tr>` based on data values. `cell_class` on column config (string or value-keyed dict) applies classes to `<td>`.
  - **Multi-Level Column Headers**: `column_groups` list of `{label, columns}` renders a grouped header row with `colspan` spanning sub-columns.
  - **Row Drag-and-Drop Reorder**: `row_drag=True` adds a grip handle column; fires `row_drag_event` with `{old_index, new_index}`. Mixin auto-reorders `table_rows`.
  - **Copy Row/Selection**: `copyable=True` adds a Copy toolbar button; fires `copy_event`. Mixin generates CSV/TSV in `table_copy_data`.

### Added
- **Cascading Form Components**: 3 new form components with Django template tags, Rust engine handlers, Python component classes, CSS, and tests (including XSS coverage):
  - **Dependent Select** (`{% dependent_select name="city" parent="country" source_event="load_cities" %}`) — Cascading dropdown that reloads options when parent field changes. Spinner while loading (`loading`). Supports `parent`, `source_event`, `options` (dict/string list), `value`, `placeholder`, `label`, `required`, `disabled`, `error`, `custom_class`. Uses `dj-change` event and `data-parent`/`data-source-event` attributes for wiring (#108)
  - **Currency Input** (`{% currency_input name="price" currency="USD" min=0 %}`) — Numeric input with currency symbol prefix, currency code suffix, and `type="number"` with configurable `step`/`min`/`max`. Built-in symbol lookup for 12 currencies (USD, EUR, GBP, JPY, etc.). Supports `currency`, `value`, `step`, `min`, `max`, `placeholder`, `label`, `required`, `disabled`, `error`, `event`, `custom_class`. Tabular-nums and hidden spin buttons in CSS (#109)
  - **Form Validation Display** (`{% form_errors form=form %}` / `{% field_error field=form.email %}`) — Two tags for rendering Django form validation errors. `form_errors` renders non-field errors as a styled alert list. `field_error` renders inline per-field error messages. Both accept `custom_class`. ARIA `role="alert"` for accessibility (#110)

- **Confirmation Dialog** (`{% confirm_dialog message="Delete?" confirm_event="delete" %}`): Reusable yes/no modal pattern wrapping existing Modal conventions. Renders only when `open=True`. Supports `title`, `message`, `confirm_event`, `cancel_event`, `variant` (default/danger), `confirm_label`, `cancel_label`, `custom_class`. Danger variant highlights title and confirm button in destructive color. ARIA `alertdialog` role with `aria-modal`. Backdrop click dismisses. Template tag, Rust engine handler (`ConfirmDialogHandler`), CSS, and tests including XSS coverage (#75)
- **Popconfirm** (`{% popconfirm message="Delete this item?" confirm_event="delete" %}...{% endpopconfirm %}`): Inline confirmation popover that appears next to the trigger element — less disruptive than a modal. Block tag wraps any trigger content. Auto-positioned with `placement` (top/bottom/left/right). Supports `message`, `confirm_event`, `cancel_event`, `confirm_label`, `cancel_label`, `variant` (default/danger), `custom_class`, `id`. Client-side toggle/dismiss via inline JS. CSS arrows for each placement direction. Template tag, Rust engine handler (`PopconfirmHandler`), CSS, and tests including XSS coverage (#180)

### Added
- **Form Essentials (v1.5)**: 4 new form input components with Django template tags, Rust engine handlers, CSS, and tests (including XSS coverage):
  - **Slider / Range** (`{% slider name="price" min=0 max=100 value=50 %}`) — Horizontal slider with optional dual-handle range mode (`value_end`), configurable `step`, tick marks (`show_ticks`), value display output, `dj-input` event; supports `label`, `disabled`, `custom_class` (#82)
  - **Search Input** (`{% search_input name="q" placeholder="Search..." event="search" %}`) — Input with search icon, clear button, loading spinner state (`loading`), debounced `dj-input` event (`debounce` ms); supports `label`, `value`, `disabled`, `custom_class` (#83)
  - **Password Input** (`{% password_input name="pwd" %}`) — Input with show/hide toggle button, optional strength meter bar (`show_strength`, `strength` 0-4); supports `label`, `error`, `required`, `disabled`, `placeholder`, `custom_class` (#84)
  - **Autocomplete** (`{% autocomplete name="city" source_event="search_cities" %}`) — Input with dropdown suggestions fetched server-side on keystroke; `source_event` for server search, debounced input, `min_chars` threshold, suggestion list (dict/tuple/string), hidden value input, ARIA combobox/listbox roles; supports `label`, `error`, `required`, `loading`, `disabled`, `custom_class` (#85)

### Changed
- **CSS @layer adoption**: All component CSS (`components.css`, `components-classes.css`) is now wrapped in `@layer djust-components`, giving consumers explicit control over cascade precedence when overriding styles
- **Animation consistency**: Consolidated 17 scattered `@keyframes` declarations into 9 shared keyframes (`dj-spin`, `dj-pulse`, `dj-fade`, `dj-shimmer`, `dj-slide-in-right`, `dj-slide-in-up`, `dj-slide-out-up`, `dj-flash`, `dj-counter-roll`) defined once outside the layer; all components now reference these shared animations with consistent naming
- **RTL support via logical properties**: Replaced physical CSS properties (`padding-left`/`padding-right`, `margin-left`/`margin-right`, `border-left`/`border-right`, `text-align: left`, directional `border-radius`) with CSS logical property equivalents (`padding-inline-start`/`padding-inline-end`, `margin-inline-start`/`margin-inline-end`, `border-inline-start`/`border-inline-end`, `text-align: start`, `border-start-end-radius`, etc.) across all flow-relative contexts — components now render correctly in RTL layouts without additional CSS
- **Hardcoded transition durations**: Replaced remaining hardcoded `0.3s` and `0.2s` transition durations in accordion and collapsible icons with design token variables (`--duration-normal`, `--duration-fast`)

### Added
- **Page Header** (`{% page_header title="Products" subtitle="Manage inventory" %}{% page_header_actions %}...{% endpage_header_actions %}{% endpage_header %}`): Structured page-level header with title, optional subtitle, optional description, optional breadcrumb slot (direct child content), and right-aligned action buttons area via nested `{% page_header_actions %}` block tag. Responsive: actions stack below title on mobile (640px breakpoint). Template tags, Rust engine handlers (`PageHeaderHandler`, `PageHeaderActionsHandler`), CSS with flexbox layout, and tests including XSS coverage (#179)
- **Icon System** (`{% icon name="check" size="md" set="heroicons" %}`): Shared SVG icon rendering primitive with bundled Heroicons Outline set (60+ icons). Four size presets: xs (12px), sm (16px), md (20px), lg (24px). Extensible via `DJUST_COMPONENTS_ICON_SETS` Django setting for custom icon sets. Python helper `render_icon(name, size, ...)` for use in Rust handlers and component classes — eliminates inline SVG paths. Template tag, Rust handler, CSS size classes, and 34 tests including XSS coverage (#178)
- **Theme Toggle** (`{% theme_toggle current="system" event="set_theme" %}`): Light/dark/system mode switcher with sun/moon/monitor icons from the Icon System. Reads `prefers-color-scheme`, stores preference in `localStorage` under `djust-theme` key, applies `data-theme` attribute to `<html>`. Optional `dj-click` event for server-side persistence via `event` parameter. ARIA radiogroup with labeled buttons. Client-side JS with MutationObserver for LiveView compatibility, system theme media query listener. Template tag, Rust handler, CSS (inline-flex button group with active state), JS, and 24 tests including XSS coverage (#138)

- **Utility Components**: 5 new utility components with Django template tags, Rust engine handlers, Python component classes, client-side JS, CSS, and tests (including XSS coverage):
  - **Scroll to Top** (`{% scroll_to_top threshold="300px" %}`) — Floating button appearing after scroll threshold, smooth-scrolls to top on click; supports `threshold`, `label`, `custom_class`; client-side only (#125)
  - **Code Snippet** (`{% code_snippet language="bash" code="pip install djust" %}`) — Code block with language badge and copy-to-clipboard button; supports `code`, `language`, `custom_class`; client-side JS for clipboard API (#139)
  - **Responsive Image** (`{% responsive_image src=url alt="..." aspect_ratio="16/9" lazy=True %}`) — Picture element with `srcset`, `sizes`, native lazy loading, blur-up placeholder transition; supports `src`, `alt`, `aspect_ratio`, `lazy`, `srcset`, `sizes`, `placeholder`, `custom_class` (#140)
  - **Relative Time** (`{% relative_time datetime=created_at auto_update=True %}`) — Displays datetime as "3 hours ago" with client-side auto-update interval; supports `datetime` (string or object), `auto_update`, `interval`, `custom_class` (#146)
  - **Copyable Text** (`{% copyable_text %}your-api-key{% endcopyable_text %}`) — Inline click-to-copy with "Copied!" tooltip feedback; supports `copied_label`, `custom_class`; block tag with content (#153)
- **Component Classes**: 5 new Python component classes — `ScrollToTop`, `CodeSnippet`, `ResponsiveImage`, `RelativeTime`, `CopyableText`
- **Client-side JS**: 5 new JS modules — `scroll-to-top.js`, `code-snippet.js`, `responsive-image.js`, `relative-time.js`, `copyable-text.js`; all with MutationObserver for LiveView compatibility
- **CSS**: Styles for scroll-to-top (fixed positioning, visibility transition), code snippet (header with language badge and copy button, monospace code block), responsive image (aspect-ratio container, blur-up placeholder transition), relative time (tabular-nums), copyable text (inline monospace with hover state and tooltip)

- **WebSocket-Powered Components**: 4 new real-time components with Django template tags, Rust engine handlers, Python component classes, client-side JS, CSS, and tests (including XSS coverage):
  - **Streaming Text** (`{% streaming_text stream_event="stream_chunk" %}`) — Renders text arriving incrementally via WebSocket with typing cursor animation; supports `stream_event`, `text`, `markdown`, `auto_scroll`, `cursor`, `custom_class`; auto-scrolls on new content; client-side JS listener for `djust:<event>` events
  - **Connection Status Bar** (`{% connection_status %}`) — Slim fixed-top bar showing WebSocket state: hidden when connected, yellow "Reconnecting..." when disconnected, green "Reconnected" flash on recovery; hooks into djust client.js `djust:disconnected`/`djust:reconnected` lifecycle events; supports `reconnecting_text`, `connected_text`, `custom_class`
  - **Live Counter** (`{% live_counter value=42 label="online" stream_event="counter_update" %}`) — Animated counter updating in real-time via WebSocket push with number roll animation on change; supports `value`, `label`, `stream_event`, `size` (sm/md/lg), `custom_class`
  - **Server Event Toast** (`{% server_toast_container position="top-right" %}` + `self.push_toast("Saved!", type="success")`) — Python `ServerEventToastMixin` for LiveViews that sends `__toast__` events via WebSocket; client-side JS auto-renders toast notifications with auto-dismiss, dismiss button, slide-in/out animations; supports `position` (top-right/top-left/bottom-right/bottom-left/top-center/bottom-center), `max_toasts`, `custom_class`; toast types: info/success/warning/error
- **Component Classes**: 3 new Python component classes — `StreamingText`, `ConnectionStatus`, `LiveCounter`; plus `ServerEventToastMixin` for LiveViews
- **Client-side JS**: 4 new JS modules — `streaming-text.js`, `connection-status.js`, `live-counter.js`, `toast-container.js`; all with MutationObserver for LiveView compatibility
- **CSS**: Styles for streaming text (cursor animation, auto-scroll container), connection status bar (reconnecting/connected states, flash animation), live counter (size variants, roll animation, tabular-nums), toast container (6 position variants, toast type colors, slide-in/out animations)

- **Rich Select** (`{% rich_select name="assignee" options=opts %}`): Select dropdown where each option can include icons, images, descriptions, or badges alongside the label; selected value shows the rich display; supports `searchable` filter, `disabled` state, `label`, custom `event`, hidden input for form submission, ARIA roles (`combobox`, `listbox`, `option`); template tag, Rust handler, Python component class (`RichSelect`), CSS, and tests with XSS coverage
- **Data Grid** (`{% data_grid columns=cols rows=rows %}`): Editable spreadsheet-like grid with cell-level editing, column resize, frozen left/right columns, keyboard navigation (arrow keys, Enter/F2 to edit, Tab to advance, Escape to cancel), striped/compact modes, Add Row and Delete Row actions; distinct from Data Table (grid is for editing, table is for display); template tag, Rust handler, Python component class (`DataGrid`), client-side JS (`data-grid.js`), CSS, and tests with XSS coverage

- **Overlay/Feedback Components**: 2 new components with Django template tags, Rust engine handlers, CSS, and tests (including XSS coverage):
  - **Loading Overlay** (`{% loading_overlay active=is_loading %}...{% endloading_overlay %}`) — Semi-transparent overlay with centered spinner that blocks interaction; supports `active`, `text`, `spinner_size` (sm/md/lg), `custom_class`
  - **Announcement Bar** (`{% announcement_bar type="info" dismissible=True %}...{% endannouncement_bar %}`) — Full-width sticky top bar for site-wide announcements; supports `type` (info/success/warning/danger), `dismissible`, `dismiss_event`, `custom_class`; uses `dj-click` for dismissal

- **Status/Progress Indicators**: 4 new components with Django template tags, Rust engine handlers, component classes, CSS, and 74 tests (including XSS coverage):
  - **Notification Badge** (`{% notification_badge count=5 %}`) — Small count badge for icons/buttons with dot-only mode, max count overflow (99+), pulse animation; supports `count`, `max`, `dot`, `pulse`, `size`, `custom_class`
  - **Segmented Progress** (`{% segmented_progress steps=steps current=2 %}`) — Multi-step progress bar with labeled segments, numbered indicators, and connector lines; supports string or dict steps, `current`, `size`, `custom_class`
  - **Progress Circle** (`{% progress_circle value=65 size="md" %}`) — SVG circular progress indicator with stroke-dasharray animation, percentage text, ARIA progressbar role; supports `value`, `size` (sm/md/lg), `color` (primary/success/warning/danger), `show_value`, `custom_class`
  - **Status Indicator** (`{% status_indicator status="online" label="API" %}`) — Colored dot with optional label and pulse animation; maps online=green, degraded=yellow, offline=red, maintenance=blue; supports `status`, `label`, `pulse`, `size`, `custom_class`

- **Display/Layout Primitives**: 5 new components with Django template tags, CSS, and full test + XSS coverage:
  - **Scroll Area** (`{% scroll_area %}...{% endscroll_area %}`) — Custom-styled scrollbar container with `max_height` prop, CSS custom properties for thumb/track colors, and thin-scrollbar support; `max_height`, `custom_class`
  - **Callout / Blockquote** (`{% callout %}...{% endcallout %}`) — Styled content block with colored left border, icon, and title; type variants (info/warning/danger/success) with auto-icons; `type`, `title`, `icon`, `custom_class`
  - **Aspect Ratio** (`{% aspect_ratio %}...{% endaspect_ratio %}`) — CSS `aspect-ratio` container for responsive media; `ratio` (e.g. "16/9", "4/3", "1/1"), `custom_class`
  - **Description List** (`{% description_list items=items %}`) — Key-value display with vertical/horizontal layout modes using `<dl>`/`<dt>`/`<dd>` semantics; `items` (list of `{term, detail}` dicts), `layout`, `custom_class`
  - **Sticky Header** (`{% sticky_header %}...{% endsticky_header %}`) — `position: sticky` container with configurable top offset, z-index, and shadow-on-scroll CSS class; `offset`, `z_index`, `custom_class`

- **Button & Control Variants**: 3 new components with Django template tags, Rust engine handlers, CSS, and full test + XSS coverage:
  - **Toggle Group** (`{% toggle_group %}`) — Segmented button group with single/multi select mode, icon support, size variants, ARIA pressed state; supports `name`, `options`, `value`, `event`, `mode`, `disabled`, `size`
  - **Floating Action Button** (`{% fab %}`) — Fixed-position FAB with optional speed-dial sub-actions, position variants (4 corners), size/variant/disabled support; supports `icon`, `event`, `position`, `label`, `size`, `variant`, `disabled`, `actions`
  - **Split Button** (`{% split_button %}`) — Primary action + dropdown for secondary actions with loading spinner, open/closed menu state, variant/size support; supports `label`, `event`, `options`, `variant`, `size`, `disabled`, `loading`, `open`, `toggle_event`

- **Form Input Components**: 7 new form-related components with Django template tags, Rust engine handlers, CSS, and 94 tests (including XSS escaping coverage):
  - **Multi-select** (`{% multi_select %}`) — Checkbox list with client-side search filtering and tag output for selected values; supports `options`, `selected`, `event`, `placeholder`, `disabled`
  - **OTP Input** (`{% otp_input %}`) — One-time-code input with individual digit boxes (4/6/custom), hidden input for form submission, `inputmode="numeric"`; supports `digits`, `event`, `label`, `disabled`
  - **Number Stepper** (`{% number_stepper %}`) — +/- numeric input with min/max/step constraints; emits `dj-click` for buttons and `dj-change` for direct input; supports `value`, `min_val`, `max_val`, `step`, `label`, `disabled`
  - **Tag Input** (`{% tag_input %}`) — Input creating dismissible tags with hidden inputs for form submission and datalist suggestions; supports `tags`, `suggestions`, `event`, `placeholder`, `label`, `disabled`
  - **Input Group** (`{% input_group %}...{% endinput_group %}`) — Block wrapper combining prefix/suffix addons with form inputs; supports `size` (sm/md/lg), `error`
  - **Input Addon** (`{% input_addon %}...{% endinput_addon %}`) — Prefix/suffix addon for use inside input groups; supports `position` (prefix/suffix)
  - **Label** (`{% dj_label %}...{% enddj_label %}`) — Accessible form label with `for`, `required` (asterisk indicator), and `class` support
  - **Fieldset** (`{% fieldset %}...{% endfieldset %}`) — Styled fieldset with legend, disabled state, and custom class support

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
