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
               column_stats=None,
               # Phase 4 params
               footer_aggregations=None,
               row_class_map=None,
               column_groups=None,
               row_drag=False, row_drag_event="table_row_drag",
               copyable=False, copy_event="table_copy",
               copy_format="csv",
               # Phase 5 params
               importable=False, import_event="table_import",
               import_formats=None, import_preview=True,
               import_preview_data=None, import_errors=None,
               import_pending=False,
               computed_columns=None,
               cell_merge_key="_merge",
               column_expressions=None, expression_event="table_expression",
               active_expressions=None,
               conditional_formatting=None):
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

    Phase 4 args:
        footer_aggregations: dict of {col_key: "sum"|"avg"|"count"|"min"|"max"}
        row_class_map: dict of {col_key: {value: css_class}} for conditional row styling
        column_groups: list of dicts {label, columns} for multi-level headers
        row_drag: enable row drag-and-drop reorder
        row_drag_event: row reorder event name
        copyable: enable copy rows to clipboard
        copy_event: copy event name
        copy_format: "csv" or "tsv"

    Phase 5 args:
        importable: show import button/dropzone
        import_event: import event name
        import_formats: list of import formats (csv, json)
        import_preview: preview imported data before confirming
        import_preview_data: staged import rows for preview
        import_errors: import validation errors
        import_pending: whether import preview is awaiting confirmation
        computed_columns: list of virtual computed column dicts
        cell_merge_key: row data key holding colspan info
        column_expressions: dict of column expression filter configs
        expression_event: column expression filter event name
        active_expressions: dict of active column expression filters
        conditional_formatting: list of formatting preset dicts
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
        # Phase 4
        "footer_aggregations": footer_aggregations or {},
        "row_class_map": row_class_map or {},
        "column_groups": column_groups or [],
        "row_drag": row_drag,
        "row_drag_event": row_drag_event,
        "copyable": copyable,
        "copy_event": copy_event,
        "copy_format": copy_format,
        # Phase 5
        "importable": importable,
        "import_event": import_event,
        "import_formats": import_formats or ["csv", "json"],
        "import_preview": import_preview,
        "import_preview_data": import_preview_data or [],
        "import_errors": import_errors or [],
        "import_pending": import_pending,
        "computed_columns": computed_columns or [],
        "cell_merge_key": cell_merge_key,
        "column_expressions": column_expressions or {},
        "expression_event": expression_event,
        "active_expressions": active_expressions or {},
        "conditional_formatting": conditional_formatting or [],
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
              disabled=False, loading=False, size="md", preset=""):
    """Render a button element.

    Args:
        label: button text
        variant: primary, secondary, danger, ghost, link, success, warning
        event: dj-click event name
        icon: optional icon HTML/text prepended to label
        disabled: disables the button
        loading: shows spinner and disables button
        size: sm, md, lg (md emits no extra class)
        preset: optional preset name (see ``djust_components.presets``)
    """
    # Apply preset defaults — explicit kwargs take precedence.
    if preset:
        from djust_components.presets import get_preset

        preset_params = get_preset("dj_button", preset)
        if preset_params:
            # Only apply preset values for args the caller left at defaults.
            _defaults = {"variant": "primary", "event": "", "icon": "",
                         "disabled": False, "loading": False, "size": "md"}
            if label == "" and "label" in preset_params:
                label = preset_params["label"]
            if variant == _defaults["variant"] and "variant" in preset_params:
                variant = preset_params["variant"]
            if event == _defaults["event"] and "event" in preset_params:
                event = preset_params["event"]
            if icon == _defaults["icon"] and "icon" in preset_params:
                icon = preset_params["icon"]
            if disabled == _defaults["disabled"] and "disabled" in preset_params:
                disabled = preset_params["disabled"]
            if loading == _defaults["loading"] and "loading" in preset_params:
                loading = preset_params["loading"]
            if size == _defaults["size"] and "size" in preset_params:
                size = preset_params["size"]

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


# ---------------------------------------------------------------------------
# Scroll to Top (#125)
# ---------------------------------------------------------------------------

@register.simple_tag
def scroll_to_top(threshold="300px", label="Back to top", custom_class=""):
    """Floating button that appears after scrolling past a threshold.

    Args:
        threshold: scroll distance before button appears (default "300px")
        label: accessible button label
        custom_class: additional CSS classes
    """
    e_threshold = conditional_escape(threshold)
    e_label = conditional_escape(label)
    e_cls = conditional_escape(custom_class)

    cls = "dj-scroll-to-top"
    if e_cls:
        cls += f" {e_cls}"

    return mark_safe(
        f'<button class="{cls}" '
        f'data-threshold="{e_threshold}" '
        f'aria-label="{e_label}" '
        f'title="{e_label}" '
        f'style="display:none">'
        f'<svg width="20" height="20" viewBox="0 0 20 20" fill="none" '
        f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round">'
        f'<path d="M10 16V4M10 4l-6 6M10 4l6 6"/>'
        f'</svg>'
        f'</button>'
    )


# ---------------------------------------------------------------------------
# Code Snippet (#139)
# ---------------------------------------------------------------------------

