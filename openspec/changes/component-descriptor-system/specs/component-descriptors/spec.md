## ADDED Requirements

### Requirement: LiveComponent acts as a Python descriptor
LiveComponent SHALL implement `__set_name__`, `__get__`, and `__set__` so it can be declared as a class attribute on a LiveView. The attribute name SHALL become the component's identity (component_id).

#### Scenario: Class-level declaration
- **WHEN** a developer writes `faq = Accordion(active="q1")` on a LiveView class
- **THEN** `__set_name__` fires at class creation time, registering the descriptor with name `"faq"`

#### Scenario: Instance-level access
- **WHEN** a developer accesses `self.faq` on a LiveView instance
- **THEN** `__get__` returns a TypedState object with `active="q1"` and `component_id="faq"`

#### Scenario: Per-instance isolation
- **WHEN** two browser sessions create instances of the same LiveView class
- **THEN** each instance SHALL have independent component state (no shared mutable state)

### Requirement: Component descriptor registry
LiveComponent's `__set_name__` SHALL build a `_component_descriptors` dict on the owner class mapping attribute names to descriptor instances.

#### Scenario: Registry populated at class creation
- **WHEN** a LiveView class defines `faq = Accordion()` and `tabs = Tabs()`
- **THEN** `cls._component_descriptors` SHALL equal `{"faq": <Accordion>, "tabs": <Tabs>}`

#### Scenario: Inheritance preserves descriptors
- **WHEN** `class ChildView(ParentView)` and ParentView has `faq = Accordion()`
- **THEN** `ChildView._component_descriptors` SHALL include `"faq"`

### Requirement: State storage uses underscore-prefixed key
Descriptor state SHALL be stored in `obj.__dict__["_component_{name}"]` to avoid double-inclusion in djust's template context pipeline.

#### Scenario: Storage key excludes from context
- **WHEN** djust's `get_context_data()` iterates instance attributes
- **THEN** `_component_faq` is skipped (underscore prefix) while `faq` (via `__get__`) is included

### Requirement: Rehydration after serialization
`__get__` SHALL detect when stored state is a plain dict (after djust deserialization) and convert it back to the component's State class via `State.from_dict()`.

#### Scenario: State survives serialization round-trip
- **WHEN** djust serializes view state to JSON and restores it on the next event
- **THEN** `self.faq.active` SHALL return the correct value (not raise AttributeError)

### Requirement: Descriptor __set__ handles dict assignment
`__set__` SHALL accept a plain dict and convert it to the component's State class.

#### Scenario: Dict assignment
- **WHEN** a developer writes `self.faq = {"active": "q2"}`
- **THEN** `self.faq` SHALL be an AccordionState with `active="q2"`
