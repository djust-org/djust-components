"""
Template tags for djust-components.

Usage:
    {% load djust_components %}
    {% modal id="my-modal" title="Confirm" open=modal_open %}...{% endmodal %}
    {% tabs id="my-tabs" active=active_tab %}
        {% tab "overview" label="Overview" %}...{% endtab %}
        {% tab "settings" label="Settings" %}...{% endtab %}
    {% endtabs %}
"""
import uuid

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve(value, context):
    """Resolve a template variable or return the literal value."""
    if isinstance(value, template.Variable):
        try:
            return value.resolve(context)
        except template.VariableDoesNotExist:
            return ""
    return value


def _parse_kv_args(bits, parser):
    """Parse key=value arguments from template tag tokens."""
    kwargs = {}
    for bit in bits:
        if "=" in bit:
            key, val = bit.split("=", 1)
            # Strip quotes for literal strings
            if (val.startswith('"') and val.endswith('"')) or \
               (val.startswith("'") and val.endswith("'")):
                kwargs[key] = val[1:-1]
            else:
                kwargs[key] = template.Variable(val)
        else:
            raise template.TemplateSyntaxError(
                f"Unexpected argument '{bit}'. Use key=value format."
            )
    return kwargs


# ---------------------------------------------------------------------------
# 1. Modal
# ---------------------------------------------------------------------------

class ModalNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        modal_id = kw.get("id", "modal")
        title = kw.get("title", "")
        is_open = kw.get("open", False)
        size = kw.get("size", "md")  # sm, md, lg, xl
        close_event = kw.get("close_event", "close_modal")

        if not is_open:
            return ""

        content = self.nodelist.render(context)
        size_class = {
            "sm": "dj-modal--sm",
            "md": "dj-modal--md",
            "lg": "dj-modal--lg",
            "xl": "dj-modal--xl",
        }.get(size, "dj-modal--md")

        return mark_safe(f"""<div class="dj-modal-backdrop" dj-click="{close_event}">
  <div class="dj-modal {size_class}" onclick="event.stopPropagation()">
    <div class="dj-modal__header">
      <h3 class="dj-modal__title">{title}</h3>
      <button class="dj-modal__close" dj-click="{close_event}">&times;</button>
    </div>
    <div class="dj-modal__body">{content}</div>
  </div>
</div>""")


