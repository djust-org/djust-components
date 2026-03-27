# Migration Guide: Mixins to Descriptors (DEP-001 to DEP-002)

This guide covers migrating from the mixin-based interactive component pattern
(DEP-001) to the descriptor-based pattern (DEP-002).

## Quick Summary

| Aspect | Mixin (old) | Descriptor (new) |
|--------|------------|-------------------|
| Import | `from djust_components.mixins import AccordionMixin` | `from djust_components.descriptors import Accordion` |
| Declaration | Class base + `init_accordion()` in mount | Class attribute: `faq = Accordion()` |
| State access | `self.accordion_instances["faq"]["active"]` | `self.faq.active` |
| Event handlers | Provided by mixin, manual `component_id` routing | Auto-registered, auto-routed |
| Multiple instances | String keys in instances dict | Multiple class attributes |

## Before (Mixin Pattern)

```python
from djust import LiveView
from djust_components.mixins import AccordionMixin, TabsMixin, ModalMixin

class MyPage(AccordionMixin, TabsMixin, ModalMixin, LiveView):
    def mount(self, request, **kwargs):
        self.init_accordion("faq", active="q1")
        self.init_accordion("settings")
        self.init_tabs("nav", active="overview")
        self.init_modal("confirm")

    def get_context_data(self, **kwargs):
        self.faq = self.get_accordion_ctx("faq")
        self.nav = self.get_tabs_ctx("nav")
        return super().get_context_data(**kwargs)
```

## After (Descriptor Pattern)

```python
from djust import LiveView
from djust_components.descriptors import Accordion, Tabs, Modal

class MyPage(LiveView):
    faq = Accordion(active="q1")
    settings_acc = Accordion()
    nav = Tabs(active="overview")
    confirm = Modal()

    # No mount() needed for component init
    # No get_context_data() override needed
    # Event handlers auto-registered: accordion_toggle, set_tab, toggle_modal
```

## Step-by-Step Migration

### 1. Replace imports

```python
# Old
from djust_components.mixins import AccordionMixin, TabsMixin

# New
from djust_components.descriptors import Accordion, Tabs
```

### 2. Remove mixin bases, add descriptors as class attributes

```python
# Old
class MyPage(AccordionMixin, TabsMixin, LiveView):
    ...

# New
class MyPage(LiveView):
    faq = Accordion(active="q1")
    nav = Tabs(active="overview")
```

### 3. Remove init calls from mount()

```python
# Old
def mount(self, request, **kwargs):
    self.init_accordion("faq", active="q1")
    self.init_tabs("nav", active="overview")

# New — descriptors auto-initialise on first access
# mount() only needed for non-component setup
```

### 4. Update state access

```python
# Old
active = self.accordion_instances["faq"]["active"]
inst = self._get_typed_instance("faq", AccordionState)
active = inst.active

# New
active = self.faq.active  # typed, IDE autocomplete works
```

### 5. Event handlers work the same

Templates using `dj-click="accordion_toggle"` and `data-component-id` continue
to work unchanged. The descriptor auto-registers the same event handler names.

### 6. Update template context

```html
<!-- Old: required get_context_data() to set self.faq dict -->
{% accordion id="faq" active=faq.active component_id=faq.component_id %}

<!-- New: descriptor state is a dict, same template syntax works -->
{% accordion id="faq" active=faq.active component_id=faq.component_id %}
```

## Key Differences

- **No more mixin class bases** -- fewer MRO conflicts
- **No `init_*()` calls** -- state created on first attribute access
- **Attribute name = component_id** -- `faq = Accordion()` means `component_id="faq"`
- **Typed state** -- `self.faq.active` with IDE autocomplete
- **Per-instance isolation** -- each view instance gets independent state
- **Automatic rehydration** -- after djust serialization, plain dicts rehydrate to TypedState

## Compatibility

DEP-001 mixins remain fully functional and are not removed. They are marked
deprecated and will be removed in a future major release. You can migrate
incrementally -- mixins and descriptors can coexist on different views.
