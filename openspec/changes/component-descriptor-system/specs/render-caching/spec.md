## ADDED Requirements

### Requirement: Dirty flag on TypedState mutation
TypedState's `__setitem__` SHALL set a `_dirty` flag to `True` when a value changes.

#### Scenario: Mutation marks dirty
- **WHEN** `state.active = "q2"` is called and the previous value was `"q1"`
- **THEN** `state._dirty` SHALL be `True`

#### Scenario: Same-value assignment stays clean
- **WHEN** `state.active = "q1"` is called and the previous value was already `"q1"`
- **THEN** `state._dirty` SHALL remain unchanged

### Requirement: Skip render for clean components
The rendering pipeline SHALL skip calling `.render()` on components whose state is not dirty, reusing the previously cached HTML.

#### Scenario: Clean component uses cached HTML
- **WHEN** an event handler modifies component A but not component B
- **THEN** component B's `.render()` SHALL NOT be called; its cached HTML SHALL be reused

#### Scenario: Dirty component re-renders
- **WHEN** an event handler modifies component A's state
- **THEN** component A's `.render()` SHALL be called and the cache updated

### Requirement: Cache stored on state instance
The cached HTML and dirty flag SHALL be stored on the TypedState instance (per-session), not at the class level.

#### Scenario: No cross-session cache sharing
- **WHEN** user A modifies their accordion and user B has the same page open
- **THEN** user B's render cache SHALL be independent of user A's changes
