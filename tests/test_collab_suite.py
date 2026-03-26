"""Tests for v2.0 Batch 5 Collaboration Suite — template tags, component classes, and XSS."""
from django.template import Template, Context
import pytest


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ===========================================================================
# Cursors Overlay — Template Tag
# ===========================================================================

class TestCursorsOverlay:
    def test_basic_render(self):
        users = [
            {"name": "Alice", "color": "#3b82f6", "x": 100, "y": 200},
            {"name": "Bob", "color": "#ef4444", "x": 300, "y": 150},
        ]
        html = render('{% cursors users=users %}', {"users": users})
        assert "dj-cursors" in html
        assert 'data-user="Alice"' in html
        assert 'data-user="Bob"' in html
        assert "left:100px" in html
        assert "top:200px" in html

    def test_default_colors(self):
        users = [{"name": "Alice", "x": 0, "y": 0}]
        html = render('{% cursors users=users %}', {"users": users})
        assert "dj-cursors__cursor" in html
        assert "#3b82f6" in html

    def test_cursor_svg(self):
        users = [{"name": "A", "x": 0, "y": 0}]
        html = render('{% cursors users=users %}', {"users": users})
        assert "dj-cursors__arrow" in html
        assert "<svg" in html

    def test_label(self):
        users = [{"name": "Alice", "x": 0, "y": 0}]
        html = render('{% cursors users=users %}', {"users": users})
        assert "dj-cursors__label" in html
        assert "Alice" in html

    def test_hook(self):
        html = render('{% cursors users=users %}', {"users": []})
        assert 'dj-hook="CursorsOverlay"' in html

    def test_role_group(self):
        html = render('{% cursors users=users %}', {"users": []})
        assert 'role="group"' in html

    def test_aria_label_singular(self):
        users = [{"name": "A", "x": 0, "y": 0}]
        html = render('{% cursors users=users %}', {"users": users})
        assert '1 cursor"' in html

    def test_aria_label_plural(self):
        users = [{"name": "A", "x": 0, "y": 0}, {"name": "B", "x": 1, "y": 1}]
        html = render('{% cursors users=users %}', {"users": users})
        assert '2 cursors"' in html

    def test_empty_users(self):
        html = render('{% cursors users=users %}', {"users": []})
        assert "dj-cursors" in html
        assert "dj-cursors__cursor" not in html

    def test_custom_class(self):
        html = render('{% cursors users=users class="extra" %}', {"users": []})
        assert "extra" in html


# ===========================================================================
# Cursors Overlay — Component Class
# ===========================================================================

class TestCursorsOverlayClass:
    def test_basic(self):
        from djust_components.components.cursors_overlay import CursorsOverlay
        co = CursorsOverlay(
            users=[
                {"name": "Alice", "color": "#3b82f6", "x": 50, "y": 100},
            ],
        )
        html = co._render_custom()
        assert "dj-cursors" in html
        assert 'data-user="Alice"' in html
        assert "left:50px" in html

    def test_empty(self):
        from djust_components.components.cursors_overlay import CursorsOverlay
        co = CursorsOverlay()
        html = co._render_custom()
        assert "dj-cursors" in html
        assert "dj-cursors__cursor" not in html

    def test_multiple_users(self):
        from djust_components.components.cursors_overlay import CursorsOverlay
        co = CursorsOverlay(
            users=[
                {"name": "Alice", "x": 10, "y": 20},
                {"name": "Bob", "x": 30, "y": 40},
            ],
        )
        html = co._render_custom()
        assert "Alice" in html
        assert "Bob" in html


# ===========================================================================
# Live Indicator — Template Tag
# ===========================================================================

