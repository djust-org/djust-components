# CSS Batch 1 — Simple Inline Components Plan

## Components to Style

### 1. Kbd (#38)
- **Classes**: `.kbd-group`, `.kbd`, `.kbd-sep`
- **HTML**: `<span class="kbd-group"><kbd class="kbd">Ctrl</kbd><span class="kbd-sep">+</span><kbd class="kbd">K</kbd></span>`
- **Style**: Inline monospace keys with subtle border/background, separator styled as muted text

### 2. Copy Button (#37)
- **Classes**: `.copy-btn` (on top of `.btn .btn-{variant} .btn-{size}`)
- **HTML**: `<button class="btn btn-outline btn-sm copy-btn" ...>Copy</button>`
- **Style**: Mostly inherits from `.btn`; add copy-btn specific icon/feedback styles

### 3. Rating (#36)
- **Classes**: `.rating`, `.rating-star`, `.rating-star-full`, `.rating-star-half`, `.rating-star-empty`, `.rating-sm`, `.rating-lg`
- **HTML**: `<div class="rating"><span/button class="rating-star rating-star-full">...</span/button></div>`
- **Style**: Inline-flex star display, gold/muted colors, hover effects for interactive, size variants

### 4. Code Block (#34)
- **Classes**: `.code-block`, `.code-block-header`, `.code-block-filename`, `.code-block-lang`, `.code-block-copy`, `.code-block-pre`
- **HTML**: Container with header (filename, language badge, copy button) + `<pre><code>` block
- **Style**: Dark card background, monospace, header with border-bottom, copy button positioned right
- **Note**: Two rules already exist for highlight.js integration; extend from there

### 5. Collapsible (#39)
- **Classes**: `.collapsible`, `.collapsible-open`, `.collapsible-trigger`, `.collapsible-label`, `.collapsible-icon`, `.collapsible-content`
- **HTML**: Wrapper div with button trigger and content div; `.collapsible-open` toggles visibility
- **Style**: Trigger as full-width button, icon rotates on open, content hidden by default, shown when `.collapsible-open`

## Design Conventions (from existing CSS)
- Colors: `hsl(var(--token))` or `hsl(var(--token) / opacity)`
- Spacing: `var(--space-N)`
- Radii: `var(--radius-sm|md|lg|xl|full)`
- Typography: `var(--text-xs|sm|base|lg)`, `var(--font-medium|semibold|bold)`
- Transitions: `var(--duration-fast|normal)`
- Shadows: `var(--shadow-sm|md|lg)`
- No dark mode media queries — theme tokens handle both modes automatically
- No `@layer` — flat CSS
- One-line rules (minified style)

## Test Plan
- Add tests in `tests/test_rust_handlers.py` that verify CSS class names appear in rendered HTML for each component
- Follow existing pattern: import handler, call `.render()`, assert class names in result

## Files to Change
1. `src/djust_components/static/djust_components/components.css` — add styles
2. `tests/test_rust_handlers.py` — add CSS class tests
3. `CHANGELOG.md` — update [Unreleased]
