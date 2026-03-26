"""Tests for Icon System (#178) and Theme Toggle (#138)."""
from django.template import Template, Context
from django.test import override_settings
import pytest

from djust_components.icons import (
    render_icon,
    get_icon_names,
    get_icon_sets,
    clear_icon_sets_cache,
    HEROICONS_OUTLINE,
    ICON_SIZES,
)


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ═══════════════════════════════════════════════════════════════════════════
# 1. Icon System — render_icon() Python helper
# ═══════════════════════════════════════════════════════════════════════════

class TestRenderIcon:
    def test_basic_icon_renders_svg(self):
        html = render_icon("check")
        assert "<svg" in html
        assert "</svg>" in html
        assert 'class="dj-icon dj-icon--md"' in html
        assert 'width="20"' in html
        assert 'height="20"' in html

    def test_unknown_icon_returns_empty(self):
        assert render_icon("nonexistent-icon-xyz") == ""

    def test_size_xs(self):
        html = render_icon("check", size="xs")
        assert 'width="12"' in html
        assert 'dj-icon--xs' in html

    def test_size_sm(self):
        html = render_icon("check", size="sm")
        assert 'width="16"' in html
        assert 'dj-icon--sm' in html

    def test_size_md(self):
        html = render_icon("check", size="md")
        assert 'width="20"' in html
        assert 'dj-icon--md' in html

    def test_size_lg(self):
        html = render_icon("check", size="lg")
        assert 'width="24"' in html
        assert 'dj-icon--lg' in html

    def test_custom_pixel_size(self):
        html = render_icon("check", size=32)
        assert 'width="32"' in html
        assert 'height="32"' in html
        # No size-specific class for custom sizes
        assert "dj-icon--" not in html.replace("dj-icon--", "", 0)

    def test_custom_class(self):
        html = render_icon("check", custom_class="text-red my-icon")
        assert "text-red my-icon" in html

    def test_extra_attrs(self):
        html = render_icon("check", aria_label="Done", data_tooltip="Check")
        assert 'aria-label="Done"' in html
        assert 'data-tooltip="Check"' in html

    def test_viewbox_24(self):
        html = render_icon("check")
        assert 'viewBox="0 0 24 24"' in html

    def test_stroke_based(self):
        html = render_icon("check")
        assert 'fill="none"' in html
        assert 'stroke="currentColor"' in html

    def test_aria_hidden(self):
        html = render_icon("check")
        assert 'aria-hidden="true"' in html

    def test_all_bundled_icons_render(self):
        """Every icon in the default set should produce valid SVG output."""
        for name in HEROICONS_OUTLINE:
            html = render_icon(name)
            assert "<svg" in html, f"Icon '{name}' failed to render"
            assert "</svg>" in html, f"Icon '{name}' missing closing tag"

    def test_mark_safe(self):
        from django.utils.safestring import SafeData
        html = render_icon("check")
        assert isinstance(html, SafeData)


class TestIconSets:
    def setup_method(self):
        clear_icon_sets_cache()

    def teardown_method(self):
        clear_icon_sets_cache()

    def test_default_set_is_heroicons(self):
        assert "heroicons" in get_icon_sets()

    def test_get_icon_names_returns_sorted(self):
        names = get_icon_names()
        assert names == sorted(names)
        assert "check" in names
        assert "sun" in names
        assert "moon" in names

    @override_settings(DJUST_COMPONENTS_ICON_SETS={
        "custom": {"logo": '<circle cx="12" cy="12" r="10"/>'},
    })
    def test_custom_icon_set_from_settings(self):
        clear_icon_sets_cache()
        html = render_icon("logo", icon_set="custom")
        assert '<circle cx="12" cy="12" r="10"/>' in html

    @override_settings(DJUST_COMPONENTS_ICON_SETS={
        "custom": {"logo": '<circle cx="12" cy="12" r="10"/>'},
    })
    def test_custom_set_appears_in_get_icon_sets(self):
        clear_icon_sets_cache()
        sets = get_icon_sets()
        assert "custom" in sets
        assert "heroicons" in sets

    def test_unknown_set_returns_empty(self):
        html = render_icon("check", icon_set="nonexistent")
        assert html == ""


