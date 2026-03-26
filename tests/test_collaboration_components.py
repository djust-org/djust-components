"""Tests for collaboration components — template tags, component classes, and XSS."""
from django.template import Template, Context
import pytest


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ===========================================================================
# Chat Bubble — Template Tag
# ===========================================================================

class TestChatBubble:
    def test_basic_user_message(self):
        msg = {"sender": "user", "name": "Alice", "text": "Hello!", "time": "10:01 AM"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        assert "dj-bubble" in html
        assert "dj-bubble--user" in html
        assert "Alice" in html
        assert "Hello!" in html
        assert "10:01 AM" in html

    def test_other_sender(self):
        msg = {"sender": "other", "name": "Bob", "text": "Hi!"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        assert "dj-bubble--other" in html
        assert "Bob" in html

    def test_avatar_image(self):
        msg = {"sender": "user", "name": "Alice", "text": "Hi", "avatar": "/img/alice.jpg"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        assert "dj-bubble__avatar-img" in html
        assert "/img/alice.jpg" in html

    def test_avatar_initials_fallback(self):
        msg = {"sender": "user", "name": "Alice Baker", "text": "Hi"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        assert "dj-bubble__avatar--initials" in html
        assert "AB" in html

    def test_status_delivered(self):
        msg = {"sender": "user", "name": "A", "text": "t", "status": "delivered"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        assert "dj-bubble__status--delivered" in html
        assert "&#10003;&#10003;" in html

    def test_status_sent(self):
        msg = {"sender": "user", "name": "A", "text": "t", "status": "sent"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        assert "dj-bubble__status--sent" in html

    def test_status_read(self):
        msg = {"sender": "user", "name": "A", "text": "t", "status": "read"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        assert "dj-bubble__status--read" in html

    def test_status_sending(self):
        msg = {"sender": "user", "name": "A", "text": "t", "status": "sending"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        assert "dj-bubble__status--sending" in html

    def test_status_error(self):
        msg = {"sender": "user", "name": "A", "text": "t", "status": "error"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        assert "dj-bubble__status--error" in html

    def test_invalid_status_ignored(self):
        msg = {"sender": "user", "name": "A", "text": "t", "status": "bogus"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        assert "dj-bubble__status" not in html

    def test_custom_class(self):
        msg = {"sender": "user", "name": "A", "text": "t"}
        html = render('{% chat_bubble message=msg class="extra" %}', {"msg": msg})
        assert "extra" in html

    def test_empty_message(self):
        html = render('{% chat_bubble message=msg %}', {"msg": {}})
        assert "dj-bubble" in html
        assert "dj-bubble--user" in html  # default sender

    def test_no_name_shows_question_mark(self):
        msg = {"sender": "user", "text": "hi"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        assert "?" in html


# ===========================================================================
# Chat Bubble — Component Class
# ===========================================================================

class TestChatBubbleClass:
    def test_basic_render(self):
        from djust_components.components.chat_bubble import ChatBubble
        bubble = ChatBubble(
            message={"sender": "user", "name": "Alice", "text": "Hello!", "time": "10:01"},
        )
        html = bubble._render_custom()
        assert "dj-bubble--user" in html
        assert "Alice" in html
        assert "Hello!" in html

    def test_other_sender(self):
        from djust_components.components.chat_bubble import ChatBubble
        bubble = ChatBubble(
            message={"sender": "other", "name": "Bot", "text": "Hi!"},
        )
        html = bubble._render_custom()
        assert "dj-bubble--other" in html

    def test_status(self):
        from djust_components.components.chat_bubble import ChatBubble
        bubble = ChatBubble(
            message={"sender": "user", "name": "A", "text": "t", "status": "read"},
        )
        html = bubble._render_custom()
        assert "dj-bubble__status--read" in html

    def test_avatar_image(self):
        from djust_components.components.chat_bubble import ChatBubble
        bubble = ChatBubble(
            message={"sender": "user", "name": "A", "text": "t", "avatar": "/img/a.jpg"},
        )
        html = bubble._render_custom()
        assert "dj-bubble__avatar-img" in html

    def test_empty(self):
        from djust_components.components.chat_bubble import ChatBubble
        bubble = ChatBubble()
        html = bubble._render_custom()
        assert "dj-bubble" in html


# ===========================================================================
# Presence Avatars — Template Tag
# ===========================================================================

class TestPresenceAvatars:
    def test_basic_render(self):
        users = [
            {"name": "Alice", "status": "online"},
            {"name": "Bob", "status": "away"},
        ]
        html = render('{% presence_avatars users=users %}', {"users": users})
        assert "dj-presence" in html
        assert 'title="Alice"' in html
        assert 'title="Bob"' in html
        assert "dj-presence__dot--online" in html
        assert "dj-presence__dot--away" in html

    def test_busy_status(self):
        users = [{"name": "Carol", "status": "busy"}]
        html = render('{% presence_avatars users=users %}', {"users": users})
        assert "dj-presence__dot--busy" in html

    def test_offline_status(self):
        users = [{"name": "Dave", "status": "offline"}]
        html = render('{% presence_avatars users=users %}', {"users": users})
        assert "dj-presence__dot--offline" in html

    def test_avatar_image(self):
        users = [{"name": "Alice", "avatar": "/img/alice.jpg"}]
        html = render('{% presence_avatars users=users %}', {"users": users})
        assert "dj-presence__img" in html
        assert "/img/alice.jpg" in html

    def test_initials_fallback(self):
        users = [{"name": "Alice Baker"}]
        html = render('{% presence_avatars users=users %}', {"users": users})
        assert "dj-presence__initials" in html
        assert "AB" in html

    def test_overflow_count(self):
        users = [{"name": f"User{i}"} for i in range(7)]
        html = render('{% presence_avatars users=users max=3 %}', {"users": users})
        assert "+4" in html
        assert "dj-presence__overflow" in html

    def test_no_overflow_when_under_max(self):
        users = [{"name": "Alice"}, {"name": "Bob"}]
        html = render('{% presence_avatars users=users max=5 %}', {"users": users})
        assert "dj-presence__overflow" not in html

    def test_custom_class(self):
        users = [{"name": "Alice"}]
        html = render('{% presence_avatars users=users class="extra" %}', {"users": users})
        assert "extra" in html

    def test_role_group(self):
        users = [{"name": "Alice"}]
        html = render('{% presence_avatars users=users %}', {"users": users})
        assert 'role="group"' in html

    def test_aria_label_singular(self):
        users = [{"name": "Alice"}]
        html = render('{% presence_avatars users=users %}', {"users": users})
        assert '1 user present' in html

    def test_aria_label_plural(self):
        users = [{"name": "Alice"}, {"name": "Bob"}]
        html = render('{% presence_avatars users=users %}', {"users": users})
        assert '2 users present' in html

    def test_empty_users(self):
        html = render('{% presence_avatars users=users %}', {"users": []})
        assert "dj-presence" in html
        assert "dj-presence__item" not in html

    def test_invalid_status_defaults_online(self):
        users = [{"name": "X", "status": "bogus"}]
        html = render('{% presence_avatars users=users %}', {"users": users})
        assert "dj-presence__dot--online" in html

    def test_z_index_stacking(self):
        users = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        html = render('{% presence_avatars users=users %}', {"users": users})
        assert 'style="z-index:3"' in html
        assert 'style="z-index:2"' in html
        assert 'style="z-index:1"' in html


# ===========================================================================
# Presence Avatars — Component Class
# ===========================================================================

class TestPresenceAvatarsClass:
    def test_basic(self):
        from djust_components.components.presence_avatars import PresenceAvatars
        pa = PresenceAvatars(
            users=[
                {"name": "Alice", "status": "online"},
                {"name": "Bob", "status": "away"},
            ],
        )
        html = pa._render_custom()
        assert "dj-presence" in html
        assert "dj-presence__dot--online" in html
        assert "dj-presence__dot--away" in html

    def test_overflow(self):
        from djust_components.components.presence_avatars import PresenceAvatars
        users = [{"name": f"U{i}"} for i in range(8)]
        pa = PresenceAvatars(users=users, max_display=3)
        html = pa._render_custom()
        assert "+5" in html

    def test_empty(self):
        from djust_components.components.presence_avatars import PresenceAvatars
        pa = PresenceAvatars()
        html = pa._render_custom()
        assert "dj-presence" in html


# ===========================================================================
# Mentions Input — Template Tag
# ===========================================================================

class TestMentionsInput:
    def test_basic_render(self):
        users = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]
        html = render('{% mentions_input name="msg" users=users %}', {"users": users})
        assert "dj-mentions" in html
        assert 'name="msg"' in html
        assert 'role="listbox"' in html
        assert "Alice" in html
        assert "Bob" in html

    def test_event(self):
        html = render('{% mentions_input name="msg" event="send_msg" users=users %}', {"users": []})
        assert 'dj-keydown.enter="send_msg"' in html

    def test_placeholder(self):
        html = render('{% mentions_input placeholder="Say something..." users=users %}', {"users": []})
        assert 'placeholder="Say something..."' in html

    def test_default_placeholder(self):
        html = render('{% mentions_input users=users %}', {"users": []})
        assert "Type @ to mention" in html

    def test_disabled(self):
        html = render('{% mentions_input disabled=True users=users %}', {"users": []})
        assert "dj-mentions--disabled" in html
        assert "disabled" in html

    def test_custom_class(self):
        html = render('{% mentions_input class="extra" users=users %}', {"users": []})
        assert "extra" in html

    def test_user_avatar_image(self):
        users = [{"id": "1", "name": "Alice", "avatar": "/img/alice.jpg"}]
        html = render('{% mentions_input users=users %}', {"users": users})
        assert "dj-mentions__avatar-img" in html
        assert "/img/alice.jpg" in html

    def test_user_initials_fallback(self):
        users = [{"id": "1", "name": "Alice Baker"}]
        html = render('{% mentions_input users=users %}', {"users": users})
        assert "dj-mentions__avatar-initials" in html
        assert "AB" in html

    def test_data_user_id(self):
        users = [{"id": "42", "name": "Alice"}]
        html = render('{% mentions_input users=users %}', {"users": users})
        assert 'data-user-id="42"' in html

    def test_data_user_name(self):
        users = [{"id": "1", "name": "Alice"}]
        html = render('{% mentions_input users=users %}', {"users": users})
        assert 'data-user-name="Alice"' in html

    def test_dj_hook(self):
        html = render('{% mentions_input users=users %}', {"users": []})
        assert 'dj-hook="MentionsInput"' in html

    def test_data_users_json(self):
        users = [{"id": "1", "name": "Alice"}]
        html = render('{% mentions_input users=users %}', {"users": users})
        assert "data-users=" in html

    def test_role_option(self):
        users = [{"id": "1", "name": "Alice"}]
        html = render('{% mentions_input users=users %}', {"users": users})
        assert 'role="option"' in html

    def test_empty_users(self):
        html = render('{% mentions_input users=users %}', {"users": []})
        assert "dj-mentions__item" not in html

    def test_autocomplete_off(self):
        html = render('{% mentions_input users=users %}', {"users": []})
        assert 'autocomplete="off"' in html


# ===========================================================================
# Mentions Input — Component Class
# ===========================================================================

class TestMentionsInputClass:
    def test_basic(self):
        from djust_components.components.mentions_input import MentionsInput
        mi = MentionsInput(
            name="msg",
            users=[{"id": "1", "name": "Alice"}],
            event="send_msg",
        )
        html = mi._render_custom()
        assert "dj-mentions" in html
        assert 'name="msg"' in html
        assert "Alice" in html

    def test_disabled(self):
        from djust_components.components.mentions_input import MentionsInput
        mi = MentionsInput(disabled=True)
        html = mi._render_custom()
        assert "dj-mentions--disabled" in html

    def test_empty(self):
        from djust_components.components.mentions_input import MentionsInput
        mi = MentionsInput()
        html = mi._render_custom()
        assert "dj-mentions" in html
        assert "dj-mentions__item" not in html


# ===========================================================================
# XSS Escaping
# ===========================================================================

class TestCollaborationXSS:
    """Verify that user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # --- Chat Bubble XSS ---

    def test_bubble_text_xss(self):
        msg = {"sender": "user", "name": "A", "text": self.XSS, "time": "now"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        self._assert_no_script(html)

    def test_bubble_name_xss(self):
        msg = {"sender": "user", "name": self.XSS, "text": "hi", "time": "now"}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        self._assert_no_script(html)

    def test_bubble_time_xss(self):
        msg = {"sender": "user", "name": "A", "text": "t", "time": self.XSS}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        self._assert_no_script(html)

    def test_bubble_avatar_xss(self):
        msg = {"sender": "user", "name": "A", "text": "t", "avatar": self.XSS_ATTR}
        html = render('{% chat_bubble message=msg %}', {"msg": msg})
        self._assert_attr_escaped(html)

    def test_bubble_class_xss(self):
        msg = {"sender": "user", "name": "A", "text": "t"}
        html = render(
            '{% chat_bubble message=msg class=bad %}',
            {"msg": msg, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Presence Avatars XSS ---

    def test_presence_name_xss(self):
        users = [{"name": self.XSS, "status": "online"}]
        html = render('{% presence_avatars users=users %}', {"users": users})
        self._assert_no_script(html)

    def test_presence_avatar_xss(self):
        users = [{"name": "A", "avatar": self.XSS_ATTR}]
        html = render('{% presence_avatars users=users %}', {"users": users})
        self._assert_attr_escaped(html)

    def test_presence_class_xss(self):
        users = [{"name": "A"}]
        html = render(
            '{% presence_avatars users=users class=bad %}',
            {"users": users, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Mentions Input XSS ---

    def test_mentions_name_xss(self):
        html = render(
            '{% mentions_input name=bad users=users %}',
            {"bad": self.XSS_ATTR, "users": []},
        )
        self._assert_attr_escaped(html)

    def test_mentions_placeholder_xss(self):
        html = render(
            '{% mentions_input placeholder=bad users=users %}',
            {"bad": self.XSS_ATTR, "users": []},
        )
        self._assert_attr_escaped(html)

    def test_mentions_event_xss(self):
        html = render(
            '{% mentions_input event=bad users=users %}',
            {"bad": self.XSS_ATTR, "users": []},
        )
        self._assert_attr_escaped(html)

    def test_mentions_class_xss(self):
        html = render(
            '{% mentions_input class=bad users=users %}',
            {"bad": self.XSS_ATTR, "users": []},
        )
        self._assert_attr_escaped(html)

    def test_mentions_user_name_xss(self):
        users = [{"id": "1", "name": self.XSS}]
        html = render('{% mentions_input users=users %}', {"users": users})
        self._assert_no_script(html)

    def test_mentions_user_id_xss(self):
        users = [{"id": self.XSS_ATTR, "name": "A"}]
        html = render('{% mentions_input users=users %}', {"users": users})
        self._assert_attr_escaped(html)

    def test_mentions_user_avatar_xss(self):
        users = [{"id": "1", "name": "A", "avatar": self.XSS_ATTR}]
        html = render('{% mentions_input users=users %}', {"users": users})
        self._assert_attr_escaped(html)