@register.tag("modal")
def do_modal(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endmodal",))
    parser.delete_first_token()
    return ModalNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# 2. Tabs
# ---------------------------------------------------------------------------

class TabNode(template.Node):
    """A single tab pane."""
    def __init__(self, tab_id, label, icon, nodelist):
        self.tab_id = tab_id
        self.label = label
        self.icon = icon
        self.nodelist = nodelist

    def render(self, context):
        return self.nodelist.render(context)


class TabsNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        tabs_id = kw.get("id", "tabs")
        active = kw.get("active", "")
        event = kw.get("event", "set_tab")

        # Collect tab nodes
        tabs = [n for n in self.nodelist if isinstance(n, TabNode)]
        if not active and tabs:
            active = _resolve(tabs[0].tab_id, context)

        # Build tab nav
        nav_items = []
        for tab in tabs:
            tid = _resolve(tab.tab_id, context)
            label = _resolve(tab.label, context)
            icon = _resolve(tab.icon, context) if tab.icon else ""
            active_cls = "dj-tab--active" if tid == active else ""
            icon_html = f'<span class="dj-tab__icon">{icon}</span> ' if icon else ""
            nav_items.append(
                f'<button class="dj-tab {active_cls}" '
                f'dj-click="{event}" data-value="{tid}">'
                f'{icon_html}{label}</button>'
            )

        nav = f'<nav class="dj-tabs__nav">{"".join(nav_items)}</nav>'

        # Build active pane
        pane = ""
        for tab in tabs:
            tid = _resolve(tab.tab_id, context)
            if tid == active:
                pane = f'<div class="dj-tabs__pane">{tab.render(context)}</div>'
                break

        return mark_safe(f'<div class="dj-tabs" id="{tabs_id}">{nav}{pane}</div>')


@register.tag("tabs")
def do_tabs(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endtabs",))
    parser.delete_first_token()
    return TabsNode(nodelist, kwargs)


@register.tag("tab")
def do_tab(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    tab_id = kwargs.get("id", "")
    label = kwargs.get("label", "")
    icon = kwargs.get("icon", "")
    nodelist = parser.parse(("endtab",))
    parser.delete_first_token()
    return TabNode(tab_id, label, icon, nodelist)


# ---------------------------------------------------------------------------
# 3. Accordion
# ---------------------------------------------------------------------------

class AccordionItemNode(template.Node):
    def __init__(self, item_id, title, nodelist):
        self.item_id = item_id
        self.title = title
        self.nodelist = nodelist

    def render(self, context):
        return self.nodelist.render(context)


class AccordionNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        accordion_id = kw.get("id", "accordion")
        active = kw.get("active", "")
        event = kw.get("event", "accordion_toggle")

        items = [n for n in self.nodelist if isinstance(n, AccordionItemNode)]
        parts = []
        for item in items:
            iid = _resolve(item.item_id, context)
            title = _resolve(item.title, context)
            is_open = iid == active
            open_cls = "dj-accordion-item--open" if is_open else ""
            chevron_cls = "dj-accordion__chevron--open" if is_open else ""
            content_html = ""
            if is_open:
                content_html = (
                    f'<div class="dj-accordion__content">'
                    f'{item.render(context)}</div>'
                )
            parts.append(
                f'<div class="dj-accordion-item {open_cls}">'
                f'<button class="dj-accordion__trigger" dj-click="{event}" data-value="{iid}">'
                f'<span>{title}</span>'
                f'<span class="dj-accordion__chevron {chevron_cls}">&#9662;</span>'
                f'</button>'
                f'{content_html}</div>'
            )

        return mark_safe(
            f'<div class="dj-accordion" id="{accordion_id}">{"".join(parts)}</div>'
        )


@register.tag("accordion")
def do_accordion(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endaccordion",))
    parser.delete_first_token()
    return AccordionNode(nodelist, kwargs)


@register.tag("accordion_item")
def do_accordion_item(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    item_id = kwargs.get("id", "")
    title = kwargs.get("title", "")
    nodelist = parser.parse(("endaccordion_item",))
    parser.delete_first_token()
    return AccordionItemNode(item_id, title, nodelist)


# ---------------------------------------------------------------------------
# 4. Dropdown
# ---------------------------------------------------------------------------

class DropdownNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        dropdown_id = kw.get("id", "dropdown")
        label = kw.get("label", "Menu")
        is_open = kw.get("open", False)
        toggle_event = kw.get("toggle_event", "toggle_dropdown")
        variant = kw.get("variant", "default")

        content = self.nodelist.render(context)
        open_cls = "dj-dropdown--open" if is_open else ""
        variant_cls = f"dj-dropdown--{variant}"

        menu_html = ""
        if is_open:
            menu_html = f'<div class="dj-dropdown__menu">{content}</div>'

        return mark_safe(
            f'<div class="dj-dropdown {open_cls} {variant_cls}" id="{dropdown_id}">'
            f'<button class="dj-dropdown__trigger" dj-click="{toggle_event}">{label}</button>'
            f'{menu_html}</div>'
        )


@register.tag("dropdown")
def do_dropdown(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("enddropdown",))
    parser.delete_first_token()
    return DropdownNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# 5. Toast
# ---------------------------------------------------------------------------

@register.inclusion_tag("djust_components/toast.html")
def toast_container(toasts, dismiss_event="dismiss_toast"):
    """Render a stack of toast notifications.

    Args:
        toasts: list of dicts with keys: id, type (success|error|warning|info), message
        dismiss_event: djust event name for dismissing a toast
    """
    return {"toasts": toasts, "dismiss_event": dismiss_event}


# ---------------------------------------------------------------------------
# 6. Tooltip
# ---------------------------------------------------------------------------

class TooltipNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        text = kw.get("text", "")
        position = kw.get("position", "top")  # top, bottom, left, right
        content = self.nodelist.render(context)

        return mark_safe(
            f'<span class="dj-tooltip dj-tooltip--{position}">'
            f'{content}'
            f'<span class="dj-tooltip__text">{text}</span>'
            f'</span>'
        )


@register.tag("tooltip")
def do_tooltip(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endtooltip",))
    parser.delete_first_token()
    return TooltipNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# 7. Progress
# ---------------------------------------------------------------------------

@register.inclusion_tag("djust_components/progress.html")
def progress(value=0, label="", size="md", color="primary", show_label=True):
    """Render a progress bar.

    Args:
        value: 0-100
        label: text label
        size: sm, md, lg
        color: primary, success, warning, danger
        show_label: whether to show percentage
    """
    value = max(0, min(100, int(value)))
    return {
        "value": value,
        "label": label,
        "size": size,
        "color": color,
        "show_label": show_label,
    }


# ---------------------------------------------------------------------------
# 8. Badge
# ---------------------------------------------------------------------------

@register.inclusion_tag("djust_components/badge.html")
def badge(label="", status="default", pulse=False):
    """Render a status badge.

    Args:
        label: display text
        status: online, offline, warning, error, default
        pulse: whether the dot should animate
    """
    return {"label": label, "status": status, "pulse": pulse}


# ---------------------------------------------------------------------------
# 9. Card
# ---------------------------------------------------------------------------

class CardNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        title = kw.get("title", "")
        subtitle = kw.get("subtitle", "")
        variant = kw.get("variant", "default")  # default, outlined, elevated
        extra_class = kw.get("class", "")

        content = self.nodelist.render(context)

        header = ""
        if title:
            sub = f'<p class="dj-card__subtitle">{subtitle}</p>' if subtitle else ""
            header = f'<div class="dj-card__header"><h3 class="dj-card__title">{title}</h3>{sub}</div>'

        return mark_safe(
            f'<div class="dj-card dj-card--{variant} {extra_class}">'
            f'{header}'
            f'<div class="dj-card__body">{content}</div>'
            f'</div>'
        )


@register.tag("card")
def do_card(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endcard",))
    parser.delete_first_token()
    return CardNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# 10. Table
# ---------------------------------------------------------------------------

@register.inclusion_tag("djust_components/table.html")
def data_table(rows, columns, sort_by="", sort_desc=False, sort_event="table_sort",
               page=1, total_pages=1, prev_event="table_prev", next_event="table_next"):
    """Render a sortable data table with pagination.

    Args:
        rows: list of dicts
        columns: list of dicts with keys: key, label
        sort_by: current sort column key
        sort_desc: sort descending?
        sort_event: djust event for sorting
        page: current page number
        total_pages: total pages
        prev_event: djust event for previous page
        next_event: djust event for next page
    """
    return {
        "rows": rows,
        "columns": columns,
        "sort_by": sort_by,
        "sort_desc": sort_desc,
        "sort_event": sort_event,
        "page": page,
        "total_pages": total_pages,
        "prev_event": prev_event,
        "next_event": next_event,
    }


# ---------------------------------------------------------------------------
# 11. Pagination
# ---------------------------------------------------------------------------

@register.inclusion_tag("djust_components/pagination.html")
def pagination(page=1, total_pages=1, prev_event="page_prev", next_event="page_next"):
    """Render pagination controls."""
    pages = []
    for p in range(1, total_pages + 1):
        if p == 1 or p == total_pages or abs(p - page) <= 2:
            pages.append(p)
        elif pages and pages[-1] != "...":
            pages.append("...")
    return {
        "page": page,
        "total_pages": total_pages,
        "pages": pages,
        "prev_event": prev_event,
        "next_event": next_event,
    }


# ---------------------------------------------------------------------------
# 12. Avatar
# ---------------------------------------------------------------------------

@register.inclusion_tag("djust_components/avatar.html")
def avatar(src="", alt="", initials="", size="md", status=""):
    """Render an avatar with optional status indicator.

    Args:
        src: image URL (if empty, shows initials)
        alt: alt text
        initials: fallback initials (e.g. "JD")
        size: xs, sm, md, lg, xl
        status: online, offline, busy, away, or empty
    """
    return {
        "src": src,
        "alt": alt,
        "initials": initials or (alt[:2].upper() if alt else ""),
        "size": size,
        "status": status,
    }
