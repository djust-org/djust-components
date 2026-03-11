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
from django.utils.html import conditional_escape
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
        e_close_event = conditional_escape(close_event)
        e_title = conditional_escape(title)

        return mark_safe(f"""<div class="dj-modal-backdrop" dj-click="{e_close_event}">
  <div class="dj-modal {size_class}" onclick="event.stopPropagation()">
    <div class="dj-modal__header">
      <h3 class="dj-modal__title">{e_title}</h3>
      <button class="dj-modal__close" dj-click="{e_close_event}">&times;</button>
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
            icon_html = f'<span class="dj-tab__icon">{conditional_escape(icon)}</span> ' if icon else ""
            nav_items.append(
                f'<button class="dj-tab {active_cls}" '
                f'dj-click="{conditional_escape(event)}" data-value="{conditional_escape(tid)}">'
                f'{icon_html}{conditional_escape(label)}</button>'
            )

        nav = f'<nav class="dj-tabs__nav">{"".join(nav_items)}</nav>'

        # Build active pane
        pane = ""
        for tab in tabs:
            tid = _resolve(tab.tab_id, context)
            if tid == active:
                pane = f'<div class="dj-tabs__pane">{tab.render(context)}</div>'
                break

        return mark_safe(f'<div class="dj-tabs" id="{conditional_escape(tabs_id)}">{nav}{pane}</div>')


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
                f'<button class="dj-accordion__trigger" dj-click="{conditional_escape(event)}" data-value="{conditional_escape(iid)}">'
                f'<span>{conditional_escape(title)}</span>'
                f'<span class="dj-accordion__chevron {chevron_cls}">&#9662;</span>'
                f'</button>'
                f'{content_html}</div>'
            )

        return mark_safe(
            f'<div class="dj-accordion" id="{conditional_escape(accordion_id)}">{"".join(parts)}</div>'
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
        variant_cls = f"dj-dropdown--{conditional_escape(variant)}"

        menu_html = ""
        if is_open:
            menu_html = f'<div class="dj-dropdown__menu">{content}</div>'

        return mark_safe(
            f'<div class="dj-dropdown {open_cls} {variant_cls}" id="{conditional_escape(dropdown_id)}">'
            f'<button class="dj-dropdown__trigger" dj-click="{conditional_escape(toggle_event)}">{conditional_escape(label)}</button>'
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
            f'<span class="dj-tooltip dj-tooltip--{conditional_escape(position)}">'
            f'{content}'
            f'<span class="dj-tooltip__text">{conditional_escape(text)}</span>'
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
            sub = f'<p class="dj-card__subtitle">{conditional_escape(subtitle)}</p>' if subtitle else ""
            header = f'<div class="dj-card__header"><h3 class="dj-card__title">{conditional_escape(title)}</h3>{sub}</div>'

        return mark_safe(
            f'<div class="dj-card dj-card--{conditional_escape(variant)} {conditional_escape(extra_class)}">'
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


# ---------------------------------------------------------------------------
# 13. Alert
# ---------------------------------------------------------------------------

_ALERT_ICONS = {
    "info": "&#8505;",
    "success": "&#10003;",
    "warning": "&#9888;",
    "error": "&#10005;",
    "danger": "&#10005;",
}


class AlertNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        alert_type = kw.get("type", "info")
        title = kw.get("title", "")
        dismissible = kw.get("dismissible", False)
        if isinstance(dismissible, str):
            dismissible = dismissible.lower() not in ("false", "0", "")
        event = kw.get("event", "dismiss_alert")

        content = self.nodelist.render(context)

        # Normalise error/danger to the same CSS class
        css_type = "error" if alert_type == "danger" else conditional_escape(alert_type)
        icon_char = _ALERT_ICONS.get(alert_type, "&#8505;")
        dismissible_cls = " alert-dismissible" if dismissible else ""

        title_html = (
            f'<div class="alert-title">{conditional_escape(title)}</div>'
            if title else ""
        )
        close_html = (
            f'<button class="alert-close" dj-click="{conditional_escape(event)}">'
            f'&times;</button>'
            if dismissible else ""
        )

        return mark_safe(
            f'<div class="alert alert-{css_type}{dismissible_cls}">'
            f'<span class="alert-icon">{icon_char}</span>'
            f'<div class="alert-body">'
            f'{title_html}'
            f'<div class="alert-message">{content}</div>'
            f'</div>'
            f'{close_html}'
            f'</div>'
        )


@register.tag("alert")
def do_alert(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endalert",))
    parser.delete_first_token()
    return AlertNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# 14. Button
# ---------------------------------------------------------------------------

@register.simple_tag
def dj_button(label="", variant="primary", event="", icon="",
              disabled=False, loading=False, size="md"):
    """Render a button element.

    Args:
        label: button text
        variant: primary, secondary, danger, ghost, link, success, warning
        event: dj-click event name
        icon: optional icon HTML/text prepended to label
        disabled: disables the button
        loading: shows spinner and disables button
        size: sm, md, lg (md emits no extra class)
    """
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    if isinstance(loading, str):
        loading = loading.lower() not in ("false", "0", "")

    classes = f"btn btn-{conditional_escape(variant)}"
    if size and size != "md":
        classes += f" btn-{conditional_escape(size)}"
    if loading:
        classes += " btn-loading"

    attrs = f'class="{classes}"'
    if event:
        attrs += f' dj-click="{conditional_escape(event)}"'
    if disabled or loading:
        attrs += " disabled"

    spinner_html = (
        '<span class="btn-spinner"></span>' if loading else ""
    )
    icon_html = (
        f'<span class="btn-icon">{conditional_escape(icon)}</span> '
        if icon else ""
    )

    return mark_safe(
        f'<button {attrs}>'
        f'{spinner_html}'
        f'{icon_html}'
        f'<span class="btn-label">{conditional_escape(label)}</span>'
        f'</button>'
    )


# ---------------------------------------------------------------------------
# 15. Input field
# ---------------------------------------------------------------------------

@register.simple_tag
def dj_input(name="", label="", value="", placeholder="", input_type="text",
             error="", helper="", required=False, disabled=False, event=""):
    """Render a labelled text input inside a form-group wrapper."""
    if isinstance(required, str):
        required = required.lower() not in ("false", "0", "")
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_value = conditional_escape(value)
    e_placeholder = conditional_escape(placeholder)
    e_type = conditional_escape(input_type)
    e_error = conditional_escape(error)
    e_helper = conditional_escape(helper)
    dj_event = conditional_escape(event or name)

    required_attr = " required" if required else ""
    disabled_attr = " disabled" if disabled else ""
    error_cls = " form-input-error" if error else ""
    required_span = '<span class="form-required"> *</span>' if required else ""

    label_html = (
        f'<label class="form-label" for="{e_name}">'
        f'{e_label}'
        f'{required_span}'
        f'</label>'
        if label else ""
    )
    error_html = (
        f'<span class="form-error-message">{e_error}</span>' if error else ""
    )
    helper_html = (
        f'<span class="form-helper">{e_helper}</span>' if helper else ""
    )

    return mark_safe(
        f'<div class="form-group">'
        f'{label_html}'
        f'<input class="form-input{error_cls}" type="{e_type}" '
        f'name="{e_name}" id="{e_name}" value="{e_value}" '
        f'placeholder="{e_placeholder}" '
        f'dj-input="{dj_event}"{required_attr}{disabled_attr}>'
        f'{error_html}'
        f'{helper_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 16. Select field
# ---------------------------------------------------------------------------

@register.simple_tag
def dj_select(name="", label="", value="", options=None,
              error="", helper="", required=False, disabled=False, event=""):
    """Render a labelled <select> inside a form-group wrapper.

    Args:
        options: list of dicts {"value":..., "label":...} or list of 2-tuples
    """
    if isinstance(required, str):
        required = required.lower() not in ("false", "0", "")
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    if options is None:
        options = []

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_error = conditional_escape(error)
    e_helper = conditional_escape(helper)
    dj_event = conditional_escape(event or name)

    required_attr = " required" if required else ""
    disabled_attr = " disabled" if disabled else ""
    error_cls = " form-select-error" if error else ""

    # Normalise options to list of (val, lbl)
    def _opt_pair(opt):
        if isinstance(opt, dict):
            return str(opt.get("value", "")), str(opt.get("label", ""))
        if isinstance(opt, (list, tuple)) and len(opt) >= 2:
            return str(opt[0]), str(opt[1])
        return str(opt), str(opt)

    options_html_parts = []
    for opt in options:
        ov, ol = _opt_pair(opt)
        selected_attr = ' selected' if str(ov) == str(value) else ""
        options_html_parts.append(
            f'<option value="{conditional_escape(ov)}"{selected_attr}>'
            f'{conditional_escape(ol)}</option>'
        )

    required_span = '<span class="form-required"> *</span>' if required else ""
    label_html = (
        f'<label class="form-label" for="{e_name}">{e_label}'
        f'{required_span}'
        f'</label>'
        if label else ""
    )
    error_html = f'<span class="form-error-message">{e_error}</span>' if error else ""
    helper_html = f'<span class="form-helper">{e_helper}</span>' if helper else ""

    return mark_safe(
        f'<div class="form-group">'
        f'{label_html}'
        f'<select class="form-select{error_cls}" name="{e_name}" id="{e_name}" '
        f'dj-change="{dj_event}"{required_attr}{disabled_attr}>'
        f'{"".join(options_html_parts)}'
        f'</select>'
        f'{error_html}'
        f'{helper_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 17. Checkbox
# ---------------------------------------------------------------------------

@register.simple_tag
def dj_checkbox(name="", label="", checked=False, value="on",
                event="", disabled=False):
    """Render a single checkbox input."""
    if isinstance(checked, str):
        checked = checked.lower() not in ("false", "0", "")
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_value = conditional_escape(value)
    dj_event = conditional_escape(event or name)

    checked_attr = " checked" if checked else ""
    disabled_attr = " disabled" if disabled else ""

    return mark_safe(
        f'<div class="form-checkbox-wrapper">'
        f'<input class="form-checkbox" type="checkbox" '
        f'name="{e_name}" id="{e_name}" value="{e_value}" '
        f'dj-change="{dj_event}"{checked_attr}{disabled_attr}>'
        f'<label class="form-checkbox-label" for="{e_name}">{e_label}</label>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 18. Radio
# ---------------------------------------------------------------------------

@register.simple_tag
def dj_radio(name="", label="", value="", current_value="",
             event="", disabled=False):
    """Render a single radio button."""
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_value = conditional_escape(value)
    radio_id = conditional_escape(f"{name}_{value}")
    dj_event = conditional_escape(event or name)

    checked_attr = " checked" if str(value) == str(current_value) else ""
    disabled_attr = " disabled" if disabled else ""

    return mark_safe(
        f'<div class="form-radio-wrapper">'
        f'<input class="form-radio" type="radio" '
        f'name="{e_name}" id="{radio_id}" value="{e_value}" '
        f'dj-change="{dj_event}"{checked_attr}{disabled_attr}>'
        f'<label class="form-radio-label" for="{radio_id}">{e_label}</label>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 19. Textarea
# ---------------------------------------------------------------------------

@register.simple_tag
def dj_textarea(name="", label="", value="", placeholder="", rows=4,
                error="", helper="", required=False, disabled=False, event=""):
    """Render a labelled <textarea> inside a form-group wrapper."""
    if isinstance(required, str):
        required = required.lower() not in ("false", "0", "")
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    try:
        rows = int(rows)
    except (ValueError, TypeError):
        rows = 4

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_value = conditional_escape(value)
    e_placeholder = conditional_escape(placeholder)
    e_error = conditional_escape(error)
    e_helper = conditional_escape(helper)
    dj_event = conditional_escape(event or name)

    required_attr = " required" if required else ""
    disabled_attr = " disabled" if disabled else ""
    error_cls = " form-input-error" if error else ""
    required_span = '<span class="form-required"> *</span>' if required else ""

    label_html = (
        f'<label class="form-label" for="{e_name}">{e_label}'
        f'{required_span}'
        f'</label>'
        if label else ""
    )
    error_html = f'<span class="form-error-message">{e_error}</span>' if error else ""
    helper_html = f'<span class="form-helper">{e_helper}</span>' if helper else ""

    return mark_safe(
        f'<div class="form-group">'
        f'{label_html}'
        f'<textarea class="form-input{error_cls}" name="{e_name}" id="{e_name}" '
        f'rows="{rows}" placeholder="{e_placeholder}" '
        f'dj-input="{dj_event}"{required_attr}{disabled_attr}>'
        f'{e_value}</textarea>'
        f'{error_html}'
        f'{helper_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 20. Form Group (block tag)
# ---------------------------------------------------------------------------

class FormGroupNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        label = kw.get("label", "")
        error = kw.get("error", "")
        helper = kw.get("helper", "")
        required = kw.get("required", False)
        if isinstance(required, str):
            required = required.lower() not in ("false", "0", "")
        for_input = kw.get("for_input", "")

        content = self.nodelist.render(context)

        for_attr = f' for="{conditional_escape(for_input)}"' if for_input else ""
        required_html = '<span class="form-required"> *</span>' if required else ""
        label_html = (
            f'<label class="form-label"{for_attr}>{conditional_escape(label)}{required_html}</label>'
            if label else ""
        )
        error_html = (
            f'<span class="form-error-message">{conditional_escape(error)}</span>'
            if error else ""
        )
        helper_html = (
            f'<span class="form-helper">{conditional_escape(helper)}</span>'
            if helper else ""
        )

        return mark_safe(
            f'<div class="form-group">'
            f'{label_html}'
            f'{content}'
            f'{error_html}'
            f'{helper_html}'
            f'</div>'
        )


@register.tag("form_group")
def do_form_group(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endform_group",))
    parser.delete_first_token()
    return FormGroupNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# 21. Spinner
# ---------------------------------------------------------------------------

@register.simple_tag
def spinner(size="md", color="primary"):
    """Render an animated spinner."""
    e_size = conditional_escape(size)
    e_color = conditional_escape(color)
    return mark_safe(
        f'<span class="spinner spinner-{e_size} spinner-{e_color}" '
        f'aria-label="Loading" role="status"></span>'
    )


# ---------------------------------------------------------------------------
# 22. Skeleton
# ---------------------------------------------------------------------------

@register.simple_tag
def skeleton(skeleton_type="text", lines=3):
    """Render skeleton loading placeholder.

    Args:
        skeleton_type: text, card, avatar, table
        lines: number of lines for text/table type
    """
    try:
        lines = int(lines)
    except (ValueError, TypeError):
        lines = 3

    if skeleton_type == "avatar":
        return mark_safe('<div class="skeleton-avatar"></div>')

    if skeleton_type == "card":
        inner_lines = "".join(
            f'<div class="skeleton-line"></div>' for _ in range(max(1, lines))
        )
        return mark_safe(
            f'<div class="skeleton-card">'
            f'<div class="skeleton-card-header"></div>'
            f'<div class="skeleton-card-body">{inner_lines}</div>'
            f'</div>'
        )

    if skeleton_type == "table":
        rows = "".join(
            f'<div class="skeleton-line"></div>' for _ in range(max(1, lines))
        )
        return mark_safe(
            f'<div class="skeleton-table">'
            f'<div class="skeleton-line skeleton-line-header"></div>'
            f'{rows}'
            f'</div>'
        )

    # Default: text lines
    line_html = "".join(
        f'<div class="skeleton-line"></div>' for _ in range(max(1, lines))
    )
    return mark_safe(f'<div class="skeleton-text">{line_html}</div>')


# ---------------------------------------------------------------------------
# 23. Breadcrumb
# ---------------------------------------------------------------------------

@register.simple_tag
def breadcrumb(items=None):
    """Render breadcrumb navigation.

    Args:
        items: list of dicts {"label":..., "url":..., "active": False}
    """
    if not items:
        return mark_safe('<nav class="breadcrumb"></nav>')

    parts = []
    for i, item in enumerate(items):
        if isinstance(item, dict):
            lbl = item.get("label", "")
            url = item.get("url", "")
            active = item.get("active", False)
        else:
            lbl, url, active = str(item), "", False

        e_lbl = conditional_escape(lbl)
        e_url = conditional_escape(url)

        if active or not url:
            crumb = f'<span class="breadcrumb-item breadcrumb-active">{e_lbl}</span>'
        else:
            crumb = (
                f'<a class="breadcrumb-item breadcrumb-link" href="{e_url}">{e_lbl}</a>'
            )

        parts.append(crumb)
        if i < len(items) - 1:
            parts.append('<span class="breadcrumb-separator">&#8250;</span>')

    return mark_safe(f'<nav class="breadcrumb">{"".join(parts)}</nav>')


# ---------------------------------------------------------------------------
# 24. Empty State
# ---------------------------------------------------------------------------

@register.simple_tag
def empty_state(title="", description="", icon="", action_label="", action_event=""):
    """Render an empty-state placeholder with optional CTA."""
    e_title = conditional_escape(title)
    e_description = conditional_escape(description)
    e_icon = conditional_escape(icon)
    e_action_label = conditional_escape(action_label)
    e_action_event = conditional_escape(action_event)

    icon_html = (
        f'<div class="empty-state-icon">{e_icon}</div>' if icon else ""
    )
    title_html = (
        f'<h3 class="empty-state-title">{e_title}</h3>' if title else ""
    )
    desc_html = (
        f'<p class="empty-state-description">{e_description}</p>' if description else ""
    )
    action_html = ""
    if action_label:
        action_html = (
            f'<button class="btn btn-primary empty-state-action" '
            f'dj-click="{e_action_event}">{e_action_label}</button>'
        )

    return mark_safe(
        f'<div class="empty-state">'
        f'{icon_html}'
        f'{title_html}'
        f'{desc_html}'
        f'{action_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 25. Divider
# ---------------------------------------------------------------------------

@register.simple_tag
def dj_divider(label="", vertical=False):
    """Render a horizontal or vertical divider, optionally with a label."""
    if isinstance(vertical, str):
        vertical = vertical.lower() not in ("false", "0", "")

    orientation_cls = "divider-vertical" if vertical else ""

    if label:
        e_label = conditional_escape(label)
        return mark_safe(
            f'<div class="divider {orientation_cls}">'
            f'<span class="divider-label">{e_label}</span>'
            f'</div>'
        )

    return mark_safe(f'<hr class="divider {orientation_cls}">')


# ---------------------------------------------------------------------------
# 26. Switch / Toggle
# ---------------------------------------------------------------------------

@register.simple_tag
def switch(name="", checked=False, label="", event="toggle", size="md", disabled=False):
    """Render an accessible switch/toggle."""
    if isinstance(checked, str):
        checked = checked.lower() not in ("false", "0", "")
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_event = conditional_escape(event)
    e_size = conditional_escape(size)

    checked_attr = " checked" if checked else ""
    disabled_attr = " disabled" if disabled else ""
    switch_id = e_name

    label_html = (
        f'<span class="switch-label">{e_label}</span>' if label else ""
    )

    return mark_safe(
        f'<label class="switch switch-{e_size}">'
        f'<input type="checkbox" name="{e_name}" id="{switch_id}" '
        f'class="switch-input" dj-change="{e_event}"{checked_attr}{disabled_attr}>'
        f'<span class="switch-track">'
        f'<span class="switch-thumb"></span>'
        f'</span>'
        f'{label_html}'
        f'</label>'
    )


# ---------------------------------------------------------------------------
# 27. Stat Card
# ---------------------------------------------------------------------------

@register.simple_tag
def stat_card(label="", value="", trend="", description="", trend_direction=""):
    """Render a metric/stat card."""
    e_label = conditional_escape(label)
    e_value = conditional_escape(value)
    e_trend = conditional_escape(trend)
    e_description = conditional_escape(description)
    e_dir = conditional_escape(trend_direction)

    trend_html = ""
    if trend:
        dir_cls = f" trend-{e_dir}" if trend_direction else ""
        arrow = {"up": "&#8593;", "down": "&#8595;", "flat": "&#8212;"}.get(
            trend_direction, ""
        )
        trend_html = (
            f'<span class="stat-trend{dir_cls}">'
            f'{arrow} {e_trend}'
            f'</span>'
        )

    desc_html = (
        f'<p class="stat-description">{e_description}</p>' if description else ""
    )

    return mark_safe(
        f'<div class="stat-card">'
        f'<div class="stat-label">{e_label}</div>'
        f'<div class="stat-value">{e_value}</div>'
        f'{trend_html}'
        f'{desc_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 28. Tag / Chip
# ---------------------------------------------------------------------------

@register.simple_tag
def dj_tag(label="", variant="default", dismissible=False, event="dismiss_tag", size=""):
    """Render a tag/chip element."""
    if isinstance(dismissible, str):
        dismissible = dismissible.lower() not in ("false", "0", "")

    e_label = conditional_escape(label)
    e_variant = conditional_escape(variant)
    e_event = conditional_escape(event)
    size_cls = f" tag-{conditional_escape(size)}" if size else ""

    close_html = (
        f'<button class="tag-close" dj-click="{e_event}">&times;</button>'
        if dismissible else ""
    )

    return mark_safe(
        f'<span class="tag tag-{e_variant}{size_cls}">'
        f'{e_label}'
        f'{close_html}'
        f'</span>'
    )


# ---------------------------------------------------------------------------
# 29. Timeline (block tag)
# ---------------------------------------------------------------------------

class TimelineNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context)
        return mark_safe(f'<div class="timeline">{content}</div>')


@register.tag("timeline")
def do_timeline(parser, token):
    nodelist = parser.parse(("endtimeline",))
    parser.delete_first_token()
    return TimelineNode(nodelist)


# ---------------------------------------------------------------------------
# 30. Timeline Item (block tag)
# ---------------------------------------------------------------------------

class TimelineItemNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        title = kw.get("title", "")
        time = kw.get("time", "")

        content = self.nodelist.render(context)

        title_html = (
            f'<div class="timeline-title">{conditional_escape(title)}</div>'
            if title else ""
        )
        time_html = (
            f'<div class="timeline-time">{conditional_escape(time)}</div>'
            if time else ""
        )

        return mark_safe(
            f'<div class="timeline-item">'
            f'<div class="timeline-marker"></div>'
            f'<div class="timeline-content">'
            f'{title_html}'
            f'{time_html}'
            f'{content}'
            f'</div>'
            f'</div>'
        )


@register.tag("timeline_item")
def do_timeline_item(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endtimeline_item",))
    parser.delete_first_token()
    return TimelineItemNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# 31. Stepper
# ---------------------------------------------------------------------------

@register.simple_tag
def stepper(steps=None, active=0, event="set_step"):
    """Render a step indicator.

    Args:
        steps: list of dicts {"label":..., "complete": False} or list of strings
        active: 0-based index of the current step
        event: dj-click event name for step navigation
    """
    if not steps:
        return mark_safe('<div class="stepper"></div>')

    try:
        active = int(active)
    except (ValueError, TypeError):
        active = 0

    e_event = conditional_escape(event)
    parts = []
    for i, step in enumerate(steps):
        if isinstance(step, dict):
            lbl = step.get("label", "")
            complete = step.get("complete", False)
        else:
            lbl = str(step)
            complete = False

        cls = "stepper-step"
        if i == active:
            cls += " stepper-step-active"
        if complete:
            cls += " stepper-step-complete"

        parts.append(
            f'<button class="{cls}" dj-click="{e_event}" data-value="{i}">'
            f'<span class="stepper-number">{i + 1}</span>'
            f'<span class="stepper-label">{conditional_escape(lbl)}</span>'
            f'</button>'
        )

    return mark_safe(f'<div class="stepper">{"".join(parts)}</div>')
