"""Tests for Button & Control Variant components: Toggle Group, FAB, Split Button.

Covers rendering, parameters, disabled/loading state, XSS escaping,
and Rust handler delegation.
"""
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
from django.utils.safestring import SafeData
import pytest

from djust_components.rust_handlers import (
    _parse_args,
    ToggleGroupHandler,
    FabHandler,
    SplitButtonHandler,
)


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ═══════════════════════════════════════════════════════════════════════════
# 1. Toggle Group
# ═══════════════════════════════════════════════════════════════════════════


class TestToggleGroup:
    def test_renders_basic(self):
        html = render(
            '{% toggle_group name="view" options=opts value="grid" %}',
            {"opts": [
                {"value": "grid", "label": "Grid"},
                {"value": "list", "label": "List"},
            ]},
        )
        assert "toggle-group" in html
        assert "toggle-group-btn" in html
        assert "Grid" in html
        assert "List" in html

    def test_active_state(self):
        html = render(
            '{% toggle_group name="view" options=opts value="list" %}',
            {"opts": [
                {"value": "grid", "label": "Grid"},
                {"value": "list", "label": "List"},
            ]},
        )
        assert "toggle-group-btn--active" in html
        assert 'aria-pressed="true"' in html
        assert 'aria-pressed="false"' in html

    def test_multi_mode(self):
        html = render(
            '{% toggle_group name="filters" options=opts value=sel mode="multi" %}',
            {
                "opts": [
                    {"value": "a", "label": "Alpha"},
                    {"value": "b", "label": "Beta"},
                    {"value": "c", "label": "Gamma"},
                ],
                "sel": ["a", "c"],
            },
        )
        assert 'data-mode="multi"' in html
        # a and c should be active, b should not
        # Count active buttons
        assert html.count("toggle-group-btn--active") == 2

    def test_event_attribute(self):
        html = render(
            '{% toggle_group name="v" options=opts value="" event="pick" %}',
            {"opts": [{"value": "x", "label": "X"}]},
        )
        assert 'dj-click="pick"' in html
        assert 'data-value="x"' in html

    def test_disabled(self):
        html = render(
            '{% toggle_group name="v" options=opts value="" disabled=True %}',
            {"opts": [{"value": "x", "label": "X"}]},
        )
        assert " disabled" in html
        assert "toggle-group-disabled" in html
        assert "dj-click" not in html

    def test_size_sm(self):
        html = render(
            '{% toggle_group name="v" options=opts value="" size="sm" %}',
            {"opts": [{"value": "x", "label": "X"}]},
        )
        assert "toggle-group-sm" in html

    def test_size_lg(self):
        html = render(
            '{% toggle_group name="v" options=opts value="" size="lg" %}',
            {"opts": [{"value": "x", "label": "X"}]},
        )
        assert "toggle-group-lg" in html

    def test_icon_rendered(self):
        html = render(
            '{% toggle_group name="v" options=opts value="" %}',
            {"opts": [{"value": "x", "label": "X", "icon": "📊"}]},
        )
        assert "toggle-group-icon" in html

    def test_role_group(self):
        html = render(
            '{% toggle_group name="v" options=opts value="" %}',
            {"opts": []},
        )
        assert 'role="group"' in html

    def test_empty_options(self):
        html = render(
            '{% toggle_group name="v" options=opts value="" %}',
            {"opts": []},
        )
        assert "toggle-group" in html
        assert "toggle-group-btn" not in html

    def test_data_name(self):
        html = render(
            '{% toggle_group name="view_mode" options=opts value="" %}',
            {"opts": [{"value": "x", "label": "X"}]},
        )
        assert 'data-name="view_mode"' in html


# ═══════════════════════════════════════════════════════════════════════════
# 2. Floating Action Button
# ═══════════════════════════════════════════════════════════════════════════


