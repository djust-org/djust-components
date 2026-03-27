"""
AccordionMixin — accordion state management for djust LiveViews.

Usage::

    class MyPage(AccordionMixin, LiveView):
        def mount(self, request, **kwargs):
            self.init_accordion("faq", active="q1")
            self.faq = self.get_accordion_ctx("faq")
"""

from djust.decorators import event_handler

from .base import ComponentMixin

__all__ = ["AccordionMixin"]


class AccordionMixin(ComponentMixin):
    """Mixin adding accordion state management and event handlers."""

    component_name = "accordion"
    accordion_instances = None

    def init_accordion(self, instance_id, active="", multiple=False):
        """Register an accordion instance.

        Args:
            instance_id: Unique identifier for this accordion.
            active: Initially active item ID (str), or list if multiple=True.
            multiple: Whether multiple items can be open simultaneously.
        """
        if self.accordion_instances is None:
            self.accordion_instances = {}
        instances = self.accordion_instances
        instances[instance_id] = {
            "active": list(active) if multiple and isinstance(active, (list, tuple)) else (active if not multiple else []),
            "multiple": multiple,
        }

    @event_handler
    def accordion_toggle(self, value="", component_id="", **kwargs):
        """Toggle an accordion item open/closed."""
        instances = self.accordion_instances or {}
        inst = instances.get(component_id)
        if inst is None:
            return
        if inst["multiple"]:
            actives = inst["active"]
            if value in actives:
                actives.remove(value)
            else:
                actives.append(value)
        else:
            inst["active"] = "" if inst["active"] == value else value

    def get_accordion_ctx(self, instance_id):
        """Return template context dict for an accordion instance."""
        inst = (self.accordion_instances or {}).get(instance_id, {})
        return {
            "active": inst.get("active", ""),
            "event": "accordion_toggle",
            "component_id": instance_id,
        }
