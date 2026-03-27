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


# ─── Event Handler Tests ───


class TestCategoryGalleryViewEvents:
    """Tests for CategoryGalleryView event handlers."""

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
            "accordion_toggle",
            "set_tab",
            "toggle_collapsible",
            "close_modal",
            "close_sheet",
            # inherited from mixin
            "change_design_system",
            "change_preset",
            "toggle_mode",
            "set_preview",
        ):
            assert hasattr(view, handler), f"Missing event handler: {handler}"

    def test_accordion_toggle(self):
        view = self._make_mounted_view()

        # Initially empty
        assert view.accordion_states == {}

        # Toggle open
        view.accordion_toggle(id="acc1", index=0)
        assert view.accordion_states == {"acc1": {0: True}}

        # Toggle closed
        view.accordion_toggle(id="acc1", index=0)
        assert view.accordion_states == {"acc1": {0: False}}

    def test_set_tab(self):
        view = self._make_mounted_view()

        assert view.active_tabs == {}
        view.set_tab(id="t1", value="settings")
        assert view.active_tabs == {"t1": "settings"}

    def test_toggle_collapsible(self):
        view = self._make_mounted_view()

        assert view.collapsible_states == {}
        view.toggle_collapsible(id="col1")
        assert view.collapsible_states == {"col1": True}
        view.toggle_collapsible(id="col1")
        assert view.collapsible_states == {"col1": False}

    def test_close_modal(self):
        view = self._make_mounted_view()

        assert view.modal_open == {}
        view.close_modal(id="m1")
        assert view.modal_open == {"m1": False}

    def test_close_sheet(self):
        view = self._make_mounted_view()

        assert view.sheet_open == {}
        view.close_sheet(id="s1")
        assert view.sheet_open == {"s1": False}

    def test_toggle_mode_switches(self):
        view = self._make_mounted_view()

        assert view.mode == "light"
        view.toggle_mode()
        assert view.mode == "dark"
        view.toggle_mode()
        assert view.mode == "light"


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