class TestFab:
    def test_renders_basic(self):
        html = render('{% fab icon="+" event="create" %}')
        assert "fab-container" in html
        assert "fab" in html
        assert 'dj-click="create"' in html
        assert "+" in html

    def test_default_position(self):
        html = render('{% fab %}')
        assert "fab-bottom-right" in html

    def test_position_bottom_left(self):
        html = render('{% fab position="bottom-left" %}')
        assert "fab-bottom-left" in html

    def test_position_top_right(self):
        html = render('{% fab position="top-right" %}')
        assert "fab-top-right" in html

    def test_position_top_left(self):
        html = render('{% fab position="top-left" %}')
        assert "fab-top-left" in html

    def test_invalid_position_defaults(self):
        html = render('{% fab position="center" %}')
        assert "fab-bottom-right" in html

    def test_variant_primary(self):
        html = render('{% fab variant="primary" %}')
        assert "fab-primary" in html

    def test_variant_danger(self):
        html = render('{% fab variant="danger" %}')
        assert "fab-danger" in html

    def test_variant_success(self):
        html = render('{% fab variant="success" %}')
        assert "fab-success" in html

    def test_variant_secondary(self):
        html = render('{% fab variant="secondary" %}')
        assert "fab-secondary" in html

    def test_size_sm(self):
        html = render('{% fab size="sm" %}')
        assert "fab-sm" in html

    def test_size_lg(self):
        html = render('{% fab size="lg" %}')
        assert "fab-lg" in html

    def test_disabled(self):
        html = render('{% fab event="go" disabled=True %}')
        assert " disabled" in html
        assert "dj-click" not in html

    def test_label_aria(self):
        html = render('{% fab label="Add item" %}')
        assert 'aria-label="Add item"' in html

    def test_no_label_no_aria(self):
        html = render('{% fab %}')
        assert "aria-label" not in html

    def test_speed_dial_actions(self):
        html = render(
            '{% fab icon="+" event="main" actions=acts %}',
            {"acts": [
                {"icon": "📝", "event": "new_note", "label": "New Note"},
                {"icon": "📷", "event": "upload_photo", "label": "Upload Photo"},
            ]},
        )
        assert "fab-actions" in html
        assert "fab-action" in html
        assert 'dj-click="new_note"' in html
        assert 'dj-click="upload_photo"' in html
        assert 'aria-label="New Note"' in html

    def test_speed_dial_disabled(self):
        html = render(
            '{% fab disabled=True actions=acts %}',
            {"acts": [{"icon": "x", "event": "go", "label": "Go"}]},
        )
        # sub-actions should also be disabled
        assert html.count(" disabled") >= 2

    def test_no_event_no_click(self):
        html = render('{% fab %}')
        assert "dj-click" not in html

    def test_empty_actions(self):
        html = render('{% fab actions=acts %}', {"acts": []})
        assert "fab-actions" not in html


# ═══════════════════════════════════════════════════════════════════════════
# 3. Split Button
# ═══════════════════════════════════════════════════════════════════════════


