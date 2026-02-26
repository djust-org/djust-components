"""TtydTerminalView — embed a ttyd WebSocket terminal via xterm.js.

The view renders a container div with dj-hook="TtydTerminal" and passes
all config as data-* attributes. The JS hook (ttyd_terminal.js) opens a
direct WebSocket to the ttyd backend — no djust relay.

Primary use cases:
  - djustlive deploy log tailing
  - Local dev shell embedding

Usage::

    # urls.py
    from djust_components.ttyd import TtydTerminalView

    path("shell/", TtydTerminalView.as_view(), name="shell"),

    # With custom defaults (subclass pattern)
    class DeployLogView(TtydTerminalView):
        ttyd_url = "ws://localhost:7682"
        rows = 40
        cols = 120

    # Or pass URL query params: /shell/?url=ws://host:7681&rows=30&cols=100

Note: ttyd must be run with --check-origin=false (or same origin) to allow
WebSocket connections from the browser. CDN-loaded xterm.js requires internet
access; vendor xterm.js to static/ for offline/air-gapped environments.
"""

import json
from typing import Optional

from djust import LiveView


class TtydTerminalView(LiveView):
    """LiveView that renders an xterm.js terminal connected to a ttyd backend.

    All terminal configuration flows through URL query params (mount-time only).
    To hardcode config, use the subclass pattern — this avoids user-controlled
    WebSocket URL injection in sensitive deployments.
    """

    template_name = "djust_components/ttyd_terminal.html"
    login_required = False  # v1: assume open/local access; override in subclasses

    # Default props — override by subclassing or via URL query params
    ttyd_url: str = "ws://localhost:7681"
    rows: int = 24
    cols: int = 80
    theme: Optional[dict] = None

    def mount(self, request, **kwargs):
        params = request.GET
        self.ttyd_url = params.get("url", self.__class__.ttyd_url)
        self.rows = int(params.get("rows", self.__class__.rows))
        self.cols = int(params.get("cols", self.__class__.cols))

        theme_param = params.get("theme", None)
        if theme_param:
            try:
                self.theme = json.loads(theme_param)
            except (json.JSONDecodeError, TypeError):
                self.theme = {}
        else:
            class_theme = self.__class__.theme
            self.theme = dict(class_theme) if class_theme else {}

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["theme_json"] = json.dumps(self.theme or {})
        return ctx
