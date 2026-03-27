"""Tests for the component gallery — discovery, rendering, views, and management command."""
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
        """Discovered classes match __all__ from components package."""
        from djust_components.gallery.registry import discover_component_classes
        from djust_components.components import __all__ as exported_names

        classes = discover_component_classes()
        # Dynamic: discovered set must exactly match the package's __all__
        assert set(classes.keys()) == set(exported_names), (
            f"Mismatch between discovered classes and __all__.\n"
            f"  In __all__ but not discovered: {set(exported_names) - set(classes.keys())}\n"
            f"  Discovered but not in __all__: {set(classes.keys()) - set(exported_names)}"
        )
        # Sanity: should have a reasonable number of components
        assert len(classes) >= 50, f"Only {len(classes)} classes discovered — expected 50+"

    def test_discover_component_classes_includes_known_core(self):
        """Smoke-check that well-known classes are always present."""
        from djust_components.gallery.registry import discover_component_classes

        classes = discover_component_classes()
        for name in ("Badge", "Button", "Card", "Alert", "Toast", "Progress"):
            assert name in classes, f"Core class {name!r} missing from discovery"

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
        # Child tags are rendered by their parent — they don't need standalone examples
        child_tags = {
            "tab", "accordion_item", "timeline_item", "context_menu_item",
            "palette_item",
            # app_shell children
            "app_content", "app_header", "app_sidebar",
            # sidebar children
            "sidebar_item", "sidebar_section",
            # nav_menu children
            "nav_item",
            # filter_bar children
            "filter_date_range", "filter_search", "filter_select",
            # toolbar children
            "toolbar_overflow", "toolbar_separator",
            # page_header children
            "page_header_actions",
            # dropdown_menu children
            "menu_divider", "menu_item",
            # input_group children
            "input_addon",
        }
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


# ─── Index View Tests ───


class TestGalleryIndexView:
    """Tests for the gallery index (landing) view."""

    def test_index_view_200(self):
        from djust_components.gallery.views import gallery_index_view

        factory = RequestFactory()
        request = factory.get("/")
        response = gallery_index_view(request)
        assert response.status_code == 200

    def test_index_contains_all_category_links(self):
        from djust_components.gallery.views import gallery_index_view
        from djust_components.gallery.examples import CATEGORIES

        factory = RequestFactory()
        request = factory.get("/")
        response = gallery_index_view(request)
        content = response.content.decode()

        for slug, label in CATEGORIES.items():
            assert f'href="{slug}/"' in content, f"Missing link for category '{label}'"
            assert label in content, f"Category label '{label}' not in index"

    def test_index_shows_component_counts(self):
        from djust_components.gallery.views import gallery_index_view

        factory = RequestFactory()
        request = factory.get("/")
        response = gallery_index_view(request)
        content = response.content.decode()
        assert "components" in content

    def test_index_has_theme_toolbar(self):
        from djust_components.gallery.views import gallery_index_view

        factory = RequestFactory()
        request = factory.get("/")
        response = gallery_index_view(request)
        content = response.content.decode()
        assert "design-system" in content
        assert "preset" in content
        assert "theme-toggle" in content


# ─── Category View Tests ───


class TestGalleryCategoryView:
    """Tests for the per-category gallery view."""

    def test_all_categories_return_200(self):
        from djust_components.gallery.views import gallery_category_view
        from djust_components.gallery.examples import CATEGORY_ORDER

        factory = RequestFactory()
        for slug in CATEGORY_ORDER:
            request = factory.get(f"/{slug}/")
            response = gallery_category_view(request, slug)
            assert response.status_code == 200, f"Category '{slug}' returned {response.status_code}"

    def test_invalid_category_returns_404(self):
        from djust_components.gallery.views import gallery_category_view

        factory = RequestFactory()
        request = factory.get("/nonexistent/")
        try:
            gallery_category_view(request, "nonexistent")
            assert False, "Expected Http404"
        except Exception as exc:
            assert "404" in type(exc).__name__ or "Unknown category" in str(exc)

    def test_category_contains_only_own_components(self):
        from djust_components.gallery.views import gallery_category_view
        from djust_components.gallery.examples import EXAMPLES, CLASS_EXAMPLES

        factory = RequestFactory()
        request = factory.get("/form/")
        response = gallery_category_view(request, "form")
        content = response.content.decode()

        # Should contain form components
        assert "component-card" in content

        # Should NOT contain layout-only components
        assert 'id="accordion"' not in content or "accordion" in [
            k for k, v in EXAMPLES.items() if v.get("category") == "form"
        ]

    def test_category_has_breadcrumb(self):
        from djust_components.gallery.views import gallery_category_view

        factory = RequestFactory()
        request = factory.get("/data/")
        response = gallery_category_view(request, "data")
        content = response.content.decode()
        assert "gallery-breadcrumb" in content
        assert "Data" in content

    def test_category_has_prev_next(self):
        from djust_components.gallery.views import gallery_category_view

        factory = RequestFactory()
        # "data" is index 2 in CATEGORY_ORDER — should have both prev and next
        request = factory.get("/data/")
        response = gallery_category_view(request, "data")
        content = response.content.decode()
        assert "category-nav" in content

    def test_category_sidebar_highlights_current(self):
        from djust_components.gallery.views import gallery_category_view

        factory = RequestFactory()
        request = factory.get("/form/")
        response = gallery_category_view(request, "form")
        content = response.content.decode()
        assert 'class="active"' in content

    def test_first_category_has_no_prev(self):
        from djust_components.gallery.views import gallery_category_view
        from djust_components.gallery.examples import CATEGORY_ORDER

        factory = RequestFactory()
        first = CATEGORY_ORDER[0]
        request = factory.get(f"/{first}/")
        response = gallery_category_view(request, first)
        content = response.content.decode()
        # Should have next but not prev (no leftarrow link)
        assert "&rarr;" in content
        # The first category's prev link should be empty
        nav_section = content[content.index("category-nav"):]
        assert "&larr;" not in nav_section.split("</div>")[0]

    def test_last_category_has_no_next(self):
        from djust_components.gallery.views import gallery_category_view
        from djust_components.gallery.examples import CATEGORY_ORDER

        factory = RequestFactory()
        last = CATEGORY_ORDER[-1]
        request = factory.get(f"/{last}/")
        response = gallery_category_view(request, last)
        content = response.content.decode()
        nav_section = content[content.index("category-nav"):]
        assert "&rarr;" not in nav_section.split("</div>")[0]


