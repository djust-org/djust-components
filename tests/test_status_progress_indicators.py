"""Tests for status/progress indicator components — template tags, component classes, and XSS."""
from django.template import Template, Context
import pytest

from djust_components.components import (
    NotificationBadge,
    ProgressCircle,
    SegmentedProgress,
    StatusIndicator,
)


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ─── Notification Badge (Template Tag) ───

class TestNotificationBadgeTag:
    def test_basic_count(self):
        html = render('{% notification_badge count=5 %}')
        assert "dj-notification-badge" in html
        assert ">5<" in html

    def test_zero_count_hidden(self):
        html = render('{% notification_badge count=0 %}')
        assert html.strip() == ""

    def test_negative_count_hidden(self):
        html = render('{% notification_badge count=cnt %}', {"cnt": -3})
        assert html.strip() == ""

    def test_max_count_overflow(self):
        html = render('{% notification_badge count=cnt %}', {"cnt": 150})
        assert "99+" in html

    def test_custom_max_count(self):
        html = render('{% notification_badge count=cnt max=max_c %}', {"cnt": 50, "max_c": 9})
        assert "9+" in html

    def test_dot_mode(self):
        html = render('{% notification_badge dot=True %}')
        assert "dj-notification-badge--dot" in html

    def test_pulse(self):
        html = render('{% notification_badge count=3 pulse=True %}')
        assert "dj-notification-badge--pulse" in html

    def test_sizes(self):
        for size in ("sm", "md", "lg"):
            html = render(f'{{% notification_badge count=1 size="{size}" %}}')
            assert f"dj-notification-badge--{size}" in html

    def test_custom_class(self):
        html = render('{% notification_badge count=1 custom_class="extra" %}')
        assert "extra" in html

    def test_variable_count(self):
        html = render('{% notification_badge count=n %}', {"n": 42})
        assert ">42<" in html


# ─── Segmented Progress (Template Tag) ───

class TestSegmentedProgressTag:
    def test_basic_render(self):
        steps = ["A", "B", "C"]
        html = render('{% segmented_progress steps=steps current=2 %}', {"steps": steps})
        assert "dj-segmented-progress" in html
        assert "dj-segmented-progress__step--completed" in html
        assert "dj-segmented-progress__step--active" in html
        assert "dj-segmented-progress__step--pending" in html

    def test_step_labels(self):
        steps = ["Account", "Profile", "Review"]
        html = render('{% segmented_progress steps=steps current=1 %}', {"steps": steps})
        assert "Account" in html
        assert "Profile" in html
        assert "Review" in html

    def test_dict_steps(self):
        steps = [{"label": "Cart"}, {"label": "Ship"}, {"label": "Pay"}]
        html = render('{% segmented_progress steps=steps current=2 %}', {"steps": steps})
        assert "Cart" in html
        assert "Ship" in html
        assert "Pay" in html

    def test_connectors(self):
        steps = ["A", "B", "C"]
        html = render('{% segmented_progress steps=steps current=2 %}', {"steps": steps})
        assert "dj-segmented-progress__connector--completed" in html
        assert "dj-segmented-progress__connector--pending" in html

    def test_all_completed(self):
        steps = ["A", "B"]
        html = render('{% segmented_progress steps=steps current=3 %}', {"steps": steps})
        assert "dj-segmented-progress__step--pending" not in html
        assert "dj-segmented-progress__step--active" not in html

    def test_sizes(self):
        steps = ["A"]
        for size in ("sm", "md", "lg"):
            html = render(
                f'{{% segmented_progress steps=steps current=1 size="{size}" %}}',
                {"steps": steps},
            )
            assert f"dj-segmented-progress--{size}" in html

    def test_empty_steps(self):
        html = render('{% segmented_progress steps=steps current=1 %}', {"steps": []})
        assert "dj-segmented-progress" in html
        assert "dj-segmented-progress__step" not in html

    def test_step_numbering(self):
        steps = ["First", "Second"]
        html = render('{% segmented_progress steps=steps current=1 %}', {"steps": steps})
        assert ">1<" in html
        assert ">2<" in html


# ─── Progress Circle (Template Tag) ───

