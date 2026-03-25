"""Tests for Rich Select and Data Grid components — template tags, Rust handlers, and XSS coverage."""
import types
import sys

# Stub djust before importing any component code
_stub = types.ModuleType("djust")


class _Component:
    def __init__(self, **kwargs):
        pass

    def __str__(self):
        return self._render_custom()

    def _render_custom(self):
        return ""


_stub.Component = _Component


class _LV:
    pass


_stub.LiveView = _LV
sys.modules.setdefault("djust", _stub)
sys.modules.setdefault("djust._rust", types.ModuleType("djust._rust"))

# Build a fake 'djust.decorators' submodule — event_handler is a pass-through.
_decorators_stub = types.ModuleType("djust.decorators")


def _event_handler(fn=None, **kwargs):
    """No-op stand-in for @event_handler; returns the function unchanged."""
    if fn is not None:
        return fn
    return lambda f: f


_decorators_stub.event_handler = _event_handler
sys.modules.setdefault("djust.decorators", _decorators_stub)

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "djust_components",
        ],
        TEMPLATES=[{
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {"context_processors": []},
        }],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    )
    django.setup()

from django.template import Template, Context
import pytest


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ===========================================================================
# Rich Select Template Tag
# ===========================================================================


class TestRichSelect:
    OPTIONS = [
        {"value": "alice", "label": "Alice", "icon": "A", "description": "Engineering"},
        {"value": "bob", "label": "Bob", "badge": "Admin"},
        {"value": "carol", "label": "Carol", "image": "/img/carol.jpg"},
    ]

    def test_basic_render(self):
        html = render(
            '{% rich_select name="assignee" options=opts %}',
            {"opts": self.OPTIONS},
        )
        assert 'class="rich-select' in html
        assert 'name="assignee"' in html
        assert 'role="combobox"' in html
        assert 'role="listbox"' in html

    def test_selected_value(self):
        html = render(
            '{% rich_select name="assignee" options=opts value="alice" %}',
            {"opts": self.OPTIONS},
        )
        assert "rich-select-option--active" in html
        assert 'aria-selected="true"' in html
        assert "Alice" in html

    def test_placeholder(self):
        html = render(
            '{% rich_select name="x" options=opts placeholder="Choose..." %}',
            {"opts": self.OPTIONS},
        )
        assert "Choose..." in html
        assert "rich-select-placeholder" in html

    def test_icon_option(self):
        html = render(
            '{% rich_select name="x" options=opts %}',
            {"opts": self.OPTIONS},
        )
        assert "rich-select-option-icon" in html

    def test_image_option(self):
        html = render(
            '{% rich_select name="x" options=opts %}',
            {"opts": self.OPTIONS},
        )
        assert "rich-select-option-image" in html
        assert "/img/carol.jpg" in html

    def test_badge_option(self):
        html = render(
            '{% rich_select name="x" options=opts %}',
            {"opts": self.OPTIONS},
        )
        assert "rich-select-option-badge" in html
        assert "Admin" in html

    def test_description_option(self):
        html = render(
            '{% rich_select name="x" options=opts %}',
            {"opts": self.OPTIONS},
        )
        assert "rich-select-option-desc" in html
        assert "Engineering" in html

    def test_disabled(self):
        html = render(
            '{% rich_select name="x" options=opts disabled=True %}',
            {"opts": self.OPTIONS},
        )
        assert "rich-select--disabled" in html

    def test_searchable(self):
        html = render(
            '{% rich_select name="x" options=opts searchable=True %}',
            {"opts": self.OPTIONS},
        )
        assert "rich-select-search" in html
        assert "rich-select-search-input" in html

    def test_label(self):
        html = render(
            '{% rich_select name="x" options=opts label="Assignee" %}',
            {"opts": self.OPTIONS},
        )
        assert "form-label" in html
        assert "Assignee" in html

    def test_custom_event(self):
        html = render(
            '{% rich_select name="x" options=opts event="pick_user" %}',
            {"opts": self.OPTIONS},
        )
        assert 'dj-click="pick_user"' in html

    def test_empty_options(self):
        html = render('{% rich_select name="x" %}')
        assert "rich-select" in html
        assert "rich-select-option" not in html

    def test_selected_shows_rich_display(self):
        html = render(
            '{% rich_select name="x" options=opts value="bob" %}',
            {"opts": self.OPTIONS},
        )
        # The trigger should show Bob with badge, not just plain text
        # The trigger area contains the selected option's rich display
        assert "Bob" in html
        assert 'value="bob"' in html

    def test_hidden_input(self):
        html = render(
            '{% rich_select name="user" options=opts value="alice" %}',
            {"opts": self.OPTIONS},
        )
        assert 'type="hidden"' in html
        assert 'name="user"' in html
        assert 'value="alice"' in html


