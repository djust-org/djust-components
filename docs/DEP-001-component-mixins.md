# DEP-001: Per-Component Interactive Mixins

**Status**: Accepted
**Created**: 2026-03-27
**PR**: feat-component-mixins

## Problem

Interactive djust components (accordions, tabs, modals, sheets, etc.) require manual state tracking in every LiveView that uses them. Developers duplicate the same patterns:

1. Declare state dicts (`accordion_states = {}`, `active_tabs = {}`)
2. Write event handlers (`accordion_toggle`, `set_tab`, `close_modal`)
3. Route events to the correct instance by ID
4. Expose state to templates

This is error-prone, repetitive, and makes it hard to compose multiple interactive components on a single page.

## Solution

Per-component mixins that encapsulate state management and event handling for each interactive component type. Mixins use an **instance registry pattern**: one mixin manages multiple instances of the same component type, routed by `component_id`.

### Usage

```python
class SettingsPage(AccordionMixin, TabsMixin, ModalMixin, LiveView):
    template_name = "settings.html"

    def mount(self, request, **kwargs):
        self.init_accordion("faq", active="q1")
        self.init_accordion("help")
        self.init_tabs("main", active="general")
        self.init_modal("confirm")
```

Event handlers are provided by the mixins. Template tags route events via `data-component-id`:

```html
{% accordion id="faq" active=faq.active event=faq.event component_id=faq.component_id %}
```

## Architecture: 4 Layers

### Layer 1: Per-Component Mixins (this PR)

Eight mixins covering the interactive component types:

| Mixin | Event handlers | State key |
|-------|---------------|-----------|
| AccordionMixin | `accordion_toggle` | `accordion_instances` |
| TabsMixin | `set_tab` | `tabs_instances` |
| ModalMixin | `open_modal`, `close_modal`, `toggle_modal` | `modal_instances` |
| CollapsibleMixin | `toggle_collapsible` | `collapsible_instances` |
| SheetMixin | `open_sheet`, `close_sheet` | `sheet_instances` |
| DropdownMixin | `toggle_dropdown`, `close_dropdown` | `dropdown_instances` |
| TooltipMixin | `show_tooltip`, `hide_tooltip` | `tooltip_instances` |
| CarouselMixin | `carousel_prev`, `carousel_next`, `carousel_go` | `carousel_instances` |

All mixins inherit from `ComponentMixin` base class but use direct attribute access internally to avoid MRO conflicts when composing multiple mixins.

### Layer 2: Optimistic UI via dj-hook (future)

For predictable toggles, a `dj-hook` applies DOM changes instantly before the server round-trip. The VDOM diff system handles correction on mismatch.

### Layer 3: Component Boundaries for Diff Skipping (future, requires djust core)

Mark component subtrees with input hashes. The Rust VDOM differ skips unchanged subtrees entirely.

### Layer 4: Unified Component API (future vision)

When all layers are in place, a single `init_accordion()` call handles state, events, serialization, optimistic UI, and diff skipping.

## Security Considerations

Mixin state dicts are visible in template context because underscore-prefixed attributes are excluded from djust's rendering pipeline. This is acceptable because:

- Mixin state contains only UI state (which item is open, which tab is active)
- Values are primitives (strings, bools, lists of strings) -- never sensitive data
- `component_id` values are escaped with `conditional_escape()` before HTML output

**Rule**: Never store application data or secrets in mixin state dicts.

## Migration

Fully backward-compatible and additive:

- Template tags accept an optional `component_id` parameter; when absent, behavior is unchanged
- Existing manual state tracking continues to work
- Mixins can be adopted incrementally, one component type at a time

## Verification

- 100 unit tests covering all mixins (init, toggle, routing, serialization, composition)
- 22 gallery LiveView tests validating the refactored CategoryGalleryView
- 3717 total tests passing with no regressions
- Template tag `component_id` tests with XSS escaping validation
