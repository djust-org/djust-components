"""
CarouselMixin — carousel/slideshow state management for djust LiveViews.

Usage::

    class MyPage(CarouselMixin, LiveView):
        def mount(self, request, **kwargs):
            self.init_carousel("gallery", total=5)
            self.gallery = self.get_carousel_ctx("gallery")
"""

from djust.decorators import event_handler

from .base import ComponentMixin

__all__ = ["CarouselMixin"]


class CarouselMixin(ComponentMixin):
    """Mixin adding carousel state management and event handlers."""

    component_name = "carousel"
    carousel_instances = None

    def init_carousel(self, instance_id, active=0, total=0):
        """Register a carousel instance.

        Args:
            instance_id: Unique identifier for this carousel.
            active: Initially active slide index (0-based).
            total: Total number of slides.
        """
        if self.carousel_instances is None:
            self.carousel_instances = {}
        instances = self.carousel_instances
        instances[instance_id] = {
            "active": int(active),
            "total": int(total),
        }

    @event_handler
    def carousel_prev(self, component_id="", **kwargs):
        """Go to the previous slide (wraps around)."""
        instances = self.carousel_instances or {}
        inst = instances.get(component_id)
        if inst is None:
            return
        total = inst["total"]
        if total > 0:
            inst["active"] = (inst["active"] - 1) % total

    @event_handler
    def carousel_next(self, component_id="", **kwargs):
        """Go to the next slide (wraps around)."""
        instances = self.carousel_instances or {}
        inst = instances.get(component_id)
        if inst is None:
            return
        total = inst["total"]
        if total > 0:
            inst["active"] = (inst["active"] + 1) % total

    @event_handler
    def carousel_go(self, value="0", component_id="", **kwargs):
        """Go to a specific slide by index."""
        instances = self.carousel_instances or {}
        inst = instances.get(component_id)
        if inst is None:
            return
        try:
            index = int(value)
        except (ValueError, TypeError):
            return
        total = inst["total"]
        if total > 0 and 0 <= index < total:
            inst["active"] = index

    def get_carousel_ctx(self, instance_id):
        """Return template context dict for a carousel instance."""
        inst = (self.carousel_instances or {}).get(instance_id, {})
        return {
            "active": inst.get("active", 0),
            "total": inst.get("total", 0),
            "prev_event": "carousel_prev",
            "next_event": "carousel_next",
            "go_event": "carousel_go",
            "component_id": instance_id,
        }
