# Component Classes

Alternative to template tags for programmatic use in LiveViews.

## Overview

djust-components provides two patterns for using UI components:

1. **Template Tags** - Declarative, HTML-first approach
2. **Component Classes** (this guide) - Programmatic, Python-first approach

## When to Use Component Classes

Component classes are ideal when you need to:
- **Update component state dynamically** from event handlers
- **Store component instances** as view attributes
- **Programmatically configure** components based on business logic
- **Reuse component instances** across multiple renders

## Installation

Component classes are included when you install djust-components:

```python
INSTALLED_APPS = [
    # ...
    "djust_components",
]
```

Include the CSS in your base template:

```html
<link rel="stylesheet" href="{% static 'djust_components/components-classes.css' %}">
```

## Available Components

### Badge

Status and priority indicators with auto-coloring.

#### Basic Usage

```python
from djust import LiveView
from djust_components.components import Badge

class DashboardView(LiveView):
    def mount(self, **kwargs):
        # Manual variant
        self.status = Badge("Active", variant="success")

        # Auto-colored from status string
        self.task = Badge.status("running")      # → success variant
        self.agent = Badge.status("failed")      # → danger variant

        # Auto-colored from priority
        self.p0 = Badge.priority("P0")           # → danger variant
        self.p2 = Badge.priority("P2")           # → info variant
```

```django
<!-- In template -->
{{ status|safe }}
{{ task|safe }}
{{ p0|safe }}
```

#### Status Mapping

Built-in status→variant mappings:

| Status | Variant |
|--------|---------|
| done, completed, passed, success, active, online, published | success |
| in_progress, running, processing, info | info |
| pending, starting, warning, draft, review | warning |
| failed, error, danger, offline, rejected | danger |
| skipped, cancelled, archived, disabled, muted | muted |

#### Priority Mapping

Built-in priority→variant mappings:

| Priority | Variant |
|----------|---------|
| P0 | danger |
| P1 | warning |
| P2 | info |
| P3 | muted |

#### Customization

```python
# Custom status mapping
custom_map = {
    "my_status": "success",
    "special": "warning",
}
badge = Badge.status("my_status", custom_map=custom_map)

# Size variants
sm = Badge("Small", size="sm")
lg = Badge("Large", size="lg")

# Custom CSS classes
badge = Badge("Custom", custom_class="glow-effect")
```

#### Dynamic Updates

```python
class TaskView(LiveView):
    def mount(self, **kwargs):
        self.task_status = Badge.status("pending")

    @event_handler
    def complete_task(self, **kwargs):
        # Update status dynamically
        self.task_status = Badge.status("completed")
        # Component will re-render with new variant
```

### StatusDot

Animated status indicator dots.

#### Basic Usage

```python
from djust import LiveView
from djust_components.components import StatusDot

class AgentView(LiveView):
    def mount(self, **kwargs):
        # Auto-colored and animated
        self.agent_status = StatusDot("running")    # green, pulsing
        self.task_status = StatusDot("completed")   # blue, static
        self.error = StatusDot("failed")            # red, static
```

```django
<!-- In template -->
{{ agent_status|safe }}
{{ task_status|safe }}
```

#### Status Mapping

Built-in status→variant and animation mappings:

| Status | Variant | Animation |
|--------|---------|-----------|
| running, active, online, passed | success | pulse |
| completed, done, idle | info | none |
| starting, pending, paused | warning | pulse |
| failed, error, offline | danger | none |
| stopped, skipped, cancelled, disabled | muted | none |
| loading, processing | (auto) | spin |

#### Customization

```python
# Explicit variant and animation
dot = StatusDot("custom", variant="success", animate="pulse")

# Size variants
sm = StatusDot("test", size="sm")
lg = StatusDot("test", size="lg")

# Tooltip
dot = StatusDot("running", tooltip="Agent is active")

# Disable animation
dot = StatusDot("running", animate=None)

# Custom mappings
custom_status_map = {"my_status": "success"}
custom_anim_map = {"my_status": "fade"}
dot = StatusDot(
    "my_status",
    custom_status_map=custom_status_map,
    custom_animation_map=custom_anim_map
)
```

#### Available Animations

- `pulse` - Gentle scaling pulse
- `spin` - Continuous rotation
- `fade` - Fade in/out
- `None` - Static (no animation)

## Pattern Comparison

### Template Tags (Declarative)

```django
{% load djust_components %}
{% badge label="Active" status="online" %}
```

