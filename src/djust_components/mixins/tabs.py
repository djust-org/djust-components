"""
TabsMixin — tab state management for djust LiveViews.

Usage::

    class MyPage(TabsMixin, LiveView):
        def mount(self, request, **kwargs):
            self.init_tabs("nav", active="overview")
            self.nav = self.get_tabs_ctx("nav")
"""

from djust.decorators import event_handler

from .base import ComponentMixin

__all__ = ["TabsMixin"]


class TabsMixin(ComponentMixin):
    """Mixin adding tab state management and event handlers."""

    component_name = "tabs"
    tabs_instances = None

    def init_tabs(self, instance_id, active=""):
        """Register a tabs instance.

        Args:
            instance_id: Unique identifier for this tab group.
            active: Initially active tab ID.
        """
        if self.tabs_instances is None:
            self.tabs_instances = {}
        instances = self.tabs_instances
        instances[instance_id] = {
            "active": active,
        }

    @event_handler
    def set_tab(self, value="", component_id="", **kwargs):
        """Set the active tab for a tab group."""
        instances = self.tabs_instances or {}
        inst = instances.get(component_id)
        if inst is None:
            return
        inst["active"] = value

    def get_tabs_ctx(self, instance_id):
        """Return template context dict for a tabs instance."""
        inst = (self.tabs_instances or {}).get(instance_id, {})
        return {
            "active": inst.get("active", ""),
            "event": "set_tab",
            "component_id": instance_id,
        }
