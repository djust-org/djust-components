"""Tests for LiveView-based gallery views (CategoryGalleryView)."""

import pytest
from django.http import Http404
from django.test import RequestFactory


# ─── Mount Tests ───


class TestCategoryGalleryViewMount:
    """Tests for CategoryGalleryView.mount()."""

    def test_liveview_class_exists(self):
        from djust_components.gallery.live_views import CategoryGalleryView

        assert CategoryGalleryView is not None

    def test_liveview_has_template(self):
        from djust_components.gallery.live_views import CategoryGalleryView

        assert CategoryGalleryView.template_name == "djust_components/gallery/category.html"

    def test_mount_sets_category_state(self):
        from djust_components.gallery.live_views import CategoryGalleryView

        view = CategoryGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {}
        view.mount(request, category_slug="layout")

        assert view.category_slug == "layout"
        assert view.category_label == "Layout"
        assert isinstance(view.rendered_components, list)
        assert len(view.rendered_components) > 0

    def test_mount_validates_category_slug(self):
        from djust_components.gallery.live_views import CategoryGalleryView

        view = CategoryGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {}

        with pytest.raises(Http404):
            view.mount(request, category_slug="nonexistent")

    def test_mount_reads_theme_cookies(self):
        from djust_components.gallery.live_views import CategoryGalleryView

        view = CategoryGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {
            "gallery_ds": "material",
            "gallery_preset": "default",
            "gallery_mode": "dark",
        }
        view.mount(request, category_slug="layout")

        assert view.design_system == "material"
        assert view.preset == "default"
        assert view.mode == "dark"

    def test_mount_validates_cookies(self):
        from djust_components.gallery.live_views import CategoryGalleryView

        view = CategoryGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {
            "gallery_ds": "INVALID",
            "gallery_mode": "bogus",
            "gallery_preset": "<script>alert(1)</script>",
        }
        view.mount(request, category_slug="layout")

        assert view.design_system == "material"
        assert view.mode == "light"
        assert view.preset == "default"

    def test_mount_builds_prev_next(self):
        from djust_components.gallery.live_views import CategoryGalleryView
        from djust_components.gallery.examples import CATEGORY_ORDER

        view = CategoryGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {}
        view.mount(request, category_slug="layout")

        # "layout" is first in CATEGORY_ORDER, so no previous
        assert view.prev_category is None
        # next should be the second entry
        assert view.next_category is not None
        assert view.next_category["slug"] == CATEGORY_ORDER[1]

    def test_all_categories_mount_successfully(self):
        from djust_components.gallery.live_views import CategoryGalleryView
        from djust_components.gallery.examples import CATEGORIES

        for slug in CATEGORIES:
            view = CategoryGalleryView()
            request = RequestFactory().get("/")
            request.COOKIES = {}
            view.mount(request, category_slug=slug)

            assert view.category_slug == slug
            assert view.category_label == CATEGORIES[slug]

    def test_mount_initialises_mixin_instances(self):
        """Verify that mount() uses mixins to track interactive component state."""
        from djust_components.gallery.live_views import CategoryGalleryView

        view = CategoryGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {}
        view.mount(request, category_slug="layout")

        # After mount, mixin instance dicts should exist (may be None if
        # no components of that type are in the category, but at least
        # accordion should exist for layout category)
        has_any_instances = any([
            view.accordion_instances,
            view.tabs_instances,
            view.collapsible_instances,
            view.modal_instances,
            view.sheet_instances,
        ])
        # Layout category should have at least one interactive component
        assert has_any_instances


# ─── Event Handler Tests ───