class TestProgressCircleTag:
    def test_basic_render(self):
        html = render('{% progress_circle value=65 %}')
        assert "dj-progress-circle" in html
        assert "65%" in html
        assert "<svg" in html
        assert "stroke-dasharray" in html

    def test_zero_value(self):
        html = render('{% progress_circle value=0 %}')
        assert "0%" in html
        assert 'aria-valuenow="0"' in html

    def test_full_value(self):
        html = render('{% progress_circle value=100 %}')
        assert "100%" in html

    def test_clamped_over_100(self):
        html = render('{% progress_circle value=val %}', {"val": 200})
        assert "100%" in html

    def test_clamped_negative(self):
        html = render('{% progress_circle value=val %}', {"val": -10})
        assert "0%" in html

    def test_sizes(self):
        for size in ("sm", "md", "lg"):
            html = render(f'{{% progress_circle value=50 size="{size}" %}}')
            assert f"dj-progress-circle--{size}" in html

    def test_color_variants(self):
        for color in ("primary", "success", "warning", "danger"):
            html = render(f'{{% progress_circle value=50 color="{color}" %}}')
            assert f"dj-progress-circle--{color}" in html

    def test_hide_value(self):
        html = render('{% progress_circle value=50 show_value=False %}')
        assert "dj-progress-circle__value" not in html
        assert "50%" not in html

    def test_aria_attributes(self):
        html = render('{% progress_circle value=75 %}')
        assert 'role="progressbar"' in html
        assert 'aria-valuenow="75"' in html
        assert 'aria-valuemin="0"' in html
        assert 'aria-valuemax="100"' in html

    def test_svg_dimensions_sm(self):
        html = render('{% progress_circle value=50 size="sm" %}')
        assert 'width="48"' in html
        assert 'height="48"' in html

    def test_svg_dimensions_lg(self):
        html = render('{% progress_circle value=50 size="lg" %}')
        assert 'width="120"' in html
        assert 'height="120"' in html


# ─── Status Indicator (Template Tag) ───

class TestStatusIndicatorTag:
    def test_basic_render(self):
        html = render('{% status_indicator status="online" label="API" %}')
        assert "dj-status-indicator" in html
        assert "dj-status-indicator--green" in html
        assert "API" in html

    def test_status_color_mapping(self):
        mappings = {
            "online": "green",
            "degraded": "yellow",
            "offline": "red",
            "maintenance": "blue",
        }
        for status, color in mappings.items():
            html = render(f'{{% status_indicator status="{status}" %}}')
            assert f"dj-status-indicator--{color}" in html

    def test_unknown_status_gray(self):
        html = render('{% status_indicator status="unknown" %}')
        assert "dj-status-indicator--gray" in html

    def test_no_label(self):
        html = render('{% status_indicator status="online" %}')
        assert "dj-status-indicator__label" not in html

    def test_with_label(self):
        html = render('{% status_indicator status="offline" label="DB" %}')
        assert "dj-status-indicator__label" in html
        assert "DB" in html

    def test_pulse(self):
        html = render('{% status_indicator status="online" pulse=True %}')
        assert "dj-status-indicator--pulse" in html

    def test_sizes(self):
        for size in ("sm", "md", "lg"):
            html = render(f'{{% status_indicator status="online" size="{size}" %}}')
            assert f"dj-status-indicator--{size}" in html

    def test_dot_always_present(self):
        html = render('{% status_indicator status="online" %}')
        assert "dj-status-indicator__dot" in html

    def test_variable_status(self):
        html = render('{% status_indicator status=s label=lbl %}', {"s": "degraded", "lbl": "CDN"})
        assert "dj-status-indicator--yellow" in html
        assert "CDN" in html


# ─── XSS Escaping ───

