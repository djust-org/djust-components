## Why

djust's `LiveComponent` provides stateful, interactive components but requires too much ceremony: untyped `kwargs.get()` for state, manual `trigger_update()` calls, string-keyed instance IDs prone to typos, and mixin inheritance gymnastics when composing multiple components. Developers need typed, declarative component attributes that work like Django model fields — `faq = Accordion(active="q1")` — with IDE autocomplete, automatic event routing, and render caching.

## What Changes

- **Evolve LiveComponent** to support Python descriptor protocol (`__set_name__`, `__get__`, `__set__`) so components can be declared as typed class attributes on LiveViews
- **Add TypedState inner class** pattern replacing untyped `kwargs.get()` with typed, IDE-friendly state: `class State(TypedState): active: str = ""`
- **Auto-register event handlers** via `__set_name__` — no mixin inheritance needed, attribute name IS the component ID
- **Add render caching** via dirty flags on TypedState — skip `.render()` for unchanged components
- **Add dependency tracking** using existing `extract_template_variables()` Rust FFI to know which components a template references
- **Add client/server tier system** — components declare whether state changes are server (full round-trip), optimistic (instant client + server confirm), or client-only (pure JS, no server)
- **Deprecate DEP-001 mixins** — AccordionMixin, TabsMixin, etc. replaced by descriptor-based components
- **BREAKING**: LiveComponent API changes — `mount(**kwargs)` replaced by `State` inner class with typed defaults

## Capabilities

### New Capabilities
- `component-descriptors`: Descriptor protocol for LiveComponent — `__set_name__`, `__get__`, `__set__`, auto-registration, rehydration after serialization
- `typed-component-state`: TypedState inner class pattern for type-safe, IDE-friendly component state that serializes as plain dicts
- `render-caching`: Dirty flag tracking on TypedState mutations, skip render for clean components, HTML cache by state hash
- `dependency-tracking`: Template variable extraction cross-referenced with component descriptors to determine which components need re-rendering
- `client-server-tiers`: Three-tier system (server/optimistic/client) with declarative rules for client-side DOM manipulation
- `auto-event-routing`: Event handlers auto-registered by descriptors, routed by attribute name, single-instance auto-resolution

### Modified Capabilities

## Impact

- **djust core** (`LiveComponent`, `_sync_state_to_rust`, `get_context_data`): Descriptor support, TypedState integration, render caching hooks
- **djust-components**: All 8 DEP-001 mixins deprecated, replaced by descriptor-based component classes
- **Client JS** (`client.js`): Optimistic tier rule interpreter for instant DOM updates
- **Templates**: `{{ faq.active }}` works automatically (TypedState is a dict); future `{% component %}` tag
- **Gallery**: Per-category views refactored from mixin composition to descriptor declaration
- **Rust VDOM** (future P3): Component boundary markers for subtree-scoped diffing
