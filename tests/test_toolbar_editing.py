"""Tests for toolbar/editing components: Toolbar, Inline Edit, Filter Bar."""
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
# Toolbar (#87)
# ===========================================================================

class TestToolbar:
    def test_basic_toolbar_renders(self):
        html = render(
            '{% toolbar id="tb" %}'
            '<button>Save</button>'
            '{% endtoolbar %}'
        )
        assert 'class="dj-toolbar' in html
        assert 'id="tb"' in html
        assert 'role="toolbar"' in html
        assert "Save" in html

    def test_toolbar_sizes(self):
        for size in ("sm", "md", "lg"):
            html = render(
                f'{{% toolbar size="{size}" %}}'
                '<button>X</button>'
                '{% endtoolbar %}'
            )
            assert f"dj-toolbar--{size}" in html

    def test_toolbar_variants(self):
        for variant in ("default", "flat"):
            html = render(
                f'{{% toolbar variant="{variant}" %}}'
                '<button>X</button>'
                '{% endtoolbar %}'
            )
            assert f"dj-toolbar--{variant}" in html

    def test_toolbar_custom_class(self):
        html = render(
            '{% toolbar class="my-bar" %}'
            '<button>X</button>'
            '{% endtoolbar %}'
        )
        assert "my-bar" in html

    def test_toolbar_separator(self):
        html = render(
            '{% toolbar %}'
            '<button>A</button>'
            '{% toolbar_separator %}'
            '<button>B</button>'
            '{% endtoolbar %}'
        )
        assert 'dj-toolbar__separator' in html
        assert 'role="separator"' in html

    def test_toolbar_overflow(self):
        html = render(
            '{% toolbar %}'
            '<button>Main</button>'
            '{% toolbar_overflow %}'
            '<button>Hidden</button>'
            '{% endtoolbar_overflow %}'
            '{% endtoolbar %}'
        )
        assert 'dj-toolbar__overflow' in html
        assert 'dj-toolbar__overflow-trigger' in html
        assert 'dj-toolbar__overflow-menu' in html
        assert "Hidden" in html

    def test_toolbar_groups_content(self):
        html = render(
            '{% toolbar %}'
            '<button>One</button>'
            '{% endtoolbar %}'
        )
        assert 'dj-toolbar__group' in html
        assert "One" in html


# ===========================================================================
# Inline Edit (#88)
# ===========================================================================

class TestInlineEdit:
    def test_display_mode(self):
        html = render(
            '{% inline_edit value=title event="update_title" %}',
            {"title": "Hello World"},
        )
        assert "dj-inline-edit" in html
        assert "Hello World" in html
        assert "dj-inline-edit__display" in html
        assert "dj-inline-edit__icon" in html
        assert 'dj-click="inline_edit_start"' in html
        assert 'title="Click to edit"' in html

    def test_editing_mode(self):
        html = render(
            '{% inline_edit value=title event="update_title" editing=is_editing %}',
            {"title": "Hello", "is_editing": True},
        )
        assert "dj-inline-edit--editing" in html
        assert "dj-inline-edit__input" in html
        assert 'value="Hello"' in html
        assert 'dj-keydown.enter="update_title"' in html
        assert 'dj-blur="update_title"' in html
        assert 'dj-keydown.escape="inline_edit_cancel"' in html
        assert "autofocus" in html

    def test_custom_field_attribute(self):
        html = render(
            '{% inline_edit value="x" event="save" field="name" %}',
        )
        assert 'data-field="name"' in html

    def test_custom_input_type(self):
        html = render(
            '{% inline_edit value="5" event="save" type="number" editing=True %}',
            {"True": True},  # workaround for literal True
        )
        # The editing=True needs to resolve. Let's use context variable.
        html = render(
            '{% inline_edit value="5" event="save" type="number" editing=editing %}',
            {"editing": True},
        )
        assert 'type="number"' in html

    def test_placeholder(self):
        html = render(
            '{% inline_edit value="" event="save" placeholder="Enter name" editing=editing %}',
            {"editing": True},
        )
        assert 'placeholder="Enter name"' in html

    def test_custom_class(self):
        html = render(
            '{% inline_edit value="x" event="save" class="my-edit" %}',
        )
        assert "my-edit" in html


