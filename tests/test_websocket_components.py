"""Tests for WebSocket-powered components: Streaming Text, Connection Status,
Live Counter, Toast Container, and ServerEventToastMixin."""

import sys
import types

# ---------------------------------------------------------------------------
# Minimal djust stub — must happen before any djust_components import.
# ---------------------------------------------------------------------------
_djust_stub = types.ModuleType("djust")


class _ComponentBase:
    """Minimal stand-in for djust.Component used during unit tests."""
    def __init__(self, **kwargs):
        pass


class _LiveViewBase:
    """Minimal stand-in for djust.LiveView used during unit tests."""
    def __init__(self):
        self._pushed_events = []

    def push_event(self, event_name, payload):
        self._pushed_events.append((event_name, payload))

    def get_context_data(self, **kwargs):
        return {}


_djust_stub.Component = _ComponentBase
_djust_stub.LiveView = _LiveViewBase
sys.modules.setdefault("djust", _djust_stub)

# Build a fake 'djust.decorators' submodule
_decorators_stub = types.ModuleType("djust.decorators")


def _event_handler(fn=None, **kwargs):
    if fn is not None:
        return fn
    def _decorator(fn):
        return fn
    return _decorator


_decorators_stub.event_handler = _event_handler
sys.modules.setdefault("djust.decorators", _decorators_stub)

# ---------------------------------------------------------------------------
# Django minimal setup
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

from django.template import Template, Context  # noqa: E402
import pytest  # noqa: E402


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ===========================================================================
# Streaming Text
# ===========================================================================

class TestStreamingText:
    def test_basic_render(self):
        html = render('{% streaming_text stream_event="stream_chunk" %}')
        assert "dj-streaming-text" in html
        assert 'data-stream-event="stream_chunk"' in html
        assert "dj-streaming-text__content" in html

    def test_custom_event(self):
        html = render('{% streaming_text stream_event="ai_response" %}')
        assert 'data-stream-event="ai_response"' in html

    def test_initial_text(self):
        html = render(
            '{% streaming_text stream_event="s" text=initial_text %}',
            {"initial_text": "Hello world"},
        )
        assert "Hello world" in html

    def test_cursor_class_default(self):
        html = render('{% streaming_text stream_event="s" %}')
        assert "dj-streaming-text--cursor" in html

    def test_cursor_disabled(self):
        html = render('{% streaming_text stream_event="s" cursor=False %}')
        assert "dj-streaming-text--cursor" not in html

    def test_auto_scroll_default(self):
        html = render('{% streaming_text stream_event="s" %}')
        assert 'data-auto-scroll="true"' in html

    def test_auto_scroll_disabled(self):
        html = render('{% streaming_text stream_event="s" auto_scroll=False %}')
        assert "data-auto-scroll" not in html

    def test_markdown_enabled(self):
        html = render('{% streaming_text stream_event="s" markdown=True %}')
        assert 'data-markdown="true"' in html

    def test_markdown_default_off(self):
        html = render('{% streaming_text stream_event="s" %}')
        assert "data-markdown" not in html

    def test_custom_class(self):
        html = render('{% streaming_text stream_event="s" custom_class="my-class" %}')
        assert "my-class" in html

    def test_context_variable_event(self):
        html = render(
            '{% streaming_text stream_event=evt %}',
            {"evt": "my_event"},
        )
        assert 'data-stream-event="my_event"' in html


