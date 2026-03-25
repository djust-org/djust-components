"""Tests for AI chat interface components — template tags, component classes, and XSS."""
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
# Conversation Thread
# ===========================================================================

class TestConversationThread:
    def test_empty_thread(self):
        html = render('{% conversation_thread messages=msgs %}', {"msgs": []})
        assert "dj-chat-thread" in html
        assert "dj-chat-msg" not in html

    def test_renders_messages(self):
        msgs = [
            {"sender": "user", "name": "Alice", "text": "Hello!", "time": "10:01"},
            {"sender": "ai", "name": "Bot", "text": "Hi there!", "time": "10:02"},
        ]
        html = render('{% conversation_thread messages=msgs %}', {"msgs": msgs})
        assert "dj-chat-msg--user" in html
        assert "dj-chat-msg--ai" in html
        assert "Alice" in html
        assert "Hello!" in html
        assert "Bot" in html
        assert "Hi there!" in html
        assert "10:01" in html
        assert "10:02" in html

    def test_avatar_initials(self):
        msgs = [{"sender": "user", "name": "Zara", "text": "test", "time": ""}]
        html = render('{% conversation_thread messages=msgs %}', {"msgs": msgs})
        assert ">Z</span>" in html

    def test_message_grouping(self):
        msgs = [
            {"sender": "user", "name": "Alice", "text": "msg1", "time": "10:01"},
            {"sender": "user", "name": "Alice", "text": "msg2", "time": "10:02"},
        ]
        html = render('{% conversation_thread messages=msgs %}', {"msgs": msgs})
        assert "dj-chat-msg--grouped" in html
        # Second message should have hidden avatar
        assert "dj-chat-avatar--hidden" in html

    def test_streaming_indicator(self):
        html = render(
            '{% conversation_thread messages=msgs streaming=True %}',
            {"msgs": []},
        )
        assert "dj-chat-typing" in html
        assert "dj-chat-typing__dot" in html

    def test_stream_event_attr(self):
        html = render(
            '{% conversation_thread messages=msgs stream_event="my_event" %}',
            {"msgs": []},
        )
        assert 'data-stream-event="my_event"' in html

    def test_custom_class(self):
        html = render(
            '{% conversation_thread messages=msgs class="my-thread" %}',
            {"msgs": []},
        )
        assert "my-thread" in html


class TestConversationThreadClass:
    def test_basic_render(self):
        from djust_components.components.conversation_thread import ConversationThread
        thread = ConversationThread(
            messages=[
                {"sender": "user", "name": "Alice", "text": "Hi", "time": "now"},
            ],
        )
        html = thread._render_custom()
        assert "dj-chat-thread" in html
        assert "Alice" in html
        assert "Hi" in html

    def test_streaming(self):
        from djust_components.components.conversation_thread import ConversationThread
        thread = ConversationThread(messages=[], streaming=True)
        html = thread._render_custom()
        assert "dj-chat-typing" in html

    def test_empty(self):
        from djust_components.components.conversation_thread import ConversationThread
        thread = ConversationThread()
        html = thread._render_custom()
        assert "dj-chat-thread" in html
        assert "dj-chat-msg" not in html


# ===========================================================================
# Thinking Indicator
# ===========================================================================

class TestThinkingIndicator:
    def test_thinking_status(self):
        html = render('{% thinking_indicator status="thinking" label="Processing..." %}')
        assert "dj-thinking--thinking" in html
        assert "dj-thinking__dots" in html
        assert "Processing..." in html

    def test_searching_status(self):
        html = render('{% thinking_indicator status="searching" %}')
        assert "dj-thinking--searching" in html
        assert "dj-thinking__pulse" in html

    def test_generating_status(self):
        html = render('{% thinking_indicator status="generating" %}')
        assert "dj-thinking--generating" in html
        assert "dj-thinking__cursor" in html

    def test_tool_use_status(self):
        html = render('{% thinking_indicator status="tool_use" %}')
        assert "dj-thinking--tool_use" in html
        assert "dj-thinking__spinner" in html

    def test_idle_returns_empty(self):
        html = render('{% thinking_indicator status="idle" %}')
        assert html.strip() == ""

    def test_invalid_status_defaults_to_thinking(self):
        html = render('{% thinking_indicator status="bogus" %}')
        assert "dj-thinking--thinking" in html

    def test_role_status(self):
        html = render('{% thinking_indicator status="thinking" %}')
        assert 'role="status"' in html

    def test_custom_class(self):
        html = render('{% thinking_indicator status="thinking" class="extra" %}')
        assert "extra" in html


