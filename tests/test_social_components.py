"""Tests for social/user-facing components: Avatar Group, Hover Card, Notification Popover."""
from django.template import Template, Context
import pytest


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ===========================================================================
# Avatar Group (#89)
# ===========================================================================


class TestAvatarGroup:
    def test_basic_render(self):
        users = [{"name": "Alice"}, {"name": "Bob"}]
        html = render('{% avatar_group users=users %}', {"users": users})
        assert "dj-avatar-group" in html
        assert "A" in html  # Alice initials
        assert "B" in html  # Bob initials

    def test_with_avatars(self):
        users = [{"name": "Alice", "avatar": "/img/alice.jpg"}]
        html = render('{% avatar_group users=users %}', {"users": users})
        assert "/img/alice.jpg" in html
        assert 'alt="Alice"' in html
        assert "dj-avatar-group__img" in html

    def test_overflow_count(self):
        users = [{"name": f"User{i}"} for i in range(8)]
        html = render('{% avatar_group users=users max=5 %}', {"users": users})
        assert "+3" in html
        assert "dj-avatar-group__overflow" in html

    def test_no_overflow_when_within_max(self):
        users = [{"name": "A"}, {"name": "B"}]
        html = render('{% avatar_group users=users max=5 %}', {"users": users})
        assert "dj-avatar-group__overflow" not in html

    def test_exactly_max_no_overflow(self):
        users = [{"name": f"U{i}"} for i in range(5)]
        html = render('{% avatar_group users=users max=5 %}', {"users": users})
        assert "dj-avatar-group__overflow" not in html

    def test_size_sm(self):
        html = render(
            '{% avatar_group users=users size="sm" %}',
            {"users": [{"name": "A"}]},
        )
        assert "dj-avatar-group--sm" in html

    def test_size_lg(self):
        html = render(
            '{% avatar_group users=users size="lg" %}',
            {"users": [{"name": "A"}]},
        )
        assert "dj-avatar-group--lg" in html

    def test_custom_class(self):
        html = render(
            '{% avatar_group users=users class="my-cls" %}',
            {"users": [{"name": "A"}]},
        )
        assert "my-cls" in html

    def test_empty_users(self):
        html = render('{% avatar_group users=users %}', {"users": []})
        assert "dj-avatar-group" in html
        assert "dj-avatar-group__item" not in html

    def test_initials_two_words(self):
        users = [{"name": "Alice Wonderland"}]
        html = render('{% avatar_group users=users %}', {"users": users})
        assert "AW" in html

    def test_z_index_stacking(self):
        users = [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        html = render('{% avatar_group users=users %}', {"users": users})
        assert "z-index:3" in html  # first item
        assert "z-index:1" in html  # last item


# ===========================================================================
# Hover Card (#91)
# ===========================================================================


class TestHoverCard:
    def test_basic_render(self):
        html = render(
            '{% hover_card trigger="@alice" %}<p>Alice info</p>{% endhover_card %}'
        )
        assert "dj-hover-card" in html
        assert "@alice" in html
        assert "<p>Alice info</p>" in html
        assert "dj-hover-card__content" in html

    def test_position_top(self):
        html = render(
            '{% hover_card trigger="x" position="top" %}content{% endhover_card %}'
        )
        assert "dj-hover-card--top" in html

    def test_position_bottom_default(self):
        html = render(
            '{% hover_card trigger="x" %}content{% endhover_card %}'
        )
        assert "dj-hover-card--bottom" in html

    def test_delay_attributes(self):
        html = render(
            '{% hover_card trigger="x" delay_in=100 delay_out=500 %}'
            'content{% endhover_card %}'
        )
        assert 'data-delay-in="100"' in html
        assert 'data-delay-out="500"' in html

    def test_default_delays(self):
        html = render(
            '{% hover_card trigger="x" %}content{% endhover_card %}'
        )
        assert 'data-delay-in="200"' in html
        assert 'data-delay-out="300"' in html

    def test_custom_class(self):
        html = render(
            '{% hover_card trigger="x" class="custom" %}c{% endhover_card %}'
        )
        assert "custom" in html

    def test_trigger_from_variable(self):
        html = render(
            '{% hover_card trigger=name %}info{% endhover_card %}',
            {"name": "@bob"},
        )
        assert "@bob" in html

    def test_rich_content(self):
        html = render(
            '{% hover_card trigger="user" %}'
            '<img src="/pic.jpg"><strong>Name</strong>'
            '{% endhover_card %}'
        )
        assert '<img src="/pic.jpg">' in html
        assert "<strong>Name</strong>" in html


# ===========================================================================
# Notification Popover (#168)
# ===========================================================================


class TestNotificationPopover:
    def test_basic_render_closed(self):
        html = render(
            '{% notification_popover notifications=notifs unread_count=count %}',
            {"notifs": [], "count": 0},
        )
        assert "dj-notif-popover" in html
        assert "dj-notif-popover__bell" in html
        assert "dj-notif-popover__panel" not in html  # closed

    def test_bell_icon_present(self):
        html = render(
            '{% notification_popover notifications=notifs %}',
            {"notifs": []},
        )
        assert "<svg" in html
        assert 'aria-label="Notifications"' in html

    def test_unread_badge(self):
        html = render(
            '{% notification_popover notifications=notifs unread_count=count %}',
            {"notifs": [], "count": 5},
        )
        assert "dj-notif-popover__badge" in html
        assert "5" in html

    def test_badge_overflow_99(self):
        html = render(
            '{% notification_popover notifications=notifs unread_count=count %}',
            {"notifs": [], "count": 150},
        )
        assert "99+" in html

    def test_no_badge_when_zero(self):
        html = render(
            '{% notification_popover notifications=notifs unread_count=count %}',
            {"notifs": [], "count": 0},
        )
        assert "dj-notif-popover__badge" not in html

    def test_open_shows_panel(self):
        notifs = [
            {"id": "1", "title": "Deploy", "body": "v2 deployed", "time": "2m ago"},
        ]
        html = render(
            '{% notification_popover notifications=notifs open=is_open %}',
            {"notifs": notifs, "is_open": True},
        )
        assert 'data-open' in html
        assert "dj-notif-popover__panel" in html
        assert "Deploy" in html
        assert "v2 deployed" in html
        assert "2m ago" in html

    def test_notification_items(self):
        notifs = [
            {"id": "1", "title": "A", "body": "msg1", "time": "1m"},
            {"id": "2", "title": "B", "body": "msg2", "time": "5m", "read": True},
        ]
        html = render(
            '{% notification_popover notifications=notifs open=is_open %}',
            {"notifs": notifs, "is_open": True},
        )
        assert "dj-notif-popover__item-title" in html
        assert "dj-notif-popover__item--read" in html

    def test_unread_item_has_mark_read_event(self):
        notifs = [{"id": "42", "title": "X", "body": "y"}]
        html = render(
            '{% notification_popover notifications=notifs open=is_open mark_read_event="mark_read" %}',
            {"notifs": notifs, "is_open": True},
        )
        assert 'dj-click="mark_read"' in html
        assert 'data-id="42"' in html

    def test_read_item_no_mark_event(self):
        notifs = [{"id": "42", "title": "X", "body": "y", "read": True}]
        html = render(
            '{% notification_popover notifications=notifs open=is_open %}',
            {"notifs": notifs, "is_open": True},
        )
        # Read items should not have the mark_read click handler
        assert 'data-id="42"' not in html

    def test_toggle_event(self):
        html = render(
            '{% notification_popover notifications=notifs toggle_event="toggle_notifs" %}',
            {"notifs": []},
        )
        assert 'dj-click="toggle_notifs"' in html

    def test_empty_state(self):
        html = render(
            '{% notification_popover notifications=notifs open=is_open %}',
            {"notifs": [], "is_open": True},
        )
        assert "No notifications" in html
        assert "dj-notif-popover__empty" in html

    def test_custom_title(self):
        html = render(
            '{% notification_popover notifications=notifs open=is_open title="Alerts" %}',
            {"notifs": [], "is_open": True},
        )
        assert "Alerts" in html

    def test_custom_class(self):
        html = render(
            '{% notification_popover notifications=notifs class="my-class" %}',
            {"notifs": []},
        )
        assert "my-class" in html


# ===========================================================================
# XSS Escaping
# ===========================================================================


class TestXSSEscaping:
    """Verify that user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_script(self, html):
        assert "<script>" not in html

    def _assert_attr_escaped(self, html):
        # The raw attribute injection payload would break out of a quoted attr.
        # If properly escaped, the literal sequence '" onmouseover="' must NOT
        # appear unescaped — i.e. the double-quote must be &quot; not a raw ".
        assert '" onmouseover="' not in html

    # --- Avatar Group ---

    def test_avatar_group_name_xss(self):
        users = [{"name": self.XSS}]
        html = render('{% avatar_group users=users %}', {"users": users})
        self._assert_no_script(html)

    def test_avatar_group_name_attr_xss(self):
        users = [{"name": self.XSS_ATTR}]
        html = render('{% avatar_group users=users %}', {"users": users})
        self._assert_attr_escaped(html)

    def test_avatar_group_avatar_xss(self):
        users = [{"name": "A", "avatar": self.XSS_ATTR}]
        html = render('{% avatar_group users=users %}', {"users": users})
        self._assert_attr_escaped(html)

    def test_avatar_group_size_xss(self):
        users = [{"name": "A"}]
        html = render(
            '{% avatar_group users=users size=bad %}',
            {"users": users, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_avatar_group_class_xss(self):
        users = [{"name": "A"}]
        html = render(
            '{% avatar_group users=users class=bad %}',
            {"users": users, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Hover Card ---

    def test_hover_card_trigger_xss(self):
        html = render(
            '{% hover_card trigger=bad %}c{% endhover_card %}',
            {"bad": self.XSS},
        )
        self._assert_no_script(html)

    def test_hover_card_trigger_attr_xss(self):
        html = render(
            '{% hover_card trigger=bad %}c{% endhover_card %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_hover_card_position_xss(self):
        html = render(
            '{% hover_card trigger="x" position=bad %}c{% endhover_card %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_hover_card_class_xss(self):
        html = render(
            '{% hover_card trigger="x" class=bad %}c{% endhover_card %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Notification Popover ---

    def test_notif_popover_title_xss(self):
        html = render(
            '{% notification_popover notifications=n open=o title=bad %}',
            {"n": [], "o": True, "bad": self.XSS},
        )
        self._assert_no_script(html)

    def test_notif_popover_toggle_event_xss(self):
        html = render(
            '{% notification_popover notifications=n toggle_event=bad %}',
            {"n": [], "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_notif_popover_mark_read_event_xss(self):
        notifs = [{"id": "1", "title": "A", "body": "B"}]
        html = render(
            '{% notification_popover notifications=n open=o mark_read_event=bad %}',
            {"n": notifs, "o": True, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_notif_popover_notification_title_xss(self):
        notifs = [{"id": "1", "title": self.XSS, "body": "B"}]
        html = render(
            '{% notification_popover notifications=n open=o %}',
            {"n": notifs, "o": True},
        )
        self._assert_no_script(html)

    def test_notif_popover_notification_body_xss(self):
        notifs = [{"id": "1", "title": "A", "body": self.XSS}]
        html = render(
            '{% notification_popover notifications=n open=o %}',
            {"n": notifs, "o": True},
        )
        self._assert_no_script(html)

    def test_notif_popover_notification_id_xss(self):
        notifs = [{"id": self.XSS_ATTR, "title": "A", "body": "B"}]
        html = render(
            '{% notification_popover notifications=n open=o %}',
            {"n": notifs, "o": True},
        )
        self._assert_attr_escaped(html)

    def test_notif_popover_class_xss(self):
        html = render(
            '{% notification_popover notifications=n class=bad %}',
            {"n": [], "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)
