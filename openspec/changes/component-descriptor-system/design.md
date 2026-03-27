## Context

djust is a Phoenix LiveView-style reactive framework for Django. The server re-renders templates on every state change, Rust VDOM tree-diffs produce minimal patches, and the client applies patches via WebSocket. LiveComponent exists as a stateful component base class with event handlers and templates, but requires manual state wiring, untyped kwargs, and string-keyed instance routing.

DEP-001 introduced per-component mixins (AccordionMixin, TabsMixin, etc.) with TypedState — dict subclasses with typed property access. Testing revealed that mixins still require too much ceremony and string-based routing is error-prone. This design evolves LiveComponent into a descriptor-based system that eliminates those issues.

**Key constraints:**
- All state MUST be JSON-serializable (djust syncs state to Rust as JSON)
- Underscore-prefixed attributes are excluded from djust's context pipeline
- `normalize_django_value()` converts dicts recursively but falls back to `str()` for unknown types
- `extract_template_variables()` (Rust FFI) returns `{var: [attr_paths]}` from template content
- Components render to HTML strings before Rust sees them (`{"render": "<html>"}`)

## Goals / Non-Goals

**Goals:**
- Typed, declarative component attributes: `faq = Accordion(active="q1")`
- IDE autocomplete for component state: `self.faq.active` (str)
- Automatic event handler registration — no mixin inheritance needed
- Render caching — skip `.render()` for unchanged components
- Dependency tracking — know which components a template references
- Client/server tier system — instant UI for predictable toggles
- Backward compatibility with existing LiveComponent subclasses during transition

**Non-Goals:**
- Component-level VDOM subtree diffing (P3 — requires Rust core changes)
- Client-side component framework (no React/Solid equivalent)
- Component marketplace or registry system
- Visual component editor

## Decisions

### Decision 1: Evolve LiveComponent, not parallel system

**Choice:** Add descriptor protocol to LiveComponent rather than creating a new ComponentDescriptor class.

**Rationale:** LiveComponent already has state management, event handlers, templates, parent communication (`send_parent`), and lifecycle hooks. Building a parallel system would duplicate all of this. Since LiveComponent is not widely used yet, we can reshape it directly.

**Alternative considered:** Separate `ComponentDescriptor` class that wraps LiveComponent. Rejected because it adds an unnecessary layer of indirection.

### Decision 2: TypedState inner class for state declaration

**Choice:** Each component declares state as `class State(TypedState): active: str = ""`.

**Rationale:** TypedState is a dict subclass — serializes through djust's pipeline without changes. Properties auto-generated via `__init_subclass__` give IDE autocomplete. Inner class keeps state schema co-located with the component.

**Alternative considered:** Dataclasses with `to_dict()`/`from_dict()`. Rejected because djust's serialization pipeline expects dicts, and adding custom serialization hooks would require framework changes.

### Decision 3: Descriptor storage key uses underscore prefix

**Choice:** `obj.__dict__["_component_faq"]` stores the state, while `self.faq` (via `__get__`) returns it to the context pipeline.

**Rationale:** The underscore-prefixed storage key prevents djust from double-including the state in template context. The descriptor's `__get__` provides the public access path that IS included in context.

### Decision 4: Single event handler per component type, routed by component_id

**Choice:** Two Accordions share one `accordion_toggle` handler. The `component_id` parameter (= attribute name) routes to the correct instance.

**Rationale:** This matches how djust dispatches events (`getattr(view, event_name)`). One method per event name is simpler than per-instance methods. Auto-resolution for single-instance cases (empty component_id → sole instance) reduces template boilerplate.

**Alternative considered:** Per-instance event names (e.g., `faq_toggle`, `settings_acc_toggle`). Rejected because it requires unique template bindings per instance and complicates the template tag API.

### Decision 5: Three-tier client/server boundary

**Choice:** Components declare tier per state key: `server`, `optimistic`, or `client`.

**Rationale:**
- `server`: Full round-trip. Required for data mutations, permissions.
- `optimistic`: Client applies DOM change instantly via declarative rule, server confirms via VDOM diff. Self-correcting — no rollback code needed.
- `client`: Pure dj-hook JS. Server never knows. For transient state (tooltip hover, dropdown open).

**Alternative considered:** Binary server/client split. Rejected because optimistic is the sweet spot for most interactive components — instant feel with server truth.

### Decision 6: Render caching via dirty flag, not input hashing

**Choice:** TypedState sets `_dirty = True` on mutation. Render is skipped when clean.

**Rationale:** Flag-based tracking is O(1) on each state write. Hash-based would require hashing the entire state dict on each render cycle to check for changes. The flag approach integrates naturally with TypedState's `__setitem__`.

## Risks / Trade-offs

- **[Descriptor unfamiliarity]** → Mitigate with clear error messages, documentation, and migration guide. Django developers are used to model fields as descriptors even if they don't think of them that way.

- **[Rehydration after serialization]** → djust deserializes state as plain dicts. `__get__` must detect and convert back to TypedState on every access. Mitigate by caching the rehydrated object in `obj.__dict__`.

- **[Optimistic tier misprediction]** → Client applies wrong DOM change, VDOM diff corrects ~50-100ms later causing a flash. Mitigate by defaulting to `server` tier and documenting when `optimistic` is safe (deterministic state transitions only).

- **[Class-level descriptor mutation]** → `__set_name__` modifies the owner class by adding event handlers via `setattr`. This is unusual but matches Django's `contribute_to_class` pattern. Mitigate by respecting user-defined methods (skip registration if method already exists).

- **[Template variable extraction limitations]** → `extract_template_variables()` doesn't resolve `{% include %}` or dynamic template selection. Mitigate by building dep map from the full rendered template chain, or falling back to full re-render when includes are detected.

## Open Questions

1. Should `self.faq` return the State object directly, or should there be `self.faq.state` and `self.faq.meta` separation?
2. Should optimistic rules be declared on the component class or configurable per-instance?
3. How should `send_parent()` work with descriptors — does the parent view need to declare a handler, or is there a convention?
4. Should we support component composition (a component containing other components)?
5. Is full VDOM diff (<1ms) fast enough that subtree scoping (P3) is never needed?
