"""Tests for Component class implementations (Badge, Button, Card, StatusDot, etc.)."""

import pytest

from djust_components.components import (
    Alert,
    Badge,
    Button,
    Card,
    Markdown,
    Progress,
    Spinner,
    StatCard,
    StatusDot,
    Switch,
    Tag,
    Toast,
)


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


class TestMarkdown:
    """Test Markdown component."""

    def test_basic_rendering(self):
        """Test basic markdown to HTML conversion."""
        md = Markdown("# Hello\n\nWorld")
        html = md._render_custom()
        assert "<h1>Hello</h1>" in html
        assert "<p>World</p>" in html

    def test_wrapper_div(self):
        """Test output is wrapped in dj-prose div."""
        md = Markdown("hello")
        html = md._render_custom()
        assert 'class="dj-prose"' in html
        assert html.startswith('<div class="dj-prose">')

    def test_empty_text(self):
        """Test empty text returns empty string."""
        assert Markdown("")._render_custom() == ""
        assert Markdown()._render_custom() == ""

    def test_custom_class(self):
        """Test custom_class is added to wrapper."""
        md = Markdown("hello", custom_class="text-sm")
        html = md._render_custom()
        assert 'class="dj-prose text-sm"' in html

    def test_xss_prevention(self):
        """Script tags are stripped from rendered output."""
        md = Markdown("<script>alert('xss')</script>")
        html = md._render_custom()
        assert "<script>" not in html
        assert "alert(" not in html

    def test_backtick_angle_brackets(self):
        """Angle brackets inside code spans render as < > not &lt; &gt;."""
        md = Markdown("There are no `<<<<<<< ` or `>>>>>>> ` markers")
        html = md._render_custom()
        # The code element text content should be the literal characters,
        # encoded by the markdown library as &lt; (not double-encoded &amp;lt;)
        assert "&amp;lt;" not in html
        assert "<code>" in html or "<code " in html

    def test_apostrophes_not_escaped(self):
        """Test apostrophes are NOT escaped — avoids &#x27; in code blocks."""
        md = Markdown("`mark_safe(f'hello')`")
        html = md._render_custom()
        assert "&#x27;" not in html
        assert "'" in html

    def test_quotes_not_escaped(self):
        """Test double quotes are NOT escaped in rendered output."""
        md = Markdown('`config["key"]`')
        html = md._render_custom()
        assert "&quot;" not in html
        assert '"' in html

    def test_code_block(self):
        """Test fenced code blocks render correctly."""
        md = Markdown("```python\ndef foo():\n    pass\n```")
        html = md._render_custom()
        assert "<code" in html
        assert "def foo():" in html

    def test_table_rendering(self):
        """Test markdown tables render as HTML tables."""
        md = Markdown("| A | B |\n|---|---|\n| 1 | 2 |")
        html = md._render_custom()
        assert "<table>" in html
        assert "<th>" in html

    def test_reset_between_renders(self):
        """Test the markdown instance resets between calls (no state bleed)."""
        md = Markdown("# First")
        html1 = md._render_custom()
        md.text = "# Second"
        html2 = md._render_custom()
        assert "First" in html1
        assert "Second" in html2
        assert "First" not in html2

    def test_ampersand_not_escaped(self):
        """& is left as-is so pre-encoded entities are not double-encoded."""
        md = Markdown("cats & dogs")
        html = md._render_custom()
        # markdown itself converts & to &amp; inside paragraph text
        # — we just verify raw & in input doesn't become &amp;amp;
        assert "&amp;amp;" not in html

    def test_existing_entity_not_double_encoded(self):
        """Pre-encoded &lt; from agent output must not become &amp;lt;."""
        md = Markdown("There are no &lt;&lt;&lt; markers")
        html = md._render_custom()
        assert "&amp;lt;" not in html
        assert "&lt;" in html


