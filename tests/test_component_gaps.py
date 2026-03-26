"""Tests for 5 component gap fixes: Virtual List, Kanban Board, Combobox multi-select,
Date Picker range, Code Block syntax highlighting."""
import json

from django.template import Template, Context
import pytest


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ===========================================================================
# 1. Virtual List — Rust handler JSON string resolution
# ===========================================================================

class TestVirtualListDictResolution:
    """VirtualListHandler should deserialize JSON strings to list-of-dicts."""

    def test_items_as_list_of_dicts(self):
        """Pass items as Python list-of-dicts via context, verify rendered HTML."""
        from djust_components.rust_handlers import VirtualListHandler
        handler = VirtualListHandler()
        ctx = {"my_items": [{"label": "Alpha"}, {"label": "Beta"}]}
        html = handler.render(['items=my_items', 'total=2'], ctx)
        assert "Alpha" in html
        assert "Beta" in html

    def test_items_as_json_string(self):
        """JSON string in context should be deserialized by the handler."""
        from djust_components.rust_handlers import VirtualListHandler
        handler = VirtualListHandler()
        items_json = json.dumps([{"label": "Foo"}, {"label": "Bar"}])
        ctx = {"my_items": items_json}
        html = handler.render(['items=my_items', 'total=2'], ctx)
        assert "Foo" in html
        assert "Bar" in html

    def test_items_empty_list(self):
        """Empty list renders no items."""
        html = render('{% virtual_list items=items total=0 %}', {"items": []})
        assert "vl-item" not in html
        assert "Showing 0 of 0" in html

    def test_items_missing_from_context(self):
        """Missing variable falls back to empty list."""
        from djust_components.rust_handlers import VirtualListHandler
        handler = VirtualListHandler()
        html = handler.render(['items=nonexistent'], {})
        assert "Showing 0 of 0" in html

    def test_items_invalid_json_string(self):
        """Invalid JSON string falls back to empty list."""
        from djust_components.rust_handlers import VirtualListHandler
        handler = VirtualListHandler()
        ctx = {"my_items": "{not valid json["}
        html = handler.render(['items=my_items', 'total=0'], ctx)
        assert "virtual-list" in html


# ===========================================================================
# 2. Kanban Board — Rust handler JSON string resolution
# ===========================================================================

class TestKanbanBoardDictResolution:
    """KanbanBoardHandler should deserialize JSON strings to list-of-dicts."""

    def test_columns_as_list_of_dicts(self):
        """Pass columns with nested cards, verify rendered HTML."""
        from djust_components.rust_handlers import KanbanBoardHandler
        handler = KanbanBoardHandler()
        cols = [
            {"id": "todo", "title": "To Do", "cards": [
                {"id": "c1", "title": "Task A"}
            ]},
        ]
        ctx = {"my_cols": cols}
        html = handler.render(['columns=my_cols'], ctx)
        assert "To Do" in html
        assert "Task A" in html

    def test_columns_as_json_string(self):
        """JSON string in context should be deserialized."""
        from djust_components.rust_handlers import KanbanBoardHandler
        handler = KanbanBoardHandler()
        cols = [{"id": "done", "title": "Done", "cards": []}]
        ctx = {"my_cols": json.dumps(cols)}
        html = handler.render(['columns=my_cols'], ctx)
        assert "Done" in html

    def test_columns_empty(self):
        """Empty columns renders empty kanban."""
        html = render('{% kanban_board columns=cols %}', {"cols": []})
        assert 'class="kanban"' in html
        assert "kanban-col" not in html

    def test_columns_missing_from_context(self):
        """Missing variable falls back to empty."""
        from djust_components.rust_handlers import KanbanBoardHandler
        handler = KanbanBoardHandler()
        html = handler.render(['columns=nonexistent'], {})
        assert "kanban" in html

    def test_columns_invalid_json_string(self):
        """Invalid JSON falls back to empty columns."""
        from djust_components.rust_handlers import KanbanBoardHandler
        handler = KanbanBoardHandler()
        ctx = {"my_cols": "not json"}
        html = handler.render(['columns=my_cols'], ctx)
        assert "kanban" in html


# ===========================================================================
# 3. Combobox — Multi-select mode
# ===========================================================================

