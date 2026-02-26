"""Tests for TtydTerminalView LiveView.

djust (the core framework) uses a Rust extension built with maturin and
cannot be pip-installed in the test environment without a full Rust toolchain.
We therefore mock the ``djust`` module before importing
``djust_components.ttyd`` so all tests can run against pure Python.
"""
import json
import sys
import types
import unittest.mock as mock

# ---------------------------------------------------------------------------
# Minimal djust stub — must happen before any djust_components import.
# ---------------------------------------------------------------------------

# Build a fake 'djust' package with a LiveView base class.
_djust_stub = types.ModuleType("djust")


class _LiveViewBase:
    """Minimal stand-in for djust.LiveView used during unit tests."""

    def get_context_data(self, **kwargs):
        return {}


_djust_stub.LiveView = _LiveViewBase
sys.modules.setdefault("djust", _djust_stub)

# ---------------------------------------------------------------------------
# Django minimal setup (needed for RequestFactory).
# ---------------------------------------------------------------------------
import django  # noqa: E402
from django.conf import settings  # noqa: E402

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

import pytest  # noqa: E402
from django.test import RequestFactory  # noqa: E402

# Now safe to import — djust stub is already in sys.modules.
from djust_components.ttyd import TtydTerminalView  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_request(params=None):
    """Return a mock GET request with optional query-string params."""
    factory = RequestFactory()
    return factory.get("/", params or {})


# ---------------------------------------------------------------------------
# Default class attributes
# ---------------------------------------------------------------------------

class TestTtydTerminalViewDefaults:
    """Class-level defaults are correct before any mount() call."""

    def test_default_ttyd_url(self):
        assert TtydTerminalView.ttyd_url == "ws://localhost:7681"

    def test_default_rows(self):
        assert TtydTerminalView.rows == 24

    def test_default_cols(self):
        assert TtydTerminalView.cols == 80

    def test_default_theme_is_none_or_empty(self):
        assert TtydTerminalView.theme is None or TtydTerminalView.theme == {}

    def test_template_name(self):
        assert TtydTerminalView.template_name == "djust_components/ttyd_terminal.html"

    def test_login_required_false(self):
        assert TtydTerminalView.login_required is False


# ---------------------------------------------------------------------------
# mount() — prop parsing from request.GET
# ---------------------------------------------------------------------------

class TestTtydTerminalViewMount:
    """mount() reads props from request.GET and falls back to class defaults."""

    def test_mount_sets_defaults_when_no_params(self):
        view = TtydTerminalView()
        view.mount(make_request())
        assert view.ttyd_url == "ws://localhost:7681"
        assert view.rows == 24
        assert view.cols == 80
        assert view.theme == {}

    def test_mount_url_override(self):
        view = TtydTerminalView()
        view.mount(make_request({"url": "ws://myhost:9999"}))
        assert view.ttyd_url == "ws://myhost:9999"

    def test_mount_rows_override(self):
        view = TtydTerminalView()
        view.mount(make_request({"rows": "40"}))
        assert view.rows == 40
        assert isinstance(view.rows, int)

    def test_mount_cols_override(self):
        view = TtydTerminalView()
        view.mount(make_request({"cols": "120"}))
        assert view.cols == 120
        assert isinstance(view.cols, int)

    def test_mount_rows_and_cols_together(self):
        view = TtydTerminalView()
        view.mount(make_request({"rows": "30", "cols": "100"}))
        assert view.rows == 30
        assert view.cols == 100

    def test_mount_valid_theme_json(self):
        theme = {"background": "#1e1e2e", "foreground": "#cdd6f4"}
        view = TtydTerminalView()
        view.mount(make_request({"theme": json.dumps(theme)}))
        assert view.theme == theme

    def test_mount_invalid_theme_json_degrades_to_empty(self):
        view = TtydTerminalView()
        view.mount(make_request({"theme": "not-valid-json{"}))
        assert view.theme == {}

    def test_mount_no_theme_param_is_empty_dict(self):
        view = TtydTerminalView()
        view.mount(make_request())
        assert view.theme == {}


# ---------------------------------------------------------------------------
# get_context_data()
# ---------------------------------------------------------------------------

class TestTtydTerminalViewContextData:
    """get_context_data() produces correct context after mount()."""

    def _mounted_view(self, params=None):
        view = TtydTerminalView()
        view.request = make_request(params)
        view.mount(view.request)
        return view

    def test_theme_json_in_context_is_valid_json(self):
        view = self._mounted_view()
        ctx = view.get_context_data()
        parsed = json.loads(ctx["theme_json"])
        assert parsed == {}

    def test_theme_json_reflects_parsed_theme(self):
        theme = {"background": "#000000"}
        view = self._mounted_view({"theme": json.dumps(theme)})
        ctx = view.get_context_data()
        assert json.loads(ctx["theme_json"]) == theme

    def test_theme_json_no_xss(self):
        """HTML special chars in theme values are contained inside JSON strings."""
        dangerous = {"background": "<script>alert(1)</script>"}
        view = self._mounted_view({"theme": json.dumps(dangerous)})
        ctx = view.get_context_data()
        theme_json = ctx["theme_json"]
        # Must be valid JSON whose value equals the original string
        parsed = json.loads(theme_json)
        assert parsed["background"] == "<script>alert(1)</script>"
        # The angle brackets live inside a JSON string value — Django will
        # auto-escape them when rendering the data-* attribute in the template.
        assert "<script>" in theme_json


# ---------------------------------------------------------------------------
# Subclass pattern
# ---------------------------------------------------------------------------

class TestTtydTerminalViewSubclass:
    """Subclasses can override class-level defaults; base class is unaffected."""

    def test_subclass_url_override(self):
        class DeployLogView(TtydTerminalView):
            ttyd_url = "ws://deploy-host:7682"
            rows = 40
            cols = 120

        view = DeployLogView()
        view.mount(make_request())
        assert view.ttyd_url == "ws://deploy-host:7682"
        assert view.rows == 40
        assert view.cols == 120

    def test_subclass_url_can_still_be_overridden_by_param(self):
        class DeployLogView(TtydTerminalView):
            ttyd_url = "ws://deploy-host:7682"

        view = DeployLogView()
        view.mount(make_request({"url": "ws://other:9999"}))
        assert view.ttyd_url == "ws://other:9999"

    def test_subclass_does_not_affect_base_class(self):
        class CustomView(TtydTerminalView):
            ttyd_url = "ws://custom:1234"

        assert TtydTerminalView.ttyd_url == "ws://localhost:7681"

    def test_subclass_theme_dict_preserved(self):
        class ThemedView(TtydTerminalView):
            theme = {"background": "#000000", "foreground": "#ffffff"}

        view = ThemedView()
        view.mount(make_request())
        assert view.theme == {"background": "#000000", "foreground": "#ffffff"}