class TestLiveIndicator:
    def test_basic_render(self):
        user = {"name": "Alice"}
        html = render('{% live_indicator user=user field="title" %}', {"user": user})
        assert "dj-live-indicator" in html
        assert "Alice" in html
        assert "is typing" in html
        assert 'data-field="title"' in html

    def test_custom_action(self):
        user = {"name": "Bob"}
        html = render('{% live_indicator user=user action="editing" %}', {"user": user})
        assert "is editing" in html

    def test_avatar(self):
        user = {"name": "Alice", "avatar": "/img/alice.jpg"}
        html = render('{% live_indicator user=user %}', {"user": user})
        assert "dj-live-indicator__avatar" in html
        assert "/img/alice.jpg" in html

    def test_hidden_when_no_user(self):
        html = render('{% live_indicator user=user %}', {"user": None})
        assert "dj-live-indicator--hidden" in html

    def test_hidden_when_inactive(self):
        user = {"name": "Alice"}
        html = render('{% live_indicator user=user active=False %}', {"user": user})
        assert "dj-live-indicator--hidden" in html

    def test_dots_animation(self):
        user = {"name": "A"}
        html = render('{% live_indicator user=user %}', {"user": user})
        assert "dj-live-indicator__dots" in html
        assert "dj-live-indicator__dot" in html

    def test_role_status(self):
        user = {"name": "A"}
        html = render('{% live_indicator user=user %}', {"user": user})
        assert 'role="status"' in html
        assert 'aria-live="polite"' in html

    def test_custom_class(self):
        user = {"name": "A"}
        html = render('{% live_indicator user=user class="extra" %}', {"user": user})
        assert "extra" in html

    def test_no_field_attr_when_empty(self):
        user = {"name": "A"}
        html = render('{% live_indicator user=user %}', {"user": user})
        assert "data-field" not in html


# ===========================================================================
# Live Indicator — Component Class
# ===========================================================================

class TestLiveIndicatorClass:
    def test_basic(self):
        from djust_components.components.live_indicator import LiveIndicator
        li = LiveIndicator(user={"name": "Alice"}, field="title")
        html = li._render_custom()
        assert "dj-live-indicator" in html
        assert "Alice" in html
        assert 'data-field="title"' in html

    def test_hidden_no_user(self):
        from djust_components.components.live_indicator import LiveIndicator
        li = LiveIndicator()
        html = li._render_custom()
        assert "dj-live-indicator--hidden" in html

    def test_custom_action(self):
        from djust_components.components.live_indicator import LiveIndicator
        li = LiveIndicator(user={"name": "Bob"}, action="editing")
        html = li._render_custom()
        assert "is editing" in html


# ===========================================================================
# Collaborative Selection — Template Tag
# ===========================================================================

class TestCollabSelection:
    def test_basic_render(self):
        users = [
            {"name": "Alice", "color": "#3b82f6", "text": "hello world",
             "start": 10, "end": 21},
        ]
        html = render('{% collab_selection users=users %}', {"users": users})
        assert "dj-collab-sel" in html
        assert 'data-user="Alice"' in html
        assert "hello world" in html
        assert 'data-start="10"' in html
        assert 'data-end="21"' in html

    def test_multiple_selections(self):
        users = [
            {"name": "Alice", "text": "foo", "start": 0, "end": 3},
            {"name": "Bob", "text": "bar", "start": 5, "end": 8},
        ]
        html = render('{% collab_selection users=users %}', {"users": users})
        assert "Alice" in html
        assert "Bob" in html

    def test_label_with_color(self):
        users = [{"name": "Alice", "color": "#ff0000", "text": "x"}]
        html = render('{% collab_selection users=users %}', {"users": users})
        assert "dj-collab-sel__label" in html
        assert "background:#ff0000" in html

    def test_highlight(self):
        users = [{"name": "A", "text": "selected"}]
        html = render('{% collab_selection users=users %}', {"users": users})
        assert "dj-collab-sel__highlight" in html

    def test_hook(self):
        html = render('{% collab_selection users=users %}', {"users": []})
        assert 'dj-hook="CollabSelection"' in html

    def test_role_group(self):
        html = render('{% collab_selection users=users %}', {"users": []})
        assert 'role="group"' in html

    def test_aria_label_plural(self):
        users = [{"name": "A", "text": "x"}, {"name": "B", "text": "y"}]
        html = render('{% collab_selection users=users %}', {"users": users})
        assert '2 selections"' in html

    def test_empty_users(self):
        html = render('{% collab_selection users=users %}', {"users": []})
        assert "dj-collab-sel" in html
        assert "dj-collab-sel__range" not in html

    def test_custom_class(self):
        html = render('{% collab_selection users=users class="extra" %}', {"users": []})
        assert "extra" in html

    def test_default_colors(self):
        users = [{"name": "A", "text": "x"}]
        html = render('{% collab_selection users=users %}', {"users": users})
        assert "#3b82f6" in html


