"""LiveView-based gallery views for interactive component browsing."""

from django.http import Http404

from djust import LiveView
from djust.decorators import event_handler

from djust_components.mixins import (
    AccordionMixin,
    CollapsibleMixin,
    ModalMixin,
    SheetMixin,
    TabsMixin,
)
from djust_components.mixins.accordion import AccordionState
from djust_components.mixins.tabs import TabsState

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
    """Base for per-category gallery views.

    Subclasses declare their category and which components are interactive::

        class LayoutGalleryView(AccordionMixin, TabsMixin, ...,
                                GalleryCategoryMixin, LiveView):
            category_slug = "layout"
            interactive_components = ["accordion", "tabs", "collapsible", "modal", "sheet"]
            _state_context = {
                "accordion": ("accordion_instances", AccordionState, "active"),
                "tabs": ("tabs_instances", TabsState, "active"),
            }
    """

    template_name = "djust_components/gallery/category.html"
    login_required = False

    # ── Subclass configuration ──
    category_slug = ""
    interactive_components = []
    _state_context = {}

    # Maps component name → init method name
    _INIT_METHODS = {
        "accordion": "init_accordion",
        "tabs": "init_tabs",
        "collapsible": "init_collapsible",
        "modal": "init_modal",
        "sheet": "init_sheet",
    }

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

        # Register mixin instances for interactive components
        for comp in self.raw_components:
            method = self._INIT_METHODS.get(comp["name"])
            if method and comp["name"] in self.interactive_components:
                getattr(self, method)(comp["name"])

    def get_context_data(self, **kwargs):
        """Re-render component examples with current mixin state."""
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
        mapping = self._state_context.get(comp_name)
        if mapping is None:
            return {}
        attr_name, state_class, ctx_key = mapping
        instances = getattr(self, attr_name, None)
        if not instances or comp_name not in instances:
            return {}
        inst = self._get_typed_instance(comp_name, state_class)
        if inst is None:
            return {}
        return {ctx_key: getattr(inst, ctx_key, "")}


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


class LayoutGalleryView(
    AccordionMixin, TabsMixin, CollapsibleMixin, ModalMixin, SheetMixin,
    GalleryCategoryMixin, LiveView,
):
    """Layout category — accordion, tabs, cards, sheets, etc."""
    category_slug = "layout"
    interactive_components = ["accordion", "tabs", "collapsible", "modal", "sheet"]
    _state_context = {
        "accordion": ("accordion_instances", AccordionState, "active"),
        "tabs": ("tabs_instances", TabsState, "active"),
    }


class FormGalleryView(GalleryCategoryMixin, LiveView):
    """Form category — inputs, selects, pickers, etc."""
    category_slug = "form"


class DataGalleryView(TabsMixin, GalleryCategoryMixin, LiveView):
    """Data category — tables, charts, trees, etc."""
    category_slug = "data"
    interactive_components = ["tabs"]
    _state_context = {
        "tabs": ("tabs_instances", TabsState, "active"),
    }


class OverlayGalleryView(
    ModalMixin, SheetMixin, GalleryCategoryMixin, LiveView,
):
    """Overlay category — modals, dropdowns, tooltips, etc."""
    category_slug = "overlay"
    interactive_components = ["modal", "sheet"]


class FeedbackGalleryView(GalleryCategoryMixin, LiveView):
    """Feedback category — alerts, toasts, progress, etc."""
    category_slug = "feedback"


class NavGalleryView(
    AccordionMixin, TabsMixin, GalleryCategoryMixin, LiveView,
):
    """Navigation category — stepper, breadcrumb, pagination, etc."""
    category_slug = "navigation"
    interactive_components = ["accordion", "tabs"]
    _state_context = {
        "accordion": ("accordion_instances", AccordionState, "active"),
        "tabs": ("tabs_instances", TabsState, "active"),
    }


class IndicatorGalleryView(GalleryCategoryMixin, LiveView):
    """Indicator category — badges, gauges, ratings, etc."""
    category_slug = "indicator"


class TypographyGalleryView(GalleryCategoryMixin, LiveView):
    """Typography category — code blocks, markdown, etc."""
    category_slug = "typography"


class MiscGalleryView(
    AccordionMixin, TabsMixin, ModalMixin,
    GalleryCategoryMixin, LiveView,
):
    """Misc category — carousel, chat, theme toggle, etc."""
    category_slug = "misc"
    interactive_components = ["accordion", "tabs", "modal"]
    _state_context = {
        "accordion": ("accordion_instances", AccordionState, "active"),
        "tabs": ("tabs_instances", TabsState, "active"),
    }