@register.simple_tag
def code_snippet(code="", language="", custom_class=""):
    """Code block with copy button and language badge.

    Args:
        code: source code text
        language: programming language label
        custom_class: additional CSS classes
    """
    e_code = conditional_escape(code)
    e_lang = conditional_escape(language)
    e_cls = conditional_escape(custom_class)

    cls = "dj-code-snippet"
    if e_cls:
        cls += f" {e_cls}"

    lang_badge = ""
    if language:
        lang_badge = f'<span class="dj-code-snippet__lang">{e_lang}</span>'

    return mark_safe(
        f'<div class="{cls}">'
        f'<div class="dj-code-snippet__header">'
        f'{lang_badge}'
        f'<button class="dj-code-snippet__copy" aria-label="Copy code" '
        f'type="button">Copy</button>'
        f'</div>'
        f'<pre class="dj-code-snippet__pre">'
        f'<code class="dj-code-snippet__code">{e_code}</code>'
        f'</pre>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Responsive Image (#140)
# ---------------------------------------------------------------------------

@register.simple_tag
def responsive_image(src="", alt="", aspect_ratio="", lazy=True, srcset="",
                     sizes="", placeholder="", custom_class=""):
    """Picture element with srcset, lazy loading, and blur-up placeholder.

    Args:
        src: image URL
        alt: alt text
        aspect_ratio: CSS aspect-ratio (e.g. "16/9")
        lazy: enable native lazy loading (default True)
        srcset: srcset attribute value
        sizes: sizes attribute value
        placeholder: blur-up placeholder image URL
        custom_class: additional CSS classes
    """
    if isinstance(lazy, str):
        lazy = lazy.lower() not in ("false", "0", "")

    e_src = conditional_escape(src)
    e_alt = conditional_escape(alt)
    e_cls = conditional_escape(custom_class)

    cls = "dj-responsive-image"
    if placeholder:
        cls += " dj-responsive-image--blur-up"
    if e_cls:
        cls += f" {e_cls}"

    style = ""
    if aspect_ratio:
        e_ratio = conditional_escape(aspect_ratio)
        style = f' style="aspect-ratio:{e_ratio}"'

    img_attrs = [f'src="{e_src}"', f'alt="{e_alt}"']
    if lazy:
        img_attrs.append('loading="lazy"')
    if srcset:
        img_attrs.append(f'srcset="{conditional_escape(srcset)}"')
    if sizes:
        img_attrs.append(f'sizes="{conditional_escape(sizes)}"')

    img_tag = f'<img {" ".join(img_attrs)} class="dj-responsive-image__img">'

    placeholder_html = ""
    if placeholder:
        e_ph = conditional_escape(placeholder)
        placeholder_html = (
            f'<img src="{e_ph}" alt="" class="dj-responsive-image__placeholder" '
            f'aria-hidden="true">'
        )

    return mark_safe(
        f'<div class="{cls}"{style}>'
        f'{placeholder_html}'
        f'{img_tag}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Relative Time (#146)
# ---------------------------------------------------------------------------

@register.simple_tag
def relative_time(datetime="", auto_update=True, interval=60, custom_class=""):
    """Display a datetime as relative text ("3 hours ago") with auto-update.

    Args:
        datetime: ISO datetime string or datetime object
        auto_update: enable client-side interval updates (default True)
        interval: update interval in seconds (default 60)
        custom_class: additional CSS classes
    """
    if isinstance(auto_update, str):
        auto_update = auto_update.lower() not in ("false", "0", "")

    e_cls = conditional_escape(custom_class)
    cls = "dj-relative-time"
    if e_cls:
        cls += f" {e_cls}"

    iso_val = ""
    if datetime:
        if hasattr(datetime, "isoformat"):
            iso_val = datetime.isoformat()
        else:
            iso_val = str(datetime)

    e_iso = conditional_escape(iso_val)
    auto_str = "true" if auto_update else "false"

    try:
        interval_val = int(interval)
    except (ValueError, TypeError):
        interval_val = 60

    return mark_safe(
        f'<time class="{cls}" '
        f'datetime="{e_iso}" '
        f'data-auto-update="{auto_str}" '
        f'data-interval="{interval_val}">'
        f'{e_iso}'
        f'</time>'
    )


# ---------------------------------------------------------------------------
# Copyable Text (#153)
# ---------------------------------------------------------------------------

class CopyableTextNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        copied_label = kw.get("copied_label", "Copied!")
        custom_class = kw.get("custom_class", "")

        content = self.nodelist.render(context).strip()

        e_content = conditional_escape(content)
        e_label = conditional_escape(copied_label)
        e_cls = conditional_escape(custom_class)

        cls = "dj-copyable-text"
        if e_cls:
            cls += f" {e_cls}"

        return mark_safe(
            f'<span class="{cls}" '
            f'data-copy-text="{e_content}" '
            f'data-copied-label="{e_label}" '
            f'role="button" tabindex="0" '
            f'aria-label="Click to copy">'
            f'<span class="dj-copyable-text__value">{e_content}</span>'
            f'<span class="dj-copyable-text__tooltip" aria-hidden="true">{e_label}</span>'
            f'</span>'
        )


@register.tag("copyable_text")
def do_copyable_text(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endcopyable_text",))
    parser.delete_first_token()
    return CopyableTextNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Icon System (#178)
# ---------------------------------------------------------------------------

@register.simple_tag
def icon(name="", size="md", set="heroicons", **kwargs):
    """Render an SVG icon from a bundled icon set.

    Args:
        name: icon name (e.g. "check", "x-mark", "sun", "moon")
        size: xs (12px), sm (16px), md (20px), lg (24px)
        set: icon set name (default "heroicons"); extensible via
             DJUST_COMPONENTS_ICON_SETS setting
        **kwargs: extra HTML attributes — ``class`` adds CSS classes,
                  ``aria_label`` becomes ``aria-label``, etc.
    """
    from djust_components.icons import render_icon

    custom_class = kwargs.pop("custom_class", "")
    # Also accept 'class' as alias (but 'class' is a Python keyword,
    # so callers from Rust handlers can pass custom_class)
    return render_icon(
        name=name,
        size=size,
        icon_set=conditional_escape(set),
        custom_class=custom_class,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Theme Toggle (#138)
# ---------------------------------------------------------------------------

class ThemeToggleNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        current = kw.get("current", "system")
        event = kw.get("event", "")
        custom_class = kw.get("custom_class", "")

        e_event = conditional_escape(event) if event else ""
        e_cls = conditional_escape(custom_class)
        e_current = conditional_escape(current)

        # CSS classes
        cls = "dj-theme-toggle"
        if e_cls:
            cls += f" {e_cls}"

        # Build dj-click attribute if server-side persistence is desired
        click_attr = f' dj-click="{e_event}"' if e_event else ""

        # Icon SVGs for light/dark/system (rendered inline via render_icon)
        from djust_components.icons import render_icon
        sun_svg = render_icon("sun", size="sm")
        moon_svg = render_icon("moon", size="sm")
        monitor_svg = render_icon("computer-desktop", size="sm")

        # Generate a unique ID for this toggle instance
        toggle_id = f"dj-theme-toggle-{uuid.uuid4().hex[:8]}"

        return mark_safe(
            f'<div class="{cls}" id="{toggle_id}" '
            f'data-current="{e_current}"{click_attr} '
            f'role="radiogroup" aria-label="Color theme">'
            f'<button type="button" class="dj-theme-toggle__btn" '
            f'data-theme="light" aria-label="Light theme" '
            f'title="Light">{sun_svg}</button>'
            f'<button type="button" class="dj-theme-toggle__btn" '
            f'data-theme="dark" aria-label="Dark theme" '
            f'title="Dark">{moon_svg}</button>'
            f'<button type="button" class="dj-theme-toggle__btn" '
            f'data-theme="system" aria-label="System theme" '
            f'title="System">{monitor_svg}</button>'
            f'</div>'
        )


@register.tag("theme_toggle")
def do_theme_toggle(parser, token):
    """{% theme_toggle current="system" event="set_theme" %}"""
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ThemeToggleNode(kwargs)


# ---------------------------------------------------------------------------
# Page Header (#179)
# ---------------------------------------------------------------------------

_page_header_actions_key = "__page_header_actions__"


class PageHeaderActionsNode(template.Node):
    """Renders the actions slot inside a page header."""
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        content = self.nodelist.render(context)
        # Stash the rendered actions content on the context for the parent
        context[_page_header_actions_key] = content
        return ""


class PageHeaderNode(template.Node):
    """Structured page-level header with title, optional subtitle/description,
    optional breadcrumb slot, and right-aligned action buttons area."""
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        title = kw.get("title", "")
        subtitle = kw.get("subtitle", "")
        description = kw.get("description", "")
        custom_class = kw.get("custom_class", "")

        e_title = conditional_escape(str(title))
        e_subtitle = conditional_escape(str(subtitle))
        e_description = conditional_escape(str(description))
        e_custom_class = conditional_escape(str(custom_class))

        # Render child nodelist — this may include page_header_actions which
        # stashes its content in the context.
        context[_page_header_actions_key] = ""
        breadcrumb_content = self.nodelist.render(context)
        actions_html = context.get(_page_header_actions_key, "")

        cls = "dj-page-header"
        if e_custom_class:
            cls += f" {e_custom_class}"

        # Breadcrumb slot — any direct child content (not actions)
        breadcrumb_html = ""
        if breadcrumb_content.strip():
            breadcrumb_html = (
                f'<div class="dj-page-header__breadcrumb">'
                f'{breadcrumb_content}'
                f'</div>'
            )

        # Title
        title_html = f'<h1 class="dj-page-header__title">{e_title}</h1>' if e_title else ""

        # Subtitle
        subtitle_html = ""
        if e_subtitle:
            subtitle_html = f'<p class="dj-page-header__subtitle">{e_subtitle}</p>'

        # Description
        description_html = ""
        if e_description:
            description_html = f'<p class="dj-page-header__description">{e_description}</p>'

        # Actions
        actions_section = ""
        if actions_html.strip():
            actions_section = (
                f'<div class="dj-page-header__actions">'
                f'{actions_html}'
                f'</div>'
            )

        return mark_safe(
            f'<header class="{cls}">'
            f'{breadcrumb_html}'
            f'<div class="dj-page-header__row">'
            f'<div class="dj-page-header__text">'
            f'{title_html}'
            f'{subtitle_html}'
            f'{description_html}'
            f'</div>'
            f'{actions_section}'
            f'</div>'
            f'</header>'
        )


@register.tag("page_header")
def do_page_header(parser, token):
    """{% page_header title="Products" subtitle="Manage inventory" %}...{% endpage_header %}"""
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endpage_header",))
    parser.delete_first_token()
    return PageHeaderNode(nodelist, kwargs)


@register.tag("page_header_actions")
def do_page_header_actions(parser, token):
    """{% page_header_actions %}...{% endpage_header_actions %}"""
    nodelist = parser.parse(("endpage_header_actions",))
    parser.delete_first_token()
    return PageHeaderActionsNode(nodelist)


# ---------------------------------------------------------------------------
# FORM ESSENTIALS (v1.5)
# ---------------------------------------------------------------------------

# --- Slider / Range ---

@register.simple_tag
def slider(name="", label="", min=0, max=100, step=1, value=None,
           value_end=None, event="", disabled=False, show_ticks=False,
           show_value=True, custom_class=""):
    """Render a horizontal slider with optional range mode.

    Args:
        name: Input name attribute.
        label: Optional label text.
        min/max/step: Range bounds and step increment.
        value: Current value (or start value in range mode).
        value_end: End value — when set, enables dual-handle range mode.
        event: dj-input event name (defaults to name).
        show_ticks: Show tick marks along the track.
        show_value: Show current value output (default True).
        disabled: Disable the input.
        custom_class: Extra CSS class.
    """
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    if isinstance(show_ticks, str):
        show_ticks = show_ticks.lower() not in ("false", "0", "")
    if isinstance(show_value, str):
        show_value = show_value.lower() not in ("false", "0", "")

    min_val = int(min)
    max_val = int(max)
    step_val = int(step)
    if value is None:
        value = min_val
    value = int(value)

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    dj_event = conditional_escape(event or name)
    e_class = conditional_escape(custom_class)

    disabled_attr = " disabled" if disabled else ""
    range_mode = value_end is not None
    if range_mode:
        value_end = int(value_end)

    cls = "dj-slider"
    if range_mode:
        cls += " dj-slider--range"
    if e_class:
        cls += f" {e_class}"

    label_html = (
        f'<label class="dj-slider__label" for="{e_name}">{e_label}</label>'
        if label else ""
    )

    value_display = ""
    if show_value:
        if range_mode:
            value_display = (
                f'<output class="dj-slider__value">'
                f'{value} &ndash; {value_end}</output>'
            )
        else:
            value_display = (
                f'<output class="dj-slider__value">{value}</output>'
            )

    ticks_html = ""
    if show_ticks:
        tick_count = builtins_max(1, (max_val - min_val) // step_val)
        tick_items = "".join(
            '<span class="dj-slider__tick"></span>'
            for _ in range(tick_count + 1)
        )
        ticks_html = f'<div class="dj-slider__ticks">{tick_items}</div>'

    input_html = (
        f'<input type="range" class="dj-slider__input" '
        f'name="{e_name}" id="{e_name}" '
        f'min="{min_val}" max="{max_val}" step="{step_val}" '
        f'value="{value}" '
        f'dj-input="{dj_event}"{disabled_attr}>'
    )

    if range_mode:
        input_html += (
            f'<input type="range" class="dj-slider__input dj-slider__input--end" '
            f'name="{e_name}_end" id="{e_name}_end" '
            f'min="{min_val}" max="{max_val}" step="{step_val}" '
            f'value="{value_end}" '
            f'dj-input="{dj_event}"{disabled_attr}>'
        )

    return mark_safe(
        f'<div class="{cls}">'
        f'{label_html}'
        f'<div class="dj-slider__track">{input_html}</div>'
        f'{ticks_html}'
        f'{value_display}'
        f'</div>'
    )


# Need a reference to the builtin max since 'max' is shadowed as a parameter
import builtins as _builtins
builtins_max = _builtins.max


# --- Search Input ---

@register.simple_tag
def search_input(name="", label="", value="", placeholder="Search...",
                 event="", debounce=300, loading=False, disabled=False,
                 custom_class=""):
    """Render a search input with icon, clear button, and loading spinner.

    Args:
        name: Input name attribute.
        label: Optional label text.
        value: Current value.
        placeholder: Placeholder text (default "Search...").
        event: dj-input event name (defaults to name).
        debounce: Debounce delay in ms (default 300).
        loading: Show loading spinner.
        disabled: Disable the input.
        custom_class: Extra CSS class.
    """
    if isinstance(loading, str):
        loading = loading.lower() not in ("false", "0", "")
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_value = conditional_escape(value)
    e_placeholder = conditional_escape(placeholder)
    dj_event = conditional_escape(event or name)
    e_class = conditional_escape(custom_class)
    debounce_val = int(debounce)

    disabled_attr = " disabled" if disabled else ""
    cls = "dj-search-input"
    if loading:
        cls += " dj-search-input--loading"
    if e_class:
        cls += f" {e_class}"

    label_html = (
        f'<label class="dj-search-input__label" for="{e_name}">{e_label}</label>'
        if label else ""
    )

    icon_html = (
        '<svg class="dj-search-input__icon" viewBox="0 0 20 20" fill="currentColor" '
        'width="16" height="16" aria-hidden="true">'
        '<path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11z'
        'M2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328'
        'A7 7 0 012 9z" clip-rule="evenodd"/></svg>'
    )

    spinner_html = (
        '<span class="dj-search-input__spinner" aria-hidden="true"></span>'
        if loading else ""
    )

    clear_html = (
        '<button type="button" class="dj-search-input__clear" '
        'aria-label="Clear search" tabindex="-1">&times;</button>'
    )

    return mark_safe(
        f'{label_html}'
        f'<div class="{cls}">'
        f'{icon_html}'
        f'<input type="search" class="dj-search-input__input" '
        f'name="{e_name}" id="{e_name}" value="{e_value}" '
        f'placeholder="{e_placeholder}" autocomplete="off" '
        f'dj-input="{dj_event}" data-debounce="{debounce_val}"{disabled_attr}>'
        f'{clear_html}'
        f'{spinner_html}'
        f'</div>'
    )


# --- Password Input ---

@register.simple_tag
def password_input(name="", label="", value="", placeholder="", event="",
                   error="", required=False, disabled=False,
                   show_strength=False, strength=0, custom_class=""):
    """Render a password input with show/hide toggle and optional strength meter.

    Args:
        name: Input name attribute.
        label: Optional label text.
        value: Current value.
        placeholder: Placeholder text.
        event: dj-input event name (defaults to name).
        error: Error message text.
        required: Mark as required.
        disabled: Disable the input.
        show_strength: Show strength meter bar.
        strength: Strength value 0-4.
        custom_class: Extra CSS class.
    """
    if isinstance(required, str):
        required = required.lower() not in ("false", "0", "")
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    if isinstance(show_strength, str):
        show_strength = show_strength.lower() not in ("false", "0", "")

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_value = conditional_escape(value)
    e_placeholder = conditional_escape(placeholder)
    dj_event = conditional_escape(event or name)
    e_error = conditional_escape(error)
    e_class = conditional_escape(custom_class)
    strength_val = builtins_max(0, builtins_min(4, int(strength)))

    required_attr = " required" if required else ""
    disabled_attr = " disabled" if disabled else ""

    cls = "dj-password-input"
    if error:
        cls += " dj-password-input--error"
    if e_class:
        cls += f" {e_class}"

    label_html = ""
    if label:
        req_span = '<span class="form-required"> *</span>' if required else ""
        label_html = (
            f'<label class="form-label" for="{e_name}">{e_label}{req_span}</label>'
        )

    error_html = (
        f'<span class="form-error-message">{e_error}</span>' if error else ""
    )

    toggle_btn = (
        '<button type="button" class="dj-password-input__toggle" '
        'aria-label="Toggle password visibility" tabindex="-1">'
        '<svg class="dj-password-input__eye" viewBox="0 0 20 20" '
        'fill="currentColor" width="16" height="16">'
        '<path d="M10 3C5 3 1.73 7.11 1 10c.73 2.89 4 7 9 7s8.27-4.11 9-7'
        'c-.73-2.89-4-7-9-7zm0 12a5 5 0 110-10 5 5 0 010 10zm0-8a3 3 0 '
        '100 6 3 3 0 000-6z"/></svg>'
        '</button>'
    )

    strength_html = ""
    if show_strength:
        s_cls = f"dj-password-strength--{strength_val}"
        strength_html = (
            f'<div class="dj-password-strength {s_cls}" '
            f'role="meter" aria-valuenow="{strength_val}" '
            f'aria-valuemin="0" aria-valuemax="4">'
            f'<div class="dj-password-strength__bar"></div>'
            f'<div class="dj-password-strength__bar"></div>'
            f'<div class="dj-password-strength__bar"></div>'
            f'<div class="dj-password-strength__bar"></div>'
            f'</div>'
        )

    return mark_safe(
        f'<div class="form-group">'
        f'{label_html}'
        f'<div class="{cls}">'
        f'<input type="password" class="dj-password-input__input form-input" '
        f'name="{e_name}" id="{e_name}" value="{e_value}" '
        f'placeholder="{e_placeholder}" '
        f'dj-input="{dj_event}"{required_attr}{disabled_attr}>'
        f'{toggle_btn}'
        f'</div>'
        f'{strength_html}'
        f'{error_html}'
        f'</div>'
    )


builtins_min = _builtins.min


# --- Autocomplete ---

@register.simple_tag
def autocomplete(name="", label="", value="", display_value="",
                 placeholder="", source_event="", event="",
                 debounce=300, min_chars=1, suggestions=None,
                 loading=False, disabled=False, error="",
                 required=False, custom_class=""):
    """Render an autocomplete input with server-driven suggestions.

    Args:
        name: Input name attribute (hidden input carries the selected value).
        label: Optional label text.
        value: Selected value (submitted in form).
        display_value: Display text for the input (defaults to value).
        placeholder: Placeholder text.
        source_event: dj-input event for fetching suggestions from the server.
        event: dj-change event when a value is selected (defaults to name).
        debounce: Debounce delay in ms (default 300).
        min_chars: Minimum characters before triggering search (default 1).
        suggestions: List of suggestion dicts/tuples for current render.
        loading: Show loading spinner.
        disabled: Disable the input.
        error: Error message text.
        required: Mark as required.
        custom_class: Extra CSS class.
    """
    if isinstance(loading, str):
        loading = loading.lower() not in ("false", "0", "")
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    if isinstance(required, str):
        required = required.lower() not in ("false", "0", "")
    if suggestions is None:
        suggestions = []
    if not isinstance(suggestions, (list, tuple)):
        suggestions = []

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_value = conditional_escape(str(value))
    e_display = conditional_escape(str(display_value or value))
    e_placeholder = conditional_escape(placeholder)
    e_source_event = conditional_escape(source_event)
    dj_event = conditional_escape(event or name)
    e_error = conditional_escape(error)
    e_class = conditional_escape(custom_class)
    debounce_val = int(debounce)
    min_chars_val = int(min_chars)

    disabled_attr = " disabled" if disabled else ""
    required_attr = " required" if required else ""

    cls = "dj-autocomplete"
    if loading:
        cls += " dj-autocomplete--loading"
    if error:
        cls += " dj-autocomplete--error"
    if e_class:
        cls += f" {e_class}"

    label_html = ""
    if label:
        req_span = '<span class="form-required"> *</span>' if required else ""
        label_html = (
            f'<label class="form-label" for="{e_name}">{e_label}{req_span}</label>'
        )

    error_html = (
        f'<span class="form-error-message">{e_error}</span>' if error else ""
    )

    # Build suggestion items
    suggestion_items = []
    for sug in suggestions:
        if isinstance(sug, dict):
            sv = conditional_escape(str(sug.get("value", "")))
            sl = conditional_escape(str(sug.get("label", sv)))
        elif isinstance(sug, (list, tuple)) and len(sug) >= 2:
            sv = conditional_escape(str(sug[0]))
            sl = conditional_escape(str(sug[1]))
        else:
            sv = sl = conditional_escape(str(sug))
        suggestion_items.append(
            f'<li class="dj-autocomplete__item" role="option" '
            f'data-value="{sv}">{sl}</li>'
        )

    dropdown_cls = "dj-autocomplete__dropdown"
    if not suggestion_items:
        dropdown_cls += " dj-autocomplete__dropdown--hidden"

    suggestions_html = (
        f'<ul class="{dropdown_cls}" role="listbox">'
        f'{"".join(suggestion_items)}'
        f'</ul>'
    )

    spinner_html = (
        '<span class="dj-autocomplete__spinner" aria-hidden="true"></span>'
        if loading else ""
    )

    return mark_safe(
        f'<div class="form-group">'
        f'{label_html}'
        f'<div class="{cls}" data-source-event="{e_source_event}" '
        f'data-debounce="{debounce_val}" data-min-chars="{min_chars_val}">'
        f'<input type="text" class="dj-autocomplete__input form-input" '
        f'name="{e_name}_display" id="{e_name}" value="{e_display}" '
        f'placeholder="{e_placeholder}" autocomplete="off" '
        f'role="combobox" aria-autocomplete="list" '
        f'aria-expanded="{"true" if suggestion_items else "false"}" '
        f'dj-input="{e_source_event or dj_event}" '
        f'data-debounce="{debounce_val}"{required_attr}{disabled_attr}>'
        f'<input type="hidden" name="{e_name}" value="{e_value}">'
        f'{spinner_html}'
        f'{suggestions_html}'
        f'</div>'
        f'{error_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Confirmation Dialog
# ---------------------------------------------------------------------------

class ConfirmDialogNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        message = kw.get("message", "Are you sure?")
        confirm_event = kw.get("confirm_event", "confirm")
        cancel_event = kw.get("cancel_event", "cancel")
        title = kw.get("title", "Confirm")
        is_open = kw.get("open", False)
        variant = kw.get("variant", "default")  # default or danger
        confirm_label = kw.get("confirm_label", "Confirm")
        cancel_label = kw.get("cancel_label", "Cancel")
        custom_class = kw.get("custom_class", "")

        if not is_open:
            return ""

        e_confirm_event = conditional_escape(confirm_event)
        e_cancel_event = conditional_escape(cancel_event)
        e_title = conditional_escape(title)
        e_message = conditional_escape(message)
        e_variant = conditional_escape(variant)
        e_confirm_label = conditional_escape(confirm_label)
        e_cancel_label = conditional_escape(cancel_label)
        e_custom_class = conditional_escape(custom_class)

        variant_cls = f" dj-confirm-dialog--{e_variant}" if variant != "default" else ""
        extra_cls = f" {e_custom_class}" if custom_class else ""

        return mark_safe(
            f'<div class="dj-confirm-dialog-backdrop" dj-click="{e_cancel_event}">'
            f'<div class="dj-confirm-dialog{variant_cls}{extra_cls}" '
            f'role="alertdialog" aria-modal="true" aria-labelledby="dj-confirm-title" '
            f'aria-describedby="dj-confirm-msg" onclick="event.stopPropagation()">'
            f'<div class="dj-confirm-dialog__header">'
            f'<h3 class="dj-confirm-dialog__title" id="dj-confirm-title">{e_title}</h3>'
            f'<button class="dj-confirm-dialog__close" dj-click="{e_cancel_event}" '
            f'aria-label="Close">&times;</button>'
            f'</div>'
            f'<div class="dj-confirm-dialog__body" id="dj-confirm-msg">'
            f'<p class="dj-confirm-dialog__message">{e_message}</p>'
            f'</div>'
            f'<div class="dj-confirm-dialog__footer">'
            f'<button class="dj-confirm-dialog__btn dj-confirm-dialog__btn--cancel" '
            f'dj-click="{e_cancel_event}">{e_cancel_label}</button>'
            f'<button class="dj-confirm-dialog__btn dj-confirm-dialog__btn--confirm" '
            f'dj-click="{e_confirm_event}">{e_confirm_label}</button>'
            f'</div>'
            f'</div>'
            f'</div>'
        )


@register.tag("confirm_dialog")
def do_confirm_dialog(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ConfirmDialogNode(kwargs)


# ---------------------------------------------------------------------------
# Popconfirm
# ---------------------------------------------------------------------------

class PopconfirmNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        message = kw.get("message", "Are you sure?")
        confirm_event = kw.get("confirm_event", "confirm")
        cancel_event = kw.get("cancel_event", "cancel")
        confirm_label = kw.get("confirm_label", "Yes")
        cancel_label = kw.get("cancel_label", "No")
        placement = kw.get("placement", "top")
        variant = kw.get("variant", "default")  # default or danger
        custom_class = kw.get("custom_class", "")
        uid = kw.get("id", f"popconfirm-{uuid.uuid4().hex[:6]}")

        content = self.nodelist.render(context)

        e_message = conditional_escape(message)
        e_confirm_event = conditional_escape(confirm_event)
        e_cancel_event = conditional_escape(cancel_event)
        e_confirm_label = conditional_escape(confirm_label)
        e_cancel_label = conditional_escape(cancel_label)
        e_placement = conditional_escape(placement)
        e_variant = conditional_escape(variant)
        e_custom_class = conditional_escape(custom_class)
        e_uid = conditional_escape(uid)

        variant_cls = f" dj-popconfirm--{e_variant}" if variant != "default" else ""
        extra_cls = f" {e_custom_class}" if custom_class else ""

        js_toggle = (
            "(function(el){"
            "var w=el.closest('.dj-popconfirm-wrapper');"
            "w.classList.toggle('dj-popconfirm-open');"
            "document.addEventListener('click',function h(e){"
            "if(!w.contains(e.target)){"
            "w.classList.remove('dj-popconfirm-open');"
            "document.removeEventListener('click',h);"
            "}},true);"
            "})(this)"
        )

        js_close = (
            "(function(el){"
            "el.closest('.dj-popconfirm-wrapper').classList.remove('dj-popconfirm-open');"
            "})(this)"
        )

        return mark_safe(
            f'<div class="dj-popconfirm-wrapper{variant_cls}{extra_cls}" id="{e_uid}">'
            f'<div class="dj-popconfirm-trigger" onclick="{js_toggle}">'
            f'{content}'
            f'</div>'
            f'<div class="dj-popconfirm dj-popconfirm-{e_placement}" role="tooltip">'
            f'<p class="dj-popconfirm__message">{e_message}</p>'
            f'<div class="dj-popconfirm__actions">'
            f'<button class="dj-popconfirm__btn dj-popconfirm__btn--cancel" '
            f'onclick="{js_close}" dj-click="{e_cancel_event}">{e_cancel_label}</button>'
            f'<button class="dj-popconfirm__btn dj-popconfirm__btn--confirm" '
            f'onclick="{js_close}" dj-click="{e_confirm_event}">{e_confirm_label}</button>'
            f'</div>'
            f'</div>'
            f'</div>'
        )


@register.tag("popconfirm")
def do_popconfirm(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endpopconfirm",))
    parser.delete_first_token()
    return PopconfirmNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# CASCADING FORM COMPONENTS
# ---------------------------------------------------------------------------

# --- Dependent Select (#108) ---

@register.simple_tag
def dependent_select(name="", parent="", source_event="", label="",
                     placeholder="Select...", value="", options=None,
                     loading=False, disabled=False, required=False,
                     error="", custom_class=""):
    """Cascading dropdown that reloads options when parent field changes.

    Args:
        name: Input name attribute.
        parent: Name of the parent field this select depends on.
        source_event: djust event name to fire when parent changes (loads new options).
        label: Optional label text.
        placeholder: Placeholder text when nothing selected.
        value: Currently selected value.
        options: List of dicts with 'value' and 'label' keys, or list of strings.
        loading: Show spinner while loading options.
        disabled: Disable the select.
        required: Mark field as required.
        error: Error message to display.
        custom_class: Extra CSS class.
    """
    if isinstance(loading, str):
        loading = loading.lower() not in ("false", "0", "")
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    if isinstance(required, str):
        required = required.lower() not in ("false", "0", "")

    e_name = conditional_escape(name)
    e_parent = conditional_escape(parent)
    e_source_event = conditional_escape(source_event or name)
    e_label = conditional_escape(label)
    e_placeholder = conditional_escape(placeholder)
    e_value = conditional_escape(str(value))
    e_error = conditional_escape(error)
    e_class = conditional_escape(custom_class)

    if options is None:
        options = []

    disabled_attr = " disabled" if disabled else ""
    required_attr = " required" if required else ""

    cls = "dj-dependent-select"
    if loading:
        cls += " dj-dependent-select--loading"
    if error:
        cls += " dj-dependent-select--error"
    if e_class:
        cls += f" {e_class}"

    label_html = ""
    if label:
        req_mark = ' <span class="form-required">*</span>' if required else ""
        label_html = (
            f'<label class="form-label" for="{e_name}">'
            f'{e_label}{req_mark}</label>'
        )

    # Build options
    opt_parts = [f'<option value="">{e_placeholder}</option>']
    for opt in options:
        if isinstance(opt, dict):
            ov = conditional_escape(str(opt.get("value", "")))
            ol = conditional_escape(str(opt.get("label", ov)))
        else:
            ov = conditional_escape(str(opt))
            ol = ov
        selected = " selected" if ov == e_value else ""
        opt_parts.append(f'<option value="{ov}"{selected}>{ol}</option>')

    spinner_html = (
        '<span class="dj-dependent-select__spinner" aria-hidden="true"></span>'
        if loading else ""
    )

    error_html = (
        f'<span class="form-error-message" role="alert">{e_error}</span>'
        if error else ""
    )

    return mark_safe(
        f'<div class="{cls}">'
        f'{label_html}'
        f'<div class="dj-dependent-select__control">'
        f'<select name="{e_name}" id="{e_name}" '
        f'data-parent="{e_parent}" '
        f'data-source-event="{e_source_event}" '
        f'dj-change="{e_source_event}"'
        f'{disabled_attr}{required_attr}>'
        f'{"".join(opt_parts)}'
        f'</select>'
        f'{spinner_html}'
        f'</div>'
        f'{error_html}'
        f'</div>'
    )


# --- Currency Input (#109) ---

CURRENCY_SYMBOLS = {
    "USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "JPY": "\u00a5",
    "CAD": "CA$", "AUD": "A$", "CHF": "CHF", "CNY": "\u00a5",
    "INR": "\u20b9", "BRL": "R$", "KRW": "\u20a9", "MXN": "MX$",
}


@register.simple_tag
def currency_input(name="", currency="USD", value="", label="",
                   min=None, max=None, step="0.01", placeholder="0.00",
                   event="", disabled=False, required=False,
                   error="", custom_class=""):
    """Numeric input with currency symbol prefix and formatting hints.

    Args:
        name: Input name attribute.
        currency: Currency code (e.g. USD, EUR, GBP). Determines prefix symbol.
        value: Current numeric value.
        label: Optional label text.
        min: Minimum value.
        max: Maximum value.
        step: Step increment (default 0.01 for cents).
        placeholder: Placeholder text.
        event: dj-input event name (defaults to name).
        disabled: Disable the input.
        required: Mark field as required.
        error: Error message to display.
        custom_class: Extra CSS class.
    """
    if isinstance(disabled, str):
        disabled = disabled.lower() not in ("false", "0", "")
    if isinstance(required, str):
        required = required.lower() not in ("false", "0", "")

    e_name = conditional_escape(name)
    e_currency = conditional_escape(str(currency).upper())
    e_value = conditional_escape(str(value))
    e_label = conditional_escape(label)
    e_placeholder = conditional_escape(placeholder)
    e_step = conditional_escape(str(step))
    e_event = conditional_escape(event or name)
    e_error = conditional_escape(error)
    e_class = conditional_escape(custom_class)

    symbol = CURRENCY_SYMBOLS.get(str(currency).upper(), str(currency).upper())
    e_symbol = conditional_escape(symbol)

    disabled_attr = " disabled" if disabled else ""
    required_attr = " required" if required else ""
    min_attr = f' min="{conditional_escape(str(min))}"' if min is not None else ""
    max_attr = f' max="{conditional_escape(str(max))}"' if max is not None else ""

    cls = "dj-currency-input"
    if error:
        cls += " dj-currency-input--error"
    if e_class:
        cls += f" {e_class}"

    label_html = ""
    if label:
        req_mark = ' <span class="form-required">*</span>' if required else ""
        label_html = (
            f'<label class="form-label" for="{e_name}">'
            f'{e_label}{req_mark}</label>'
        )

    error_html = (
        f'<span class="form-error-message" role="alert">{e_error}</span>'
        if error else ""
    )

    return mark_safe(
        f'<div class="{cls}">'
        f'{label_html}'
        f'<div class="dj-currency-input__control">'
        f'<span class="dj-currency-input__symbol">{e_symbol}</span>'
        f'<input type="number" name="{e_name}" id="{e_name}" '
        f'value="{e_value}" placeholder="{e_placeholder}" '
        f'step="{e_step}"{min_attr}{max_attr} '
        f'data-currency="{e_currency}" '
        f'dj-input="{e_event}" '
        f'class="dj-currency-input__field"'
        f'{disabled_attr}{required_attr}>'
        f'<span class="dj-currency-input__code">{e_currency}</span>'
        f'</div>'
        f'{error_html}'
        f'</div>'
    )


# --- Form Validation Display (#110) ---

@register.simple_tag
def form_errors(form=None, custom_class=""):
    """Render all form-level (non-field) validation errors.

    Args:
        form: A Django form instance.
        custom_class: Extra CSS class.
    """
    if form is None or not hasattr(form, "non_field_errors"):
        return ""

    errors = form.non_field_errors()
    if not errors:
        return ""

    e_class = conditional_escape(custom_class)
    cls = "dj-form-errors"
    if e_class:
        cls += f" {e_class}"

    items = []
    for err in errors:
        items.append(
            f'<li class="dj-form-errors__item">{conditional_escape(str(err))}</li>'
        )

    return mark_safe(
        f'<div class="{cls}" role="alert">'
        f'<ul class="dj-form-errors__list">{"".join(items)}</ul>'
        f'</div>'
    )


@register.simple_tag
def field_error(field=None, custom_class=""):
    """Render inline validation error for a single form field.

    Args:
        field: A Django BoundField instance (e.g. form.email).
        custom_class: Extra CSS class.
    """
    if field is None:
        return ""

    # Support both BoundField and a raw errors list
    if hasattr(field, "errors"):
        errors = field.errors
    else:
        return ""

    if not errors:
        return ""

    e_class = conditional_escape(custom_class)
    cls = "dj-field-error"
    if e_class:
        cls += f" {e_class}"

    items = []
    for err in errors:
        items.append(
            f'<span class="dj-field-error__message">{conditional_escape(str(err))}</span>'
        )

    return mark_safe(
        f'<div class="{cls}" role="alert">{"".join(items)}</div>'
    )


# ---------------------------------------------------------------------------
# DJANGO INTEGRATION COMPONENTS
# ---------------------------------------------------------------------------

# --- Django Form Renderer (#73) ---

# Mapping of Django form field class names to djust component renderers.
_FIELD_TYPE_MAP = {
    "CharField": "text",
    "EmailField": "email",
    "URLField": "url",
    "IntegerField": "number",
    "FloatField": "number",
    "DecimalField": "number",
    "DateField": "date",
    "DateTimeField": "datetime-local",
    "TimeField": "time",
    "SlugField": "text",
    "UUIDField": "text",
    "GenericIPAddressField": "text",
    "FilePathField": "text",
    "TypedChoiceField": "select",
    "ChoiceField": "select",
    "ModelChoiceField": "select",
    "BooleanField": "checkbox",
    "NullBooleanField": "checkbox",
    "FileField": "file",
    "ImageField": "file",
    "TypedMultipleChoiceField": "select_multiple",
    "MultipleChoiceField": "select_multiple",
    "ModelMultipleChoiceField": "select_multiple",
}


def _get_field_type(bound_field):
    """Determine the djust component type for a Django BoundField."""
    field = bound_field.field
    cls_name = type(field).__name__

    # Check widget override — textarea widget means textarea
    widget_cls = type(field.widget).__name__ if hasattr(field, "widget") else ""
    if widget_cls in ("Textarea", "AdminTextareaWidget"):
        return "textarea"
    if widget_cls in ("CheckboxInput",):
        return "checkbox"
    if widget_cls in ("RadioSelect",):
        return "radio_group"
    if widget_cls in ("CheckboxSelectMultiple",):
        return "checkbox_group"
    if widget_cls in ("Select", "NullBooleanSelect"):
        if cls_name not in ("BooleanField", "NullBooleanField"):
            return "select"
    if widget_cls in ("SelectMultiple",):
        return "select_multiple"
    if widget_cls in ("PasswordInput",):
        return "password"
    if widget_cls in ("HiddenInput", "MultipleHiddenInput"):
        return "hidden"
    if widget_cls in ("FileInput", "ClearableFileInput"):
        return "file"

    return _FIELD_TYPE_MAP.get(cls_name, "text")


def _get_choices(bound_field):
    """Extract choices from a Django BoundField as list of (value, label) tuples."""
    field = bound_field.field
    if hasattr(field, "choices"):
        choices = field.choices
        # choices can be a callable
        if callable(choices):
            choices = choices()
        return [(str(v), str(l)) for v, l in choices]
    return []


def _render_field(bound_field, event_prefix=""):
    """Render a single Django BoundField as the appropriate djust component HTML."""
    field_type = _get_field_type(bound_field)
    name = bound_field.html_name if hasattr(bound_field, "html_name") else bound_field.name
    label = bound_field.label or ""
    help_text = str(bound_field.help_text) if hasattr(bound_field, "help_text") and bound_field.help_text else ""
    required = bound_field.field.required if hasattr(bound_field, "field") else False
    disabled = getattr(bound_field.field, "disabled", False) if hasattr(bound_field, "field") else False
    errors = list(bound_field.errors) if hasattr(bound_field, "errors") and bound_field.errors else []
    error_msg = errors[0] if errors else ""

    # Get current value
    value = ""
    if hasattr(bound_field, "value"):
        v = bound_field.value()
        if v is not None:
            value = str(v)

    e_name = conditional_escape(name)
    e_label = conditional_escape(label)
    e_value = conditional_escape(value)
    e_helper = conditional_escape(help_text)
    e_error = conditional_escape(error_msg)
    dj_event = conditional_escape(event_prefix + name if event_prefix else name)

    required_attr = " required" if required else ""
    disabled_attr = " disabled" if disabled else ""

    required_span = '<span class="form-required"> *</span>' if required else ""
    error_cls = " form-input-error" if error_msg else ""
    label_html = (
        f'<label class="form-label" for="{e_name}">{e_label}{required_span}</label>'
        if label else ""
    )
    error_html = f'<span class="form-error-message">{e_error}</span>' if error_msg else ""
    helper_html = f'<span class="form-helper">{e_helper}</span>' if help_text else ""

    # Render all field errors (multiple) below the first
    extra_errors_html = ""
    if len(errors) > 1:
        extra_items = "".join(
            f'<span class="form-error-message">{conditional_escape(str(e))}</span>'
            for e in errors[1:]
        )
        extra_errors_html = extra_items

    if field_type == "hidden":
        return f'<input type="hidden" name="{e_name}" id="{e_name}" value="{e_value}">'

    if field_type == "checkbox":
        checked_attr = " checked" if value and value not in ("False", "false", "0", "") else ""
        return (
            f'<div class="form-group">'
            f'<div class="form-checkbox-wrapper">'
            f'<input class="form-checkbox" type="checkbox" '
            f'name="{e_name}" id="{e_name}" value="on" '
            f'dj-change="{dj_event}"{checked_attr}{required_attr}{disabled_attr}>'
            f'<label class="form-checkbox-label" for="{e_name}">{e_label}</label>'
            f'</div>'
            f'{error_html}{extra_errors_html}{helper_html}'
            f'</div>'
        )

    if field_type == "textarea":
        return (
            f'<div class="form-group">'
            f'{label_html}'
            f'<textarea class="form-input{error_cls}" name="{e_name}" id="{e_name}" '
            f'rows="4" dj-input="{dj_event}"{required_attr}{disabled_attr}>'
            f'{e_value}</textarea>'
            f'{error_html}{extra_errors_html}{helper_html}'
            f'</div>'
        )

    if field_type in ("select", "select_multiple"):
        choices = _get_choices(bound_field)
        multiple_attr = " multiple" if field_type == "select_multiple" else ""
        select_error_cls = " form-select-error" if error_msg else ""
        options_html = ""
        for ov, ol in choices:
            selected_attr = ' selected' if str(ov) == str(value) else ""
            options_html += (
                f'<option value="{conditional_escape(ov)}"{selected_attr}>'
                f'{conditional_escape(ol)}</option>'
            )
        return (
            f'<div class="form-group">'
            f'{label_html}'
            f'<select class="form-select{select_error_cls}" name="{e_name}" id="{e_name}" '
            f'dj-change="{dj_event}"{required_attr}{disabled_attr}{multiple_attr}>'
            f'{options_html}'
            f'</select>'
            f'{error_html}{extra_errors_html}{helper_html}'
            f'</div>'
        )

    if field_type == "radio_group":
        choices = _get_choices(bound_field)
        radios = ""
        for ov, ol in choices:
            checked_attr = " checked" if str(ov) == str(value) else ""
            radio_id = conditional_escape(f"{name}_{ov}")
            radios += (
                f'<div class="form-radio-wrapper">'
                f'<input class="form-radio" type="radio" '
                f'name="{e_name}" id="{radio_id}" value="{conditional_escape(ov)}" '
                f'dj-change="{dj_event}"{checked_attr}{disabled_attr}>'
                f'<label class="form-radio-label" for="{radio_id}">{conditional_escape(ol)}</label>'
                f'</div>'
            )
        return (
            f'<div class="form-group">'
            f'{label_html}'
            f'{radios}'
            f'{error_html}{extra_errors_html}{helper_html}'
            f'</div>'
        )

    if field_type == "checkbox_group":
        choices = _get_choices(bound_field)
        # value might be a list for multiple checkboxes
        selected_values = value.split(",") if value else []
        checks = ""
        for ov, ol in choices:
            checked_attr = " checked" if ov in selected_values else ""
            cb_id = conditional_escape(f"{name}_{ov}")
            checks += (
                f'<div class="form-checkbox-wrapper">'
                f'<input class="form-checkbox" type="checkbox" '
                f'name="{e_name}" id="{cb_id}" value="{conditional_escape(ov)}" '
                f'dj-change="{dj_event}"{checked_attr}{disabled_attr}>'
                f'<label class="form-checkbox-label" for="{cb_id}">{conditional_escape(ol)}</label>'
                f'</div>'
            )
        return (
            f'<div class="form-group">'
            f'{label_html}'
            f'{checks}'
            f'{error_html}{extra_errors_html}{helper_html}'
            f'</div>'
        )

    if field_type == "file":
        return (
            f'<div class="form-group">'
            f'{label_html}'
            f'<input class="form-input" type="file" '
            f'name="{e_name}" id="{e_name}"{required_attr}{disabled_attr}>'
            f'{error_html}{extra_errors_html}{helper_html}'
            f'</div>'
        )

    if field_type == "password":
        return (
            f'<div class="form-group">'
            f'{label_html}'
            f'<input class="form-input{error_cls}" type="password" '
            f'name="{e_name}" id="{e_name}" '
            f'dj-input="{dj_event}"{required_attr}{disabled_attr}>'
            f'{error_html}{extra_errors_html}{helper_html}'
            f'</div>'
        )

    # Default: text-like input (text, email, url, number, date, etc.)
    input_type = field_type if field_type in (
        "email", "url", "number", "date", "datetime-local", "time"
    ) else "text"
    e_type = conditional_escape(input_type)
    placeholder = ""
    if hasattr(bound_field.field, "widget") and hasattr(bound_field.field.widget, "attrs"):
        placeholder = bound_field.field.widget.attrs.get("placeholder", "")
    e_placeholder = conditional_escape(placeholder)

    return (
        f'<div class="form-group">'
        f'{label_html}'
        f'<input class="form-input{error_cls}" type="{e_type}" '
        f'name="{e_name}" id="{e_name}" value="{e_value}" '
        f'placeholder="{e_placeholder}" '
        f'dj-input="{dj_event}"{required_attr}{disabled_attr}>'
        f'{error_html}{extra_errors_html}{helper_html}'
        f'</div>'
    )


@register.simple_tag
def dj_form(form=None, event_prefix="", action="", method="post",
            submit_label="Submit", submit_event="", custom_class="",
            show_errors=True):
    """Auto-render a Django Form or ModelForm using djust-components.

    Maps Django field types to djust input components:
      CharField -> dj_input (text)
      EmailField -> dj_input (email)
      ChoiceField -> dj_select
      BooleanField -> dj_checkbox
      TextField/Textarea widget -> dj_textarea
      etc.

    Args:
        form: A Django Form or ModelForm instance.
        event_prefix: Prefix for dj-input/dj-change event names (e.g. "myform_").
        action: Form action URL (empty = no action attribute).
        method: Form method (default "post").
        submit_label: Label for the submit button.
        submit_event: djust event for the submit button (if empty, uses standard form submit).
        custom_class: Extra CSS class for the form wrapper.
        show_errors: Show non-field errors at the top (default True).
    """
    if form is None:
        return ""

    e_class = conditional_escape(custom_class)
    e_action = conditional_escape(action)
    e_method = conditional_escape(method)
    e_submit_label = conditional_escape(submit_label)
    e_submit_event = conditional_escape(submit_event)

    cls = "dj-form"
    if e_class:
        cls += f" {e_class}"

    # Non-field errors
    errors_html = ""
    if show_errors and hasattr(form, "non_field_errors"):
        non_field = form.non_field_errors()
        if non_field:
            items = "".join(
                f'<li class="dj-form-errors__item">{conditional_escape(str(e))}</li>'
                for e in non_field
            )
            errors_html = (
                f'<div class="dj-form-errors" role="alert">'
                f'<ul class="dj-form-errors__list">{items}</ul>'
                f'</div>'
            )

    # Render each visible field
    fields_html = ""
    visible_fields = form.visible_fields() if hasattr(form, "visible_fields") else []
    for bf in visible_fields:
        fields_html += _render_field(bf, event_prefix=event_prefix)

    # Hidden fields
    hidden_html = ""
    hidden_fields = form.hidden_fields() if hasattr(form, "hidden_fields") else []
    for bf in hidden_fields:
        h_name = bf.html_name if hasattr(bf, "html_name") else bf.name
        h_value = ""
        if hasattr(bf, "value"):
            v = bf.value()
            if v is not None:
                h_value = str(v)
        hidden_html += (
            f'<input type="hidden" name="{conditional_escape(h_name)}" '
            f'id="{conditional_escape(h_name)}" value="{conditional_escape(h_value)}">'
        )

    # Action/method attributes
    action_attr = f' action="{e_action}"' if action else ""
    method_attr = f' method="{e_method}"'

    # Submit button
    if e_submit_event:
        submit_html = (
            f'<div class="form-group dj-form__actions">'
            f'<button class="dj-btn dj-btn--primary" type="button" '
            f'dj-click="{e_submit_event}">{e_submit_label}</button>'
            f'</div>'
        )
    else:
        submit_html = (
            f'<div class="form-group dj-form__actions">'
            f'<button class="dj-btn dj-btn--primary" type="submit">'
            f'{e_submit_label}</button>'
            f'</div>'
        )

    return mark_safe(
        f'<form class="{cls}"{action_attr}{method_attr}>'
        f'{errors_html}'
        f'{fields_html}'
        f'{hidden_html}'
        f'{submit_html}'
        f'</form>'
    )


# --- Django ModelForm Table (#74) ---

def _get_verbose_name(field):
    """Get verbose name from a Django model field."""
    if hasattr(field, "verbose_name"):
        return str(field.verbose_name).title()
    return str(field.name).replace("_", " ").title()


def _is_sortable_field(field):
    """Determine if a model field should be sortable."""
    cls_name = type(field).__name__
    # Most concrete fields are sortable; relations and file fields are not
    non_sortable = {"ManyToManyField", "ManyToManyRel", "ManyToOneRel",
                    "FileField", "ImageField", "JSONField"}
    return cls_name not in non_sortable


def _is_filterable_field(field):
    """Determine if a model field should be filterable."""
    cls_name = type(field).__name__
    filterable = {"CharField", "TextField", "SlugField", "EmailField",
                  "URLField", "BooleanField", "NullBooleanField",
                  "IntegerField", "FloatField", "DecimalField",
                  "ChoiceField", "ForeignKey"}
    return cls_name in filterable


def _get_filter_type(field):
    """Get appropriate filter type for a model field."""
    cls_name = type(field).__name__
    if cls_name in ("BooleanField", "NullBooleanField"):
        return "select"
    if cls_name in ("IntegerField", "FloatField", "DecimalField"):
        return "number"
    if cls_name == "ForeignKey":
        return "select"
    if hasattr(field, "choices") and field.choices:
        return "select"
    return "text"


def _get_filter_options(field):
    """Get filter options for fields with choices."""
    if hasattr(field, "choices") and field.choices:
        return [{"value": str(v), "label": str(l)} for v, l in field.choices]
    cls_name = type(field).__name__
    if cls_name in ("BooleanField",):
        return [{"value": "true", "label": "Yes"}, {"value": "false", "label": "No"}]
    if cls_name in ("NullBooleanField",):
        return [
            {"value": "true", "label": "Yes"},
            {"value": "false", "label": "No"},
            {"value": "null", "label": "Unknown"},
        ]
    return []


def _infer_columns(model_meta, exclude=None, include=None):
    """Infer data_table columns from a Django model's _meta."""
    exclude = set(exclude or [])
    fields = model_meta.get_fields() if hasattr(model_meta, "get_fields") else []

    columns = []
    for field in fields:
        # Skip reverse relations
        if hasattr(field, "related_model") and not hasattr(field, "column"):
            continue
        name = field.name if hasattr(field, "name") else str(field)
        if name in exclude:
            continue
        if include and name not in include:
            continue

        col = {
            "key": name,
            "label": _get_verbose_name(field),
            "sortable": _is_sortable_field(field),
        }
        if _is_filterable_field(field):
            col["filterable"] = True
            col["filter_type"] = _get_filter_type(field)
            options = _get_filter_options(field)
            if options:
                col["filter_options"] = options

        columns.append(col)

    return columns


def _queryset_to_rows(queryset, columns, row_key="id"):
    """Convert a Django QuerySet to a list of row dicts for data_table."""
    rows = []
    col_keys = [c["key"] for c in columns]
    for obj in queryset:
        row = {}
        for key in col_keys:
            val = getattr(obj, key, "")
            # Handle ForeignKey — use str() for display
            if hasattr(val, "pk"):
                val = str(val)
            elif callable(val) and not isinstance(val, str):
                try:
                    val = val()
                except Exception:
                    val = ""
            row[key] = val if val is not None else ""
        # Ensure row_key is present
        if row_key not in row:
            pk = getattr(obj, "pk", None) or getattr(obj, "id", None) or ""
            row[row_key] = pk
        rows.append(row)
    return rows


@register.simple_tag
def model_table(queryset=None, exclude=None, include=None,
                sort_by="", sort_desc=False, sort_event="table_sort",
                page=1, total_pages=1, paginate=False,
                page_event="table_page",
                prev_event="table_prev", next_event="table_next",
                search=False, search_query="", search_event="table_search",
                filters=None, filter_event="table_filter",
                selectable=False, selected_rows=None, select_event="table_select",
                row_key="id", loading=False,
                empty_title="No data", empty_description="",
                striped=True, compact=False,
                custom_class=""):
    """Auto-generate a Data Table Pro from a Django QuerySet.

    Introspects model fields to infer columns. Supports sorting, filtering,
    pagination, search, and selection — all delegated to the existing data_table
    component.

    Args:
        queryset: A Django QuerySet instance.
        exclude: List of field names to exclude from the table.
        include: List of field names to include (if set, only these are shown).
        sort_by: Current sort column key.
        sort_desc: Sort descending?
        sort_event: djust event for sorting.
        page: Current page number.
        total_pages: Total pages.
        paginate: Show pagination controls.
        page_event: Pagination event name.
        prev_event: Previous page event.
        next_event: Next page event.
        search: Show global search box.
        search_query: Current search value.
        search_event: Search event name.
        filters: Per-column filter values dict.
        filter_event: Filter event name.
        selectable: Enable row selection.
        selected_rows: List of selected row IDs.
        select_event: Selection event name.
        row_key: Key field for row identity.
        loading: Show loading state.
        empty_title: Empty state title.
        empty_description: Empty state description.
        striped: Alternating row backgrounds (default True for model tables).
        compact: Reduced padding.
        custom_class: Extra CSS class for the wrapper div.
    """
    if queryset is None:
        return ""

    # Get model metadata
    model = None
    if hasattr(queryset, "model"):
        model = queryset.model
    elif hasattr(queryset, "_meta"):
        model = queryset

    if model is None:
        return "<!-- model_table: queryset has no model -->"

    meta = model._meta if hasattr(model, "_meta") else None
    if meta is None:
        return "<!-- model_table: model has no _meta -->"

    # Infer columns
    columns = _infer_columns(meta, exclude=exclude, include=include)
    if not columns:
        return "<!-- model_table: no columns inferred -->"

    # Convert queryset to rows
    rows = _queryset_to_rows(queryset, columns, row_key=row_key)

    # Escape values in rows for safe rendering
    safe_rows = []
    for row in rows:
        safe_row = {}
        for k, v in row.items():
            safe_row[k] = conditional_escape(str(v)) if v is not None else ""
        safe_rows.append(safe_row)

    # Build the table HTML directly (composing the data_table pattern)
    e_class = conditional_escape(custom_class)
    e_sort_event = conditional_escape(sort_event)
    e_search_event = conditional_escape(search_event)
    e_filter_event = conditional_escape(filter_event)
    e_page_event = conditional_escape(page_event)
    e_prev_event = conditional_escape(prev_event)
    e_next_event = conditional_escape(next_event)
    e_select_event = conditional_escape(select_event)
    e_empty_title = conditional_escape(empty_title)
    e_empty_desc = conditional_escape(empty_description)
    e_search_query = conditional_escape(search_query)

    if selected_rows is None:
        selected_rows = []
    if filters is None:
        filters = {}

    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 1
    try:
        total_pages = int(total_pages)
    except (ValueError, TypeError):
        total_pages = 1

    wrapper_cls = "dj-model-table"
    if e_class:
        wrapper_cls += f" {e_class}"

    density_cls = " data-table--compact" if compact else ""
    striped_cls = " data-table--striped" if striped else ""

    # Search bar
    search_html = ""
    if search:
        search_html = (
            f'<div class="data-table__search">'
            f'<input type="text" class="data-table__search-input" '
            f'placeholder="Search..." value="{e_search_query}" '
            f'dj-input="{e_search_event}">'
            f'</div>'
        )

    # Table header
    header_cells = ""
    if selectable:
        header_cells += '<th class="data-table__th data-table__th--select"><input type="checkbox"></th>'
    for col in columns:
        col_key = conditional_escape(col["key"])
        col_label = conditional_escape(col["label"])
        sort_cls = ""
        sort_attr = ""
        if col.get("sortable"):
            sort_cls = " data-table__th--sortable"
            sort_attr = f' dj-click="{e_sort_event}" dj-value-column="{col_key}"'
            if sort_by == col["key"]:
                arrow = " &#9660;" if sort_desc else " &#9650;"
                col_label += arrow
                sort_cls += " data-table__th--sorted"

        # Filter row is separate; just header for now
        filter_attr = ""
        header_cells += f'<th class="data-table__th{sort_cls}"{sort_attr}{filter_attr}>{col_label}</th>'

    # Filter row
    filter_row = ""
    has_filters = any(col.get("filterable") for col in columns)
    if has_filters:
        filter_cells = ""
        if selectable:
            filter_cells += '<td class="data-table__filter-cell"></td>'
        for col in columns:
            if col.get("filterable"):
                col_key = conditional_escape(col["key"])
                fval = conditional_escape(str(filters.get(col["key"], "")))
                ft = col.get("filter_type", "text")
                if ft == "select" and col.get("filter_options"):
                    opts = '<option value="">All</option>'
                    for fo in col["filter_options"]:
                        fov = conditional_escape(str(fo.get("value", "")))
                        fol = conditional_escape(str(fo.get("label", "")))
                        sel = " selected" if fov == fval else ""
                        opts += f'<option value="{fov}"{sel}>{fol}</option>'
                    filter_cells += (
                        f'<td class="data-table__filter-cell">'
                        f'<select class="data-table__filter-select" '
                        f'dj-change="{e_filter_event}" dj-value-column="{col_key}">'
                        f'{opts}</select></td>'
                    )
                else:
                    filter_cells += (
                        f'<td class="data-table__filter-cell">'
                        f'<input type="{conditional_escape(ft)}" '
                        f'class="data-table__filter-input" value="{fval}" '
                        f'dj-input="{e_filter_event}" dj-value-column="{col_key}">'
                        f'</td>'
                    )
            else:
                filter_cells += '<td class="data-table__filter-cell"></td>'
        filter_row = f'<tr class="data-table__filter-row">{filter_cells}</tr>'

    # Table body
    body_rows = ""
    if loading:
        col_count = len(columns) + (1 if selectable else 0)
        body_rows = (
            f'<tr class="data-table__loading-row">'
            f'<td colspan="{col_count}" class="data-table__loading-cell">'
            f'<div class="dj-spinner"></div></td></tr>'
        )
    elif not safe_rows:
        col_count = len(columns) + (1 if selectable else 0)
        body_rows = (
            f'<tr class="data-table__empty-row">'
            f'<td colspan="{col_count}" class="data-table__empty-cell">'
            f'<div class="data-table__empty-title">{e_empty_title}</div>'
            f'<div class="data-table__empty-desc">{e_empty_desc}</div>'
            f'</td></tr>'
        )
    else:
        for row in safe_rows:
            row_id = row.get(row_key, "")
            row_selected = str(row_id) in [str(s) for s in selected_rows]
            selected_cls = " data-table__tr--selected" if row_selected else ""
            cells = ""
            if selectable:
                chk = " checked" if row_selected else ""
                cells += (
                    f'<td class="data-table__td data-table__td--select">'
                    f'<input type="checkbox" dj-change="{e_select_event}" '
                    f'dj-value-row="{conditional_escape(str(row_id))}"{chk}></td>'
                )
            for col in columns:
                cell_val = row.get(col["key"], "")
                cells += f'<td class="data-table__td">{cell_val}</td>'
            body_rows += f'<tr class="data-table__tr{selected_cls}">{cells}</tr>'

    # Pagination
    pagination_html = ""
    if paginate:
        prev_disabled = " disabled" if page <= 1 else ""
        next_disabled = " disabled" if page >= total_pages else ""
        pagination_html = (
            f'<div class="data-table__pagination">'
            f'<button class="data-table__page-btn" dj-click="{e_prev_event}"{prev_disabled}>'
            f'&laquo; Prev</button>'
            f'<span class="data-table__page-info">Page {page} of {total_pages}</span>'
            f'<button class="data-table__page-btn" dj-click="{e_next_event}"{next_disabled}>'
            f'Next &raquo;</button>'
            f'</div>'
        )

    return mark_safe(
        f'<div class="{wrapper_cls}">'
        f'{search_html}'
        f'<div class="data-table__wrapper">'
        f'<table class="data-table{striped_cls}{density_cls}">'
        f'<thead><tr class="data-table__header-row">{header_cells}</tr>'
        f'{filter_row}</thead>'
        f'<tbody>{body_rows}</tbody>'
        f'</table></div>'
        f'{pagination_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Sidebar Nav (#86)
# ---------------------------------------------------------------------------

class SidebarItemNode(template.Node):
    """A single sidebar menu item."""
    def __init__(self, kwargs, nodelist):
        self.kwargs = kwargs
        self.nodelist = nodelist  # sub-items if nested

    def render(self, context):
        return ""  # rendered by parent SidebarNode


class SidebarSectionNode(template.Node):
    """A section header within a sidebar."""
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        return ""  # rendered by parent SidebarNode


class SidebarNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def _render_item(self, item, context, active_path, level=0):
        kw = {k: _resolve(v, context) for k, v in item.kwargs.items()}
        label = kw.get("label", "")
        href = kw.get("href", "#")
        icon = kw.get("icon", "")
        item_id = kw.get("id", "")
        event = kw.get("event", "")

        is_active = item_id == active_path or href == active_path
        active_cls = " dj-sidebar__item--active" if is_active else ""
        level_cls = f" dj-sidebar__item--level-{level}" if level > 0 else ""

        icon_html = ""
        if icon:
            icon_html = f'<span class="dj-sidebar__icon">{conditional_escape(icon)}</span>'

        # Check for nested sub-items
        sub_items = [n for n in item.nodelist if isinstance(n, SidebarItemNode)]

        if event:
            trigger = (
                f'<button class="dj-sidebar__link{active_cls}{level_cls}" '
                f'dj-click="{conditional_escape(event)}">'
                f'{icon_html}<span class="dj-sidebar__label">'
                f'{conditional_escape(label)}</span></button>'
            )
        else:
            trigger = (
                f'<a class="dj-sidebar__link{active_cls}{level_cls}" '
                f'href="{conditional_escape(href)}">'
                f'{icon_html}<span class="dj-sidebar__label">'
                f'{conditional_escape(label)}</span></a>'
            )

        if sub_items:
            children = "".join(
                self._render_item(si, context, active_path, level + 1)
                for si in sub_items
            )
            return (
                f'<li class="dj-sidebar__item dj-sidebar__item--parent">'
                f'{trigger}'
                f'<ul class="dj-sidebar__submenu">{children}</ul></li>'
            )

        return f'<li class="dj-sidebar__item">{trigger}</li>'

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        sidebar_id = kw.get("id", "sidebar")
        active = kw.get("active", "")
        collapsed = kw.get("collapsed", False)
        title = kw.get("title", "")
        toggle_event = kw.get("toggle_event", "toggle_sidebar")
        custom_class = kw.get("class", "")

        collapsed_cls = " dj-sidebar--collapsed" if collapsed else ""
        cls = f"dj-sidebar{collapsed_cls}"
        if custom_class:
            cls += f" {conditional_escape(custom_class)}"

        header_html = ""
        if title:
            header_html = (
                f'<div class="dj-sidebar__header">'
                f'<span class="dj-sidebar__title">{conditional_escape(title)}</span>'
                f'<button class="dj-sidebar__toggle" dj-click="{conditional_escape(toggle_event)}">'
                f'&#9776;</button></div>'
            )

        # Collect sections and items
        parts = []
        for node in self.nodelist:
            if isinstance(node, SidebarSectionNode):
                skw = {k: _resolve(v, context) for k, v in node.kwargs.items()}
                section_label = skw.get("label", "")
                parts.append(
                    f'<li class="dj-sidebar__section">'
                    f'<span class="dj-sidebar__section-label">'
                    f'{conditional_escape(section_label)}</span></li>'
                )
            elif isinstance(node, SidebarItemNode):
                parts.append(self._render_item(node, context, active))

        menu_html = f'<ul class="dj-sidebar__menu">{"".join(parts)}</ul>'

        # Mobile overlay backdrop
        backdrop = (
            f'<div class="dj-sidebar__backdrop" dj-click="{conditional_escape(toggle_event)}"></div>'
        )

        return mark_safe(
            f'<nav class="{cls}" id="{conditional_escape(sidebar_id)}" role="navigation">'
            f'{header_html}{menu_html}{backdrop}</nav>'
        )


@register.tag("sidebar")
def do_sidebar(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endsidebar",))
    parser.delete_first_token()
    return SidebarNode(nodelist, kwargs)


@register.tag("sidebar_item")
def do_sidebar_item(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endsidebar_item",))
    parser.delete_first_token()
    return SidebarItemNode(kwargs, nodelist)


@register.tag("sidebar_section")
def do_sidebar_section(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return SidebarSectionNode(kwargs)


# ---------------------------------------------------------------------------
# Navigation Menu (#90)
# ---------------------------------------------------------------------------

class NavItemNode(template.Node):
    """A single nav menu item, optionally containing dropdown children."""
    def __init__(self, kwargs, nodelist):
        self.kwargs = kwargs
        self.nodelist = nodelist

    def render(self, context):
        return ""  # rendered by parent NavMenuNode


class NavMenuNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def _render_nav_item(self, item, context, active_path):
        kw = {k: _resolve(v, context) for k, v in item.kwargs.items()}
        label = kw.get("label", "")
        href = kw.get("href", "#")
        item_id = kw.get("id", "")
        event = kw.get("event", "")
        mega = kw.get("mega", False)

        is_active = item_id == active_path or href == active_path
        active_cls = " dj-nav__item--active" if is_active else ""

        # Check for sub-items (dropdown children)
        sub_items = [n for n in item.nodelist if isinstance(n, NavItemNode)]

        if sub_items:
            children = "".join(
                self._render_dropdown_item(si, context, active_path)
                for si in sub_items
            )
            mega_cls = " dj-nav__dropdown--mega" if mega else ""
            return (
                f'<li class="dj-nav__item dj-nav__item--has-dropdown{active_cls}">'
                f'<button class="dj-nav__link">{conditional_escape(label)}'
                f'<span class="dj-nav__caret">&#9662;</span></button>'
                f'<div class="dj-nav__dropdown{mega_cls}">'
                f'<ul class="dj-nav__dropdown-list">{children}</ul></div></li>'
            )

        if event:
            return (
                f'<li class="dj-nav__item{active_cls}">'
                f'<button class="dj-nav__link" dj-click="{conditional_escape(event)}">'
                f'{conditional_escape(label)}</button></li>'
            )

        return (
            f'<li class="dj-nav__item{active_cls}">'
            f'<a class="dj-nav__link" href="{conditional_escape(href)}">'
            f'{conditional_escape(label)}</a></li>'
        )

    def _render_dropdown_item(self, item, context, active_path):
        kw = {k: _resolve(v, context) for k, v in item.kwargs.items()}
        label = kw.get("label", "")
        href = kw.get("href", "#")
        desc = kw.get("description", "")
        event = kw.get("event", "")
        item_id = kw.get("id", "")

        is_active = item_id == active_path or href == active_path
        active_cls = " dj-nav__dropdown-item--active" if is_active else ""

        desc_html = ""
        if desc:
            desc_html = f'<span class="dj-nav__dropdown-desc">{conditional_escape(desc)}</span>'

        if event:
            return (
                f'<li class="dj-nav__dropdown-item{active_cls}">'
                f'<button class="dj-nav__dropdown-link" dj-click="{conditional_escape(event)}">'
                f'{conditional_escape(label)}{desc_html}</button></li>'
            )

        return (
            f'<li class="dj-nav__dropdown-item{active_cls}">'
            f'<a class="dj-nav__dropdown-link" href="{conditional_escape(href)}">'
            f'{conditional_escape(label)}{desc_html}</a></li>'
        )

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        nav_id = kw.get("id", "nav-menu")
        active = kw.get("active", "")
        brand = kw.get("brand", "")
        brand_href = kw.get("brand_href", "/")
        toggle_event = kw.get("toggle_event", "toggle_nav")
        mobile_open = kw.get("mobile_open", False)
        custom_class = kw.get("class", "")

        cls = "dj-nav"
        if custom_class:
            cls += f" {conditional_escape(custom_class)}"

        mobile_cls = " dj-nav__list--open" if mobile_open else ""

        brand_html = ""
        if brand:
            brand_html = (
                f'<a class="dj-nav__brand" href="{conditional_escape(brand_href)}">'
                f'{conditional_escape(brand)}</a>'
            )

        hamburger = (
            f'<button class="dj-nav__hamburger" dj-click="{conditional_escape(toggle_event)}" '
            f'aria-label="Toggle navigation">&#9776;</button>'
        )

        items = [n for n in self.nodelist if isinstance(n, NavItemNode)]
        items_html = "".join(
            self._render_nav_item(item, context, active) for item in items
        )

        return mark_safe(
            f'<nav class="{cls}" id="{conditional_escape(nav_id)}" role="navigation">'
            f'<div class="dj-nav__container">'
            f'{brand_html}{hamburger}'
            f'<ul class="dj-nav__list{mobile_cls}">{items_html}</ul>'
            f'</div></nav>'
        )


@register.tag("nav_menu")
def do_nav_menu(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endnav_menu",))
    parser.delete_first_token()
    return NavMenuNode(nodelist, kwargs)


@register.tag("nav_item")
def do_nav_item(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endnav_item",))
    parser.delete_first_token()
    return NavItemNode(kwargs, nodelist)


# ---------------------------------------------------------------------------
# App Shell (#167)
# ---------------------------------------------------------------------------

class AppSidebarNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        return ""  # rendered by AppShellNode


class AppHeaderNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        return ""  # rendered by AppShellNode


class AppContentNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        return ""  # rendered by AppShellNode


class AppShellNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        shell_id = kw.get("id", "app-shell")
        sidebar_collapsed = kw.get("sidebar_collapsed", False)
        custom_class = kw.get("class", "")

        cls = "dj-app-shell"
        if sidebar_collapsed:
            cls += " dj-app-shell--sidebar-collapsed"
        if custom_class:
            cls += f" {conditional_escape(custom_class)}"

        # Find sub-nodes
        sidebar_nodes = [n for n in self.nodelist if isinstance(n, AppSidebarNode)]
        header_nodes = [n for n in self.nodelist if isinstance(n, AppHeaderNode)]
        content_nodes = [n for n in self.nodelist if isinstance(n, AppContentNode)]

        sidebar_html = ""
        if sidebar_nodes:
            sidebar_content = sidebar_nodes[0].nodelist.render(context)
            sidebar_html = f'<aside class="dj-app-shell__sidebar">{sidebar_content}</aside>'

        header_html = ""
        if header_nodes:
            header_content = header_nodes[0].nodelist.render(context)
            header_html = f'<header class="dj-app-shell__header">{header_content}</header>'

        content_html = ""
        if content_nodes:
            main_content = content_nodes[0].nodelist.render(context)
            content_html = f'<main class="dj-app-shell__content">{main_content}</main>'

        return mark_safe(
            f'<div class="{cls}" id="{conditional_escape(shell_id)}">'
            f'{sidebar_html}'
            f'<div class="dj-app-shell__main">'
            f'{header_html}{content_html}'
            f'</div></div>'
        )


@register.tag("app_shell")
def do_app_shell(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endapp_shell",))
    parser.delete_first_token()
    return AppShellNode(nodelist, kwargs)


@register.tag("app_sidebar")
def do_app_sidebar(parser, token):
    nodelist = parser.parse(("endapp_sidebar",))
    parser.delete_first_token()
    return AppSidebarNode(nodelist)


@register.tag("app_header")
def do_app_header(parser, token):
    nodelist = parser.parse(("endapp_header",))
    parser.delete_first_token()
    return AppHeaderNode(nodelist)


@register.tag("app_content")
def do_app_content(parser, token):
    nodelist = parser.parse(("endapp_content",))
    parser.delete_first_token()
    return AppContentNode(nodelist)


# ---------------------------------------------------------------------------
# Toolbar (#87)
# ---------------------------------------------------------------------------

class ToolbarSeparatorNode(template.Node):
    def render(self, context):
        return ""  # rendered by ToolbarNode


class ToolbarOverflowNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        return ""  # rendered by ToolbarNode


class ToolbarNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        toolbar_id = kw.get("id", f"toolbar-{uuid.uuid4().hex[:8]}")
        custom_class = kw.get("class", "")
        size = kw.get("size", "md")
        variant = kw.get("variant", "default")

        cls = f"dj-toolbar dj-toolbar--{conditional_escape(size)} dj-toolbar--{conditional_escape(variant)}"
        if custom_class:
            cls += f" {conditional_escape(custom_class)}"

        parts = []
        for node in self.nodelist:
            if isinstance(node, ToolbarSeparatorNode):
                parts.append('<div class="dj-toolbar__separator" role="separator"></div>')
            elif isinstance(node, ToolbarOverflowNode):
                overflow_content = node.nodelist.render(context)
                parts.append(
                    f'<div class="dj-toolbar__overflow">'
                    f'<button class="dj-toolbar__overflow-trigger" aria-label="More actions">'
                    f'<span class="dj-toolbar__overflow-icon">&#8942;</span></button>'
                    f'<div class="dj-toolbar__overflow-menu">{overflow_content}</div></div>'
                )
            else:
                rendered = node.render(context)
                if rendered.strip():
                    parts.append(f'<div class="dj-toolbar__group">{rendered}</div>')

        return mark_safe(
            f'<div class="{cls}" id="{conditional_escape(toolbar_id)}" role="toolbar">'
            f'{"".join(parts)}</div>'
        )


@register.tag("toolbar")
def do_toolbar(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endtoolbar",))
    parser.delete_first_token()
    return ToolbarNode(nodelist, kwargs)


@register.tag("toolbar_separator")
def do_toolbar_separator(parser, token):
    return ToolbarSeparatorNode()


@register.tag("toolbar_overflow")
def do_toolbar_overflow(parser, token):
    nodelist = parser.parse(("endtoolbar_overflow",))
    parser.delete_first_token()
    return ToolbarOverflowNode(nodelist)


# ---------------------------------------------------------------------------
# Inline Edit (#88)
# ---------------------------------------------------------------------------

class InlineEditNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        value = kw.get("value", "")
        event = kw.get("event", "inline_edit")
        field = kw.get("field", "")
        input_type = kw.get("type", "text")
        placeholder = kw.get("placeholder", "")
        custom_class = kw.get("class", "")
        editing = kw.get("editing", False)

        e_value = conditional_escape(str(value))
        e_event = conditional_escape(event)
        e_field = conditional_escape(field)
        e_placeholder = conditional_escape(placeholder)
        e_input_type = conditional_escape(input_type)

        cls = "dj-inline-edit"
        if editing:
            cls += " dj-inline-edit--editing"
        if custom_class:
            cls += f" {conditional_escape(custom_class)}"

        if editing:
            return mark_safe(
                f'<span class="{cls}">'
                f'<input class="dj-inline-edit__input" type="{e_input_type}" '
                f'value="{e_value}" placeholder="{e_placeholder}" '
                f'data-field="{e_field}" '
                f'dj-keydown.enter="{e_event}" '
                f'dj-blur="{e_event}" '
                f'dj-keydown.escape="inline_edit_cancel" '
                f'autofocus></span>'
            )
        else:
            return mark_safe(
                f'<span class="{cls}" dj-click="inline_edit_start" '
                f'data-field="{e_field}" title="Click to edit">'
                f'<span class="dj-inline-edit__display">{e_value}</span>'
                f'<span class="dj-inline-edit__icon">&#9998;</span></span>'
            )


@register.tag("inline_edit")
def do_inline_edit(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return InlineEditNode(kwargs)


# ---------------------------------------------------------------------------
# Filter Bar (#166)
# ---------------------------------------------------------------------------

class FilterSelectNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs
    def render(self, context):
        return ""  # rendered by FilterBarNode


class FilterDateRangeNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs
    def render(self, context):
        return ""  # rendered by FilterBarNode


class FilterSearchNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs
    def render(self, context):
        return ""  # rendered by FilterBarNode


class FilterBarNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        bar_id = kw.get("id", f"filter-bar-{uuid.uuid4().hex[:8]}")
        event = kw.get("event", "filter_change")
        custom_class = kw.get("class", "")
        clear_event = kw.get("clear_event", "filter_clear")

        cls = "dj-filter-bar"
        if custom_class:
            cls += f" {conditional_escape(custom_class)}"

        e_event = conditional_escape(event)
        e_clear = conditional_escape(clear_event)

        filter_nodes = [
            n for n in self.nodelist
            if isinstance(n, (FilterSelectNode, FilterDateRangeNode, FilterSearchNode))
        ]

        parts = []
        has_values = False
        for node in filter_nodes:
            nkw = {k: _resolve(v, context) for k, v in node.kwargs.items()}
            if isinstance(node, FilterSelectNode):
                name = conditional_escape(nkw.get("name", ""))
                label = conditional_escape(nkw.get("label", name))
                options = nkw.get("options", [])
                value = nkw.get("value", "")
                if value:
                    has_values = True
                opt_html = f'<option value="">{label}</option>'
                if isinstance(options, list):
                    for opt in options:
                        if isinstance(opt, dict):
                            ov = conditional_escape(str(opt.get("value", "")))
                            ol = conditional_escape(str(opt.get("label", ov)))
                        else:
                            ov = conditional_escape(str(opt))
                            ol = ov
                        selected = " selected" if str(opt.get("value", opt) if isinstance(opt, dict) else opt) == str(value) else ""
                        opt_html += f'<option value="{ov}"{selected}>{ol}</option>'
                parts.append(
                    f'<div class="dj-filter-bar__control dj-filter-bar__select-wrap">'
                    f'<select class="dj-filter-bar__select" name="{name}" '
                    f'dj-change="{e_event}">{opt_html}</select></div>'
                )
            elif isinstance(node, FilterDateRangeNode):
                name = conditional_escape(nkw.get("name", ""))
                label = conditional_escape(nkw.get("label", name))
                value_start = conditional_escape(str(nkw.get("start", "")))
                value_end = conditional_escape(str(nkw.get("end", "")))
                if value_start or value_end:
                    has_values = True
                parts.append(
                    f'<div class="dj-filter-bar__control dj-filter-bar__date-range">'
                    f'<label class="dj-filter-bar__label">{label}</label>'
                    f'<input class="dj-filter-bar__date" type="date" name="{name}_start" '
                    f'value="{value_start}" dj-change="{e_event}">'
                    f'<span class="dj-filter-bar__date-sep">&ndash;</span>'
                    f'<input class="dj-filter-bar__date" type="date" name="{name}_end" '
                    f'value="{value_end}" dj-change="{e_event}"></div>'
                )
            elif isinstance(node, FilterSearchNode):
                name = conditional_escape(nkw.get("name", ""))
                placeholder = conditional_escape(nkw.get("placeholder", "Search\u2026"))
                value = conditional_escape(str(nkw.get("value", "")))
                debounce = nkw.get("debounce", 300)
                if value:
                    has_values = True
                parts.append(
                    f'<div class="dj-filter-bar__control dj-filter-bar__search-wrap">'
                    f'<input class="dj-filter-bar__search" type="search" name="{name}" '
                    f'placeholder="{placeholder}" value="{value}" '
                    f'dj-input="{e_event}" dj-debounce="{int(debounce)}"></div>'
                )

        clear_html = ""
        if has_values:
            clear_html = (
                f'<div class="dj-filter-bar__actions">'
                f'<button class="dj-filter-bar__clear" dj-click="{e_clear}">Clear filters</button></div>'
            )

        return mark_safe(
            f'<div class="{cls}" id="{conditional_escape(bar_id)}" role="search">'
            f'<div class="dj-filter-bar__controls">{"".join(parts)}</div>'
            f'{clear_html}</div>'
        )


@register.tag("filter_bar")
def do_filter_bar(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endfilter_bar",))
    parser.delete_first_token()
    return FilterBarNode(nodelist, kwargs)


@register.tag("filter_select")
def do_filter_select(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return FilterSelectNode(kwargs)


@register.tag("filter_date_range")
def do_filter_date_range(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return FilterDateRangeNode(kwargs)


@register.tag("filter_search")
def do_filter_search(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return FilterSearchNode(kwargs)


# ---------------------------------------------------------------------------
# Avatar Group
# ---------------------------------------------------------------------------

class AvatarGroupNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        users = kw.get("users", [])
        max_display = int(kw.get("max", 5))
        size = kw.get("size", "md")
        custom_class = kw.get("class", "")

        e_size = conditional_escape(str(size))
        e_class = conditional_escape(str(custom_class))

        visible = users[:max_display]
        overflow = len(users) - max_display

        avatars_html = []
        for i, user in enumerate(visible):
            if isinstance(user, dict):
                name = user.get("name", "")
                src = user.get("avatar", "") or user.get("src", "")
            elif hasattr(user, "get_full_name"):
                name = user.get_full_name() or str(user)
                src = getattr(user, "avatar", "")
                if hasattr(src, "url"):
                    src = src.url
            else:
                name = str(user)
                src = ""
            e_name = conditional_escape(str(name))
            e_src = conditional_escape(str(src))
            initials = conditional_escape(
                "".join(w[0].upper() for w in str(name).split()[:2] if w)
            )
            z = len(visible) - i
            if e_src:
                avatars_html.append(
                    f'<span class="dj-avatar-group__item" title="{e_name}" style="z-index:{z}">'
                    f'<img src="{e_src}" alt="{e_name}" class="dj-avatar-group__img">'
                    f'</span>'
                )
            else:
                avatars_html.append(
                    f'<span class="dj-avatar-group__item dj-avatar-group__initials" '
                    f'title="{e_name}" style="z-index:{z}">{initials}</span>'
                )

        overflow_html = ""
        if overflow > 0:
            overflow_html = (
                f'<span class="dj-avatar-group__item dj-avatar-group__overflow">'
                f'+{overflow}</span>'
            )

        cls = f"dj-avatar-group dj-avatar-group--{e_size}"
        if e_class:
            cls += f" {e_class}"
        return mark_safe(
            f'<div class="{cls}">{"".join(avatars_html)}{overflow_html}</div>'
        )


@register.tag("avatar_group")
def do_avatar_group(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return AvatarGroupNode(kwargs)


# ---------------------------------------------------------------------------
# Hover Card
# ---------------------------------------------------------------------------

class HoverCardNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        trigger = kw.get("trigger", "")
        position = kw.get("position", "bottom")
        delay_in = kw.get("delay_in", 200)
        delay_out = kw.get("delay_out", 300)
        custom_class = kw.get("class", "")

        e_trigger = conditional_escape(str(trigger))
        e_position = conditional_escape(str(position))
        e_class = conditional_escape(str(custom_class))

        content = self.nodelist.render(context)

        cls = f"dj-hover-card dj-hover-card--{e_position}"
        if e_class:
            cls += f" {e_class}"
        return mark_safe(
            f'<span class="{cls}" data-delay-in="{int(delay_in)}" '
            f'data-delay-out="{int(delay_out)}">'
            f'<span class="dj-hover-card__trigger">{e_trigger}</span>'
            f'<div class="dj-hover-card__content">{content}</div>'
            f'</span>'
        )


@register.tag("hover_card")
def do_hover_card(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endhover_card",))
    parser.delete_first_token()
    return HoverCardNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Notification Popover
# ---------------------------------------------------------------------------

class NotificationPopoverNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        notifications = kw.get("notifications", [])
        unread_count = int(kw.get("unread_count", 0))
        mark_read_event = kw.get("mark_read_event", "mark_read")
        toggle_event = kw.get("toggle_event", "toggle_notifications")
        is_open = kw.get("open", False)
        custom_class = kw.get("class", "")
        title = kw.get("title", "Notifications")

        e_mark_read = conditional_escape(str(mark_read_event))
        e_toggle = conditional_escape(str(toggle_event))
        e_class = conditional_escape(str(custom_class))
        e_title = conditional_escape(str(title))

        badge_html = ""
        if unread_count > 0:
            display = "99+" if unread_count > 99 else str(unread_count)
            badge_html = f'<span class="dj-notif-popover__badge">{display}</span>'

        open_cls = "dj-notif-popover--open" if is_open else ""
        cls = f"dj-notif-popover {open_cls}"
        if e_class:
            cls += f" {e_class}"

        bell_html = (
            f'<button class="dj-notif-popover__bell" dj-click="{e_toggle}" '
            f'aria-label="Notifications">'
            f'<svg class="dj-notif-popover__icon" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round" width="20" height="20">'
            f'<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>'
            f'<path d="M13.73 21a2 2 0 0 1-3.46 0"/>'
            f'</svg>'
            f'{badge_html}'
            f'</button>'
        )

        items_html = []
        for notif in notifications:
            if isinstance(notif, dict):
                n_id = notif.get("id", "")
                n_title = notif.get("title", "")
                n_body = notif.get("body", notif.get("message", ""))
                n_time = notif.get("time", "")
                n_read = notif.get("read", False)
            else:
                n_id = getattr(notif, "id", "")
                n_title = getattr(notif, "title", "")
                n_body = getattr(notif, "body", getattr(notif, "message", ""))
                n_time = getattr(notif, "time", "")
                n_read = getattr(notif, "read", False)
            e_n_id = conditional_escape(str(n_id))
            e_n_title = conditional_escape(str(n_title))
            e_n_body = conditional_escape(str(n_body))
            e_n_time = conditional_escape(str(n_time))
            read_cls = "dj-notif-popover__item--read" if n_read else ""
            mark_attr = ""
            if not n_read:
                mark_attr = f' dj-click="{e_mark_read}" data-id="{e_n_id}"'
            items_html.append(
                f'<div class="dj-notif-popover__item {read_cls}"{mark_attr}>'
                f'<div class="dj-notif-popover__item-title">{e_n_title}</div>'
                f'<div class="dj-notif-popover__item-body">{e_n_body}</div>'
                f'<div class="dj-notif-popover__item-time">{e_n_time}</div>'
                f'</div>'
            )

        panel_html = ""
        if is_open:
            empty = ""
            if not notifications:
                empty = '<div class="dj-notif-popover__empty">No notifications</div>'
            panel_html = (
                f'<div class="dj-notif-popover__panel">'
                f'<div class="dj-notif-popover__header">{e_title}</div>'
                f'{"".join(items_html)}{empty}'
                f'</div>'
            )

        return mark_safe(f'<div class="{cls}">{bell_html}{panel_html}</div>')


@register.tag("notification_popover")
def do_notification_popover(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return NotificationPopoverNode(kwargs)


# ---------------------------------------------------------------------------
# AI Chat: Conversation Thread
# ---------------------------------------------------------------------------

class ConversationThreadNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        messages = kw.get("messages", [])
        stream_event = kw.get("stream_event", "new_message")
        streaming = kw.get("streaming", False)
        custom_class = kw.get("class", "")

        e_stream = conditional_escape(str(stream_event))
        e_class = conditional_escape(str(custom_class))

        cls = "dj-chat-thread"
        if e_class:
            cls += f" {e_class}"

        msgs_html = []
        prev_sender = None
        for msg in messages:
            if isinstance(msg, dict):
                sender = msg.get("sender", "user")
                name = msg.get("name", "")
                text = msg.get("text", "")
                time = msg.get("time", "")
            else:
                sender = getattr(msg, "sender", "user")
                name = getattr(msg, "name", "")
                text = getattr(msg, "text", "")
                time = getattr(msg, "time", "")

            e_name = conditional_escape(str(name))
            e_text = conditional_escape(str(text))
            e_time = conditional_escape(str(time))

            grouped = "dj-chat-msg--grouped" if sender == prev_sender else ""
            side = "dj-chat-msg--ai" if sender == "ai" else "dj-chat-msg--user"

            initials = str(name)[:1].upper() if name else "?"
            avatar = (
                f'<span class="dj-chat-avatar">{conditional_escape(initials)}</span>'
                if sender != prev_sender
                else '<span class="dj-chat-avatar dj-chat-avatar--hidden"></span>'
            )

            header = ""
            if sender != prev_sender:
                header = (
                    f'<div class="dj-chat-msg__header">'
                    f'<span class="dj-chat-msg__name">{e_name}</span>'
                    f'<span class="dj-chat-msg__time">{e_time}</span>'
                    f'</div>'
                )

            msgs_html.append(
                f'<div class="dj-chat-msg {side} {grouped}">'
                f'{avatar}'
                f'<div class="dj-chat-bubble">'
                f'{header}'
                f'<div class="dj-chat-msg__text">{e_text}</div>'
                f'</div></div>'
            )
            prev_sender = sender

        streaming_html = ""
        if streaming:
            streaming_html = (
                '<div class="dj-chat-msg dj-chat-msg--ai">'
                '<span class="dj-chat-avatar">&#8943;</span>'
                '<div class="dj-chat-bubble">'
                '<div class="dj-chat-typing">'
                '<span class="dj-chat-typing__dot"></span>'
                '<span class="dj-chat-typing__dot"></span>'
                '<span class="dj-chat-typing__dot"></span>'
                '</div></div></div>'
            )

        return mark_safe(
            f'<div class="{cls}" data-stream-event="{e_stream}">'
            f'{"".join(msgs_html)}{streaming_html}'
            f'</div>'
        )


@register.tag("conversation_thread")
def do_conversation_thread(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ConversationThreadNode(kwargs)


# ---------------------------------------------------------------------------
# AI Chat: Thinking Indicator
# ---------------------------------------------------------------------------

class ThinkingIndicatorNode(template.Node):
    VALID_STATUSES = {"thinking", "searching", "generating", "tool_use", "idle"}

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        status = kw.get("status", "thinking")
        label = kw.get("label", "")
        custom_class = kw.get("class", "")

        safe_status = status if status in self.VALID_STATUSES else "thinking"

        if safe_status == "idle":
            return ""

        e_label = conditional_escape(str(label)) if label else ""
        e_class = conditional_escape(str(custom_class))

        cls = f"dj-thinking dj-thinking--{safe_status}"
        if e_class:
            cls += f" {e_class}"

        if safe_status == "thinking":
            anim = (
                '<span class="dj-thinking__dots">'
                '<span class="dj-thinking__dot"></span>'
                '<span class="dj-thinking__dot"></span>'
                '<span class="dj-thinking__dot"></span>'
                '</span>'
            )
        elif safe_status == "searching":
            anim = '<span class="dj-thinking__pulse"></span>'
        elif safe_status == "generating":
            anim = '<span class="dj-thinking__cursor"></span>'
        else:
            anim = '<span class="dj-thinking__spinner"></span>'

        label_html = f'<span class="dj-thinking__label">{e_label}</span>' if e_label else ""

        return mark_safe(
            f'<div class="{cls}" role="status" aria-label="{e_label or safe_status}">'
            f'{anim}{label_html}'
            f'</div>'
        )


@register.tag("thinking_indicator")
def do_thinking_indicator(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ThinkingIndicatorNode(kwargs)


# ---------------------------------------------------------------------------
# AI Chat: Multimodal Input
# ---------------------------------------------------------------------------

class MultimodalInputNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        name = kw.get("name", "message")
        event = kw.get("event", "send")
        placeholder = kw.get("placeholder", "Type a message...")
        accept_files = kw.get("accept_files", False)
        accept_voice = kw.get("accept_voice", False)
        file_accept = kw.get("file_accept", "*/*")
        disabled = kw.get("disabled", False)
        custom_class = kw.get("class", "")

        e_name = conditional_escape(str(name))
        e_event = conditional_escape(str(event))
        e_placeholder = conditional_escape(str(placeholder))
        e_accept = conditional_escape(str(file_accept))
        e_class = conditional_escape(str(custom_class))
        disabled_attr = " disabled" if disabled else ""

        cls = "dj-mminput"
        if disabled:
            cls += " dj-mminput--disabled"
        if e_class:
            cls += f" {e_class}"

        textarea = (
            f'<textarea class="dj-mminput__text" name="{e_name}" '
            f'placeholder="{e_placeholder}" rows="1"{disabled_attr}></textarea>'
        )

        file_btn = ""
        if accept_files:
            file_btn = (
                f'<label class="dj-mminput__btn dj-mminput__file-btn" title="Attach file">'
                f'<input type="file" accept="{e_accept}" hidden{disabled_attr}>'
                f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                f'stroke-width="2" width="18" height="18">'
                f'<path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/>'
                f'</svg></label>'
            )

        voice_btn = ""
        if accept_voice:
            voice_btn = (
                f'<button type="button" class="dj-mminput__btn dj-mminput__voice-btn" '
                f'title="Voice input"{disabled_attr}>'
                f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                f'stroke-width="2" width="18" height="18">'
                f'<path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/>'
                f'<path d="M19 10v2a7 7 0 01-14 0v-2"/>'
                f'<line x1="12" y1="19" x2="12" y2="23"/>'
                f'<line x1="8" y1="23" x2="16" y2="23"/>'
                f'</svg></button>'
            )

        send_btn = (
            f'<button type="button" class="dj-mminput__btn dj-mminput__send-btn" '
            f'dj-click="{e_event}" title="Send"{disabled_attr}>'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" width="18" height="18">'
            f'<line x1="22" y1="2" x2="11" y2="13"/>'
            f'<polygon points="22 2 15 22 11 13 2 9 22 2"/>'
            f'</svg></button>'
        )

        return mark_safe(
            f'<div class="{cls}">'
            f'{file_btn}{voice_btn}'
            f'{textarea}'
            f'{send_btn}'
            f'</div>'
        )


@register.tag("multimodal_input")
def do_multimodal_input(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return MultimodalInputNode(kwargs)


# ---------------------------------------------------------------------------
# AI Chat: Feedback Widget
# ---------------------------------------------------------------------------

class FeedbackWidgetNode(template.Node):
    VALID_MODES = {"thumbs", "stars", "emoji"}

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        event = kw.get("event", "rate_response")
        mode = kw.get("mode", "thumbs")
        value = kw.get("value", None)
        custom_class = kw.get("class", "")

        if mode not in self.VALID_MODES:
            mode = "thumbs"

        e_event = conditional_escape(str(event))
        e_class = conditional_escape(str(custom_class))

        cls = f"dj-feedback dj-feedback--{mode}"
        if e_class:
            cls += f" {e_class}"

        if mode == "thumbs":
            buttons = self._render_thumbs(e_event, value)
        elif mode == "stars":
            buttons = self._render_stars(e_event, value)
        else:
            buttons = self._render_emoji(e_event, value)

        return mark_safe(
            f'<div class="{cls}" role="group" aria-label="Feedback">{buttons}</div>'
        )

    def _render_thumbs(self, e_event, value):
        up_cls = "dj-feedback__btn--active" if value == "up" else ""
        down_cls = "dj-feedback__btn--active" if value == "down" else ""
        return (
            f'<button class="dj-feedback__btn {up_cls}" '
            f'dj-click="{e_event}" data-value="up" aria-label="Thumbs up">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" width="18" height="18">'
            f'<path d="M14 9V5a3 3 0 00-3-3l-4 9v11h11.28a2 2 0 002-1.7l1.38-9a2 2 0 00-2-2.3H14z"/>'
            f'<path d="M7 22H4a2 2 0 01-2-2v-7a2 2 0 012-2h3"/>'
            f'</svg></button>'
            f'<button class="dj-feedback__btn {down_cls}" '
            f'dj-click="{e_event}" data-value="down" aria-label="Thumbs down">'
            f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" width="18" height="18">'
            f'<path d="M10 15v4a3 3 0 003 3l4-9V2H5.72a2 2 0 00-2 1.7l-1.38 9a2 2 0 002 2.3H10z"/>'
            f'<path d="M17 2h2.67A2.31 2.31 0 0122 4v7a2.31 2.31 0 01-2.33 2H17"/>'
            f'</svg></button>'
        )

    def _render_stars(self, e_event, value):
        parts = []
        current = int(value) if value and str(value).isdigit() else 0
        for i in range(1, 6):
            active = "dj-feedback__star--active" if i <= current else ""
            fill = "currentColor" if i <= current else "none"
            parts.append(
                f'<button class="dj-feedback__btn dj-feedback__star {active}" '
                f'dj-click="{e_event}" data-value="{i}" aria-label="{i} star">'
                f'<svg viewBox="0 0 24 24" fill="{fill}" stroke="currentColor" '
                f'stroke-width="2" width="18" height="18">'
                f'<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'
                f'</svg></button>'
            )
        return "".join(parts)

    def _render_emoji(self, e_event, value):
        emojis = [
            ("\U0001f44d", "thumbs_up"),
            ("\u2764\ufe0f", "heart"),
            ("\U0001f60a", "smile"),
            ("\U0001f914", "thinking"),
            ("\U0001f44e", "thumbs_down"),
        ]
        parts = []
        for emoji, val in emojis:
            active = "dj-feedback__btn--active" if value == val else ""
            e_val = conditional_escape(val)
            parts.append(
                f'<button class="dj-feedback__btn {active}" '
                f'dj-click="{e_event}" data-value="{e_val}" aria-label="{e_val}">'
                f'{emoji}</button>'
            )
        return "".join(parts)


@register.tag("feedback")
def do_feedback(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return FeedbackWidgetNode(kwargs)


# ---------------------------------------------------------------------------
# AI Trust: Approval Gate
# ---------------------------------------------------------------------------

class ApprovalGateNode(template.Node):
    VALID_RISKS = {"low", "medium", "high", "critical"}

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        message = kw.get("message", "")
        risk = kw.get("risk", "medium")
        approve_event = kw.get("approve_event", "approve")
        reject_event = kw.get("reject_event", "reject")
        approve_label = kw.get("approve_label", "Approve")
        reject_label = kw.get("reject_label", "Reject")
        custom_class = kw.get("class", "")

        if risk not in self.VALID_RISKS:
            risk = "medium"

        e_msg = conditional_escape(str(message))
        e_approve_evt = conditional_escape(str(approve_event))
        e_reject_evt = conditional_escape(str(reject_event))
        e_approve_lbl = conditional_escape(str(approve_label))
        e_reject_lbl = conditional_escape(str(reject_label))
        e_class = conditional_escape(str(custom_class))

        cls = f"dj-approval dj-approval--{risk}"
        if e_class:
            cls += f" {e_class}"

        risk_label = risk.capitalize()

        if risk in ("high", "critical"):
            icon = (
                '<svg class="dj-approval__icon" viewBox="0 0 24 24" fill="none" '
                'stroke="currentColor" stroke-width="2" width="20" height="20">'
                '<path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>'
                '<path d="M12 9v4M12 17h.01"/></svg>'
            )
        else:
            icon = (
                '<svg class="dj-approval__icon" viewBox="0 0 24 24" fill="none" '
                'stroke="currentColor" stroke-width="2" width="20" height="20">'
                '<circle cx="12" cy="12" r="10"/>'
                '<path d="M12 16v-4M12 8h.01"/></svg>'
            )

        return mark_safe(
            f'<div class="{cls}" role="alert">'
            f'<div class="dj-approval__header">'
            f'{icon}'
            f'<span class="dj-approval__risk">{risk_label} Risk</span>'
            f'</div>'
            f'<div class="dj-approval__message">{e_msg}</div>'
            f'<div class="dj-approval__actions">'
            f'<button class="dj-approval__btn dj-approval__btn--reject" '
            f'dj-click="{e_reject_evt}">{e_reject_lbl}</button>'
            f'<button class="dj-approval__btn dj-approval__btn--approve" '
            f'dj-click="{e_approve_evt}">{e_approve_lbl}</button>'
            f'</div>'
            f'</div>'
        )


@register.tag("approval_gate")
def do_approval_gate(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ApprovalGateNode(kwargs)


# ---------------------------------------------------------------------------
# AI Trust: Source Citation
# ---------------------------------------------------------------------------

class SourceCitationNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        index = kw.get("index", 1)
        title = kw.get("title", "")
        url = kw.get("url", "")
        relevance = kw.get("relevance", None)
        custom_class = kw.get("class", "")

        try:
            idx = int(index)
        except (ValueError, TypeError):
            idx = 1

        e_title = conditional_escape(str(title)) if title else ""
        e_url = conditional_escape(str(url)) if url else ""
        e_class = conditional_escape(str(custom_class))

        cls = "dj-citation"
        if e_class:
            cls += f" {e_class}"

        popover_parts = []
        if e_title:
            popover_parts.append(
                f'<span class="dj-citation__title">{e_title}</span>'
            )
        if e_url:
            popover_parts.append(
                f'<a class="dj-citation__url" href="{e_url}" '
                f'target="_blank" rel="noopener noreferrer">{e_url}</a>'
            )
        if relevance is not None:
            try:
                pct = min(100, max(0, float(relevance) * 100))
                popover_parts.append(
                    f'<span class="dj-citation__relevance">'
                    f'Relevance: {pct:.0f}%</span>'
                )
            except (ValueError, TypeError):
                pass

        popover_html = "".join(popover_parts)

        return mark_safe(
            f'<span class="{cls}">'
            f'<sup class="dj-citation__marker">[{idx}]</sup>'
            f'<span class="dj-citation__popover">{popover_html}</span>'
            f'</span>'
        )


@register.tag("source_citation")
def do_source_citation(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return SourceCitationNode(kwargs)


# ---------------------------------------------------------------------------
# AI Trust: Model Selector
# ---------------------------------------------------------------------------

class ModelSelectorNode(template.Node):
    TIER_LABELS = {
        "free": "Free",
        "standard": "Standard",
        "premium": "Premium",
        "enterprise": "Enterprise",
    }

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        name = kw.get("name", "model")
        options = kw.get("options", [])
        value = str(kw.get("value", "")) if kw.get("value") else ""
        event = kw.get("event", "select_model")
        placeholder = kw.get("placeholder", "Select a model...")
        disabled = kw.get("disabled", False)
        label = kw.get("label", "")
        custom_class = kw.get("class", "")

        e_name = conditional_escape(str(name))
        e_event = conditional_escape(str(event or name))
        e_placeholder = conditional_escape(str(placeholder))
        e_class = conditional_escape(str(custom_class))
        disabled_attr = " disabled" if disabled else ""
        disabled_cls = " dj-model-sel--disabled" if disabled else ""

        cls = f"dj-model-sel{disabled_cls}"
        if e_class:
            cls += f" {e_class}"

        if not isinstance(options, list):
            options = []

        selected_opt = None
        for opt in options:
            if isinstance(opt, dict) and str(opt.get("value", "")) == value:
                selected_opt = opt
                break

        if selected_opt:
            selected_html = self._option_inner(selected_opt)
        else:
            selected_html = (
                f'<span class="dj-model-sel__placeholder">{e_placeholder}</span>'
            )

        opt_parts = []
        for opt in options:
            if not isinstance(opt, dict):
                continue
            ov = str(opt.get("value", ""))
            active_cls = " dj-model-sel__opt--active" if ov == value else ""
            inner = self._option_inner(opt)
            opt_parts.append(
                f'<div class="dj-model-sel__opt{active_cls}" '
                f'data-value="{conditional_escape(ov)}" '
                f'dj-click="{e_event}" '
                f'role="option" aria-selected="{"true" if ov == value else "false"}">'
                f'{inner}</div>'
            )

        label_html = ""
        if label:
            label_html = (
                f'<label class="dj-model-sel__label">'
                f'{conditional_escape(str(label))}</label>'
            )

        return mark_safe(
            f'<div class="{cls}">'
            f'{label_html}'
            f'<input type="hidden" name="{e_name}" value="{conditional_escape(value)}">'
            f'<div class="dj-model-sel__trigger" tabindex="0" role="combobox" '
            f'aria-expanded="false" aria-haspopup="listbox"{disabled_attr}>'
            f'{selected_html}'
            f'<span class="dj-model-sel__chevron">&#9662;</span>'
            f'</div>'
            f'<div class="dj-model-sel__dropdown" role="listbox">'
            f'{"".join(opt_parts)}'
            f'</div></div>'
        )

    def _option_inner(self, opt):
        label = conditional_escape(str(opt.get("label", "")))
        desc = conditional_escape(str(opt.get("description", ""))) if opt.get("description") else ""
        ctx_win = conditional_escape(str(opt.get("context_window", ""))) if opt.get("context_window") else ""
        tier = str(opt.get("tier", "")).lower()
        tier_label = conditional_escape(
            self.TIER_LABELS.get(tier, tier.capitalize())
        ) if tier else ""

        parts = [f'<span class="dj-model-sel__name">{label}</span>']
        if desc:
            parts.append(f'<span class="dj-model-sel__desc">{desc}</span>')

        meta = []
        if ctx_win:
            meta.append(f'<span class="dj-model-sel__ctx">{ctx_win}</span>')
        if tier_label:
            safe_tier = conditional_escape(tier)
            meta.append(
                f'<span class="dj-model-sel__tier dj-model-sel__tier--{safe_tier}">'
                f'{tier_label}</span>'
            )
        if meta:
            parts.append(f'<span class="dj-model-sel__meta">{"".join(meta)}</span>')

        return f'<span class="dj-model-sel__info">{"".join(parts)}</span>'


@register.tag("model_selector")
def do_model_selector(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ModelSelectorNode(kwargs)


# ---------------------------------------------------------------------------
# AI Trust: Token Counter
# ---------------------------------------------------------------------------

class TokenCounterNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        try:
            current = int(kw.get("current", 0))
        except (ValueError, TypeError):
            current = 0
        try:
            max_tokens = int(kw.get("max", 4096))
        except (ValueError, TypeError):
            max_tokens = 4096

        label = kw.get("label", None)
        show_label = kw.get("show_label", True)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))

        if max_tokens <= 0:
            pct = 0.0
        else:
            pct = min(100.0, max(0.0, (current / max_tokens) * 100))

        if pct >= 85:
            threshold = "dj-token--danger"
        elif pct >= 60:
            threshold = "dj-token--warn"
        else:
            threshold = "dj-token--ok"

        cls = f"dj-token {threshold}"
        if e_class:
            cls += f" {e_class}"

        label_html = ""
        if show_label:
            if label:
                display_label = conditional_escape(str(label))
            else:
                display_label = f"{current:,} / {max_tokens:,}"
            label_html = f'<span class="dj-token__label">{display_label}</span>'

        return mark_safe(
            f'<div class="{cls}" role="meter" '
            f'aria-valuenow="{current}" aria-valuemin="0" aria-valuemax="{max_tokens}" '
            f'aria-label="Token usage">'
            f'{label_html}'
            f'<div class="dj-token__track">'
            f'<div class="dj-token__bar" style="width:{pct:.1f}%"></div>'
            f'</div>'
            f'</div>'
        )


@register.tag("token_counter")
def do_token_counter(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return TokenCounterNode(kwargs)


# ---------------------------------------------------------------------------
# Collaboration: Chat Bubble
# ---------------------------------------------------------------------------

class ChatBubbleNode(template.Node):
    VALID_STATUSES = {"sending", "sent", "delivered", "read", "error"}

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        message = kw.get("message", {})
        custom_class = kw.get("class", "")

        if not isinstance(message, dict):
            message = {}

        sender = message.get("sender", "user")
        name = message.get("name", "")
        text = message.get("text", "")
        time_str = message.get("time", "")
        avatar_src = message.get("avatar", "")
        status = message.get("status", "")

        e_name = conditional_escape(str(name))
        e_text = conditional_escape(str(text))
        e_time = conditional_escape(str(time_str))
        e_avatar = conditional_escape(str(avatar_src))
        e_class = conditional_escape(str(custom_class))

        side = "dj-bubble--user" if sender == "user" else "dj-bubble--other"
        cls = f"dj-bubble {side}"
        if e_class:
            cls += f" {e_class}"

        # Avatar
        initials = conditional_escape(
            "".join(w[0].upper() for w in str(name).split()[:2] if w) or "?"
        )
        if e_avatar:
            avatar_html = (
                f'<span class="dj-bubble__avatar">'
                f'<img src="{e_avatar}" alt="{e_name}" class="dj-bubble__avatar-img">'
                f'</span>'
            )
        else:
            avatar_html = (
                f'<span class="dj-bubble__avatar dj-bubble__avatar--initials">'
                f'{initials}</span>'
            )

        # Status
        status_html = ""
        if status and status in self.VALID_STATUSES:
            e_status = conditional_escape(str(status))
            status_icons = {
                "sending": "&#8987;",
                "sent": "&#10003;",
                "delivered": "&#10003;&#10003;",
                "read": "&#10003;&#10003;",
                "error": "&#9888;",
            }
            icon = status_icons.get(status, "")
            status_html = (
                f'<span class="dj-bubble__status dj-bubble__status--{e_status}" '
                f'aria-label="{e_status}">{icon}</span>'
            )

        # Header
        header_html = ""
        if e_name or e_time:
            name_part = f'<span class="dj-bubble__name">{e_name}</span>' if e_name else ""
            time_part = f'<span class="dj-bubble__time">{e_time}</span>' if e_time else ""
            header_html = f'<div class="dj-bubble__header">{name_part}{time_part}</div>'

        # Footer
        footer_html = ""
        if status_html:
            footer_html = f'<div class="dj-bubble__footer">{status_html}</div>'

        return mark_safe(
            f'<div class="{cls}">'
            f'{avatar_html}'
            f'<div class="dj-bubble__content">'
            f'{header_html}'
            f'<div class="dj-bubble__text">{e_text}</div>'
            f'{footer_html}'
            f'</div>'
            f'</div>'
        )


@register.tag("chat_bubble")
def do_chat_bubble(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ChatBubbleNode(kwargs)


# ---------------------------------------------------------------------------
# Collaboration: Presence Avatars
# ---------------------------------------------------------------------------

class PresenceAvatarsNode(template.Node):
    VALID_STATUSES = {"online", "away", "busy", "offline"}

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        users = kw.get("users", [])
        max_display = int(kw.get("max", 5))
        custom_class = kw.get("class", "")

        if not isinstance(users, list):
            users = []

        e_class = conditional_escape(str(custom_class))

        visible = users[:max_display]
        overflow = len(users) - max_display

        parts = []
        for i, user in enumerate(visible):
            if isinstance(user, dict):
                name = user.get("name", "")
                src = user.get("avatar", "") or user.get("src", "")
                status = user.get("status", "online")
            else:
                name = str(user)
                src = ""
                status = "online"

            e_name = conditional_escape(str(name))
            e_src = conditional_escape(str(src))
            safe_status = status if status in self.VALID_STATUSES else "online"
            initials = conditional_escape(
                "".join(w[0].upper() for w in str(name).split()[:2] if w) or "?"
            )
            z = len(visible) - i

            if e_src:
                avatar_inner = (
                    f'<img src="{e_src}" alt="{e_name}" '
                    f'class="dj-presence__img">'
                )
            else:
                avatar_inner = (
                    f'<span class="dj-presence__initials">{initials}</span>'
                )

            dot = (
                f'<span class="dj-presence__dot '
                f'dj-presence__dot--{safe_status}"></span>'
            )

            parts.append(
                f'<span class="dj-presence__item" title="{e_name}" '
                f'style="z-index:{z}">'
                f'{avatar_inner}{dot}'
                f'</span>'
            )

        if overflow > 0:
            parts.append(
                f'<span class="dj-presence__item dj-presence__overflow">'
                f'+{overflow}</span>'
            )

        cls = "dj-presence"
        if e_class:
            cls += f" {e_class}"

        total = len(users)
        label = f'{total} user{"s" if total != 1 else ""} present'

        return mark_safe(
            f'<div class="{cls}" role="group" aria-label="{label}">'
            f'{"".join(parts)}'
            f'</div>'
        )


@register.tag("presence_avatars")
def do_presence_avatars(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return PresenceAvatarsNode(kwargs)


# ---------------------------------------------------------------------------
# Collaboration: Mentions Input
# ---------------------------------------------------------------------------

class MentionsInputNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        import json as _json

        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        name = kw.get("name", "message")
        users = kw.get("users", [])
        event = kw.get("event", "send")
        placeholder = kw.get("placeholder", "Type @ to mention...")
        disabled = kw.get("disabled", False)
        custom_class = kw.get("class", "")

        if not isinstance(users, list):
            users = []

        e_name = conditional_escape(str(name))
        e_event = conditional_escape(str(event))
        e_placeholder = conditional_escape(str(placeholder))
        e_class = conditional_escape(str(custom_class))
        disabled_attr = " disabled" if disabled else ""

        cls = "dj-mentions"
        if disabled:
            cls += " dj-mentions--disabled"
        if e_class:
            cls += f" {e_class}"

        # Render suggestion items
        items_html = []
        for user in users:
            if not isinstance(user, dict):
                continue
            uid = conditional_escape(str(user.get("id", "")))
            uname = conditional_escape(str(user.get("name", "")))
            avatar_src = conditional_escape(str(user.get("avatar", "")))

            initials = conditional_escape(
                "".join(w[0].upper() for w in str(user.get("name", "")).split()[:2] if w)
            ) or "?"

            if avatar_src:
                avatar_html = (
                    f'<img src="{avatar_src}" alt="{uname}" '
                    f'class="dj-mentions__avatar-img">'
                )
            else:
                avatar_html = (
                    f'<span class="dj-mentions__avatar-initials">{initials}</span>'
                )

            items_html.append(
                f'<li class="dj-mentions__item" data-user-id="{uid}" '
                f'data-user-name="{uname}" role="option">'
                f'<span class="dj-mentions__avatar">{avatar_html}</span>'
                f'<span class="dj-mentions__name">{uname}</span>'
                f'</li>'
            )

        users_json = conditional_escape(_json.dumps(users, default=str))

        return mark_safe(
            f'<div class="{cls}" dj-hook="MentionsInput" '
            f'data-users="{users_json}">'
            f'<input type="text" class="dj-mentions__input" name="{e_name}" '
            f'placeholder="{e_placeholder}" autocomplete="off"{disabled_attr} '
            f'dj-keydown.enter="{e_event}">'
            f'<ul class="dj-mentions__dropdown" role="listbox">'
            f'{"".join(items_html)}'
            f'</ul>'
            f'</div>'
        )


@register.tag("mentions_input")
def do_mentions_input(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return MentionsInputNode(kwargs)


# ---------------------------------------------------------------------------
# Expandable Text (#118)
# ---------------------------------------------------------------------------

class ExpandableTextNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        max_lines = int(kw.get("max_lines", 3))
        expanded = kw.get("expanded", False)
        toggle_event = kw.get("toggle_event", "toggle_expand")
        more_label = kw.get("more_label", "Read more")
        less_label = kw.get("less_label", "Show less")
        custom_class = kw.get("class", "")

        content = self.nodelist.render(context)
        e_event = conditional_escape(str(toggle_event))
        e_more = conditional_escape(str(more_label))
        e_less = conditional_escape(str(less_label))
        e_class = conditional_escape(str(custom_class))

        cls = "dj-expandable-text"
        if expanded:
            cls += " dj-expandable-text--expanded"
        if e_class:
            cls += f" {e_class}"

        if expanded:
            style = ""
            label = e_less
        else:
            style = (
                f' style="-webkit-line-clamp:{max_lines};'
                f'display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden"'
            )
            label = e_more

        return mark_safe(
            f'<div class="{cls}">'
            f'<div class="dj-expandable-text__content"{style}>{content}</div>'
            f'<button class="dj-expandable-text__toggle" dj-click="{e_event}">'
            f'{label}</button>'
            f'</div>'
        )


@register.tag("expandable_text")
def do_expandable_text(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endexpandable_text",))
    parser.delete_first_token()
    return ExpandableTextNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Truncated List (#150)
# ---------------------------------------------------------------------------

class TruncatedListNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        items = kw.get("items", [])
        max_count = int(kw.get("max", 3))
        expanded = kw.get("expanded", False)
        toggle_event = kw.get("toggle_event", "toggle_list")
        overflow_label = kw.get("overflow_label", "+{count} more")
        custom_class = kw.get("class", "")

        if not isinstance(items, (list, tuple)):
            items = []

        e_class = conditional_escape(str(custom_class))
        cls = "dj-truncated-list"
        if expanded:
            cls += " dj-truncated-list--expanded"
        if e_class:
            cls += f" {e_class}"

        total = len(items)
        visible = items if expanded else items[:max_count]
        hidden_count = max(0, total - max_count)

        items_html = []
        for item in visible:
            if isinstance(item, dict):
                label = conditional_escape(str(item.get("label", item.get("name", ""))))
            else:
                label = conditional_escape(str(item))
            items_html.append(f'<span class="dj-truncated-list__item">{label}</span>')

        overflow_html = ""
        if hidden_count > 0:
            e_event = conditional_escape(str(toggle_event))
            if expanded:
                overflow_text = conditional_escape("Show less")
            else:
                overflow_text = conditional_escape(
                    str(overflow_label).replace("{count}", str(hidden_count))
                )
            overflow_html = (
                f'<button class="dj-truncated-list__overflow" dj-click="{e_event}">'
                f'{overflow_text}</button>'
            )

        return mark_safe(
            f'<div class="{cls}" role="list">'
            f'{"".join(items_html)}{overflow_html}'
            f'</div>'
        )


@register.tag("truncated_list")
def do_truncated_list(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return TruncatedListNode(kwargs)


# ---------------------------------------------------------------------------
# Inline Markdown Preview (#169)
# ---------------------------------------------------------------------------

class MarkdownTextareaNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        name = kw.get("name", "content")
        value = kw.get("value", "")
        preview = kw.get("preview", False)
        toggle_event = kw.get("toggle_event", "toggle_preview")
        placeholder = kw.get("placeholder", "Write markdown here...")
        rows = int(kw.get("rows", 6))
        disabled = kw.get("disabled", False)
        custom_class = kw.get("class", "")

        e_name = conditional_escape(str(name))
        e_value = conditional_escape(str(value))
        e_event = conditional_escape(str(toggle_event))
        e_placeholder = conditional_escape(str(placeholder))
        e_class = conditional_escape(str(custom_class))
        disabled_attr = " disabled" if disabled else ""

        cls = "dj-md-textarea"
        if preview:
            cls += " dj-md-textarea--preview"
        if e_class:
            cls += f" {e_class}"

        write_active = "" if preview else " dj-md-textarea__tab--active"
        preview_active = " dj-md-textarea__tab--active" if preview else ""

        toolbar = (
            f'<div class="dj-md-textarea__toolbar">'
            f'<button type="button" class="dj-md-textarea__tab{write_active}" '
            f'dj-click="{e_event}" data-mode="write">Write</button>'
            f'<button type="button" class="dj-md-textarea__tab{preview_active}" '
            f'dj-click="{e_event}" data-mode="preview">Preview</button>'
            f'</div>'
        )

        if preview:
            body = (
                f'<div class="dj-md-textarea__preview" data-raw="{e_value}">'
                f'{e_value}</div>'
                f'<input type="hidden" name="{e_name}" value="{e_value}">'
            )
        else:
            body = (
                f'<textarea class="dj-md-textarea__input" name="{e_name}" '
                f'rows="{rows}" placeholder="{e_placeholder}"{disabled_attr}>'
                f'{e_value}</textarea>'
            )

        return mark_safe(
            f'<div class="{cls}" dj-hook="MarkdownTextarea">'
            f'{toolbar}{body}'
            f'</div>'
        )


@register.tag("markdown_textarea")
def do_markdown_textarea(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return MarkdownTextareaNode(kwargs)


# ---------------------------------------------------------------------------
# Skeleton Factory (#144)
# ---------------------------------------------------------------------------

class SkeletonForNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        component = kw.get("component", "text")
        columns = int(kw.get("columns", 4))
        rows = int(kw.get("rows", 5))
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))
        cls = "dj-skeleton"
        if e_class:
            cls += f" {e_class}"

        supported = {"data_table", "card", "list", "text"}
        if component not in supported:
            component = "text"

        if component == "data_table":
            return mark_safe(self._render_table(cls, columns, rows))
        elif component == "card":
            return mark_safe(self._render_card(cls))
        elif component == "list":
            return mark_safe(self._render_list(cls, rows))
        else:
            return mark_safe(self._render_text(cls, rows))

    def _render_table(self, cls, cols, rows):
        header_cells = "".join(
            '<th><span class="dj-skeleton__line dj-skeleton__pulse" '
            'style="width:70%">&nbsp;</span></th>'
            for _ in range(cols)
        )
        header = f'<thead><tr>{header_cells}</tr></thead>'
        body_rows = []
        for _ in range(rows):
            cells = "".join(
                '<td><span class="dj-skeleton__line dj-skeleton__pulse">'
                '&nbsp;</span></td>'
                for _ in range(cols)
            )
            body_rows.append(f'<tr>{cells}</tr>')
        body = f'<tbody>{"".join(body_rows)}</tbody>'
        return (
            f'<div class="{cls} dj-skeleton--data-table" '
            f'role="status" aria-label="Loading">'
            f'<table class="dj-skeleton__table">{header}{body}</table>'
            f'</div>'
        )

    def _render_card(self, cls):
        return (
            f'<div class="{cls} dj-skeleton--card" '
            f'role="status" aria-label="Loading">'
            f'<div class="dj-skeleton__card-image dj-skeleton__pulse">&nbsp;</div>'
            f'<div class="dj-skeleton__card-body">'
            f'<span class="dj-skeleton__line dj-skeleton__pulse" '
            f'style="width:60%">&nbsp;</span>'
            f'<span class="dj-skeleton__line dj-skeleton__pulse" '
            f'style="width:90%">&nbsp;</span>'
            f'<span class="dj-skeleton__line dj-skeleton__pulse" '
            f'style="width:40%">&nbsp;</span>'
            f'</div></div>'
        )

    def _render_list(self, cls, rows):
        items = []
        for _ in range(rows):
            items.append(
                '<div class="dj-skeleton__list-item">'
                '<span class="dj-skeleton__circle dj-skeleton__pulse">&nbsp;</span>'
                '<span class="dj-skeleton__line dj-skeleton__pulse" '
                'style="width:80%">&nbsp;</span>'
                '</div>'
            )
        return (
            f'<div class="{cls} dj-skeleton--list" '
            f'role="status" aria-label="Loading">'
            f'{"".join(items)}</div>'
        )

    def _render_text(self, cls, rows):
        widths = [95, 85, 90, 70, 80, 60, 75, 88, 65, 92]
        lines = []
        for i in range(rows):
            w = widths[i % len(widths)]
            lines.append(
                f'<span class="dj-skeleton__line dj-skeleton__pulse" '
                f'style="width:{w}%">&nbsp;</span>'
            )
        return (
            f'<div class="{cls} dj-skeleton--text" '
            f'role="status" aria-label="Loading">'
            f'{"".join(lines)}</div>'
        )


@register.tag("skeleton_for")
def do_skeleton_for(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return SkeletonForNode(kwargs)


# ---------------------------------------------------------------------------
# Content Loader / Suspense (#152)
# ---------------------------------------------------------------------------

class AwaitNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        loading_event = kw.get("loading_event", "data_loaded")
        loaded = kw.get("loaded", False)
        error = kw.get("error", "")
        error_event = kw.get("error_event", "")
        custom_class = kw.get("class", "")

        e_event = conditional_escape(str(loading_event))
        e_class = conditional_escape(str(custom_class))

        cls = "dj-content-loader"
        if loaded:
            cls += " dj-content-loader--loaded"
        if error:
            cls += " dj-content-loader--error"
        if e_class:
            cls += f" {e_class}"

        if error:
            e_error = conditional_escape(str(error))
            retry_html = ""
            if error_event:
                e_retry = conditional_escape(str(error_event))
                retry_html = (
                    f'<button class="dj-content-loader__retry" '
                    f'dj-click="{e_retry}">Retry</button>'
                )
            return mark_safe(
                f'<div class="{cls}" data-loading-event="{e_event}">'
                f'<div class="dj-content-loader__error" role="alert">'
                f'<span class="dj-content-loader__error-msg">{e_error}</span>'
                f'{retry_html}</div></div>'
            )

        # Render child nodes — for loaded state these are the actual content,
        # for loading state they are the placeholder (e.g. skeleton_for)
        inner = self.nodelist.render(context)

        if loaded:
            return mark_safe(
                f'<div class="{cls}" data-loading-event="{e_event}">'
                f'<div class="dj-content-loader__content">{inner}</div>'
                f'</div>'
            )

        return mark_safe(
            f'<div class="{cls}" data-loading-event="{e_event}" '
            f'role="status" aria-label="Loading">'
            f'<div class="dj-content-loader__placeholder">{inner}</div>'
            f'</div>'
        )


@register.tag("await")
def do_await(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endawait",))
    parser.delete_first_token()
    return AwaitNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Time Picker
# ---------------------------------------------------------------------------

class TimePickerNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        name = kw.get("name", "time")
        value = kw.get("value", "")
        event = kw.get("event", "")
        format_24h = kw.get("format_24h", False)
        step = kw.get("step", 1)
        disabled = kw.get("disabled", False)
        label = kw.get("label", "")
        custom_class = kw.get("class", "")

        e_name = conditional_escape(str(name))
        e_value = conditional_escape(str(value))
        e_event = conditional_escape(str(event)) if event else ""
        e_label = conditional_escape(str(label)) if label else ""
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-time-picker"]
        if disabled:
            classes.append("dj-time-picker--disabled")
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        # Parse time
        hour, minute = 0, 0
        if value:
            parts = str(value).split(":")
            try:
                hour = int(parts[0])
                minute = int(parts[1]) if len(parts) > 1 else 0
            except (ValueError, IndexError):
                pass

        parts_html = []
        if e_label:
            parts_html.append(
                f'<label class="dj-time-picker__label" for="{e_name}">{e_label}</label>'
            )

        event_attr = f' dj-change="{e_event}"' if e_event else ""
        disabled_attr = " disabled" if disabled else ""

        parts_html.append(
            f'<input type="hidden" name="{e_name}" value="{e_value}"{event_attr}>'
        )
        parts_html.append('<div class="dj-time-picker__controls">')

        # Hour select
        hour_options = []
        if format_24h:
            for h in range(24):
                sel = " selected" if h == hour else ""
                hour_options.append(f'<option value="{h}"{sel}>{h:02d}</option>')
        else:
            display_hour = hour % 12 or 12
            for h in range(1, 13):
                sel = " selected" if h == display_hour else ""
                hour_options.append(f'<option value="{h}"{sel}>{h}</option>')

        parts_html.append(
            f'<select class="dj-time-picker__hour" aria-label="Hour"{disabled_attr}>'
            f'{"".join(hour_options)}</select>'
        )
        parts_html.append('<span class="dj-time-picker__separator">:</span>')

        # Minute select
        try:
            step_val = max(1, int(step))
        except (ValueError, TypeError):
            step_val = 1
        minute_options = []
        for m in range(0, 60, step_val):
            sel = " selected" if m == minute else ""
            minute_options.append(f'<option value="{m}"{sel}>{m:02d}</option>')

        parts_html.append(
            f'<select class="dj-time-picker__minute" aria-label="Minute"{disabled_attr}>'
            f'{"".join(minute_options)}</select>'
        )

        # AM/PM toggle
        if not format_24h:
            is_pm = hour >= 12
            parts_html.append(
                f'<select class="dj-time-picker__period" aria-label="AM/PM"{disabled_attr}>'
                f'<option value="AM"{"" if is_pm else " selected"}>AM</option>'
                f'<option value="PM"{" selected" if is_pm else ""}>PM</option>'
                f'</select>'
            )

        parts_html.append('</div>')

        return mark_safe(f'<div class="{class_str}">{"".join(parts_html)}</div>')


@register.tag("time_picker")
def do_time_picker(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return TimePickerNode(kwargs)


# ---------------------------------------------------------------------------
# Wizard / Multi-step Form
# ---------------------------------------------------------------------------

class WizardNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        steps = kw.get("steps", [])
        active = kw.get("active", "")
        event = kw.get("event", "set_step")
        show_numbers = kw.get("show_numbers", True)
        custom_class = kw.get("class", "")

        e_event = conditional_escape(str(event))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-wizard"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(steps, list):
            steps = []

        # Find active index
        active_idx = 0
        for i, step in enumerate(steps):
            if isinstance(step, dict) and step.get("id") == active:
                active_idx = i
                break

        # Step indicators
        indicators = []
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            step_id = conditional_escape(str(step.get("id", "")))
            step_label = conditional_escape(str(step.get("label", "")))
            step_cls = "dj-wizard__step"
            if i < active_idx:
                step_cls += " dj-wizard__step--completed"
            elif i == active_idx:
                step_cls += " dj-wizard__step--active"

            number_html = ""
            if show_numbers:
                number_html = f'<span class="dj-wizard__number">{i + 1}</span>'

            indicators.append(
                f'<button class="{step_cls}" '
                f'dj-click="{e_event}" data-value="{step_id}">'
                f'{number_html}'
                f'<span class="dj-wizard__label">{step_label}</span></button>'
            )

        nav_items = []
        for i, ind in enumerate(indicators):
            nav_items.append(ind)
            if i < len(indicators) - 1:
                conn_cls = "dj-wizard__connector"
                if i < active_idx:
                    conn_cls += " dj-wizard__connector--completed"
                nav_items.append(f'<div class="{conn_cls}"></div>')

        nav = f'<nav class="dj-wizard__nav" role="tablist">{"".join(nav_items)}</nav>'

        content = self.nodelist.render(context)

        return mark_safe(
            f'<div class="{class_str}">{nav}'
            f'<div class="dj-wizard__body">{content}</div></div>'
        )


@register.tag("wizard")
def do_wizard(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endwizard",))
    parser.delete_first_token()
    return WizardNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Bottom Sheet
# ---------------------------------------------------------------------------

class BottomSheetNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        title = kw.get("title", "")
        is_open = kw.get("open", False)
        close_event = kw.get("close_event", "close_sheet")
        custom_class = kw.get("class", "")

        if not is_open:
            return ""

        e_title = conditional_escape(str(title))
        e_close = conditional_escape(str(close_event))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-bottom-sheet"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        content = self.nodelist.render(context)

        title_html = ""
        if title:
            title_html = f'<h3 class="dj-bottom-sheet__title">{e_title}</h3>'

        return mark_safe(
            f'<div class="dj-bottom-sheet__backdrop" dj-click="{e_close}">'
            f'<div class="{class_str}" onclick="event.stopPropagation()">'
            f'<div class="dj-bottom-sheet__handle"><div class="dj-bottom-sheet__handle-bar"></div></div>'
            f'<div class="dj-bottom-sheet__header">'
            f'{title_html}'
            f'<button class="dj-bottom-sheet__close" dj-click="{e_close}">&times;</button>'
            f'</div>'
            f'<div class="dj-bottom-sheet__body">{content}</div>'
            f'</div></div>'
        )


@register.tag("bottom_sheet")
def do_bottom_sheet(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endbottom_sheet",))
    parser.delete_first_token()
    return BottomSheetNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Infinite Scroll
# ---------------------------------------------------------------------------

class InfiniteScrollNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        load_event = kw.get("load_event", "load_more")
        threshold = kw.get("threshold", "200px")
        loading = kw.get("loading", False)
        finished = kw.get("finished", False)
        custom_class = kw.get("class", "")

        e_event = conditional_escape(str(load_event))
        e_threshold = conditional_escape(str(threshold))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-infinite-scroll"]
        if loading:
            classes.append("dj-infinite-scroll--loading")
        if finished:
            classes.append("dj-infinite-scroll--finished")
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        content = self.nodelist.render(context)

        sentinel = ""
        if loading:
            sentinel = '<div class="dj-infinite-scroll__spinner" role="status" aria-label="Loading"></div>'
        elif finished:
            sentinel = '<div class="dj-infinite-scroll__done">No more items</div>'

        return mark_safe(
            f'<div class="{class_str}" dj-hook="InfiniteScroll" '
            f'data-event="{e_event}" data-threshold="{e_threshold}">'
            f'<div class="dj-infinite-scroll__content">{content}</div>'
            f'{sentinel}</div>'
        )


@register.tag("infinite_scroll")
def do_infinite_scroll(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endinfinite_scroll",))
    parser.delete_first_token()
    return InfiniteScrollNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Countdown / Timer
# ---------------------------------------------------------------------------

class CountdownNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        target = kw.get("target", "")
        event = kw.get("event", "")
        show_days = kw.get("show_days", True)
        show_seconds = kw.get("show_seconds", True)
        labels = kw.get("labels", {})
        custom_class = kw.get("class", "")

        e_target = conditional_escape(str(target))
        e_event = conditional_escape(str(event)) if event else ""
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-countdown"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        event_attr = f' data-event="{e_event}"' if e_event else ""

        default_labels = {"days": "Days", "hours": "Hours", "minutes": "Minutes", "seconds": "Seconds"}
        if isinstance(labels, dict):
            merged = {**default_labels, **labels}
        else:
            merged = default_labels

        segments = []
        if show_days:
            segments.append(
                f'<div class="dj-countdown__segment">'
                f'<span class="dj-countdown__value" data-unit="days">00</span>'
                f'<span class="dj-countdown__label">{conditional_escape(merged["days"])}</span></div>'
            )
        segments.append(
            f'<div class="dj-countdown__segment">'
            f'<span class="dj-countdown__value" data-unit="hours">00</span>'
            f'<span class="dj-countdown__label">{conditional_escape(merged["hours"])}</span></div>'
        )
        segments.append(
            f'<div class="dj-countdown__segment">'
            f'<span class="dj-countdown__value" data-unit="minutes">00</span>'
            f'<span class="dj-countdown__label">{conditional_escape(merged["minutes"])}</span></div>'
        )
        if show_seconds:
            segments.append(
                f'<div class="dj-countdown__segment">'
                f'<span class="dj-countdown__value" data-unit="seconds">00</span>'
                f'<span class="dj-countdown__label">{conditional_escape(merged["seconds"])}</span></div>'
            )

        separators = []
        for i, seg in enumerate(segments):
            separators.append(seg)
            if i < len(segments) - 1:
                separators.append('<span class="dj-countdown__separator">:</span>')

        return mark_safe(
            f'<div class="{class_str}" dj-hook="Countdown" '
            f'data-target="{e_target}"{event_attr} '
            f'role="timer">{"".join(separators)}</div>'
        )


@register.tag("countdown")
def do_countdown(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return CountdownNode(kwargs)


# ---------------------------------------------------------------------------
# Cookie Consent Banner
# ---------------------------------------------------------------------------

class CookieConsentNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        message = kw.get("message", "We use cookies to improve your experience.")
        accept_event = kw.get("accept_event", "accept_cookies")
        reject_event = kw.get("reject_event", "")
        accept_label = kw.get("accept_label", "Accept")
        reject_label = kw.get("reject_label", "Decline")
        privacy_url = kw.get("privacy_url", "")
        show_reject = kw.get("show_reject", True)
        position = kw.get("position", "bottom")
        custom_class = kw.get("class", "")

        e_msg = conditional_escape(str(message))
        e_accept = conditional_escape(str(accept_event))
        e_accept_label = conditional_escape(str(accept_label))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-cookie-consent", f"dj-cookie-consent--{conditional_escape(str(position))}"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        content = self.nodelist.render(context) if self.nodelist else ""

        msg_text = content.strip() if content.strip() else e_msg

        privacy_html = ""
        if privacy_url:
            e_url = conditional_escape(str(privacy_url))
            privacy_html = f' <a href="{e_url}" class="dj-cookie-consent__link">Privacy Policy</a>'

        buttons = [
            f'<button class="dj-cookie-consent__accept" '
            f'dj-click="{e_accept}">{e_accept_label}</button>'
        ]

        if show_reject and reject_event:
            e_reject = conditional_escape(str(reject_event))
            e_reject_label = conditional_escape(str(reject_label))
            buttons.append(
                f'<button class="dj-cookie-consent__reject" '
                f'dj-click="{e_reject}">{e_reject_label}</button>'
            )

        return mark_safe(
            f'<div class="{class_str}" role="banner" aria-label="Cookie consent">'
            f'<p class="dj-cookie-consent__message">{msg_text}{privacy_html}</p>'
            f'<div class="dj-cookie-consent__actions">{"".join(buttons)}</div>'
            f'</div>'
        )


@register.tag("cookie_consent")
def do_cookie_consent(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endcookie_consent",))
    parser.delete_first_token()
    return CookieConsentNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Form Array
# ---------------------------------------------------------------------------

class FormArrayNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        name = kw.get("name", "items")
        rows = kw.get("rows", [{"value": ""}])
        min_rows = kw.get("min", 1)
        max_rows = kw.get("max", 10)
        add_event = kw.get("add_event", "add_row")
        remove_event = kw.get("remove_event", "remove_row")
        add_label = kw.get("add_label", "Add row")
        custom_class = kw.get("class", "")

        e_name = conditional_escape(str(name))
        e_add_event = conditional_escape(str(add_event))
        e_remove_event = conditional_escape(str(remove_event))
        e_add_label = conditional_escape(str(add_label))
        e_class = conditional_escape(str(custom_class))

        try:
            min_rows = int(min_rows)
        except (ValueError, TypeError):
            min_rows = 1
        try:
            max_rows = int(max_rows)
        except (ValueError, TypeError):
            max_rows = 10

        if not isinstance(rows, list):
            rows = [{"value": ""}]

        classes = ["dj-form-array"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        row_count = len(rows)
        can_add = row_count < max_rows
        can_remove = row_count > min_rows

        # Render template content for each row, or default inputs
        content = self.nodelist.render(context)
        rows_html = []
        for i, row in enumerate(rows):
            val = conditional_escape(str(row.get("value", "") if isinstance(row, dict) else row))
            remove_html = ""
            if can_remove:
                remove_html = (
                    f'<button class="dj-form-array__remove" type="button" '
                    f'dj-click="{e_remove_event}" data-value="{i}" '
                    f'aria-label="Remove row {i + 1}">&times;</button>'
                )
            rows_html.append(
                f'<div class="dj-form-array__row" data-index="{i}">'
                f'<input type="text" name="{e_name}[{i}]" value="{val}" '
                f'class="dj-form-array__input">'
                f'{remove_html}</div>'
            )

        add_disabled = "" if can_add else " disabled"
        add_html = (
            f'<button class="dj-form-array__add" type="button" '
            f'dj-click="{e_add_event}"{add_disabled}>'
            f'{e_add_label}</button>'
        )

        return mark_safe(
            f'<div class="{class_str}" data-min="{min_rows}" data-max="{max_rows}">'
            f'<div class="dj-form-array__rows">{"".join(rows_html)}</div>'
            f'{add_html}</div>'
        )


@register.tag("form_array")
def do_form_array(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endform_array",))
    parser.delete_first_token()
    return FormArrayNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Scroll Spy
# ---------------------------------------------------------------------------

class ScrollSpyNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        import json as _json

        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        sections = kw.get("sections", [])
        active = kw.get("active", "")
        active_event = kw.get("active_event", "section_changed")
        offset = kw.get("offset", "0px")
        custom_class = kw.get("class", "")

        e_event = conditional_escape(str(active_event))
        e_offset = conditional_escape(str(offset))
        e_class = conditional_escape(str(custom_class))

        if not isinstance(sections, list):
            sections = []

        sections_json = conditional_escape(_json.dumps(sections))

        classes = ["dj-scroll-spy"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        nav_items = []
        for section_id in sections:
            e_id = conditional_escape(str(section_id))
            active_cls = " dj-scroll-spy__item--active" if str(section_id) == str(active) else ""
            nav_items.append(
                f'<a href="#{e_id}" '
                f'class="dj-scroll-spy__item{active_cls}" '
                f'data-section="{e_id}">{e_id}</a>'
            )

        return mark_safe(
            f'<nav class="{class_str}" dj-hook="ScrollSpy" '
            f'data-sections="{sections_json}" '
            f'data-event="{e_event}" data-offset="{e_offset}" '
            f'role="navigation" aria-label="Section navigation">'
            f'{"".join(nav_items)}</nav>'
        )


@register.tag("scroll_spy")
def do_scroll_spy(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ScrollSpyNode(kwargs)


# ---------------------------------------------------------------------------
# Page Alert / Banner
# ---------------------------------------------------------------------------

class PageAlertNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        alert_type = kw.get("type", "info")
        dismissible = kw.get("dismissible", False)
        dismiss_event = kw.get("dismiss_event", "dismiss_alert")
        icon = kw.get("icon", "")
        custom_class = kw.get("class", "")

        e_type = conditional_escape(str(alert_type))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-page-alert", f"dj-page-alert--{e_type}"]
        if dismissible:
            classes.append("dj-page-alert--dismissible")
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        content = self.nodelist.render(context)

        icon_html = ""
        if icon:
            icon_html = f'<span class="dj-page-alert__icon">{conditional_escape(str(icon))}</span>'

        dismiss_html = ""
        if dismissible:
            e_dismiss = conditional_escape(str(dismiss_event))
            dismiss_html = (
                f'<button class="dj-page-alert__dismiss" '
                f'dj-click="{e_dismiss}" aria-label="Dismiss">&times;</button>'
            )

        return mark_safe(
            f'<div class="{class_str}" role="alert">'
            f'{icon_html}'
            f'<span class="dj-page-alert__message">{content}</span>'
            f'{dismiss_html}</div>'
        )


@register.tag("page_alert")
def do_page_alert(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endpage_alert",))
    parser.delete_first_token()
    return PageAlertNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Dropdown Menu
# ---------------------------------------------------------------------------

class DropdownMenuNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        label = kw.get("label", "Menu")
        items = kw.get("items", [])
        is_open = kw.get("open", False)
        toggle_event = kw.get("toggle_event", "toggle_menu")
        align = kw.get("align", "left")
        custom_class = kw.get("class", "")

        e_label = conditional_escape(str(label))
        e_toggle = conditional_escape(str(toggle_event))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-dropdown-menu"]
        if is_open:
            classes.append("dj-dropdown-menu--open")
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        trigger = (
            f'<button class="dj-dropdown-menu__trigger" '
            f'dj-click="{e_toggle}" '
            f'aria-expanded="{"true" if is_open else "false"}" '
            f'aria-haspopup="true">{e_label}</button>'
        )

        if not is_open:
            return mark_safe(f'<div class="{class_str}">{trigger}</div>')

        if not isinstance(items, list):
            items = []

        # Render nodelist children (menu_item / menu_divider tags)
        menu_child_nodes = [n for n in self.nodelist if isinstance(n, (MenuItemNode, MenuDividerNode))]

        menu_items = []
        if menu_child_nodes:
            for node in menu_child_nodes:
                menu_items.append(node.render(context))
        else:
            for item in items:
                if not isinstance(item, dict):
                    continue
                if item.get("divider"):
                    menu_items.append('<hr class="dj-dropdown-menu__divider" role="separator">')
                    continue

                item_cls = "dj-dropdown-menu__item"
                if item.get("danger"):
                    item_cls += " dj-dropdown-menu__item--danger"
                if item.get("disabled"):
                    item_cls += " dj-dropdown-menu__item--disabled"

                e_item_label = conditional_escape(str(item.get("label", "")))
                e_event = conditional_escape(str(item.get("event", "")))
                disabled_attr = " disabled" if item.get("disabled") else ""
                event_attr = f' dj-click="{e_event}"' if e_event else ""

                icon_html = ""
                if item.get("icon"):
                    icon_html = f'<span class="dj-dropdown-menu__icon">{conditional_escape(str(item["icon"]))}</span>'

                menu_items.append(
                    f'<button class="{item_cls}" role="menuitem"'
                    f'{event_attr}{disabled_attr}>'
                    f'{icon_html}{e_item_label}</button>'
                )

        menu = (
            f'<div class="dj-dropdown-menu__content dj-dropdown-menu--{conditional_escape(str(align))}" '
            f'role="menu">{"".join(menu_items)}</div>'
        )

        return mark_safe(f'<div class="{class_str}">{trigger}{menu}</div>')


class MenuItemNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        label = kw.get("label", "")
        event = kw.get("event", "")
        danger = kw.get("danger", False)
        disabled = kw.get("disabled", False)
        icon = kw.get("icon", "")

        item_cls = "dj-dropdown-menu__item"
        if danger:
            item_cls += " dj-dropdown-menu__item--danger"
        if disabled:
            item_cls += " dj-dropdown-menu__item--disabled"

        e_label = conditional_escape(str(label))
        e_event = conditional_escape(str(event))
        disabled_attr = " disabled" if disabled else ""
        event_attr = f' dj-click="{e_event}"' if event else ""

        icon_html = ""
        if icon:
            icon_html = f'<span class="dj-dropdown-menu__icon">{conditional_escape(str(icon))}</span>'

        return (
            f'<button class="{item_cls}" role="menuitem"'
            f'{event_attr}{disabled_attr}>'
            f'{icon_html}{e_label}</button>'
        )


class MenuDividerNode(template.Node):
    def render(self, context):
        return '<hr class="dj-dropdown-menu__divider" role="separator">'


@register.tag("dropdown_menu")
def do_dropdown_menu(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("enddropdown_menu",))
    parser.delete_first_token()
    return DropdownMenuNode(nodelist, kwargs)


@register.tag("menu_item")
def do_menu_item(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return MenuItemNode(kwargs)


@register.tag("menu_divider")
def do_menu_divider(parser, token):
    return MenuDividerNode()


# ---------------------------------------------------------------------------
# Meter / Stacked Progress
# ---------------------------------------------------------------------------

class MeterNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        segments = kw.get("segments", [])
        total = kw.get("total", 100)
        label = kw.get("label", "")
        show_legend = kw.get("show_legend", True)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))

        classes = ["dj-meter"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        try:
            total = int(total)
        except (ValueError, TypeError):
            total = 100

        if not isinstance(segments, list):
            segments = []

        label_html = ""
        if label:
            label_html = f'<div class="dj-meter__label">{conditional_escape(str(label))}</div>'

        bar_parts = []
        for seg in segments:
            if not isinstance(seg, dict):
                continue
            val = seg.get("value", 0)
            try:
                val = float(val)
            except (ValueError, TypeError):
                val = 0
            if total > 0:
                pct = min(100, max(0, (val / total) * 100))
            else:
                pct = 0
            color = conditional_escape(str(seg.get("color", "")))
            seg_label = conditional_escape(str(seg.get("label", "")))
            style = f"width:{pct:.1f}%"
            if color:
                style += f";background:{color}"
            bar_parts.append(
                f'<div class="dj-meter__segment" style="{style}" '
                f'role="meter" aria-valuenow="{int(val)}" '
                f'aria-valuemin="0" aria-valuemax="{total}" '
                f'aria-label="{seg_label}"></div>'
            )

        bar = f'<div class="dj-meter__bar">{"".join(bar_parts)}</div>'

        legend_html = ""
        if show_legend and segments:
            legend_items = []
            for seg in segments:
                if not isinstance(seg, dict):
                    continue
                color = conditional_escape(str(seg.get("color", "")))
                seg_label = conditional_escape(str(seg.get("label", "")))
                val = seg.get("value", 0)
                swatch_style = f"background:{color}" if color else ""
                legend_items.append(
                    f'<div class="dj-meter__legend-item">'
                    f'<span class="dj-meter__legend-swatch" style="{swatch_style}"></span>'
                    f'<span class="dj-meter__legend-label">{seg_label}</span>'
                    f'<span class="dj-meter__legend-value">{val}</span></div>'
                )
            legend_html = f'<div class="dj-meter__legend">{"".join(legend_items)}</div>'

        return mark_safe(f'<div class="{class_str}">{label_html}{bar}{legend_html}</div>')


@register.tag("meter")
def do_meter(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return MeterNode(kwargs)


# ---------------------------------------------------------------------------
# Export Dialog
# ---------------------------------------------------------------------------

class ExportDialogNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        formats = kw.get("formats", [])
        columns = kw.get("columns", [])
        event = kw.get("event", "export")
        is_open = kw.get("open", False)
        close_event = kw.get("close_event", "close_export")
        selected_format = kw.get("selected_format", "")
        title = kw.get("title", "Export Data")
        custom_class = kw.get("class", "")

        if not is_open:
            return ""

        e_title = conditional_escape(str(title))
        e_event = conditional_escape(str(event))
        e_close = conditional_escape(str(close_event))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-export-dialog"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(formats, list):
            formats = []
        if not isinstance(columns, list):
            columns = []

        if not selected_format and formats:
            selected_format = formats[0]

        format_options = []
        for fmt in formats:
            e_fmt = conditional_escape(str(fmt))
            checked = " checked" if str(fmt) == str(selected_format) else ""
            format_options.append(
                f'<label class="dj-export-dialog__format">'
                f'<input type="radio" name="export_format" value="{e_fmt}"{checked}>'
                f'<span class="dj-export-dialog__format-label">{e_fmt.upper()}</span></label>'
            )
        format_section = (
            f'<div class="dj-export-dialog__formats">'
            f'<h4 class="dj-export-dialog__section-title">Format</h4>'
            f'{"".join(format_options)}</div>'
        )

        col_options = []
        for col in columns:
            if not isinstance(col, dict):
                continue
            e_id = conditional_escape(str(col.get("id", "")))
            e_label = conditional_escape(str(col.get("label", "")))
            checked = " checked" if col.get("checked", True) else ""
            col_options.append(
                f'<label class="dj-export-dialog__column">'
                f'<input type="checkbox" name="export_col" value="{e_id}"{checked}>'
                f'<span>{e_label}</span></label>'
            )
        col_section = (
            f'<div class="dj-export-dialog__columns">'
            f'<h4 class="dj-export-dialog__section-title">Columns</h4>'
            f'{"".join(col_options)}</div>'
        )

        return mark_safe(
            f'<div class="dj-export-dialog__backdrop" dj-click="{e_close}">'
            f'<div class="{class_str}" onclick="event.stopPropagation()">'
            f'<div class="dj-export-dialog__header">'
            f'<h3>{e_title}</h3>'
            f'<button class="dj-export-dialog__close" dj-click="{e_close}">&times;</button></div>'
            f'<div class="dj-export-dialog__body">{format_section}{col_section}</div>'
            f'<div class="dj-export-dialog__footer">'
            f'<button class="dj-export-dialog__cancel" dj-click="{e_close}">Cancel</button>'
            f'<button class="dj-export-dialog__submit" dj-click="{e_event}">Export</button>'
            f'</div></div></div>'
        )


@register.tag("export_dialog")
def do_export_dialog(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ExportDialogNode(kwargs)


# ---------------------------------------------------------------------------
# Import Wizard
# ---------------------------------------------------------------------------

class ImportWizardNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        accepted_formats = kw.get("accepted_formats", ".csv")
        model_fields = kw.get("model_fields", [])
        event = kw.get("event", "import_data")
        step = kw.get("step", "upload")
        upload_event = kw.get("upload_event", "upload_file")
        custom_class = kw.get("class", "")

        e_event = conditional_escape(str(event))
        e_formats = conditional_escape(str(accepted_formats))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-import-wizard"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(model_fields, list):
            model_fields = []

        steps = ["upload", "map", "preview"]
        step_labels = {"upload": "Upload", "map": "Map Fields", "preview": "Preview"}
        active_idx = steps.index(step) if step in steps else 0

        step_items = []
        for i, s in enumerate(steps):
            step_cls = "dj-import-wizard__step"
            if i < active_idx:
                step_cls += " dj-import-wizard__step--completed"
            elif i == active_idx:
                step_cls += " dj-import-wizard__step--active"
            step_items.append(
                f'<div class="{step_cls}">'
                f'<span class="dj-import-wizard__step-number">{i + 1}</span>'
                f'<span class="dj-import-wizard__step-label">'
                f'{step_labels[s]}</span></div>'
            )
        nav = f'<div class="dj-import-wizard__nav">{"".join(step_items)}</div>'

        if step == "upload":
            e_upload = conditional_escape(str(upload_event))
            body = (
                f'<div class="dj-import-wizard__upload">'
                f'<div class="dj-import-wizard__dropzone">'
                f'<p>Drag &amp; drop or click to upload</p>'
                f'<input type="file" accept="{e_formats}" '
                f'class="dj-import-wizard__file-input" dj-change="{e_upload}">'
                f'<p class="dj-import-wizard__formats">Accepted: {e_formats}</p>'
                f'</div></div>'
            )
        elif step == "map":
            field_rows = []
            for field in model_fields:
                if not isinstance(field, dict):
                    continue
                e_id = conditional_escape(str(field.get("id", "")))
                e_label = conditional_escape(str(field.get("label", "")))
                field_rows.append(
                    f'<div class="dj-import-wizard__field-row">'
                    f'<span class="dj-import-wizard__field-label">{e_label}</span>'
                    f'<select class="dj-import-wizard__field-select" name="map_{e_id}">'
                    f'<option value="">-- Skip --</option></select></div>'
                )
            body = f'<div class="dj-import-wizard__mapping">{"".join(field_rows)}</div>'
        else:
            body = (
                f'<div class="dj-import-wizard__preview">'
                f'<p>Preview your data before importing.</p>'
                f'<button class="dj-import-wizard__import-btn" '
                f'dj-click="{e_event}">Import</button></div>'
            )

        return mark_safe(f'<div class="{class_str}">{nav}{body}</div>')


@register.tag("import_wizard")
def do_import_wizard(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ImportWizardNode(kwargs)


# ---------------------------------------------------------------------------
# Audit Log Table
# ---------------------------------------------------------------------------

class AuditLogNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        entries = kw.get("entries", [])
        stream_event = kw.get("stream_event", "")
        columns = kw.get("columns", ["timestamp", "user", "action", "resource", "detail"])
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))

        classes = ["dj-audit-log"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(entries, list):
            entries = []
        if not isinstance(columns, list):
            columns = ["timestamp", "user", "action", "resource", "detail"]

        stream_attr = ""
        if stream_event:
            e_stream = conditional_escape(str(stream_event))
            stream_attr = f' data-stream-event="{e_stream}"'

        col_labels = {
            "timestamp": "Timestamp", "user": "User", "action": "Action",
            "resource": "Resource", "detail": "Detail",
        }

        headers = []
        for col in columns:
            label = conditional_escape(col_labels.get(col, col.title()))
            headers.append(f'<th class="dj-audit-log__th">{label}</th>')
        thead = f'<thead><tr>{"".join(headers)}</tr></thead>'

        rows = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            cells = []
            for col in columns:
                val = conditional_escape(str(entry.get(col, "")))
                cell_cls = f"dj-audit-log__td dj-audit-log__td--{col}"
                if col == "action":
                    cell_cls += f" dj-audit-log__action--{conditional_escape(str(entry.get('action', '')))}"
                cells.append(f'<td class="{cell_cls}">{val}</td>')
            rows.append(f'<tr class="dj-audit-log__row">{"".join(cells)}</tr>')

        if rows:
            tbody = f'<tbody>{"".join(rows)}</tbody>'
        else:
            col_count = len(columns)
            tbody = (
                f'<tbody><tr><td colspan="{col_count}" '
                f'class="dj-audit-log__empty">No entries</td></tr></tbody>'
            )

        return mark_safe(
            f'<div class="{class_str}"{stream_attr}>'
            f'<table class="dj-audit-log__table">{thead}{tbody}</table></div>'
        )


@register.tag("audit_log")
def do_audit_log(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return AuditLogNode(kwargs)


# ---------------------------------------------------------------------------
# Error Boundary
# ---------------------------------------------------------------------------

class ErrorBoundaryNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        fallback = kw.get("fallback", "Something went wrong")
        retry_event = kw.get("retry_event", "")
        custom_class = kw.get("class", "")

        e_fallback = conditional_escape(str(fallback))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-error-boundary"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        try:
            content = self.nodelist.render(context)
        except Exception:
            classes.append("dj-error-boundary--error")
            class_str = " ".join(classes)
            retry_html = ""
            if retry_event:
                e_retry = conditional_escape(str(retry_event))
                retry_html = (
                    f'<button class="dj-error-boundary__retry" '
                    f'dj-click="{e_retry}">Retry</button>'
                )
            return mark_safe(
                f'<div class="{class_str}" role="alert">'
                f'<div class="dj-error-boundary__fallback">'
                f'<p class="dj-error-boundary__message">{e_fallback}</p>'
                f'{retry_html}</div></div>'
            )

        return mark_safe(f'<div class="{class_str}">{content}</div>')


@register.tag("error_boundary")
def do_error_boundary(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("enderror_boundary",))
    parser.delete_first_token()
    return ErrorBoundaryNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Sortable List
# ---------------------------------------------------------------------------

class SortableListNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        items = kw.get("items", [])
        move_event = kw.get("move_event", "reorder")
        handle = kw.get("handle", True)
        disabled = kw.get("disabled", False)
        custom_class = kw.get("class", "")

        e_event = conditional_escape(str(move_event))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-sortable-list"]
        if disabled:
            classes.append("dj-sortable-list--disabled")
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(items, list):
            items = []

        items_html = []
        for item in items:
            if not isinstance(item, dict):
                continue
            item_id = conditional_escape(str(item.get("id", "")))
            label = conditional_escape(str(item.get("label", "")))
            handle_html = (
                '<span class="dj-sortable-list__handle" aria-hidden="true">&#x2630;</span> '
                if handle else ""
            )
            drag_attr = ' draggable="true"' if not disabled else ""
            items_html.append(
                f'<li class="dj-sortable-list__item" data-id="{item_id}"{drag_attr} '
                f'role="listitem">'
                f'{handle_html}'
                f'<span class="dj-sortable-list__label">{label}</span></li>'
            )

        disabled_attr = ' data-disabled="true"' if disabled else ""

        return mark_safe(
            f'<ul class="{class_str}" dj-hook="SortableList" '
            f'data-move-event="{e_event}" '
            f'role="list"{disabled_attr}>{"".join(items_html)}</ul>'
        )


@register.tag("sortable_list")
def do_sortable_list(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return SortableListNode(kwargs)


# ---------------------------------------------------------------------------
# Sortable Grid
# ---------------------------------------------------------------------------

class SortableGridNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        items = kw.get("items", [])
        columns = kw.get("columns", 3)
        move_event = kw.get("move_event", "reorder")
        gap = kw.get("gap", "0.75rem")
        disabled = kw.get("disabled", False)
        custom_class = kw.get("class", "")

        e_event = conditional_escape(str(move_event))
        e_class = conditional_escape(str(custom_class))
        e_gap = conditional_escape(str(gap))

        classes = ["dj-sortable-grid"]
        if disabled:
            classes.append("dj-sortable-grid--disabled")
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(items, list):
            items = []

        try:
            cols = int(columns)
        except (ValueError, TypeError):
            cols = 3

        items_html = []
        for item in items:
            if not isinstance(item, dict):
                continue
            item_id = conditional_escape(str(item.get("id", "")))
            label = conditional_escape(str(item.get("label", "")))
            thumbnail = item.get("thumbnail", "")
            thumb_html = ""
            if thumbnail:
                e_thumb = conditional_escape(str(thumbnail))
                thumb_html = (
                    f'<img class="dj-sortable-grid__thumb" '
                    f'src="{e_thumb}" alt="{label}" loading="lazy">'
                )
            drag_attr = ' draggable="true"' if not disabled else ""
            items_html.append(
                f'<div class="dj-sortable-grid__item" data-id="{item_id}"{drag_attr}>'
                f'{thumb_html}'
                f'<span class="dj-sortable-grid__label">{label}</span></div>'
            )

        disabled_attr = ' data-disabled="true"' if disabled else ""
        style = f'style="grid-template-columns:repeat({cols},1fr);gap:{e_gap}"'

        return mark_safe(
            f'<div class="{class_str}" dj-hook="SortableGrid" '
            f'data-move-event="{e_event}" data-columns="{cols}" '
            f'{style} role="grid"{disabled_attr}>{"".join(items_html)}</div>'
        )


@register.tag("sortable_grid")
def do_sortable_grid(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return SortableGridNode(kwargs)


# ---------------------------------------------------------------------------
# Image Cropper
# ---------------------------------------------------------------------------

class ImageCropperNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        src = kw.get("src", "")
        crop_event = kw.get("crop_event", "save_crop")
        aspect_ratio = kw.get("aspect_ratio", "")
        min_width = kw.get("min_width", 50)
        min_height = kw.get("min_height", 50)
        disabled = kw.get("disabled", False)
        custom_class = kw.get("class", "")

        e_src = conditional_escape(str(src))
        e_event = conditional_escape(str(crop_event))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-image-cropper"]
        if disabled:
            classes.append("dj-image-cropper--disabled")
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        ratio_attr = ""
        if aspect_ratio:
            e_ratio = conditional_escape(str(aspect_ratio))
            ratio_attr = f' data-aspect-ratio="{e_ratio}"'

        try:
            min_w = int(min_width)
        except (ValueError, TypeError):
            min_w = 50
        try:
            min_h = int(min_height)
        except (ValueError, TypeError):
            min_h = 50

        return mark_safe(
            f'<div class="{class_str}" dj-hook="ImageCropper" '
            f'data-crop-event="{e_event}" '
            f'data-min-width="{min_w}" '
            f'data-min-height="{min_h}"{ratio_attr}>'
            f'<div class="dj-image-cropper__canvas">'
            f'<img class="dj-image-cropper__image" src="{e_src}" alt="Image to crop" draggable="false">'
            f'<div class="dj-image-cropper__overlay"></div>'
            f'<div class="dj-image-cropper__selection"></div>'
            f'</div>'
            f'<div class="dj-image-cropper__actions">'
            f'<button class="dj-image-cropper__crop-btn" type="button">Crop</button>'
            f'<button class="dj-image-cropper__reset-btn" type="button">Reset</button>'
            f'</div>'
            f'</div>'
        )


@register.tag("image_cropper")
def do_image_cropper(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return ImageCropperNode(kwargs)


# ---------------------------------------------------------------------------
# Signature Pad
# ---------------------------------------------------------------------------

class SignaturePadNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        name = kw.get("name", "signature")
        save_event = kw.get("save_event", "save_signature")
        width = kw.get("width", 400)
        height = kw.get("height", 200)
        pen_color = kw.get("pen_color", "#000000")
        pen_width = kw.get("pen_width", 2)
        disabled = kw.get("disabled", False)
        custom_class = kw.get("class", "")

        e_name = conditional_escape(str(name))
        e_event = conditional_escape(str(save_event))
        e_color = conditional_escape(str(pen_color))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-signature-pad"]
        if disabled:
            classes.append("dj-signature-pad--disabled")
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        try:
            w = int(width)
        except (ValueError, TypeError):
            w = 400
        try:
            h = int(height)
        except (ValueError, TypeError):
            h = 200
        try:
            pw = int(pen_width)
        except (ValueError, TypeError):
            pw = 2

        disabled_attr = " disabled" if disabled else ""

        return mark_safe(
            f'<div class="{class_str}" dj-hook="SignaturePad" '
            f'data-save-event="{e_event}" '
            f'data-pen-color="{e_color}" '
            f'data-pen-width="{pw}">'
            f'<canvas class="dj-signature-pad__canvas" '
            f'width="{w}" height="{h}"'
            f'{disabled_attr}></canvas>'
            f'<input type="hidden" name="{e_name}" class="dj-signature-pad__value">'
            f'<div class="dj-signature-pad__actions">'
            f'<button class="dj-signature-pad__clear-btn" type="button">Clear</button>'
            f'<button class="dj-signature-pad__save-btn" type="button"'
            f'{disabled_attr}>Save</button>'
            f'</div>'
            f'</div>'
        )


@register.tag("signature_pad")
def do_signature_pad(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return SignaturePadNode(kwargs)


# ---------------------------------------------------------------------------
# Resizable Panel
# ---------------------------------------------------------------------------

class ResizablePanelNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        direction = kw.get("direction", "horizontal")
        min_size = kw.get("min_size", "100px")
        max_size = kw.get("max_size", "none")
        initial_size = kw.get("initial_size", "50%")
        disabled = kw.get("disabled", False)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))

        if direction not in ("horizontal", "vertical"):
            direction = "horizontal"

        classes = ["dj-resizable-panel", f"dj-resizable-panel--{direction}"]
        if disabled:
            classes.append("dj-resizable-panel--disabled")
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        e_min = conditional_escape(str(min_size))
        e_max = conditional_escape(str(max_size))
        e_initial = conditional_escape(str(initial_size))

        content = self.nodelist.render(context)

        size_prop = "width" if direction == "horizontal" else "height"
        style_parts = [f"{size_prop}:{e_initial}", f"min-{size_prop}:{e_min}"]
        if max_size != "none":
            style_parts.append(f"max-{size_prop}:{e_max}")
        style = f'style="{";".join(style_parts)}"'

        disabled_attr = ' data-disabled="true"' if disabled else ""

        return mark_safe(
            f'<div class="{class_str}" dj-hook="ResizablePanel" '
            f'data-direction="{direction}" '
            f'data-min-size="{e_min}" data-max-size="{e_max}" '
            f'{style}{disabled_attr}>'
            f'<div class="dj-resizable-panel__content">{content}</div>'
            f'<div class="dj-resizable-panel__handle" role="separator" '
            f'aria-orientation="{direction}" tabindex="0">'
            f'<span class="dj-resizable-panel__handle-bar"></span>'
            f'</div>'
            f'</div>'
        )


@register.tag("resizable_panel")
def do_resizable_panel(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("endresizable_panel",))
    parser.delete_first_token()
    return ResizablePanelNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Image Lightbox
# ---------------------------------------------------------------------------

class LightboxNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        images = kw.get("images", [])
        active = kw.get("active", 0)
        is_open = kw.get("open", False)
        close_event = kw.get("close_event", "close_lightbox")
        navigate_event = kw.get("navigate_event", "lightbox_navigate")
        show_counter = kw.get("show_counter", True)
        custom_class = kw.get("class", "")

        if not is_open:
            return ""

        e_close = conditional_escape(str(close_event))
        e_nav = conditional_escape(str(navigate_event))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-lightbox"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(images, list):
            images = []

        total = len(images)
        try:
            idx = int(active)
        except (ValueError, TypeError):
            idx = 0
        idx = max(0, min(idx, total - 1)) if total else 0

        # Current image
        img_html = ""
        caption_html = ""
        if images and 0 <= idx < total:
            img = images[idx]
            if isinstance(img, dict):
                e_src = conditional_escape(str(img.get("src", "")))
                e_alt = conditional_escape(str(img.get("alt", "")))
                caption = img.get("caption", "")
                img_html = (
                    f'<img class="dj-lightbox__image" src="{e_src}" alt="{e_alt}">'
                )
                if caption:
                    caption_html = (
                        f'<p class="dj-lightbox__caption">'
                        f'{conditional_escape(str(caption))}</p>'
                    )

        # Navigation
        prev_btn = (
            f'<button class="dj-lightbox__prev" dj-click="{e_nav}" '
            f'data-value="{idx - 1}" aria-label="Previous">'
            f'&#8249;</button>'
        ) if total > 1 else ""

        next_btn = (
            f'<button class="dj-lightbox__next" dj-click="{e_nav}" '
            f'data-value="{idx + 1}" aria-label="Next">'
            f'&#8250;</button>'
        ) if total > 1 else ""

        counter = ""
        if show_counter and total > 1:
            counter = (
                f'<span class="dj-lightbox__counter">'
                f'{idx + 1} of {total}</span>'
            )

        return mark_safe(
            f'<div class="{class_str}" dj-hook="ImageLightbox" '
            f'data-close-event="{e_close}" data-navigate-event="{e_nav}" '
            f'role="dialog" aria-modal="true">'
            f'<div class="dj-lightbox__backdrop" dj-click="{e_close}"></div>'
            f'<button class="dj-lightbox__close" dj-click="{e_close}" '
            f'aria-label="Close">&times;</button>'
            f'{prev_btn}'
            f'<div class="dj-lightbox__stage">{img_html}{caption_html}</div>'
            f'{next_btn}'
            f'{counter}'
            f'</div>'
        )


@register.tag("lightbox")
def do_lightbox(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return LightboxNode(kwargs)


# ---------------------------------------------------------------------------
# Dashboard Grid
# ---------------------------------------------------------------------------

class DashboardGridNode(template.Node):
    def __init__(self, nodelist, kwargs):
        self.nodelist = nodelist
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        panels = kw.get("panels", [])
        columns = kw.get("columns", 4)
        row_height = kw.get("row_height", "200px")
        gap = kw.get("gap", "1rem")
        move_event = kw.get("move_event", "dashboard_move")
        resize_event = kw.get("resize_event", "dashboard_resize")
        custom_class = kw.get("class", "")

        e_move = conditional_escape(str(move_event))
        e_resize = conditional_escape(str(resize_event))
        e_gap = conditional_escape(str(gap))
        e_row_height = conditional_escape(str(row_height))
        e_class = conditional_escape(str(custom_class))

        classes = ["dj-dashboard-grid"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        try:
            cols = int(columns)
        except (ValueError, TypeError):
            cols = 4

        if not isinstance(panels, list):
            panels = []

        # Render child content (for {% dashboard_grid %}...{% enddashboard_grid %} usage)
        child_content = self.nodelist.render(context) if self.nodelist else ""

        panels_html = []
        for panel in panels:
            if not isinstance(panel, dict):
                continue
            pid = conditional_escape(str(panel.get("id", "")))
            title = conditional_escape(str(panel.get("title", "")))
            content = panel.get("content", "")
            try:
                col = int(panel.get("col", 1))
            except (ValueError, TypeError):
                col = 1
            try:
                row = int(panel.get("row", 1))
            except (ValueError, TypeError):
                row = 1
            try:
                w = int(panel.get("width", 1))
            except (ValueError, TypeError):
                w = 1
            try:
                h = int(panel.get("height", 1))
            except (ValueError, TypeError):
                h = 1

            style = (
                f'grid-column:{col}/span {w};'
                f'grid-row:{row}/span {h}'
            )

            panels_html.append(
                f'<div class="dj-dashboard-grid__panel" data-panel-id="{pid}" '
                f'style="{style}" draggable="true">'
                f'<div class="dj-dashboard-grid__panel-header">'
                f'<span class="dj-dashboard-grid__panel-title">{title}</span>'
                f'<span class="dj-dashboard-grid__panel-drag" aria-hidden="true">&#x2630;</span>'
                f'</div>'
                f'<div class="dj-dashboard-grid__panel-body">{content}</div>'
                f'<div class="dj-dashboard-grid__panel-resize" role="separator"></div>'
                f'</div>'
            )

        grid_style = (
            f'style="display:grid;grid-template-columns:repeat({cols},1fr);'
            f'grid-auto-rows:minmax({e_row_height},auto);gap:{e_gap}"'
        )

        inner = "".join(panels_html) + child_content

        return mark_safe(
            f'<div class="{class_str}" dj-hook="DashboardGrid" '
            f'data-move-event="{e_move}" data-resize-event="{e_resize}" '
            f'data-columns="{cols}" {grid_style}>{inner}</div>'
        )


@register.tag("dashboard_grid")
def do_dashboard_grid(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    nodelist = parser.parse(("enddashboard_grid",))
    parser.delete_first_token()
    return DashboardGridNode(nodelist, kwargs)


# ---------------------------------------------------------------------------
# Bar Chart
# ---------------------------------------------------------------------------

import math as _math

class BarChartNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        data = kw.get("data", [])
        labels = kw.get("labels", [])
        title = kw.get("title", "")
        width = kw.get("width", 400)
        height = kw.get("height", 250)
        color = kw.get("color", "")
        show_values = kw.get("show_values", True)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))
        classes = ["dj-bar-chart"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(data, list):
            data = []
        if not isinstance(labels, list):
            labels = []

        try:
            width = int(width)
        except (ValueError, TypeError):
            width = 400
        try:
            height = int(height)
        except (ValueError, TypeError):
            height = 250

        if not data:
            return mark_safe(f'<div class="{class_str}"><svg></svg></div>')

        w, h = width, height
        pad_top = 30 if title else 10
        pad_bottom = 30
        pad_left = 40
        pad_right = 10
        chart_w = w - pad_left - pad_right
        chart_h = h - pad_top - pad_bottom

        vals = []
        for v in data:
            try:
                vals.append(float(v))
            except (ValueError, TypeError):
                vals.append(0)

        max_val = max(vals) if vals else 1
        if max_val <= 0:
            max_val = 1

        n = len(vals)
        bar_gap = 4
        bar_w = max(1, (chart_w - (n - 1) * bar_gap) / n)

        e_title = conditional_escape(str(title)) if title else "Bar chart"
        parts = [f'<svg class="dj-bar-chart__svg" viewBox="0 0 {w} {h}" '
                 f'width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" '
                 f'role="img" aria-label="{e_title}">']

        if title:
            parts.append(
                f'<text class="dj-bar-chart__title" x="{w / 2}" y="18" '
                f'text-anchor="middle" font-size="13" font-weight="600">'
                f'{conditional_escape(str(title))}</text>'
            )

        e_color = conditional_escape(str(color)) if color else ""
        color_attr = f' fill="{e_color}"' if e_color else ""

        for i, val in enumerate(vals):
            bar_h = (val / max_val) * chart_h if max_val > 0 else 0
            x = pad_left + i * (bar_w + bar_gap)
            y = pad_top + chart_h - bar_h

            lbl = conditional_escape(str(labels[i])) if i < len(labels) else ""
            parts.append(
                f'<rect class="dj-bar-chart__bar" x="{x:.1f}" y="{y:.1f}" '
                f'width="{bar_w:.1f}" height="{bar_h:.1f}"{color_attr}>'
                f'<title>{lbl}: {val}</title></rect>'
            )

            if show_values:
                parts.append(
                    f'<text class="dj-bar-chart__value" x="{x + bar_w / 2:.1f}" '
                    f'y="{y - 4:.1f}" text-anchor="middle" font-size="10">'
                    f'{val:g}</text>'
                )

            if i < len(labels):
                parts.append(
                    f'<text class="dj-bar-chart__label" x="{x + bar_w / 2:.1f}" '
                    f'y="{pad_top + chart_h + 16:.1f}" text-anchor="middle" font-size="10">'
                    f'{lbl}</text>'
                )

        parts.append("</svg>")
        return mark_safe(f'<div class="{class_str}">{"".join(parts)}</div>')


@register.tag("bar_chart")
def do_bar_chart(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return BarChartNode(kwargs)


# ---------------------------------------------------------------------------
# Line Chart
# ---------------------------------------------------------------------------

class LineChartNode(template.Node):
    COLORS = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#8b5cf6", "#06b6d4"]

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        series = kw.get("series", [])
        labels = kw.get("labels", [])
        title = kw.get("title", "")
        width = kw.get("width", 400)
        height = kw.get("height", 250)
        area = kw.get("area", False)
        show_dots = kw.get("show_dots", True)
        show_legend = kw.get("show_legend", True)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))
        classes = ["dj-line-chart"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(series, list):
            series = []
        if not isinstance(labels, list):
            labels = []

        try:
            width = int(width)
        except (ValueError, TypeError):
            width = 400
        try:
            height = int(height)
        except (ValueError, TypeError):
            height = 250

        if not series:
            return mark_safe(f'<div class="{class_str}"><svg></svg></div>')

        w, h = width, height
        pad_top = 30 if title else 10
        pad_bottom = 40 if show_legend else 30
        pad_left = 40
        pad_right = 10
        chart_w = w - pad_left - pad_right
        chart_h = h - pad_top - pad_bottom

        all_vals = []
        for s in series:
            if isinstance(s, dict):
                for v in s.get("data", []):
                    try:
                        all_vals.append(float(v))
                    except (ValueError, TypeError):
                        pass
        max_val = max(all_vals) if all_vals else 1
        min_val = min(all_vals) if all_vals else 0
        val_range = max_val - min_val if max_val != min_val else 1

        e_title = conditional_escape(str(title)) if title else "Line chart"
        parts = [f'<svg class="dj-line-chart__svg" viewBox="0 0 {w} {h}" '
                 f'width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" '
                 f'role="img" aria-label="{e_title}">']

        if title:
            parts.append(
                f'<text class="dj-line-chart__title" x="{w / 2}" y="18" '
                f'text-anchor="middle" font-size="13" font-weight="600">'
                f'{conditional_escape(str(title))}</text>'
            )

        for si, s in enumerate(series):
            if not isinstance(s, dict):
                continue
            data = s.get("data", [])
            color = conditional_escape(str(s.get("color", self.COLORS[si % len(self.COLORS)])))
            name = conditional_escape(str(s.get("name", f"Series {si + 1}")))

            if not data:
                continue

            n = len(data)
            points = []
            for i, v in enumerate(data):
                try:
                    v = float(v)
                except (ValueError, TypeError):
                    v = 0
                x = pad_left + (i / max(n - 1, 1)) * chart_w
                y = pad_top + chart_h - ((v - min_val) / val_range) * chart_h
                points.append((x, y, v))

            path = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
                            for i, (x, y, _) in enumerate(points))

            if area and points:
                area_path = (
                    path
                    + f" L{points[-1][0]:.1f},{pad_top + chart_h:.1f}"
                    + f" L{points[0][0]:.1f},{pad_top + chart_h:.1f} Z"
                )
                parts.append(
                    f'<path class="dj-line-chart__area" d="{area_path}" '
                    f'fill="{color}" opacity="0.15"/>'
                )

            parts.append(
                f'<path class="dj-line-chart__line" d="{path}" '
                f'fill="none" stroke="{color}" stroke-width="2"/>'
            )

            if show_dots:
                for x, y, v in points:
                    parts.append(
                        f'<circle class="dj-line-chart__dot" cx="{x:.1f}" cy="{y:.1f}" '
                        f'r="3" fill="{color}">'
                        f'<title>{name}: {v:g}</title></circle>'
                    )

        if labels:
            n = len(labels)
            for i, lbl in enumerate(labels):
                x = pad_left + (i / max(n - 1, 1)) * chart_w
                parts.append(
                    f'<text class="dj-line-chart__label" x="{x:.1f}" '
                    f'y="{pad_top + chart_h + 16:.1f}" text-anchor="middle" font-size="10">'
                    f'{conditional_escape(str(lbl))}</text>'
                )

        if show_legend and series:
            lx = pad_left
            ly = h - 8
            for si, s in enumerate(series):
                if not isinstance(s, dict):
                    continue
                color = conditional_escape(str(s.get("color", self.COLORS[si % len(self.COLORS)])))
                name = conditional_escape(str(s.get("name", f"Series {si + 1}")))
                parts.append(
                    f'<rect x="{lx}" y="{ly - 6}" width="10" height="10" rx="2" fill="{color}"/>'
                )
                parts.append(f'<text x="{lx + 14}" y="{ly + 3}" font-size="10">{name}</text>')
                lx += len(name) * 7 + 24

        parts.append("</svg>")
        return mark_safe(f'<div class="{class_str}">{"".join(parts)}</div>')


@register.tag("line_chart")
def do_line_chart(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return LineChartNode(kwargs)


# ---------------------------------------------------------------------------
# Pie / Donut Chart
# ---------------------------------------------------------------------------

class PieChartNode(template.Node):
    COLORS = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#8b5cf6",
              "#06b6d4", "#ec4899", "#f97316"]

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        segments = kw.get("segments", [])
        title = kw.get("title", "")
        width = kw.get("width", 300)
        height = kw.get("height", 300)
        donut = kw.get("donut", False)
        inner_radius = kw.get("inner_radius", 0.6)
        show_labels = kw.get("show_labels", True)
        show_legend = kw.get("show_legend", True)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))
        classes = ["dj-pie-chart"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(segments, list):
            segments = []

        try:
            width = int(width)
        except (ValueError, TypeError):
            width = 300
        try:
            height = int(height)
        except (ValueError, TypeError):
            height = 300
        try:
            inner_radius = float(inner_radius)
        except (ValueError, TypeError):
            inner_radius = 0.6

        if not segments:
            return mark_safe(f'<div class="{class_str}"><svg></svg></div>')

        w, h = width, height
        title_offset = 24 if title else 0
        legend_offset = 24 if show_legend else 0
        cx = w / 2
        cy = title_offset + (h - title_offset - legend_offset) / 2
        r = min(cx, (h - title_offset - legend_offset) / 2) - 10
        ir = r * inner_radius if donut else 0

        total = 0
        for seg in segments:
            if isinstance(seg, dict):
                try:
                    total += float(seg.get("value", 0))
                except (ValueError, TypeError):
                    pass

        if total <= 0:
            return mark_safe(f'<div class="{class_str}"><svg></svg></div>')

        e_title = conditional_escape(str(title)) if title else "Pie chart"
        parts = [f'<svg class="dj-pie-chart__svg" viewBox="0 0 {w} {h}" '
                 f'width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" '
                 f'role="img" aria-label="{e_title}">']

        if title:
            parts.append(
                f'<text class="dj-pie-chart__title" x="{cx}" y="18" '
                f'text-anchor="middle" font-size="13" font-weight="600">'
                f'{conditional_escape(str(title))}</text>'
            )

        angle = -_math.pi / 2

        for si, seg in enumerate(segments):
            if not isinstance(seg, dict):
                continue
            try:
                val = float(seg.get("value", 0))
            except (ValueError, TypeError):
                val = 0
            if val <= 0:
                continue
            color = conditional_escape(str(seg.get("color", self.COLORS[si % len(self.COLORS)])))
            label = conditional_escape(str(seg.get("label", "")))
            pct = val / total

            sweep = pct * 2 * _math.pi
            x1 = cx + r * _math.cos(angle)
            y1 = cy + r * _math.sin(angle)
            x2 = cx + r * _math.cos(angle + sweep)
            y2 = cy + r * _math.sin(angle + sweep)
            large = 1 if sweep > _math.pi else 0

            if donut:
                ix1 = cx + ir * _math.cos(angle)
                iy1 = cy + ir * _math.sin(angle)
                ix2 = cx + ir * _math.cos(angle + sweep)
                iy2 = cy + ir * _math.sin(angle + sweep)
                d = (f"M{x1:.2f},{y1:.2f} A{r},{r} 0 {large},1 {x2:.2f},{y2:.2f} "
                     f"L{ix2:.2f},{iy2:.2f} A{ir},{ir} 0 {large},0 {ix1:.2f},{iy1:.2f} Z")
            else:
                d = (f"M{cx},{cy} L{x1:.2f},{y1:.2f} "
                     f"A{r},{r} 0 {large},1 {x2:.2f},{y2:.2f} Z")

            parts.append(
                f'<path class="dj-pie-chart__segment" d="{d}" fill="{color}">'
                f'<title>{label}: {val:g} ({pct * 100:.1f}%)</title></path>'
            )

            if show_labels and pct >= 0.05:
                mid_angle = angle + sweep / 2
                lr = r * 0.7 if not donut else (r + ir) / 2
                lx = cx + lr * _math.cos(mid_angle)
                ly = cy + lr * _math.sin(mid_angle)
                parts.append(
                    f'<text class="dj-pie-chart__pct" x="{lx:.1f}" y="{ly:.1f}" '
                    f'text-anchor="middle" dominant-baseline="central" '
                    f'font-size="10" fill="#fff" font-weight="600">'
                    f'{pct * 100:.0f}%</text>'
                )

            angle += sweep

        if show_legend:
            lx = 10
            ly = h - 8
            for si, seg in enumerate(segments):
                if not isinstance(seg, dict):
                    continue
                color = conditional_escape(str(seg.get("color", self.COLORS[si % len(self.COLORS)])))
                label = conditional_escape(str(seg.get("label", "")))
                parts.append(
                    f'<rect x="{lx}" y="{ly - 6}" width="10" height="10" rx="2" fill="{color}"/>'
                )
                parts.append(f'<text x="{lx + 14}" y="{ly + 3}" font-size="10">{label}</text>')
                lx += len(label) * 7 + 24

        parts.append("</svg>")
        return mark_safe(f'<div class="{class_str}">{"".join(parts)}</div>')


@register.tag("pie_chart")
def do_pie_chart(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return PieChartNode(kwargs)


# ---------------------------------------------------------------------------
# Sparkline
# ---------------------------------------------------------------------------

class SparklineNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        data = kw.get("data", [])
        variant = kw.get("variant", "line")
        width = kw.get("width", 100)
        height = kw.get("height", 24)
        color = kw.get("color", "")
        stroke_width = kw.get("stroke_width", 1.5)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))
        classes = ["dj-sparkline"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(data, list):
            data = []

        try:
            width = int(width)
        except (ValueError, TypeError):
            width = 100
        try:
            height = int(height)
        except (ValueError, TypeError):
            height = 24
        try:
            stroke_width = float(stroke_width)
        except (ValueError, TypeError):
            stroke_width = 1.5

        if not data:
            return mark_safe(f'<span class="{class_str}"><svg></svg></span>')

        w, h = width, height
        pad = 2
        chart_w = w - pad * 2
        chart_h = h - pad * 2

        vals = []
        for v in data:
            try:
                vals.append(float(v))
            except (ValueError, TypeError):
                vals.append(0)

        max_val = max(vals) if vals else 1
        min_val = min(vals) if vals else 0
        val_range = max_val - min_val if max_val != min_val else 1

        e_color = conditional_escape(str(color)) if color else ""

        parts = [f'<svg class="dj-sparkline__svg" viewBox="0 0 {w} {h}" '
                 f'width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" '
                 f'role="img" aria-label="Sparkline">']

        if variant == "bar":
            n = len(vals)
            bar_gap = 1
            bar_w = max(1, (chart_w - (n - 1) * bar_gap) / n)
            for i, v in enumerate(vals):
                bar_h = max(1, ((v - min_val) / val_range) * chart_h)
                x = pad + i * (bar_w + bar_gap)
                y = pad + chart_h - bar_h
                fill = f' fill="{e_color}"' if e_color else ""
                parts.append(
                    f'<rect class="dj-sparkline__bar" x="{x:.1f}" y="{y:.1f}" '
                    f'width="{bar_w:.1f}" height="{bar_h:.1f}"{fill}/>'
                )
        else:
            n = len(vals)
            points = []
            for i, v in enumerate(vals):
                x = pad + (i / max(n - 1, 1)) * chart_w
                y = pad + chart_h - ((v - min_val) / val_range) * chart_h
                points.append((x, y))

            path = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
                            for i, (x, y) in enumerate(points))

            if variant == "area" and points:
                area_path = (
                    path
                    + f" L{points[-1][0]:.1f},{pad + chart_h:.1f}"
                    + f" L{points[0][0]:.1f},{pad + chart_h:.1f} Z"
                )
                fill = f' fill="{e_color}"' if e_color else ""
                parts.append(
                    f'<path class="dj-sparkline__area" d="{area_path}"{fill} opacity="0.2"/>'
                )

            stroke = f' stroke="{e_color}"' if e_color else ""
            parts.append(
                f'<path class="dj-sparkline__line" d="{path}" '
                f'fill="none"{stroke} stroke-width="{stroke_width}"/>'
            )

        parts.append("</svg>")
        return mark_safe(f'<span class="{class_str}">{"".join(parts)}</span>')


@register.tag("sparkline")
def do_sparkline(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return SparklineNode(kwargs)


# ---------------------------------------------------------------------------
# Heatmap
# ---------------------------------------------------------------------------

class HeatmapNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    @staticmethod
    def _interpolate_color(c1, c2, t):
        def parse_hex(c):
            c = c.lstrip("#")
            if len(c) == 3:
                c = c[0]*2 + c[1]*2 + c[2]*2
            return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        r1, g1, b1 = parse_hex(c1)
        r2, g2, b2 = parse_hex(c2)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        data = kw.get("data", [])
        x_labels = kw.get("x_labels", [])
        y_labels = kw.get("y_labels", [])
        title = kw.get("title", "")
        color_min = kw.get("color_min", "#f0f9ff")
        color_max = kw.get("color_max", "#1e40af")
        cell_size = kw.get("cell_size", 36)
        show_values = kw.get("show_values", True)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))
        classes = ["dj-heatmap"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(data, list):
            data = []
        if not isinstance(x_labels, list):
            x_labels = []
        if not isinstance(y_labels, list):
            y_labels = []

        try:
            cell_size = int(cell_size)
        except (ValueError, TypeError):
            cell_size = 36

        if not data:
            return mark_safe(f'<div class="{class_str}"><svg></svg></div>')

        cs = cell_size
        rows = len(data)
        cols = max((len(row) for row in data if isinstance(row, list)), default=0)
        if cols == 0:
            return mark_safe(f'<div class="{class_str}"><svg></svg></div>')

        label_left = 60 if y_labels else 0
        label_top = 20 if x_labels else 0
        title_h = 24 if title else 0
        w = label_left + cols * cs + 4
        h = title_h + label_top + rows * cs + 4

        all_vals = []
        for row in data:
            if not isinstance(row, list):
                continue
            for v in row:
                try:
                    all_vals.append(float(v))
                except (ValueError, TypeError):
                    pass
        min_v = min(all_vals) if all_vals else 0
        max_v = max(all_vals) if all_vals else 1
        val_range = max_v - min_v if max_v != min_v else 1

        e_title = conditional_escape(str(title)) if title else "Heatmap"
        parts = [f'<svg class="dj-heatmap__svg" viewBox="0 0 {w} {h}" '
                 f'width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" '
                 f'role="img" aria-label="{e_title}">']

        if title:
            parts.append(
                f'<text class="dj-heatmap__title" x="{w / 2}" y="16" '
                f'text-anchor="middle" font-size="13" font-weight="600">'
                f'{conditional_escape(str(title))}</text>'
            )

        for ci, lbl in enumerate(x_labels[:cols]):
            x = label_left + ci * cs + cs / 2
            y = title_h + label_top - 4
            parts.append(
                f'<text class="dj-heatmap__xlabel" x="{x:.1f}" y="{y:.1f}" '
                f'text-anchor="middle" font-size="10">'
                f'{conditional_escape(str(lbl))}</text>'
            )

        for ri, lbl in enumerate(y_labels[:rows]):
            x = label_left - 4
            y = title_h + label_top + ri * cs + cs / 2
            parts.append(
                f'<text class="dj-heatmap__ylabel" x="{x:.1f}" y="{y:.1f}" '
                f'text-anchor="end" dominant-baseline="central" font-size="10">'
                f'{conditional_escape(str(lbl))}</text>'
            )

        for ri, row in enumerate(data):
            if not isinstance(row, list):
                continue
            for ci, v in enumerate(row):
                try:
                    val = float(v)
                except (ValueError, TypeError):
                    val = 0
                t = (val - min_v) / val_range
                color = self._interpolate_color(color_min, color_max, t)
                x = label_left + ci * cs
                y_pos = title_h + label_top + ri * cs

                parts.append(
                    f'<rect class="dj-heatmap__cell" x="{x}" y="{y_pos}" '
                    f'width="{cs}" height="{cs}" fill="{color}" stroke="#fff" stroke-width="1">'
                    f'<title>{val:g}</title></rect>'
                )

                if show_values:
                    text_color = "#fff" if t > 0.5 else "#1e293b"
                    parts.append(
                        f'<text class="dj-heatmap__value" x="{x + cs / 2:.1f}" '
                        f'y="{y_pos + cs / 2:.1f}" text-anchor="middle" '
                        f'dominant-baseline="central" font-size="10" fill="{text_color}">'
                        f'{val:g}</text>'
                    )

        parts.append("</svg>")
        return mark_safe(f'<div class="{class_str}">{"".join(parts)}</div>')


@register.tag("heatmap")
def do_heatmap(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return HeatmapNode(kwargs)


# ---------------------------------------------------------------------------
# Treemap
# ---------------------------------------------------------------------------

class TreemapNode(template.Node):
    COLORS = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#8b5cf6",
              "#06b6d4", "#ec4899", "#f97316", "#14b8a6", "#a855f7"]

    def __init__(self, kwargs):
        self.kwargs = kwargs

    @staticmethod
    def _squarify(items, x, y, w, h):
        rects = []
        if not items or w <= 0 or h <= 0:
            return rects
        total = sum(v for _, v, _ in items)
        if total <= 0:
            return rects
        if w >= h:
            cx = x
            for label, val, idx in items:
                frac = val / total
                rw = w * frac
                rects.append((cx, y, rw, h, label, val, idx))
                cx += rw
        else:
            cy = y
            for label, val, idx in items:
                frac = val / total
                rh = h * frac
                rects.append((x, cy, w, rh, label, val, idx))
                cy += rh
        return rects

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        data = kw.get("data", [])
        value_key = kw.get("value_key", "size")
        label_key = kw.get("label_key", "name")
        title = kw.get("title", "")
        width = kw.get("width", 400)
        height = kw.get("height", 250)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))
        classes = ["dj-treemap"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(data, list):
            data = []

        try:
            width = int(width)
        except (ValueError, TypeError):
            width = 400
        try:
            height = int(height)
        except (ValueError, TypeError):
            height = 250

        if not data:
            return mark_safe(f'<div class="{class_str}"><svg></svg></div>')

        w, h = width, height
        title_h = 24 if title else 0
        chart_h = h - title_h

        items = []
        for i, d in enumerate(data):
            if not isinstance(d, dict):
                continue
            try:
                val = float(d.get(value_key, 0))
            except (ValueError, TypeError):
                val = 0
            if val > 0:
                label = str(d.get(label_key, ""))
                items.append((label, val, i))

        items.sort(key=lambda x: x[1], reverse=True)
        rects = self._squarify(items, 0, title_h, w, chart_h)

        e_title = conditional_escape(str(title)) if title else "Treemap"
        parts = [f'<svg class="dj-treemap__svg" viewBox="0 0 {w} {h}" '
                 f'width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" '
                 f'role="img" aria-label="{e_title}">']

        if title:
            parts.append(
                f'<text class="dj-treemap__title" x="{w / 2}" y="16" '
                f'text-anchor="middle" font-size="13" font-weight="600">'
                f'{conditional_escape(str(title))}</text>'
            )

        for rx, ry, rw, rh, label, val, idx in rects:
            color = conditional_escape(str(self.COLORS[idx % len(self.COLORS)]))
            e_label = conditional_escape(label)
            parts.append(
                f'<rect class="dj-treemap__cell" x="{rx:.1f}" y="{ry:.1f}" '
                f'width="{rw:.1f}" height="{rh:.1f}" fill="{color}" '
                f'stroke="#fff" stroke-width="2">'
                f'<title>{e_label}: {val:g}</title></rect>'
            )
            if rw > 30 and rh > 20:
                parts.append(
                    f'<text class="dj-treemap__label" '
                    f'x="{rx + rw / 2:.1f}" y="{ry + rh / 2:.1f}" '
                    f'text-anchor="middle" dominant-baseline="central" '
                    f'font-size="{min(11, rw / max(len(label), 1) * 1.2):.0f}" '
                    f'fill="#fff" font-weight="600">{e_label}</text>'
                )

        parts.append("</svg>")
        return mark_safe(f'<div class="{class_str}">{"".join(parts)}</div>')


@register.tag("treemap")
def do_treemap(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return TreemapNode(kwargs)


# ---------------------------------------------------------------------------
# Calendar Heatmap
# ---------------------------------------------------------------------------

from datetime import date as _date, timedelta as _timedelta

class CalendarHeatmapNode(template.Node):
    LEVELS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def _get_color(self, value, max_val):
        if value <= 0:
            return self.LEVELS[0]
        if max_val <= 0:
            return self.LEVELS[0]
        ratio = value / max_val
        if ratio <= 0.25:
            return self.LEVELS[1]
        elif ratio <= 0.5:
            return self.LEVELS[2]
        elif ratio <= 0.75:
            return self.LEVELS[3]
        else:
            return self.LEVELS[4]

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        data = kw.get("data", {})
        year = kw.get("year", _date.today().year)
        title = kw.get("title", "")
        cell_size = kw.get("cell_size", 12)
        cell_gap = kw.get("cell_gap", 2)
        show_month_labels = kw.get("show_month_labels", True)
        show_day_labels = kw.get("show_day_labels", True)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))
        classes = ["dj-calendar-heatmap"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(data, dict):
            data = {}

        try:
            year = int(year)
        except (ValueError, TypeError):
            year = _date.today().year
        try:
            cell_size = int(cell_size)
        except (ValueError, TypeError):
            cell_size = 12
        try:
            cell_gap = int(cell_gap)
        except (ValueError, TypeError):
            cell_gap = 2

        cs = cell_size
        cg = cell_gap
        step = cs + cg

        start = _date(year, 1, 1)
        end = _date(year, 12, 31)

        vals = []
        for v in data.values():
            try:
                vals.append(float(v))
            except (ValueError, TypeError):
                pass
        max_val = max(vals) if vals else 1

        label_left = 30 if show_day_labels else 0
        label_top = 16 if show_month_labels else 0
        title_h = 22 if title else 0

        first_dow = start.weekday()
        num_days = (end - start).days + 1
        num_weeks = ((first_dow + num_days - 1) // 7) + 1

        w = label_left + num_weeks * step + 4
        h = title_h + label_top + 7 * step + 4

        e_title = conditional_escape(str(title)) if title else f"{year} activity"
        parts = [f'<svg class="dj-calendar-heatmap__svg" viewBox="0 0 {w} {h}" '
                 f'width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" '
                 f'role="img" aria-label="{e_title}">']

        if title:
            parts.append(
                f'<text class="dj-calendar-heatmap__title" x="{w / 2}" y="16" '
                f'text-anchor="middle" font-size="13" font-weight="600">'
                f'{conditional_escape(str(title))}</text>'
            )

        if show_day_labels:
            day_names = ["Mon", "", "Wed", "", "Fri", "", ""]
            for di, name in enumerate(day_names):
                if name:
                    y = title_h + label_top + di * step + cs / 2
                    parts.append(
                        f'<text class="dj-calendar-heatmap__day-label" x="{label_left - 4}" '
                        f'y="{y:.1f}" text-anchor="end" dominant-baseline="central" '
                        f'font-size="9">{name}</text>'
                    )

        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_positions = {}

        current = start
        while current <= end:
            day_of_year = (current - start).days
            dow = current.weekday()
            week = (first_dow + day_of_year) // 7

            x = label_left + week * step
            y = title_h + label_top + dow * step

            date_str = current.isoformat()
            try:
                val = float(data.get(date_str, 0))
            except (ValueError, TypeError):
                val = 0
            color = self._get_color(val, max_val)

            parts.append(
                f'<rect class="dj-calendar-heatmap__cell" x="{x}" y="{y}" '
                f'width="{cs}" height="{cs}" rx="2" fill="{color}">'
                f'<title>{date_str}: {val:g}</title></rect>'
            )

            if current.day == 1:
                month_positions[current.month] = x

            current += _timedelta(days=1)

        if show_month_labels:
            for month, mx in month_positions.items():
                parts.append(
                    f'<text class="dj-calendar-heatmap__month-label" '
                    f'x="{mx}" y="{title_h + label_top - 4}" '
                    f'font-size="9">{month_names[month - 1]}</text>'
                )

        parts.append("</svg>")
        return mark_safe(f'<div class="{class_str}">{"".join(parts)}</div>')


@register.tag("calendar_heatmap")
def do_calendar_heatmap(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return CalendarHeatmapNode(kwargs)


# ---------------------------------------------------------------------------
# Terminal
# ---------------------------------------------------------------------------

import re as _re

class TerminalNode(template.Node):
    ANSI_RE = _re.compile(r'\033\[([0-9;]*)m')
    ANSI_COLORS = {
        '30': '#000', '31': '#e74c3c', '32': '#2ecc71', '33': '#f1c40f',
        '34': '#3498db', '35': '#9b59b6', '36': '#1abc9c', '37': '#ecf0f1',
        '90': '#7f8c8d', '91': '#ff6b6b', '92': '#55efc4', '93': '#ffeaa7',
        '94': '#74b9ff', '95': '#a29bfe', '96': '#81ecec', '97': '#fff',
    }

    def __init__(self, kwargs):
        self.kwargs = kwargs

    @classmethod
    def _ansi_to_html(cls, text):
        from django.utils.html import escape
        result = []
        open_spans = 0
        last_end = 0
        for m in cls.ANSI_RE.finditer(text):
            start, end = m.span()
            result.append(conditional_escape(text[last_end:start]))
            last_end = end
            codes = m.group(1).split(';')
            for code in codes:
                if code == '0' or code == '':
                    result.append('</span>' * open_spans)
                    open_spans = 0
                elif code == '1':
                    result.append('<span style="font-weight:bold">')
                    open_spans += 1
                elif code in cls.ANSI_COLORS:
                    color = cls.ANSI_COLORS[code]
                    result.append(f'<span style="color:{color}">')
                    open_spans += 1
        result.append(conditional_escape(text[last_end:]))
        result.append('</span>' * open_spans)
        return ''.join(result)

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        output = kw.get("output", [])
        title = kw.get("title", "")
        stream_event = kw.get("stream_event", "")
        show_line_numbers = kw.get("show_line_numbers", False)
        wrap = kw.get("wrap", False)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))

        classes = ["dj-terminal"]
        if wrap:
            classes.append("dj-terminal--wrap")
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(output, list):
            output = []

        title_html = ""
        if title:
            e_title = conditional_escape(str(title))
            title_html = (
                f'<div class="dj-terminal__titlebar">'
                f'<span class="dj-terminal__title">{e_title}</span>'
                f'<span class="dj-terminal__dots">'
                f'<span class="dj-terminal__dot dj-terminal__dot--red"></span>'
                f'<span class="dj-terminal__dot dj-terminal__dot--yellow"></span>'
                f'<span class="dj-terminal__dot dj-terminal__dot--green"></span>'
                f'</span></div>'
            )

        lines_html = []
        for i, line in enumerate(output):
            line_text = self._ansi_to_html(str(line))
            num_html = ""
            if show_line_numbers:
                num_html = f'<span class="dj-terminal__line-num">{i + 1}</span>'
            lines_html.append(
                f'<div class="dj-terminal__line">{num_html}'
                f'<span class="dj-terminal__text">{line_text}</span></div>'
            )

        stream_attr = ""
        if stream_event:
            e_stream = conditional_escape(str(stream_event))
            stream_attr = f' data-stream-event="{e_stream}"'

        return mark_safe(
            f'<div class="{class_str}" dj-hook="Terminal"{stream_attr}>'
            f'{title_html}'
            f'<div class="dj-terminal__body">{"".join(lines_html)}</div>'
            f'</div>'
        )


@register.tag("terminal")
def do_terminal(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return TerminalNode(kwargs)


# ---------------------------------------------------------------------------
# Markdown Editor
# ---------------------------------------------------------------------------

class MarkdownEditorNode(template.Node):
    TOOLBAR_BUTTONS = [
        ("bold", "B", "**", "**"),
        ("italic", "I", "_", "_"),
        ("code", "&lt;/&gt;", "`", "`"),
        ("link", "Link", "[", "](url)"),
        ("heading", "H", "## ", ""),
    ]

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        name = kw.get("name", "content")
        value = kw.get("value", "")
        preview = kw.get("preview", True)
        toolbar = kw.get("toolbar", True)
        placeholder = kw.get("placeholder", "Write markdown...")
        rows = kw.get("rows", 12)
        disabled = kw.get("disabled", False)
        event = kw.get("event", "")
        custom_class = kw.get("class", "")

        e_name = conditional_escape(str(name))
        e_value = conditional_escape(str(value))
        e_placeholder = conditional_escape(str(placeholder))
        e_class = conditional_escape(str(custom_class))

        try:
            rows = int(rows)
        except (ValueError, TypeError):
            rows = 12

        classes = ["dj-md-editor"]
        if preview:
            classes.append("dj-md-editor--split")
        if disabled:
            classes.append("dj-md-editor--disabled")
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        disabled_attr = ' disabled' if disabled else ""
        event_attr = ""
        if event:
            e_event = conditional_escape(str(event))
            event_attr = f' dj-input="{e_event}"'

        toolbar_html = ""
        if toolbar:
            btns = []
            for btn_id, label, prefix, suffix in self.TOOLBAR_BUTTONS:
                btns.append(
                    f'<button type="button" class="dj-md-editor__btn" '
                    f'data-action="{btn_id}" data-prefix="{conditional_escape(prefix)}" '
                    f'data-suffix="{conditional_escape(suffix)}" '
                    f'aria-label="{btn_id.title()}">{label}</button>'
                )
            toolbar_html = (
                f'<div class="dj-md-editor__toolbar">{"".join(btns)}</div>'
            )

        textarea_html = (
            f'<textarea class="dj-md-editor__textarea" name="{e_name}" '
            f'placeholder="{e_placeholder}" rows="{rows}"'
            f'{disabled_attr}{event_attr}>{e_value}</textarea>'
        )

        preview_html = ""
        if preview:
            preview_html = (
                f'<div class="dj-md-editor__preview" '
                f'aria-label="Preview"></div>'
            )

        panes = f'<div class="dj-md-editor__panes">{textarea_html}{preview_html}</div>'

        return mark_safe(
            f'<div class="{class_str}" dj-hook="MarkdownEditor">'
            f'{toolbar_html}{panes}</div>'
        )


@register.tag("markdown_editor")
def do_markdown_editor(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return MarkdownEditorNode(kwargs)


# ---------------------------------------------------------------------------
# JSON Viewer
# ---------------------------------------------------------------------------

import json as _json

class JsonViewerNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def _render_node(self, value, depth, collapsed_depth):
        collapsed = depth >= collapsed_depth

        if isinstance(value, dict):
            if not value:
                return '<span class="dj-json__bracket">{}</span>'
            collapse_cls = " dj-json__node--collapsed" if collapsed else ""
            toggle = (
                f'<span class="dj-json__toggle" role="button" tabindex="0" '
                f'aria-expanded="{"false" if collapsed else "true"}">'
                f'{"&#9654;" if collapsed else "&#9660;"}</span>'
            )
            items = []
            for k, v in value.items():
                e_key = conditional_escape(str(k))
                items.append(
                    f'<div class="dj-json__pair">'
                    f'<span class="dj-json__key">"{e_key}"</span>'
                    f'<span class="dj-json__colon">: </span>'
                    f'{self._render_node(v, depth + 1, collapsed_depth)}</div>'
                )
            count = f' <span class="dj-json__count">({len(value)} keys)</span>' if collapsed else ""
            return (
                f'<div class="dj-json__node dj-json__node--object{collapse_cls}">'
                f'{toggle}'
                f'<span class="dj-json__bracket">{{</span>{count}'
                f'<div class="dj-json__children">{"".join(items)}</div>'
                f'<span class="dj-json__bracket">}}</span></div>'
            )

        if isinstance(value, list):
            if not value:
                return '<span class="dj-json__bracket">[]</span>'
            collapse_cls = " dj-json__node--collapsed" if collapsed else ""
            toggle = (
                f'<span class="dj-json__toggle" role="button" tabindex="0" '
                f'aria-expanded="{"false" if collapsed else "true"}">'
                f'{"&#9654;" if collapsed else "&#9660;"}</span>'
            )
            items = []
            for i, v in enumerate(value):
                items.append(
                    f'<div class="dj-json__item">'
                    f'{self._render_node(v, depth + 1, collapsed_depth)}'
                    f'{"," if i < len(value) - 1 else ""}</div>'
                )
            count = f' <span class="dj-json__count">({len(value)} items)</span>' if collapsed else ""
            return (
                f'<div class="dj-json__node dj-json__node--array{collapse_cls}">'
                f'{toggle}'
                f'<span class="dj-json__bracket">[</span>{count}'
                f'<div class="dj-json__children">{"".join(items)}</div>'
                f'<span class="dj-json__bracket">]</span></div>'
            )

        if isinstance(value, str):
            return f'<span class="dj-json__value dj-json__value--string">"{conditional_escape(value)}"</span>'
        if isinstance(value, bool):
            return f'<span class="dj-json__value dj-json__value--bool">{"true" if value else "false"}</span>'
        if isinstance(value, (int, float)):
            return f'<span class="dj-json__value dj-json__value--number">{value}</span>'
        if value is None:
            return '<span class="dj-json__value dj-json__value--null">null</span>'

        return f'<span class="dj-json__value">{conditional_escape(str(value))}</span>'

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        data = kw.get("data", None)
        collapsed_depth = kw.get("collapsed_depth", 2)
        root_label = kw.get("root_label", "root")
        copy_button = kw.get("copy_button", True)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))
        e_label = conditional_escape(str(root_label))

        try:
            collapsed_depth = int(collapsed_depth)
        except (ValueError, TypeError):
            collapsed_depth = 2

        classes = ["dj-json-viewer"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        copy_html = ""
        if copy_button:
            copy_html = (
                '<button class="dj-json-viewer__copy" type="button" '
                'aria-label="Copy JSON">Copy</button>'
            )

        try:
            raw_json = _json.dumps(data, indent=2, default=str)
        except (TypeError, ValueError):
            raw_json = str(data)

        tree_html = self._render_node(data, 0, collapsed_depth)

        return mark_safe(
            f'<div class="{class_str}" dj-hook="JsonViewer" '
            f'data-collapsed-depth="{collapsed_depth}">'
            f'<div class="dj-json-viewer__header">'
            f'<span class="dj-json-viewer__label">{e_label}</span>'
            f'{copy_html}</div>'
            f'<div class="dj-json-viewer__tree">{tree_html}</div>'
            f'<script type="application/json" class="dj-json-viewer__raw">'
            f'{conditional_escape(raw_json)}</script>'
            f'</div>'
        )


@register.tag("json_viewer")
def do_json_viewer(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return JsonViewerNode(kwargs)


# ---------------------------------------------------------------------------
# Log Viewer
# ---------------------------------------------------------------------------

class LogViewerNode(template.Node):
    LEVEL_RE = _re.compile(r'\b(INFO|WARN(?:ING)?|ERROR|DEBUG|TRACE|FATAL|CRITICAL)\b', _re.IGNORECASE)

    def __init__(self, kwargs):
        self.kwargs = kwargs

    @classmethod
    def _detect_level(cls, line):
        m = cls.LEVEL_RE.search(line)
        if m:
            level = m.group(1).upper()
            if level in ('WARN', 'WARNING'):
                return 'warn'
            if level in ('ERROR', 'FATAL', 'CRITICAL'):
                return 'error'
            if level in ('DEBUG', 'TRACE'):
                return 'debug'
            return 'info'
        return ''

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        lines = kw.get("lines", [])
        stream_event = kw.get("stream_event", "")
        show_line_numbers = kw.get("show_line_numbers", True)
        auto_scroll = kw.get("auto_scroll", True)
        filter_level = kw.get("filter_level", "")
        wrap = kw.get("wrap", False)
        max_lines = kw.get("max_lines", 0)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))

        classes = ["dj-log-viewer"]
        if wrap:
            classes.append("dj-log-viewer--wrap")
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(lines, list):
            lines = []

        try:
            max_lines = int(max_lines)
        except (ValueError, TypeError):
            max_lines = 0

        display_lines = lines
        if max_lines and max_lines > 0:
            display_lines = display_lines[-max_lines:]

        lines_html = []
        for i, line in enumerate(display_lines):
            line_str = str(line)
            level = self._detect_level(line_str)
            e_line = conditional_escape(line_str)

            if filter_level and level != str(filter_level).lower():
                continue

            level_cls = f" dj-log-viewer__line--{level}" if level else ""
            num_html = ""
            if show_line_numbers:
                num_html = f'<span class="dj-log-viewer__num">{i + 1}</span>'
            lines_html.append(
                f'<div class="dj-log-viewer__line{level_cls}">'
                f'{num_html}<span class="dj-log-viewer__text">{e_line}</span></div>'
            )

        stream_attr = ""
        if stream_event:
            e_stream = conditional_escape(str(stream_event))
            stream_attr = f' data-stream-event="{e_stream}"'

        scroll_attr = ' data-auto-scroll="true"' if auto_scroll else ""

        return mark_safe(
            f'<div class="{class_str}" dj-hook="LogViewer"'
            f'{stream_attr}{scroll_attr} role="log" aria-live="polite">'
            f'<div class="dj-log-viewer__body">{"".join(lines_html)}</div>'
            f'</div>'
        )


@register.tag("log_viewer")
def do_log_viewer(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return LogViewerNode(kwargs)


# ---------------------------------------------------------------------------
# File Tree
# ---------------------------------------------------------------------------

class FileTreeNode(template.Node):
    FOLDER_ICON = '&#x1F4C1;'
    FOLDER_OPEN_ICON = '&#x1F4C2;'
    DEFAULT_FILE_ICON = '&#x1F4C4;'

    def __init__(self, kwargs):
        self.kwargs = kwargs

    def _render_tree_node(self, node, depth, event, show_icons, selected):
        if not isinstance(node, dict):
            return ""

        name = str(node.get("name", ""))
        node_type = str(node.get("type", "file"))
        children = node.get("children", [])
        expanded = node.get("expanded", True)
        e_name = conditional_escape(name)
        e_type = conditional_escape(node_type)

        is_selected = (name == selected)
        selected_cls = " dj-file-tree__node--selected" if is_selected else ""
        type_cls = f" dj-file-tree__node--{e_type}"

        icon_html = ""
        if show_icons:
            if node_type == 'folder':
                icon = self.FOLDER_OPEN_ICON if expanded else self.FOLDER_ICON
            else:
                icon = self.DEFAULT_FILE_ICON
            icon_html = f'<span class="dj-file-tree__icon" aria-hidden="true">{icon}</span>'

        indent_style = f' style="padding-left:{depth * 1.25}rem"'
        e_event = conditional_escape(str(event))

        if node_type == 'folder' and isinstance(children, list) and children:
            expand_cls = " dj-file-tree__node--expanded" if expanded else ""
            toggle = (
                f'<span class="dj-file-tree__toggle" role="button" tabindex="0" '
                f'aria-expanded="{"true" if expanded else "false"}">'
                f'{"&#9660;" if expanded else "&#9654;"}</span>'
            )
            children_html = []
            for child in children:
                children_html.append(
                    self._render_tree_node(child, depth + 1, event, show_icons, selected)
                )
            child_display = ' style="display:none"' if not expanded else ""
            return (
                f'<div class="dj-file-tree__node{type_cls}{selected_cls}{expand_cls}"'
                f'{indent_style} data-name="{e_name}" data-type="{e_type}">'
                f'{toggle}{icon_html}'
                f'<span class="dj-file-tree__name">{e_name}</span></div>'
                f'<div class="dj-file-tree__children"{child_display}>'
                f'{"".join(children_html)}</div>'
            )

        return (
            f'<div class="dj-file-tree__node{type_cls}{selected_cls}"'
            f'{indent_style} data-name="{e_name}" data-type="{e_type}" '
            f'dj-click="{e_event}" role="treeitem" tabindex="0">'
            f'{icon_html}<span class="dj-file-tree__name">{e_name}</span></div>'
        )

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        nodes = kw.get("nodes", [])
        selected = kw.get("selected", "")
        event = kw.get("event", "select_file")
        show_icons = kw.get("show_icons", True)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))
        e_event = conditional_escape(str(event))
        e_selected = conditional_escape(str(selected))

        classes = ["dj-file-tree"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(nodes, list):
            nodes = []

        nodes_html = []
        for node in nodes:
            nodes_html.append(
                self._render_tree_node(node, 0, event, show_icons, str(selected))
            )

        return mark_safe(
            f'<div class="{class_str}" dj-hook="FileTree" '
            f'data-event="{e_event}" data-selected="{e_selected}" '
            f'role="tree">{"".join(nodes_html)}</div>'
        )


@register.tag("file_tree")
def do_file_tree(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return FileTreeNode(kwargs)


# ---------------------------------------------------------------------------
# Tour / Onboarding Guide
# ---------------------------------------------------------------------------

class TourNode(template.Node):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def render(self, context):
        kw = {k: _resolve(v, context) for k, v in self.kwargs.items()}
        steps = kw.get("steps", [])
        active = kw.get("active", 0)
        event = kw.get("event", "tour")
        show_progress = kw.get("show_progress", True)
        show_skip = kw.get("show_skip", True)
        custom_class = kw.get("class", "")

        e_class = conditional_escape(str(custom_class))

        classes = ["dj-tour"]
        if e_class:
            classes.append(e_class)
        class_str = " ".join(classes)

        if not isinstance(steps, list) or not steps:
            return ""

        try:
            idx = int(active)
        except (ValueError, TypeError):
            idx = 0
        total = len(steps)
        idx = max(0, min(idx, total - 1))

        step = steps[idx]
        if not isinstance(step, dict):
            return ""

        e_event = conditional_escape(str(event))
        e_target = conditional_escape(str(step.get("target", "")))
        e_title = conditional_escape(str(step.get("title", "")))
        e_content = conditional_escape(str(step.get("content", "")))

        progress_html = ""
        if show_progress:
            dots = []
            for i in range(total):
                dot_cls = "dj-tour__dot"
                if i == idx:
                    dot_cls += " dj-tour__dot--active"
                elif i < idx:
                    dot_cls += " dj-tour__dot--completed"
                dots.append(f'<span class="{dot_cls}"></span>')
            progress_html = (
                f'<div class="dj-tour__progress">{"".join(dots)}</div>'
            )

        prev_btn = ""
        if idx > 0:
            prev_btn = (
                f'<button class="dj-tour__prev" type="button" '
                f'dj-click="{e_event}" data-value="prev">Back</button>'
            )

        next_label = "Finish" if idx == total - 1 else "Next"
        next_action = "finish" if idx == total - 1 else "next"
        next_btn = (
            f'<button class="dj-tour__next" type="button" '
            f'dj-click="{e_event}" data-value="{next_action}">{next_label}</button>'
        )

        skip_btn = ""
        if show_skip and idx < total - 1:
            skip_btn = (
                f'<button class="dj-tour__skip" type="button" '
                f'dj-click="{e_event}" data-value="skip">Skip tour</button>'
            )

        step_label = f'<span class="dj-tour__step-label">Step {idx + 1} of {total}</span>'

        return mark_safe(
            f'<div class="{class_str}" dj-hook="Tour" '
            f'data-target="{e_target}" data-step="{idx}" '
            f'data-total="{total}" data-event="{e_event}" role="dialog" aria-modal="true">'
            f'<div class="dj-tour__overlay"></div>'
            f'<div class="dj-tour__popover">'
            f'<div class="dj-tour__header">'
            f'<h4 class="dj-tour__title">{e_title}</h4>'
            f'{step_label}</div>'
            f'<div class="dj-tour__body">'
            f'<p class="dj-tour__content">{e_content}</p></div>'
            f'{progress_html}'
            f'<div class="dj-tour__footer">'
            f'{skip_btn}{prev_btn}{next_btn}</div></div></div>'
        )


@register.tag("tour")
def do_tour(parser, token):
    bits = token.split_contents()[1:]
    kwargs = _parse_kv_args(bits, parser)
    return TourNode(kwargs)
