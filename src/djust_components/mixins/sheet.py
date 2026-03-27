"""
SheetMixin — slide-out sheet/drawer state management for djust LiveViews.

Usage::

    class MyPage(SheetMixin, LiveView):
        def mount(self, request, **kwargs):
            self.init_sheet("settings", side="right")
            self.settings = self.get_sheet_ctx("settings")
"""

from djust.decorators import event_handler

from .base import ComponentMixin

__all__ = ["SheetMixin"]


class SheetMixin(ComponentMixin):
    """Mixin adding sheet/drawer state management and event handlers."""

    component_name = "sheet"
    sheet_instances = None

    def init_sheet(self, instance_id, is_open=False, side="right"):
        """Register a sheet instance.

        Args:
            instance_id: Unique identifier for this sheet.
            is_open: Whether the sheet is initially open.
            side: Which side the sheet slides from (left, right).
        """
        if self.sheet_instances is None:
            self.sheet_instances = {}
        instances = self.sheet_instances
        instances[instance_id] = {
            "is_open": bool(is_open),
            "side": side if side in ("left", "right") else "right",
        }

    @event_handler
    def open_sheet(self, component_id="", **kwargs):
        """Open a sheet by component_id."""
        instances = self.sheet_instances or {}
        inst = instances.get(component_id)
        if inst is None:
            return
        inst["is_open"] = True

    @event_handler
    def close_sheet(self, component_id="", **kwargs):
        """Close a sheet by component_id."""
        instances = self.sheet_instances or {}
        inst = instances.get(component_id)
        if inst is None:
            return
        inst["is_open"] = False

    def get_sheet_ctx(self, instance_id):
        """Return template context dict for a sheet instance."""
        inst = (self.sheet_instances or {}).get(instance_id, {})
        return {
            "is_open": inst.get("is_open", False),
            "side": inst.get("side", "right"),
            "open_event": "open_sheet",
            "close_event": "close_sheet",
            "component_id": instance_id,
        }
