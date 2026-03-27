"""
TooltipMixin — server-managed tooltip state for djust LiveViews.

Most tooltips are CSS-only, but this mixin handles cases where tooltip
visibility needs to be tracked on the server (e.g. for analytics or
conditional content loading).

Usage::

    class MyPage(TooltipMixin, LiveView):
        def mount(self, request, **kwargs):
            self.init_tooltip("help")
            self.help_tip = self.get_tooltip_ctx("help")
"""

from djust.decorators import event_handler

from .base import ComponentMixin

__all__ = ["TooltipMixin"]


class TooltipMixin(ComponentMixin):
    """Mixin adding server-managed tooltip state and event handlers."""

    component_name = "tooltip"
    tooltip_instances = None

    def init_tooltip(self, instance_id, is_visible=False):
        """Register a tooltip instance.

        Args:
            instance_id: Unique identifier for this tooltip.
            is_visible: Whether the tooltip is initially visible.
        """
        if self.tooltip_instances is None:
            self.tooltip_instances = {}
        instances = self.tooltip_instances
        instances[instance_id] = {
            "is_visible": bool(is_visible),
        }

    @event_handler
    def show_tooltip(self, component_id="", **kwargs):
        """Show a tooltip by component_id."""
        instances = self.tooltip_instances or {}
        inst = instances.get(component_id)
        if inst is None:
            return
        inst["is_visible"] = True

    @event_handler
    def hide_tooltip(self, component_id="", **kwargs):
        """Hide a tooltip by component_id."""
        instances = self.tooltip_instances or {}
        inst = instances.get(component_id)
        if inst is None:
            return
        inst["is_visible"] = False

    def get_tooltip_ctx(self, instance_id):
        """Return template context dict for a tooltip instance."""
        inst = (self.tooltip_instances or {}).get(instance_id, {})
        return {
            "is_visible": inst.get("is_visible", False),
            "show_event": "show_tooltip",
            "hide_event": "hide_tooltip",
            "component_id": instance_id,
        }
