"""
djust-components: Reusable UI components for djust.

Add 'djust_components' to INSTALLED_APPS, then use:

**Template Tags (declarative):**

    {% load djust_components %}
    {% modal id="confirm" title="Are you sure?" %}
        <p>This action cannot be undone.</p>
    {% endmodal %}

**Component Classes (programmatic):**

    from djust_components.components import Badge, StatusDot

    class MyView(LiveView):
        def mount(self, **kwargs):
            self.status = Badge.status("running")

    # In template:
    {{ status|safe }}

See COMPONENT_CLASSES.md for full documentation.

**LiveViews:**

    from djust_components.ttyd import TtydTerminalView

    path("shell/", TtydTerminalView.as_view(), name="shell"),
"""

__version__ = "0.1.0"

default_app_config = "djust_components.apps.DjustComponentsConfig"

from .ttyd import TtydTerminalView  # noqa: E402

__all__ = ["TtydTerminalView"]
