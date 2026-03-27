## ADDED Requirements

### Requirement: Template dependency map built at mount
The system SHALL call `extract_template_variables(template_content)` at mount time and cross-reference the result with `_component_descriptors` to build a dependency map.

#### Scenario: Dependency map identifies referenced components
- **WHEN** a template contains `{{ faq.active }}` and `{{ main_tabs.active }}`
- **THEN** the dependency map SHALL identify `faq` and `main_tabs` as referenced components

#### Scenario: Unreferenced components excluded
- **WHEN** a LiveView declares `confirm = Modal()` but the template never uses `{{ confirm.* }}`
- **THEN** `confirm` SHALL NOT appear in the dependency map

### Requirement: Selective state sync using dependency map
After an event, the system SHALL combine dirty flags with the dependency map to determine which component state to sync to Rust.

#### Scenario: Only dirty + referenced components synced
- **WHEN** `faq` is dirty and `main_tabs` is clean, and the template references both
- **THEN** only `faq`'s state SHALL be sent to Rust (Rust retains `main_tabs` from previous sync)

### Requirement: Dependency map cached per template
The dependency map SHALL be computed once per template content hash and cached for the lifetime of the view class.

#### Scenario: Repeated mounts reuse cached map
- **WHEN** two instances of the same LiveView class mount
- **THEN** both SHALL use the same cached dependency map (computed only once)
