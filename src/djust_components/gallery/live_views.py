"""LiveView-based gallery views for interactive component browsing."""

from djust import LiveView
from djust.decorators import event_handler

from .views import _get_theme_css, _get_theme_options


class GalleryIndexView(LiveView):
    """Landing page showing category cards with reactive theme switching."""

    template_name = "djust_components/gallery/index.html"
    login_required = False

    def mount(self, request, **kwargs):
        # Theme options
        self.preset_options, self.ds_options = _get_theme_options()

        # Read initial theme from cookies
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

        # Preview mode
        self.preview_mode = "desktop"

        # Gallery data
        from .registry import get_gallery_data
        from .examples import CATEGORIES, CATEGORY_ORDER

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