class TestAlert:
    """Test Alert component."""

    def test_basic_alert(self):
        """Test basic alert creation."""
        alert = Alert("Something happened")
        out = alert._render_custom()
        assert "dj-alert" in out
        assert "dj-alert-info" in out  # default variant
        assert "Something happened" in out
        assert 'role="alert"' in out

    def test_alert_variants(self):
        """Test alert color variants."""
        for variant in ["info", "success", "warning", "danger"]:
            alert = Alert("test", variant=variant)
            out = alert._render_custom()
            assert f"dj-alert-{variant}" in out

    def test_alert_factory_methods(self):
        """Test factory methods set correct variant."""
        assert Alert.info("msg").variant == "info"
        assert Alert.success("msg").variant == "success"
        assert Alert.warning("msg").variant == "warning"
        assert Alert.danger("msg").variant == "danger"

    def test_alert_dismissible(self):
        """Test dismissible alert has dismiss button."""
        alert = Alert("notice", dismissible=True)
        out = alert._render_custom()
        assert "dj-alert-dismissible" in out
        assert "dj-alert-dismiss" in out
        assert "&times;" in out

    def test_alert_dismiss_action(self):
        """Test dismiss button has dj-click when action set."""
        alert = Alert("notice", dismissible=True, action="dismiss_alert")
        out = alert._render_custom()
        assert 'dj-click="dismiss_alert"' in out

    def test_alert_not_dismissible_no_button(self):
        """Test non-dismissible alert has no dismiss button."""
        alert = Alert("notice", dismissible=False)
        out = alert._render_custom()
        assert "dj-alert-dismiss" not in out

    def test_alert_with_icon(self):
        """Test alert with icon."""
        alert = Alert("notice", icon="⚠️")
        out = alert._render_custom()
        assert "dj-alert-icon" in out
        assert "⚠️" in out

    def test_alert_html_escaping(self):
        """Test message is HTML escaped."""
        alert = Alert("<script>alert('xss')</script>")
        out = alert._render_custom()
        assert "<script>" not in out
        assert "&lt;script&gt;" in out

    def test_alert_custom_class(self):
        """Test custom CSS class."""
        alert = Alert("test", custom_class="my-alert")
        out = alert._render_custom()
        assert "my-alert" in out

    def test_alert_factory_passes_kwargs(self):
        """Test factory methods pass through kwargs."""
        alert = Alert.success("Saved!", dismissible=True, custom_class="extra")
        assert alert.dismissible is True
        assert alert.custom_class == "extra"


class TestStatCard:
    """Test StatCard component."""

    def test_basic_stat_card(self):
        """Test basic stat card creation."""
        sc = StatCard(label="Revenue", value="$12,345")
        out = sc._render_custom()
        assert "dj-stat-card" in out
        assert "dj-stat-card-label" in out
        assert "Revenue" in out
        assert "$12,345" in out

    def test_stat_card_variants(self):
        """Test stat card style variants."""
        for variant in ["bordered", "elevated"]:
            sc = StatCard(label="x", value="1", variant=variant)
            out = sc._render_custom()
            assert f"dj-stat-card-{variant}" in out

    def test_stat_card_default_variant_no_extra_class(self):
        """Test default variant does not add extra class."""
        sc = StatCard(label="x", value="1")
        out = sc._render_custom()
        assert "dj-stat-card-default" not in out

    def test_stat_card_trend_up(self):
        """Test trend up indicator."""
        sc = StatCard(label="Users", value="1000", trend="up", trend_value="+12%")
        out = sc._render_custom()
        assert "dj-stat-card-trend" in out
        assert "dj-stat-card-trend-up" in out
        assert "+12%" in out

    def test_stat_card_trend_down(self):
        """Test trend down indicator."""
        sc = StatCard(label="Errors", value="5", trend="down", trend_value="-20%")
        out = sc._render_custom()
        assert "dj-stat-card-trend-down" in out
        assert "-20%" in out

    def test_stat_card_trend_flat(self):
        """Test flat trend indicator."""
        sc = StatCard(label="Uptime", value="99.9%", trend="flat")
        out = sc._render_custom()
        assert "dj-stat-card-trend-flat" in out

    def test_stat_card_no_trend(self):
        """Test stat card without trend."""
        sc = StatCard(label="x", value="1")
        out = sc._render_custom()
        assert "dj-stat-card-trend" not in out

    def test_stat_card_with_icon(self):
        """Test stat card with icon."""
        sc = StatCard(label="Revenue", value="$1", icon="💰")
        out = sc._render_custom()
        assert "dj-stat-card-icon" in out
        assert "💰" in out

    def test_stat_card_html_escaping(self):
        """Test label and value are HTML escaped."""
        sc = StatCard(label="<b>bad</b>", value="<script>")
        out = sc._render_custom()
        assert "<b>" not in out
        assert "<script>" not in out
        assert "&lt;b&gt;" in out
        assert "&lt;script&gt;" in out

    def test_stat_card_custom_class(self):
        """Test custom CSS class."""
        sc = StatCard(label="x", value="1", custom_class="my-stat")
        out = sc._render_custom()
        assert "my-stat" in out


