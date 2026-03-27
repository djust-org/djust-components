"""Tests for per-category LiveView gallery views (descriptor-based)."""

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


# --- Mount Tests ---


class TestGalleryCategoryViews:

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

    def test_mount_builds_prev_next(self):
        from djust_components.gallery.live_views import LayoutGalleryView
        from djust_components.gallery.examples import CATEGORY_ORDER

        view = _mount_view(LayoutGalleryView)

        assert view.prev_category is None
        assert view.next_category is not None
        assert view.next_category["slug"] == CATEGORY_ORDER[1]

    def test_layout_has_descriptor_state(self):
        from djust_components.gallery.live_views import LayoutGalleryView
        from djust_components.mixins.base import TypedState

        view = _mount_view(LayoutGalleryView)

        assert isinstance(view.accordion, TypedState)
        assert isinstance(view.tabs, TypedState)
        assert isinstance(view.collapsible, TypedState)
        assert isinstance(view.modal, TypedState)
        assert isinstance(view.sheet, TypedState)

    def test_layout_descriptors_registered(self):
        from djust_components.gallery.live_views import LayoutGalleryView

        descriptors = LayoutGalleryView._component_descriptors
        assert "accordion" in descriptors
        assert "tabs" in descriptors
        assert "collapsible" in descriptors
        assert "modal" in descriptors
        assert "sheet" in descriptors


# --- Event Handler Tests ---


class TestGalleryViewEvents:

    def _make_view(self):
        from djust_components.gallery.live_views import LayoutGalleryView
        return _mount_view(LayoutGalleryView)

    def test_component_event_handlers_exist(self):
        view = self._make_view()
        for handler in (
            "accordion_toggle", "set_tab", "toggle_collapsible",
            "toggle_modal", "toggle_sheet",
        ):
            assert hasattr(view, handler), f"Missing: {handler}"

    def test_accordion_toggle(self):
        view = self._make_view()
        view.accordion_toggle(value="item1", component_id="accordion")
        assert view.accordion.active == "item1"

    def test_accordion_close(self):
        view = self._make_view()
        view.accordion_toggle(value="item1", component_id="accordion")
        view.accordion_toggle(value="item1", component_id="accordion")
        assert view.accordion.active == ""

    def test_set_tab(self):
        view = self._make_view()
        view.set_tab(value="settings", component_id="tabs")
        assert view.tabs.active == "settings"

    def test_toggle_collapsible(self):
        view = self._make_view()
        view.toggle_collapsible(component_id="collapsible")
        assert view.collapsible.is_open is True
        view.toggle_collapsible(component_id="collapsible")
        assert view.collapsible.is_open is False

    def test_toggle_modal(self):
        view = self._make_view()
        view.toggle_modal(component_id="modal")
        assert view.modal.is_open is True

    def test_toggle_sheet(self):
        view = self._make_view()
        view.toggle_sheet(component_id="sheet")
        assert view.sheet.is_open is True

    def test_unknown_component_id_safe(self):
        view = self._make_view()
        view.accordion_toggle(value="x", component_id="nonexistent")
        view.set_tab(value="x", component_id="nonexistent")


# --- Rendering Tests ---


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


# --- XSS Tests ---


class TestGalleryViewXSS:

    def test_xss_category_slug_rejected(self):
        from djust_components.gallery.live_views import GalleryCategoryMixin

        class BadView(GalleryCategoryMixin):
            category_slug = '<script>alert("xss")</script>'

        view = BadView()
        request = RequestFactory().get("/")
        request.COOKIES = {}
        with pytest.raises(Http404):
            view.mount(request)


# --- Theme Context Processor Tests ---


class TestGalleryThemeContextProcessor:

    def test_context_processor_returns_theme_data(self):
        from djust_components.gallery.context_processors import gallery_theme

        request = RequestFactory().get("/")
        request.COOKIES = {}
        ctx = gallery_theme(request)

        assert "theme_css" in ctx
        assert ctx["design_system"] == "material"
        assert ctx["preset"] == "default"
        assert ctx["mode"] == "light"
        assert "ds_options" in ctx
        assert "preset_options" in ctx

    def test_context_processor_reads_cookies(self):
        from djust_components.gallery.context_processors import gallery_theme

        request = RequestFactory().get("/")
        request.COOKIES = {"gallery_mode": "dark"}
        ctx = gallery_theme(request)

        assert ctx["mode"] == "dark"

    def test_context_processor_validates_cookies(self):
        from djust_components.gallery.context_processors import gallery_theme

        request = RequestFactory().get("/")
        request.COOKIES = {
            "gallery_ds": '<script>alert("xss")</script>',
            "gallery_mode": "INVALID",
        }
        ctx = gallery_theme(request)

        assert ctx["design_system"] == "material"
        assert ctx["mode"] == "light"


# --- Descriptor Integration Tests ---


class TestGalleryDescriptorIntegration:

    def test_data_view_has_tabs_descriptor(self):
        from djust_components.gallery.live_views import DataGalleryView
        assert "tabs" in DataGalleryView._component_descriptors

    def test_overlay_view_has_modal_and_sheet(self):
        from djust_components.gallery.live_views import OverlayGalleryView
        assert "modal" in OverlayGalleryView._component_descriptors
        assert "sheet" in OverlayGalleryView._component_descriptors

    def test_build_extra_context_reads_descriptor_state(self):
        from djust_components.gallery.live_views import LayoutGalleryView
        view = _mount_view(LayoutGalleryView)
        view.accordion_toggle(value="item1", component_id="accordion")

        ctx = view._build_extra_context("accordion")
        assert ctx["active"] == "item1"

    def test_build_extra_context_empty_for_unknown(self):
        from djust_components.gallery.live_views import LayoutGalleryView
        view = _mount_view(LayoutGalleryView)
        assert view._build_extra_context("nonexistent") == {}

    def test_form_view_no_descriptors(self):
        from djust_components.gallery.live_views import FormGalleryView
        descriptors = getattr(FormGalleryView, "_component_descriptors", {})
        assert len(descriptors) == 0