# ===========================================================================
# Data Grid Template Tag
# ===========================================================================


class TestDataGrid:
    COLUMNS = [
        {"key": "name", "label": "Name"},
        {"key": "email", "label": "Email"},
        {"key": "role", "label": "Role", "editable": False},
    ]
    ROWS = [
        {"id": "1", "name": "Alice", "email": "alice@ex.com", "role": "Admin"},
        {"id": "2", "name": "Bob", "email": "bob@ex.com", "role": "User"},
    ]

    def test_basic_render(self):
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert 'class="data-grid-wrapper' in html
        assert 'role="grid"' in html
        assert "Alice" in html
        assert "Bob" in html

    def test_header_cells(self):
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert "data-grid-header-cell" in html
        assert 'data-col-key="name"' in html
        assert 'data-col-key="email"' in html

    def test_editable_cells(self):
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert 'data-editable="true"' in html

    def test_non_editable_cells(self):
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        # Role column has editable=False, so should NOT have data-editable
        # Count occurrences — name and email are editable (4 cells), role is not (2 cells)
        assert html.count('data-editable="true"') == 4  # 2 rows x 2 editable cols

    def test_row_keys(self):
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert 'data-row-key="1"' in html
        assert 'data-row-key="2"' in html

    def test_custom_row_key(self):
        rows = [
            {"uid": "a", "name": "Alice"},
            {"uid": "b", "name": "Bob"},
        ]
        cols = [{"key": "name", "label": "Name"}]
        html = render(
            '{% data_grid columns=cols rows=rows row_key="uid" %}',
            {"cols": cols, "rows": rows},
        )
        assert 'data-row-key="a"' in html
        assert 'data-row-key="b"' in html

    def test_striped(self):
        html = render(
            '{% data_grid columns=cols rows=rows striped=True %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert "data-grid-striped" in html

    def test_compact(self):
        html = render(
            '{% data_grid columns=cols rows=rows compact=True %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert "data-grid-compact" in html

    def test_edit_event(self):
        html = render(
            '{% data_grid columns=cols rows=rows edit_event="my_edit" %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert 'data-edit-event="my_edit"' in html

    def test_resizable(self):
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert 'data-resizable="true"' in html

    def test_keyboard_nav(self):
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert 'data-keyboard-nav="true"' in html

    def test_frozen_left(self):
        html = render(
            '{% data_grid columns=cols rows=rows frozen_left=1 %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert "data-grid-frozen-left" in html

    def test_frozen_right(self):
        html = render(
            '{% data_grid columns=cols rows=rows frozen_right=1 %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert "data-grid-frozen-right" in html

    def test_new_row_event(self):
        html = render(
            '{% data_grid columns=cols rows=rows new_row_event="add_row" %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert "data-grid-add-btn" in html
        assert 'dj-click="add_row"' in html
        assert "+ Add Row" in html

    def test_delete_row_event(self):
        html = render(
            '{% data_grid columns=cols rows=rows delete_row_event="del_row" %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert "data-grid-delete-btn" in html
        assert 'dj-click="del_row"' in html
        assert "data-grid-actions-col" in html

    def test_custom_class(self):
        html = render(
            '{% data_grid columns=cols rows=rows custom_class="my-grid" %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert "my-grid" in html

    def test_empty_grid(self):
        html = render('{% data_grid %}')
        assert "data-grid-wrapper" in html
        assert "data-grid-row" not in html

    def test_column_width(self):
        cols = [{"key": "name", "label": "Name", "width": "200px"}]
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": cols, "rows": self.ROWS},
        )
        assert "200px" in html

    def test_cell_tabindex(self):
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert 'tabindex="-1"' in html

    def test_edit_trigger_hidden(self):
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": self.COLUMNS, "rows": self.ROWS},
        )
        assert "data-grid-edit-trigger" in html
        assert 'style="display:none"' in html


# ===========================================================================
# Rust Handler Tests
# ===========================================================================


class TestRichSelectRustHandler:
    def test_basic_render(self):
        from djust_components.rust_handlers import RichSelectHandler, _parse_args
        handler = RichSelectHandler()
        opts = [
            {"value": "a", "label": "Alice"},
            {"value": "b", "label": "Bob"},
        ]
        result = handler.render(
            ['name="assignee"', 'value="a"'],
            {"options": opts, "assignee_options": opts},
        )
        # The handler delegates to the template tag, so minimal check:
        assert "rich-select" in result

    def test_handler_with_options_var(self):
        from djust_components.rust_handlers import RichSelectHandler
        handler = RichSelectHandler()
        opts = [{"value": "x", "label": "X"}]
        result = handler.render(
            ['name="pick"', "options=opts"],
            {"opts": opts},
        )
        assert "rich-select" in result


class TestDataGridRustHandler:
    def test_basic_render(self):
        from djust_components.rust_handlers import DataGridHandler
        handler = DataGridHandler()
        cols = [{"key": "name", "label": "Name"}]
        rows = [{"id": "1", "name": "Test"}]
        result = handler.render(
            ['edit_event="my_edit"'],
            {"columns": cols, "rows": rows},
        )
        assert "data-grid" in result

    def test_handler_with_vars(self):
        from djust_components.rust_handlers import DataGridHandler
        handler = DataGridHandler()
        cols = [{"key": "a", "label": "A"}]
        rows = [{"id": "1", "a": "val"}]
        result = handler.render(
            ["columns=cols", "rows=rows"],
            {"cols": cols, "rows": rows},
        )
        assert "data-grid-wrapper" in result


# ===========================================================================
# Component Class Tests
# ===========================================================================


class TestRichSelectComponent:
    def test_basic_render(self):
        from djust_components.components.rich_select import RichSelect
        rs = RichSelect(
            name="user",
            options=[{"value": "a", "label": "Alice"}],
            value="a",
        )
        html = str(rs)
        assert "rich-select" in html
        assert "Alice" in html
        assert 'value="a"' in html

    def test_empty_options(self):
        from djust_components.components.rich_select import RichSelect
        rs = RichSelect(name="x")
        html = str(rs)
        assert "rich-select" in html

    def test_disabled(self):
        from djust_components.components.rich_select import RichSelect
        rs = RichSelect(name="x", disabled=True)
        html = str(rs)
        assert "rich-select--disabled" in html


class TestDataGridComponent:
    def test_basic_render(self):
        from djust_components.components.data_grid import DataGrid
        grid = DataGrid(
            columns=[{"key": "name", "label": "Name"}],
            rows=[{"id": "1", "name": "Alice"}],
        )
        html = str(grid)
        assert "data-grid-wrapper" in html
        assert "Alice" in html

    def test_empty_grid(self):
        from djust_components.components.data_grid import DataGrid
        grid = DataGrid()
        html = str(grid)
        assert "data-grid" in html

    def test_striped_compact(self):
        from djust_components.components.data_grid import DataGrid
        grid = DataGrid(striped=True, compact=True)
        html = str(grid)
        assert "data-grid-striped" in html
        assert "data-grid-compact" in html

    def test_delete_row_event(self):
        from djust_components.components.data_grid import DataGrid
        grid = DataGrid(
            columns=[{"key": "a", "label": "A"}],
            rows=[{"id": "1", "a": "x"}],
            delete_row_event="del",
        )
        html = str(grid)
        assert "data-grid-delete-btn" in html
        assert 'dj-click="del"' in html


# ===========================================================================
# XSS Escaping Tests
# ===========================================================================


class TestXSSEscaping:
    """Verify that user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_raw_script(self, html):
        assert "<script>" not in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html or "&#x27;" in html

    # --- Rich Select XSS ---

    def test_rich_select_name_xss(self):
        html = render(
            '{% rich_select name=bad options=opts %}',
            {"bad": self.XSS_ATTR, "opts": []},
        )
        self._assert_attr_escaped(html)

    def test_rich_select_label_xss(self):
        html = render(
            '{% rich_select name="x" label=bad %}',
            {"bad": self.XSS},
        )
        self._assert_no_raw_script(html)
        assert "&lt;script&gt;" in html

    def test_rich_select_placeholder_xss(self):
        html = render(
            '{% rich_select name="x" placeholder=bad %}',
            {"bad": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_rich_select_option_label_xss(self):
        opts = [{"value": "a", "label": self.XSS}]
        html = render(
            '{% rich_select name="x" options=opts %}',
            {"opts": opts},
        )
        self._assert_no_raw_script(html)
        assert "&lt;script&gt;" in html

    def test_rich_select_option_description_xss(self):
        opts = [{"value": "a", "label": "A", "description": self.XSS}]
        html = render(
            '{% rich_select name="x" options=opts %}',
            {"opts": opts},
        )
        self._assert_no_raw_script(html)

    def test_rich_select_option_badge_xss(self):
        opts = [{"value": "a", "label": "A", "badge": self.XSS}]
        html = render(
            '{% rich_select name="x" options=opts %}',
            {"opts": opts},
        )
        self._assert_no_raw_script(html)

    def test_rich_select_option_icon_xss(self):
        opts = [{"value": "a", "label": "A", "icon": self.XSS}]
        html = render(
            '{% rich_select name="x" options=opts %}',
            {"opts": opts},
        )
        self._assert_no_raw_script(html)

    def test_rich_select_option_image_xss(self):
        opts = [{"value": "a", "label": "A", "image": self.XSS_ATTR}]
        html = render(
            '{% rich_select name="x" options=opts %}',
            {"opts": opts},
        )
        self._assert_attr_escaped(html)

    def test_rich_select_option_value_xss(self):
        opts = [{"value": self.XSS_ATTR, "label": "A"}]
        html = render(
            '{% rich_select name="x" options=opts %}',
            {"opts": opts},
        )
        self._assert_attr_escaped(html)

    def test_rich_select_event_xss(self):
        html = render(
            '{% rich_select name="x" options=opts event=bad %}',
            {"bad": self.XSS_ATTR, "opts": [{"value": "a", "label": "A"}]},
        )
        self._assert_attr_escaped(html)

    # --- Data Grid XSS ---

    def test_data_grid_cell_value_xss(self):
        cols = [{"key": "name", "label": "Name"}]
        rows = [{"id": "1", "name": self.XSS}]
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": cols, "rows": rows},
        )
        self._assert_no_raw_script(html)
        assert "&lt;script&gt;" in html

    def test_data_grid_column_label_xss(self):
        cols = [{"key": "x", "label": self.XSS}]
        rows = [{"id": "1", "x": "ok"}]
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": cols, "rows": rows},
        )
        self._assert_no_raw_script(html)

    def test_data_grid_row_key_xss(self):
        cols = [{"key": "x", "label": "X"}]
        rows = [{"id": self.XSS_ATTR, "x": "ok"}]
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": cols, "rows": rows},
        )
        self._assert_attr_escaped(html)

    def test_data_grid_col_key_xss(self):
        cols = [{"key": self.XSS_ATTR, "label": "X"}]
        rows = [{"id": "1"}]
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": cols, "rows": rows},
        )
        self._assert_attr_escaped(html)

    def test_data_grid_edit_event_xss(self):
        cols = [{"key": "x", "label": "X"}]
        rows = [{"id": "1", "x": "ok"}]
        html = render(
            '{% data_grid columns=cols rows=rows edit_event=bad %}',
            {"cols": cols, "rows": rows, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_data_grid_custom_class_xss(self):
        cols = [{"key": "x", "label": "X"}]
        rows = [{"id": "1", "x": "ok"}]
        html = render(
            '{% data_grid columns=cols rows=rows custom_class=bad %}',
            {"cols": cols, "rows": rows, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_data_grid_new_row_event_xss(self):
        html = render(
            '{% data_grid columns=cols rows=rows new_row_event=bad %}',
            {"cols": [{"key": "x", "label": "X"}], "rows": [], "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_data_grid_delete_row_event_xss(self):
        cols = [{"key": "x", "label": "X"}]
        rows = [{"id": "1", "x": "ok"}]
        html = render(
            '{% data_grid columns=cols rows=rows delete_row_event=bad %}',
            {"cols": cols, "rows": rows, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_data_grid_column_width_xss(self):
        cols = [{"key": "x", "label": "X", "width": self.XSS_ATTR}]
        rows = [{"id": "1", "x": "ok"}]
        html = render(
            '{% data_grid columns=cols rows=rows %}',
            {"cols": cols, "rows": rows},
        )
        self._assert_attr_escaped(html)
