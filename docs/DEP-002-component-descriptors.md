# DEP-002: Component Descriptor System

**Status**: Draft
**Created**: 2026-03-27
**Supersedes**: DEP-001 Layer 4 ("Unified Component API")

---

## Motivation

DEP-001 delivered per-component interactive mixins with TypedState. They work but have ergonomic issues:

- **String-keyed instance IDs** (`"faq"`) are prone to typos and invisible to type checkers
- **Mixin inheritance gymnastics** — composing 5+ mixins causes MRO complexity
- **Manual boilerplate** — `init_*` in mount, `get_*_ctx` for templates, override handlers for re-rendering
- **State stored in nested dicts** — `self.accordion_instances["faq"]["active"]` is not Pythonic

The descriptor system replaces all of this with typed class attributes.

---

## The API

```python
class SettingsPage(LiveView):
    faq = Accordion(active="q1")
    settings_acc = Accordion()
    main_tabs = Tabs(active="general")
    confirm = Modal()

    @event_handler
    def save_settings(self, **kwargs):
        if self.main_tabs.active == "general":  # typed, IDE autocomplete works
            ...
```

No mixins in the inheritance chain. No `init_*` calls. No string keys. The attribute name **is** the component ID.

---

## 1. Descriptor Mechanics

### Current State

Mixins store state in `self.accordion_instances["faq"]` (a dict-of-TypedState). Event handlers use `component_id` string parameters to disambiguate instances. `get_context_data()` collects all non-underscore, non-callable attributes into the template context.

### Proposed Design

Each component type (`Accordion`, `Tabs`, `Modal`, etc.) is a Python **descriptor** with `__set_name__`, `__get__`, and `__set__`.

```python
class ComponentDescriptor:
    """Base descriptor for interactive UI components."""

    state_class = None  # Subclass sets: AccordionState, TabsState, etc.

    def __init__(self, **defaults):
        self._defaults = defaults
        self._attr_name = None
        self._storage_key = None

    def __set_name__(self, owner, name):
        self._attr_name = name
        self._storage_key = f"_component_{name}"

        # Class-level registry for introspection
        if not hasattr(owner, "_component_descriptors"):
            owner._component_descriptors = {}
        owner._component_descriptors[name] = self

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self  # Class-level access returns descriptor
        state = obj.__dict__.get(self._storage_key)
        if state is None:
            # First access — create with defaults
            state = self.state_class(**self._defaults)
            state["component_id"] = self._attr_name
            obj.__dict__[self._storage_key] = state
        elif not isinstance(state, self.state_class):
            # Rehydrate from plain dict after djust deserialization
            state = self.state_class.from_dict(state)
            state["component_id"] = self._attr_name
            obj.__dict__[self._storage_key] = state
        return state

    def __set__(self, obj, value):
        if isinstance(value, dict) and not isinstance(value, self.state_class):
            value = self.state_class.from_dict(value)
            value["component_id"] = self._attr_name
        obj.__dict__[self._storage_key] = value
```

Concrete descriptors:

```python
class Accordion(ComponentDescriptor):
    state_class = AccordionState
    default_event = "accordion_toggle"

class Tabs(ComponentDescriptor):
    state_class = TabsState
    default_event = "set_tab"

class Modal(ComponentDescriptor):
    state_class = ModalState
    default_event = "toggle_modal"
```

### Per-Instance State Isolation

