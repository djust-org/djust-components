"""Example data definitions for every component in the gallery.

To add a new component to the gallery:
1. Add an entry to EXAMPLES (for template tags) or CLASS_EXAMPLES (for component classes)
2. Include at least one variant with a 'name' and 'template' (or 'render' for classes)
3. Set the 'category' to one of the keys in CATEGORIES
4. Run tests to verify: .venv/bin/python -m pytest tests/test_gallery.py -v
"""

# Category slug -> display label mapping
CATEGORIES = {
    "layout": "Layout",
    "form": "Form",
    "overlay": "Overlay",
    "feedback": "Feedback",
    "data": "Data",
    "navigation": "Navigation",
    "indicator": "Indicator",
    "typography": "Typography",
    "misc": "Misc",
}

# ─── Template Tag Examples ───
# Each key must match a registered template tag name.
# 'variants' is a list of dicts: {"name": str, "template": str, "context": dict (optional)}

EXAMPLES = {
    # ── Layout ──
    "modal": {
        "label": "Modal",
        "category": "overlay",
        "variants": [
            {
                "name": "Default",
                "template": '{% modal open=True title="Confirm Action" %}Are you sure you want to proceed?{% endmodal %}',
            },
            {
                "name": "Large",
                "template": '{% modal open=True title="Details" size="lg" %}Detailed content goes here.{% endmodal %}',
            },
            {
                "name": "Small",
                "template": '{% modal open=True title="Quick" size="sm" %}Small modal.{% endmodal %}',
            },
        ],
    },
    "card": {
        "label": "Card",
        "category": "layout",
        "variants": [
            {
                "name": "Default",
                "template": '{% card title="Project Status" %}Card body content.{% endcard %}',
            },
            {
                "name": "With Subtitle",
                "template": '{% card title="Metrics" subtitle="Last 30 days" %}Data here.{% endcard %}',
            },
            {
                "name": "Elevated",
                "template": '{% card title="Elevated" variant="elevated" %}Shadow card.{% endcard %}',
            },
        ],
    },
    "accordion": {
        "label": "Accordion",
        "category": "layout",
        "variants": [
            {
                "name": "Default",
                "template": (
                    '{% accordion id="acc1" %}'
                    '{% accordion_item title="Section 1" %}Content for section 1.{% endaccordion_item %}'
                    '{% accordion_item title="Section 2" %}Content for section 2.{% endaccordion_item %}'
                    '{% endaccordion %}'
                ),
            },
        ],
    },
    "tabs": {
        "label": "Tabs",
        "category": "layout",
        "variants": [
            {
                "name": "Default",
                "template": (
                    '{% tabs id="t1" active="overview" %}'
                    '{% tab id="overview" label="Overview" %}Overview content.{% endtab %}'
                    '{% tab id="settings" label="Settings" %}Settings content.{% endtab %}'
                    '{% endtabs %}'
                ),
            },
        ],
    },
    "collapsible": {
        "label": "Collapsible",
        "category": "layout",
        "variants": [
            {
                "name": "Closed",
                "template": '{% collapsible trigger="Show Details" %}Hidden content here.{% endcollapsible %}',
            },
            {
                "name": "Open",
                "template": '{% collapsible trigger="Hide Details" open=True %}Visible content.{% endcollapsible %}',
            },
        ],
    },
    "sheet": {
        "label": "Sheet / Drawer",
        "category": "layout",
        "variants": [
            {
                "name": "Right (default)",
                "template": '{% sheet open=True title="Settings" %}Sheet body content.{% endsheet %}',
            },
            {
                "name": "Left",
                "template": '{% sheet open=True title="Navigation" side="left" %}Nav items.{% endsheet %}',
            },
        ],
    },
    "split_pane": {
        "label": "Split Pane",
        "category": "layout",
        "variants": [
            {
                "name": "Horizontal",
                "template": (
                    '{% split_pane direction="horizontal" initial="50" %}'
                    '<p>Left pane</p>'
                    '{% pane %}'
                    '<p>Right pane</p>'
                    '{% endsplit_pane %}'
                ),
            },
        ],
    },

    # ── Form ──
    "dj_button": {
        "label": "Button",
        "category": "form",
        "variants": [
            {"name": "Primary", "template": '{% dj_button label="Save" variant="primary" %}'},
            {"name": "Danger", "template": '{% dj_button label="Delete" variant="danger" %}'},
            {"name": "Outline", "template": '{% dj_button label="Cancel" variant="outline" %}'},
            {"name": "Loading", "template": '{% dj_button label="Processing..." loading=True %}'},
            {"name": "With Icon", "template": '{% dj_button label="Download" icon="⬇" %}'},
            {"name": "Small", "template": '{% dj_button label="Small" size="sm" %}'},
            {"name": "Large", "template": '{% dj_button label="Large" size="lg" %}'},
        ],
    },
    "dj_input": {
        "label": "Input",
        "category": "form",
        "variants": [
            {"name": "Default", "template": '{% dj_input name="email" label="Email" placeholder="you@example.com" %}'},
            {"name": "With Value", "template": '{% dj_input name="name" label="Name" value="John Doe" %}'},
            {"name": "Password", "template": '{% dj_input name="pass" label="Password" input_type="password" %}'},
        ],
    },
    "dj_select": {
        "label": "Select",
        "category": "form",
        "variants": [
            {
                "name": "Default",
                "template": '{% dj_select name="color" label="Color" options=options %}',
                "context": {"options": [{"value": "red", "label": "Red"}, {"value": "blue", "label": "Blue"}, {"value": "green", "label": "Green"}]},
            },
        ],
    },
    "dj_textarea": {
        "label": "Textarea",
        "category": "form",
        "variants": [
            {"name": "Default", "template": '{% dj_textarea name="notes" label="Notes" placeholder="Write something..." %}'},
        ],
    },
    "dj_checkbox": {
        "label": "Checkbox",
        "category": "form",
        "variants": [
            {"name": "Unchecked", "template": '{% dj_checkbox name="agree" label="I agree to the terms" %}'},
            {"name": "Checked", "template": '{% dj_checkbox name="agree" label="I agree to the terms" checked=True %}'},
        ],
    },
    "dj_radio": {
        "label": "Radio",
        "category": "form",
        "variants": [
            {"name": "Default", "template": '{% dj_radio name="plan" label="Free" value="free" %}'},
            {"name": "Selected", "template": '{% dj_radio name="plan" label="Pro" value="pro" current_value="pro" %}'},
        ],
    },
    "switch": {
        "label": "Switch",
        "category": "form",
        "variants": [
            {"name": "Off", "template": '{% switch name="dark" label="Dark Mode" %}'},
            {"name": "On", "template": '{% switch name="dark" label="Dark Mode" checked=True %}'},
        ],
    },
    "color_picker": {
        "label": "Color Picker",
        "category": "form",
        "variants": [
            {"name": "Default", "template": '{% color_picker name="theme" label="Theme Color" value="#3B82F6" %}'},
        ],
    },
    "combobox": {
        "label": "Combobox",
        "category": "form",
        "variants": [
            {
                "name": "Default",
                "template": '{% combobox name="lang" label="Language" options=options %}',
                "context": {"options": [{"value": "py", "label": "Python"}, {"value": "js", "label": "JavaScript"}, {"value": "rs", "label": "Rust"}]},
            },
        ],
    },
    "date_picker": {
        "label": "Date Picker",
        "category": "form",
        "variants": [
            {"name": "Default", "template": '{% date_picker year=2026 month=3 %}'},
        ],
    },
    "file_dropzone": {
        "label": "File Dropzone",
        "category": "form",
        "variants": [
            {"name": "Default", "template": '{% file_dropzone name="upload" label="Drop files here" %}'},
            {"name": "Multiple", "template": '{% file_dropzone name="uploads" label="Drop files" multiple=True %}'},
        ],
    },
    "form_group": {
        "label": "Form Group",
        "category": "form",
        "variants": [
            {
                "name": "Default",
                "template": '{% form_group label="Full Name" %}{% dj_input name="fullname" %}{% endform_group %}',
            },
        ],
    },

    # ── Overlay ──
    "dropdown": {
        "label": "Dropdown",
        "category": "overlay",
        "variants": [
            {
                "name": "Default",
                "template": (
                    '{% dropdown id="d1" label="Options" %}'
                    '<a class="dropdown-item">Edit</a>'
                    '<a class="dropdown-item">Delete</a>'
                    '{% enddropdown %}'
                ),
            },
        ],
    },
    "tooltip": {
        "label": "Tooltip",
        "category": "overlay",
        "variants": [
            {"name": "Top", "template": '{% tooltip text="Helpful tip" position="top" %}Hover me{% endtooltip %}'},
            {"name": "Bottom", "template": '{% tooltip text="More info" position="bottom" %}Hover me{% endtooltip %}'},
        ],
    },
    "popover": {
        "label": "Popover",
        "category": "overlay",
        "variants": [
            {
                "name": "Default",
                "template": '{% popover trigger="Click me" title="Info" %}Popover content here.{% endpopover %}',
            },
        ],
    },
    "command_palette": {
        "label": "Command Palette",
        "category": "overlay",
        "variants": [
            {
                "name": "Open",
                "template": (
                    '{% command_palette open=True %}'
                    '{% palette_item label="New File" shortcut="Ctrl+N" event="new_file" %}'
                    '{% palette_item label="Open File" shortcut="Ctrl+O" event="open_file" %}'
                    '{% endcommand_palette %}'
                ),
            },
        ],
    },
    "context_menu": {
        "label": "Context Menu",
        "category": "overlay",
        "variants": [
            {
                "name": "Default",
                "template": (
                    '{% context_menu label="Right-click here" %}'
                    '{% context_menu_item label="Copy" event="copy" icon="📋" %}'
                    '{% context_menu_item label="Delete" event="delete" danger=True %}'
                    '{% endcontext_menu %}'
                ),
            },
        ],
    },

    # ── Feedback ──
    "alert": {
        "label": "Alert",
        "category": "feedback",
        "variants": [
            {"name": "Info", "template": '{% alert variant="info" %}This is an info alert.{% endalert %}'},
            {"name": "Success", "template": '{% alert variant="success" %}Operation succeeded!{% endalert %}'},
            {"name": "Warning", "template": '{% alert variant="warning" %}Please review.{% endalert %}'},
            {"name": "Danger", "template": '{% alert variant="danger" %}Something went wrong.{% endalert %}'},
        ],
    },
    "toast_container": {
        "label": "Toast",
        "category": "feedback",
        "variants": [
            {
                "name": "Default",
                "template": '{% toast_container toasts %}',
                "context": {"toasts": [
                    {"id": "1", "type": "success", "message": "File saved!"},
                    {"id": "2", "type": "error", "message": "Upload failed."},
                ]},
            },
        ],
    },
    "progress": {
        "label": "Progress",
        "category": "feedback",
        "variants": [
            {"name": "25%", "template": '{% progress 25 %}'},
            {"name": "75%", "template": '{% progress 75 %}'},
            {"name": "100%", "template": '{% progress 100 %}'},
        ],
    },
    "spinner": {
        "label": "Spinner",
        "category": "feedback",
        "variants": [
            {"name": "Default", "template": '{% spinner %}'},
            {"name": "Small", "template": '{% spinner size="sm" %}'},
            {"name": "Large", "template": '{% spinner size="lg" %}'},
        ],
    },
    "skeleton": {
        "label": "Skeleton",
        "category": "feedback",
        "variants": [
            {"name": "Text", "template": '{% skeleton skeleton_type="text" lines=3 %}'},
            {"name": "Circle", "template": '{% skeleton skeleton_type="circle" %}'},
            {"name": "Rectangle", "template": '{% skeleton skeleton_type="rect" %}'},
        ],
    },
    "empty_state": {
        "label": "Empty State",
        "category": "feedback",
        "variants": [
            {
                "name": "Default",
                "template": '{% empty_state title="No results" description="Try adjusting your search." icon="🔍" action_label="Clear filters" action_event="clear" %}',
            },
        ],
    },

    # ── Data ──
    "data_table": {
        "label": "Data Table",
        "category": "data",
        "variants": [
            {
                "name": "Default",
                "template": '{% data_table rows columns %}',
                "context": {
                    "rows": [
                        {"name": "Alice", "role": "Admin"},
                        {"name": "Bob", "role": "User"},
                        {"name": "Carol", "role": "Editor"},
                    ],
                    "columns": [
                        {"key": "name", "label": "Name"},
                        {"key": "role", "label": "Role"},
                    ],
                },
            },
        ],
    },
    "pagination": {
        "label": "Pagination",
        "category": "data",
        "variants": [
            {"name": "Default", "template": '{% pagination page=3 total_pages=10 %}'},
        ],
    },
    "virtual_list": {
        "label": "Virtual List",
        "category": "data",
        "variants": [
            {
                "name": "Default",
                "template": '{% virtual_list items=items total=100 page=1 page_size=5 %}',
                "context": {"items": [
                    {"id": "1", "content": "Item 1"},
                    {"id": "2", "content": "Item 2"},
                    {"id": "3", "content": "Item 3"},
                ]},
            },
        ],
    },
    "kanban_board": {
        "label": "Kanban Board",
        "category": "data",
        "variants": [
            {
                "name": "Default",
                "template": '{% kanban_board columns=cols %}',
                "context": {"cols": [
                    {"id": "todo", "title": "To Do", "cards": [{"id": "1", "title": "Task 1"}]},
                    {"id": "doing", "title": "In Progress", "cards": [{"id": "2", "title": "Task 2"}]},
                    {"id": "done", "title": "Done", "cards": []},
                ]},
            },
        ],
    },
    "tree_view": {
        "label": "Tree View",
        "category": "data",
        "variants": [
            {
                "name": "Default",
                "template": '{% tree_view nodes=nodes %}',
                "context": {"nodes": [
                    {"id": "1", "label": "Root", "children": [
                        {"id": "2", "label": "Child A", "children": []},
                        {"id": "3", "label": "Child B", "children": []},
                    ]},
                ]},
            },
        ],
    },

    # ── Navigation ──
    "breadcrumb": {
        "label": "Breadcrumb",
        "category": "navigation",
        "variants": [
            {
                "name": "Default",
                "template": '{% breadcrumb items=items %}',
                "context": {"items": [
                    {"label": "Home", "url": "/"},
                    {"label": "Products", "url": "/products/"},
                    {"label": "Widget"},
                ]},
            },
        ],
    },
    "stepper": {
        "label": "Stepper",
        "category": "navigation",
        "variants": [
            {
                "name": "Default",
                "template": '{% stepper steps=steps active=1 %}',
                "context": {"steps": [
                    {"label": "Account", "complete": True},
                    {"label": "Profile", "complete": False},
                    {"label": "Confirm", "complete": False},
                ]},
            },
        ],
    },
    "table_of_contents": {
        "label": "Table of Contents",
        "category": "navigation",
        "variants": [
            {
                "name": "Default",
                "template": '{% table_of_contents items=items active="intro" %}',
                "context": {"items": [
                    {"id": "intro", "label": "Introduction", "level": 1},
                    {"id": "setup", "label": "Setup", "level": 1},
                    {"id": "config", "label": "Configuration", "level": 2},
                ]},
            },
        ],
    },
    "timeline": {
        "label": "Timeline",
        "category": "navigation",
        "variants": [
            {
                "name": "Default",
                "template": (
                    '{% timeline %}'
                    '{% timeline_item title="Created" time="9:00 AM" %}Initial setup.{% endtimeline_item %}'
                    '{% timeline_item title="Updated" time="2:00 PM" %}Config changed.{% endtimeline_item %}'
                    '{% endtimeline %}'
                ),
            },
        ],
    },

    # ── Indicator ──
    "badge": {
        "label": "Badge (Tag)",
        "category": "indicator",
        "variants": [
            {"name": "Default", "template": '{% badge label="Active" %}'},
            {"name": "Online", "template": '{% badge label="Online" status="online" %}'},
            {"name": "Error", "template": '{% badge label="Error" status="error" %}'},
            {"name": "Warning", "template": '{% badge label="Pending" status="warning" %}'},
            {"name": "Pulse", "template": '{% badge label="Live" status="online" pulse=True %}'},
        ],
    },
    "avatar": {
        "label": "Avatar",
        "category": "indicator",
        "variants": [
            {"name": "Initials", "template": '{% avatar initials="JD" alt="John Doe" %}'},
            {"name": "With Status", "template": '{% avatar initials="AB" status="online" %}'},
            {"name": "Large", "template": '{% avatar initials="XY" size="lg" %}'},
        ],
    },
    "rating": {
        "label": "Rating",
        "category": "indicator",
        "variants": [
            {"name": "3 of 5", "template": '{% rating value=3 %}'},
            {"name": "Readonly", "template": '{% rating value=4 readonly=True %}'},
        ],
    },
    "gauge": {
        "label": "Gauge",
        "category": "indicator",
        "variants": [
            {"name": "Default", "template": '{% gauge value=65 label="CPU" %}'},
            {"name": "Full", "template": '{% gauge value=100 max_value=100 label="Memory" color="danger" %}'},
        ],
    },
    "stat_card": {
        "label": "Stat Card",
        "category": "indicator",
        "variants": [
            {"name": "Default", "template": '{% stat_card label="Users" value="1,234" trend="+12%" trend_direction="up" %}'},
            {"name": "Down", "template": '{% stat_card label="Errors" value="42" trend="-5%" trend_direction="down" %}'},
        ],
    },

    # ── Typography ──
    "code_block": {
        "label": "Code Block",
        "category": "typography",
        "variants": [
            {"name": "Python", "template": '{% code_block code="def hello():\\n    print(\'Hello!\')" language="python" %}'},
        ],
    },
    "kbd": {
        "label": "Kbd",
        "category": "typography",
        "variants": [
            {"name": "Single", "template": '{% kbd "Ctrl" %}'},
            {"name": "Combo", "template": '{% kbd "Ctrl" "C" %}'},
        ],
    },

    # ── Misc ──
    "dj_tag": {
        "label": "Tag",
        "category": "misc",
        "variants": [
            {"name": "Default", "template": '{% dj_tag label="python" %}'},
            {"name": "Dismissible", "template": '{% dj_tag label="removable" dismissible=True %}'},
        ],
    },
    "dj_divider": {
        "label": "Divider",
        "category": "misc",
        "variants": [
            {"name": "Horizontal", "template": '{% dj_divider %}'},
            {"name": "With Label", "template": '{% dj_divider label="OR" %}'},
        ],
    },
    "carousel": {
        "label": "Carousel",
        "category": "misc",
        "variants": [
            {
                "name": "Default",
                "template": '{% carousel images=images %}',
                "context": {"images": [
                    {"src": "https://via.placeholder.com/600x300/3B82F6/fff?text=Slide+1", "alt": "Slide 1"},
                    {"src": "https://via.placeholder.com/600x300/10B981/fff?text=Slide+2", "alt": "Slide 2"},
                ]},
            },
        ],
    },
    "copy_button": {
        "label": "Copy Button",
        "category": "misc",
        "variants": [
            {"name": "Default", "template": '{% copy_button text="Copied text here" %}'},
        ],
    },
    "notification_center": {
        "label": "Notification Center",
        "category": "misc",
        "variants": [
            {
                "name": "Default",
                "template": '{% notification_center notifications=notifs unread_count=2 %}',
                "context": {"notifs": [
                    {"id": "1", "title": "New message", "body": "You have a new message.", "time": "2m ago", "read": False},
                    {"id": "2", "title": "Deploy done", "body": "v1.2.0 deployed.", "time": "1h ago", "read": True},
                ]},
            },
        ],
    },
    "rich_text_editor": {
        "label": "Rich Text Editor",
        "category": "misc",
        "variants": [
            {"name": "Default", "template": '{% rich_text_editor name="content" value="<p>Hello world</p>" %}'},
        ],
    },
}