class TestTag:
    """Test Tag component."""

    def test_basic_tag(self):
        """Test basic tag creation."""
        tag = Tag("Python")
        out = tag._render_custom()
        assert "dj-tag" in out
        assert "Python" in out

    def test_tag_variants(self):
        """Test tag color variants."""
        for variant in ["primary", "success", "info", "warning", "danger"]:
            tag = Tag("test", variant=variant)
            out = tag._render_custom()
            assert f"dj-tag-{variant}" in out

    def test_tag_default_variant_no_extra_class(self):
        """Test default variant has no extra class."""
        tag = Tag("test")
        out = tag._render_custom()
        assert "dj-tag-default" not in out

    def test_tag_sizes(self):
        """Test tag size variants."""
        sm = Tag("test", size="sm")
        md = Tag("test", size="md")
        lg = Tag("test", size="lg")
        assert "dj-tag-sm" in sm._render_custom()
        assert "dj-tag-sm" not in md._render_custom()
        assert "dj-tag-lg" in lg._render_custom()

    def test_tag_dismissible(self):
        """Test dismissible tag has dismiss button."""
        tag = Tag("filter", dismissible=True)
        out = tag._render_custom()
        assert "dj-tag-dismiss" in out
        assert "&times;" in out

    def test_tag_dismiss_action(self):
        """Test dismiss button with dj-click."""
        tag = Tag("filter", dismissible=True, action="remove_tag")
        out = tag._render_custom()
        assert 'dj-click="remove_tag"' in out

    def test_tag_not_dismissible_no_button(self):
        """Test non-dismissible tag has no dismiss button."""
        tag = Tag("test")
        out = tag._render_custom()
        assert "dj-tag-dismiss" not in out

    def test_tag_html_escaping(self):
        """Test label is HTML escaped."""
        tag = Tag("<script>alert('xss')</script>")
        out = tag._render_custom()
        assert "<script>" not in out
        assert "&lt;script&gt;" in out

    def test_tag_custom_class(self):
        """Test custom CSS class."""
        tag = Tag("test", custom_class="my-tag")
        out = tag._render_custom()
        assert "my-tag" in out


class TestToast:
    """Test Toast component."""

    def test_basic_toast(self):
        """Test basic toast creation."""
        toast = Toast("Hello")
        out = toast._render_custom()
        assert "dj-toast" in out
        assert "dj-toast-info" in out  # default type
        assert "Hello" in out
        assert 'role="status"' in out

    def test_toast_types(self):
        """Test toast type variants."""
        for t in ["info", "success", "warning", "error"]:
            toast = Toast("test", type=t)
            out = toast._render_custom()
            assert f"dj-toast-{t}" in out

    def test_toast_factory_methods(self):
        """Test factory methods set correct type."""
        assert Toast.info("msg").type == "info"
        assert Toast.success("msg").type == "success"
        assert Toast.warning("msg").type == "warning"
        assert Toast.error("msg").type == "error"

    def test_toast_duration(self):
        """Test duration data attribute."""
        toast = Toast("test", duration=5000)
        out = toast._render_custom()
        assert 'data-duration="5000"' in out

    def test_toast_no_duration(self):
        """Test zero duration means no data attribute."""
        toast = Toast("test", duration=0)
        out = toast._render_custom()
        assert "data-duration" not in out

    def test_toast_dismissible(self):
        """Test dismissible toast has dismiss button."""
        toast = Toast("test", dismissible=True)
        out = toast._render_custom()
        assert "dj-toast-dismiss" in out
        assert "&times;" in out

    def test_toast_dismiss_action(self):
        """Test dismiss button with dj-click."""
        toast = Toast("test", dismissible=True, action="close_toast")
        out = toast._render_custom()
        assert 'dj-click="close_toast"' in out

    def test_toast_not_dismissible(self):
        """Test non-dismissible toast has no dismiss button."""
        toast = Toast("test", dismissible=False)
        out = toast._render_custom()
        assert "dj-toast-dismiss" not in out

    def test_toast_html_escaping(self):
        """Test message is HTML escaped."""
        toast = Toast("<script>alert('xss')</script>")
        out = toast._render_custom()
        assert "<script>" not in out
        assert "&lt;script&gt;" in out

    def test_toast_custom_class(self):
        """Test custom CSS class."""
        toast = Toast("test", custom_class="my-toast")
        out = toast._render_custom()
        assert "my-toast" in out

    def test_toast_factory_passes_kwargs(self):
        """Test factory methods pass through kwargs."""
        toast = Toast.error("Fail", duration=10000, dismissible=False)
        assert toast.duration == 10000
        assert toast.dismissible is False


