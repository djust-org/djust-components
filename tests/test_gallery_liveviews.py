"""Tests for per-category LiveView gallery views."""

import pytest
from django.http import Http404
from django.test import RequestFactory


def _mount_view(view_class):
    """Helper: instantiate and mount a gallery view."""
    view = view_class()
    request = RequestFactory().get("/")
    request.COOKIES = {}
    view.mount(request)
    return view


# ─── Mount Tests ───


class TestGalleryCategoryViews:
    """Tests for per-category gallery views."""

    def test_layout_view_exists(self):
        from djust_components.gallery.live_views import LayoutGalleryView
        assert LayoutGalleryView.category_slug == "layout"

    def test_all_category_views_have_template(self):
        from djust_components.gallery.live_views import (
            LayoutGalleryView, FormGalleryView, DataGalleryView,
            OverlayGalleryView, FeedbackGalleryView, NavGalleryView,
            IndicatorGalleryView, TypographyGalleryView, MiscGalleryView,
        )
        for view_class in (
            LayoutGalleryView, FormGalleryView, DataGalleryView,
            OverlayGalleryView, FeedbackGalleryView, NavGalleryView,
            IndicatorGalleryView, TypographyGalleryView, MiscGalleryView,
        ):
            assert view_class.template_name == "djust_components/gallery/category.html"

    def test_layout_mount_sets_state(self):
        from djust_components.gallery.live_views import LayoutGalleryView
        view = _mount_view(LayoutGalleryView)

        assert view.category_slug == "layout"
        assert view.category_label == "Layout"
        assert isinstance(view.raw_components, list)
        assert len(view.raw_components) > 0

    def test_all_category_views_mount(self):
        from djust_components.gallery.live_views import (
            LayoutGalleryView, FormGalleryView, DataGalleryView,
            OverlayGalleryView, FeedbackGalleryView, NavGalleryView,
            IndicatorGalleryView, TypographyGalleryView, MiscGalleryView,
        )
        from djust_components.gallery.examples import CATEGORIES

        views = {
            "layout": LayoutGalleryView,
            "form": FormGalleryView,
            "data": DataGalleryView,
            "overlay": OverlayGalleryView,
            "feedback": FeedbackGalleryView,
            "navigation": NavGalleryView,
            "indicator": IndicatorGalleryView,
            "typography": TypographyGalleryView,
            "misc": MiscGalleryView,
        }
        for slug, view_class in views.items():
            view = _mount_view(view_class)
            assert view.category_slug == slug
            assert view.category_label == CATEGORIES[slug]

    def test_mount_reads_theme_cookies(self):
        from djust_components.gallery.live_views import LayoutGalleryView

        view = LayoutGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {
            "gallery_ds": "material",
            "gallery_preset": "default",
            "gallery_mode": "dark",
        }
        view.mount(request)

        assert view.design_system == "material"
        assert view.preset == "default"
        assert view.mode == "dark"

    def test_mount_validates_cookies(self):
        from djust_components.gallery.live_views import LayoutGalleryView

        view = LayoutGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {
            "gallery_ds": "INVALID",
            "gallery_mode": "bogus",
            "gallery_preset": "<script>alert(1)</script>",
        }
        view.mount(request)

        assert view.design_system == "material"
        assert view.mode == "light"
        assert view.preset == "default"

    def test_mount_builds_prev_next(self):
        from djust_components.gallery.live_views import LayoutGalleryView
        from djust_components.gallery.examples import CATEGORY_ORDER

        view = _mount_view(LayoutGalleryView)

        # "layout" is first in CATEGORY_ORDER, so no previous
        assert view.prev_category is None
        assert view.next_category is not None
        assert view.next_category["slug"] == CATEGORY_ORDER[1]

    def test_layout_has_interactive_instances(self):
        from djust_components.gallery.live_views import LayoutGalleryView

        view = _mount_view(LayoutGalleryView)

        has_any = any([
            view.accordion_instances,
            view.tabs_instances,
            view.collapsible_instances,
            view.modal_instances,
            view.sheet_instances,
        ])
        assert has_any


# ─── Event Handler Tests ───