# ─── Component Class Examples ───
# For Python component classes (Badge, Button, Card, StatusDot, Markdown)
# Each variant has a 'render' callable that returns HTML.

def _make_class_examples():
    """Build CLASS_EXAMPLES lazily to avoid import-time issues with djust stubs."""
    from djust_components.components import Badge, Button, Card, Markdown, StatusDot

    return {
        "Badge": {
            "label": "Badge (Class)",
            "category": "indicator",
            "variants": [
                {"name": "Status Running", "render": lambda: Badge.status("running")._render_custom()},
                {"name": "Status Error", "render": lambda: Badge.status("error")._render_custom()},
                {"name": "Priority P0", "render": lambda: Badge.priority("P0")._render_custom()},
                {"name": "Priority P3", "render": lambda: Badge.priority("P3")._render_custom()},
            ],
        },
        "Button": {
            "label": "Button (Class)",
            "category": "form",
            "variants": [
                {"name": "Primary", "render": lambda: Button("Save", variant="primary")._render_custom()},
                {"name": "Danger", "render": lambda: Button("Delete", variant="danger")._render_custom()},
                {"name": "Loading", "render": lambda: Button("Wait...", loading=True)._render_custom()},
            ],
        },
        "Card": {
            "label": "Card (Class)",
            "category": "layout",
            "variants": [
                {"name": "Default", "render": lambda: Card(content="<p>Card content</p>")._render_custom()},
                {"name": "Elevated", "render": lambda: Card(content="<p>Elevated</p>", variant="elevated")._render_custom()},
            ],
        },
        "StatusDot": {
            "label": "StatusDot (Class)",
            "category": "indicator",
            "variants": [
                {"name": "Running", "render": lambda: StatusDot("running")._render_custom()},
                {"name": "Stopped", "render": lambda: StatusDot("stopped")._render_custom()},
                {"name": "Completed", "render": lambda: StatusDot("completed")._render_custom()},
            ],
        },
        "Markdown": {
            "label": "Markdown (Class)",
            "category": "typography",
            "variants": [
                {"name": "Simple", "render": lambda: Markdown("**Bold** and *italic* text.")._render_custom()},
                {"name": "Code", "render": lambda: Markdown("Inline `code` and:\n\n```python\nprint('hello')\n```")._render_custom()},
            ],
        },
    }