class TestThinkingIndicatorClass:
    def test_thinking(self):
        from djust_components.components.thinking_indicator import ThinkingIndicator
        ind = ThinkingIndicator(status="thinking", label="Analyzing...")
        html = ind._render_custom()
        assert "dj-thinking--thinking" in html
        assert "Analyzing..." in html

    def test_idle(self):
        from djust_components.components.thinking_indicator import ThinkingIndicator
        ind = ThinkingIndicator(status="idle")
        assert ind._render_custom() == ""

    def test_invalid_status(self):
        from djust_components.components.thinking_indicator import ThinkingIndicator
        ind = ThinkingIndicator(status="nope")
        html = ind._render_custom()
        assert "dj-thinking--thinking" in html


# ===========================================================================
# Multimodal Input
# ===========================================================================

class TestMultimodalInput:
    def test_basic_render(self):
        html = render('{% multimodal_input name="msg" event="send" %}')
        assert "dj-mminput" in html
        assert 'name="msg"' in html
        assert 'dj-click="send"' in html
        assert "dj-mminput__text" in html

    def test_file_button(self):
        html = render('{% multimodal_input accept_files=True %}')
        assert "dj-mminput__file-btn" in html
        assert 'type="file"' in html

    def test_no_file_button_by_default(self):
        html = render('{% multimodal_input %}')
        assert "dj-mminput__file-btn" not in html

    def test_voice_button(self):
        html = render('{% multimodal_input accept_voice=True %}')
        assert "dj-mminput__voice-btn" in html

    def test_no_voice_button_by_default(self):
        html = render('{% multimodal_input %}')
        assert "dj-mminput__voice-btn" not in html

    def test_disabled(self):
        html = render('{% multimodal_input disabled=True %}')
        assert "dj-mminput--disabled" in html
        assert "disabled" in html

    def test_placeholder(self):
        html = render('{% multimodal_input placeholder="Ask me..." %}')
        assert 'placeholder="Ask me..."' in html

    def test_custom_class(self):
        html = render('{% multimodal_input class="extra" %}')
        assert "extra" in html

    def test_send_button_present(self):
        html = render('{% multimodal_input %}')
        assert "dj-mminput__send-btn" in html


class TestMultimodalInputClass:
    def test_basic(self):
        from djust_components.components.multimodal_input import MultimodalInput
        inp = MultimodalInput(name="msg", event="send")
        html = inp._render_custom()
        assert "dj-mminput" in html
        assert 'name="msg"' in html

    def test_all_buttons(self):
        from djust_components.components.multimodal_input import MultimodalInput
        inp = MultimodalInput(accept_files=True, accept_voice=True)
        html = inp._render_custom()
        assert "dj-mminput__file-btn" in html
        assert "dj-mminput__voice-btn" in html
        assert "dj-mminput__send-btn" in html

    def test_disabled(self):
        from djust_components.components.multimodal_input import MultimodalInput
        inp = MultimodalInput(disabled=True)
        html = inp._render_custom()
        assert "dj-mminput--disabled" in html


# ===========================================================================
# Feedback Widget
# ===========================================================================

