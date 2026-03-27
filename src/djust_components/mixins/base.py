"""
ComponentMixin — base class for per-component interactive mixins.

Provides the instance registry pattern: each mixin manages multiple
instances of the same component type, routed by component_id.

State is stored as plain JSON-serializable dicts (no underscore prefix)
so djust's rendering pipeline can serialize them. Mixin state should
only contain UI state (which item is open, which tab is active),
never application data or secrets.
"""

__all__ = ["ComponentMixin"]


class ComponentMixin:
    """Base for per-component interactive mixins.

    Subclasses set ``component_name`` (e.g. ``"accordion"``) and declare
    a class-level ``{name}_instances = None`` attribute.  The base class
    provides helpers to initialise and look up instance state dicts.
    """

    component_name = ""

    def _instances_attr(self):
        """Return the attribute name for this mixin's instance dict."""
        return f"{self.component_name}_instances"

    def _get_instances(self):
        """Return the current instances dict, or empty dict if unset."""
        return getattr(self, self._instances_attr()) or {}

    def _get_instance(self, instance_id):
        """Return state dict for a single instance, or empty dict."""
        return self._get_instances().get(instance_id, {})

    def _init_instances(self):
        """Initialise the instances dict if it is None.

        Returns the (possibly newly created) instances dict.
        """
        attr = self._instances_attr()
        if getattr(self, attr) is None:
            setattr(self, attr, {})
        return getattr(self, attr)