# ===========================================================================
# Filter Bar (#166)
# ===========================================================================

class TestFilterBar:
    def test_basic_filter_bar_renders(self):
        html = render(
            '{% filter_bar id="fb" %}'
            '{% filter_search name="q" %}'
            '{% endfilter_bar %}'
        )
        assert 'class="dj-filter-bar' in html
        assert 'id="fb"' in html
        assert 'role="search"' in html

    def test_filter_select(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_select name="status" options=statuses %}'
            '{% endfilter_bar %}',
            {"statuses": [
                {"value": "active", "label": "Active"},
                {"value": "inactive", "label": "Inactive"},
            ]},
        )
        assert 'dj-filter-bar__select' in html
        assert 'name="status"' in html
        assert 'value="active"' in html
        assert "Active" in html
        assert "Inactive" in html
        assert 'dj-change="filter_change"' in html

    def test_filter_select_with_value(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_select name="status" options=statuses value=current %}'
            '{% endfilter_bar %}',
            {
                "statuses": [
                    {"value": "active", "label": "Active"},
                    {"value": "inactive", "label": "Inactive"},
                ],
                "current": "active",
            },
        )
        assert "selected" in html

    def test_filter_select_simple_options(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_select name="color" options=colors %}'
            '{% endfilter_bar %}',
            {"colors": ["red", "blue", "green"]},
        )
        assert 'value="red"' in html
        assert "blue" in html

    def test_filter_date_range(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_date_range name="dates" label="Date Range" %}'
            '{% endfilter_bar %}'
        )
        assert 'dj-filter-bar__date-range' in html
        assert 'type="date"' in html
        assert 'name="dates_start"' in html
        assert 'name="dates_end"' in html
        assert "Date Range" in html

    def test_filter_date_range_with_values(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_date_range name="dates" start=start end=end %}'
            '{% endfilter_bar %}',
            {"start": "2026-01-01", "end": "2026-12-31"},
        )
        assert 'value="2026-01-01"' in html
        assert 'value="2026-12-31"' in html

    def test_filter_search(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_search name="q" placeholder="Search..." %}'
            '{% endfilter_bar %}'
        )
        assert 'dj-filter-bar__search' in html
        assert 'type="search"' in html
        assert 'name="q"' in html
        assert 'placeholder="Search..."' in html
        assert 'dj-input="filter_change"' in html

    def test_filter_search_with_debounce(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_search name="q" debounce="500" %}'
            '{% endfilter_bar %}'
        )
        assert 'dj-debounce="500"' in html

    def test_custom_event(self):
        html = render(
            '{% filter_bar event="my_filter" %}'
            '{% filter_search name="q" %}'
            '{% endfilter_bar %}'
        )
        assert 'dj-input="my_filter"' in html

    def test_custom_class(self):
        html = render(
            '{% filter_bar class="my-filters" %}'
            '{% filter_search name="q" %}'
            '{% endfilter_bar %}'
        )
        assert "my-filters" in html

    def test_clear_button_with_values(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_search name="q" value=query %}'
            '{% endfilter_bar %}',
            {"query": "test"},
        )
        assert "dj-filter-bar__clear" in html
        assert "Clear filters" in html
        assert 'dj-click="filter_clear"' in html

    def test_no_clear_button_without_values(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_search name="q" %}'
            '{% endfilter_bar %}'
        )
        assert "dj-filter-bar__clear" not in html

    def test_combined_filters(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_select name="status" options=statuses %}'
            '{% filter_date_range name="dates" %}'
            '{% filter_search name="q" %}'
            '{% endfilter_bar %}',
            {"statuses": ["open", "closed"]},
        )
        assert 'dj-filter-bar__select' in html
        assert 'dj-filter-bar__date-range' in html
        assert 'dj-filter-bar__search' in html

    def test_custom_clear_event(self):
        html = render(
            '{% filter_bar clear_event="reset_filters" %}'
            '{% filter_search name="q" value=query %}'
            '{% endfilter_bar %}',
            {"query": "x"},
        )
        assert 'dj-click="reset_filters"' in html


