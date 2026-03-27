## ADDED Requirements

### Requirement: TypedState inner class defines component state schema
Each LiveComponent subclass SHALL declare state via an inner `class State(TypedState)` with annotated attributes and defaults.

#### Scenario: State declaration with types
- **WHEN** a component defines `class State(TypedState): active: str = ""; multiple: bool = False`
- **THEN** `State(active="q1")` creates a dict subclass with typed properties: `state.active` returns `"q1"`, `state["active"]` returns `"q1"`

#### Scenario: IDE autocomplete
- **WHEN** a developer types `self.faq.active` in an IDE
- **THEN** the IDE SHALL provide autocomplete showing `active: str` and `multiple: bool`

### Requirement: TypedState serializes as a plain dict
TypedState instances SHALL serialize identically to plain dicts through djust's `normalize_django_value()` pipeline.

#### Scenario: JSON serialization
- **WHEN** `json.dumps(AccordionState(active="q1", multiple=False))` is called
- **THEN** the output SHALL be `{"active": "q1", "multiple": false}`

#### Scenario: Rust state sync
- **WHEN** djust's `_sync_state_to_rust()` processes a TypedState
- **THEN** Rust receives a plain dict with the same keys and values

### Requirement: TypedState properties auto-generated from annotations
TypedState's `__init_subclass__` SHALL create getter/setter properties for each annotated attribute.

#### Scenario: Property creation
- **WHEN** `class MyState(TypedState): count: int = 0` is defined
- **THEN** `MyState().count` returns `0` and `MyState().count = 5` sets `self["count"] = 5`

### Requirement: TypedState.from_dict rehydration
TypedState SHALL provide a `from_dict(d)` classmethod that creates a typed instance from a plain dict.

#### Scenario: Rehydration preserves values
- **WHEN** `AccordionState.from_dict({"active": "q1", "multiple": True})` is called
- **THEN** the result SHALL have `active="q1"` and `multiple=True`

#### Scenario: Rehydration is idempotent
- **WHEN** `AccordionState.from_dict(existing_accordion_state)` is called with an AccordionState
- **THEN** the same object SHALL be returned unchanged
