"""LiveView-based gallery views for interactive component browsing."""

from django.http import Http404

from djust import LiveView
from djust.decorators import event_handler

from .views import _get_theme_css, _get_theme_options, _render_component_cards


class GalleryThemeMixin:
    """Shared theme management for gallery LiveViews.

    Reads theme cookies, validates against allowlists, and provides
    event handlers for changing design system, preset, mode, and preview.
    """

    def mount_theme(self, request):
        """Read and validate theme state from cookies."""
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
            cat_label = CATEGORIES.get(slug, slug.title())
            comps = categories.get(cat_label, [])
            self.category_cards.append({
                "slug": slug,
                "label": cat_label,
                "count": len(comps),
            })


class CategoryGalleryView(GalleryThemeMixin, LiveView):
    """Per-category gallery page with rendered components and interactive state."""

    template_name = "djust_components/gallery/category.html"
    login_required = False

    def mount(self, request, category_slug=None, **kwargs):
        from .examples import CATEGORIES, CATEGORY_ORDER
        from .registry import get_gallery_data

        # Validate category slug
        if category_slug not in CATEGORIES:
            raise Http404(f"Unknown category: {category_slug}")

        self.category_slug = category_slug
        self.category_label = CATEGORIES[category_slug]

        # Theme
        self.mount_theme(request)

        # Gallery data
        data = get_gallery_data()
        categories = data["categories"]

        # Build category cards for sidebar
        self.category_cards = []
        for slug in CATEGORY_ORDER:
            cat_label = CATEGORIES.get(slug, slug.title())
            comps = categories.get(cat_label, [])
            self.category_cards.append({
                "slug": slug,
                "label": cat_label,
                "count": len(comps),
            })

        # Render components for this category
        components = categories.get(self.category_label, [])
        self.rendered_components = []
        for comp in components:
            rendered_html = _render_component_cards([comp])
            self.rendered_components.append({
                "name": comp["name"],
                "label": comp["label"],
                "type": comp["type"],
                "rendered_html": rendered_html,
            })

        self.active_category = category_slug

        # Prev/next navigation
        idx = CATEGORY_ORDER.index(category_slug)
        self.prev_category = None
        self.next_category = None
        if idx > 0:
            prev_slug = CATEGORY_ORDER[idx - 1]
            self.prev_category = {
                "slug": prev_slug,
                "label": CATEGORIES.get(prev_slug, prev_slug.title()),
            }
        if idx < len(CATEGORY_ORDER) - 1:
            next_slug = CATEGORY_ORDER[idx + 1]
            self.next_category = {
                "slug": next_slug,
                "label": CATEGORIES.get(next_slug, next_slug.title()),
            }

        # Interactive state dicts
        self.accordion_states = {}
        self.active_tabs = {}
        self.collapsible_states = {}
        self.modal_open = {}
        self.sheet_open = {}

    @event_handler
    def accordion_toggle(self, id="", index=0, **kwargs):
        """Toggle an accordion item open/closed."""
        if id not in self.accordion_states:
            self.accordion_states[id] = {}
        current = self.accordion_states[id].get(index, False)
        self.accordion_states[id][index] = not current

    @event_handler
    def set_tab(self, id="", value="", **kwargs):
        """Set the active tab for a tab group."""
        self.active_tabs[id] = value

    @event_handler
    def toggle_collapsible(self, id="", **kwargs):
        """Toggle a collapsible section open/closed."""
        current = self.collapsible_states.get(id, False)
        self.collapsible_states[id] = not current

    @event_handler
    def close_modal(self, id="", **kwargs):
        """Close a modal by ID."""
        self.modal_open[id] = False

    @event_handler
    def close_sheet(self, id="", **kwargs):
        """Close a sheet by ID."""
        self.sheet_open[id] = False
