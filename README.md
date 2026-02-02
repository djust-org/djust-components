# djust-components

Reusable UI components for [djust](https://github.com/djust-org/djust) — the Phoenix LiveView for Django.

12 self-contained components with built-in CSS. No JavaScript dependencies beyond djust. Works with djust's event system (`dj-click`, `dj-input`, etc.) out of the box.

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

## Components

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

## Customization

All components use CSS custom properties. Override them to match your theme:

```css
:root {
  --dj-primary: #6366f1;
  --dj-success: #22c55e;
  --dj-warning: #eab308;
  --dj-danger: #ef4444;
  --dj-info: #3b82f6;
  --dj-text: #e2e8f0;
  --dj-bg: #0f172a;
  --dj-bg-subtle: #1e293b;
  --dj-border: rgba(99, 102, 241, 0.15);
  --dj-radius: 8px;
}
```

## Development

```bash
git clone https://github.com/djust-org/djust-components
cd djust-components
pip install -e .
pytest tests/
```

## License

MIT