# ═══════════════════════════════════════════════════════════════════════════
# 2. Icon System — {% icon %} template tag
# ═══════════════════════════════════════════════════════════════════════════

class TestIconTemplateTag:
    def test_basic_icon_tag(self):
        html = render('{% icon name="check" %}')
        assert "<svg" in html
        assert "dj-icon" in html

    def test_icon_with_size(self):
        html = render('{% icon name="check" size="lg" %}')
        assert 'width="24"' in html
        assert "dj-icon--lg" in html

    def test_icon_with_variable_name(self):
        html = render('{% icon name=icon_name %}', {"icon_name": "x-mark"})
        assert "<svg" in html

    def test_icon_empty_name(self):
        html = render('{% icon name="" %}')
        # Should produce empty string for unknown icon
        assert "<svg" not in html

    def test_icon_with_custom_class(self):
        html = render('{% icon name="check" custom_class="my-cls" %}')
        assert "my-cls" in html

    def test_icon_all_sizes(self):
        for size, px in ICON_SIZES.items():
            html = render(f'{{% icon name="check" size="{size}" %}}')
            assert f'width="{px}"' in html


# ═══════════════════════════════════════════════════════════════════════════
# 3. Icon System — Rust handler
# ═══════════════════════════════════════════════════════════════════════════

class TestIconRustHandler:
    def test_handler_renders_svg(self):
        from djust_components.rust_handlers import IconHandler
        handler = IconHandler()
        html = handler.render(["name='check'", "size='md'"], {})
        assert "<svg" in html
        assert "dj-icon" in html

    def test_handler_custom_size(self):
        from djust_components.rust_handlers import IconHandler
        handler = IconHandler()
        html = handler.render(["name='check'", "size='lg'"], {})
        assert 'width="24"' in html

    def test_handler_empty_name(self):
        from djust_components.rust_handlers import IconHandler
        handler = IconHandler()
        html = handler.render(["name=''"], {})
        assert html == ""

    def test_handler_with_custom_class(self):
        from djust_components.rust_handlers import IconHandler
        handler = IconHandler()
        html = handler.render(["name='check'", "custom_class='my-cls'"], {})
        assert "my-cls" in html


# ═══════════════════════════════════════════════════════════════════════════
# 4. Theme Toggle — {% theme_toggle %} template tag
# ═══════════════════════════════════════════════════════════════════════════

class TestThemeToggle:
    def test_default_renders_three_buttons(self):
        html = render("{% theme_toggle %}")
        assert "dj-theme-toggle" in html
        assert 'data-theme="light"' in html
        assert 'data-theme="dark"' in html
        assert 'data-theme="system"' in html

    def test_default_current_is_system(self):
        html = render("{% theme_toggle %}")
        assert 'data-current="system"' in html

    def test_custom_current(self):
        html = render('{% theme_toggle current="dark" %}')
        assert 'data-current="dark"' in html

    def test_variable_current(self):
        html = render("{% theme_toggle current=theme %}", {"theme": "light"})
        assert 'data-current="light"' in html

    def test_event_adds_dj_click(self):
        html = render('{% theme_toggle event="set_theme" %}')
        assert 'dj-click="set_theme"' in html

    def test_no_event_no_dj_click(self):
        html = render("{% theme_toggle %}")
        assert "dj-click" not in html

    def test_custom_class(self):
        html = render('{% theme_toggle custom_class="my-toggle" %}')
        assert "my-toggle" in html
        assert "dj-theme-toggle" in html

    def test_aria_attributes(self):
        html = render("{% theme_toggle %}")
        assert 'role="radiogroup"' in html
        assert 'aria-label="Color theme"' in html
        assert 'aria-label="Light theme"' in html
        assert 'aria-label="Dark theme"' in html
        assert 'aria-label="System theme"' in html

    def test_contains_sun_icon(self):
        html = render("{% theme_toggle %}")
        # The sun icon should be an SVG inside the light button
        assert "<svg" in html

    def test_contains_moon_icon(self):
        html = render("{% theme_toggle %}")
        # Should have moon path from heroicons
        assert "moon" in html.lower() or "M21.752" in html

    def test_contains_monitor_icon(self):
        html = render("{% theme_toggle %}")
        # Should have computer-desktop path
        assert "M9 17.25" in html

    def test_unique_id(self):
        html1 = render("{% theme_toggle %}")
        html2 = render("{% theme_toggle %}")
        # Extract IDs — each should be unique
        import re
        ids1 = re.findall(r'id="(dj-theme-toggle-[a-f0-9]+)"', html1)
        ids2 = re.findall(r'id="(dj-theme-toggle-[a-f0-9]+)"', html2)
        assert len(ids1) == 1
        assert len(ids2) == 1
        assert ids1[0] != ids2[0]