# ===========================================================================
# XSS Escaping
# ===========================================================================

class TestXSSEscaping:
    """Verify that user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html or "script" not in html.lower().replace("&lt;script&gt;", "")

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # --- Toolbar ---

    def test_toolbar_id_xss(self):
        html = render(
            '{% toolbar id=bad %}<button>X</button>{% endtoolbar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_toolbar_class_xss(self):
        html = render(
            '{% toolbar class=bad %}<button>X</button>{% endtoolbar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_toolbar_size_xss(self):
        html = render(
            '{% toolbar size=bad %}<button>X</button>{% endtoolbar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_toolbar_variant_xss(self):
        html = render(
            '{% toolbar variant=bad %}<button>X</button>{% endtoolbar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Inline Edit ---

    def test_inline_edit_value_xss(self):
        html = render(
            '{% inline_edit value=xss event="save" %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_inline_edit_value_attr_xss(self):
        html = render(
            '{% inline_edit value=bad event="save" editing=editing %}',
            {"bad": self.XSS_ATTR, "editing": True},
        )
        self._assert_attr_escaped(html)

    def test_inline_edit_event_xss(self):
        html = render(
            '{% inline_edit value="x" event=bad editing=editing %}',
            {"bad": self.XSS_ATTR, "editing": True},
        )
        self._assert_attr_escaped(html)

    def test_inline_edit_field_xss(self):
        html = render(
            '{% inline_edit value="x" event="save" field=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_inline_edit_placeholder_xss(self):
        html = render(
            '{% inline_edit value="" event="save" placeholder=bad editing=editing %}',
            {"bad": self.XSS_ATTR, "editing": True},
        )
        self._assert_attr_escaped(html)

    def test_inline_edit_class_xss(self):
        html = render(
            '{% inline_edit value="x" event="save" class=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Filter Bar ---

    def test_filter_bar_id_xss(self):
        html = render(
            '{% filter_bar id=bad %}{% filter_search name="q" %}{% endfilter_bar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_filter_bar_class_xss(self):
        html = render(
            '{% filter_bar class=bad %}{% filter_search name="q" %}{% endfilter_bar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_filter_bar_event_xss(self):
        html = render(
            '{% filter_bar event=bad %}{% filter_search name="q" %}{% endfilter_bar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_filter_bar_clear_event_xss(self):
        html = render(
            '{% filter_bar clear_event=bad %}'
            '{% filter_search name="q" value=query %}'
            '{% endfilter_bar %}',
            {"bad": self.XSS_ATTR, "query": "x"},
        )
        self._assert_attr_escaped(html)

    def test_filter_select_name_xss(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_select name=bad options=opts %}'
            '{% endfilter_bar %}',
            {"bad": self.XSS_ATTR, "opts": ["a"]},
        )
        self._assert_attr_escaped(html)

    def test_filter_search_placeholder_xss(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_search name="q" placeholder=bad %}'
            '{% endfilter_bar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_filter_search_value_xss(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_search name="q" value=xss %}'
            '{% endfilter_bar %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_filter_date_range_label_xss(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_date_range name="d" label=xss %}'
            '{% endfilter_bar %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_filter_date_range_name_xss(self):
        html = render(
            '{% filter_bar %}'
            '{% filter_date_range name=bad %}'
            '{% endfilter_bar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)
