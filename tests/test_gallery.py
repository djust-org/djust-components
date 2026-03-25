"""Tests for the component gallery — discovery, rendering, views, and management command."""
import types
import sys

# Stub djust before any djust_components imports
_stub = types.ModuleType("djust")


class _LV:
    pass


class _Comp:
    """Stub Component base class."""

    def __init__(self, *args, **kwargs):
        pass

    def _render_custom(self):
        return "<div>stub</div>"

    def __str__(self):
        return self._render_custom()

    def __html__(self):
        return self._render_custom()


_stub.LiveView = _LV
_stub.Component = _Comp
sys.modules.setdefault("djust", _stub)

# Stub djust.decorators
_dec_stub = types.ModuleType("djust.decorators")


def _event_handler(fn):
    return fn


_dec_stub.event_handler = _event_handler
sys.modules.setdefault("djust.decorators", _dec_stub)


import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.staticfiles",
            "djust_components",
        ],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {"context_processors": []},
            }
        ],
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
        STATIC_URL="/static/",
    )
    django.setup()


import pytest
from django.template import Template, Context
from django.test import RequestFactory


# ─── Discovery Tests ───


class TestDiscovery:
    """Tests for the gallery's auto-discovery of template tags and component classes."""

    def test_discover_template_tags(self):
        """All registered tags are discovered by the registry."""
        from djust_components.gallery.registry import discover_template_tags

        tags = discover_template_tags()
        # Should find key tags — these are certainly registered
        assert "modal" in tags
        assert "tabs" in tags
        assert "accordion" in tags
        assert "dropdown" in tags
        assert "tooltip" in tags
        assert "card" in tags
        assert "alert" in tags

    def test_discover_component_classes(self):
        """All component classes are discovered."""
        from djust_components.gallery.registry import discover_component_classes

        classes = discover_component_classes()
        expected = {"Alert", "ApprovalGate", "AvatarGroup", "Badge", "Button", "Card", "ChatBubble", "CodeSnippet", "ConnectionStatus", "ConversationThread", "CopyableText", "CurrencyInput", "DataGrid", "DependentSelect", "FeedbackWidget", "FieldError", "FormErrors", "HoverCard", "LiveCounter", "Markdown", "MentionsInput", "ModelSelector", "MultimodalInput", "NotificationBadge", "NotificationPopover", "PresenceAvatars", "Progress", "ProgressCircle", "RelativeTime", "ResponsiveImage", "RichSelect", "ScrollToTop", "SegmentedProgress", "ServerEventToastMixin", "SourceCitation", "Spinner", "StatCard", "StatusDot", "StatusIndicator", "StreamingText", "Switch", "Tag", "ThinkingIndicator", "Toast", "TokenCounter"}
        assert set(classes.keys()) == expected

    def test_all_examples_have_matching_tag_or_class(self):
        """Every key in EXAMPLES matches a registered tag or component class."""
        from djust_components.gallery.registry import (
            discover_template_tags,
            discover_component_classes,
        )
        from djust_components.gallery.examples import EXAMPLES, CLASS_EXAMPLES

        tags = discover_template_tags()
        classes = discover_component_classes()

        for key in EXAMPLES:
            assert key in tags, f"Example '{key}' has no matching template tag"

        for key in CLASS_EXAMPLES:
            assert key in classes, f"Class example '{key}' has no matching component class"

    def test_no_orphan_tags(self):
        """Warn (not fail) if a registered tag has no example.

        We collect orphans and log them; new tags may lag behind gallery examples.
        """
        from djust_components.gallery.registry import discover_template_tags
        from djust_components.gallery.examples import EXAMPLES

        tags = discover_template_tags()
        # Some child tags (tab, accordion_item, timeline_item) are nested only
        child_tags = {"tab", "accordion_item", "timeline_item", "context_menu_item",
                      "palette_item"}
        orphans = set(tags.keys()) - set(EXAMPLES.keys()) - child_tags
        if orphans:
            import warnings
            warnings.warn(
                f"Tags without gallery examples: {orphans}",
                stacklevel=1,
            )
        # Not an assertion failure — just informational


# ─── Rendering Tests ───


