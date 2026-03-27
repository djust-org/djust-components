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

**Component Gallery:**

    python manage.py component_gallery              # Serve on port 8765
    python manage.py component_gallery --port 9000  # Custom port
    python manage.py component_gallery --dry-run    # List components and exit
"""

__version__ = "0.1.0"

default_app_config = "djust_components.apps.DjustComponentsConfig"

from .ttyd import TtydTerminalView  # noqa: E402
from .mixins import (  # noqa: E402
    ComponentMixin,
    DataTableMixin,
    AccordionMixin,
    TabsMixin,
    ModalMixin,
    CollapsibleMixin,
    SheetMixin,
    DropdownMixin,
    TooltipMixin,
    CarouselMixin,
)
from .components.server_event_toast import ServerEventToastMixin  # noqa: E402
from .icons import render_icon  # noqa: E402
from .helpers import push_toast, confirm_action  # noqa: E402
from .presets import register_preset, get_preset  # noqa: E402
from .descriptors import (  # noqa: E402
    Accordion,
    Tabs,
    Modal,
    Collapsible,
    Sheet,
    Dropdown,
    Tooltip,
    Carousel,
)

__all__ = [
    # LiveViews
    "TtydTerminalView",
    # Descriptor components (preferred — DEP-002)
    "Accordion",
    "Tabs",
    "Modal",
    "Collapsible",
    "Sheet",
    "Dropdown",
    "Tooltip",
    "Carousel",
    # Mixins (deprecated — use descriptors above instead)
    "ComponentMixin",
    "DataTableMixin",
    "AccordionMixin",
    "TabsMixin",
    "ModalMixin",
    "CollapsibleMixin",
    "SheetMixin",
    "DropdownMixin",
    "TooltipMixin",
    "CarouselMixin",
    "ServerEventToastMixin",
    # Helpers
    "render_icon",
    "push_toast",
    "confirm_action",
    "register_preset",
    "get_preset",
]
