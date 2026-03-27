"""LiveView-based gallery views for interactive component browsing.

Uses descriptor-based components (DEP-002) instead of mixins for interactive
state management.  Descriptors auto-initialise on first access and register
event handlers automatically.
"""

from django.http import Http404

from djust import LiveView
from djust.decorators import event_handler

from djust_components.descriptors import (
    Accordion,
    Collapsible,
    Modal,
    Sheet,
    Tabs,
)

from .views import _get_theme_css, _get_theme_options, _render_component_cards


# ---------------------------------------------------------------------------
# Shared mixins
# ---------------------------------------------------------------------------


class GalleryThemeMixin:
    """Shared theme management: cookies, validation, event handlers."""

    def mount_theme(self, request):
        self.preset_options, self.ds_options = _get_theme_options()

        self.design_system = request.COOKIES.get("gallery_ds", "material")
        if self.design_system not in self.ds_options:
            self.design_system = "material"

        self.preset = request.COOKIES.get("gallery_preset", "default")
        if self.preset not in self.preset_options:
            self.preset = "default"

        self.mode = request.COOKIES.get("gallery_mode", "light")
        if self.mode not in ("light", "dark"):
            self.mode = "light"

        self._regenerate_theme()
        self.preview_mode = "desktop"

    @event_handler
    def change_design_system(self, value="material", **kwargs):
        if value in self.ds_options:
            self.design_system = value
            self._regenerate_theme()

    @event_handler
    def change_preset(self, value="default", **kwargs):
        if value in self.preset_options:
            self.preset = value
            self._regenerate_theme()

    @event_handler
    def toggle_mode(self, **kwargs):
        self.mode = "dark" if self.mode == "light" else "light"
        self._regenerate_theme()

    @event_handler
    def set_preview(self, value="desktop", **kwargs):
        if value in ("mobile", "tablet", "desktop"):
            self.preview_mode = value

    def _regenerate_theme(self):
        self.theme_css = _get_theme_css(
            preset=self.preset,
            design_system=self.design_system,
            mode=self.mode,
        )


class GalleryCategoryMixin(GalleryThemeMixin):
    """Base for per-category gallery views using descriptor-based components.

    Subclasses declare descriptors as class attributes::

        class LayoutGalleryView(GalleryCategoryMixin, LiveView):
            category_slug = "layout"
            accordion = Accordion()
            tabs = Tabs()
            collapsible = Collapsible()
            modal = Modal()
            sheet = Sheet()

    Descriptors auto-initialise on first access.  Event handlers
    (``accordion_toggle``, ``set_tab``, etc.) are auto-registered by
    the descriptor protocol.

    To pass descriptor state into template rendering, override
    ``_descriptor_context_map`` — a dict mapping component name to
    (descriptor_attr, state_key)::

        _descriptor_context_map = {
            "accordion": ("accordion", "active"),
            "tabs": ("tabs", "active"),
        }
    """

    template_name = "djust_components/gallery/category.html"
    login_required = False

    # ── Subclass configuration ──
    category_slug = ""
    _descriptor_context_map = {}

    def mount(self, request, **kwargs):
        from .examples import CATEGORIES, CATEGORY_ORDER
        from .registry import get_gallery_data

        slug = self.category_slug
        if slug not in CATEGORIES:
            raise Http404(f"Unknown category: {slug}")

        self.category_label = CATEGORIES[slug]
        self.mount_theme(request)

        # Sidebar
        data = get_gallery_data()
        categories = data["categories"]
        self.category_cards = []
        for s in CATEGORY_ORDER:
            label = CATEGORIES.get(s, s.title())
            self.category_cards.append({
                "slug": s,
                "label": label,
                "count": len(categories.get(label, [])),
            })

        # View class name for dj-view attribute in template
        self.view_class_name = type(self).__name__

        # Components for this category
        self.raw_components = categories.get(self.category_label, [])
        self.active_category = slug

        # Prev/next navigation
        idx = CATEGORY_ORDER.index(slug)
        self.prev_category = (
            {"slug": CATEGORY_ORDER[idx - 1],
             "label": CATEGORIES.get(CATEGORY_ORDER[idx - 1], "")}
            if idx > 0 else None
        )
        self.next_category = (
            {"slug": CATEGORY_ORDER[idx + 1],
             "label": CATEGORIES.get(CATEGORY_ORDER[idx + 1], "")}
            if idx < len(CATEGORY_ORDER) - 1 else None
        )

        # Touch descriptors to initialise state (descriptors auto-create on access)
        descriptors = getattr(type(self), "_component_descriptors", {})
        for attr_name in descriptors:
            getattr(self, attr_name)

    def get_context_data(self, **kwargs):
        """Re-render component examples with current descriptor state."""
        self.rendered_components = []
        for comp in self.raw_components:
            ctx = self._build_extra_context(comp["name"])
            rendered_html = _render_component_cards([comp], extra_context=ctx)
            self.rendered_components.append({
                "name": comp["name"],
                "label": comp["label"],
                "type": comp["type"],
                "rendered_html": rendered_html,
            })
        return super().get_context_data(**kwargs)

    def _build_extra_context(self, comp_name):
        """Build extra template context from descriptor state.

        Uses ``_descriptor_context_map`` to look up which descriptor
        attribute and state key to read for a given component name.
        """
        mapping = self._descriptor_context_map.get(comp_name)
        if mapping is None:
            return {}
        attr_name, ctx_key = mapping
        state = getattr(self, attr_name, None)
        if state is None:
            return {}
        return {ctx_key: getattr(state, ctx_key, "")}


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------


