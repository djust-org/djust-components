"""Tests for TtydTerminalView LiveView.

djust (the core framework) uses a Rust extension built with maturin and
cannot be pip-installed in the test environment without a full Rust toolchain.
We therefore mock the ``djust`` module before importing
``djust_components.ttyd`` so all tests can run against pure Python.
"""
import json
import sys
import unittest.mock as mock
import pytest
from django.test import RequestFactory

# Now safe to import — djust stub is already in sys.modules.
from djust_components.ttyd import TtydTerminalView


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


# ---------------------------------------------------------------------------
# Lifecycle state — initial values after mount()
# ---------------------------------------------------------------------------

class TestTtydTerminalViewLifecycleInitial:
    """terminal_connected and session timestamps start falsy after mount()."""

    def test_terminal_connected_false_after_mount(self):
        view = TtydTerminalView()
        view.mount(make_request())
        assert view.terminal_connected is False

    def test_session_start_none_after_mount(self):
        view = TtydTerminalView()
        view.mount(make_request())
        assert view.session_start is None

    def test_session_end_none_after_mount(self):
        view = TtydTerminalView()
        view.mount(make_request())
        assert view.session_end is None


# ---------------------------------------------------------------------------
# on_ttyd_connect event handler
# ---------------------------------------------------------------------------

class TestOnTtydConnect:
    """on_ttyd_connect sets terminal_connected=True and records session_start."""

    def _mounted_view(self):
        view = TtydTerminalView()
        view.mount(make_request())
        return view

    def test_sets_terminal_connected_true(self):
        view = self._mounted_view()
        view.on_ttyd_connect(timestamp="2026-02-26T12:00:00.000Z", user_agent="Mozilla/5.0")
        assert view.terminal_connected is True

    def test_records_session_start(self):
        ts = "2026-02-26T12:00:00.000Z"
        view = self._mounted_view()
        view.on_ttyd_connect(timestamp=ts, user_agent="Mozilla/5.0")
        assert view.session_start == ts

    def test_clears_session_end(self):
        view = self._mounted_view()
        # Simulate a previous disconnect then reconnect
        view.session_end = "2026-02-26T11:59:00.000Z"
        view.on_ttyd_connect(timestamp="2026-02-26T12:00:00.000Z", user_agent="Mozilla/5.0")
        assert view.session_end is None

    def test_accepts_empty_strings(self):
        view = self._mounted_view()
        view.on_ttyd_connect()  # all defaults
        assert view.terminal_connected is True
        assert view.session_start == ""


# ---------------------------------------------------------------------------
# on_ttyd_disconnect event handler
# ---------------------------------------------------------------------------

class TestOnTtydDisconnect:
    """on_ttyd_disconnect sets terminal_connected=False and records session_end."""

    def _connected_view(self):
        view = TtydTerminalView()
        view.mount(make_request())
        view.on_ttyd_connect(timestamp="2026-02-26T12:00:00.000Z", user_agent="Mozilla/5.0")
        return view

    def test_sets_terminal_connected_false(self):
        view = self._connected_view()
        view.on_ttyd_disconnect(timestamp="2026-02-26T12:05:00.000Z", code=1000, reason="normal")
        assert view.terminal_connected is False

    def test_records_session_end(self):
        ts = "2026-02-26T12:05:00.000Z"
        view = self._connected_view()
        view.on_ttyd_disconnect(timestamp=ts, code=1000, reason="normal")
        assert view.session_end == ts

    def test_preserves_session_start(self):
        view = self._connected_view()
        start = view.session_start
        view.on_ttyd_disconnect(timestamp="2026-02-26T12:05:00.000Z", code=1000)
        assert view.session_start == start

    def test_accepts_empty_strings_and_zero_code(self):
        view = self._connected_view()
        view.on_ttyd_disconnect()  # all defaults
        assert view.terminal_connected is False
        assert view.session_end == ""

    def test_handles_abnormal_close_code(self):
        view = self._connected_view()
        view.on_ttyd_disconnect(timestamp="2026-02-26T12:05:00.000Z", code=1006, reason="")
        assert view.terminal_connected is False


# ---------------------------------------------------------------------------
# Subclass override of lifecycle callbacks
# ---------------------------------------------------------------------------

class TestTtydTerminalViewLifecycleSubclass:
    """Subclasses can override on_ttyd_connect/on_ttyd_disconnect."""

    def test_subclass_can_override_on_connect(self):
        class LoggingView(TtydTerminalView):
            def on_ttyd_connect(self, timestamp="", user_agent="", **kwargs):
                super().on_ttyd_connect(timestamp=timestamp, user_agent=user_agent, **kwargs)
                self.last_user_agent = user_agent

        view = LoggingView()
        view.mount(make_request())
        view.on_ttyd_connect(timestamp="2026-02-26T12:00:00.000Z", user_agent="TestAgent/1.0")
        assert view.terminal_connected is True
        assert view.last_user_agent == "TestAgent/1.0"

    def test_subclass_can_override_on_disconnect(self):
        class CountingView(TtydTerminalView):
            disconnect_count = 0

            def on_ttyd_disconnect(self, timestamp="", code=0, reason="", **kwargs):
                super().on_ttyd_disconnect(timestamp=timestamp, code=code, reason=reason, **kwargs)
                self.__class__.disconnect_count += 1

        view = CountingView()
        view.mount(make_request())
        view.on_ttyd_connect(timestamp="2026-02-26T12:00:00.000Z")
        view.on_ttyd_disconnect(timestamp="2026-02-26T12:05:00.000Z", code=1000)
        assert CountingView.disconnect_count == 1
        assert view.terminal_connected is False
