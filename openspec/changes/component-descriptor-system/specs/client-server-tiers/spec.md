## ADDED Requirements

### Requirement: Components declare a client/server tier
Each LiveComponent subclass SHALL declare a tier via `class Meta: tier = "optimistic"`. Valid tiers are `"server"`, `"optimistic"`, and `"client"`. Default is `"server"`.

#### Scenario: Tier declaration
- **WHEN** a component defines `class Meta: tier = "optimistic"`
- **THEN** the component's state changes SHALL use the optimistic tier mechanism

#### Scenario: Per-instance tier override
- **WHEN** a developer writes `filters = Dropdown(tier="server")`
- **THEN** that instance SHALL use the server tier regardless of the class default

### Requirement: Server tier — full round-trip
Components with `tier="server"` SHALL process all state changes through the full pipeline: client event → WebSocket → server handler → re-render → VDOM diff → patches.

#### Scenario: Server tier latency
- **WHEN** a user clicks a server-tier component
- **THEN** the UI update SHALL wait for the server response (~50-100ms)

### Requirement: Optimistic tier — instant client + server confirm
Components with `tier="optimistic"` SHALL declare an `optimistic_rule` in Meta that specifies how the client applies the DOM change instantly.

#### Scenario: Optimistic DOM change applied immediately
- **WHEN** a user clicks an optimistic-tier accordion trigger
- **THEN** the client SHALL apply the DOM change (toggle CSS class) immediately without waiting for server

#### Scenario: Server confirms optimistic change
- **WHEN** the server processes the event and sends VDOM patches
- **THEN** the patches SHALL either confirm the client's prediction (no-op) or correct it

#### Scenario: Optimistic misprediction corrected
- **WHEN** the server's event handler rejects the state change (e.g., permission denied)
- **THEN** the VDOM patches SHALL correct the DOM to match server state

### Requirement: Optimistic rule format
The `optimistic_rule` SHALL specify: `action` (toggle_class, toggle_attr, set_attr), `target` (CSS selector with `{component_id}` and `{value}` interpolation), and the class/attribute to manipulate.

#### Scenario: Toggle class rule
- **WHEN** rule is `{"action": "toggle_class", "target": "[data-value='{value}']", "class": "open"}`
- **THEN** the client SHALL toggle the `"open"` CSS class on the matching element

### Requirement: Client tier — pure client-side state
Components with `tier="client"` SHALL NOT register server-side event handlers. State is managed entirely by client-side JS via `dj-hook`.

#### Scenario: No server round-trip
- **WHEN** a user hovers over a client-tier tooltip
- **THEN** no WebSocket event SHALL be sent to the server

#### Scenario: Client state preserved during re-render
- **WHEN** a server re-render produces VDOM patches for the page
- **THEN** client-tier component subtrees with `dj-update="ignore"` SHALL retain their client-managed state