class TestSplitButton:
    def test_renders_basic(self):
        html = render(
            '{% split_button label="Save" event="save" %}',
        )
        assert "split-btn" in html
        assert "split-btn-primary" in html
        assert "split-btn-toggle" in html
        assert "Save" in html
        assert 'dj-click="save"' in html

    def test_variant_danger(self):
        html = render('{% split_button label="Delete" variant="danger" %}')
        assert "split-btn-danger" in html

    def test_variant_secondary(self):
        html = render('{% split_button label="X" variant="secondary" %}')
        assert "split-btn-secondary" in html

    def test_variant_success(self):
        html = render('{% split_button label="X" variant="success" %}')
        assert "split-btn-success" in html

    def test_size_sm(self):
        html = render('{% split_button label="X" size="sm" %}')
        assert "split-btn-sm" in html

    def test_size_lg(self):
        html = render('{% split_button label="X" size="lg" %}')
        assert "split-btn-lg" in html

    def test_disabled(self):
        html = render('{% split_button label="X" event="go" disabled=True %}')
        assert " disabled" in html
        # Primary click should not be present
        assert 'dj-click="go"' not in html

    def test_loading(self):
        html = render('{% split_button label="X" event="go" loading=True %}')
        assert "split-btn-loading" in html
        assert "split-btn-spinner" in html
        assert " disabled" in html

    def test_options_menu(self):
        html = render(
            '{% split_button label="Save" event="save" options=opts %}',
            {"opts": [
                {"label": "Save as Draft", "event": "save_draft"},
                {"label": "Save & Close", "event": "save_close"},
            ]},
        )
        assert "split-btn-menu" in html
        assert "split-btn-option" in html
        assert "Save as Draft" in html
        assert "Save &amp; Close" in html
        assert 'dj-click="save_draft"' in html
        assert 'dj-click="save_close"' in html

    def test_menu_closed_by_default(self):
        html = render(
            '{% split_button label="X" options=opts %}',
            {"opts": [{"label": "A", "event": "a"}]},
        )
        assert 'data-open="false"' in html

    def test_menu_open(self):
        html = render(
            '{% split_button label="X" options=opts open=True %}',
            {"opts": [{"label": "A", "event": "a"}]},
        )
        assert 'data-open="true"' in html

    def test_toggle_event(self):
        html = render('{% split_button label="X" toggle_event="my_toggle" %}')
        assert 'dj-click="my_toggle"' in html

    def test_default_toggle_event(self):
        html = render('{% split_button label="X" %}')
        assert 'dj-click="toggle_split_menu"' in html

    def test_no_options_no_menu(self):
        html = render('{% split_button label="X" %}')
        assert "split-btn-menu" not in html

    def test_caret_present(self):
        html = render('{% split_button label="X" %}')
        assert "split-btn-caret" in html

    def test_options_disabled(self):
        html = render(
            '{% split_button label="X" disabled=True options=opts %}',
            {"opts": [{"label": "A", "event": "a"}]},
        )
        # options should not have dj-click when disabled
        assert 'dj-click="a"' not in html


# ═══════════════════════════════════════════════════════════════════════════
# 4. Rust Handler Delegation
# ═══════════════════════════════════════════════════════════════════════════


class TestRustHandlerToggleGroup:
    def test_basic_render(self):
        h = ToggleGroupHandler()
        ctx = {}
        out = h.render(
            ['name="view"', 'value="grid"', 'event="pick"',
             'options=[{"value":"grid","label":"Grid"},{"value":"list","label":"List"}]'],
            ctx,
        )
        assert "toggle-group" in out
        assert "Grid" in out
        assert "List" in out
        assert "toggle-group-btn--active" in out

    def test_disabled(self):
        h = ToggleGroupHandler()
        out = h.render(
            ['name="v"', 'disabled=True', 'options=[{"value":"x","label":"X"}]'],
            {},
        )
        assert "toggle-group-disabled" in out
        assert "dj-click" not in out

    def test_returns_safe_string(self):
        h = ToggleGroupHandler()
        out = h.render(['name="v"', 'options=[]'], {})
        assert isinstance(out, SafeData)


class TestRustHandlerFab:
    def test_basic_render(self):
        h = FabHandler()
        out = h.render(['icon="+"', 'event="create"', 'position="top-left"'], {})
        assert "fab-container" in out
        assert "fab-top-left" in out
        assert 'dj-click="create"' in out

    def test_speed_dial(self):
        h = FabHandler()
        out = h.render(
            ['icon="+"', 'actions=[{"icon":"x","event":"go","label":"Go"}]'],
            {},
        )
        assert "fab-actions" in out
        assert "fab-action" in out

    def test_returns_safe_string(self):
        h = FabHandler()
        out = h.render([], {})
        assert isinstance(out, SafeData)


class TestRustHandlerSplitButton:
    def test_basic_render(self):
        h = SplitButtonHandler()
        out = h.render(
            ['label="Save"', 'event="save"',
             'options=[{"label":"Draft","event":"draft"}]'],
            {},
        )
        assert "split-btn" in out
        assert "Save" in out
        assert 'dj-click="save"' in out
        assert "Draft" in out

    def test_loading(self):
        h = SplitButtonHandler()
        out = h.render(['label="X"', 'loading=True'], {})
        assert "split-btn-loading" in out
        assert "split-btn-spinner" in out

    def test_returns_safe_string(self):
        h = SplitButtonHandler()
        out = h.render(['label="X"'], {})
        assert isinstance(out, SafeData)


