# DEP-002: Component Descriptor System

**Status**: Implemented
**Created**: 2026-03-27
**Implemented**: 2026-03-27
**Builds on**: djust's existing `LiveComponent` (components/base.py)
**Supersedes**: DEP-001 mixins (deprecated)

### Implementation Notes

- All 8 component classes implemented in `src/djust_components/descriptors/`
- `LiveComponent` descriptor protocol (`__set_name__`, `__get__`, `__set__`) implemented in djust core (`djust/python/djust/components/base.py`)
- TypedState dirty tracking and render caching attributes (`_dirty`, `_cached_html`, `_render_hash`) implemented in `mixins/base.py`
- Gallery views refactored from mixin-based to descriptor-based (no more `AccordionMixin` in class bases)
- DEP-001 mixins marked deprecated with docstring notices; remain functional
- Client-tier WebSocket skip (7.4) and `dj-update="ignore"` (7.5) deferred to future djust core JS changes (TODOs in Dropdown/Tooltip Meta)
- Open question resolved: `self.faq.active` pattern chosen over `self.state.active` (attribute name IS the component identity)
- Tier is per-component (declared on Meta), not per-state-key

---

## Motivation

djust already has `LiveComponent` — a stateful component base class with event handlers, templates, lifecycle hooks, and parent communication. It works, but the developer experience has friction:

```python
# Current LiveComponent usage — too much ceremony
class AlertComponent(LiveComponent):
    def mount(self, **kwargs):
        self.message = kwargs.get("message", "")   # no type safety
        self.type = kwargs.get("type", "info")       # kwargs.get everywhere
        self.dismissible = kwargs.get("dismissible", True)
        self.visible = kwargs.get("visible", True)

    def dismiss(self):
        self.visible = False
        self.trigger_update()                        # manual update trigger

    def render(self) -> str:
        if not self.visible:
            return ""
        return mark_safe(self._render_bootstrap())   # manual render
```

DEP-002 evolves LiveComponent with typed state, descriptor-based declaration, render caching, and a client/server tier system.

---

## The API

```python
# Defining a component
class Accordion(LiveComponent):
    class State(TypedState):
        active: str = ""
        multiple: bool = False

    class Meta:
        event = "accordion_toggle"
        tier = "optimistic"
        optimistic_rule = {
            "action": "toggle_class",
            "target": ".dj-accordion-item[data-value='{value}']",
            "class": "dj-accordion-item--open",
        }

    def toggle(self, value="", **kwargs):
        if self.state.multiple:
            if value in self.state.active:
                self.state.active.remove(value)
            else:
                self.state.active.append(value)
        else:
            self.state.active = "" if self.state.active == value else value


# Using components — declared as class attributes
class SettingsPage(LiveView):
    faq = Accordion(active="q1")
    settings_acc = Accordion()
    main_tabs = Tabs(active="general")
    confirm = Modal()

    @event_handler
    def save_settings(self, **kwargs):
        if self.main_tabs.active == "general":  # typed, autocomplete works
            ...
```

No mixins. No `init_*` calls. No string keys. The attribute name IS the component ID.

---

## 1. LiveComponent Evolution

### What Changes

| Aspect | Current LiveComponent | DEP-002 LiveComponent |
|--------|----------------------|----------------------|
| State declaration | `self.x = kwargs.get("x")` in mount | `class State(TypedState): x: str = ""` |
| State access | `self.message` (untyped) | `self.state.active` (typed, autocomplete) |
| Instance identity | String `component_id` param | Attribute name via descriptor `__set_name__` |
| Event routing | Manual `component_id` lookup | Automatic via `_component_descriptors` registry |
| Render caching | None — renders every time | Dirty flag on State, skip render if clean |
| Update trigger | Manual `self.trigger_update()` | Automatic — State mutation sets dirty flag |
| Client behavior | All server | Three tiers: server, optimistic, client |
| Declaration | Created in `mount()` | Class-level attribute (descriptor) |

### What Stays

- `mount()` / `unmount()` lifecycle hooks (optional, for components that need setup)
- `send_parent()` for child → parent communication
- `render()` method (override for custom rendering)
- Template-based rendering (`template` or `template_name`)
- Integration with djust's VDOM diffing pipeline

### LiveComponent as Descriptor

LiveComponent gains `__set_name__`, `__get__`, `__set__` to work as a class attribute:

```python
class LiveComponent:
    # ... existing methods ...

    def __set_name__(self, owner, name):
        self._attr_name = name
        self._storage_key = f"_component_{name}"

        if not hasattr(owner, "_component_descriptors"):
            owner._component_descriptors = {}
        owner._component_descriptors[name] = self

        # Auto-register event handler on the owner class
        event_name = getattr(self.Meta, "event", None)
        if event_name and not hasattr(owner, event_name):
            setattr(owner, event_name, self._make_event_handler())

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        state = obj.__dict__.get(self._storage_key)
        if state is None:
            state = self.State(**self._defaults)
            state["component_id"] = self._attr_name
            obj.__dict__[self._storage_key] = state
        elif isinstance(state, dict) and not isinstance(state, self.State):
            state = self.State.from_dict(state)
            state["component_id"] = self._attr_name
            obj.__dict__[self._storage_key] = state
        return state

    def __set__(self, obj, value):
        if isinstance(value, dict) and not isinstance(value, self.State):
            value = self.State.from_dict(value)
            value["component_id"] = self._attr_name
        obj.__dict__[self._storage_key] = value
```

### Typed State via Inner Class

Each component defines its state schema as an inner `State` class:

```python
class Modal(LiveComponent):
    class State(TypedState):
        is_open: bool = False

    class Meta:
        event = "toggle_modal"
        tier = "optimistic"

    def toggle(self, **kwargs):
        self.state.is_open = not self.state.is_open

    def open(self, **kwargs):
        self.state.is_open = True

    def close(self, **kwargs):
        self.state.is_open = False
```

`TypedState` is a dict subclass with typed properties (already built in DEP-001). IDE autocomplete works on `self.state.is_open`. The dict nature ensures JSON serialization through djust's pipeline.

---

## 2. Render Caching

### How Components Render Today

`_sync_state_to_rust()` calls `.render()` on every Component/LiveComponent on every event. The HTML string is sent to Rust as `{"render": "<html>"}`. Rust's VDOM diff minimizes DOM patches, but the Python `.render()` call is repeated even when the component's state hasn't changed.

### Dirty Flag Caching

TypedState's `__setitem__` sets `_dirty = True` on mutation. Before rendering:

```python
# In _sync_state_to_rust or get_context_data:
if not state._dirty and hasattr(state, "_cached_html"):
    html = state._cached_html  # skip render
else:
    html = component.render(state)
    state._cached_html = html
    state._dirty = False
```

### When to Invalidate

- Any `state.xxx = value` that changes the value → `_dirty = True`
- `_cached_html` cleared when dirty
- On next render cycle, re-renders only dirty components

---

## 3. Template Integration

### State in Templates

Since State is a dict subclass, `{{ faq.active }}` resolves automatically:

```html
{# faq is a dict: {"active": "q1", "multiple": false, "component_id": "faq"} #}
{% accordion id="faq" active=faq.active component_id=faq.component_id %}
    {% accordion_item id="q1" title="Q1" %}Answer{% endaccordion_item %}
{% endaccordion %}
```

### Template Inspection

`extract_template_variables(template_str)` (existing Rust FFI) returns which variables a template uses:

```python
# {"faq": ["active", "component_id"], "main_tabs": ["active"], "items": ["name"]}
```

Cross-referencing with `_component_descriptors` gives the dependency graph: which components does this template actually reference? Components not referenced don't need state synced to Rust.

### Future: {% component %} Tag

```html
{% component faq %}
    {% accordion_item id="q1" title="Q1" %}Answer{% endaccordion_item %}
{% endcomponent %}
```

Auto-injects: wrapper `<div data-component-id="faq">`, event names, component_id, active state. Reduces template boilerplate.

---

## 4. Dependency Tracking

### Build Dep Map at Mount

```python
template_deps = extract_template_variables(template_content)
component_names = set(cls._component_descriptors.keys())
# Components used by template = intersection
```

### After Event: What Changed?

```python
# Event handler mutated faq.state.active
# faq.state._dirty = True, main_tabs.state._dirty = False
# Only re-render faq, skip main_tabs
```

### Enables Future Optimizations

- **Selective state sync**: only send dirty component state to Rust
- **Subtree-scoped diffing**: Rust diffs only `data-component-id="faq"` subtree
- **Fragment rendering**: Rust renders only changed component's template section

---

