# Button & Control Variants — Implementation Plan

## Components

### 1. Toggle Group (#61)
- **Tag**: `{% toggle_group name="view" options=opts value=current event="set_view" mode="single" %}`
- **Params**: `name`, `options` (list of `{value, label, icon?}`), `value` (selected), `event` (dj-click), `mode` ("single"|"multi"), `disabled`, `size` (sm/md/lg)
- **HTML**: `<div class="toggle-group">` with `<button class="toggle-group-btn toggle-group-btn--active">` per option
- **Rust handler**: `ToggleGroupHandler` — inline handler
- **Template tag**: `@register.simple_tag` `toggle_group()`
- **CSS**: `.toggle-group`, `.toggle-group-btn`, `--active`, size/disabled variants

### 2. Floating Action Button (#65)
- **Tag**: `{% fab icon="+" event="create" position="bottom-right" %}`
- **Params**: `icon`, `event` (dj-click), `position` (bottom-right/bottom-left/top-right/top-left), `label` (tooltip/a11y), `size` (sm/md/lg), `variant` (primary/secondary/danger/success), `disabled`, `actions` (list of `{icon, event, label}` for speed-dial)
- **HTML**: `<div class="fab-container fab-bottom-right"><button class="fab">...</button>` + optional speed-dial `<div class="fab-actions">` with sub-buttons
- **Rust handler**: `FabHandler` — inline handler
- **Template tag**: `@register.simple_tag` `fab()`
- **CSS**: `.fab-container`, `.fab`, `.fab-actions`, `.fab-action`, position classes, size/variant

### 3. Split Button (#133)
- **Tag**: `{% split_button label="Save" event="save" options=secondary_actions %}`
- **Params**: `label`, `event` (primary dj-click), `options` (list of `{label, event}`), `variant` (primary/secondary/danger/success), `size` (sm/md/lg), `disabled`, `loading`, `open` (dropdown open), `toggle_event` (for dropdown)
- **HTML**: `<div class="split-btn"><button class="split-btn-primary" dj-click="...">Label</button><button class="split-btn-toggle" dj-click="toggle_event">▾</button><div class="split-btn-menu" data-open="...">` with `<button class="split-btn-option">` per option
- **Rust handler**: `SplitButtonHandler` — inline handler
- **Template tag**: `@register.simple_tag` `split_button()`
- **CSS**: `.split-btn`, `.split-btn-primary`, `.split-btn-toggle`, `.split-btn-menu`, `.split-btn-option`, variant/size/disabled/loading

## Files Changed

1. `src/djust_components/rust_handlers.py` — Add 3 handler classes + register in INLINE_HANDLERS
2. `src/djust_components/templatetags/djust_components.py` — Add 3 `@register.simple_tag` functions
3. `src/djust_components/static/djust_components/components.css` — Add CSS for all 3
4. `tests/test_button_control_variants.py` — New test file with rendering + XSS tests
5. `CHANGELOG.md` — Update [Unreleased] section

## Security
- All user-controlled values (`name`, `label`, `icon`, `event`, option labels/values/events, `position`, `variant`, `size`) use `conditional_escape()` before interpolation into HTML.
- XSS tests cover script injection and attribute injection payloads for every user-controlled parameter.
