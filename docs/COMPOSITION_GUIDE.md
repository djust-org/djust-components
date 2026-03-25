# Component Composition Guide

Common patterns for nesting djust-components together. These recipes show
how to combine lower-level components into cohesive UI regions.

---

## Card + Tabs

Use a Card as the outer container and Tabs inside for sectioned content.

```html
{% load djust_components %}

{% card title="User Profile" %}
    {% tabs active=active_tab %}
        {% tab id="overview" label="Overview" %}
            <p>Name: {{ user.name }}</p>
            <p>Email: {{ user.email }}</p>
        {% endtab %}
        {% tab id="activity" label="Activity" %}
            {% audit_log entries=recent_activity %}
        {% endtab %}
        {% tab id="settings" label="Settings" %}
            {% dj_input name="display_name" label="Display Name" value=user.name %}
            {% dj_button label="Save" variant="primary" event="save_settings" %}
        {% endtab %}
    {% endtabs %}
{% endcard %}
```

**LiveView handler:**

```python
class ProfileView(LiveView):
    def mount(self, **kwargs):
        self.active_tab = "overview"
        self.recent_activity = self.load_activity()

    @event_handler
    def switch_tab(self, tab_id):
        self.active_tab = tab_id
```

---

## Modal + Form

Wrap a form inside a Modal for create/edit dialogs.

```html
{% modal id="edit-item" open=modal_open title="Edit Item" close_event="close_modal" %}
    {% dj_input name="title" label="Title" value=item.title event="update_title" %}
    {% dj_input name="description" label="Description" value=item.description event="update_desc" %}
    {% dj_select name="priority" label="Priority" value=item.priority
       options=priority_options event="update_priority" %}

    <div class="modal-actions">
        {% dj_button label="Cancel" variant="ghost" event="close_modal" %}
        {% dj_button label="Save" variant="primary" event="save_item" %}
    </div>
{% endmodal %}
```

**LiveView handler:**

```python
class ItemListView(LiveView):
    def mount(self, **kwargs):
        self.modal_open = False
        self.item = {}
        self.priority_options = [
            {"value": "low", "label": "Low"},
            {"value": "medium", "label": "Medium"},
            {"value": "high", "label": "High"},
        ]

    @event_handler
    def edit_item(self, item_id):
        self.item = Item.objects.get(id=item_id)
        self.modal_open = True

    @event_handler
    def close_modal(self):
        self.modal_open = False

    @event_handler
    def save_item(self):
        self.item.save()
        self.modal_open = False
```

---

## Toolbar + Data Table

Place action buttons in a toolbar above a data table for bulk operations,
search, and filtering.

```html
<div class="page-content">
    {% toolbar %}
        {% toolbar_group align="left" %}
            {% dj_input name="search" placeholder="Search..." value=search_query
               event="search" %}
            {% dj_select name="status_filter" value=status_filter
               options=status_options event="filter_status" %}
        {% endtoolbar_group %}

        {% toolbar_group align="right" %}
            {% dj_button label="Export" variant="ghost" icon="↓" event="open_export" %}
            {% dj_button label="Add New" variant="primary" icon="+" event="add_item" %}
        {% endtoolbar_group %}
    {% endtoolbar %}

    {% data_table columns=columns rows=filtered_rows
       sort_column=sort_col sort_direction=sort_dir
       sort_event="sort" select_event="select_row" %}
    {% enddata_table %}

    {% export_dialog formats=export_formats columns=export_columns
       event="export" open=export_open close_event="close_export" %}
</div>
```

**LiveView handler:**

```python
class OrdersView(LiveView):
    def mount(self, **kwargs):
        self.search_query = ""
        self.status_filter = "all"
        self.sort_col = "created_at"
        self.sort_dir = "desc"
        self.export_open = False

    @event_handler
    def search(self, value):
        self.search_query = value
        self.refresh_rows()

    @event_handler
    def sort(self, column):
        if self.sort_col == column:
            self.sort_dir = "asc" if self.sort_dir == "desc" else "desc"
        else:
            self.sort_col = column
            self.sort_dir = "asc"
        self.refresh_rows()
```

---

## Sidebar + Breadcrumb + Page Content

Compose a navigation sidebar with breadcrumb trail and main content area.

