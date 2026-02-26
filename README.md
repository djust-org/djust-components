# djust-components

Reusable UI components for [djust](https://github.com/djust-org/djust) — the Phoenix LiveView for Django.

12 self-contained components with built-in CSS. No JavaScript dependencies beyond djust. Works with djust's event system (`dj-click`, `dj-input`, etc.) out of the box.

## Two Ways to Use Components

djust-components provides two complementary APIs:

| | Template Tags | Component Classes |
|--|--------------|-------------------|
| **Usage** | `{% badge label="Active" %}` in templates | `self.badge = Badge.status("active")` in Python |
| **Best for** | Static/declarative rendering | Dynamic state, event-driven updates |
| **Update from handler** | Re-render whole template | Reassign the attribute |
| **Logic** | Template-level | Full Python |

**Use template tags** when the component is static or driven directly by template variables.

**Use component classes** when you need to store component state as a view attribute, update it from an event handler, or configure it with complex business logic.

## Installation

```bash
pip install djust-components
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "djust_components",
]
```

Include the CSS in your base template:

```html
<link rel="stylesheet" href="{% static 'djust_components/components.css' %}">
```

## Quick Start

```html
{% load djust_components %}

{% modal id="confirm" title="Are you sure?" open=modal_open %}
  <p>This action cannot be undone.</p>
  <button dj-click="confirm_delete">Delete</button>
  <button dj-click="close_modal">Cancel</button>
{% endmodal %}
```

## Template Tags

12 components available as Django template tags via `{% load djust_components %}`.

### 1. Modal

Overlay dialog with backdrop blur. Hidden when `open` is falsy.

```html
{% modal id="my-modal" title="Title" open=is_open size="md" close_event="close_modal" %}
  Modal content here
{% endmodal %}
```

**Args:** `id`, `title`, `open` (bool/variable), `size` (sm/md/lg/xl), `close_event`

### 2. Tabs

Content switching with active state styling.

```html
{% tabs id="my-tabs" active=active_tab event="set_tab" %}
  {% tab id="overview" label="Overview" icon="📊" %}
    Overview content
  {% endtab %}
  {% tab id="settings" label="Settings" icon="⚙️" %}
    Settings content
  {% endtab %}
{% endtabs %}
```

**Args:** `id`, `active` (tab id), `event` (djust click event)

### 3. Accordion

Expandable sections — only one open at a time.

```html
{% accordion id="faq" active=open_item event="accordion_toggle" %}
  {% accordion_item id="q1" title="What is djust?" %}
    djust is Phoenix LiveView for Django.
  {% endaccordion_item %}
  {% accordion_item id="q2" title="How does it work?" %}
    Server-side rendering over WebSocket.
  {% endaccordion_item %}
{% endaccordion %}
```

**Args:** `id`, `active` (item id), `event`

### 4. Dropdown

Toggle menu with positioned content.

```html
{% dropdown id="menu" label="Actions" open=dropdown_open toggle_event="toggle_dropdown" %}
  <a dj-click="edit">Edit</a>
  <a dj-click="delete">Delete</a>
{% enddropdown %}
```

**Args:** `id`, `label`, `open`, `toggle_event`, `variant`

### 5. Toast Notifications

Server-push notifications that can be dismissed.

```html
{% toast_container toasts dismiss_event="dismiss_toast" %}
```

Pass a list of dicts: `[{"id": 1, "type": "success", "message": "Done!"}]`

Types: `success`, `error`, `warning`, `info`

### 6. Tooltip

Hover tooltip with configurable position.

```html
{% tooltip text="Click to save" position="top" %}
  <button dj-click="save">💾</button>
{% endtooltip %}
```

**Args:** `text`, `position` (top/bottom/left/right)

### 7. Progress Bar

Animated bar with color themes.

```html
{% progress value=75 label="Upload" size="md" color="success" %}
```

**Args:** `value` (0-100), `label`, `size` (sm/md/lg), `color` (primary/success/warning/danger), `show_label`

### 8. Badge

Status indicator with optional pulse animation.

```html
{% badge label="API Server" status="online" pulse=True %}
```

**Args:** `label`, `status` (online/offline/warning/error/default), `pulse`

### 9. Card

Content container with optional header.

```html
{% card title="Dashboard" subtitle="Overview" variant="elevated" %}
  Card content here
{% endcard %}
```

**Args:** `title`, `subtitle`, `variant` (default/outlined/elevated), `class`

### 10. Data Table

Sortable table with pagination.

```html
{% data_table rows=rows columns=columns sort_by=sort_by sort_desc=sort_desc %}
```

**Args:** `rows` (list of dicts), `columns` (list of `{key, label}`), `sort_by`, `sort_desc`, `sort_event`, `page`, `total_pages`, `prev_event`, `next_event`

### 11. Pagination

Standalone pagination controls.

```html
{% pagination page=current_page total_pages=total prev_event="prev" next_event="next" %}
```

### 12. Avatar

User avatar with initials fallback and status indicator.

```html
{% avatar src="/img/user.jpg" alt="Jane Doe" size="lg" status="online" %}
{% avatar initials="JD" size="md" status="busy" %}
```

**Args:** `src`, `alt`, `initials`, `size` (xs/sm/md/lg/xl), `status` (online/offline/busy/away)

## Theming

**djust-components v0.2.0+** integrates with [djust-theming](https://github.com/djust-org/djust-theming) for automatic theme adaptation. All components use theme variables and design tokens, so they automatically adapt to any of djust-theming's 19 built-in presets (Default, Shadcn, Blue, Green, Purple, Orange, Rose, Cyberpunk, Forest, Amber, Slate, Nebula, and more) and mode (light/dark/system).

### Setup with djust-theming

Install djust-theming (required for v0.2.0+):

```bash
pip install djust-theming
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "djust_theming",
    "djust_components",
]
```

Include both CSS files in your base template:

```html
{% load djust_theming %}
{% theme_head %}  <!-- djust-theming CSS with theme variables -->
<link rel="stylesheet" href="{% static 'djust_components/components.css' %}">
```

All components will now automatically adapt to theme changes. No additional configuration needed.

### Design Tokens

Components use djust-theming's design tokens for consistent spacing, typography, and styling:

- **Colors**: `--primary`, `--success`, `--warning`, `--destructive`, `--info`, `--muted`, etc.
- **Spacing**: `--space-1` (4px) through `--space-24` (96px)
- **Typography**: `--text-xs`, `--text-sm`, `--text-base`, `--font-medium`, etc.
- **Radius**: `--radius-sm`, `--radius-md`, `--radius-lg`, `--radius-xl`, `--radius-full`
- **Transitions**: `--duration-fast`, `--duration-normal`
- **Shadows**: `--shadow-sm`, `--shadow-md`, `--shadow-lg`

### Custom Theming

To create custom themes, use djust-theming's preset system. See [djust-theming documentation](https://github.com/djust-org/djust-theming) for details.

## Component Classes

In addition to template tags, djust-components provides a Python class API for programmatic use in LiveViews. Component instances can be stored as view attributes and updated dynamically from event handlers.

```python
from djust_components.components import Badge, Button, Card, Markdown, StatusDot

class TaskView(LiveView):
    def mount(self, **kwargs):
        self.status   = Badge.status("running")     # auto-colored
        self.priority = Badge.priority("P0")        # danger variant
        self.dot      = StatusDot("running")        # pulsing green dot
        self.submit   = Button("Save", variant="primary", action="save")
        self.card     = Card(content="<p>Details</p>", variant="elevated")
        self.body     = Markdown(task.spec)         # safe rendered markdown
```

```django
{{ status|safe }}   {{ priority|safe }}
{{ dot|safe }}
{{ submit|safe }}
{{ card|safe }}
{{ body|safe }}
```

### Available Component Classes

| Class | Description |
|-------|-------------|
| `Badge` | Status/priority badge with auto-coloring. Factory methods: `Badge.status()`, `Badge.priority()` |
| `StatusDot` | Animated dot indicator with built-in status → color/animation mapping |
| `Button` | Action button with variants, icons, loading state, and djust event wiring |
| `Card` | Content container with optional image, header, content, and footer sections |
| `Markdown` | Renders Markdown to sanitized HTML. Wrapped in `<div class="dj-prose">` |

See [COMPONENT_CLASSES.md](COMPONENT_CLASSES.md) for full API reference.

## LiveViews

In addition to components, djust-components ships ready-made LiveView classes for common full-page interactions.

### TtydTerminalView

Embeds a [ttyd](https://github.com/tsl0922/ttyd) WebSocket terminal using xterm.js 5.x — no djust relay, no build step.

```python
# urls.py
from djust_components.ttyd import TtydTerminalView

urlpatterns = [
    path("shell/", TtydTerminalView.as_view(), name="shell"),
]
```

**Props** (all optional — override by subclass or URL query param):

| Prop | Default | Description |
|------|---------|-------------|
| `ttyd_url` | `ws://localhost:7681` | WebSocket URL of the ttyd backend |
| `rows` | `24` | Terminal rows |
| `cols` | `80` | Terminal columns |
| `theme` | `{}` | xterm.js theme dict (e.g. `{"background": "#1e1e2e"}`) |

**Subclass pattern** (recommended for production — prevents user-controlled URL injection):

```python
class DeployLogView(TtydTerminalView):
    ttyd_url = "ws://localhost:7682"
    rows = 40
    cols = 120
    theme = {"background": "#1e1e2e", "foreground": "#cdd6f4"}

    path("deploy/logs/", DeployLogView.as_view(), name="deploy-logs"),
```

**URL query param override** (useful for dev/debugging):

```
/shell/?url=ws://myhost:7681&rows=30&cols=100
```

**Requirements:**
- ttyd must be run with `--check-origin=false` (or same origin) to allow browser WebSocket connections.
- xterm.js is loaded from `esm.sh` CDN at runtime. For offline/air-gapped environments, vendor `xterm@5` and `@xterm/addon-fit@0.10` to your static files and update the CDN constants in `ttyd_terminal.js`.

**Security note:** `login_required = False` by default (v1 targets local/trusted access). Override in subclasses for authenticated deployments.

## Development

```bash
git clone https://github.com/djust-org/djust-components
cd djust-components
pip install -e .
pytest tests/
```

## License

MIT
