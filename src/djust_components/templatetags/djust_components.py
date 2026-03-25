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
               page=1, total_pages=1, prev_event="table_prev", next_event="table_next",
               selectable=False, selected_rows=None, select_event="table_select",
               row_key="id", search=False, search_query="", search_event="table_search",
               search_debounce=300, filters=None, filter_event="table_filter",
               loading=False, empty_title="No data", empty_description="",
               empty_icon="", paginate=False, page_event="table_page",
               striped=False, compact=False,
               # Phase 2 params
               editable_columns=None, edit_event="table_cell_edit",
               resizable=False, reorderable=False, reorder_event="table_reorder",
               frozen_left=0, frozen_right=0,
               column_visibility=False, visibility_event="table_visibility",
               density="comfortable", density_toggle=False, density_event="table_density",
               responsive_cards=False,
               editable_rows=False, edit_row_event="table_row_edit",
               save_row_event="table_row_save", cancel_row_event="table_row_cancel",
               editing_rows=None,
               # Phase 3 params
               expandable=False, expand_event="table_expand", expanded_rows=None,
               bulk_actions=None, bulk_action_event="table_bulk_action",
               exportable=False, export_event="table_export", export_formats=None,
               group_by="", group_event="table_group",
               group_toggle_event="table_group_toggle",
               collapsible_groups=True, collapsed_groups=None,
               keyboard_nav=False,
               virtual_scroll=False, virtual_row_height=40, virtual_buffer=5,
               server_mode=False,
               facets=False, facet_counts=None,
               persist_key="",
               printable=False,
               column_stats=None):
    """Render a sortable data table with search, filters, selection, pagination, and editing.

    Phase 1 args:
        rows: list of dicts
        columns: list of dicts with keys: key, label, sortable, filterable, filter_type, filter_options, width
        sort_by: current sort column key
        sort_desc: sort descending?
        sort_event: djust event for sorting
        page: current page number
        total_pages: total pages
        prev_event: djust event for previous page
        next_event: djust event for next page
        selectable: enable row selection checkboxes
        selected_rows: list of selected row IDs/keys
        select_event: selection event name
        row_key: key field for row identity
        search: show global search box
        search_query: current search value
        search_event: search event name
        search_debounce: debounce ms for search input
        filters: per-column filter values {col_key: value}
        filter_event: filter event name
        loading: show loading/skeleton state
        empty_title: empty state title
        empty_description: empty state description
        empty_icon: empty state icon
        paginate: show pagination controls
        page_event: pagination event name
        striped: alternating row backgrounds
        compact: reduced padding

    Phase 2 args:
        editable_columns: list of column keys that support inline editing
        edit_event: inline cell edit event name
        resizable: enable column resize (client-side JS)
        reorderable: enable column reorder via drag (client-side JS)
        reorder_event: column reorder persist event
        frozen_left: number of columns frozen on the left
        frozen_right: number of columns frozen on the right
        column_visibility: show column visibility dropdown
        visibility_event: column visibility toggle persist event
        density: row density — "compact", "comfortable", or "spacious"
        density_toggle: show density toggle buttons
        density_event: density change event
        responsive_cards: collapse rows to stacked cards on narrow viewports
        editable_rows: enable row edit mode with Edit/Save/Cancel buttons
        edit_row_event: enter row edit mode event
        save_row_event: save edited row event
        cancel_row_event: cancel row edit event
        editing_rows: list of row keys currently in edit mode

    Phase 3 args:
        expandable: enable row expansion with detail rows
        expand_event: row expand toggle event name
        expanded_rows: list of expanded row IDs/keys
        bulk_actions: list of dicts with key/label for bulk action buttons
        bulk_action_event: bulk action event name
        exportable: show export buttons
        export_event: export event name
        export_formats: list of export formats (csv, json)
        group_by: column key to group rows by
        group_event: group change event name
        group_toggle_event: group collapse/expand toggle event
        collapsible_groups: allow group collapse/expand
        collapsed_groups: list of collapsed group values
        keyboard_nav: enable keyboard navigation
        virtual_scroll: enable virtual scrolling for large datasets
        virtual_row_height: row height in px for virtual scroll
        virtual_buffer: number of buffer rows for virtual scroll
        server_mode: explicit server-driven sort/filter/page
        facets: show faceted filtering with counts
        facet_counts: dict of {col_key: {value: count}}
        persist_key: localStorage key for state persistence
        printable: add print-friendly styles
        column_stats: dict of {col_key: {min, max, avg, sum, count}}
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
        "selectable": selectable,
        "selected_rows": selected_rows or [],
        "select_event": select_event,
        "row_key": row_key,
        "search": search,
        "search_query": search_query,
        "search_event": search_event,
        "search_debounce": search_debounce,
        "filters": filters or {},
        "filter_event": filter_event,
        "loading": loading,
        "empty_title": empty_title,
        "empty_description": empty_description,
        "empty_icon": empty_icon,
        "paginate": paginate,
        "page_event": page_event,
        "striped": striped,
        "compact": compact,
        # Phase 2
        "editable_columns": editable_columns or [],
        "edit_event": edit_event,
        "resizable": resizable,
        "reorderable": reorderable,
        "reorder_event": reorder_event,
        "frozen_left": frozen_left,
        "frozen_right": frozen_right,
        "column_visibility": column_visibility,
        "visibility_event": visibility_event,
        "density": density,
        "density_toggle": density_toggle,
        "density_event": density_event,
        "responsive_cards": responsive_cards,
        "editable_rows": editable_rows,
        "edit_row_event": edit_row_event,
        "save_row_event": save_row_event,
        "cancel_row_event": cancel_row_event,
        "editing_rows": editing_rows or [],
        # Phase 3
        "expandable": expandable,
        "expand_event": expand_event,
        "expanded_rows": expanded_rows or [],
        "bulk_actions": bulk_actions or [],
        "bulk_action_event": bulk_action_event,
        "exportable": exportable,
        "export_event": export_event,
        "export_formats": export_formats or ["csv", "json"],
        "group_by": group_by,
        "group_event": group_event,
        "group_toggle_event": group_toggle_event,
        "collapsible_groups": collapsible_groups,
        "collapsed_groups": collapsed_groups or [],
        "keyboard_nav": keyboard_nav,
        "virtual_scroll": virtual_scroll,
        "virtual_row_height": virtual_row_height,
        "virtual_buffer": virtual_buffer,
        "server_mode": server_mode,
        "facets": facets,
        "facet_counts": facet_counts or {},
        "persist_key": persist_key,
        "printable": printable,
        "column_stats": column_stats or {},
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

    orientation_cls = "divider-vertical" if vertical else "divider-horizontal"

    if label:
        e_label = conditional_escape(label)
        return mark_safe(
            f'<div class="divider-label">'
            f'<span>{e_label}</span>'
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
        f'<label class="switch-wrapper switch-{e_size}">'
        f'<span class="switch">'
        f'<input type="checkbox" name="{e_name}" id="{switch_id}" '
        f'class="switch-input" dj-change="{e_event}"{checked_attr}{disabled_attr}>'
        f'<span class="switch-track"></span>'
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


# ===========================================================================
# TIER 2 REMAINING + TIER 3 COMPONENTS
# ===========================================================================

# ---------------------------------------------------------------------------
# 32. Code Block
# ---------------------------------------------------------------------------

@register.simple_tag
def code_block(code="", language="", filename="", copy_event="copy_code",
               highlight=True, theme="github-dark"):
    """Render a syntax-highlighted code block with optional copy button.

    Args:
        highlight: When True (default), lazy-loads highlight.js from CDN.
        theme: highlight.js theme name (default "github-dark").
    """
    if isinstance(highlight, str):
        highlight = highlight.lower() not in ("false", "0", "")

    import re as _re
    e_language = conditional_escape(language or "text")
    e_filename = conditional_escape(filename)
    e_code = conditional_escape(code)
    e_event = conditional_escape(copy_event)
    # Theme is interpolated inside a <script> — HTML escaping is insufficient.
    # Restrict to alphanumeric, hyphens, and underscores to prevent injection.
    safe_theme = theme if _re.match(r'^[a-zA-Z0-9_-]+$', str(theme)) else "github-dark"
    e_theme = conditional_escape(safe_theme)

    filename_html = (
        f'<span class="code-block-filename">{e_filename}</span>'
        if filename else ""
    )
    lang_html = f'<span class="code-block-lang">{e_language}</span>'
    copy_html = (
        f'<button class="code-block-copy" '
        f'onclick="(function(btn){{var pre=btn.closest(\'.code-block\').querySelector(\'code\');'
        f'navigator.clipboard&&navigator.clipboard.writeText(pre.textContent).then(function(){{'
        f'btn.textContent=\'Copied!\';setTimeout(function(){{btn.textContent=\'Copy\';}},2000);}});}})(this)">'
        f'Copy</button>'
    )

    highlight_html = ""
    if highlight:
        highlight_html = (
            f'<script>'
            f'(function(){{'
            f'var el=document.currentScript.previousElementSibling.querySelector("code");'
            f'if(el.dataset.highlighted)return;'
            f'function doHL(){{if(window.hljs){{hljs.highlightElement(el);el.dataset.highlighted="true";}}}}'
            f'if(window.hljs){{doHL();return;}}'
            f'if(!window.__djcHljsLoading){{'
            f'window.__djcHljsLoading=true;'
            f'var lnk=document.createElement("link");lnk.rel="stylesheet";'
            f'lnk.href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11/build/styles/{e_theme}.min.css";'
            f'document.head.appendChild(lnk);'
            f'var s=document.createElement("script");'
            f's.src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11/build/highlight.min.js";'
            f's.onload=function(){{document.querySelectorAll("pre code[class^=language-]").forEach(function(b)'
            f'{{if(!b.dataset.highlighted){{hljs.highlightElement(b);b.dataset.highlighted="true";}}}});}};'
            f'document.head.appendChild(s);'
            f'}}else{{var iv=setInterval(function(){{if(window.hljs){{clearInterval(iv);doHL();}}}},50);}}'
            f'}})();'
            f'</script>'
        )

    return mark_safe(
        f'<div class="code-block" data-highlight="{e_theme if highlight else ""}">'
        f'<div class="code-block-header">'
        f'{filename_html}{lang_html}{copy_html}'
        f'</div>'
        f'<pre class="code-block-pre"><code class="language-{e_language}">{e_code}</code></pre>'
        f'{highlight_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 33. Combobox (searchable select with server-side filtering)
# ---------------------------------------------------------------------------

@register.simple_tag
def combobox(name="", label="", value="", placeholder="Search…",
             options=None, event="", search_event="", required=False,
             error="", helper="", multiple=False, selected=None):
    """Render a combobox (searchable select).

    Args:
        options: list of dicts {"value":..., "label":...}
        event: dj-change event when option selected
        search_event: dj-input event for search input (server filters options)
        multiple: when True, enables multi-select with tags
        selected: list of selected values for multi-select mode
    """
    if options is None:
        options = []
    if selected is None:
        selected = []
    if isinstance(required, str):
        required = required.lower() not in ("false", "0", "")
    if isinstance(multiple, str):
        multiple = multiple.lower() not in ("false", "0", "")

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_value = conditional_escape(value)
    e_placeholder = conditional_escape(placeholder)
    e_event = conditional_escape(event or name)
    e_search = conditional_escape(search_event or (name + "_search"))
    e_error = conditional_escape(error)
    e_helper = conditional_escape(helper)

    # Build a lookup for option labels
    opt_label_map = {}
    for opt in options:
        if isinstance(opt, dict):
            opt_label_map[str(opt.get("value", ""))] = str(opt.get("label", ""))
        else:
            opt_label_map[str(opt)] = str(opt)

    selected_set = set(str(s) for s in selected) if multiple else set()

    if multiple:
        # Multi-select mode
        # Tags for selected values
        tags_html = ""
        hidden_inputs_html = ""
        for sv in selected:
            e_sv = conditional_escape(str(sv))
            sl = opt_label_map.get(str(sv), str(sv))
            e_sl = conditional_escape(sl)
            tags_html += (
                f'<span class="combobox-tag">'
                f'<span class="combobox-tag-label">{e_sl}</span>'
                f'<button class="combobox-tag-remove" dj-click="{e_event}" '
                f'data-value="{e_sv}" type="button">&times;</button>'
                f'</span>'
            )
            hidden_inputs_html += (
                f'<input type="hidden" name="{e_name}[]" value="{e_sv}">'
            )

        tags_container = (
            f'<div class="combobox-tags">{tags_html}</div>'
            if selected else ""
        )

        # Options with selected state
        options_html = ""
        for opt in options:
            if isinstance(opt, dict):
                ov = conditional_escape(str(opt.get("value", "")))
                ol = conditional_escape(str(opt.get("label", "")))
            else:
                ov = ol = conditional_escape(str(opt))
            sel_cls = " combobox-option-selected" if str(ov) in selected_set else ""
            options_html += (
                f'<div class="combobox-option{sel_cls}" '
                f'dj-click="{e_event}" data-value="{ov}">{ol}</div>'
            )
    else:
        # Single-select mode (existing behavior)
        tags_container = ""
        hidden_inputs_html = ""

        # Find current label
        current_label = e_value
        for opt in options:
            if isinstance(opt, dict) and str(opt.get("value", "")) == str(value):
                current_label = conditional_escape(str(opt.get("label", value)))
                break

        options_html = ""
        for opt in options:
            if isinstance(opt, dict):
                ov = conditional_escape(str(opt.get("value", "")))
                ol = conditional_escape(str(opt.get("label", "")))
            else:
                ov = ol = conditional_escape(str(opt))
            sel = ' class="combobox-option-selected"' if str(ov) == str(value) else ""
            options_html += (
                f'<div class="combobox-option"{sel} '
                f'dj-click="{e_event}" data-value="{ov}">{ol}</div>'
            )

    label_html = (
        f'<label class="form-label" for="{e_name}-input">{e_label}</label>'
        if label else ""
    )
    error_html = f'<span class="form-error-message">{e_error}</span>' if error else ""
    helper_html = f'<span class="form-helper">{e_helper}</span>' if helper else ""
    req = " required" if required else ""

    if not multiple:
        current_label = e_value
        for opt in options:
            if isinstance(opt, dict) and str(opt.get("value", "")) == str(value):
                current_label = conditional_escape(str(opt.get("label", value)))
                break
        input_value = current_label
    else:
        input_value = e_value

    return mark_safe(
        f'<div class="form-group">'
        f'{label_html}'
        f'<div class="combobox" id="{e_name}-combobox">'
        f'{tags_container}'
        f'{hidden_inputs_html}'
        f'<input class="combobox-input form-input" type="text" id="{e_name}-input" '
        f'name="{e_name}" placeholder="{e_placeholder}" value="{input_value}" '
        f'dj-input="{e_search}" autocomplete="off"{req}>'
        f'<div class="combobox-dropdown" onmousedown="event.preventDefault()" onclick="this.previousElementSibling.blur()">{options_html}</div>'
        f'</div>'
        f'{error_html}{helper_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 34. Popover
# ---------------------------------------------------------------------------

@register.tag("popover")
def do_popover(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endpopover",))
    parser.delete_first_token()
    return PopoverNode(nodelist, kwargs)


class PopoverNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        trigger = kw.get("trigger", "Click me")
        placement = kw.get("placement", "bottom")
        title = kw.get("title", "")
        uid = kw.get("id", f"pop-{uuid.uuid4().hex[:6]}")

        e_uid = conditional_escape(uid)
        e_trigger = conditional_escape(trigger)
        e_placement = conditional_escape(placement)

        content = self.nodelist.render(context)
        title_html = (
            f'<div class="popover-title">{conditional_escape(title)}</div>'
            if title else ""
        )

        js = (
            "(function(el){var p=el.parentElement;"
            "p.classList.toggle('popover-open');"
            "document.addEventListener('click',function h(e){"
            "if(!p.contains(e.target)){p.classList.remove('popover-open');"
            "document.removeEventListener('click',h);}},true);})(this)"
        )
        return mark_safe(
            f'<div class="popover-wrapper" id="{e_uid}">'
            f'<button class="popover-trigger btn btn-outline btn-sm" '
            f'onclick="{js}">'
            f'{e_trigger}</button>'
            f'<div class="popover popover-{e_placement}">'
            f'{title_html}'
            f'<div class="popover-content">{content}</div>'
            f'</div>'
            f'</div>'
        )


# ---------------------------------------------------------------------------
# 35. Rating / Stars
# ---------------------------------------------------------------------------

@register.simple_tag
def rating(value=0, max_stars=5, readonly=False, event="set_rating", size="md"):
    """Render a star rating component."""
    try:
        value = float(value)
        max_stars = int(max_stars)
    except (ValueError, TypeError):
        value = 0
        max_stars = 5
    if isinstance(readonly, str):
        readonly = readonly.lower() not in ("false", "0", "")

    e_event = conditional_escape(event)
    size_cls = f" rating-{conditional_escape(size)}" if size != "md" else ""
    parts = []

    for i in range(1, max_stars + 1):
        if i <= value:
            star_cls = "rating-star rating-star-full"
        elif i - 0.5 <= value:
            star_cls = "rating-star rating-star-half"
        else:
            star_cls = "rating-star rating-star-empty"

        if readonly:
            parts.append(f'<span class="{star_cls}">★</span>')
        else:
            parts.append(
                f'<button class="{star_cls}" dj-click="{e_event}" '
                f'data-value="{i}" title="{i} star{"s" if i > 1 else ""}">★</button>'
            )

    return mark_safe(f'<div class="rating{size_cls}">{"".join(parts)}</div>')


# ---------------------------------------------------------------------------
# 36. Copy Button
# ---------------------------------------------------------------------------

@register.simple_tag
def copy_button(text="", label="Copy", copied_label="Copied!", variant="outline", size="sm"):
    """Render a copy-to-clipboard button."""
    e_text = conditional_escape(text)
    e_label = conditional_escape(label)
    e_copied = conditional_escape(copied_label)
    e_variant = conditional_escape(variant)
    e_size = conditional_escape(size)

    return mark_safe(
        f'<button class="btn btn-{e_variant} btn-{e_size} copy-btn" '
        f'data-copy-text="{e_text}" '
        f'data-copied-label="{e_copied}" '
        f'onclick="(function(btn){{var t=btn.getAttribute(\'data-copy-text\');'
        f'navigator.clipboard&&navigator.clipboard.writeText(t).then(function(){{'
        f'var orig=btn.textContent;btn.textContent=btn.getAttribute(\'data-copied-label\');'
        f'setTimeout(function(){{btn.textContent=orig;}},2000);}});}})(this)">'
        f'{e_label}</button>'
    )


# ---------------------------------------------------------------------------
# 37. Kbd / Keyboard Shortcut
# ---------------------------------------------------------------------------

@register.simple_tag
def kbd(*keys):
    """Render keyboard shortcut keys.

    Usage: {% kbd "Ctrl" "K" %} → <kbd>Ctrl</kbd>+<kbd>K</kbd>
    """
    if not keys:
        return mark_safe("")
    parts = [f'<kbd class="kbd">{conditional_escape(k)}</kbd>' for k in keys]
    return mark_safe('<span class="kbd-group">' + '<span class="kbd-sep">+</span>'.join(parts) + '</span>')


# ---------------------------------------------------------------------------
# 38. Collapsible
# ---------------------------------------------------------------------------

@register.tag("collapsible")
def do_collapsible(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endcollapsible",))
    parser.delete_first_token()
    return CollapsibleNode(nodelist, kwargs)


class CollapsibleNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        trigger = kw.get("trigger", "Toggle")
        open_ = kw.get("open", False)
        if isinstance(open_, str):
            open_ = open_.lower() not in ("false", "0", "")
        event = kw.get("event", "toggle_collapsible")
        uid = f"coll-{uuid.uuid4().hex[:6]}"

        e_uid = conditional_escape(uid)
        e_trigger = conditional_escape(trigger)
        e_event = conditional_escape(event)
        open_cls = " collapsible-open" if open_ else ""
        content = self.nodelist.render(context)

        return mark_safe(
            f'<div class="collapsible{open_cls}" id="{e_uid}">'
            f'<button class="collapsible-trigger" '
            f'onclick="(function(el){{el.closest(\'.collapsible\').classList.toggle(\'collapsible-open\');}})(this)"'
            f' dj-click="{e_event}">'
            f'<span class="collapsible-label">{e_trigger}</span>'
            f'<span class="collapsible-icon">▾</span>'
            f'</button>'
            f'<div class="collapsible-content">{content}</div>'
            f'</div>'
        )


# ---------------------------------------------------------------------------
# 39. Sheet / Drawer
# ---------------------------------------------------------------------------

@register.tag("sheet")
def do_sheet(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endsheet",))
    parser.delete_first_token()
    return SheetNode(nodelist, kwargs)


class SheetNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        open_ = kw.get("open", False)
        if isinstance(open_, str):
            open_ = open_.lower() not in ("false", "0", "")
        side = kw.get("side", "right")
        title = kw.get("title", "")
        close_event = kw.get("close_event", "close_sheet")

        e_side = conditional_escape(side)
        e_title = conditional_escape(title)
        e_close = conditional_escape(close_event)
        open_attr = ' data-open="true"' if open_ else ""
        content = self.nodelist.render(context)

        title_html = (
            f'<div class="sheet-header">'
            f'<h3 class="sheet-title">{e_title}</h3>'
            f'<button class="sheet-close" dj-click="{e_close}">&times;</button>'
            f'</div>'
            if title else
            f'<div class="sheet-header-close">'
            f'<button class="sheet-close" dj-click="{e_close}">&times;</button>'
            f'</div>'
        )

        return mark_safe(
            f'<div class="sheet-overlay" dj-click="{e_close}"{open_attr}></div>'
            f'<div class="sheet sheet-{e_side}"{open_attr}>'
            f'{title_html}'
            f'<div class="sheet-body">{content}</div>'
            f'</div>'
        )


# ---------------------------------------------------------------------------
# 40. Notification Center
# ---------------------------------------------------------------------------

@register.simple_tag
def notification_center(notifications=None, unread_count=0,
                        open_event="toggle_notifications",
                        mark_read_event="mark_notification_read",
                        clear_event="clear_notifications"):
    """Render a notification bell with dropdown list."""
    if notifications is None:
        notifications = []
    try:
        unread_count = int(unread_count)
    except (ValueError, TypeError):
        unread_count = 0

    e_open = conditional_escape(open_event)
    e_clear = conditional_escape(clear_event)
    e_read = conditional_escape(mark_read_event)

    badge_html = (
        f'<span class="notif-badge">{unread_count}</span>'
        if unread_count > 0 else ""
    )

    items_html = ""
    for n in notifications:
        if not isinstance(n, dict):
            continue
        nid = conditional_escape(str(n.get("id", "")))
        msg = conditional_escape(str(n.get("message", n.get("msg", ""))))
        time_ = conditional_escape(str(n.get("time", "")))
        unread = n.get("unread", False)
        unread_cls = " notif-item-unread" if unread else ""
        time_html = f'<span class="notif-item-time">{time_}</span>' if time_ else ""
        items_html += (
            f'<div class="notif-item{unread_cls}" '
            f'dj-click="{e_read}" data-value="{nid}">'
            f'<div class="notif-item-msg">{msg}</div>'
            f'{time_html}'
            f'</div>'
        )

    if not items_html:
        items_html = '<div class="notif-empty">No notifications</div>'

    footer_html = (
        f'<div class="notif-footer">'
        f'<button class="btn btn-ghost btn-sm" dj-click="{e_clear}">Clear all</button>'
        f'</div>'
        if notifications else ""
    )

    return mark_safe(
        f'<div class="notif-center">'
        f'<button class="notif-trigger" dj-click="{e_open}">'
        f'<span class="notif-bell">&#128276;</span>'
        f'{badge_html}'
        f'</button>'
        f'<div class="notif-dropdown">'
        f'<div class="notif-header"><span class="notif-title">Notifications</span></div>'
        f'<div class="notif-list">{items_html}</div>'
        f'{footer_html}'
        f'</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 41. Gauge / Donut Chart
# ---------------------------------------------------------------------------

@register.simple_tag
def gauge(value=0, max_value=100, label="", color="primary", size="md", show_value=True):
    """Render an SVG donut/gauge chart."""
    try:
        value = float(value)
        max_value = float(max_value) or 100
    except (ValueError, TypeError):
        value = 0
        max_value = 100
    if isinstance(show_value, str):
        show_value = show_value.lower() not in ("false", "0", "")

    pct = min(max(value / max_value, 0), 1)
    sizes = {"sm": 64, "md": 96, "lg": 128}
    px = sizes.get(str(size), 96)
    r = (px - 12) / 2
    circ = 2 * 3.14159 * r
    dash = pct * circ
    gap = circ - dash
    cx = cy = px / 2

    e_color = conditional_escape(color)
    e_label = conditional_escape(label)
    display_val = f"{int(pct * 100)}%"
    val_html = (
        f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" '
        f'class="gauge-value-text" font-size="{px * 0.18:.0f}">{display_val}</text>'
        if show_value else ""
    )
    label_html = (
        f'<div class="gauge-label">{e_label}</div>' if e_label else ""
    )

    return mark_safe(
        f'<div class="gauge gauge-{e_color}" style="width:{px}px;height:{px}px;">'
        f'<svg width="{px}" height="{px}" viewBox="0 0 {px} {px}">'
        f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" class="gauge-track" '
        f'stroke-width="8" fill="none"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" class="gauge-fill gauge-fill-{e_color}" '
        f'stroke-width="8" fill="none" '
        f'stroke-dasharray="{dash:.1f} {gap:.1f}" '
        f'stroke-linecap="round" transform="rotate(-90 {cx} {cy})"/>'
        f'{val_html}'
        f'</svg>'
        f'{label_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 42. Image Carousel
# ---------------------------------------------------------------------------

@register.simple_tag
def carousel(images=None, active=0, prev_event="carousel_prev",
             next_event="carousel_next", go_event="carousel_go"):
    """Render an image carousel / slideshow."""
    if images is None:
        images = []
    try:
        active = int(active)
    except (ValueError, TypeError):
        active = 0

    if not images:
        return mark_safe('<div class="carousel carousel-empty"></div>')

    e_prev = conditional_escape(prev_event)
    e_next = conditional_escape(next_event)
    e_go = conditional_escape(go_event)

    slides = ""
    dots = ""
    for i, img in enumerate(images):
        if isinstance(img, dict):
            src = conditional_escape(str(img.get("src", img.get("url", ""))))
            alt = conditional_escape(str(img.get("alt", f"Slide {i + 1}")))
            caption = img.get("caption", "")
        else:
            src = conditional_escape(str(img))
            alt = f"Slide {i + 1}"
            caption = ""

        active_cls = " carousel-slide-active" if i == active else ""
        caption_html = (
            f'<div class="carousel-caption">{conditional_escape(caption)}</div>'
            if caption else ""
        )
        slides += (
            f'<div class="carousel-slide{active_cls}">'
            f'<img src="{src}" alt="{alt}" class="carousel-img">'
            f'{caption_html}'
            f'</div>'
        )
        dot_cls = " carousel-dot-active" if i == active else ""
        dots += (
            f'<button class="carousel-dot{dot_cls}" '
            f'dj-click="{e_go}" data-value="{i}"></button>'
        )

    total = len(images)
    counter_html = (
        f'<div class="carousel-counter">{active + 1} / {total}</div>'
        if total > 1 else ""
    )

    return mark_safe(
        f'<div class="carousel">'
        f'<div class="carousel-track">{slides}</div>'
        f'<button class="carousel-btn carousel-btn-prev" dj-click="{e_prev}">&#8249;</button>'
        f'<button class="carousel-btn carousel-btn-next" dj-click="{e_next}">&#8250;</button>'
        f'<div class="carousel-dots">{dots}</div>'
        f'{counter_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 43. Tree View
# ---------------------------------------------------------------------------

@register.simple_tag
def tree_view(nodes=None, expand_event="tree_expand", select_event="tree_select",
              selected=""):
    """Render an expandable tree view.

    Args:
        nodes: list of dicts:
            {"id": "n1", "label": "Root", "expanded": True,
             "children": [{"id": "n1a", "label": "Child"}]}
        expand_event: dj-click event fired with node id when expanding
        select_event: dj-click event fired with node id when selected
        selected: currently selected node id
    """
    if nodes is None:
        return mark_safe('<div class="tree"></div>')

    e_expand = conditional_escape(expand_event)
    e_select = conditional_escape(select_event)
    e_selected = conditional_escape(selected)

    def render_node(node, depth=0):
        if not isinstance(node, dict):
            return ""
        nid = conditional_escape(str(node.get("id", "")))
        label = conditional_escape(str(node.get("label", "")))
        children = node.get("children", [])
        expanded = node.get("expanded", False)
        has_children = bool(children)

        sel_cls = " tree-node-selected" if str(node.get("id", "")) == str(selected) else ""
        exp_cls = " tree-node-expanded" if expanded else ""
        has_cls = " tree-node-has-children" if has_children else " tree-node-leaf"
        indent = depth * 1.25

        toggle_icon = "▾" if expanded else "▸"
        toggle_html = (
            f'<button class="tree-toggle" dj-click="{e_expand}" data-value="{nid}">'
            f'{toggle_icon}</button>'
            if has_children else
            f'<span class="tree-toggle-placeholder"></span>'
        )

        children_html = ""
        if has_children and expanded:
            children_html = (
                f'<div class="tree-children">'
                + "".join(render_node(c, depth + 1) for c in children)
                + "</div>"
            )

        return (
            f'<div class="tree-node{sel_cls}{exp_cls}{has_cls}" '
            f'style="padding-left:{indent}rem">'
            f'<div class="tree-node-row">'
            f'{toggle_html}'
            f'<button class="tree-node-label" dj-click="{e_select}" data-value="{nid}">'
            f'{label}</button>'
            f'</div>'
            f'{children_html}'
            f'</div>'
        )

    html = "".join(render_node(n) for n in nodes)
    return mark_safe(f'<div class="tree">{html}</div>')


# ---------------------------------------------------------------------------
# 44. Color Picker (swatches + hex input)
# ---------------------------------------------------------------------------

@register.simple_tag
def color_picker(name="", value="#3B82F6", event="", label="",
                 swatches=None):
    """Render a color picker with preset swatches and a hex input."""
    if swatches is None:
        swatches = [
            "#EF4444", "#F97316", "#EAB308", "#22C55E",
            "#3B82F6", "#8B5CF6", "#EC4899", "#6B7280",
        ]
    e_name = conditional_escape(name)
    e_value = conditional_escape(value)
    e_event = conditional_escape(event or name)
    e_label = conditional_escape(label)

    label_html = f'<label class="form-label">{e_label}</label>' if label else ""

    swatch_html = ""
    for sw in swatches:
        e_sw = conditional_escape(sw)
        active_cls = " color-swatch-active" if sw == value else ""
        swatch_html += (
            f'<button class="color-swatch{active_cls}" '
            f'style="background:{e_sw}" title="{e_sw}" '
            f'dj-click="{e_event}" data-value="{e_sw}"></button>'
        )

    return mark_safe(
        f'<div class="form-group">'
        f'{label_html}'
        f'<div class="color-picker">'
        f'<div class="color-preview" style="background:{e_value}"></div>'
        f'<div class="color-swatches">{swatch_html}</div>'
        f'<input class="color-hex-input form-input" type="text" '
        f'name="{e_name}" value="{e_value}" placeholder="#000000" '
        f'maxlength="7" dj-input="{e_event}">'
        f'</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 45. Command Palette
# ---------------------------------------------------------------------------

@register.tag("command_palette")
def do_command_palette(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endcommand_palette",))
    parser.delete_first_token()
    return CommandPaletteNode(nodelist, kwargs)


class CommandPaletteNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        open_ = kw.get("open", False)
        if isinstance(open_, str):
            open_ = open_.lower() not in ("false", "0", "")
        search_event = kw.get("search_event", "palette_search")
        close_event = kw.get("close_event", "close_palette")
        placeholder = kw.get("placeholder", "Search commands…")

        e_search = conditional_escape(search_event)
        e_close = conditional_escape(close_event)
        e_placeholder = conditional_escape(placeholder)
        open_attr = ' data-open="true"' if open_ else ""
        content = self.nodelist.render(context)

        return mark_safe(
            f'<div class="palette-overlay" dj-click="{e_close}"{open_attr}></div>'
            f'<div class="palette"{open_attr}>'
            f'<div class="palette-search">'
            f'<span class="palette-search-icon">⌕</span>'
            f'<input class="palette-input" type="text" placeholder="{e_placeholder}" '
            f'dj-input="{e_search}" autofocus>'
            f'<button class="palette-close" dj-click="{e_close}">Esc</button>'
            f'</div>'
            f'<div class="palette-results">{content}</div>'
            f'</div>'
        )


@register.simple_tag
def palette_item(label="", shortcut="", description="", event="", icon=""):
    """Render a single command palette result item."""
    e_label = conditional_escape(label)
    e_event = conditional_escape(event)
    e_desc = conditional_escape(description)
    e_icon = conditional_escape(icon)

    icon_html = f'<span class="palette-item-icon">{e_icon}</span>' if icon else ""
    shortcut_html = f'<kbd class="kbd">{conditional_escape(shortcut)}</kbd>' if shortcut else ""
    desc_html = f'<span class="palette-item-desc">{e_desc}</span>' if description else ""

    return mark_safe(
        f'<div class="palette-item" dj-click="{e_event}">'
        f'{icon_html}'
        f'<div class="palette-item-body">'
        f'<span class="palette-item-label">{e_label}</span>'
        f'{desc_html}'
        f'</div>'
        f'{shortcut_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 46. Context Menu
# ---------------------------------------------------------------------------

@register.tag("context_menu")
def do_context_menu(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endcontext_menu",))
    parser.delete_first_token()
    return ContextMenuNode(nodelist, kwargs)


class ContextMenuNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        label = kw.get("label", "Right-click area")
        uid = f"ctx-{uuid.uuid4().hex[:6]}"

        e_uid = conditional_escape(uid)
        e_label = conditional_escape(label)
        content = self.nodelist.render(context)

        return mark_safe(
            f'<div class="ctx-wrapper" id="{e_uid}" '
            f'oncontextmenu="(function(e,el){{e.preventDefault();'
            f'document.querySelectorAll(\'.ctx-menu[data-open]\').forEach(function(m){{delete m.dataset.open;}});'
            f'var m=el.querySelector(\'.ctx-menu\');'
            f'm.style.left=e.offsetX+\'px\';m.style.top=e.offsetY+\'px\';'
            f'm.dataset.open=\'1\';'
            f'document.addEventListener(\'click\',function h(){{delete m.dataset.open;document.removeEventListener(\'click\',h);}},{{once:true}});'
            f'}})(event,this)">'
            f'<div class="ctx-trigger">{e_label}</div>'
            f'<div class="ctx-menu">{content}</div>'
            f'</div>'
        )


@register.simple_tag
def context_menu_item(label="", event="", icon="", danger=False, divider=False):
    """Render a context menu item."""
    if divider:
        return mark_safe('<div class="ctx-divider"></div>')

    e_label = conditional_escape(label)
    e_event = conditional_escape(event)
    e_icon = conditional_escape(icon)
    danger_cls = " ctx-item-danger" if danger else ""
    icon_html = f'<span class="ctx-item-icon">{e_icon}</span>' if icon else ""

    return mark_safe(
        f'<div class="ctx-item{danger_cls}" dj-click="{e_event}">'
        f'{icon_html}{e_label}'
        f'</div>'
    )


# ===========================================================================
# TIER 3 REMAINING — v1.3 COMPONENTS
# ===========================================================================

# ---------------------------------------------------------------------------
# 47. Date Picker (server-rendered calendar)
# ---------------------------------------------------------------------------

import calendar as _calendar


@register.simple_tag
def date_picker(year=None, month=None, selected="", prev_event="date_prev_month",
                next_event="date_next_month", select_event="date_select",
                name="date", label="", required=False, error="", helper="",
                range=False, range_start="", range_end=""):
    """Render a server-driven calendar date picker.

    The server owns year/month navigation state. On each prev/next click,
    the view re-renders the calendar for the new month.

    Args:
        range: when True, enables date range selection mode.
        range_start: start date of the range (YYYY-MM-DD).
        range_end: end date of the range (YYYY-MM-DD).
    """
    import datetime
    if isinstance(range, str):
        range = range.lower() not in ("false", "0", "")

    try:
        today = datetime.date.today()
        year = int(year) if year else today.year
        month = int(month) if month else today.month
        today_str = today.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        import datetime
        today = datetime.date.today()
        year, month = today.year, today.month
        today_str = today.strftime("%Y-%m-%d")

    e_prev = conditional_escape(prev_event)
    e_next = conditional_escape(next_event)
    e_select = conditional_escape(select_event)
    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_selected = conditional_escape(selected)
    e_error = conditional_escape(error)
    e_helper = conditional_escape(helper)
    e_range_start = conditional_escape(range_start)
    e_range_end = conditional_escape(range_end)

    if isinstance(required, str):
        required = required.lower() not in ("false", "0", "")

    month_name = _calendar.month_name[month]
    weekdays = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

    # Build day grid
    cal = _calendar.monthcalendar(year, month)
    header_cells = "".join(f'<div class="dp-weekday">{d}</div>' for d in weekdays)

    day_cells = ""
    for week in cal:
        for day in week:
            if day == 0:
                day_cells += '<div class="dp-day dp-day-empty"></div>'
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                cls = "dp-day"
                if date_str == today_str:
                    cls += " dp-day-today"
                if range:
                    if range_start and date_str == range_start:
                        cls += " dp-day-range-start"
                    if range_end and date_str == range_end:
                        cls += " dp-day-range-end"
                    if range_start and range_end and range_start < date_str < range_end:
                        cls += " dp-day-in-range"
                else:
                    if date_str == selected:
                        cls += " dp-day-selected"
                day_cells += (
                    f'<button class="{cls}" dj-click="{e_select}" '
                    f'data-value="{date_str}">{day}</button>'
                )

    label_html = f'<label class="form-label">{e_label}</label>' if label else ""
    required_html = ' <span class="form-required">*</span>' if required else ""
    error_html = f'<span class="form-error-message">{e_error}</span>' if error else ""
    helper_html = f'<span class="form-helper">{e_helper}</span>' if helper else ""

    if range:
        if range_start and range_end:
            selected_html = (
                f'<div class="dp-selected-value">'
                f'{e_range_start} &ndash; {e_range_end}</div>'
            )
        elif range_start:
            selected_html = (
                f'<div class="dp-selected-value">{e_range_start} &ndash; ...</div>'
            )
        else:
            selected_html = ""
        hidden_html = (
            f'<input type="hidden" name="{e_name}_start" value="{e_range_start}">'
            f'<input type="hidden" name="{e_name}_end" value="{e_range_end}">'
        )
    else:
        selected_html = (
            f'<div class="dp-selected-value">{e_selected}</div>'
            if selected else ""
        )
        hidden_html = f'<input type="hidden" name="{e_name}" value="{e_selected}">'

    return mark_safe(
        f'<div class="form-group">'
        f'{label_html}{required_html}'
        f'<div class="date-picker">'
        f'<div class="dp-header">'
        f'<button class="dp-nav-btn" dj-click="{e_prev}" title="Previous month">&#8249;</button>'
        f'<span class="dp-month-label">{month_name} {year}</span>'
        f'<button class="dp-nav-btn" dj-click="{e_next}" title="Next month">&#8250;</button>'
        f'</div>'
        f'<div class="dp-grid">'
        f'{header_cells}'
        f'{day_cells}'
        f'</div>'
        f'{hidden_html}'
        f'{selected_html}'
        f'</div>'
        f'{error_html}{helper_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 48. File Dropzone
# ---------------------------------------------------------------------------

@register.simple_tag
def file_dropzone(name="file", label="", accept="", multiple=False,
                  max_size_mb=10, event="file_selected", helper=""):
    """Render a drag-and-drop file upload zone."""
    if isinstance(multiple, str):
        multiple = multiple.lower() not in ("false", "0", "")

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_accept = conditional_escape(accept)
    e_event = conditional_escape(event)
    e_helper = conditional_escape(helper)
    e_max = conditional_escape(str(max_size_mb))

    multiple_attr = " multiple" if multiple else ""
    accept_attr = f' accept="{e_accept}"' if accept else ""
    label_html = f'<label class="form-label">{e_label}</label>' if label else ""
    helper_html = f'<span class="form-helper">{e_helper}</span>' if helper else ""

    js_id = f"dz-{name}"

    return mark_safe(
        f'{label_html}'
        f'<div class="dropzone" id="{js_id}" '
        f'ondragover="event.preventDefault();this.classList.add(\'dropzone-over\')" '
        f'ondragleave="this.classList.remove(\'dropzone-over\')" '
        f'ondrop="(function(e,el){{e.preventDefault();el.classList.remove(\'dropzone-over\');'
        f'var f=e.dataTransfer.files;if(f.length){{var inp=el.querySelector(\'input[type=file]\');'
        f'try{{var dt=new DataTransfer();for(var i=0;i<f.length;i++)dt.items.add(f[i]);'
        f'inp.files=dt.files;}}catch(ex){{}}el.querySelector(\'.dz-file-count\').textContent='
        f'f.length+\' file\'+(f.length>1?\'s\':\'\')+\' selected\';'
        f'el.classList.add(\'dropzone-has-file\');}}}})( event,this)">'
        f'<input type="file" name="{e_name}" class="dropzone-input" '
        f'{accept_attr}{multiple_attr} '
        f'onchange="(function(el){{var f=el.files;var c=el.closest(\'.dropzone\');'
        f'c.querySelector(\'.dz-file-count\').textContent=f.length+\' file\'+(f.length>1?\'s\':\'\')+\' selected\';'
        f'c.classList.add(\'dropzone-has-file\');}})( this)">'
        f'<div class="dz-icon">&#128196;</div>'
        f'<div class="dz-text">Drag files here or <span class="dz-browse">browse</span></div>'
        f'<div class="dz-hint">Max {e_max} MB{(", accepts " + e_accept) if accept else ""}</div>'
        f'<div class="dz-file-count"></div>'
        f'</div>'
        f'{helper_html}'
    )


# ---------------------------------------------------------------------------
# 49. Split Pane
# ---------------------------------------------------------------------------

@register.tag("split_pane")
def do_split_pane(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    # parse two children: {% pane %}...{% endpane %}{% pane %}...{% endpane %}
    pane1 = parser.parse(("pane",))
    parser.delete_first_token()  # consume {% pane %}
    pane2 = parser.parse(("endsplit_pane",))
    parser.delete_first_token()  # consume {% endsplit_pane %}
    return SplitPaneNode(pane1, pane2, kwargs)


class SplitPaneNode(template.Node):
    def __init__(self, pane1, pane2, kwargs):
        self.pane1 = pane1
        self.pane2 = pane2
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        direction = kw.get("direction", "horizontal")
        initial = kw.get("initial", "50")
        uid = f"sp-{uuid.uuid4().hex[:6]}"

        e_uid = conditional_escape(uid)
        e_dir = conditional_escape(direction)
        e_init = conditional_escape(str(initial))

        content1 = self.pane1.render(context)
        content2 = self.pane2.render(context)

        flex_dir = "row" if direction == "horizontal" else "column"
        size_prop = "width" if direction == "horizontal" else "height"

        js = (
            f"(function(){{var sp=document.getElementById('{uid}');"
            f"if(!sp)return;"
            f"var h=sp.querySelector('.sp-handle');"
            f"var p1=sp.querySelector('.sp-pane-1');"
            f"var dragging=false;"
            f"h.addEventListener('mousedown',function(e){{dragging=true;e.preventDefault();}});"
            f"document.addEventListener('mousemove',function(e){{"
            f"if(!dragging)return;"
            f"var r=sp.getBoundingClientRect();"
            f"var pct={'((e.clientX-r.left)/r.width*100)' if direction == 'horizontal' else '((e.clientY-r.top)/r.height*100)'};"
            f"pct=Math.max(10,Math.min(90,pct));"
            f"p1.style.{size_prop}=pct+'%';}});"
            f"document.addEventListener('mouseup',function(){{dragging=false;}});"
            f"}})();"
        )

        return mark_safe(
            f'<div class="split-pane split-pane-{e_dir}" id="{e_uid}">'
            f'<div class="sp-pane sp-pane-1" style="{size_prop}:{e_init}%">{content1}</div>'
            f'<div class="sp-handle sp-handle-{e_dir}"></div>'
            f'<div class="sp-pane sp-pane-2" style="flex:1">{content2}</div>'
            f'</div>'
            f'<script>{js}</script>'
        )


# ---------------------------------------------------------------------------
# 50. Table of Contents
# ---------------------------------------------------------------------------

@register.simple_tag
def table_of_contents(items=None, title="Contents", active="", event=""):
    """Render a table of contents from a list of items.

    Args:
        items: list of dicts {"id": "section-1", "label": "Introduction", "level": 1}
        title: TOC heading
        active: currently active section id (highlight)
        event: dj-click event when an item is clicked (sends id as data-value)
    """
    if not items:
        return mark_safe("")

    e_title = conditional_escape(title)
    e_active = conditional_escape(active)
    e_event = conditional_escape(event) if event else ""

    def render_item(item):
        if not isinstance(item, dict):
            return ""
        iid = conditional_escape(str(item.get("id", "")))
        lbl = conditional_escape(str(item.get("label", "")))
        level = int(item.get("level", 1))
        indent = (level - 1) * 1.0
        active_cls = " toc-item-active" if str(item.get("id", "")) == active else ""
        event_attr = f' dj-click="{e_event}" data-value="{iid}"' if e_event else ""
        return (
            f'<a href="#{iid}" class="toc-item toc-level-{level}{active_cls}" '
            f'style="padding-left:{indent + 0.75}rem"{event_attr}>{lbl}</a>'
        )

    items_html = "".join(render_item(i) for i in items)
    title_html = f'<div class="toc-title">{e_title}</div>' if title else ""

    return mark_safe(
        f'<nav class="toc">'
        f'{title_html}'
        f'<div class="toc-list">{items_html}</div>'
        f'</nav>'
    )


# ---------------------------------------------------------------------------
# 51. Virtualized List (server-paginated "virtual" list)
# ---------------------------------------------------------------------------

@register.simple_tag
def virtual_list(items=None, total=0, page=1, page_size=20,
                 load_more_event="load_more", item_height=48):
    """Render a paginated list optimised for large datasets.

    Renders one page of items in a scrollable container. A 'Load more'
    sentinel triggers the server to extend the list.
    """
    if items is None:
        items = []
    try:
        total = int(total)
        page = int(page)
        page_size = int(page_size)
        item_height = int(item_height)
    except (ValueError, TypeError):
        total = len(items)
        page = 1
        page_size = 20
        item_height = 48

    e_load = conditional_escape(load_more_event)
    has_more = (page * page_size) < total

    rows = ""
    for item in items:
        if isinstance(item, dict):
            label = conditional_escape(str(item.get("label", item.get("title", str(item)))))
            sub = conditional_escape(str(item.get("sub", item.get("subtitle", ""))))
            sub_html = f'<span class="vl-item-sub">{sub}</span>' if sub else ""
            rows += (
                f'<div class="vl-item" style="height:{item_height}px">'
                f'<span class="vl-item-label">{label}</span>'
                f'{sub_html}'
                f'</div>'
            )
        else:
            rows += (
                f'<div class="vl-item" style="height:{item_height}px">'
                f'<span class="vl-item-label">{conditional_escape(str(item))}</span>'
                f'</div>'
            )

    shown = min(len(items), page * page_size)
    load_more_html = (
        f'<div class="vl-load-more">'
        f'<button class="btn btn-ghost btn-sm" dj-click="{e_load}">'
        f'Load more ({total - shown} remaining)'
        f'</button>'
        f'</div>'
        if has_more else ""
    )

    return mark_safe(
        f'<div class="virtual-list">'
        f'<div class="vl-info">Showing {shown} of {total} items</div>'
        f'<div class="vl-scroll">'
        f'{rows}'
        f'{load_more_html}'
        f'</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# 52. Kanban Board
# ---------------------------------------------------------------------------

@register.simple_tag
def kanban_board(columns=None, move_event="kanban_move", add_card_event="kanban_add_card",
                 add_col_event="kanban_add_column"):
    """Render a Kanban board.

    Args:
        columns: list of dicts:
            {"id": "todo", "title": "To Do", "color": "#6366F1",
             "cards": [{"id": "c1", "title": "Task A", "label": "bug"}]}
        move_event: event fired on drag-drop with JSON payload {card_id, from_col, to_col}
        add_card_event: event fired when adding a card, passes column id
    """
    if not columns:
        return mark_safe('<div class="kanban"></div>')

    e_move = conditional_escape(move_event)
    e_add_card = conditional_escape(add_card_event)

    cols_html = ""
    for col in columns:
        if not isinstance(col, dict):
            continue
        col_id = conditional_escape(str(col.get("id", "")))
        col_title = conditional_escape(str(col.get("title", "")))
        col_color = conditional_escape(str(col.get("color", "#6366F1")))
        cards = col.get("cards", [])

        cards_html = ""
        for card in cards:
            if not isinstance(card, dict):
                continue
            card_id = conditional_escape(str(card.get("id", "")))
            card_title = conditional_escape(str(card.get("title", "")))
            card_label = card.get("label", "")
            card_sub = card.get("sub", "")
            label_html = (
                f'<span class="kanban-card-label kanban-label-{conditional_escape(card_label)}">'
                f'{conditional_escape(card_label)}</span>'
                if card_label else ""
            )
            sub_html = (
                f'<div class="kanban-card-sub">{conditional_escape(card_sub)}</div>'
                if card_sub else ""
            )
            cards_html += (
                f'<div class="kanban-card" draggable="true" '
                f'data-card-id="{card_id}" data-col-id="{col_id}" '
                f'ondragstart="(function(e,el){{e.dataTransfer.setData(\'card\',el.dataset.cardId);'
                f'e.dataTransfer.setData(\'from\',el.dataset.colId);el.classList.add(\'dragging\');}})( event,this)" '
                f'ondragend="this.classList.remove(\'dragging\')">'
                f'<div class="kanban-card-title">{card_title}</div>'
                f'{sub_html}'
                f'{label_html}'
                f'</div>'
            )

        add_btn = (
            f'<button class="kanban-add-card" dj-click="{e_add_card}" '
            f'data-value="{col_id}">+ Add card</button>'
        )

        cols_html += (
            f'<div class="kanban-col" '
            f'data-col-id="{col_id}" '
            f'ondragover="event.preventDefault();this.classList.add(\'kanban-col-over\')" '
            f'ondragleave="this.classList.remove(\'kanban-col-over\')" '
            f'ondrop="(function(e,el){{e.preventDefault();el.classList.remove(\'kanban-col-over\');'
            f'var cid=e.dataTransfer.getData(\'card\');'
            f'var from=e.dataTransfer.getData(\'from\');'
            f'var to=el.dataset.colId;'
            f'if(from!==to){{window.djust&&window.djust.handleEvent(\'{e_move}\',{{card_id:cid,from_col:from,to_col:to}});}}'
            f'}})( event,this)">'
            f'<div class="kanban-col-header" style="border-top-color:{col_color}">'
            f'<span class="kanban-col-title">{col_title}</span>'
            f'<span class="kanban-col-count">{len(cards)}</span>'
            f'</div>'
            f'<div class="kanban-cards">{cards_html}</div>'
            f'{add_btn}'
            f'</div>'
        )

    return mark_safe(f'<div class="kanban">{cols_html}</div>')


# ---------------------------------------------------------------------------
# 53. Rich Text Editor
# ---------------------------------------------------------------------------

@register.simple_tag
def rich_text_editor(name="content", value="", event="update_content",
                     placeholder="Start typing…", height="200px",
                     label="", required=False):
    """Render a basic rich text editor (contenteditable + toolbar).

    Toolbar: Bold, Italic, Underline, Strikethrough, | H2, H3, | UL, OL, | Link, Quote, Code
    The content is synced to the server via dj-input on blur.
    """
    if isinstance(required, str):
        required = required.lower() not in ("false", "0", "")

    e_name = conditional_escape(name)
    e_value = value  # Already HTML — rendered as-is (trust server content)
    e_event = conditional_escape(event)
    e_placeholder = conditional_escape(placeholder)
    e_height = conditional_escape(height)
    e_label = conditional_escape(label)

    uid = f"rte-{uuid.uuid4().hex[:6]}"
    e_uid = conditional_escape(uid)

    label_html = f'<label class="form-label">{e_label}</label>' if label else ""
    req_html = ' <span class="form-required">*</span>' if required else ""

    buttons = [
        ("bold", "B", "bold"),
        ("italic", "I", "italic"),
        ("underline", "U", "underline"),
        ("strikeThrough", "S̶", "strikeThrough"),
        ("|", "", ""),
        ("formatBlock", "H2", "h2"),
        ("formatBlock", "H3", "h3"),
        ("|", "", ""),
        ("insertUnorderedList", "•", "insertUnorderedList"),
        ("insertOrderedList", "1.", "insertOrderedList"),
        ("|", "", ""),
        ("formatBlock", "❝", "blockquote"),
        ("formatBlock", "</>", "pre"),
    ]

    toolbar_html = ""
    for cmd, lbl, arg in buttons:
        if cmd == "|":
            toolbar_html += '<div class="rte-sep"></div>'
        else:
            e_cmd = conditional_escape(cmd)
            e_arg = conditional_escape(arg)
            e_lbl = conditional_escape(lbl)
            toolbar_html += (
                f'<button class="rte-btn" type="button" title="{e_cmd}" '
                f'onmousedown="event.preventDefault();'
                f'document.execCommand(\'{e_cmd}\',false,{repr(arg)});">'
                f'{e_lbl}</button>'
            )

    sync_js = (
        f"var ed=document.getElementById('{uid}-editor');"
        f"var hid=document.getElementById('{uid}-hidden');"
        f"if(ed&&hid){{hid.value=ed.innerHTML;}}"
    )

    return mark_safe(
        f'<div class="form-group">'
        f'{label_html}{req_html}'
        f'<div class="rte" id="{e_uid}">'
        f'<div class="rte-toolbar">{toolbar_html}</div>'
        f'<div class="rte-editor" id="{e_uid}-editor" '
        f'contenteditable="true" '
        f'style="min-height:{e_height}" '
        f'data-placeholder="{e_placeholder}" '
        f'dj-input="{e_event}" '
        f'oninput="(function(el){{var h=document.getElementById(\'{e_uid}-hidden\');'
        f'if(h)h.value=el.innerHTML;}})(this)">'
        f'{e_value}'
        f'</div>'
        f'<input type="hidden" id="{e_uid}-hidden" name="{e_name}" value="">'
        f'</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Multi-select (#53)
# ---------------------------------------------------------------------------

@register.simple_tag
def multi_select(name="", label="", options=None, selected=None,
                 event="", placeholder="Search...", disabled=False):
    """Render a multi-select checkbox list with search filtering and tag output.

    Args:
        name: form field name
        label: label text above the control
        options: list of dicts {"value":..., "label":...} or list of 2-tuples
        selected: list of currently selected values
        event: dj-change event name
        placeholder: search input placeholder
        disabled: disables the control
    """
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    if options is None:
        options = []
    if selected is None:
        selected = []
    # Normalise selected to list of strings
    selected = [str(s) for s in selected]

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_placeholder = conditional_escape(placeholder)
    dj_event = conditional_escape(event or name)
    disabled_attr = " disabled" if disabled else ""

    uid = f"ms-{uuid.uuid4().hex[:6]}"

    def _opt_pair(opt):
        if isinstance(opt, dict):
            return str(opt.get("value", "")), str(opt.get("label", ""))
        if isinstance(opt, (list, tuple)) and len(opt) >= 2:
            return str(opt[0]), str(opt[1])
        return str(opt), str(opt)

    # Build tag chips for selected values
    tag_parts = []
    for opt in options:
        ov, ol = _opt_pair(opt)
        if ov in selected:
            tag_parts.append(
                f'<span class="multi-select-tag">'
                f'{conditional_escape(ol)}'
                f'<button type="button" class="multi-select-tag-remove" '
                f'dj-click="{dj_event}" data-value="{conditional_escape(ov)}"'
                f'{disabled_attr}>&times;</button>'
                f'</span>'
            )

    tags_html = f'<div class="multi-select-tags">{"".join(tag_parts)}</div>' if tag_parts else ""

    # Build checkbox list
    cb_parts = []
    for opt in options:
        ov, ol = _opt_pair(opt)
        checked_attr = " checked" if ov in selected else ""
        cb_parts.append(
            f'<label class="multi-select-option">'
            f'<input type="checkbox" name="{e_name}" value="{conditional_escape(ov)}"'
            f'{checked_attr}{disabled_attr} dj-change="{dj_event}">'
            f' {conditional_escape(ol)}'
            f'</label>'
        )

    label_html = (
        f'<label class="form-label">{e_label}</label>' if label else ""
    )

    return mark_safe(
        f'<div class="multi-select" id="{uid}">'
        f'{label_html}'
        f'{tags_html}'
        f'<input type="text" class="multi-select-search" '
        f'placeholder="{e_placeholder}"{disabled_attr} '
        f'oninput="(function(el){{var items=el.parentElement.querySelectorAll(\'.multi-select-option\');'
        f'var q=el.value.toLowerCase();items.forEach(function(item){{item.style.display='
        f'item.textContent.toLowerCase().indexOf(q)>=0?\'\':\'none\';}});}})(this)">'
        f'<div class="multi-select-options">{"".join(cb_parts)}</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# OTP Input (#58)
# ---------------------------------------------------------------------------

@register.simple_tag
def otp_input(name="", digits=6, event="", label="", disabled=False):
    """Render a one-time-code input with individual digit boxes.

    Args:
        name: form field name (hidden input holds the full code)
        digits: number of digit boxes (4 or 6 typical)
        event: dj-change event name
        label: optional label above the input
        disabled: disables all boxes
    """
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    try:
        digits = int(digits)
    except (ValueError, TypeError):
        digits = 6
    digits = max(1, min(12, digits))

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    dj_event = conditional_escape(event or name)
    disabled_attr = " disabled" if disabled else ""

    uid = f"otp-{uuid.uuid4().hex[:6]}"

    box_parts = []
    for i in range(digits):
        box_parts.append(
            f'<input type="text" class="otp-digit" maxlength="1" inputmode="numeric" '
            f'pattern="[0-9]" data-index="{i}" autocomplete="one-time-code"'
            f'{disabled_attr}>'
        )

    label_html = (
        f'<label class="form-label">{e_label}</label>' if label else ""
    )

    return mark_safe(
        f'<div class="otp-input" id="{uid}" data-digits="{digits}">'
        f'{label_html}'
        f'<div class="otp-boxes">{"".join(box_parts)}</div>'
        f'<input type="hidden" name="{e_name}" class="otp-hidden" '
        f'dj-change="{dj_event}">'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Number Stepper (#59)
# ---------------------------------------------------------------------------

@register.simple_tag
def number_stepper(name="", value=0, min_val=None, max_val=None, step=1,
                   event="", label="", disabled=False):
    """Render a +/- numeric stepper input.

    Args:
        name: form field name
        value: current value
        min_val: minimum allowed value (None = no minimum)
        max_val: maximum allowed value (None = no maximum)
        step: increment/decrement amount
        event: dj-click event name for +/- buttons
        label: optional label
        disabled: disables the control
    """
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    try:
        value = int(value)
    except (ValueError, TypeError):
        value = 0
    try:
        step = int(step)
    except (ValueError, TypeError):
        step = 1

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    dj_event = conditional_escape(event or name)
    disabled_attr = " disabled" if disabled else ""

    min_attr = f' min="{int(min_val)}"' if min_val is not None else ""
    max_attr = f' max="{int(max_val)}"' if max_val is not None else ""

    label_html = (
        f'<label class="form-label" for="{e_name}">{e_label}</label>' if label else ""
    )

    return mark_safe(
        f'<div class="number-stepper">'
        f'{label_html}'
        f'<div class="number-stepper-controls">'
        f'<button type="button" class="number-stepper-btn number-stepper-dec" '
        f'dj-click="{dj_event}" data-value="dec"{disabled_attr}>&minus;</button>'
        f'<input type="number" class="number-stepper-input" name="{e_name}" '
        f'id="{e_name}" value="{value}" step="{step}"'
        f'{min_attr}{max_attr}{disabled_attr} dj-change="{dj_event}">'
        f'<button type="button" class="number-stepper-btn number-stepper-inc" '
        f'dj-click="{dj_event}" data-value="inc"{disabled_attr}>&plus;</button>'
        f'</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Tag Input (#63)
# ---------------------------------------------------------------------------

@register.simple_tag
def tag_input(name="", tags=None, suggestions=None, event="",
              placeholder="Add tag...", disabled=False, label=""):
    """Render an input that creates dismissible tags.

    Args:
        name: form field name
        tags: list of current tag strings
        suggestions: list of suggestion strings
        event: dj-click event name for add/remove
        placeholder: input placeholder text
        disabled: disables the control
        label: optional label
    """
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    if tags is None:
        tags = []
    if suggestions is None:
        suggestions = []

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_placeholder = conditional_escape(placeholder)
    dj_event = conditional_escape(event or name)
    disabled_attr = " disabled" if disabled else ""

    uid = f"ti-{uuid.uuid4().hex[:6]}"

    # Build existing tag chips
    tag_parts = []
    for tag in tags:
        e_tag = conditional_escape(str(tag))
        tag_parts.append(
            f'<span class="tag-input-tag">'
            f'{e_tag}'
            f'<button type="button" class="tag-input-remove" '
            f'dj-click="{dj_event}" data-value="remove:{e_tag}"'
            f'{disabled_attr}>&times;</button>'
            f'<input type="hidden" name="{e_name}" value="{e_tag}">'
            f'</span>'
        )

    # Build suggestion datalist
    suggestion_parts = []
    for s in suggestions:
        suggestion_parts.append(f'<option value="{conditional_escape(str(s))}">')

    label_html = (
        f'<label class="form-label">{e_label}</label>' if label else ""
    )

    return mark_safe(
        f'<div class="tag-input" id="{uid}">'
        f'{label_html}'
        f'<div class="tag-input-tags">{"".join(tag_parts)}</div>'
        f'<input type="text" class="tag-input-field" '
        f'placeholder="{e_placeholder}" list="{uid}-suggestions"'
        f'{disabled_attr} '
        f'dj-keydown.enter="{dj_event}">'
        f'<datalist id="{uid}-suggestions">{"".join(suggestion_parts)}</datalist>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Input Group (#64)
# ---------------------------------------------------------------------------

class InputGroupNode(template.Node):
    """Wraps child content (addons + input) in an input-group container."""
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        size = kw.get("size", "md")
        error = kw.get("error", "")
        content = self.nodelist.render(context)
        size_cls = f" input-group-{conditional_escape(size)}" if size != "md" else ""
        error_cls = " input-group-error" if error else ""
        error_html = (
            f'<span class="form-error-message">{conditional_escape(error)}</span>'
            if error else ""
        )
        return mark_safe(
            f'<div class="input-group{size_cls}{error_cls}">'
            f'{content}'
            f'</div>'
            f'{error_html}'
        )


class InputAddonNode(template.Node):
    """Renders a prefix/suffix addon inside an input group."""
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        position = kw.get("position", "prefix")
        content = self.nodelist.render(context)
        return mark_safe(
            f'<span class="input-addon input-addon-{conditional_escape(position)}">'
            f'{content}'
            f'</span>'
        )


@register.tag("input_group")
def do_input_group(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endinput_group",))
    parser.delete_first_token()
    return InputGroupNode(nodelist, kwargs)


@register.tag("input_addon")
def do_input_addon(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endinput_addon",))
    parser.delete_first_token()
    return InputAddonNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Label (#66)
# ---------------------------------------------------------------------------

class DjLabelNode(template.Node):
    """Renders an accessible form label element."""
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        for_input = kw.get("for", "")
        required = kw.get("required", False)
        if isinstance(required, str):
            required = required.lower() not in ("false", "0", "")
        extra_class = kw.get("class", "")

        content = self.nodelist.render(context)
        for_attr = f' for="{conditional_escape(for_input)}"' if for_input else ""
        required_span = ' <span class="form-required">*</span>' if required else ""
        cls = f"form-label {conditional_escape(extra_class)}".strip()

        return mark_safe(
            f'<label class="{cls}"{for_attr}>'
            f'{content}{required_span}'
            f'</label>'
        )


@register.tag("dj_label")
def do_dj_label(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("enddj_label",))
    parser.delete_first_token()
    return DjLabelNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Fieldset (#147)
# ---------------------------------------------------------------------------

class FieldsetNode(template.Node):
    """Renders a styled fieldset with legend."""
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        legend = kw.get("legend", "")
        disabled = kw.get("disabled", False)
        if isinstance(disabled, str):
            disabled = disabled.lower() not in ("false", "0", "")
        extra_class = kw.get("class", "")

        content = self.nodelist.render(context)
        disabled_attr = " disabled" if disabled else ""
        legend_html = (
            f'<legend class="fieldset-legend">{conditional_escape(legend)}</legend>'
            if legend else ""
        )
        cls = f"fieldset {conditional_escape(extra_class)}".strip()

        return mark_safe(
            f'<fieldset class="{cls}"{disabled_attr}>'
            f'{legend_html}'
            f'<div class="fieldset-content">{content}</div>'
            f'</fieldset>'
        )


@register.tag("fieldset")
def do_fieldset(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endfieldset",))
    parser.delete_first_token()
    return FieldsetNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Toggle Group (#61)
# ---------------------------------------------------------------------------

@register.simple_tag
def toggle_group(name="", options=None, value="", event="toggle_select",
                 mode="single", disabled=False, size="md"):
    """Render a segmented toggle button group (radio-style or multi-select).

    Args:
        name: group name for identification
        options: list of dicts with keys: value, label, icon (optional)
        value: currently selected value (or list of values in multi mode)
        event: dj-click event name
        mode: "single" (radio) or "multi" (checkbox-style)
        disabled: disables all buttons
        size: sm, md, lg
    """
    if options is None:
        options = []
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")

    e_name = conditional_escape(name)
    e_event = conditional_escape(event)
    e_mode = conditional_escape(mode)

    size_cls = ""
    if size and size != "md":
        size_cls = f" toggle-group-{conditional_escape(size)}"
    disabled_cls = " toggle-group-disabled" if disabled else ""

    buttons = []
    for opt in options:
        if not isinstance(opt, dict):
            continue
        opt_value = conditional_escape(str(opt.get("value", "")))
        opt_label = conditional_escape(str(opt.get("label", "")))
        opt_icon = opt.get("icon", "")

        if mode == "multi" and isinstance(value, (list, tuple)):
            is_active = opt.get("value", "") in value
        else:
            is_active = str(opt.get("value", "")) == str(value)

        active_cls = " toggle-group-btn--active" if is_active else ""
        aria_pressed = "true" if is_active else "false"
        disabled_attr = " disabled" if disabled else ""
        click_attr = "" if disabled else f' dj-click="{e_event}" data-value="{opt_value}"'

        icon_html = ""
        if opt_icon:
            icon_html = f'<span class="toggle-group-icon">{conditional_escape(str(opt_icon))}</span>'

        buttons.append(
            f'<button class="toggle-group-btn{active_cls}" '
            f'aria-pressed="{aria_pressed}" '
            f'data-name="{e_name}"{click_attr}{disabled_attr}>'
            f'{icon_html}'
            f'<span class="toggle-group-label">{opt_label}</span>'
            f'</button>'
        )

    return mark_safe(
        f'<div class="toggle-group{size_cls}{disabled_cls}" '
        f'role="group" data-mode="{e_mode}">'
        f'{"".join(buttons)}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Floating Action Button (#65)
# ---------------------------------------------------------------------------

@register.simple_tag
def fab(icon="+", event="", position="bottom-right", label="",
        size="md", variant="primary", disabled=False, actions=None):
    """Render a floating action button with optional speed-dial actions.

    Args:
        icon: icon text/emoji for the FAB
        event: dj-click event name
        position: bottom-right, bottom-left, top-right, top-left
        label: accessible label / tooltip text
        size: sm, md, lg
        variant: primary, secondary, danger, success
        disabled: disables the FAB
        actions: list of dicts with keys: icon, event, label (speed-dial)
    """
    if actions is None:
        actions = []
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")

    e_icon = conditional_escape(icon)
    e_event = conditional_escape(event)
    e_label = conditional_escape(label)

    valid_positions = ("bottom-right", "bottom-left", "top-right", "top-left")
    pos_cls = position if position in valid_positions else "bottom-right"
    pos_cls = conditional_escape(pos_cls)

    size_cls = ""
    if size and size != "md":
        size_cls = f" fab-{conditional_escape(size)}"
    variant_cls = f" fab-{conditional_escape(variant)}"
    disabled_attr = " disabled" if disabled else ""
    click_attr = "" if disabled or not event else f' dj-click="{e_event}"'
    aria_label = f' aria-label="{e_label}"' if label else ""

    actions_html = ""
    if actions:
        action_items = []
        for act in actions:
            if not isinstance(act, dict):
                continue
            act_icon = conditional_escape(str(act.get("icon", "")))
            act_event = conditional_escape(str(act.get("event", "")))
            act_label = conditional_escape(str(act.get("label", "")))
            act_click = f' dj-click="{act_event}"' if act_event and not disabled else ""
            act_aria = f' aria-label="{act_label}"' if act_label else ""
            action_items.append(
                f'<button class="fab-action"{act_click}{act_aria}{disabled_attr}>'
                f'<span class="fab-action-icon">{act_icon}</span>'
                f'</button>'
            )
        if action_items:
            actions_html = (
                f'<div class="fab-actions">{"".join(action_items)}</div>'
            )

    return mark_safe(
        f'<div class="fab-container fab-{pos_cls}">'
        f'{actions_html}'
        f'<button class="fab{size_cls}{variant_cls}"{click_attr}{aria_label}{disabled_attr}>'
        f'<span class="fab-icon">{e_icon}</span>'
        f'</button>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Split Button (#133)
# ---------------------------------------------------------------------------

@register.simple_tag
def split_button(label="", event="", options=None, variant="primary",
                 size="md", disabled=False, loading=False, open=False,
                 toggle_event="toggle_split_menu"):
    """Render a split button with primary action and dropdown secondary actions.

    Args:
        label: primary button text
        event: dj-click event for primary action
        options: list of dicts with keys: label, event
        variant: primary, secondary, danger, success
        size: sm, md, lg
        disabled: disables all buttons
        loading: shows spinner on primary, disables all
        open: whether the dropdown menu is open
        toggle_event: dj-click event for toggle button
    """
    if options is None:
        options = []
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    if isinstance(loading, str):
        loading = loading.lower() not in ("false", "0", "")
    if isinstance(open, str):
        open = open.lower() not in ("false", "0", "")

    e_label = conditional_escape(label)
    e_event = conditional_escape(event)
    e_toggle = conditional_escape(toggle_event)

    variant_cls = f" split-btn-{conditional_escape(variant)}"
    size_cls = ""
    if size and size != "md":
        size_cls = f" split-btn-{conditional_escape(size)}"
    loading_cls = " split-btn-loading" if loading else ""
    disabled_attr = " disabled" if disabled or loading else ""
    click_attr = "" if disabled or loading or not event else f' dj-click="{e_event}"'

    spinner_html = '<span class="split-btn-spinner"></span>' if loading else ""

    option_items = []
    for opt in options:
        if not isinstance(opt, dict):
            continue
        opt_label = conditional_escape(str(opt.get("label", "")))
        opt_event = conditional_escape(str(opt.get("event", "")))
        opt_click = f' dj-click="{opt_event}"' if opt_event and not disabled else ""
        opt_disabled = " disabled" if disabled else ""
        option_items.append(
            f'<button class="split-btn-option"{opt_click}{opt_disabled}>'
            f'{opt_label}</button>'
        )

    open_data = "true" if open else "false"
    toggle_disabled = " disabled" if disabled or loading else ""
    toggle_click = "" if disabled or loading else f' dj-click="{e_toggle}"'

    menu_html = ""
    if option_items:
        menu_html = (
            f'<div class="split-btn-menu" data-open="{open_data}">'
            f'{"".join(option_items)}'
            f'</div>'
        )

    return mark_safe(
        f'<div class="split-btn{variant_cls}{size_cls}{loading_cls}">'
        f'<button class="split-btn-primary"{click_attr}{disabled_attr}>'
        f'{spinner_html}'
        f'<span class="split-btn-label">{e_label}</span>'
        f'</button>'
        f'<button class="split-btn-toggle"{toggle_click}{toggle_disabled}>'
        f'<span class="split-btn-caret">&#9662;</span>'
        f'</button>'
        f'{menu_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Scroll Area
# ---------------------------------------------------------------------------

class ScrollAreaNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        max_height = kw.get("max_height", "400px")
        custom_class = kw.get("custom_class", "")

        e_max_height = conditional_escape(str(max_height))
        e_custom_class = conditional_escape(str(custom_class))

        content = self.nodelist.render(context)

        cls = "dj-scroll-area"
        if e_custom_class:
            cls += f" {e_custom_class}"

        return mark_safe(
            f'<div class="{cls}" style="--dj-scroll-area-max-height: {e_max_height}; '
            f'max-height: var(--dj-scroll-area-max-height); overflow-y: auto;">'
            f'{content}</div>'
        )


@register.tag("scroll_area")
def do_scroll_area(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endscroll_area",))
    parser.delete_first_token()
    return ScrollAreaNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Callout / Blockquote
# ---------------------------------------------------------------------------

class CalloutNode(template.Node):
    ICONS = {
        "info": "&#9432;",       # circled i
        "warning": "&#9888;",    # warning sign
        "danger": "&#9888;",     # warning sign
        "success": "&#10004;",   # check mark
    }

    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        callout_type = kw.get("type", "default")
        title = kw.get("title", "")
        icon = kw.get("icon", "")
        custom_class = kw.get("custom_class", "")

        e_type = conditional_escape(str(callout_type))
        e_title = conditional_escape(str(title))
        e_icon = conditional_escape(str(icon))
        e_custom_class = conditional_escape(str(custom_class))

        content = self.nodelist.render(context)

        cls = "dj-callout"
        if callout_type != "default":
            cls += f" dj-callout--{e_type}"
        if e_custom_class:
            cls += f" {e_custom_class}"

        icon_html = ""
        if e_icon:
            icon_html = f'<span class="dj-callout__icon">{e_icon}</span>'
        elif callout_type in self.ICONS:
            icon_html = f'<span class="dj-callout__icon">{self.ICONS[callout_type]}</span>'

        title_html = ""
        if e_title:
            title_html = f'<div class="dj-callout__title">{e_title}</div>'

        return mark_safe(
            f'<div class="{cls}">'
            f'{icon_html}'
            f'<div class="dj-callout__body">'
            f'{title_html}'
            f'<div class="dj-callout__content">{content}</div>'
            f'</div>'
            f'</div>'
        )


@register.tag("callout")
def do_callout(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endcallout",))
    parser.delete_first_token()
    return CalloutNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Aspect Ratio
# ---------------------------------------------------------------------------

class AspectRatioNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        ratio = kw.get("ratio", "16/9")
        custom_class = kw.get("custom_class", "")

        e_ratio = conditional_escape(str(ratio))
        e_custom_class = conditional_escape(str(custom_class))

        content = self.nodelist.render(context)

        cls = "dj-aspect-ratio"
        if e_custom_class:
            cls += f" {e_custom_class}"

        return mark_safe(
            f'<div class="{cls}" style="aspect-ratio: {e_ratio};">'
            f'{content}</div>'
        )


@register.tag("aspect_ratio")
def do_aspect_ratio(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endaspect_ratio",))
    parser.delete_first_token()
    return AspectRatioNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Description List
# ---------------------------------------------------------------------------

class DescriptionListNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        items = kw.get("items", [])
        layout = kw.get("layout", "vertical")
        custom_class = kw.get("custom_class", "")

        e_layout = conditional_escape(str(layout))
        e_custom_class = conditional_escape(str(custom_class))

        cls = "dj-dl"
        if layout == "horizontal":
            cls += " dj-dl--horizontal"
        if e_custom_class:
            cls += f" {e_custom_class}"

        dl_items = []
        if isinstance(items, (list, tuple)):
            for item in items:
                if isinstance(item, dict):
                    term = conditional_escape(str(item.get("term", "")))
                    detail = conditional_escape(str(item.get("detail", "")))
                    dl_items.append(
                        f'<div class="dj-dl__pair">'
                        f'<dt class="dj-dl__term">{term}</dt>'
                        f'<dd class="dj-dl__detail">{detail}</dd>'
                        f'</div>'
                    )

        return mark_safe(
            f'<dl class="{cls}">{"".join(dl_items)}</dl>'
        )


@register.tag("description_list")
def do_description_list(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return DescriptionListNode(kwargs)


# ---------------------------------------------------------------------------
# Sticky Header
# ---------------------------------------------------------------------------

class StickyHeaderNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        offset = kw.get("offset", "0")
        z_index = kw.get("z_index", "10")
        custom_class = kw.get("custom_class", "")

        e_offset = conditional_escape(str(offset))
        e_z_index = conditional_escape(str(z_index))
        e_custom_class = conditional_escape(str(custom_class))

        content = self.nodelist.render(context)

        cls = "dj-sticky-header"
        if e_custom_class:
            cls += f" {e_custom_class}"

        return mark_safe(
            f'<div class="{cls}" style="position: sticky; top: {e_offset}; '
            f'z-index: {e_z_index};">'
            f'{content}</div>'
        )


@register.tag("sticky_header")
def do_sticky_header(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endsticky_header",))
    parser.delete_first_token()
    return StickyHeaderNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Notification Badge
# ---------------------------------------------------------------------------

class NotificationBadgeNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        try:
            count = int(kw.get("count", 0))
        except (ValueError, TypeError):
            count = 0
        try:
            max_count = int(kw.get("max", 99))
        except (ValueError, TypeError):
            max_count = 99
        dot = kw.get("dot", False)
        pulse = kw.get("pulse", False)
        size = kw.get("size", "md")
        custom_class = kw.get("custom_class", "")

        e_size = conditional_escape(str(size))
        e_custom_class = conditional_escape(str(custom_class))

        cls = f"dj-notification-badge dj-notification-badge--{e_size}"
        if pulse:
            cls += " dj-notification-badge--pulse"
        if e_custom_class:
            cls += f" {e_custom_class}"

        if dot:
            return mark_safe(f'<span class="{cls} dj-notification-badge--dot"></span>')

        display = f"{max_count}+" if count > max_count else str(count)
        if count <= 0:
            return ""

        return mark_safe(f'<span class="{cls}">{display}</span>')


@register.tag("notification_badge")
def do_notification_badge(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return NotificationBadgeNode(kwargs)


# ---------------------------------------------------------------------------
# Segmented Progress
# ---------------------------------------------------------------------------

class SegmentedProgressNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        steps = kw.get("steps", [])
        if not isinstance(steps, (list, tuple)):
            steps = []
        try:
            current = int(kw.get("current", 0))
        except (ValueError, TypeError):
            current = 0
        size = kw.get("size", "md")
        custom_class = kw.get("custom_class", "")

        e_size = conditional_escape(str(size))
        e_custom_class = conditional_escape(str(custom_class))

        cls = f"dj-segmented-progress dj-segmented-progress--{e_size}"
        if e_custom_class:
            cls += f" {e_custom_class}"

        segments = []
        for i, step in enumerate(steps):
            label = conditional_escape(str(step)) if isinstance(step, str) else conditional_escape(str(step.get("label", ""))) if isinstance(step, dict) else conditional_escape(str(step))
            step_num = i + 1
            if step_num < current:
                state = "completed"
            elif step_num == current:
                state = "active"
            else:
                state = "pending"
            segments.append(
                f'<div class="dj-segmented-progress__step dj-segmented-progress__step--{state}">'
                f'<div class="dj-segmented-progress__indicator">{step_num}</div>'
                f'<div class="dj-segmented-progress__label">{label}</div>'
                f'</div>'
            )

        # Connector lines between steps
        parts = []
        for i, seg in enumerate(segments):
            parts.append(seg)
            if i < len(segments) - 1:
                step_num = i + 1
                line_state = "completed" if step_num < current else "pending"
                parts.append(
                    f'<div class="dj-segmented-progress__connector dj-segmented-progress__connector--{line_state}"></div>'
                )

        return mark_safe(f'<div class="{cls}">{"".join(parts)}</div>')


@register.tag("segmented_progress")
def do_segmented_progress(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return SegmentedProgressNode(kwargs)


# ---------------------------------------------------------------------------
# Progress Circle
# ---------------------------------------------------------------------------

class ProgressCircleNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        try:
            value = max(0, min(100, int(kw.get("value", 0))))
        except (ValueError, TypeError):
            value = 0
        size = kw.get("size", "md")
        color = kw.get("color", "primary")
        show_value = kw.get("show_value", True)
        custom_class = kw.get("custom_class", "")

        e_size = conditional_escape(str(size))
        e_color = conditional_escape(str(color))
        e_custom_class = conditional_escape(str(custom_class))

        sizes = {"sm": 48, "md": 80, "lg": 120}
        dim = sizes.get(str(size), 80)
        stroke_widths = {"sm": 4, "md": 6, "lg": 8}
        stroke_w = stroke_widths.get(str(size), 6)

        radius = (dim - stroke_w) / 2
        circumference = 2 * 3.14159265 * radius
        dash_offset = circumference * (1 - value / 100)

        cls = f"dj-progress-circle dj-progress-circle--{e_size} dj-progress-circle--{e_color}"
        if e_custom_class:
            cls += f" {e_custom_class}"

        value_html = ""
        if show_value:
            font_sizes = {"sm": "0.625rem", "md": "1rem", "lg": "1.5rem"}
            fs = font_sizes.get(str(size), "1rem")
            value_html = (
                f'<text x="{dim / 2}" y="{dim / 2}" '
                f'class="dj-progress-circle__value" '
                f'text-anchor="middle" dominant-baseline="central" '
                f'style="font-size:{fs}">'
                f'{value}%</text>'
            )

        return mark_safe(
            f'<div class="{cls}" role="progressbar" '
            f'aria-valuenow="{value}" aria-valuemin="0" aria-valuemax="100">'
            f'<svg width="{dim}" height="{dim}" viewBox="0 0 {dim} {dim}">'
            f'<circle class="dj-progress-circle__track" '
            f'cx="{dim / 2}" cy="{dim / 2}" r="{radius}" '
            f'fill="none" stroke-width="{stroke_w}"/>'
            f'<circle class="dj-progress-circle__fill" '
            f'cx="{dim / 2}" cy="{dim / 2}" r="{radius}" '
            f'fill="none" stroke-width="{stroke_w}" '
            f'stroke-dasharray="{circumference:.2f}" '
            f'stroke-dashoffset="{dash_offset:.2f}" '
            f'stroke-linecap="round" '
            f'transform="rotate(-90 {dim / 2} {dim / 2})"/>'
            f'{value_html}'
            f'</svg></div>'
        )


@register.tag("progress_circle")
def do_progress_circle(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ProgressCircleNode(kwargs)


# ---------------------------------------------------------------------------
# Status Indicator
# ---------------------------------------------------------------------------

class StatusIndicatorNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        status = kw.get("status", "offline")
        label = kw.get("label", "")
        pulse = kw.get("pulse", False)
        size = kw.get("size", "md")
        custom_class = kw.get("custom_class", "")

        e_status = conditional_escape(str(status))
        e_label = conditional_escape(str(label))
        e_size = conditional_escape(str(size))
        e_custom_class = conditional_escape(str(custom_class))

        # Map statuses to colors
        status_colors = {
            "online": "green",
            "degraded": "yellow",
            "offline": "red",
            "maintenance": "blue",
        }
        color = status_colors.get(str(status), "gray")

        cls = f"dj-status-indicator dj-status-indicator--{e_size} dj-status-indicator--{color}"
        if pulse:
            cls += " dj-status-indicator--pulse"
        if e_custom_class:
            cls += f" {e_custom_class}"

        dot_html = f'<span class="dj-status-indicator__dot"></span>'
        label_html = f'<span class="dj-status-indicator__label">{e_label}</span>' if label else ""

        return mark_safe(f'<span class="{cls}">{dot_html}{label_html}</span>')


@register.tag("status_indicator")
def do_status_indicator(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return StatusIndicatorNode(kwargs)


# ---------------------------------------------------------------------------
# Loading Overlay
# ---------------------------------------------------------------------------

class LoadingOverlayNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        active = kw.get("active", False)
        text = kw.get("text", "")
        spinner_size = kw.get("spinner_size", "md")
        custom_class = kw.get("custom_class", "")

        content = self.nodelist.render(context)

        e_spinner_size = conditional_escape(str(spinner_size))
        e_custom_class = conditional_escape(str(custom_class))
        e_text = conditional_escape(str(text))

        cls = "dj-loading-overlay-wrap"
        if e_custom_class:
            cls += f" {e_custom_class}"

        overlay_html = ""
        if active:
            text_html = f'<span class="dj-loading-overlay__text">{e_text}</span>' if text else ""
            overlay_html = (
                f'<div class="dj-loading-overlay">'
                f'<div class="dj-loading-overlay__spinner dj-loading-overlay__spinner--{e_spinner_size}"></div>'
                f'{text_html}'
                f'</div>'
            )

        return mark_safe(
            f'<div class="{cls}">'
            f'{content}'
            f'{overlay_html}'
            f'</div>'
        )


@register.tag("loading_overlay")
def do_loading_overlay(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endloading_overlay",))
    parser.delete_first_token()
    return LoadingOverlayNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Announcement Bar
# ---------------------------------------------------------------------------

class AnnouncementBarNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        bar_type = kw.get("type", "info")
        dismissible = kw.get("dismissible", False)
        dismiss_event = kw.get("dismiss_event", "dismiss_announcement")
        custom_class = kw.get("custom_class", "")

        content = self.nodelist.render(context)

        e_bar_type = conditional_escape(str(bar_type))
        e_dismiss_event = conditional_escape(str(dismiss_event))
        e_custom_class = conditional_escape(str(custom_class))

        cls = f"dj-announcement-bar dj-announcement-bar--{e_bar_type}"
        if e_custom_class:
            cls += f" {e_custom_class}"

        close_html = ""
        if dismissible:
            close_html = (
                f'<button class="dj-announcement-bar__close" '
                f'dj-click="{e_dismiss_event}">&times;</button>'
            )

        return mark_safe(
            f'<div class="{cls}" role="banner">'
            f'<div class="dj-announcement-bar__content">{content}</div>'
            f'{close_html}'
            f'</div>'
        )


@register.tag("announcement_bar")
def do_announcement_bar(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endannouncement_bar",))
    parser.delete_first_token()
    return AnnouncementBarNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Rich Select (#103)
# ---------------------------------------------------------------------------

@register.simple_tag
def rich_select(name="", options=None, value="", event="", placeholder="Select...",
                disabled=False, searchable=False, label=""):
    """Render a rich select dropdown where each option can include icons, images,
    descriptions, or badges alongside the label.

    Args:
        name: form field name
        options: list of dicts with keys: value, label, and optional icon, image,
                 description, badge
        value: currently selected value
        event: dj-click event name for selection
        placeholder: text shown when nothing is selected
        disabled: disables the control
        searchable: adds a search input to filter options
        label: optional label above the control
    """
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    if isinstance(searchable, str):
        searchable = searchable.lower() not in ("false", "0", "")
    if options is None:
        options = []

    value = str(value) if value else ""

    e_name = conditional_escape(name)
    e_placeholder = conditional_escape(placeholder)
    e_label = conditional_escape(label)
    dj_event = conditional_escape(event or name)
    disabled_attr = " disabled" if disabled else ""
    disabled_cls = " rich-select--disabled" if disabled else ""

    uid = f"rs-{uuid.uuid4().hex[:6]}"

    # Build selected display
    selected_opt = None
    for opt in options:
        if isinstance(opt, dict) and str(opt.get("value", "")) == value:
            selected_opt = opt
            break

    if selected_opt:
        selected_html = _rich_select_option_html(selected_opt, is_display=True)
    else:
        selected_html = f'<span class="rich-select-placeholder">{e_placeholder}</span>'

    # Build option list
    opt_parts = []
    for opt in options:
        if not isinstance(opt, dict):
            continue
        ov = str(opt.get("value", ""))
        active_cls = " rich-select-option--active" if ov == value else ""
        opt_html = _rich_select_option_html(opt, is_display=False)
        opt_parts.append(
            f'<div class="rich-select-option{active_cls}" '
            f'data-value="{conditional_escape(ov)}" '
            f'dj-click="{dj_event}" '
            f'role="option" aria-selected="{"true" if ov == value else "false"}">'
            f'{opt_html}'
            f'</div>'
        )

    search_html = ""
    if searchable:
        search_html = (
            f'<div class="rich-select-search">'
            f'<input type="text" class="rich-select-search-input" '
            f'placeholder="Search..." '
            f'oninput="(function(el){{var items=el.closest(\'.rich-select-dropdown\').'
            f'querySelectorAll(\'.rich-select-option\');'
            f'var q=el.value.toLowerCase();items.forEach(function(item){{item.style.display='
            f'item.textContent.toLowerCase().indexOf(q)>=0?\'\':\'none\';}});}})(this)">'
            f'</div>'
        )

    label_html = f'<label class="form-label">{e_label}</label>' if label else ""

    return mark_safe(
        f'<div class="rich-select{disabled_cls}" id="{uid}">'
        f'{label_html}'
        f'<input type="hidden" name="{e_name}" value="{conditional_escape(value)}">'
        f'<div class="rich-select-trigger" tabindex="0" role="combobox" '
        f'aria-expanded="false" aria-haspopup="listbox"{disabled_attr} '
        f'onclick="this.parentElement.classList.toggle(\'rich-select--open\')" '
        f'onkeydown="if(event.key===\'Enter\'||event.key===\' \'){{event.preventDefault();'
        f'this.parentElement.classList.toggle(\'rich-select--open\');}}">'
        f'{selected_html}'
        f'<span class="rich-select-chevron">&#9662;</span>'
        f'</div>'
        f'<div class="rich-select-dropdown" role="listbox">'
        f'{search_html}'
        f'{"".join(opt_parts)}'
        f'</div>'
        f'</div>'
    )


def _rich_select_option_html(opt, is_display=False):
    """Render the inner HTML for a rich select option."""
    parts = []
    icon = opt.get("icon", "")
    image = opt.get("image", "")
    label = conditional_escape(str(opt.get("label", "")))
    description = opt.get("description", "")
    badge_text = opt.get("badge", "")

    if image:
        parts.append(
            f'<img class="rich-select-option-image" '
            f'src="{conditional_escape(str(image))}" alt="">'
        )
    elif icon:
        parts.append(
            f'<span class="rich-select-option-icon">'
            f'{conditional_escape(str(icon))}</span>'
        )

    text_parts = [f'<span class="rich-select-option-label">{label}</span>']
    if description:
        text_parts.append(
            f'<span class="rich-select-option-desc">'
            f'{conditional_escape(str(description))}</span>'
        )

    parts.append(f'<span class="rich-select-option-text">{"".join(text_parts)}</span>')

    if badge_text:
        parts.append(
            f'<span class="rich-select-option-badge">'
            f'{conditional_escape(str(badge_text))}</span>'
        )

    return "".join(parts)


# ---------------------------------------------------------------------------
# Data Grid (#54)
# ---------------------------------------------------------------------------

@register.simple_tag
def data_grid(columns=None, rows=None, row_key="id", edit_event="grid_cell_edit",
              resizable=True, frozen_left=0, frozen_right=0,
              striped=False, compact=False, keyboard_nav=True,
              new_row_event="", delete_row_event="",
              custom_class=""):
    """Render an editable data grid — spreadsheet-like component.

    Distinct from data_table: the grid is optimised for cell-level editing with
    keyboard navigation, column resize, and frozen columns.

    Args:
        columns: list of dicts with keys: key, label, width (optional),
                 editable (bool, default True), type (text|number|select),
                 options (for select type), frozen (left|right|None)
        rows: list of dicts keyed by column keys
        row_key: key field for row identity (default "id")
        edit_event: dj-click event fired on cell edit commit
        resizable: enable column resize handles
        frozen_left: number of columns frozen on the left
        frozen_right: number of columns frozen on the right
        striped: alternating row backgrounds
        compact: reduced cell padding
        keyboard_nav: enable arrow-key cell navigation
        new_row_event: event name for Add Row button (hidden if empty)
        delete_row_event: event name for row deletion
        custom_class: additional CSS classes
    """
    if columns is None:
        columns = []
    if rows is None:
        rows = []
    if isinstance(resizable, str):
        resizable = resizable.lower() not in ("false", "0", "")
    if isinstance(striped, str):
        striped = striped.lower() not in ("false", "0", "")
    if isinstance(compact, str):
        compact = compact.lower() not in ("false", "0", "")
    if isinstance(keyboard_nav, str):
        keyboard_nav = keyboard_nav.lower() not in ("false", "0", "")

    e_edit_event = conditional_escape(edit_event)
    e_custom_class = conditional_escape(custom_class)
    e_new_row_event = conditional_escape(new_row_event)
    e_delete_row_event = conditional_escape(delete_row_event)

    wrapper_cls = "data-grid-wrapper"
    if striped:
        wrapper_cls += " data-grid-striped"
    if compact:
        wrapper_cls += " data-grid-compact"
    if e_custom_class:
        wrapper_cls += f" {e_custom_class}"

    wrapper_attrs = f'class="{wrapper_cls}"'
    if resizable:
        wrapper_attrs += ' data-resizable="true"'
    if keyboard_nav:
        wrapper_attrs += ' data-keyboard-nav="true"'
    wrapper_attrs += f' data-edit-event="{e_edit_event}"'

    # --- Header ---
    header_cells = []
    for idx, col in enumerate(columns):
        if not isinstance(col, dict):
            continue
        col_key = conditional_escape(str(col.get("key", "")))
        col_label = conditional_escape(str(col.get("label", col.get("key", ""))))
        width = col.get("width", "")
        style = f' style="width:{conditional_escape(str(width))};min-width:{conditional_escape(str(width))}"' if width else ""
        frozen_cls = ""
        if idx < frozen_left:
            frozen_cls = " data-grid-frozen-left"
        elif frozen_right and idx >= len(columns) - frozen_right:
            frozen_cls = " data-grid-frozen-right"
        resize_attr = ' data-resizable="true"' if resizable else ""
        header_cells.append(
            f'<th class="data-grid-header-cell{frozen_cls}" '
            f'data-col-key="{col_key}"{style}{resize_attr}>'
            f'{col_label}</th>'
        )

    # Add delete column header if delete_row_event is set
    if delete_row_event:
        header_cells.append('<th class="data-grid-header-cell data-grid-actions-col"></th>')

    # --- Body rows ---
    body_rows = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        rk = conditional_escape(str(row.get(row_key, "")))
        cells = []
        for idx, col in enumerate(columns):
            if not isinstance(col, dict):
                continue
            col_key_raw = str(col.get("key", ""))
            col_key = conditional_escape(col_key_raw)
            cell_val = conditional_escape(str(row.get(col_key_raw, "")))
            editable = col.get("editable", True)
            if isinstance(editable, str):
                editable = editable.lower() not in ("false", "0", "")
            col_type = col.get("type", "text")

            frozen_cls = ""
            if idx < frozen_left:
                frozen_cls = " data-grid-frozen-left"
            elif frozen_right and idx >= len(columns) - frozen_right:
                frozen_cls = " data-grid-frozen-right"

            edit_attr = ' data-editable="true"' if editable else ""
            type_attr = f' data-type="{conditional_escape(str(col_type))}"'

            cells.append(
                f'<td class="data-grid-cell{frozen_cls}" '
                f'data-col-key="{col_key}" tabindex="-1"'
                f'{edit_attr}{type_attr}>'
                f'{cell_val}</td>'
            )

        # Delete button cell
        if delete_row_event:
            cells.append(
                f'<td class="data-grid-cell data-grid-actions-col">'
                f'<button class="data-grid-delete-btn" '
                f'dj-click="{e_delete_row_event}" data-value="{rk}" '
                f'title="Delete row">&times;</button>'
                f'</td>'
            )

        body_rows.append(
            f'<tr class="data-grid-row" data-row-key="{rk}">{"".join(cells)}</tr>'
        )

    # --- Add Row button ---
    add_row_html = ""
    if new_row_event:
        add_row_html = (
            f'<div class="data-grid-toolbar">'
            f'<button class="data-grid-add-btn" dj-click="{e_new_row_event}">+ Add Row</button>'
            f'</div>'
        )

    # Hidden triggers for edit events
    trigger_html = (
        f'<button class="data-grid-edit-trigger" style="display:none" '
        f'dj-click="{e_edit_event}"></button>'
    )

    return mark_safe(
        f'<div {wrapper_attrs}>'
        f'<div class="data-grid-scroll">'
        f'<table class="data-grid" role="grid">'
        f'<thead><tr>{"".join(header_cells)}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody>'
        f'</table>'
        f'</div>'
        f'{trigger_html}'
        f'{add_row_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Streaming Text
# ---------------------------------------------------------------------------

class StreamingTextNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        stream_event = kw.get("stream_event", "stream_chunk")
        text = kw.get("text", "")
        markdown = kw.get("markdown", False)
        auto_scroll = kw.get("auto_scroll", True)
        cursor = kw.get("cursor", True)
        custom_class = kw.get("custom_class", "")

        e_stream_event = conditional_escape(str(stream_event))
        e_custom_class = conditional_escape(str(custom_class))

        cls = "dj-streaming-text"
        if cursor:
            cls += " dj-streaming-text--cursor"
        if e_custom_class:
            cls += f" {e_custom_class}"

        attrs = [
            f'class="{cls}"',
            f'data-stream-event="{e_stream_event}"',
        ]
        if auto_scroll:
            attrs.append('data-auto-scroll="true"')
        if markdown:
            attrs.append('data-markdown="true"')

        attrs_str = " ".join(attrs)
        e_text = conditional_escape(str(text))
        return mark_safe(
            f'<div {attrs_str}>'
            f'<div class="dj-streaming-text__content">{e_text}</div>'
            f'</div>'
        )


@register.tag("streaming_text")
def do_streaming_text(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return StreamingTextNode(kwargs)


# ---------------------------------------------------------------------------
# Connection Status Bar
# ---------------------------------------------------------------------------

class ConnectionStatusNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        custom_class = kw.get("custom_class", "")
        reconnecting_text = kw.get("reconnecting_text", "Reconnecting...")
        connected_text = kw.get("connected_text", "Reconnected")

        e_custom_class = conditional_escape(str(custom_class))
        e_reconnecting_text = conditional_escape(str(reconnecting_text))
        e_connected_text = conditional_escape(str(connected_text))

        cls = "dj-connection-status"
        if e_custom_class:
            cls += f" {e_custom_class}"

        return mark_safe(
            f'<div class="{cls}" '
            f'data-reconnecting-text="{e_reconnecting_text}" '
            f'data-connected-text="{e_connected_text}" '
            f'role="status" aria-live="polite" style="display:none">'
            f'<span class="dj-connection-status__text">{e_reconnecting_text}</span>'
            f'</div>'
        )


@register.tag("connection_status")
def do_connection_status(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ConnectionStatusNode(kwargs)


# ---------------------------------------------------------------------------
# Live Counter
# ---------------------------------------------------------------------------

class LiveCounterNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        try:
            value = int(kw.get("value", 0))
        except (ValueError, TypeError):
            value = 0
        label = kw.get("label", "")
        stream_event = kw.get("stream_event", "counter_update")
        custom_class = kw.get("custom_class", "")
        size = kw.get("size", "md")

        e_stream_event = conditional_escape(str(stream_event))
        e_label = conditional_escape(str(label))
        e_custom_class = conditional_escape(str(custom_class))
        e_size = conditional_escape(str(size))

        cls = f"dj-live-counter dj-live-counter--{e_size}"
        if e_custom_class:
            cls += f" {e_custom_class}"

        label_html = ""
        if e_label:
            label_html = f'<span class="dj-live-counter__label">{e_label}</span>'

        return mark_safe(
            f'<div class="{cls}" data-stream-event="{e_stream_event}">'
            f'<span class="dj-live-counter__value" data-value="{value}">{value}</span>'
            f'{label_html}'
            f'</div>'
        )


@register.tag("live_counter")
def do_live_counter(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return LiveCounterNode(kwargs)


# ---------------------------------------------------------------------------
# Toast Container (Server Event Toast)
# ---------------------------------------------------------------------------

class ToastContainerNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        position = kw.get("position", "top-right")
        custom_class = kw.get("custom_class", "")
        max_toasts = kw.get("max_toasts", 5)

        e_position = conditional_escape(str(position))
        e_custom_class = conditional_escape(str(custom_class))

        try:
            max_toasts = int(max_toasts)
        except (ValueError, TypeError):
            max_toasts = 5

        cls = f"dj-toast-container dj-toast-container--{e_position}"
        if e_custom_class:
            cls += f" {e_custom_class}"

        return mark_safe(
            f'<div class="{cls}" '
            f'data-max-toasts="{max_toasts}" '
            f'role="region" aria-live="polite" aria-label="Notifications">'
            f'</div>'
        )


@register.tag("server_toast_container")
def do_server_toast_container(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ToastContainerNode(kwargs)