class TestXSSEscaping:
    """Verify that user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_attr_escaped(self, html, payload=None):
        if payload is None:
            payload = self.XSS_ATTR
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # Notification Badge
    def test_notification_badge_custom_class_xss(self):
        html = render(
            '{% notification_badge count=1 custom_class=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_notification_badge_size_xss(self):
        html = render(
            '{% notification_badge count=1 size=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Segmented Progress
    def test_segmented_progress_label_xss(self):
        steps = [self.XSS]
        html = render(
            '{% segmented_progress steps=steps current=1 %}',
            {"steps": steps},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_segmented_progress_dict_label_xss(self):
        steps = [{"label": self.XSS}]
        html = render(
            '{% segmented_progress steps=steps current=1 %}',
            {"steps": steps},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_segmented_progress_custom_class_xss(self):
        html = render(
            '{% segmented_progress steps=steps current=1 custom_class=xss %}',
            {"steps": ["A"], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Progress Circle
    def test_progress_circle_custom_class_xss(self):
        html = render(
            '{% progress_circle value=50 custom_class=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_progress_circle_color_xss(self):
        html = render(
            '{% progress_circle value=50 color=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_progress_circle_size_xss(self):
        html = render(
            '{% progress_circle value=50 size=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Status Indicator
    def test_status_indicator_label_xss(self):
        html = render(
            '{% status_indicator status="online" label=xss %}',
            {"xss": self.XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_status_indicator_status_xss(self):
        html = render(
            '{% status_indicator status=xss %}',
            {"xss": self.XSS_ATTR},
        )
        # Status goes through dict lookup (maps to "gray"), so payload never reaches output
        assert '" onmouseover="' not in html
        assert "alert(1)" not in html

    def test_status_indicator_custom_class_xss(self):
        html = render(
            '{% status_indicator status="online" custom_class=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_status_indicator_size_xss(self):
        html = render(
            '{% status_indicator status="online" size=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)


# ─── Component Classes ───

class TestNotificationBadgeClass:
    def test_basic_count(self):
        badge = NotificationBadge(count=5)
        html = badge._render_custom()
        assert "dj-notification-badge" in html
        assert ">5<" in html

    def test_zero_hidden(self):
        badge = NotificationBadge(count=0)
        assert badge._render_custom() == ""

    def test_max_count(self):
        badge = NotificationBadge(count=150, max_count=99)
        html = badge._render_custom()
        assert "99+" in html

    def test_custom_max(self):
        badge = NotificationBadge(count=15, max_count=9)
        html = badge._render_custom()
        assert "9+" in html

    def test_dot_mode(self):
        badge = NotificationBadge(dot=True)
        html = badge._render_custom()
        assert "dj-notification-badge--dot" in html

    def test_pulse(self):
        badge = NotificationBadge(count=3, pulse=True)
        html = badge._render_custom()
        assert "dj-notification-badge--pulse" in html

    def test_sizes(self):
        for size in ("sm", "md", "lg"):
            badge = NotificationBadge(count=1, size=size)
            html = badge._render_custom()
            assert f"dj-notification-badge--{size}" in html


class TestSegmentedProgressClass:
    def test_basic(self):
        sp = SegmentedProgress(steps=["A", "B", "C"], current=2)
        html = sp._render_custom()
        assert "dj-segmented-progress" in html
        assert "dj-segmented-progress__step--completed" in html
        assert "dj-segmented-progress__step--active" in html
        assert "dj-segmented-progress__step--pending" in html

    def test_dict_steps(self):
        sp = SegmentedProgress(steps=[{"label": "X"}, {"label": "Y"}], current=1)
        html = sp._render_custom()
        assert "X" in html
        assert "Y" in html

    def test_connectors(self):
        sp = SegmentedProgress(steps=["A", "B"], current=1)
        html = sp._render_custom()
        assert "dj-segmented-progress__connector" in html

    def test_empty_steps(self):
        sp = SegmentedProgress(steps=[], current=1)
        html = sp._render_custom()
        assert "dj-segmented-progress__step" not in html

    def test_xss_label(self):
        sp = SegmentedProgress(steps=['<script>alert(1)</script>'], current=1)
        html = sp._render_custom()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


class TestProgressCircleClass:
    def test_basic(self):
        pc = ProgressCircle(value=65)
        html = pc._render_custom()
        assert "dj-progress-circle" in html
        assert "65%" in html
        assert "<svg" in html

    def test_clamped(self):
        pc = ProgressCircle(value=200)
        assert pc.value == 100
        pc2 = ProgressCircle(value=-10)
        assert pc2.value == 0

    def test_sizes(self):
        for size in ("sm", "md", "lg"):
            pc = ProgressCircle(value=50, size=size)
            html = pc._render_custom()
            assert f"dj-progress-circle--{size}" in html

    def test_colors(self):
        for color in ("primary", "success", "warning", "danger"):
            pc = ProgressCircle(value=50, color=color)
            html = pc._render_custom()
            assert f"dj-progress-circle--{color}" in html

    def test_hide_value(self):
        pc = ProgressCircle(value=50, show_value=False)
        html = pc._render_custom()
        assert "dj-progress-circle__value" not in html

    def test_aria(self):
        pc = ProgressCircle(value=75)
        html = pc._render_custom()
        assert 'role="progressbar"' in html
        assert 'aria-valuenow="75"' in html


class TestStatusIndicatorClass:
    def test_basic(self):
        si = StatusIndicator(status="online", label="API")
        html = si._render_custom()
        assert "dj-status-indicator--green" in html
        assert "API" in html

    def test_color_mapping(self):
        assert StatusIndicator(status="online").color == "green"
        assert StatusIndicator(status="degraded").color == "yellow"
        assert StatusIndicator(status="offline").color == "red"
        assert StatusIndicator(status="maintenance").color == "blue"
        assert StatusIndicator(status="unknown").color == "gray"

    def test_no_label(self):
        si = StatusIndicator(status="online")
        html = si._render_custom()
        assert "dj-status-indicator__label" not in html

    def test_pulse(self):
        si = StatusIndicator(status="online", pulse=True)
        html = si._render_custom()
        assert "dj-status-indicator--pulse" in html

    def test_sizes(self):
        for size in ("sm", "md", "lg"):
            si = StatusIndicator(status="online", size=size)
            html = si._render_custom()
            assert f"dj-status-indicator--{size}" in html

    def test_xss_label(self):
        si = StatusIndicator(status="online", label='<script>alert(1)</script>')
        html = si._render_custom()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