# Lazy singleton
_class_examples_cache = None


def _get_class_examples():
    """Return the CLASS_EXAMPLES dict, building it on first call.

    Deferred so that ``djust_components.components`` (which imports ``djust``)
    is not loaded at module import time -- important for test environments that
    stub out the ``djust`` module.
    """
    global _class_examples_cache
    if _class_examples_cache is None:
        _class_examples_cache = _make_class_examples()
    return _class_examples_cache


class _ClassExamplesProxy:
    """Dict-like proxy that lazily loads CLASS_EXAMPLES on first access.

    Implements the ``Mapping`` protocol (``__getitem__``, ``__contains__``,
    ``__iter__``, ``__len__``, ``keys``, ``values``, ``items``, ``get``)
    so it can be used anywhere a regular dict is expected.
    """

    def __getitem__(self, key):
        return _get_class_examples()[key]

    def __contains__(self, key):
        return key in _get_class_examples()

    def __iter__(self):
        return iter(_get_class_examples())

    def __len__(self):
        return len(_get_class_examples())

    def keys(self):
        return _get_class_examples().keys()

    def values(self):
        return _get_class_examples().values()

    def items(self):
        return _get_class_examples().items()

    def get(self, key, default=None):
        return _get_class_examples().get(key, default)


CLASS_EXAMPLES = _ClassExamplesProxy()