class GalleryIndexView(GalleryThemeMixin, LiveView):
    """Landing page showing category cards with reactive theme switching."""

    template_name = "djust_components/gallery/index.html"
    login_required = False

    def mount(self, request, **kwargs):
        self.mount_theme(request)

        from .examples import CATEGORIES, CATEGORY_ORDER
        from .registry import get_gallery_data

        data = get_gallery_data()
        categories = data["categories"]
        self.category_cards = []
        for slug in CATEGORY_ORDER:
            label = CATEGORIES.get(slug, slug.title())
            self.category_cards.append({
                "slug": slug,
                "label": label,
                "count": len(categories.get(label, [])),
            })


class LayoutGalleryView(GalleryCategoryMixin, LiveView):
    """Layout category — accordion, tabs, cards, sheets, etc."""
    category_slug = "layout"
    accordion = Accordion()
    tabs = Tabs()
    collapsible = Collapsible()
    modal = Modal()
    sheet = Sheet()
    _descriptor_context_map = {
        "accordion": ("accordion", "active"),
        "tabs": ("tabs", "active"),
    }


class FormGalleryView(GalleryCategoryMixin, LiveView):
    """Form category — inputs, selects, pickers, etc."""
    category_slug = "form"


class DataGalleryView(GalleryCategoryMixin, LiveView):
    """Data category — tables, charts, trees, etc."""
    category_slug = "data"
    tabs = Tabs()
    _descriptor_context_map = {
        "tabs": ("tabs", "active"),
    }


class OverlayGalleryView(GalleryCategoryMixin, LiveView):
    """Overlay category — modals, dropdowns, tooltips, etc."""
    category_slug = "overlay"
    modal = Modal()
    sheet = Sheet()


class FeedbackGalleryView(GalleryCategoryMixin, LiveView):
    """Feedback category — alerts, toasts, progress, etc."""
    category_slug = "feedback"


class NavGalleryView(GalleryCategoryMixin, LiveView):
    """Navigation category — stepper, breadcrumb, pagination, etc."""
    category_slug = "navigation"
    accordion = Accordion()
    tabs = Tabs()
    _descriptor_context_map = {
        "accordion": ("accordion", "active"),
        "tabs": ("tabs", "active"),
    }


class IndicatorGalleryView(GalleryCategoryMixin, LiveView):
    """Indicator category — badges, gauges, ratings, etc."""
    category_slug = "indicator"


class TypographyGalleryView(GalleryCategoryMixin, LiveView):
    """Typography category — code blocks, markdown, etc."""
    category_slug = "typography"


class MiscGalleryView(GalleryCategoryMixin, LiveView):
    """Misc category — carousel, chat, theme toggle, etc."""
    category_slug = "misc"
    accordion = Accordion()
    tabs = Tabs()
    modal = Modal()
    _descriptor_context_map = {
        "accordion": ("accordion", "active"),
        "tabs": ("tabs", "active"),
    }