class TestProgress:
    """Test Progress component."""

    def test_basic_progress(self):
        """Test basic progress bar creation."""
        p = Progress(value=50)
        out = p._render_custom()
        assert "dj-progress" in out
        assert "dj-progress-track" in out
        assert "dj-progress-bar" in out
        assert 'role="progressbar"' in out

    def test_progress_percentage(self):
        """Test percentage calculation."""
        assert Progress(value=50, max=100).percentage == 50.0
        assert Progress(value=3, max=10).percentage == 30.0
        assert Progress(value=0, max=100).percentage == 0.0
        assert Progress(value=100, max=100).percentage == 100.0

    def test_progress_percentage_clamped(self):
        """Test percentage is clamped to 0-100."""
        assert Progress(value=150, max=100).percentage == 100.0
        assert Progress(value=-10, max=100).percentage == 0.0

    def test_progress_zero_max(self):
        """Test zero max returns 0 percentage."""
        assert Progress(value=50, max=0).percentage == 0.0

    def test_progress_style_width(self):
        """Test the bar width style matches percentage."""
        p = Progress(value=75, max=100)
        out = p._render_custom()
        assert "width:75.0%" in out

    def test_progress_variants(self):
        """Test progress color variants."""
        for variant in ["success", "info", "warning", "danger"]:
            p = Progress(value=50, variant=variant)
            out = p._render_custom()
            assert f"dj-progress-{variant}" in out

    def test_progress_default_variant_no_extra_class(self):
        """Test default variant has no extra class."""
        p = Progress(value=50)
        out = p._render_custom()
        assert "dj-progress-default" not in out

    def test_progress_sizes(self):
        """Test progress size variants."""
        sm = Progress(value=50, size="sm")
        md = Progress(value=50, size="md")
        lg = Progress(value=50, size="lg")
        assert "dj-progress-sm" in sm._render_custom()
        assert "dj-progress-sm" not in md._render_custom()
        assert "dj-progress-lg" in lg._render_custom()

    def test_progress_with_label(self):
        """Test progress bar with label."""
        p = Progress(value=50, label="Uploading...")
        out = p._render_custom()
        assert "dj-progress-label" in out
        assert "Uploading..." in out

    def test_progress_show_value(self):
        """Test progress bar with percentage display."""
        p = Progress(value=75, show_value=True)
        out = p._render_custom()
        assert "dj-progress-value" in out
        assert "75%" in out

    def test_progress_no_value_by_default(self):
        """Test percentage not shown by default."""
        p = Progress(value=50)
        out = p._render_custom()
        assert "dj-progress-value" not in out

    def test_progress_aria_attributes(self):
        """Test ARIA attributes on the bar."""
        p = Progress(value=30, max=200)
        out = p._render_custom()
        assert 'aria-valuenow="30"' in out
        assert 'aria-valuemin="0"' in out
        assert 'aria-valuemax="200"' in out

    def test_progress_html_escaping(self):
        """Test label is HTML escaped."""
        p = Progress(value=50, label="<script>alert('xss')</script>")
        out = p._render_custom()
        assert "<script>" not in out
        assert "&lt;script&gt;" in out

    def test_progress_custom_class(self):
        """Test custom CSS class."""
        p = Progress(value=50, custom_class="my-progress")
        out = p._render_custom()
        assert "my-progress" in out


