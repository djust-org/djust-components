"""
CollapsibleMixin — collapsible section state management for djust LiveViews.

Usage::

    class MyPage(CollapsibleMixin, LiveView):
        def mount(self, request, **kwargs):
            self.init_collapsible("details", is_open=True)
            self.details = self.get_collapsible_ctx("details")
"""

from djust.decorators import event_handler

from .base import ComponentMixin

__all__ = ["CollapsibleMixin"]


class CollapsibleMixin(ComponentMixin):
    """Mixin adding collapsible section state management and event handlers."""

    component_name = "collapsible"
    collapsible_instances = None

    def init_collapsible(self, instance_id, is_open=False):
        """Register a collapsible instance.

        Args:
            instance_id: Unique identifier for this collapsible section.
            is_open: Whether the section is initially open.
        """
        if self.collapsible_instances is None:
            self.collapsible_instances = {}
        instances = self.collapsible_instances
        instances[instance_id] = {
            "is_open": bool(is_open),
        }

    @event_handler
    def toggle_collapsible(self, component_id="", **kwargs):
        """Toggle a collapsible section open/closed."""
        instances = self.collapsible_instances or {}
        inst = instances.get(component_id)
        if inst is None:
            return
        inst["is_open"] = not inst["is_open"]

    def get_collapsible_ctx(self, instance_id):
        """Return template context dict for a collapsible instance."""
        inst = (self.collapsible_instances or {}).get(instance_id, {})
        return {
            "is_open": inst.get("is_open", False),
            "event": "toggle_collapsible",
            "component_id": instance_id,
        }