class TestRendering:
    """Tests that all example templates render without errors."""

    def test_render_all_template_tag_examples(self):
        """Each example template string renders without raising."""
        from djust_components.gallery.examples import EXAMPLES

        for tag_name, info in EXAMPLES.items():
            for variant in info["variants"]:
                tpl_str = variant["template"]
                try:
                    t = Template("{% load djust_components %}" + tpl_str)
                    html = t.render(Context(variant.get("context", {})))
                    # Should produce non-empty output (or empty string for conditional components)
                    assert isinstance(html, str), f"{tag_name}/{variant['name']} returned non-string"
                except Exception as exc:
                    pytest.fail(
                        f"Failed to render {tag_name}/{variant['name']}: {exc}\n"
                        f"Template: {tpl_str}"
                    )

    def test_render_all_class_examples(self):
        """Each class example callable produces non-empty HTML."""
        from djust_components.gallery.examples import CLASS_EXAMPLES

        for class_name, info in CLASS_EXAMPLES.items():
            for variant in info["variants"]:
                try:
                    html = variant["render"]()
                    assert html and len(html) > 0, (
                        f"{class_name}/{variant['name']} produced empty output"
                    )
                except Exception as exc:
                    pytest.fail(f"Failed to render {class_name}/{variant['name']}: {exc}")

    def test_rendered_html_contains_expected_classes(self):
        """Spot-check that rendered HTML contains expected CSS classes."""
        from djust_components.gallery.examples import EXAMPLES

        # Modal should contain dj-modal when open
        modal_info = EXAMPLES.get("modal")
        if modal_info:
            for v in modal_info["variants"]:
                if v.get("context", {}).get("is_open", False) or "open=True" in v["template"]:
                    t = Template("{% load djust_components %}" + v["template"])
                    html = t.render(Context(v.get("context", {})))
                    if html.strip():
                        assert "dj-modal" in html


# ─── Management Command Tests ───


class TestManagementCommand:
    """Tests for the component_gallery management command."""

    def test_command_exists(self):
        """The management command is discoverable."""
        from django.core.management import get_commands

        commands = get_commands()
        assert "component_gallery" in commands

    def test_command_dry_run(self):
        """--dry-run prints discovered components and exits."""
        from django.core.management import call_command
        from io import StringIO

        out = StringIO()
        call_command("component_gallery", "--dry-run", stdout=out)
        output = out.getvalue()
        # Should mention discovered components
        assert "modal" in output.lower() or "Modal" in output
        assert "badge" in output.lower() or "Badge" in output


# ─── View Tests ───


class TestGalleryView:
    """Tests for the gallery view."""

    def test_gallery_view_200(self):
        """GET to gallery view returns 200."""
        from djust_components.gallery.views import gallery_view

        factory = RequestFactory()
        request = factory.get("/gallery/")
        response = gallery_view(request)
        assert response.status_code == 200

    def test_gallery_view_contains_all_categories(self):
        """Response contains category headings."""
        from djust_components.gallery.views import gallery_view

        factory = RequestFactory()
        request = factory.get("/gallery/")
        response = gallery_view(request)
        content = response.content.decode()

        # Should contain at least some of the main categories
        for category in ["Layout", "Form", "Overlay", "Feedback"]:
            assert category in content, f"Category '{category}' not found in gallery"

    def test_dark_mode_toggle_present(self):
        """Dark mode toggle button is present in the HTML."""
        from djust_components.gallery.views import gallery_view

        factory = RequestFactory()
        request = factory.get("/gallery/")
        response = gallery_view(request)
        content = response.content.decode()
        assert "theme-toggle" in content or "dark-mode" in content

    def test_gallery_view_contains_component_cards(self):
        """Gallery renders cards for components."""
        from djust_components.gallery.views import gallery_view

        factory = RequestFactory()
        request = factory.get("/gallery/")
        response = gallery_view(request)
        content = response.content.decode()
        # Should contain rendered component examples
        assert "component-card" in content


# ─── Edge Case Tests ───


class TestEdgeCases:
    """Edge cases: empty data, missing values, boundary conditions."""

    def test_empty_examples_dict(self):
        """Registry handles empty examples gracefully."""
        from djust_components.gallery.registry import get_gallery_data

        data = get_gallery_data()
        # Should always return a dict with 'categories' key
        assert "categories" in data
        assert isinstance(data["categories"], dict)

    def test_example_with_none_context(self):
        """Templates render fine with no context."""
        t = Template("{% load djust_components %}{% dj_button label=\"Test\" %}")
        html = t.render(Context({}))
        assert "Test" in html

    def test_category_grouping(self):
        """Components are grouped into categories."""
        from djust_components.gallery.registry import get_gallery_data

        data = get_gallery_data()
        categories = data["categories"]
        # Should have at least 3 categories
        assert len(categories) >= 3