**Pros:**
- Concise, HTML-first
- Good for static content
- Familiar to frontend developers

**Cons:**
- Can't store/update component instances
- Harder to dynamically configure
- Limited programmatic control

### Component Classes (Programmatic)

```python
self.status = Badge.status("online")
```

```django
{{ status|safe }}
```

**Pros:**
- Store as view attributes
- Update dynamically in event handlers
- Full programmatic control
- Better for complex logic

**Cons:**
- Requires Python code
- Need to mark as safe in templates

## CSS Custom Properties

Components use CSS variables for theming:

```css
/* Badge */
--dj-badge-bg: background color
--dj-badge-fg: text color
--dj-badge-radius: border radius
--dj-badge-padding: internal padding
--dj-badge-font-size: text size
--dj-badge-font-weight: text weight

/* Badge variants */
--dj-badge-success-bg, --dj-badge-success-fg
--dj-badge-info-bg, --dj-badge-info-fg
--dj-badge-warning-bg, --dj-badge-warning-fg
--dj-badge-danger-bg, --dj-badge-danger-fg
--dj-badge-muted-bg, --dj-badge-muted-fg

/* StatusDot */
--dj-status-dot-size: dot diameter
--dj-status-dot-success: success color
--dj-status-dot-info: info color
--dj-status-dot-warning: warning color
--dj-status-dot-danger: danger color
--dj-status-dot-muted: muted color
```

Components work without customization but automatically pick up djust-theming tokens when available.

## Integration with djust-theming

When djust-theming is installed, components automatically use theme colors:

```python
INSTALLED_APPS = [
    "djust_theming",
    "djust_components",
    # ...
]
```

No additional configuration needed - components will use theme tokens like `--success`, `--danger`, etc.

## Examples

### Task Dashboard

```python
from djust import LiveView
from djust_components.components import Badge, StatusDot

class TaskDashboard(LiveView):
    def mount(self, **kwargs):
        self.tasks = [
            {
                "name": "Deploy API",
                "status_badge": Badge.status("in_progress"),
                "priority_badge": Badge.priority("P0"),
            },
            {
                "name": "Write Tests",
                "status_badge": Badge.status("pending"),
                "priority_badge": Badge.priority("P2"),
            },
        ]
```

```django
{% for task in tasks %}
<div class="task">
    <h3>{{ task.name }}</h3>
    {{ task.status_badge|safe }}
    {{ task.priority_badge|safe }}
</div>
{% endfor %}
```

### Agent Monitor

```python
from djust import LiveView
from djust_components.components import StatusDot

class AgentMonitor(LiveView):
    def mount(self, **kwargs):
        self.agents = Agent.objects.all()
        self.agent_dots = {
            agent.id: StatusDot(agent.status, tooltip=f"{agent.name} - {agent.status}")
            for agent in self.agents
        }

    @event_handler
    def refresh_status(self, **kwargs):
        # Update dots when status changes
        for agent in Agent.objects.all():
            self.agent_dots[agent.id] = StatusDot(
                agent.status,
                tooltip=f"{agent.name} - {agent.status}"
            )
```

```django
{% for agent in agents %}
<div class="agent">
    {{ agent_dots|get_item:agent.id|safe }}
    <span>{{ agent.name }}</span>
</div>
{% endfor %}
```

## Migration from Template Tags

If you're using template tags and want to migrate:

**Before (template tags):**
```django
{% badge label=task.status status=task.status %}
```

**After (component classes):**
```python
class TaskView(LiveView):
    def mount(self, **kwargs):
        self.task_badge = Badge.status(self.task.status)
```

```django
{{ task_badge|safe }}
```

**Benefits of migration:**
- Update badge on status change without re-fetching task
- Conditional badge display logic in Python
- Store badge instances for reuse

## Testing

Components can be tested by checking their rendered HTML:

```python
from djust_components.components import Badge, StatusDot

def test_badge_rendering():
    badge = Badge.status("running")
    html = badge._render_custom()

    assert "dj-badge" in html
    assert "dj-badge-info" in html
    assert "running" in html

def test_status_dot_animation():
    dot = StatusDot("running")
    html = dot._render_custom()

    assert "dj-status-dot-pulse" in html
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding new components.

Component classes should:
- Use CSS custom properties with fallbacks
- Provide sensible defaults
- Support common use cases out of the box
- Include comprehensive tests
- Document CSS requirements