State lives in `obj.__dict__["_component_faq"]` (underscore prefix = excluded from djust's context pipeline). The descriptor's `__get__` returns the TypedState through the public attribute name (`self.faq`), which IS included in context because `get_context_data()` sees it as a non-underscore attribute with a value.

Two view instances (two browser sessions) never share state — each has its own `__dict__`. Two descriptors on the same class use different storage keys.

### Serialization Survival

1. `get_context_data()` calls `__get__` on each descriptor → returns TypedState (dict subclass)
2. `normalize_django_value()` serializes it as a plain dict
3. Rust receives `{"faq": {"active": "q1", "multiple": false, "component_id": "faq"}}`
4. On next event, djust restores state into `obj.__dict__` as a plain dict
5. Next `__get__` call detects plain dict, rehydrates to TypedState via `from_dict()`

### Change Tracking

TypedState tracks mutations via a `_dirty` flag:

```python
class TypedState(dict):
    def __setitem__(self, key, value):
        old = self.get(key)
        super().__setitem__(key, value)
        if old != value:
            self._dirty = True
```

This integrates with djust's existing `_snapshot_assigns()` change detection — the `id()` of the TypedState object changes when state is mutated (because the dict contents change), triggering `_sync_state_to_rust()`.

### Constraints

- Python descriptors with `__get__` prevent simple assignment like `self.faq = {"active": "q2"}` from creating a plain dict. The `__set__` method handles dict-to-TypedState conversion.
- Descriptors are less familiar than mixins to some Django developers. Clear error messages and documentation are essential.

### Open Questions

- Should `_component_descriptors` use `__init_subclass__` instead of `__set_name__` mutation? `__set_name__` is simpler and handles inheritance.
- How to handle subclassing a view that already has descriptors? Python propagates descriptors through inheritance, so `class SpecialSettings(SettingsPage)` naturally inherits `faq`, etc.

---

## 2. Render Caching

### Current State

`_sync_state_to_rust()` calls `.render()` on every Component instance on every event, even if the component's inputs haven't changed. The Rust VDOM diff minimizes DOM patches, but the Python-side rendering work is repeated unnecessarily.

### Proposed Design: Three Layers

**Layer A — State-hash skip (Python, P2)**

Before syncing to Rust, check each component's `_dirty` flag. Clean components don't need their state re-sent — Rust already has the current values via `update_state()` merge semantics.

**Layer B — Subtree diff skip (Rust, P3)**

When Rust re-renders, compare incoming component state hash against previous. If identical, skip diffing that subtree entirely. Requires `data-dj-component` boundary markers in HTML.

**Layer C — HTML render cache (Python, P2)**

For components using `.render()` → HTML (the existing Component class, not descriptor state), cache the HTML keyed by a hash of the component's state dict:

```python
cache_key = hash(frozenset(state.items()))
if cache_key == state.get("_render_hash"):
    html = state["_cached_html"]  # skip render
else:
    html = component.render()
    state["_cached_html"] = html
    state["_render_hash"] = cache_key
```

### Cache Location

Instance-level (on the TypedState object). Per-session, never shared across users.

### Cache Invalidation

Explicit via `_dirty` flag. When `TypedState.__setitem__` fires, `_dirty = True` and `_render_hash` is cleared.

---

## 3. Template Integration

### {{ faq.active }} Works Automatically

TypedState subclasses `dict`. When `get_context_data()` returns `{"faq": {"active": "q1", ...}}`, Rust's template engine resolves `{{ faq.active }}` to `"q1"`. No special handling needed.

### component_id Injection

The descriptor injects `component_id` into the state dict (equal to the attribute name). Templates use it for event routing:

```html
{% accordion id="faq" active=faq.active
   event="accordion_toggle" component_id=faq.component_id %}
```

### Template Inspection via extract_template_variables()

djust's Rust FFI provides `extract_template_variables(template_str)` which returns `{var_name: [attr_paths]}`:

```python
# Template: {{ faq.active }} {{ main_tabs.active }} {{ items }}
result = extract_template_variables(template_str)
# {"faq": ["active"], "main_tabs": ["active"], "items": []}
```

Cross-referencing with `_component_descriptors` gives us the exact dependency graph: which declared components does the template actually use?

### Future: {% component faq %} Tag

A template tag that auto-injects event names, component_id, and wraps output in a `data-component-id` div:

```html
{% component faq %}
    {% accordion_item id="q1" title="Question 1" %}Answer{% endaccordion_item %}
{% endcomponent %}
```

Equivalent to:
```html
<div data-component-id="faq">
{% accordion id="faq" active=faq.active event="accordion_toggle" component_id="faq" %}
    {% accordion_item id="q1" title="Question 1" %}Answer{% endaccordion_item %}
{% endaccordion %}
</div>
```

---

## 4. Dependency Tracking

### Current State

`extract_template_variables()` exists and is used for JIT query optimization. No dependency tracking exists for UI component re-rendering.

### Proposed Design

**Build dependency map at mount:**

```python
def mount(self, request, **kwargs):
    ...
    template_content = self._get_template_content()
    self._template_deps = extract_template_variables(template_content)
    # {"faq": ["active"], "main_tabs": ["active"], "items": ["name", "price"]}
```

**After event, determine what changed:**

```python
changed_components = {
    name for name, desc in self._component_descriptors.items()
    if getattr(self, name).get("_dirty", True)
}
# {"faq"}  — only faq's state was mutated
```

**Selective state sync:**

Only send changed component state to Rust. Unchanged components retain previous values via Rust's `update_state()` merge semantics.

**Subtree-scoped diffing (future):**

If template uses `{% component faq %}` wrappers, Rust can diff only the subtree for changed components.

### Constraints

- Static analysis via `extract_template_variables` doesn't capture dynamic access (`{{ item.faq_ref }}`)
- `{% include %}` templates are invisible to the parent's variable extraction
- The dependency map should be computed once per mount (cached by template content hash)

---

## 5. Client vs Server Boundary

### The Fundamental Question

For each type of state change, where should it execute?

### Three Tiers

| Tier | Latency | Server knows? | Mechanism |
|------|---------|---------------|-----------|
| **server** | ~50-100ms | Yes | Full round-trip: event → handler → re-render → diff → patches |
| **optimistic** | Instant + confirm | Yes | Client applies DOM change immediately, server confirms via VDOM diff |
| **client** | Instant | No | Pure dj-hook JS, no server handler |

### Declaration

```python
class Accordion(ComponentDescriptor):
    state_class = AccordionState
    default_event = "accordion_toggle"

    class Meta:
        tier = {"active": "optimistic"}
        optimistic_rules = {
            "accordion_toggle": {
                "target": "[data-component-id='{component_id}'] .dj-accordion-item[data-value='{value}']",
                "action": "toggle_class",
                "class": "dj-accordion-item--open",
            }
        }
```

### Optimistic Tier Mechanism

1. Descriptor's optimistic rules are serialized to JSON and sent to client during mount
2. On click, client looks up event name in rules
3. Client interpolates `{component_id}` and `{value}` from event params
4. Client applies DOM change immediately (toggle class, toggle attribute)
5. Event still sent to server over WebSocket
6. Server processes normally, sends VDOM patches
7. If client prediction was wrong, patches correct the DOM automatically

No explicit rollback — the existing VDOM diff system handles corrections.

### Client Tier Mechanism

- Descriptor does NOT register a server-side event handler
- Component wrapper element gets `dj-hook="TooltipHook"`
- JS hook handles show/hide purely client-side
- `dj-update="ignore"` on wrapper prevents server re-renders from clobbering client state

### Default Tier Assignments

| Component | State | Tier | Rationale |
|-----------|-------|------|-----------|
| Accordion | active | optimistic | Predictable toggle |
| Tabs | active | optimistic | Predictable selection |
| Modal | is_open | optimistic | Predictable toggle |
| Collapsible | is_open | optimistic | Predictable toggle |
| Sheet | is_open | optimistic | Predictable toggle |
| Dropdown | is_open | client | Transient, closes on click-away |
| Tooltip | is_visible | client | Pure hover state |
| Carousel | active | server | Index math with wrapping |

Developers override per-instance: `filters = Dropdown(tier="server")`

### Constraints

- Optimistic rules must be deterministic. Conditional logic (permission checks) → use `tier="server"`
- Client tier state is invisible to server templates. `{% if dropdown.is_open %}` always sees initial value
- Optimistic adds client JS complexity (rule interpreter)

---

## 6. Event Handling

### Current State

`dj-click="accordion_toggle"` dispatches via `getattr(view, "accordion_toggle")`. Mixins provide the handler method via inheritance. `component_id` parameter disambiguates instances.

### Proposed Design

`__set_name__` auto-registers event handler methods on the owner class:

```python
def __set_name__(self, owner, name):
    ...
    # Register handler if not already defined
    handler_name = self.default_event  # e.g., "accordion_toggle"
    if not hasattr(owner, handler_name):
        setattr(owner, handler_name, self._make_handler())
```

The generated handler routes by `component_id`:

```python
def _make_handler(self):
    descriptor = self

    @event_handler
    def handler(view_self, value="", component_id="", **kwargs):
        # Resolve component_id
        if not component_id:
            # Auto-fallback: if one instance of this type, use it
            matches = [
                n for n, d in view_self._component_descriptors.items()
                if type(d) is type(descriptor)
            ]
            if len(matches) == 1:
                component_id = matches[0]
        if not component_id:
            return

        state = getattr(view_self, component_id)
        descriptor._apply_event(state, value=value, **kwargs)

    handler.__name__ = self.default_event
    return handler
```

### No Method Name Collisions

Two `Accordion` descriptors share the same `accordion_toggle` handler — correct because routing uses `component_id`. The second `__set_name__` sees `hasattr(owner, "accordion_toggle") == True` and skips.

### User Override Takes Precedence

If a developer defines `def accordion_toggle(self, ...)` on their view, the descriptor's `hasattr` check skips auto-registration. The developer's method runs instead.

---

## 7. Partial Rendering (Future)

### Current State

Every event triggers full template re-render → full VDOM diff → minimal patches. This is <1ms for typical pages but scales linearly with template complexity.

### Proposed Design: Component Islands

**Phase 1 — Boundary markers:**

`{% component faq %}` emits `<div data-component-id="faq">` wrapper. Full template still rendered.

**Phase 2 — Subtree-scoped diffing:**

When only `faq` changed, Rust locates `data-component-id="faq"` subtree in both old and new VDOM, diffs only that subtree.

**Phase 3 — Fragment rendering:**

Rust renders only the changed component's template fragment, not the full template. Requires component templates to be extractable as standalone units.

### Decision Tree

1. Non-component context changed? → Full render
2. Only component state changed? → Island render per changed component
3. Nothing changed? → Skip render entirely (existing `_skip_render` flag)

### Constraints

- Requires Rust VDOM differ changes (Phase 2+)
- Fragment templates cannot reference variables outside their component state
- May be premature — full VDOM diff is already <1ms for most pages

---

## Implementation Priority

| Priority | What | Effort | Depends On |
|----------|------|--------|------------|
| **P0** | Descriptors + Events + Templates | Medium | None |
| **P1** | Optimistic tier | High | P0 + client JS |
| **P2** | Dependency tracking | Medium | P0 |
| **P2** | Render caching (Layer C) | Low | None |
| **P2** | Client tier | Medium | P1 |
| **P3** | Partial rendering | Very High | djust core Rust |
| **P3** | Render caching (A, B) | High | P3 |

---

## Migration from DEP-001 Mixins

Fully additive — mixins continue to work unchanged. Per-component migration:

```python
# Before (DEP-001 mixins):
class MyPage(AccordionMixin, TabsMixin, LiveView):
    def mount(self, request, **kwargs):
        self.init_accordion("faq", active="q1")
        self.init_tabs("main", active="general")
        self.faq = self.get_accordion_ctx("faq")
        self.main_tabs = self.get_tabs_ctx("main")

# After (DEP-002 descriptors):
class MyPage(LiveView):
    faq = Accordion(active="q1")
    main_tabs = Tabs(active="general")
    # That's it. No mount code needed.
```

---

## Open Questions

1. Should tier be per-state-key or per-component?
2. Should `{% component faq %}` be a Rust handler or Django template tag?
3. How to handle `{% include %}` in dependency tracking?
4. Should descriptors use `__set_name__` class mutation or `__init_subclass__`?
5. How to prevent devs from using client-tier state in server-side template conditionals?
6. Is VDOM subtree diffing needed, or is full diff at <1ms fast enough?
7. Should the descriptor inject `event` name into the state dict, or rely on convention?