class TestFeedbackWidget:
    def test_thumbs_mode(self):
        html = render('{% feedback event="rate" mode="thumbs" %}')
        assert "dj-feedback--thumbs" in html
        assert 'data-value="up"' in html
        assert 'data-value="down"' in html
        assert 'dj-click="rate"' in html

    def test_stars_mode(self):
        html = render('{% feedback event="rate" mode="stars" %}')
        assert "dj-feedback--stars" in html
        assert 'data-value="1"' in html
        assert 'data-value="5"' in html

    def test_stars_active_value(self):
        html = render('{% feedback event="rate" mode="stars" value=val %}', {"val": "3"})
        assert html.count("dj-feedback__star--active") == 3

    def test_emoji_mode(self):
        html = render('{% feedback event="rate" mode="emoji" %}')
        assert "dj-feedback--emoji" in html
        assert 'data-value="thumbs_up"' in html
        assert 'data-value="heart"' in html

    def test_thumbs_active_up(self):
        html = render('{% feedback event="rate" mode="thumbs" value=val %}', {"val": "up"})
        assert "dj-feedback__btn--active" in html

    def test_thumbs_active_down(self):
        html = render('{% feedback event="rate" mode="thumbs" value=val %}', {"val": "down"})
        assert "dj-feedback__btn--active" in html

    def test_invalid_mode_defaults_thumbs(self):
        html = render('{% feedback event="rate" mode="bogus" %}')
        assert "dj-feedback--thumbs" in html

    def test_role_group(self):
        html = render('{% feedback event="rate" %}')
        assert 'role="group"' in html

    def test_custom_class(self):
        html = render('{% feedback event="rate" class="extra" %}')
        assert "extra" in html


class TestFeedbackWidgetClass:
    def test_thumbs(self):
        from djust_components.components.feedback_widget import FeedbackWidget
        fw = FeedbackWidget(event="rate", mode="thumbs")
        html = fw._render_custom()
        assert "dj-feedback--thumbs" in html
        assert 'data-value="up"' in html

    def test_stars_with_value(self):
        from djust_components.components.feedback_widget import FeedbackWidget
        fw = FeedbackWidget(event="rate", mode="stars", value="4")
        html = fw._render_custom()
        assert html.count("dj-feedback__star--active") == 4

    def test_emoji(self):
        from djust_components.components.feedback_widget import FeedbackWidget
        fw = FeedbackWidget(event="rate", mode="emoji")
        html = fw._render_custom()
        assert "dj-feedback--emoji" in html

    def test_invalid_mode(self):
        from djust_components.components.feedback_widget import FeedbackWidget
        fw = FeedbackWidget(event="rate", mode="invalid")
        assert fw.mode == "thumbs"


# ===========================================================================
# XSS Escaping
# ===========================================================================