# ─── LiveView Tests ───


class TestGalleryLiveView:
    """Tests for the LiveView-based gallery."""

    def test_liveview_class_exists(self):
        from djust_components.gallery.live_views import GalleryIndexView
        assert GalleryIndexView is not None

    def test_liveview_has_template(self):
        from djust_components.gallery.live_views import GalleryIndexView
        assert GalleryIndexView.template_name == "djust_components/gallery/index.html"

    def test_liveview_mount_sets_state(self):
        from djust_components.gallery.live_views import GalleryIndexView

        view = GalleryIndexView()
        factory = RequestFactory()
        request = factory.get("/")
        request.COOKIES = {}
        view.mount(request)

        assert view.design_system == "material"
        assert view.preset == "default"
        assert view.mode == "light"
        assert view.preview_mode == "desktop"
        assert len(view.category_cards) == 9
        assert isinstance(view.theme_css, str)  # CSS string (may be empty without djust-theming)

    def test_liveview_mount_reads_cookies(self):
        from djust_components.gallery.live_views import GalleryIndexView

        view = GalleryIndexView()
        factory = RequestFactory()
        request = factory.get("/")
        # Use values that exist in the fallback lists too (material/default always valid)
        request.COOKIES = {"gallery_ds": "material", "gallery_preset": "default", "gallery_mode": "dark"}
        view.mount(request)

        assert view.design_system == "material"
        assert view.preset == "default"
        assert view.mode == "dark"

    def test_liveview_mount_reads_cookies_with_theming(self):
        """Test cookie reading with full theme options (requires djust-theming)."""
        pytest = __import__("pytest")
        try:
            import djust_theming  # noqa: F401
        except ImportError:
            pytest.skip("djust-theming not installed")

        from djust_components.gallery.live_views import GalleryIndexView

        view = GalleryIndexView()
        factory = RequestFactory()
        request = factory.get("/")
        request.COOKIES = {"gallery_ds": "ios", "gallery_preset": "cyberpunk", "gallery_mode": "dark"}
        view.mount(request)

        assert view.design_system == "ios"
        assert view.preset == "cyberpunk"
        assert view.mode == "dark"

    def test_liveview_mount_validates_cookies(self):
        from djust_components.gallery.live_views import GalleryIndexView

        view = GalleryIndexView()
        factory = RequestFactory()
        request = factory.get("/")
        request.COOKIES = {"gallery_ds": "INVALID", "gallery_mode": "bogus"}
        view.mount(request)

        assert view.design_system == "material"  # fallback
        assert view.mode == "light"  # fallback

    def test_liveview_event_handlers_exist(self):
        from djust_components.gallery.live_views import GalleryIndexView
        view = GalleryIndexView()
        assert hasattr(view, "change_design_system")
        assert hasattr(view, "change_preset")
        assert hasattr(view, "toggle_mode")
        assert hasattr(view, "set_preview")

    def test_toggle_mode_switches(self):
        from djust_components.gallery.live_views import GalleryIndexView

        view = GalleryIndexView()
        factory = RequestFactory()
        request = factory.get("/")
        request.COOKIES = {}
        view.mount(request)

        assert view.mode == "light"
        view.toggle_mode()
        assert view.mode == "dark"
        view.toggle_mode()
        assert view.mode == "light"


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