# ===========================================================================
# Collaborative Selection — Component Class
# ===========================================================================

class TestCollabSelectionClass:
    def test_basic(self):
        from djust_components.components.collab_selection import CollabSelection
        cs = CollabSelection(
            users=[{"name": "Alice", "color": "#f00", "text": "hi", "start": 0, "end": 2}],
        )
        html = cs._render_custom()
        assert "dj-collab-sel" in html
        assert "Alice" in html
        assert "hi" in html

    def test_empty(self):
        from djust_components.components.collab_selection import CollabSelection
        cs = CollabSelection()
        html = cs._render_custom()
        assert "dj-collab-sel" in html
        assert "dj-collab-sel__range" not in html


# ===========================================================================
# Activity Feed — Template Tag
# ===========================================================================

class TestActivityFeed:
    def test_basic_render(self):
        events = [
            {"user": "Alice", "action": "commented on", "target": "Issue #42",
             "time": "2m ago"},
        ]
        html = render('{% activity_feed events=events %}', {"events": events})
        assert "dj-activity-feed" in html
        assert "Alice" in html
        assert "commented on" in html
        assert "Issue #42" in html
        assert "2m ago" in html

    def test_avatar_image(self):
        events = [
            {"user": "Alice", "action": "x", "avatar": "/img/alice.jpg"},
        ]
        html = render('{% activity_feed events=events %}', {"events": events})
        assert "dj-activity-feed__avatar-img" in html
        assert "/img/alice.jpg" in html

    def test_initials_fallback(self):
        events = [{"user": "Alice Baker", "action": "x"}]
        html = render('{% activity_feed events=events %}', {"events": events})
        assert "dj-activity-feed__avatar-initials" in html
        assert "AB" in html

    def test_stream_event(self):
        html = render(
            '{% activity_feed events=events stream="activity_update" %}',
            {"events": []},
        )
        assert 'data-stream-event="activity_update"' in html
        assert 'dj-hook="ActivityFeed"' in html

    def test_no_hook_without_stream(self):
        html = render('{% activity_feed events=events %}', {"events": []})
        assert 'dj-hook="ActivityFeed"' not in html

    def test_role_feed(self):
        html = render('{% activity_feed events=events %}', {"events": []})
        assert 'role="feed"' in html

    def test_role_article(self):
        events = [{"user": "A", "action": "x"}]
        html = render('{% activity_feed events=events %}', {"events": events})
        assert 'role="article"' in html

    def test_empty_events(self):
        html = render('{% activity_feed events=events %}', {"events": []})
        assert "dj-activity-feed" in html
        assert "dj-activity-feed__item" not in html

    def test_custom_class(self):
        html = render('{% activity_feed events=events class="extra" %}', {"events": []})
        assert "extra" in html

    def test_icon(self):
        events = [{"user": "A", "action": "x", "icon": "🔔"}]
        html = render('{% activity_feed events=events %}', {"events": events})
        assert "dj-activity-feed__icon" in html

    def test_target_optional(self):
        events = [{"user": "A", "action": "logged in"}]
        html = render('{% activity_feed events=events %}', {"events": events})
        assert "dj-activity-feed__target" not in html

    def test_time_optional(self):
        events = [{"user": "A", "action": "x"}]
        html = render('{% activity_feed events=events %}', {"events": events})
        assert "dj-activity-feed__time" not in html

    def test_max_items(self):
        events = [{"user": f"U{i}", "action": "x"} for i in range(10)]
        html = render('{% activity_feed events=events max=3 %}', {"events": events})
        assert html.count("dj-activity-feed__item") == 3


# ===========================================================================
# Activity Feed — Component Class
# ===========================================================================

class TestActivityFeedClass:
    def test_basic(self):
        from djust_components.components.activity_feed import ActivityFeed
        af = ActivityFeed(
            events=[
                {"user": "Alice", "action": "pushed", "target": "main",
                 "time": "1m ago"},
            ],
        )
        html = af._render_custom()
        assert "dj-activity-feed" in html
        assert "Alice" in html
        assert "pushed" in html

    def test_stream(self):
        from djust_components.components.activity_feed import ActivityFeed
        af = ActivityFeed(stream_event="updates")
        html = af._render_custom()
        assert 'data-stream-event="updates"' in html

    def test_empty(self):
        from djust_components.components.activity_feed import ActivityFeed
        af = ActivityFeed()
        html = af._render_custom()
        assert "dj-activity-feed" in html
        assert "dj-activity-feed__item" not in html