# ═══════════════════════════════════════════════════════════════════════════
# 5. Theme Toggle — Rust handler
# ═══════════════════════════════════════════════════════════════════════════

class TestThemeToggleRustHandler:
    def test_handler_renders_toggle(self):
        from djust_components.rust_handlers import ThemeToggleHandler
        handler = ThemeToggleHandler()
        html = handler.render([], {})
        assert "dj-theme-toggle" in html
        assert 'data-theme="light"' in html
        assert 'data-theme="dark"' in html
        assert 'data-theme="system"' in html

    def test_handler_with_event(self):
        from djust_components.rust_handlers import ThemeToggleHandler
        handler = ThemeToggleHandler()
        html = handler.render(["event='set_theme'"], {})
        assert 'dj-click="set_theme"' in html

    def test_handler_with_current(self):
        from djust_components.rust_handlers import ThemeToggleHandler
        handler = ThemeToggleHandler()
        html = handler.render(["current='dark'"], {})
        assert 'data-current="dark"' in html


# ═══════════════════════════════════════════════════════════════════════════
# 6. XSS Escaping
# ═══════════════════════════════════════════════════════════════════════════

class TestXSSEscaping:
    """Verify that user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # Icon
    def test_icon_custom_class_xss(self):
        html = render_icon("check", custom_class=XSS)
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_icon_extra_attr_xss(self):
        html = render_icon("check", aria_label=XSS_ATTR)
        self._assert_attr_escaped(html)

    def test_icon_name_xss_returns_empty(self):
        """XSS in icon name should just not find the icon → empty string."""
        html = render_icon(XSS)
        assert html == ""

    def test_icon_set_xss_returns_empty(self):
        """XSS in icon set name should just not find the set → empty string."""
        html = render_icon("check", icon_set=XSS)
        assert html == ""

    # Icon template tag
    def test_icon_tag_custom_class_xss(self):
        html = render(
            '{% icon name="check" custom_class=cls %}',
            {"cls": XSS},
        )
        assert "<script>alert" not in html

    # Theme Toggle
    def test_theme_toggle_event_xss(self):
        html = render(
            '{% theme_toggle event=bad_event %}',
            {"bad_event": XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_theme_toggle_current_xss(self):
        html = render(
            '{% theme_toggle current=bad_current %}',
            {"bad_current": XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_theme_toggle_custom_class_xss(self):
        html = render(
            '{% theme_toggle custom_class=bad_cls %}',
            {"bad_cls": XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    # Theme Toggle Rust handler
    def test_theme_toggle_handler_event_xss(self):
        from djust_components.rust_handlers import ThemeToggleHandler
        handler = ThemeToggleHandler()
        html = handler.render([f"event='{XSS_ATTR}'"], {})
        assert '" onmouseover="' not in html

    def test_theme_toggle_handler_current_xss(self):
        from djust_components.rust_handlers import ThemeToggleHandler
        handler = ThemeToggleHandler()
        html = handler.render([f"current='{XSS}'"], {})
        assert "<script>" not in html


# Local aliases for XSS test class methods
XSS = '<script>alert(1)</script>'
XSS_ATTR = '" onmouseover="alert(1)" x="'
