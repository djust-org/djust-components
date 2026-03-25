"""
djust Component class implementations.

Alternative to template tags for programmatic use in LiveViews.

Usage::

    from djust_components.components import Badge, Button, Card, StatusDot
    from djust_components.components import Alert, StatCard, Tag, Toast, Progress, Spinner, Switch

    class MyView(LiveView):
        def mount(self, **kwargs):
            self.status_badge = Badge.status("running")
            self.priority_badge = Badge.priority("P0")
            self.agent_status = StatusDot("completed")
            self.submit_btn = Button("Save", variant="primary", action="save")
            self.info_card = Card(content="<p>Info</p>", variant="elevated")
            self.notice = Alert.success("Saved!")
            self.revenue = StatCard(label="Revenue", value="$12,345", trend="up")
            self.tag = Tag("Python", variant="info")
            self.toast = Toast.success("Done!")
            self.progress = Progress(value=75)
            self.loading = Spinner()
            self.toggle = Switch(name="dark_mode", label="Dark mode")

In template::

    {{ status_badge|safe }}
    {{ priority_badge|safe }}
    {{ agent_status|safe }}
    {{ submit_btn|safe }}
    {{ info_card|safe }}
    {{ notice|safe }}
"""

from .alert import Alert
from .badge import Badge
from .button import Button
from .card import Card
from .data_grid import DataGrid
from .markdown import Markdown
from .notification_badge import NotificationBadge
from .progress import Progress
from .progress_circle import ProgressCircle
from .rich_select import RichSelect
from .segmented_progress import SegmentedProgress
from .spinner import Spinner
from .stat_card import StatCard
from .status_dot import StatusDot
from .status_indicator import StatusIndicator
from .switch import Switch
from .tag import Tag
from .toast import Toast
from .streaming_text import StreamingText
from .connection_status import ConnectionStatus
from .live_counter import LiveCounter
from .server_event_toast import ServerEventToastMixin

__all__ = [
    "Alert",
    "Badge",
    "Button",
    "Card",
    "ConnectionStatus",
    "DataGrid",
    "LiveCounter",
    "Markdown",
    "NotificationBadge",
    "Progress",
    "ProgressCircle",
    "RichSelect",
    "SegmentedProgress",
    "ServerEventToastMixin",
    "Spinner",
    "StatCard",
    "StatusDot",
    "StatusIndicator",
    "StreamingText",
    "Switch",
    "Tag",
    "Toast",
]