```html
<div class="app-layout">
    {% sidebar items=nav_items active=current_section collapse_event="toggle_sidebar" %}

    <main class="main-content">
        {% breadcrumb items=breadcrumb_trail %}

        {% page_alert type="info" dismissible=True dismiss_event="dismiss_alert" %}
            New features are available! Check the changelog.
        {% endpage_alert %}

        {% card title=page_title %}
            {% block content %}{% endblock %}
        {% endcard %}
    </main>
</div>
```

**LiveView handler:**

```python
class DashboardView(LiveView):
    def mount(self, **kwargs):
        self.current_section = "dashboard"
        self.nav_items = [
            {"id": "dashboard", "label": "Dashboard", "icon": "📊"},
            {"id": "orders", "label": "Orders", "icon": "📦"},
            {"id": "customers", "label": "Customers", "icon": "👥"},
            {"id": "settings", "label": "Settings", "icon": "⚙️"},
        ]
        self.breadcrumb_trail = [
            {"label": "Home", "url": "/"},
            {"label": "Dashboard"},
        ]

    @event_handler
    def navigate(self, section):
        self.current_section = section
        self.breadcrumb_trail = [
            {"label": "Home", "url": "/"},
            {"label": section.title()},
        ]
```

---

## Modal + Approval Gate (Confirmation Flow)

Combine a Modal with an Approval Gate for high-risk action confirmation.

```html
{% modal id="delete-confirm" open=confirm_open title="Confirm Deletion"
   close_event="cancel_delete" size="sm" %}
    {% approval_gate
        message=confirm_message
        risk="high"
        approve_event="confirm_delete"
        reject_event="cancel_delete"
        approve_label="Yes, Delete"
        reject_label="Cancel" %}
{% endmodal %}
```

**LiveView handler:**

```python
from djust_components.helpers import confirm_action

class ResourceView(LiveView):
    def mount(self, **kwargs):
        self.confirm_open = False
        self.confirm_message = ""
        self.pending_delete_id = None

    @event_handler
    def delete_resource(self, resource_id):
        resource = Resource.objects.get(id=resource_id)
        self.pending_delete_id = resource_id
        self.confirm_message = f"Delete '{resource.name}'? This cannot be undone."
        self.confirm_open = True

    @event_handler
    def confirm_delete(self):
        Resource.objects.filter(id=self.pending_delete_id).delete()
        self.confirm_open = False
        self.pending_delete_id = None

    @event_handler
    def cancel_delete(self):
        self.confirm_open = False
        self.pending_delete_id = None
```

---

## Card + Progress + Stat Cards (Dashboard)

Build a dashboard summary row with stat cards and progress indicators.

```html
<div class="stats-row">
    {% stat_card label="Total Users" value=total_users icon="👥"
       trend=user_trend trend_label=user_trend_label %}
    {% stat_card label="Revenue" value=revenue icon="💰"
       trend=revenue_trend trend_label=revenue_trend_label %}
    {% stat_card label="Active Jobs" value=active_jobs icon="⚡" %}
</div>

{% card title="Storage Usage" %}
    {% meter segments=storage_segments total=storage_total
       label="Disk Usage" show_legend=True %}
{% endcard %}

{% card title="Deployment Progress" %}
    {% segmented_progress segments=deploy_steps %}
{% endcard %}
```

---

## Toast Notifications from LiveView Handlers

Use the `push_toast` helper to format toast state from event handlers.

```python
from djust_components.helpers import push_toast

class SettingsView(LiveView):
    def mount(self, **kwargs):
        self.toast = None

    @event_handler
    def save_settings(self, **form_data):
        try:
            self.update_settings(form_data)
            self.toast = push_toast("Settings saved!", type="success")
        except ValidationError as e:
            self.toast = push_toast(str(e), type="error", duration=5000)
```

```html
{% if toast %}
    {% dj_toast message=toast.message type=toast.type
       duration=toast.duration dismissible=toast.dismissible %}
{% endif %}
```

---

## Tips

- **Keep state in the LiveView.** Components are stateless renderers; all
  state lives on the view and flows down via template context.
- **Use helpers for repetitive patterns.** `push_toast` and `confirm_action`
  reduce boilerplate in event handlers.
- **Presets reduce template noise.** Instead of repeating
  `variant="danger" size="sm"` everywhere, define a preset once and use
  `{% dj_button preset="danger-sm" label="Delete" event="delete" %}`.
- **Nest freely.** Any block-level component (`{% card %}`, `{% modal %}`,
  `{% tabs %}`) can contain any other component or raw HTML.