class TestCategoryGalleryViewEvents:
    """Tests for CategoryGalleryView event handlers (provided by mixins)."""

    def _make_mounted_view(self, slug="layout"):
        from djust_components.gallery.live_views import CategoryGalleryView

        view = CategoryGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {}
        view.mount(request, category_slug=slug)
        return view

    def test_event_handlers_exist(self):
        view = self._make_mounted_view()
        for handler in (
            # From mixins
            "accordion_toggle",
            "set_tab",
            "toggle_collapsible",
            "close_modal",
            "open_modal",
            "toggle_modal",
            "close_sheet",
            "open_sheet",
            # inherited from GalleryThemeMixin
            "change_design_system",
            "change_preset",
            "toggle_mode",
            "set_preview",
        ):
            assert hasattr(view, handler), f"Missing event handler: {handler}"

    def test_accordion_toggle_via_mixin(self):
        view = self._make_mounted_view()
        # Init a test accordion instance
        view.init_accordion("test-acc")
        view.accordion_toggle(value="item1", component_id="test-acc")
        assert view.accordion_instances["test-acc"]["active"] == "item1"

    def test_accordion_toggle_close(self):
        view = self._make_mounted_view()
        view.init_accordion("test-acc", active="item1")
        view.accordion_toggle(value="item1", component_id="test-acc")
        assert view.accordion_instances["test-acc"]["active"] == ""

    def test_set_tab_via_mixin(self):
        view = self._make_mounted_view()
        view.init_tabs("test-tabs")
        view.set_tab(value="settings", component_id="test-tabs")
        assert view.tabs_instances["test-tabs"]["active"] == "settings"

    def test_toggle_collapsible_via_mixin(self):
        view = self._make_mounted_view()
        view.init_collapsible("test-coll")
        view.toggle_collapsible(component_id="test-coll")
        assert view.collapsible_instances["test-coll"]["is_open"] is True
        view.toggle_collapsible(component_id="test-coll")
        assert view.collapsible_instances["test-coll"]["is_open"] is False

    def test_close_modal_via_mixin(self):
        view = self._make_mounted_view()
        view.init_modal("test-modal", is_open=True)
        view.close_modal(component_id="test-modal")
        assert view.modal_instances["test-modal"]["is_open"] is False

    def test_close_sheet_via_mixin(self):
        view = self._make_mounted_view()
        view.init_sheet("test-sheet", is_open=True)
        view.close_sheet(component_id="test-sheet")
        assert view.sheet_instances["test-sheet"]["is_open"] is False

    def test_toggle_mode_switches(self):
        view = self._make_mounted_view()

        assert view.mode == "light"
        view.toggle_mode()
        assert view.mode == "dark"
        view.toggle_mode()
        assert view.mode == "light"

    def test_unknown_component_id_is_safe(self):
        """Event handlers should silently ignore unknown component_ids."""
        view = self._make_mounted_view()
        view.init_accordion("real")
        # These should not raise
        view.accordion_toggle(value="x", component_id="nonexistent")
        view.set_tab(value="x", component_id="nonexistent")
        view.toggle_collapsible(component_id="nonexistent")
        view.close_modal(component_id="nonexistent")
        view.close_sheet(component_id="nonexistent")


# ─── Rendering Tests ───


class TestCategoryGalleryViewRendering:
    """Tests for CategoryGalleryView rendered output."""

    def _make_mounted_view(self, slug="layout"):
        from djust_components.gallery.live_views import CategoryGalleryView

        view = CategoryGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {}
        view.mount(request, category_slug=slug)
        return view

    def test_rendered_components_contain_html(self):
        view = self._make_mounted_view("layout")

        # Each rendered component should have html content
        for comp in view.rendered_components:
            assert "label" in comp
            assert "rendered_html" in comp
            assert isinstance(comp["rendered_html"], str)

    def test_layout_category_has_expected_components(self):
        view = self._make_mounted_view("layout")

        labels = [c["label"] for c in view.rendered_components]
        # Layout category should have Card and Accordion at minimum
        assert any("Card" in label for label in labels)
        assert any("Accordion" in label for label in labels)


# ─── XSS Tests ───


class TestCategoryGalleryViewXSS:
    """XSS prevention tests."""

    def test_xss_cookie_values_escaped(self):
        """Invalid cookie values are rejected (not used in output)."""
        from djust_components.gallery.live_views import CategoryGalleryView

        view = CategoryGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {
            "gallery_ds": '<script>alert("xss")</script>',
            "gallery_preset": '"><img src=x onerror=alert(1)>',
            "gallery_mode": '<script>alert(1)</script>',
        }
        view.mount(request, category_slug="layout")

        # All should fall back to safe defaults
        assert view.design_system == "material"
        assert view.preset == "default"
        assert view.mode == "light"
        assert "<script>" not in view.design_system
        assert "<script>" not in view.mode

    def test_xss_category_slug_rejected(self):
        """Invalid category slug raises Http404."""
        from djust_components.gallery.live_views import CategoryGalleryView

        view = CategoryGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {}

        with pytest.raises(Http404):
            view.mount(request, category_slug='<script>alert("xss")</script>')