class TestSpinner:
    """Test Spinner component."""

    def test_basic_spinner(self):
        """Test basic spinner creation."""
        s = Spinner()
        out = s._render_custom()
        assert "dj-spinner" in out
        assert 'role="status"' in out

    def test_spinner_sizes(self):
        """Test spinner size variants."""
        sm = Spinner(size="sm")
        md = Spinner(size="md")
        lg = Spinner(size="lg")
        assert "dj-spinner-sm" in sm._render_custom()
        assert "dj-spinner-sm" not in md._render_custom()
        assert "dj-spinner-lg" in lg._render_custom()

    def test_spinner_variants(self):
        """Test spinner color variants."""
        for variant in ["primary", "muted"]:
            s = Spinner(variant=variant)
            out = s._render_custom()
            assert f"dj-spinner-{variant}" in out

    def test_spinner_default_variant_no_extra_class(self):
        """Test default variant has no extra class."""
        s = Spinner()
        out = s._render_custom()
        assert "dj-spinner-default" not in out

    def test_spinner_label(self):
        """Test spinner with screen-reader label."""
        s = Spinner(label="Loading data...")
        out = s._render_custom()
        assert "dj-sr-only" in out
        assert "Loading data..." in out

    def test_spinner_default_label(self):
        """Test spinner has default Loading... label."""
        s = Spinner()
        out = s._render_custom()
        assert "Loading..." in out

    def test_spinner_no_label(self):
        """Test spinner with no label."""
        s = Spinner(label=None)
        out = s._render_custom()
        assert "dj-sr-only" not in out

    def test_spinner_custom_class(self):
        """Test custom CSS class."""
        s = Spinner(custom_class="my-spinner")
        out = s._render_custom()
        assert "my-spinner" in out

    def test_spinner_aria_label(self):
        """Test aria-label attribute."""
        s = Spinner(label="Saving...")
        out = s._render_custom()
        assert 'aria-label="Saving..."' in out


class TestSwitch:
    """Test Switch component."""

    def test_basic_switch(self):
        """Test basic switch creation."""
        sw = Switch(name="toggle")
        out = sw._render_custom()
        assert "dj-switch" in out
        assert 'type="checkbox"' in out
        assert 'name="toggle"' in out

    def test_switch_checked(self):
        """Test checked switch."""
        sw = Switch(name="opt", checked=True)
        out = sw._render_custom()
        assert "checked" in out
        assert "dj-switch-checked" in out

    def test_switch_unchecked(self):
        """Test unchecked switch."""
        sw = Switch(name="opt", checked=False)
        out = sw._render_custom()
        assert "dj-switch-checked" not in out

    def test_switch_with_label(self):
        """Test switch with label text."""
        sw = Switch(name="opt", label="Enable notifications")
        out = sw._render_custom()
        assert "dj-switch-label" in out
        assert "Enable notifications" in out

    def test_switch_no_label(self):
        """Test switch without label."""
        sw = Switch(name="opt")
        out = sw._render_custom()
        assert "dj-switch-label" not in out

    def test_switch_disabled(self):
        """Test disabled switch."""
        sw = Switch(name="opt", disabled=True, action="toggle")
        out = sw._render_custom()
        assert "disabled" in out
        assert "dj-switch-disabled" in out
        assert "dj-change" not in out  # no event when disabled

    def test_switch_action(self):
        """Test switch with djust event."""
        sw = Switch(name="opt", action="toggle_setting")
        out = sw._render_custom()
        assert 'dj-change="toggle_setting"' in out

    def test_switch_toggle(self):
        """Test toggle method flips checked state."""
        sw = Switch(name="opt", checked=False)
        assert sw.checked is False
        sw.toggle()
        assert sw.checked is True
        sw.toggle()
        assert sw.checked is False

    def test_switch_slider(self):
        """Test switch has slider span."""
        sw = Switch(name="opt")
        out = sw._render_custom()
        assert "dj-switch-slider" in out

    def test_switch_html_escaping(self):
        """Test label and name are HTML escaped."""
        sw = Switch(name="<bad>", label="<script>xss</script>")
        out = sw._render_custom()
        assert "<script>" not in out
        assert "&lt;script&gt;" in out
        assert "&lt;bad&gt;" in out

    def test_switch_custom_class(self):
        """Test custom CSS class."""
        sw = Switch(name="opt", custom_class="my-switch")
        out = sw._render_custom()
        assert "my-switch" in out

    def test_switch_wraps_in_label(self):
        """Test switch renders as a label element."""
        sw = Switch(name="opt")
        out = sw._render_custom()
        assert out.startswith("<label")
        assert out.endswith("</label>")