class TestComboboxMultiSelect:
    """Combobox should support multi-select with tags."""

    def test_single_select_backward_compat(self):
        """Existing single-select behavior unchanged when multiple not set."""
        html = render(
            '{% combobox name="color" value="red" options=opts %}',
            {"opts": [{"value": "red", "label": "Red"}, {"value": "blue", "label": "Blue"}]}
        )
        assert "combobox-tags" not in html
        assert 'name="color"' in html
        assert "Red" in html

    def test_multiple_true_renders_tags(self):
        """Selected values rendered as tag chips in multi mode."""
        html = render(
            '{% combobox name="colors" multiple=True selected=sel options=opts %}',
            {
                "sel": ["red", "blue"],
                "opts": [
                    {"value": "red", "label": "Red"},
                    {"value": "blue", "label": "Blue"},
                    {"value": "green", "label": "Green"},
                ],
            }
        )
        assert "combobox-tags" in html
        assert "combobox-tag" in html
        # Both selected values should appear as tags
        assert ">Red<" in html or "Red</span>" in html
        assert ">Blue<" in html or "Blue</span>" in html

    def test_multiple_hidden_inputs(self):
        """Each selected value gets a hidden input for form submission."""
        html = render(
            '{% combobox name="colors" multiple=True selected=sel options=opts %}',
            {
                "sel": ["red", "blue"],
                "opts": [
                    {"value": "red", "label": "Red"},
                    {"value": "blue", "label": "Blue"},
                ],
            }
        )
        assert 'type="hidden"' in html
        assert 'name="colors[]"' in html
        assert 'value="red"' in html
        assert 'value="blue"' in html

    def test_multiple_options_marked_selected(self):
        """Selected options have the selected class."""
        html = render(
            '{% combobox name="colors" multiple=True selected=sel options=opts %}',
            {
                "sel": ["red"],
                "opts": [
                    {"value": "red", "label": "Red"},
                    {"value": "blue", "label": "Blue"},
                ],
            }
        )
        # Red option should be selected, Blue should not
        assert "combobox-option-selected" in html

    def test_multiple_empty_selected(self):
        """No tags when selected list is empty."""
        html = render(
            '{% combobox name="colors" multiple=True selected=sel options=opts %}',
            {
                "sel": [],
                "opts": [{"value": "red", "label": "Red"}],
            }
        )
        # Tags container should be empty or absent
        assert "combobox-tag " not in html

    def test_multiple_xss_in_selected_values(self):
        """XSS payloads in selected values are escaped."""
        xss = '<script>alert("xss")</script>'
        html = render(
            '{% combobox name="colors" multiple=True selected=sel options=opts %}',
            {
                "sel": [xss],
                "opts": [{"value": xss, "label": xss}],
            }
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


# ===========================================================================
# 4. Date Picker — Range selection
# ===========================================================================

class TestDatePickerRange:
    """Date picker should support range selection mode."""

    def test_single_date_backward_compat(self):
        """Existing behavior unchanged when range not set."""
        html = render(
            '{% date_picker year=2026 month=3 selected="2026-03-15" %}',
        )
        assert "dp-day-selected" in html
        assert "dp-day-range-start" not in html
        assert "dp-day-in-range" not in html

    def test_range_start_end_classes(self):
        """Days between start and end get dp-day-in-range class."""
        html = render(
            '{% date_picker year=2026 month=3 range=True range_start="2026-03-10" range_end="2026-03-15" %}',
        )
        assert "dp-day-in-range" in html

    def test_range_start_class(self):
        """Start date gets dp-day-range-start class."""
        html = render(
            '{% date_picker year=2026 month=3 range=True range_start="2026-03-10" range_end="2026-03-15" %}',
        )
        assert "dp-day-range-start" in html

    def test_range_end_class(self):
        """End date gets dp-day-range-end class."""
        html = render(
            '{% date_picker year=2026 month=3 range=True range_start="2026-03-10" range_end="2026-03-15" %}',
        )
        assert "dp-day-range-end" in html

    def test_range_hidden_inputs(self):
        """Two hidden inputs for start and end in range mode."""
        html = render(
            '{% date_picker year=2026 month=3 range=True range_start="2026-03-10" range_end="2026-03-15" name="date" %}',
        )
        assert 'name="date_start"' in html
        assert 'name="date_end"' in html

    def test_range_display_value(self):
        """Selected value shows 'start - end' in range mode."""
        html = render(
            '{% date_picker year=2026 month=3 range=True range_start="2026-03-10" range_end="2026-03-15" %}',
        )
        assert "2026-03-10" in html
        assert "2026-03-15" in html

    def test_range_no_dates_selected(self):
        """No range classes when both start and end are empty."""
        html = render(
            '{% date_picker year=2026 month=3 range=True range_start="" range_end="" %}',
        )
        assert "dp-day-range-start" not in html
        assert "dp-day-range-end" not in html
        assert "dp-day-in-range" not in html


# ===========================================================================
# 5. Code Block — Syntax highlighting
# ===========================================================================

class TestCodeBlockHighlight:
    """Code block should support syntax highlighting via highlight.js."""

    def test_highlight_default_true(self):
        """By default, renders with highlight loader script."""
        html = render('{% code_block code="print(1)" language="python" %}')
        assert "hljs" in html or "highlight" in html.lower()

    def test_highlight_false_no_script(self):
        """No highlight script when highlight=False."""
        html = render('{% code_block code="print(1)" language="python" highlight=False %}')
        assert "hljs" not in html
        # Code should still render
        assert "print(1)" in html

    def test_highlight_theme_attribute(self):
        """Theme passed as data attribute."""
        html = render('{% code_block code="x" language="js" theme="monokai" %}')
        assert "monokai" in html

    def test_code_escaped(self):
        """Code content is still properly escaped with highlighting on."""
        html = render('{% code_block code=code language="html" %}', {"code": "<div>test</div>"})
        assert "&lt;div&gt;" in html
        assert "<div>test</div>" not in html  # must be escaped

    def test_language_class_preserved(self):
        """language-X class present for hljs detection."""
        html = render('{% code_block code="x" language="python" %}')
        assert 'class="language-python"' in html

    def test_xss_in_language(self):
        """Script injection in language param is escaped."""
        xss = '"><script>alert(1)</script>'
        html = render('{% code_block code="x" language=lang %}', {"lang": xss})
        # The language value must be escaped in the lang span and code class
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
        # The unescaped XSS payload must not appear in the language display or code class
        assert 'class="language-"><script>' not in html
        assert f'>{xss}<' not in html