# ═══════════════════════════════════════════════════════════════════════════
# 5. XSS Escaping Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestButtonControlVariantsXSS:
    """Verify that all user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_raw_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html

    # --- Toggle Group ---
    def test_toggle_group_name_xss(self):
        html = render(
            '{% toggle_group name=xss options=opts value="" %}',
            {"xss": self.XSS_ATTR, "opts": [{"value": "a", "label": "A"}]},
        )
        self._assert_attr_escaped(html)

    def test_toggle_group_option_label_xss(self):
        html = render(
            '{% toggle_group name="t" options=opts value="" %}',
            {"opts": [{"value": "a", "label": self.XSS}]},
        )
        self._assert_no_raw_script(html)

    def test_toggle_group_option_value_xss(self):
        html = render(
            '{% toggle_group name="t" options=opts value="" %}',
            {"opts": [{"value": self.XSS_ATTR, "label": "X"}]},
        )
        self._assert_attr_escaped(html)

    def test_toggle_group_event_xss(self):
        html = render(
            '{% toggle_group name="t" options=opts value="" event=xss %}',
            {"xss": self.XSS_ATTR, "opts": [{"value": "a", "label": "A"}]},
        )
        self._assert_attr_escaped(html)

    def test_toggle_group_icon_xss(self):
        html = render(
            '{% toggle_group name="t" options=opts value="" %}',
            {"opts": [{"value": "a", "label": "A", "icon": self.XSS}]},
        )
        self._assert_no_raw_script(html)

    # --- FAB ---
    def test_fab_icon_xss(self):
        html = render(
            '{% fab icon=xss %}',
            {"xss": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_fab_event_xss(self):
        html = render(
            '{% fab event=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_fab_label_xss(self):
        html = render(
            '{% fab label=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_fab_action_icon_xss(self):
        html = render(
            '{% fab actions=acts %}',
            {"acts": [{"icon": self.XSS, "event": "go", "label": "Go"}]},
        )
        self._assert_no_raw_script(html)

    def test_fab_action_event_xss(self):
        html = render(
            '{% fab actions=acts %}',
            {"acts": [{"icon": "x", "event": self.XSS_ATTR, "label": "Go"}]},
        )
        self._assert_attr_escaped(html)

    def test_fab_action_label_xss(self):
        html = render(
            '{% fab actions=acts %}',
            {"acts": [{"icon": "x", "event": "go", "label": self.XSS_ATTR}]},
        )
        self._assert_attr_escaped(html)

    # --- Split Button ---
    def test_split_button_label_xss(self):
        html = render(
            '{% split_button label=xss %}',
            {"xss": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_split_button_event_xss(self):
        html = render(
            '{% split_button label="X" event=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_split_button_toggle_event_xss(self):
        html = render(
            '{% split_button label="X" toggle_event=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_split_button_option_label_xss(self):
        html = render(
            '{% split_button label="X" options=opts %}',
            {"opts": [{"label": self.XSS, "event": "go"}]},
        )
        self._assert_no_raw_script(html)

    def test_split_button_option_event_xss(self):
        html = render(
            '{% split_button label="X" options=opts %}',
            {"opts": [{"label": "Go", "event": self.XSS_ATTR}]},
        )
        self._assert_attr_escaped(html)

    # --- Rust handlers XSS ---
    def test_rust_toggle_group_label_xss(self):
        h = ToggleGroupHandler()
        out = h.render(
            ['name="t"', f'options=[{{"value":"a","label":"{self.XSS}"}}]'],
            {},
        )
        assert "<script>" not in out

    def test_rust_fab_icon_xss(self):
        h = FabHandler()
        out = h.render([f'icon="{self.XSS}"'], {})
        assert "<script>" not in out

    def test_rust_split_button_label_xss(self):
        h = SplitButtonHandler()
        out = h.render([f'label="{self.XSS}"'], {})
        assert "<script>" not in out
