"""Tests for Component class implementations (Badge, Button, Card, StatusDot, etc.)."""

import pytest

from djust_components.components import Badge, Button, Card, StatusDot


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


class TestButton:
    """Test Button component."""

    def test_basic_button(self):
        """Test basic button creation."""
        btn = Button("Click me")
        html = btn._render_custom()

        assert "dj-btn" in html
        assert "Click me" in html
        assert 'type="button"' in html

    def test_button_variants(self):
        """Test button color variants."""
        variants = ["primary", "secondary", "danger", "success", "ghost", "link", "text"]

        for variant in variants:
            btn = Button("test", variant=variant)
            html = btn._render_custom()
            if variant != "primary":  # primary is default, no class
                assert f"dj-btn-{variant}" in html

    def test_button_sizes(self):
        """Test button size variants."""
        sm = Button("test", size="sm")
        md = Button("test", size="md")
        lg = Button("test", size="lg")

        assert "dj-btn-sm" in sm._render_custom()
        assert "dj-btn-sm" not in md._render_custom()  # md is default
        assert "dj-btn-lg" in lg._render_custom()

    def test_button_with_action(self):
        """Test button with djust action."""
        btn = Button("Save", action="save_form")
        html = btn._render_custom()
        assert 'dj-click="save_form"' in html

    def test_button_with_data_attributes(self):
        """Test button with data attributes."""
        btn = Button("Delete", action="delete", data={"item_id": "123", "confirm": "true"})
        html = btn._render_custom()
        assert 'data-item_id="123"' in html
        assert 'data-confirm="true"' in html

    def test_button_disabled(self):
        """Test disabled button."""
        btn = Button("Submit", disabled=True, action="submit")
        html = btn._render_custom()
        assert "disabled" in html
        assert "dj-click" not in html  # Should not add action when disabled

    def test_button_loading(self):
        """Test loading button."""
        btn = Button("Processing", loading=True, action="process")
        html = btn._render_custom()
        assert "disabled" in html
        assert "dj-btn-loading" in html
        assert "dj-btn-spinner" in html
        assert "dj-click" not in html  # Should not add action when loading

    def test_button_with_icon_left(self):
        """Test button with left icon."""
        btn = Button("Save", icon="💾", icon_position="left")
        html = btn._render_custom()
        assert "dj-btn-icon" in html
        assert "dj-btn-icon-left" in html
        assert "💾" in html

    def test_button_with_icon_right(self):
        """Test button with right icon."""
        btn = Button("Next", icon="→", icon_position="right")
        html = btn._render_custom()
        assert "dj-btn-icon" in html
        assert "dj-btn-icon-right" in html
        assert "→" in html

    def test_button_html_escaping(self):
        """Test that button labels are HTML escaped."""
        btn = Button("<script>alert('xss')</script>")
        html = btn._render_custom()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_button_data_escaping(self):
        """Test that data attributes are HTML escaped."""
        btn = Button("test", data={"value": "<script>"})
        html = btn._render_custom()
        assert "&lt;script&gt;" in html

    def test_button_onclick(self):
        """Test button with onclick handler."""
        btn = Button("test", onclick="alert('test')")
        html = btn._render_custom()
        assert "onclick=" in html

    def test_button_custom_class(self):
        """Test custom CSS class addition."""
        btn = Button("test", custom_class="my-custom-btn")
        html = btn._render_custom()
        assert "my-custom-btn" in html

    def test_button_type_attribute(self):
        """Test button type attribute."""
        submit = Button("Submit", type="submit")
        reset = Button("Reset", type="reset")

        assert 'type="submit"' in submit._render_custom()
        assert 'type="reset"' in reset._render_custom()


class TestCard:
    """Test Card component."""

    def test_basic_card(self):
        """Test basic card creation."""
        card = Card(content="<p>Content</p>")
        html = card._render_custom()

        assert "dj-card" in html
        assert "<p>Content</p>" in html

    def test_card_variants(self):
        """Test card style variants."""
        variants = ["default", "bordered", "elevated", "flat"]

        for variant in variants:
            card = Card(content="test", variant=variant)
            html = card._render_custom()
            if variant != "default":  # default has no class
                assert f"dj-card-{variant}" in html

    def test_card_padding_variants(self):
        """Test card padding variants."""
        none = Card(content="test", padding="none")
        sm = Card(content="test", padding="sm")
        md = Card(content="test", padding="md")
        lg = Card(content="test", padding="lg")

        assert "dj-card-p-" not in none._render_custom()
        assert "dj-card-p-sm" in sm._render_custom()
        assert "dj-card-p-md" in md._render_custom()
        assert "dj-card-p-lg" in lg._render_custom()

    def test_card_with_header(self):
        """Test card with header."""
        card = Card(header="<h3>Title</h3>", content="<p>Content</p>")
        html = card._render_custom()
        assert "dj-card-header" in html
        assert "<h3>Title</h3>" in html

    def test_card_with_footer(self):
        """Test card with footer."""
        card = Card(content="<p>Content</p>", footer="<button>Action</button>")
        html = card._render_custom()
        assert "dj-card-footer" in html
        assert "<button>Action</button>" in html

    def test_card_with_image(self):
        """Test card with image."""
        card = Card(image='<img src="test.jpg">', content="<p>Content</p>")
        html = card._render_custom()
        assert "dj-card-image" in html
        assert '<img src="test.jpg">' in html

    def test_card_hover_effect(self):
        """Test card with hover effect."""
        card = Card(content="test", hover=True)
        html = card._render_custom()
        assert "dj-card-hover" in html

    def test_card_clickable(self):
        """Test clickable card with action."""
        card = Card(content="test", action="card_clicked", data={"card_id": "123"})
        html = card._render_custom()
        assert "dj-card-clickable" in html
        assert 'dj-click="card_clicked"' in html
        assert 'data-card_id="123"' in html

    def test_card_all_sections(self):
        """Test card with all sections."""
        card = Card(
            image='<img src="test.jpg">',
            header="<h3>Title</h3>",
            content="<p>Content</p>",
            footer="<button>Action</button>",
        )
        html = card._render_custom()
        assert "dj-card-image" in html
        assert "dj-card-header" in html
        assert "dj-card-content" in html
        assert "dj-card-footer" in html

    def test_card_custom_class(self):
        """Test custom CSS class addition."""
        card = Card(content="test", custom_class="my-custom-card")
        html = card._render_custom()
        assert "my-custom-card" in html

    def test_card_data_escaping(self):
        """Test that data attributes are HTML escaped."""
        card = Card(content="test", action="click", data={"value": "<script>"})
        html = card._render_custom()
        assert "&lt;script&gt;" in html
