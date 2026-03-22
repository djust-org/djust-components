"""Tests for Rust template engine handlers (rust_handlers.py)."""
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

import pytest
from django.utils.safestring import SafeData

from djust_components.rust_handlers import _parse_args


# ─── _parse_args ───


class TestParseArgs:
    def test_string_literal_double_quotes(self):
        result = _parse_args(['title="Hello World"'], {})
        assert result == {"title": "Hello World"}

    def test_string_literal_single_quotes(self):
        result = _parse_args(["title='Hello'"], {})
        assert result == {"title": "Hello"}

    def test_boolean_true(self):
        for val in ("True", "true"):
            result = _parse_args([f"open={val}"], {})
            assert result["open"] is True

    def test_boolean_false(self):
        for val in ("False", "false"):
            result = _parse_args([f"open={val}"], {})
            assert result["open"] is False

    def test_integer(self):
        result = _parse_args(["count=42"], {})
        assert result["count"] == 42
        assert isinstance(result["count"], int)

    def test_float(self):
        result = _parse_args(["ratio=3.14"], {})
        assert result["ratio"] == 3.14
        assert isinstance(result["ratio"], float)

    def test_none_values(self):
        for val in ("None", "null"):
            result = _parse_args([f"value={val}"], {})
            assert result["value"] is None

    def test_empty_string(self):
        result = _parse_args(["label="], {})
        assert result["label"] == ""

    def test_json_array(self):
        result = _parse_args(['items=["a","b","c"]'], {})
        assert result["items"] == ["a", "b", "c"]

    def test_json_object(self):
        result = _parse_args(['data={"key": "val"}'], {})
        assert result["data"] == {"key": "val"}

    def test_invalid_json_falls_back_to_context(self):
        result = _parse_args(["items=[invalid"], {"[invalid": "fallback"})
        assert result["items"] == "fallback"

    def test_variable_reference(self):
        ctx = {"my_title": "Resolved Title"}
        result = _parse_args(["title=my_title"], ctx)
        assert result["title"] == "Resolved Title"

    def test_variable_not_in_context_returns_raw(self):
        result = _parse_args(["title=missing_var"], {})
        assert result["title"] == "missing_var"

    def test_skips_args_without_equals(self):
        result = _parse_args(["positional", "key=val"], {})
        assert "positional" not in result
        assert result["key"] == "val"

    def test_multiple_args(self):
        result = _parse_args(
            ['title="My Modal"', "open=True", "size=lg"],
            {"lg": "lg"},
        )
        assert result["title"] == "My Modal"
        assert result["open"] is True
        assert result["size"] == "lg"

    def test_numeric_string_one_parsed_as_int(self):
        """Verify "1" without quotes is parsed as int, not string."""
        result = _parse_args(["count=1"], {})
        assert result["count"] == 1
        assert isinstance(result["count"], int)

    def test_numeric_string_zero_parsed_as_int(self):
        """Verify "0" without quotes is parsed as int, not string."""
        result = _parse_args(["count=0"], {})
        assert result["count"] == 0
        assert isinstance(result["count"], int)

    def test_quoted_one_is_string(self):
        """Quoted "1" should remain a string."""
        result = _parse_args(["val=\"1\""], {})
        assert result["val"] == "1"
        assert isinstance(result["val"], str)

    def test_equals_in_value(self):
        """Values containing '=' should be handled (split on first '=' only)."""
        result = _parse_args(['style="color: red; font-size: 12px"'], {})
        assert result["style"] == "color: red; font-size: 12px"


# ─── Handler render smoke tests ───


class TestModalHandler:
    def test_hidden_when_closed(self):
        from djust_components.rust_handlers import ModalHandler
        handler = ModalHandler()
        result = handler.render(["open=False"], "body", {})
        assert result == ""

    def test_visible_when_open(self):
        from djust_components.rust_handlers import ModalHandler
        handler = ModalHandler()
        result = handler.render(["open=True", 'title="Confirm"'], "body text", {})
        assert "modal-overlay" in result
        assert "Confirm" in result
        assert "body text" in result
        assert isinstance(result, SafeData)


class TestPopoverHandler:
    def test_renders_with_defaults(self):
        from djust_components.rust_handlers import PopoverHandler
        handler = PopoverHandler()
        result = handler.render([], "popover content", {})
        assert "popover-wrapper" in result
        assert "Click me" in result
        assert "popover content" in result
        assert isinstance(result, SafeData)

    def test_custom_trigger_escaped(self):
        from djust_components.rust_handlers import PopoverHandler
        handler = PopoverHandler()
        result = handler.render(['trigger="<b>XSS</b>"'], "content", {})
        assert "<b>" not in result
        assert "&lt;b&gt;" in result
        assert isinstance(result, SafeData)


class TestCollapsibleHandler:
    def test_renders_closed(self):
        from djust_components.rust_handlers import CollapsibleHandler
        handler = CollapsibleHandler()
        result = handler.render([], "inner", {})
        assert 'class="collapsible"' in result
        assert 'class="collapsible collapsible-open"' not in result
        assert "inner" in result
        assert isinstance(result, SafeData)

    def test_renders_open(self):
        from djust_components.rust_handlers import CollapsibleHandler
        handler = CollapsibleHandler()
        result = handler.render(["open=True"], "inner", {})
        assert "collapsible-open" in result
        assert isinstance(result, SafeData)


class TestSheetHandler:
    def test_renders_with_title(self):
        from djust_components.rust_handlers import SheetHandler
        handler = SheetHandler()
        result = handler.render(['title="Settings"', "open=True"], "sheet body", {})
        assert "Settings" in result
        assert "sheet body" in result
        assert 'data-open="true"' in result
        assert isinstance(result, SafeData)


class TestCommandPaletteHandler:
    def test_renders_with_defaults(self):
        from djust_components.rust_handlers import CommandPaletteHandler
        handler = CommandPaletteHandler()
        result = handler.render(["open=True"], "palette items", {})
        assert "palette" in result
        assert "palette items" in result
        assert isinstance(result, SafeData)


class TestContextMenuHandler:
    def test_renders_with_label(self):
        from djust_components.rust_handlers import ContextMenuHandler
        handler = ContextMenuHandler()
        result = handler.render(['label="Options"'], "menu items", {})
        assert "Options" in result
        assert "menu items" in result
        assert isinstance(result, SafeData)

    def test_label_escaped(self):
        from djust_components.rust_handlers import ContextMenuHandler
        handler = ContextMenuHandler()
        result = handler.render(['label="<script>alert(1)</script>"'], "items", {})
        assert "<script>" not in result
        assert isinstance(result, SafeData)


class TestSplitPaneHandler:
    def test_renders_with_content(self):
        from djust_components.rust_handlers import SplitPaneHandler
        handler = SplitPaneHandler()
        result = handler.render([], "pane content", {})
        assert "split-pane" in result
        assert "pane content" in result
        assert isinstance(result, SafeData)
