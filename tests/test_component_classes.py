"""Tests for Component class implementations (Badge, StatusDot, etc.)."""

import pytest

from djust_components.components import Badge, StatusDot


class TestBadge:
    """Test Badge component."""

    def test_basic_badge(self):
        """Test basic badge creation."""
        badge = Badge("test label")
        html = badge._render_custom()

        assert "dj-badge" in html
        assert "test label" in html

    def test_badge_variants(self):
        """Test badge color variants."""
        variants = ["success", "info", "warning", "danger", "muted"]

        for variant in variants:
            badge = Badge("test", variant=variant)
            html = badge._render_custom()
            assert f"dj-badge-{variant}" in html

    def test_badge_sizes(self):
        """Test badge size variants."""
        sm = Badge("test", size="sm")
        md = Badge("test", size="md")
        lg = Badge("test", size="lg")

        assert "dj-badge-sm" in sm._render_custom()
        assert "dj-badge-sm" not in md._render_custom()  # md is default
        assert "dj-badge-lg" in lg._render_custom()

    def test_badge_status_mapping(self):
        """Test auto-colored status badges."""
        # Success states
        assert Badge.status("done").variant == "success"
        assert Badge.status("completed").variant == "success"
        assert Badge.status("passed").variant == "success"

        # Info states
        assert Badge.status("running").variant == "info"
        assert Badge.status("in_progress").variant == "info"

        # Warning states
        assert Badge.status("pending").variant == "warning"
        assert Badge.status("starting").variant == "warning"

        # Danger states
        assert Badge.status("failed").variant == "danger"
        assert Badge.status("error").variant == "danger"

        # Muted states
        assert Badge.status("skipped").variant == "muted"
        assert Badge.status("cancelled").variant == "muted"

    def test_badge_priority_mapping(self):
        """Test auto-colored priority badges."""
        assert Badge.priority("P0").variant == "danger"
        assert Badge.priority("P1").variant == "warning"
        assert Badge.priority("P2").variant == "info"
        assert Badge.priority("P3").variant == "muted"

        # Test case insensitivity
        assert Badge.priority("p0").variant == "danger"
        assert Badge.priority("p2").variant == "info"

    def test_badge_custom_status_map(self):
        """Test custom status mapping."""
        custom_map = {
            "my_status": "success",
        }
        badge = Badge.status("my_status", custom_map=custom_map)
        assert badge.variant == "success"

    def test_badge_custom_priority_map(self):
        """Test custom priority mapping."""
        custom_map = {
            "CRITICAL": "danger",
        }
        badge = Badge.priority("CRITICAL", custom_map=custom_map)
        assert badge.variant == "danger"

    def test_badge_html_escaping(self):
        """Test that badge labels are HTML escaped."""
        badge = Badge("<script>alert('xss')</script>")
        html = badge._render_custom()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_badge_custom_class(self):
        """Test custom CSS class addition."""
        badge = Badge("test", custom_class="my-custom-class")
        html = badge._render_custom()
        assert "my-custom-class" in html


class TestStatusDot:
    """Test StatusDot component."""

    def test_basic_status_dot(self):
        """Test basic status dot creation."""
        dot = StatusDot("running")
        html = dot._render_custom()

        assert "dj-status-dot" in html
        assert "dj-status-dot-success" in html  # running maps to success

    def test_status_dot_variants(self):
        """Test status dot color variants."""
        variants = ["success", "info", "warning", "danger", "muted"]

        for variant in variants:
            dot = StatusDot("test", variant=variant)
            html = dot._render_custom()
            assert f"dj-status-dot-{variant}" in html

    def test_status_dot_sizes(self):
        """Test status dot size variants."""
        sm = StatusDot("test", size="sm")
        md = StatusDot("test", size="md")
        lg = StatusDot("test", size="lg")

        assert "dj-status-dot-sm" in sm._render_custom()
        assert "dj-status-dot-sm" not in md._render_custom()  # md is default
        assert "dj-status-dot-lg" in lg._render_custom()

    def test_status_dot_auto_variant(self):
        """Test automatic variant mapping from status."""
        # Success states
        assert StatusDot("running").variant == "success"
        assert StatusDot("active").variant == "success"
        assert StatusDot("passed").variant == "success"

        # Info states
        assert StatusDot("completed").variant == "info"
        assert StatusDot("done").variant == "info"

        # Warning states
        assert StatusDot("pending").variant == "warning"
        assert StatusDot("starting").variant == "warning"

        # Danger states
        assert StatusDot("failed").variant == "danger"
        assert StatusDot("error").variant == "danger"

        # Muted states
        assert StatusDot("skipped").variant == "muted"
        assert StatusDot("cancelled").variant == "muted"

    def test_status_dot_auto_animation(self):
        """Test automatic animation mapping from status."""
        # Pulse animation for active states
        running = StatusDot("running")
        assert running.animate == "pulse"
        assert "dj-status-dot-pulse" in running._render_custom()

        # Spin animation for loading states
        loading = StatusDot("loading")
        assert loading.animate == "spin"
        assert "dj-status-dot-spin" in loading._render_custom()

        # No animation for completed states
        done = StatusDot("completed")
        assert done.animate is None
        assert "dj-status-dot-pulse" not in done._render_custom()
        assert "dj-status-dot-spin" not in done._render_custom()

    def test_status_dot_explicit_animation(self):
        """Test explicit animation override."""
        # Override default animation
        dot = StatusDot("running", animate="spin")
        assert dot.animate == "spin"
        assert "dj-status-dot-spin" in dot._render_custom()

        # Disable animation
        dot = StatusDot("running", animate=None)
        assert dot.animate is None
        assert "dj-status-dot-pulse" not in dot._render_custom()

    def test_status_dot_tooltip(self):
        """Test tooltip attribute."""
        dot = StatusDot("running", tooltip="Agent is active")
        html = dot._render_custom()
        assert 'title="Agent is active"' in html

    def test_status_dot_custom_status_map(self):
        """Test custom status variant mapping."""
        custom_map = {
            "my_status": "success",
        }
        dot = StatusDot("my_status", custom_status_map=custom_map)
        assert dot.variant == "success"

    def test_status_dot_custom_animation_map(self):
        """Test custom status animation mapping."""
        custom_map = {
            "my_status": "fade",
        }
        dot = StatusDot("my_status", custom_animation_map=custom_map)
        assert dot.animate == "fade"

    def test_status_dot_custom_class(self):
        """Test custom CSS class addition."""
        dot = StatusDot("running", custom_class="my-custom-class")
        html = dot._render_custom()
        assert "my-custom-class" in html