class TestStreamingTextXSS:
    def test_xss_stream_event(self):
        html = render(
            '{% streaming_text stream_event=evil %}',
            {"evil": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html or "&#" in html or "&quot;" in html

    def test_xss_text(self):
        html = render(
            '{% streaming_text stream_event="s" text=evil %}',
            {"evil": '<img src=x onerror=alert(1)>'},
        )
        assert "<img" not in html
        assert "&lt;img" in html

    def test_xss_custom_class(self):
        html = render(
            '{% streaming_text stream_event="s" custom_class=evil %}',
            {"evil": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html


# ===========================================================================
# Connection Status
# ===========================================================================

class TestConnectionStatus:
    def test_basic_render(self):
        html = render('{% connection_status %}')
        assert "dj-connection-status" in html
        assert 'role="status"' in html
        assert 'aria-live="polite"' in html
        assert 'style="display:none"' in html

    def test_default_texts(self):
        html = render('{% connection_status %}')
        assert "Reconnecting..." in html
        assert 'data-connected-text="Reconnected"' in html

    def test_custom_reconnecting_text(self):
        html = render('{% connection_status reconnecting_text="Connection lost..." %}')
        assert "Connection lost..." in html
        assert 'data-reconnecting-text="Connection lost..."' in html

    def test_custom_connected_text(self):
        html = render('{% connection_status connected_text="Back online!" %}')
        assert 'data-connected-text="Back online!"' in html

    def test_custom_class(self):
        html = render('{% connection_status custom_class="my-bar" %}')
        assert "my-bar" in html

    def test_status_text_element(self):
        html = render('{% connection_status %}')
        assert "dj-connection-status__text" in html


class TestConnectionStatusXSS:
    def test_xss_reconnecting_text(self):
        html = render(
            '{% connection_status reconnecting_text=evil %}',
            {"evil": '<script>alert(1)</script>'},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_connected_text(self):
        html = render(
            '{% connection_status connected_text=evil %}',
            {"evil": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html

    def test_xss_custom_class(self):
        html = render(
            '{% connection_status custom_class=evil %}',
            {"evil": '" onclick="alert(1)'},
        )
        assert 'onclick' not in html or '&quot;' in html


# ===========================================================================
# Live Counter
# ===========================================================================

class TestLiveCounter:
    def test_basic_render(self):
        html = render('{% live_counter value=42 label="online" stream_event="counter_update" %}')
        assert "dj-live-counter" in html
        assert "42" in html
        assert "online" in html
        assert 'data-stream-event="counter_update"' in html

    def test_default_event(self):
        html = render('{% live_counter value=0 %}')
        assert 'data-stream-event="counter_update"' in html

    def test_value_from_context(self):
        html = render(
            '{% live_counter value=count label="users" %}',
            {"count": 99},
        )
        assert "99" in html
        assert 'data-value="99"' in html

    def test_no_label(self):
        html = render('{% live_counter value=5 %}')
        assert "dj-live-counter__label" not in html

    def test_size_sm(self):
        html = render('{% live_counter value=1 size="sm" %}')
        assert "dj-live-counter--sm" in html

    def test_size_lg(self):
        html = render('{% live_counter value=1 size="lg" %}')
        assert "dj-live-counter--lg" in html

    def test_custom_class(self):
        html = render('{% live_counter value=1 custom_class="extra" %}')
        assert "extra" in html

    def test_value_zero(self):
        html = render('{% live_counter value=0 %}')
        assert 'data-value="0"' in html
        assert ">0<" in html

    def test_counter_value_element(self):
        html = render('{% live_counter value=7 %}')
        assert "dj-live-counter__value" in html


class TestLiveCounterXSS:
    def test_xss_label(self):
        html = render(
            '{% live_counter value=1 label=evil %}',
            {"evil": '<script>alert(1)</script>'},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_stream_event(self):
        html = render(
            '{% live_counter value=1 stream_event=evil %}',
            {"evil": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html

    def test_xss_custom_class(self):
        html = render(
            '{% live_counter value=1 custom_class=evil %}',
            {"evil": '" onclick="alert(1)'},
        )
        assert 'onclick' not in html or '&quot;' in html


# ===========================================================================
# Toast Container
# ===========================================================================

class TestToastContainer:
    def test_basic_render(self):
        html = render('{% server_toast_container %}')
        assert "dj-toast-container" in html
        assert 'role="region"' in html
        assert 'aria-live="polite"' in html
        assert 'aria-label="Notifications"' in html

    def test_default_position(self):
        html = render('{% server_toast_container %}')
        assert "dj-toast-container--top-right" in html

    def test_position_bottom_left(self):
        html = render('{% server_toast_container position="bottom-left" %}')
        assert "dj-toast-container--bottom-left" in html

    def test_position_top_center(self):
        html = render('{% server_toast_container position="top-center" %}')
        assert "dj-toast-container--top-center" in html

    def test_max_toasts_default(self):
        html = render('{% server_toast_container %}')
        assert 'data-max-toasts="5"' in html

    def test_max_toasts_custom(self):
        html = render('{% server_toast_container max_toasts=10 %}')
        assert 'data-max-toasts="10"' in html

    def test_custom_class(self):
        html = render('{% server_toast_container custom_class="my-toasts" %}')
        assert "my-toasts" in html

    def test_empty_container(self):
        """Container should render empty — toasts are added by JS."""
        html = render('{% server_toast_container %}')
        assert "dj-toast-container" in html
        # Should NOT contain any toast child elements in server render
        assert "dj-server-toast" not in html


class TestToastContainerXSS:
    def test_xss_position(self):
        html = render(
            '{% server_toast_container position=evil %}',
            {"evil": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html

    def test_xss_custom_class(self):
        html = render(
            '{% server_toast_container custom_class=evil %}',
            {"evil": '" onclick="alert(1)'},
        )
        assert 'onclick' not in html or '&quot;' in html


# ===========================================================================
# ServerEventToastMixin
# ===========================================================================

class TestServerEventToastMixin:
    def test_push_toast_default(self):
        from djust_components.components.server_event_toast import ServerEventToastMixin

        class FakeView(ServerEventToastMixin, _LiveViewBase):
            pass

        view = FakeView()
        view.push_toast("Saved!")
        assert len(view._pushed_events) == 1
        event_name, payload = view._pushed_events[0]
        assert event_name == "__toast__"
        assert payload["message"] == "Saved!"
        assert payload["type"] == "info"
        assert payload["duration"] == 3000

    def test_push_toast_success(self):
        from djust_components.components.server_event_toast import ServerEventToastMixin

        class FakeView(ServerEventToastMixin, _LiveViewBase):
            pass

        view = FakeView()
        view.push_toast("Done!", type="success", duration=5000)
        event_name, payload = view._pushed_events[0]
        assert payload["type"] == "success"
        assert payload["duration"] == 5000

    def test_push_toast_error(self):
        from djust_components.components.server_event_toast import ServerEventToastMixin

        class FakeView(ServerEventToastMixin, _LiveViewBase):
            pass

        view = FakeView()
        view.push_toast("Failed", type="error")
        assert view._pushed_events[0][1]["type"] == "error"

    def test_push_toast_warning(self):
        from djust_components.components.server_event_toast import ServerEventToastMixin

        class FakeView(ServerEventToastMixin, _LiveViewBase):
            pass

        view = FakeView()
        view.push_toast("Careful", type="warning", duration=0)
        payload = view._pushed_events[0][1]
        assert payload["type"] == "warning"
        assert payload["duration"] == 0

    def test_multiple_toasts(self):
        from djust_components.components.server_event_toast import ServerEventToastMixin

        class FakeView(ServerEventToastMixin, _LiveViewBase):
            pass

        view = FakeView()
        view.push_toast("First")
        view.push_toast("Second", type="success")
        view.push_toast("Third", type="error")
        assert len(view._pushed_events) == 3
        assert view._pushed_events[0][1]["message"] == "First"
        assert view._pushed_events[1][1]["message"] == "Second"
        assert view._pushed_events[2][1]["message"] == "Third"


# ===========================================================================
# Component Class Rendering
# ===========================================================================

class TestStreamingTextComponent:
    def test_render(self):
        from djust_components.components.streaming_text import StreamingText
        st = StreamingText(stream_event="my_event", text="Hello")
        html = st._render_custom()
        assert "dj-streaming-text" in html
        assert 'data-stream-event="my_event"' in html
        assert "Hello" in html

    def test_xss_event(self):
        from djust_components.components.streaming_text import StreamingText
        st = StreamingText(stream_event='"><script>alert(1)</script>')
        html = st._render_custom()
        assert "<script>" not in html

    def test_xss_text(self):
        from djust_components.components.streaming_text import StreamingText
        st = StreamingText(text='<img src=x onerror=alert(1)>')
        html = st._render_custom()
        assert "<img" not in html


class TestConnectionStatusComponent:
    def test_render(self):
        from djust_components.components.connection_status import ConnectionStatus
        cs = ConnectionStatus()
        html = cs._render_custom()
        assert "dj-connection-status" in html
        assert "Reconnecting..." in html

    def test_custom_text(self):
        from djust_components.components.connection_status import ConnectionStatus
        cs = ConnectionStatus(reconnecting_text="Lost...", connected_text="Back!")
        html = cs._render_custom()
        assert "Lost..." in html
        assert 'data-connected-text="Back!"' in html

    def test_xss_text(self):
        from djust_components.components.connection_status import ConnectionStatus
        cs = ConnectionStatus(reconnecting_text='<script>alert(1)</script>')
        html = cs._render_custom()
        assert "<script>" not in html


class TestLiveCounterComponent:
    def test_render(self):
        from djust_components.components.live_counter import LiveCounter
        lc = LiveCounter(value=42, label="online")
        html = lc._render_custom()
        assert "42" in html
        assert "online" in html
        assert "dj-live-counter" in html

    def test_xss_label(self):
        from djust_components.components.live_counter import LiveCounter
        lc = LiveCounter(value=1, label='<script>alert(1)</script>')
        html = lc._render_custom()
        assert "<script>" not in html


# ===========================================================================
# Rust Handler Rendering
# ===========================================================================

class TestStreamingTextRustHandler:
    def test_render(self):
        from djust_components.rust_handlers import StreamingTextHandler
        h = StreamingTextHandler()
        html = h.render(["stream_event='my_event'"], {})
        assert "dj-streaming-text" in html
        assert 'data-stream-event="my_event"' in html

    def test_xss(self):
        from djust_components.rust_handlers import StreamingTextHandler
        h = StreamingTextHandler()
        html = h.render(["stream_event='\"><script>alert(1)</script>'"], {})
        assert "<script>" not in html


class TestConnectionStatusRustHandler:
    def test_render(self):
        from djust_components.rust_handlers import ConnectionStatusHandler
        h = ConnectionStatusHandler()
        html = h.render([], {})
        assert "dj-connection-status" in html
        assert "Reconnecting..." in html

    def test_xss(self):
        from djust_components.rust_handlers import ConnectionStatusHandler
        h = ConnectionStatusHandler()
        html = h.render(["reconnecting_text='<script>alert(1)</script>'"], {})
        assert "<script>" not in html


class TestLiveCounterRustHandler:
    def test_render(self):
        from djust_components.rust_handlers import LiveCounterHandler
        h = LiveCounterHandler()
        html = h.render(["value=42", "label='online'"], {})
        assert "42" in html
        assert "online" in html

    def test_xss(self):
        from djust_components.rust_handlers import LiveCounterHandler
        h = LiveCounterHandler()
        html = h.render(["label='<script>alert(1)</script>'"], {})
        assert "<script>" not in html


class TestServerToastContainerRustHandler:
    def test_render(self):
        from djust_components.rust_handlers import ServerToastContainerHandler
        h = ServerToastContainerHandler()
        html = h.render(["position='bottom-left'"], {})
        assert "dj-toast-container--bottom-left" in html
        assert 'aria-live="polite"' in html

    def test_xss(self):
        from djust_components.rust_handlers import ServerToastContainerHandler
        h = ServerToastContainerHandler()
        html = h.render(["position='\"><script>alert(1)</script>'"], {})
        assert "<script>" not in html