class TestAIChatXSS:
    """Verify that user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # --- Conversation Thread XSS ---

    def test_thread_message_text_xss(self):
        msgs = [{"sender": "user", "name": "Alice", "text": self.XSS, "time": "now"}]
        html = render('{% conversation_thread messages=msgs %}', {"msgs": msgs})
        self._assert_no_script(html)

    def test_thread_message_name_xss(self):
        msgs = [{"sender": "user", "name": self.XSS, "text": "hi", "time": "now"}]
        html = render('{% conversation_thread messages=msgs %}', {"msgs": msgs})
        self._assert_no_script(html)

    def test_thread_stream_event_xss(self):
        html = render(
            '{% conversation_thread messages=msgs stream_event=bad %}',
            {"msgs": [], "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_thread_class_xss(self):
        html = render(
            '{% conversation_thread messages=msgs class=bad %}',
            {"msgs": [], "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_thread_time_xss(self):
        msgs = [{"sender": "user", "name": "A", "text": "t", "time": self.XSS}]
        html = render('{% conversation_thread messages=msgs %}', {"msgs": msgs})
        self._assert_no_script(html)

    # --- Thinking Indicator XSS ---

    def test_thinking_label_xss(self):
        html = render(
            '{% thinking_indicator status="thinking" label=bad %}',
            {"bad": self.XSS},
        )
        self._assert_no_script(html)

    def test_thinking_class_xss(self):
        html = render(
            '{% thinking_indicator status="thinking" class=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Multimodal Input XSS ---

    def test_mminput_name_xss(self):
        html = render(
            '{% multimodal_input name=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_mminput_event_xss(self):
        html = render(
            '{% multimodal_input event=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_mminput_placeholder_xss(self):
        html = render(
            '{% multimodal_input placeholder=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_mminput_class_xss(self):
        html = render(
            '{% multimodal_input class=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Feedback Widget XSS ---

    def test_feedback_event_xss(self):
        html = render(
            '{% feedback event=bad mode="thumbs" %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_feedback_class_xss(self):
        html = render(
            '{% feedback event="rate" class=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)


# ===========================================================================
# Rust Handler Tests
# ===========================================================================

class TestRustHandlers:
    def test_conversation_thread_handler(self):
        from djust_components.rust_handlers import ConversationThreadHandler
        h = ConversationThreadHandler()
        msgs = [
            {"sender": "user", "name": "Alice", "text": "Hello", "time": "10:00"},
        ]
        result = h.render([], {"messages": msgs})
        # No args passed, so messages comes from context default
        # Handler uses _parse_args which needs key=value format
        result2 = h.render(['messages=messages'], {"messages": msgs})
        assert "Alice" in str(result2)
        assert "Hello" in str(result2)

    def test_thinking_indicator_handler(self):
        from djust_components.rust_handlers import ThinkingIndicatorHandler
        h = ThinkingIndicatorHandler()
        result = h.render(['status="thinking"', 'label="Working..."'], {})
        assert "dj-thinking--thinking" in str(result)
        assert "Working..." in str(result)

    def test_thinking_indicator_handler_idle(self):
        from djust_components.rust_handlers import ThinkingIndicatorHandler
        h = ThinkingIndicatorHandler()
        result = h.render(['status="idle"'], {})
        assert result == ""

    def test_multimodal_input_handler(self):
        from djust_components.rust_handlers import MultimodalInputHandler
        h = MultimodalInputHandler()
        result = h.render(['name="msg"', 'event="send"', 'accept_files=True'], {})
        assert "dj-mminput" in str(result)
        assert 'name="msg"' in str(result)
        assert "dj-mminput__file-btn" in str(result)

    def test_feedback_handler_thumbs(self):
        from djust_components.rust_handlers import FeedbackWidgetHandler
        h = FeedbackWidgetHandler()
        result = h.render(['event="rate"', 'mode="thumbs"'], {})
        assert "dj-feedback--thumbs" in str(result)
        assert 'data-value="up"' in str(result)

    def test_feedback_handler_stars(self):
        from djust_components.rust_handlers import FeedbackWidgetHandler
        h = FeedbackWidgetHandler()
        result = h.render(['event="rate"', 'mode="stars"', 'value=3'], {})
        assert "dj-feedback--stars" in str(result)
        assert str(result).count("dj-feedback__star--active") == 3

    def test_feedback_handler_emoji(self):
        from djust_components.rust_handlers import FeedbackWidgetHandler
        h = FeedbackWidgetHandler()
        result = h.render(['event="rate"', 'mode="emoji"'], {})
        assert "dj-feedback--emoji" in str(result)

    def test_handlers_registered(self):
        from djust_components.rust_handlers import INLINE_HANDLERS
        handler_names = [name for name, _ in INLINE_HANDLERS]
        assert "conversation_thread" in handler_names
        assert "thinking_indicator" in handler_names
        assert "multimodal_input" in handler_names
        assert "feedback" in handler_names

    # Rust handler XSS
    def test_conversation_thread_handler_xss(self):
        from djust_components.rust_handlers import ConversationThreadHandler
        h = ConversationThreadHandler()
        msgs = [{"sender": "user", "name": "<script>alert(1)</script>", "text": "t", "time": ""}]
        result = h.render(['messages=messages'], {"messages": msgs})
        assert "<script>" not in str(result)
        assert "&lt;script&gt;" in str(result)

    def test_thinking_handler_label_xss(self):
        from djust_components.rust_handlers import ThinkingIndicatorHandler
        h = ThinkingIndicatorHandler()
        result = h.render(['status="thinking"', 'label=bad'], {"bad": '<script>alert(1)</script>'})
        assert "<script>" not in str(result)
        assert "&lt;script&gt;" in str(result)

    def test_multimodal_handler_event_xss(self):
        from djust_components.rust_handlers import MultimodalInputHandler
        h = MultimodalInputHandler()
        result = h.render(['event=bad'], {"bad": '" onmouseover="alert(1)" x="'})
        assert '" onmouseover="' not in str(result)
        assert "&quot;" in str(result)

    def test_feedback_handler_event_xss(self):
        from djust_components.rust_handlers import FeedbackWidgetHandler
        h = FeedbackWidgetHandler()
        result = h.render(['event=bad'], {"bad": '" onmouseover="alert(1)" x="'})
        assert '" onmouseover="' not in str(result)
        assert "&quot;" in str(result)