# ===========================================================================
# Reactions — Template Tag
# ===========================================================================

class TestReactions:
    def test_basic_render(self):
        options = ["\U0001f44d", "\u2764\ufe0f"]
        counts = {"\U0001f44d": 5, "\u2764\ufe0f": 2}
        html = render(
            '{% reactions options=options counts=counts event="react" %}',
            {"options": options, "counts": counts},
        )
        assert "dj-reactions" in html
        assert "dj-reactions__btn" in html
        assert "5" in html
        assert "2" in html

    def test_active_state(self):
        options = ["\U0001f44d"]
        active = ["\U0001f44d"]
        html = render(
            '{% reactions options=options counts=counts active=active %}',
            {"options": options, "counts": {}, "active": active},
        )
        assert "dj-reactions__btn--active" in html
        assert 'aria-pressed="true"' in html

    def test_inactive_state(self):
        options = ["\U0001f44d"]
        html = render(
            '{% reactions options=options counts=counts %}',
            {"options": options, "counts": {}},
        )
        assert "dj-reactions__btn--active" not in html
        assert 'aria-pressed="false"' in html

    def test_event(self):
        html = render(
            '{% reactions options=options counts=counts event="vote" %}',
            {"options": ["x"], "counts": {}},
        )
        assert 'dj-click="vote"' in html

    def test_default_event(self):
        html = render(
            '{% reactions options=options counts=counts %}',
            {"options": ["x"], "counts": {}},
        )
        assert 'dj-click="react"' in html

    def test_dj_value_emoji(self):
        html = render(
            '{% reactions options=options counts=counts %}',
            {"options": ["x"], "counts": {}},
        )
        assert 'dj-value-emoji="x"' in html

    def test_count_hidden_when_zero(self):
        html = render(
            '{% reactions options=options counts=counts %}',
            {"options": ["x"], "counts": {"x": 0}},
        )
        assert "dj-reactions__count" not in html

    def test_count_shown_when_positive(self):
        html = render(
            '{% reactions options=options counts=counts %}',
            {"options": ["x"], "counts": {"x": 3}},
        )
        assert "dj-reactions__count" in html
        assert "3" in html

    def test_role_group(self):
        html = render(
            '{% reactions options=options counts=counts %}',
            {"options": [], "counts": {}},
        )
        assert 'role="group"' in html

    def test_aria_label(self):
        html = render(
            '{% reactions options=options counts=counts %}',
            {"options": [], "counts": {}},
        )
        assert 'aria-label="Reactions"' in html

    def test_custom_class(self):
        html = render(
            '{% reactions options=options counts=counts class="extra" %}',
            {"options": [], "counts": {}},
        )
        assert "extra" in html

    def test_empty_options(self):
        html = render(
            '{% reactions options=options counts=counts %}',
            {"options": [], "counts": {}},
        )
        assert "dj-reactions" in html
        assert "dj-reactions__btn" not in html


# ===========================================================================
# Reactions — Component Class
# ===========================================================================

class TestReactionsClass:
    def test_basic(self):
        from djust_components.components.reactions import Reactions
        r = Reactions(
            options=["\U0001f44d", "\u2764\ufe0f"],
            counts={"\U0001f44d": 3},
            event="react",
        )
        html = r._render_custom()
        assert "dj-reactions" in html
        assert "3" in html

    def test_active(self):
        from djust_components.components.reactions import Reactions
        r = Reactions(
            options=["\U0001f44d"],
            active=["\U0001f44d"],
        )
        html = r._render_custom()
        assert "dj-reactions__btn--active" in html

    def test_empty(self):
        from djust_components.components.reactions import Reactions
        r = Reactions()
        html = r._render_custom()
        assert "dj-reactions" in html
        assert "dj-reactions__btn" not in html


# ===========================================================================
# XSS Escaping
# ===========================================================================

