## ADDED Requirements

### Requirement: Descriptors auto-register event handlers on the owner class
`__set_name__` SHALL register the component's event handler method on the LiveView class if no method with that name already exists.

#### Scenario: Handler auto-registered
- **WHEN** `faq = Accordion()` is declared and `Accordion.Meta.event = "accordion_toggle"`
- **THEN** the LiveView class SHALL have an `accordion_toggle` method

#### Scenario: User-defined handler takes precedence
- **WHEN** a developer defines their own `def accordion_toggle(self, ...)` on the LiveView
- **THEN** the descriptor SHALL NOT override it (hasattr check skips registration)

#### Scenario: Multiple instances share one handler
- **WHEN** `faq = Accordion()` and `settings = Accordion()` are declared on the same class
- **THEN** only one `accordion_toggle` handler SHALL exist, routed by `component_id`

### Requirement: Event routing by component_id
The auto-registered handler SHALL use the `component_id` parameter to determine which component instance to update. The `component_id` matches the attribute name.

#### Scenario: Explicit component_id routing
- **WHEN** an event arrives with `component_id="faq"`
- **THEN** the handler SHALL access `self.faq` (via descriptor `__get__`) and call the component's method

#### Scenario: Auto-resolve single instance
- **WHEN** an event arrives with empty `component_id` and only one Accordion exists on the view
- **THEN** the handler SHALL automatically route to that sole instance

#### Scenario: Empty component_id with multiple instances
- **WHEN** an event arrives with empty `component_id` and multiple Accordions exist
- **THEN** the handler SHALL do nothing (cannot determine target)

### Requirement: Component_id injected into state dict
The descriptor SHALL inject `component_id` (equal to the attribute name) into the state dict so templates can reference it.

#### Scenario: Template access to component_id
- **WHEN** a template uses `{{ faq.component_id }}`
- **THEN** it SHALL resolve to `"faq"`

## REMOVED Requirements

### Requirement: DEP-001 mixin-based event routing
**Reason**: Replaced by descriptor auto-registration. String-keyed instance IDs and manual `init_*` calls are no longer needed.
**Migration**: Replace `class MyView(AccordionMixin, LiveView)` + `self.init_accordion("faq")` with `class MyView(LiveView): faq = Accordion()`.