class TestGalleryViewEvents:
    """Tests for mixin-provided event handlers."""

    def _make_view(self):
        from djust_components.gallery.live_views import LayoutGalleryView
        return _mount_view(LayoutGalleryView)

    def test_event_handlers_exist(self):
        view = self._make_view()
        for handler in (
            "accordion_toggle", "set_tab", "toggle_collapsible",
            "close_modal", "open_modal", "toggle_modal",
            "close_sheet", "open_sheet",
            "change_design_system", "change_preset", "toggle_mode", "set_preview",
        ):
            assert hasattr(view, handler), f"Missing: {handler}"

    def test_accordion_toggle(self):
        view = self._make_view()
        view.init_accordion("test-acc")
        view.accordion_toggle(value="item1", component_id="test-acc")
        assert view.accordion_instances["test-acc"]["active"] == "item1"

    def test_accordion_close(self):
        view = self._make_view()
        view.init_accordion("test-acc", active="item1")
        view.accordion_toggle(value="item1", component_id="test-acc")
        assert view.accordion_instances["test-acc"]["active"] == ""

    def test_set_tab(self):
        view = self._make_view()
        view.init_tabs("test-tabs")
        view.set_tab(value="settings", component_id="test-tabs")
        assert view.tabs_instances["test-tabs"]["active"] == "settings"

    def test_toggle_collapsible(self):
        view = self._make_view()
        view.init_collapsible("test-coll")
        view.toggle_collapsible(component_id="test-coll")
        assert view.collapsible_instances["test-coll"]["is_open"] is True
        view.toggle_collapsible(component_id="test-coll")
        assert view.collapsible_instances["test-coll"]["is_open"] is False

    def test_close_modal(self):
        view = self._make_view()
        view.init_modal("test-modal", is_open=True)
        view.close_modal(component_id="test-modal")
        assert view.modal_instances["test-modal"]["is_open"] is False

    def test_close_sheet(self):
        view = self._make_view()
        view.init_sheet("test-sheet", is_open=True)
        view.close_sheet(component_id="test-sheet")
        assert view.sheet_instances["test-sheet"]["is_open"] is False

    def test_toggle_mode(self):
        view = self._make_view()
        assert view.mode == "light"
        view.toggle_mode()
        assert view.mode == "dark"

    def test_unknown_component_id_safe(self):
        view = self._make_view()
        # Should not raise
        view.accordion_toggle(value="x", component_id="nonexistent")
        view.set_tab(value="x", component_id="nonexistent")
        view.toggle_collapsible(component_id="nonexistent")
        view.close_modal(component_id="nonexistent")
        view.close_sheet(component_id="nonexistent")


# ─── Rendering Tests ───


class TestGalleryViewRendering:

    def test_rendered_components_contain_html(self):
        from djust_components.gallery.live_views import LayoutGalleryView
        view = _mount_view(LayoutGalleryView)
        view.get_context_data()

        for comp in view.rendered_components:
            assert "label" in comp
            assert "rendered_html" in comp
            assert isinstance(comp["rendered_html"], str)

    def test_layout_has_expected_components(self):
        from djust_components.gallery.live_views import LayoutGalleryView
        view = _mount_view(LayoutGalleryView)
        view.get_context_data()

        labels = [c["label"] for c in view.rendered_components]
        assert any("Card" in label for label in labels)
        assert any("Accordion" in label for label in labels)


# ─── XSS Tests ───


class TestGalleryViewXSS:

    def test_xss_cookie_values_escaped(self):
        from djust_components.gallery.live_views import LayoutGalleryView

        view = LayoutGalleryView()
        request = RequestFactory().get("/")
        request.COOKIES = {
            "gallery_ds": '<script>alert("xss")</script>',
            "gallery_preset": '"><img src=x onerror=alert(1)>',
            "gallery_mode": '<script>alert(1)</script>',
        }
        view.mount(request)

        assert view.design_system == "material"
        assert view.preset == "default"
        assert view.mode == "light"

    def test_xss_category_slug_rejected(self):
        """GalleryCategoryMixin validates slug against known categories."""
        from djust_components.gallery.live_views import GalleryCategoryMixin

        class BadView(GalleryCategoryMixin):
            category_slug = '<script>alert("xss")</script>'

        view = BadView()
        request = RequestFactory().get("/")
        request.COOKIES = {}
        with pytest.raises(Http404):
            view.mount(request)