class TestCollabSuiteXSS:
    """Verify that user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # --- Cursors Overlay XSS ---

    def test_cursors_name_xss(self):
        users = [{"name": self.XSS, "x": 0, "y": 0}]
        html = render('{% cursors users=users %}', {"users": users})
        self._assert_no_script(html)

    def test_cursors_color_xss(self):
        users = [{"name": "A", "color": self.XSS_ATTR, "x": 0, "y": 0}]
        html = render('{% cursors users=users %}', {"users": users})
        self._assert_attr_escaped(html)

    def test_cursors_class_xss(self):
        html = render(
            '{% cursors users=users class=bad %}',
            {"users": [], "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Live Indicator XSS ---

    def test_indicator_name_xss(self):
        user = {"name": self.XSS}
        html = render('{% live_indicator user=user %}', {"user": user})
        self._assert_no_script(html)

    def test_indicator_avatar_xss(self):
        user = {"name": "A", "avatar": self.XSS_ATTR}
        html = render('{% live_indicator user=user %}', {"user": user})
        self._assert_attr_escaped(html)

    def test_indicator_field_xss(self):
        user = {"name": "A"}
        html = render(
            '{% live_indicator user=user field=bad %}',
            {"user": user, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_indicator_action_xss(self):
        user = {"name": "A"}
        html = render(
            '{% live_indicator user=user action=bad %}',
            {"user": user, "bad": self.XSS},
        )
        self._assert_no_script(html)

    def test_indicator_class_xss(self):
        user = {"name": "A"}
        html = render(
            '{% live_indicator user=user class=bad %}',
            {"user": user, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Collaborative Selection XSS ---

    def test_collab_sel_name_xss(self):
        users = [{"name": self.XSS, "text": "x"}]
        html = render('{% collab_selection users=users %}', {"users": users})
        self._assert_no_script(html)

    def test_collab_sel_text_xss(self):
        users = [{"name": "A", "text": self.XSS}]
        html = render('{% collab_selection users=users %}', {"users": users})
        self._assert_no_script(html)

    def test_collab_sel_color_xss(self):
        users = [{"name": "A", "color": self.XSS_ATTR, "text": "x"}]
        html = render('{% collab_selection users=users %}', {"users": users})
        self._assert_attr_escaped(html)

    def test_collab_sel_class_xss(self):
        html = render(
            '{% collab_selection users=users class=bad %}',
            {"users": [], "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Activity Feed XSS ---

    def test_activity_user_xss(self):
        events = [{"user": self.XSS, "action": "x"}]
        html = render('{% activity_feed events=events %}', {"events": events})
        self._assert_no_script(html)

    def test_activity_action_xss(self):
        events = [{"user": "A", "action": self.XSS}]
        html = render('{% activity_feed events=events %}', {"events": events})
        self._assert_no_script(html)

    def test_activity_target_xss(self):
        events = [{"user": "A", "action": "x", "target": self.XSS}]
        html = render('{% activity_feed events=events %}', {"events": events})
        self._assert_no_script(html)

    def test_activity_time_xss(self):
        events = [{"user": "A", "action": "x", "time": self.XSS}]
        html = render('{% activity_feed events=events %}', {"events": events})
        self._assert_no_script(html)

    def test_activity_avatar_xss(self):
        events = [{"user": "A", "action": "x", "avatar": self.XSS_ATTR}]
        html = render('{% activity_feed events=events %}', {"events": events})
        self._assert_attr_escaped(html)

    def test_activity_stream_xss(self):
        html = render(
            '{% activity_feed events=events stream=bad %}',
            {"events": [], "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_activity_class_xss(self):
        html = render(
            '{% activity_feed events=events class=bad %}',
            {"events": [], "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Reactions XSS ---

    def test_reactions_event_xss(self):
        html = render(
            '{% reactions options=options counts=counts event=bad %}',
            {"options": ["x"], "counts": {}, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_reactions_emoji_xss(self):
        html = render(
            '{% reactions options=options counts=counts %}',
            {"options": [self.XSS], "counts": {}},
        )
        self._assert_no_script(html)

    def test_reactions_class_xss(self):
        html = render(
            '{% reactions options=options counts=counts class=bad %}',
            {"options": [], "counts": {}, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)
