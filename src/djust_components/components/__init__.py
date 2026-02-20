"""
djust Component class implementations.

Alternative to template tags for programmatic use in LiveViews.

Usage::

    from djust_components.components import Badge, Button, Card, StatusDot

    class MyView(LiveView):
        def mount(self, **kwargs):
            self.status_badge = Badge.status("running")
            self.priority_badge = Badge.priority("P0")
            self.agent_status = StatusDot("completed")
            self.submit_btn = Button("Save", variant="primary", action="save")
            self.info_card = Card(content="<p>Info</p>", variant="elevated")

In template::

    {{ status_badge|safe }}
    {{ priority_badge|safe }}
    {{ agent_status|safe }}
    {{ submit_btn|safe }}
    {{ info_card|safe }}
"""

from .badge import Badge
from .button import Button
from .card import Card
from .markdown import Markdown
from .status_dot import StatusDot

__all__ = ["Badge", "Button", "Card", "Markdown", "StatusDot"]
