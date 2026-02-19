"""Markdown component — renders Markdown text as sanitized HTML."""

from typing import Optional

import markdown as md_lib

from djust import Component


class Markdown(Component):
    """Render Markdown text as sanitized HTML.

    Escapes only ``<`` and ``>`` in the source text before rendering to
    prevent XSS. ``&`` is left untouched so that pre-encoded entities (e.g.
    ``&lt;`` from agent output) are not double-encoded into ``&amp;lt;``.

    The output is wrapped in a ``<div class="dj-prose">`` container. Style
    it with CSS targeting ``.dj-prose`` to control headings, lists, code
    blocks, tables, links, and blockquotes.

    Usage in a LiveView::

        self.body = Markdown(task.spec)
        self.summary = Markdown(agent.output, custom_class="text-sm")

    In template::

        {{ body|safe }}
        {{ summary|safe }}

    CSS Custom Properties::

        --dj-prose-font-size: base font size (default: 1rem)
        --dj-prose-line-height: line height (default: 1.6)
        --dj-prose-heading-color: heading color (default: var(--foreground))
        --dj-prose-link-color: link color (default: var(--primary))
        --dj-prose-code-bg: inline code background (default: var(--muted))
        --dj-prose-code-color: inline code text (default: var(--foreground))
        --dj-prose-blockquote-border: blockquote left border color (default: var(--border))
        --dj-prose-table-border: table border color (default: var(--border))

    Args:
        text: Markdown source text to render.
        custom_class: Additional CSS classes to add to the wrapper div.
        extensions: List of markdown extensions. Defaults to
            ``["fenced_code", "tables", "nl2br"]``.
    """

    _DEFAULT_EXTENSIONS = ["fenced_code", "tables", "nl2br"]

    def __init__(
        self,
        text: str = "",
        custom_class: str = "",
        extensions: Optional[list] = None,
        **kwargs,
    ):
        super().__init__(text=text, custom_class=custom_class, **kwargs)
        self.text = text
        self.custom_class = custom_class
        self._extensions = extensions if extensions is not None else self._DEFAULT_EXTENSIONS
        self._md = md_lib.Markdown(extensions=self._extensions)

    def _render_custom(self) -> str:
        if not self.text:
            return ""

        self._md.reset()

        # Escape only < and > to prevent XSS. Do NOT escape & — html.escape()
        # would turn existing entities (e.g. &lt; from agent output) into
        # &amp;lt;, causing them to render as literal "&lt;" in the browser.
        safe_text = self.text.replace("<", "&lt;").replace(">", "&gt;")
        body = self._md.convert(safe_text)

        classes = ["dj-prose"]
        if self.custom_class:
            classes.append(self.custom_class)
        class_str = " ".join(classes)

        return f'<div class="{class_str}">{body}</div>'