## 5. Client vs Server Boundary

### Three Tiers

| Tier | Latency | Server knows? | When to use |
|------|---------|---------------|-------------|
| **server** | ~50-100ms | Yes | Data mutations, permissions, business logic |
| **optimistic** | Instant + confirm | Yes | Predictable UI toggles (accordion, tabs, modal) |
| **client** | Instant | No | Transient state (tooltip hover, dropdown open) |

### Declaration

```python
class Accordion(LiveComponent):
    class Meta:
        tier = "optimistic"
        optimistic_rule = {
            "action": "toggle_class",
            "target": ".dj-accordion-item[data-value='{value}']",
            "class": "dj-accordion-item--open",
        }
```

### Optimistic Mechanism

1. Component's `optimistic_rule` serialized to JSON, sent to client during mount
2. On click, client applies DOM change immediately per the rule
3. Event still sent to server over WebSocket
4. Server processes, sends VDOM patches
5. If prediction was wrong, patches auto-correct — no rollback code needed

### Client Mechanism

- No server event handler registered
- Component wrapper gets `dj-hook="TooltipHook"` for client-side JS
- `dj-update="ignore"` prevents server re-renders from clobbering client state

### Default Assignments

| Component | Tier | Rationale |
|-----------|------|-----------|
| Accordion | optimistic | Predictable toggle |
| Tabs | optimistic | Predictable selection |
| Modal | optimistic | Predictable toggle |
| Collapsible | optimistic | Predictable toggle |
| Sheet | optimistic | Predictable toggle |
| Dropdown | client | Transient, closes on click-away |
| Tooltip | client | Pure hover state |
| Carousel | server | Index arithmetic with wrapping |

Override per-instance: `filters = Dropdown(tier="server")`

---

## 6. Event Handling

### Auto-Registration

`__set_name__` registers the event handler on the view class:

```python
# Two accordions on one page:
class MyPage(LiveView):
    faq = Accordion(active="q1")
    settings_acc = Accordion()
    # Both share "accordion_toggle" handler — routed by component_id
```

The handler routes by `component_id` → finds the right descriptor by attribute name → calls the component's method:

```python
def _make_event_handler(self):
    component_type = type(self)

    @event_handler
    def handler(view, value="", component_id="", **kwargs):
        # Auto-resolve if only one instance of this type
        if not component_id:
            matches = [n for n, d in view._component_descriptors.items()
                       if isinstance(d, component_type)]
            if len(matches) == 1:
                component_id = matches[0]
        if not component_id:
            return
        state = getattr(view, component_id)  # calls __get__, returns TypedState
        self.toggle(state, value=value, **kwargs)  # component's own logic

    return handler
```

### User Override

If a developer defines their own `accordion_toggle` on the view, it takes precedence — the descriptor's `hasattr` check skips registration.

---

## 7. Partial Rendering (Future — djust core)

### Phase 1: Component Boundaries

`{% component faq %}` emits `<div data-component-id="faq">`. Full template still rendered and diffed.

### Phase 2: Subtree Diffing

Rust VDOM differ locates `data-component-id` subtrees, diffs only changed ones.

### Phase 3: Fragment Rendering

Rust renders only the changed component's template fragment. Requires component templates to be extractable as standalone units.

### Decision Tree

1. Non-component context changed? → Full render
2. Only component state changed? → Island render per changed component
3. Nothing changed? → Skip render (`_skip_render` flag, already exists)

---

## Implementation Priority

| Priority | What | Effort | Depends On |
|----------|------|--------|------------|
| **P0** | LiveComponent descriptor + State + Events | Medium | None |
| **P1** | Optimistic tier | High | P0 + client JS |
| **P2** | Dependency tracking | Medium | P0 |
| **P2** | Render caching | Low | P0 |
| **P2** | Client tier | Medium | P1 |
| **P3** | Partial rendering | Very High | djust core Rust |

---

## Open Questions

1. Should `self.state.active` or `self.faq.active` be the access pattern? (inner State object vs direct attribute)
2. Should tier be per-state-key or per-component?
3. Should `{% component %}` be a Rust handler or Django template tag?
4. How to handle `{% include %}` in dependency tracking?
5. Is VDOM subtree diffing needed, or is full diff at <1ms fast enough?
6. Should components have their own templates or share the parent's template?
7. How does `send_parent()` interact with the descriptor pattern?
