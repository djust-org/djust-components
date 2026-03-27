"""Kbd component."""

import html
from typing import List

from djust import Component


class Kbd(Component):
    """Keyboard shortcut display component.

    Args:
        keys: list of key strings (e.g. ['Ctrl', 'K'])"""

    def __init__(
        self,
        keys: list = None,
        custom_class: str = "",
        **kwargs,
    ):
        super().__init__(
            keys=keys,
            custom_class=custom_class,
            **kwargs,
        )
        self.keys = keys or []
        self.custom_class = custom_class

    def _render_custom(self) -> str:
        """Render the kbd HTML."""
        keys = self.keys or []
        if not keys:
            return ""
        cls = "kbd-group"
        if self.custom_class:
            cls += f" {html.escape(self.custom_class)}"
        parts = [f'<kbd class="kbd">{html.escape(str(k))}</kbd>' for k in keys]
        return f'<span class="{cls}">{'<span class="kbd-sep">+</span>'.join(parts)}</span>'
