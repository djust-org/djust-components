"""
djust Component class implementations.

Alternative to template tags for programmatic use in LiveViews.

Usage::

    from djust_components.components import Badge, StatusDot

    class MyView(LiveView):
        def mount(self, **kwargs):
            self.status_badge = Badge.status("running")
            self.priority_badge = Badge.priority("P0")
            self.agent_status = StatusDot("completed")

In template::

    {{ status_badge|safe }}
    {{ priority_badge|safe }}
    {{ agent_status|safe }}
"""

from .badge import Badge
from .status_dot import StatusDot

__all__ = ["Badge", "StatusDot"]
