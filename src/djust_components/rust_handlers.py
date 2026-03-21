"""
Rust template engine handlers for djust-components.

Registers all component tags with the Rust tag handler registry so that
{% modal %}, {% alert %}, {% dj_button %}, etc. work in djust-templating
Rust-rendered templates — no {% load djust_components %} needed.

Inline handlers implement: render(self, args, context) -> str
Block handlers implement:  render(self, args, content, context) -> str
"""

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_args(args, context):
    """Parse handler arg list ["key='val'", "key2=var"] into a dict.

    Resolves variable references against the template context dict.
    Values that are JSON-encoded lists/objects (from the Rust engine's
    variable resolution) are deserialized automatically.
    """
    import json as _json

    result = {}
    for arg in args:
        if "=" not in arg:
            continue
        key, val = arg.split("=", 1)
        key = key.strip()
        val = val.strip()
        # String literal — strip quotes
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            result[key] = val[1:-1]
        # JSON array or object (from Rust variable resolution)
        elif (val.startswith("[") and val.endswith("]")) or (
            val.startswith("{") and val.endswith("}")
        ):
            try:
                result[key] = _json.loads(val)
            except (ValueError, TypeError):
                result[key] = context.get(val, val)
        # Boolean
        elif val in ("True", "true", "1"):
            result[key] = True
        elif val in ("False", "false", "0", ""):
            result[key] = False
        # None
        elif val in ("None", "null"):
            result[key] = None
        else:
            # Variable reference — look up in context
            result[key] = context.get(val, val)
    return result


# ---------------------------------------------------------------------------
# Block handlers (wrap content — e.g. {% modal %}...{% endmodal %})
# ---------------------------------------------------------------------------


class ModalHandler:
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        is_open = kw.get("open", False)
        if not is_open:
            return ""
        title = conditional_escape(kw.get("title", ""))
        size = kw.get("size", "md")
        close_event = conditional_escape(kw.get("close_event", "close_modal"))
        size_class = {
            "sm": "modal-sm", "md": "modal-md",
            "lg": "modal-lg", "xl": "modal-xl",
        }.get(str(size), "modal-md")
        return mark_safe(
            f'<div class="modal-overlay {size_class}" dj-click="{close_event}">'
            f'<div class="modal-content" onclick="event.stopPropagation()">'
            f'<div class="modal-header">'
            f'<h3 class="modal-title">{title}</h3>'
            f'<button class="modal-close" dj-click="{close_event}">&times;</button>'
            f"</div>"
            f'<div class="modal-body">{content}</div>'
            f"</div>"
            f"</div>"
        )


class CardHandler:
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        title = kw.get("title", "")
        subtitle = kw.get("subtitle", "")
        variant = conditional_escape(kw.get("variant", "default"))
        extra_class = conditional_escape(kw.get("class", ""))
        header = ""
        if title:
            sub = (
                f'<p class="card-subtitle">{conditional_escape(subtitle)}</p>'
                if subtitle
                else ""
            )
            header = (
                f'<div class="card-header">'
                f'<h3 class="card-title">{conditional_escape(title)}</h3>{sub}'
                f"</div>"
            )
        return mark_safe(
            f'<div class="card card-{variant} {extra_class}">'
            f"{header}"
            f'<div class="card-body">{content}</div>'
            f"</div>"
        )


class TabsHandler:
    def render(self, args, content, context):
        # Tabs need active state from args to render nav — content already rendered
        kw = _parse_args(args, context)
        tabs_id = conditional_escape(kw.get("id", "tabs"))
        # For block-handler mode, the nav is built from child content rendered as panes.
        # We wrap in the tabs container; view logic controls active tab.
        return mark_safe(
            f'<div class="tabs-container" id="{tabs_id}">{content}</div>'
        )


class AccordionHandler:
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        accordion_id = conditional_escape(kw.get("id", "accordion"))
        return mark_safe(
            f'<div class="accordion" id="{accordion_id}">{content}</div>'
        )


class AccordionItemHandler:
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        title = conditional_escape(kw.get("title", ""))
        item_id = conditional_escape(kw.get("id", ""))
        event = conditional_escape(kw.get("event", "accordion_toggle"))
        is_open = kw.get("open", False)
        open_cls = "accordion-item--open" if is_open else ""
        expanded = "true" if is_open else "false"
        panel_hidden = "" if is_open else ' hidden'
        return mark_safe(
            f'<div class="accordion-item {open_cls}">'
            f'<button class="accordion-trigger" aria-expanded="{expanded}" '
            f'dj-click="{event}" data-value="{item_id}">'
            f'<span class="accordion-title">{title}</span>'
            f'<svg class="accordion-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
            f'<polyline points="6 9 12 15 18 9"></polyline></svg>'
            f"</button>"
            f'<div class="accordion-panel"{panel_hidden}>{content}</div>'
            f"</div>"
        )


class DropdownHandler:
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        dropdown_id = conditional_escape(kw.get("id", "dropdown"))
        label = conditional_escape(kw.get("label", "Menu"))
        is_open = kw.get("open", False)
        toggle_event = conditional_escape(kw.get("toggle_event", "toggle_dropdown"))
        open_data = "true" if is_open else "false"
        return mark_safe(
            f'<div class="dropdown" id="{dropdown_id}">'
            f'<button class="dropdown-trigger" dj-click="{toggle_event}">{label}</button>'
            f'<div class="dropdown-menu" data-open="{open_data}">{content}</div>'
            f"</div>"
        )


class AlertHandler:
    _icons = {
        "info": "ℹ",
        "success": "✓",
        "warning": "⚠",
        "error": "✕",
        "danger": "✕",
    }

    def render(self, args, content, context):
        kw = _parse_args(args, context)
        alert_type = kw.get("type", "info")
        if alert_type == "danger":
            alert_type = "error"
        title = conditional_escape(kw.get("title", ""))
        dismissible = kw.get("dismissible", False)
        event = conditional_escape(kw.get("event", "dismiss_alert"))
        icon_char = self._icons.get(str(alert_type), "ℹ")
        title_html = f'<div class="alert-title">{title}</div>' if title else ""
        close_html = (
            f'<button class="alert-close" dj-click="{event}">&times;</button>'
            if dismissible
            else ""
        )
        return mark_safe(
            f'<div class="alert alert-{conditional_escape(alert_type)}'
            f'{"  alert-dismissible" if dismissible else ""}">'
            f'<span class="alert-icon">{icon_char}</span>'
            f'<div class="alert-body">{title_html}'
            f'<div class="alert-message">{content}</div>'
            f"</div>"
            f"{close_html}"
            f"</div>"
        )


class FormGroupHandler:
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        label = conditional_escape(kw.get("label", ""))
        error = conditional_escape(kw.get("error", ""))
        helper = conditional_escape(kw.get("helper", ""))
        required = kw.get("required", False)
        for_input = conditional_escape(kw.get("for_input", ""))
        required_span = '<span class="form-label-required">*</span>' if required else ""
        label_html = (
            f'<label class="form-label" for="{for_input}">{label}{required_span}</label>'
            if label
            else ""
        )
        error_html = (
            f'<div class="form-error-message">{error}</div>' if error else ""
        )
        helper_html = (
            f'<div class="form-helper">{helper}</div>' if helper else ""
        )
        return mark_safe(
            f'<div class="form-group">{label_html}{content}{error_html}{helper_html}</div>'
        )


class TimelineHandler:
    def render(self, args, content, context):
        return mark_safe(f'<div class="timeline">{content}</div>')


class TimelineItemHandler:
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        title = conditional_escape(kw.get("title", ""))
        time = conditional_escape(kw.get("time", ""))
        time_html = f'<span class="timeline-time">{time}</span>' if time else ""
        return mark_safe(
            f'<div class="timeline-item">'
            f'<div class="timeline-marker"></div>'
            f'<div class="timeline-content">'
            f'<div class="timeline-title">{title}{time_html}</div>'
            f'<div class="timeline-body">{content}</div>'
            f"</div>"
            f"</div>"
        )


# ---------------------------------------------------------------------------
# Inline handlers (no children — e.g. {% spinner %}, {% dj_button %})
# ---------------------------------------------------------------------------


class ToastContainerHandler:
    def render(self, args, context):
        toasts = context.get("toasts", [])
        dismiss_event = "dismiss_toast"
        if not toasts:
            return '<div class="toast-container"></div>'
        items = []
        for t in toasts:
            if not isinstance(t, dict):
                continue
            t_type = conditional_escape(t.get("type", "info"))
            t_id = conditional_escape(str(t.get("id", "")))
            t_msg = conditional_escape(t.get("message", ""))
            items.append(
                f'<div class="toast toast-{t_type}">'
                f'<span class="toast-message">{t_msg}</span>'
                f'<button class="toast-close" dj-click="{conditional_escape(dismiss_event)}" '
                f'data-value="{t_id}">&times;</button>'
                f"</div>"
            )
        return mark_safe(
            f'<div class="toast-container">{"".join(items)}</div>'
        )


class TooltipHandler:
    def render(self, args, content, context):
        # Tooltip is actually a block tag - but here used inline fallback
        kw = _parse_args(args, context)
        text = conditional_escape(kw.get("text", ""))
        position = conditional_escape(kw.get("position", "top"))
        return mark_safe(
            f'<span class="tooltip-wrapper">'
            f"{content}"
            f'<span class="tooltip tooltip-{position}">{text}</span>'
            f"</span>"
        )


class ProgressHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        try:
            value = max(0, min(100, int(kw.get("value", 0))))
        except (ValueError, TypeError):
            value = 0
        label = conditional_escape(kw.get("label", ""))
        size = conditional_escape(kw.get("size", "md"))
        color = conditional_escape(kw.get("color", "primary"))
        show_label = kw.get("show_label", True)
        label_row = ""
        if label or show_label:
            label_part = f'<span class="progress-label">{label}</span>' if label else ""
            pct_part = (
                f'<span class="progress-value">{value}%</span>' if show_label else ""
            )
            label_row = f'<div class="progress-label-row">{label_part}{pct_part}</div>'
        track_size = {"sm": "progress-track-sm", "lg": "progress-track-lg"}.get(
            str(size), ""
        )
        color_class = "" if color == "primary" else color
        return mark_safe(
            f'<div class="progress-wrapper">'
            f"{label_row}"
            f'<div class="progress-track {track_size}">'
            f'<div class="progress-bar {color_class}" style="width:{value}%"></div>'
            f"</div>"
            f"</div>"
        )


class BadgeHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        label = conditional_escape(kw.get("label", ""))
        status = conditional_escape(kw.get("status", "default"))
        pulse = kw.get("pulse", False)
        pulse_cls = " badge-pulse" if pulse else ""
        return mark_safe(
            f'<span class="badge badge-{status}{pulse_cls}">'
            f'<span class="badge-dot"></span>{label}'
            f"</span>"
        )


class PaginationHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        try:
            page = int(kw.get("page", 1))
            total_pages = int(kw.get("total_pages", 1))
        except (ValueError, TypeError):
            page, total_pages = 1, 1
        prev_event = conditional_escape(kw.get("prev_event", "page_prev"))
        next_event = conditional_escape(kw.get("next_event", "page_next"))
        prev_disabled = ' disabled' if page <= 1 else ""
        next_disabled = ' disabled' if page >= total_pages else ""
        return mark_safe(
            f'<div class="pagination">'
            f'<button class="pagination-btn"{prev_disabled} dj-click="{prev_event}">&#8592;</button>'
            f'<span class="pagination-info">Page {page} of {total_pages}</span>'
            f'<button class="pagination-btn"{next_disabled} dj-click="{next_event}">&#8594;</button>'
            f"</div>"
        )


class AvatarHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        src = kw.get("src", "")
        alt = conditional_escape(kw.get("alt", ""))
        initials = conditional_escape(kw.get("initials", "") or (alt[:2].upper() if alt else ""))
        size = conditional_escape(kw.get("size", "md"))
        status = conditional_escape(kw.get("status", ""))
        img_html = (
            f'<img class="avatar-image" src="{conditional_escape(src)}" alt="{alt}">'
            if src
            else f'<span class="avatar-initials">{initials}</span>'
        )
        status_html = (
            f'<span class="avatar-status avatar-status-{status}"></span>' if status else ""
        )
        return mark_safe(
            f'<div class="avatar avatar-{size}">{img_html}{status_html}</div>'
        )


class SpinnerHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        size = conditional_escape(kw.get("size", "md"))
        color = conditional_escape(kw.get("color", "primary"))
        return mark_safe(
            f'<div class="spinner spinner-{size} spinner-{color}" role="status">'
            f'<span class="sr-only">Loading...</span>'
            f"</div>"
        )


class SkeletonHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        skel_type = kw.get("type", "text")
        try:
            lines = int(kw.get("lines", 3))
        except (ValueError, TypeError):
            lines = 3
        if skel_type == "avatar":
            return mark_safe('<div class="skeleton skeleton-avatar"></div>')
        if skel_type == "card":
            inner = "".join(
                f'<div class="skeleton skeleton-line" style="width:{w}%"></div>'
                for w in [80, 60, 90, 70][:lines]
            )
            return mark_safe(
                f'<div class="skeleton skeleton-card">'
                f'<div class="skeleton skeleton-text" style="width:50%;margin-bottom:1rem"></div>'
                f"{inner}"
                f"</div>"
            )
        if skel_type == "table":
            rows = "".join(
                '<div class="skeleton skeleton-line" style="width:100%"></div>'
                for _ in range(lines)
            )
            return mark_safe(f'<div class="skeleton-table">{rows}</div>')
        # default: text lines
        widths = [90, 75, 85, 60, 80, 70, 95]
        line_html = "".join(
            f'<div class="skeleton skeleton-line" style="width:{widths[i % len(widths)]}%"></div>'
            for i in range(lines)
        )
        return mark_safe(f'<div class="skeleton-text">{line_html}</div>')


class BreadcrumbHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        items = kw.get("items") or context.get("breadcrumb_items", [])
        if not isinstance(items, (list, tuple)):
            items = []
        parts = []
        for i, item in enumerate(items):
            if isinstance(item, dict):
                label = conditional_escape(item.get("label", ""))
                url = conditional_escape(item.get("url", ""))
                active = item.get("active", i == len(items) - 1)
            else:
                label = conditional_escape(str(item))
                url = ""
                active = i == len(items) - 1
            if active:
                parts.append(f'<span class="breadcrumb-item breadcrumb-active">{label}</span>')
            else:
                link = f'<a class="breadcrumb-link" href="{url}">{label}</a>' if url else label
                parts.append(
                    f'<span class="breadcrumb-item">{link}</span>'
                    f'<span class="breadcrumb-separator">›</span>'
                )
        return mark_safe(f'<nav class="breadcrumb">{"".join(parts)}</nav>')


class EmptyStateHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        title = conditional_escape(kw.get("title", "No items found"))
        description = conditional_escape(kw.get("description", ""))
        icon = conditional_escape(kw.get("icon", "○"))
        action_label = conditional_escape(kw.get("action_label", ""))
        action_event = conditional_escape(kw.get("action_event", ""))
        desc_html = (
            f'<p class="empty-state-description">{description}</p>' if description else ""
        )
        action_html = (
            f'<button class="empty-state-action btn btn-primary" dj-click="{action_event}">'
            f"{action_label}</button>"
            if action_label and action_event
            else ""
        )
        return mark_safe(
            f'<div class="empty-state">'
            f'<div class="empty-state-icon">{icon}</div>'
            f'<h3 class="empty-state-title">{title}</h3>'
            f"{desc_html}"
            f"{action_html}"
            f"</div>"
        )


class DividerHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        label = kw.get("label", "")
        vertical = kw.get("vertical", False)
        if vertical:
            return mark_safe('<div class="divider divider-vertical"></div>')
        if label:
            return mark_safe(
                f'<div class="divider">'
                f'<span class="divider-label">{conditional_escape(label)}</span>'
                f"</div>"
            )
        return mark_safe('<hr class="divider divider-horizontal">')


class SwitchHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        name = conditional_escape(kw.get("name", "switch"))
        checked = kw.get("checked", False)
        label = conditional_escape(kw.get("label", ""))
        event = conditional_escape(kw.get("event", "toggle"))
        size = conditional_escape(kw.get("size", "md"))
        disabled = kw.get("disabled", False)
        checked_attr = " checked" if checked else ""
        disabled_attr = " disabled" if disabled else ""
        label_html = (
            f'<span class="switch-label">{label}</span>' if label else ""
        )
        size_cls = f" switch-{size}" if size != "md" else ""
        return mark_safe(
            f'<label class="switch-wrapper{size_cls}">'
            f'<input type="checkbox" class="switch-input" name="{name}"'
            f'{checked_attr}{disabled_attr} dj-change="{event}">'
            f'<span class="switch-track"><span class="switch-thumb"></span></span>'
            f"{label_html}"
            f"</label>"
        )


class StatCardHandler:
    _trend_icons = {"up": "↑", "down": "↓", "flat": "—", "": ""}

    def render(self, args, context):
        kw = _parse_args(args, context)
        label = conditional_escape(kw.get("label", ""))
        value = conditional_escape(str(kw.get("value", "")))
        trend = conditional_escape(str(kw.get("trend", "")))
        description = conditional_escape(kw.get("description", ""))
        trend_direction = kw.get("trend_direction", "")
        icon = self._trend_icons.get(str(trend_direction), "")
        trend_html = ""
        if trend:
            td_cls = f" stat-trend-{conditional_escape(trend_direction)}" if trend_direction else ""
            trend_html = (
                f'<span class="stat-card-trend{td_cls}">{icon} {trend}</span>'
            )
        desc_html = (
            f'<p class="stat-card-description">{description}</p>' if description else ""
        )
        return mark_safe(
            f'<div class="stat-card">'
            f'<div class="stat-card-label">{label}</div>'
            f'<div class="stat-card-value stat-value-primary">{value}</div>'
            f"{trend_html}"
            f"{desc_html}"
            f"</div>"
        )


class TagChipHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        label = conditional_escape(kw.get("label", ""))
        variant = conditional_escape(kw.get("variant", "default"))
        dismissible = kw.get("dismissible", False)
        event = conditional_escape(kw.get("event", "dismiss_tag"))
        size = kw.get("size", "")
        size_cls = f" tag-{conditional_escape(size)}" if size else ""
        close_html = (
            f'<button class="tag-close" dj-click="{event}">&times;</button>'
            if dismissible
            else ""
        )
        return mark_safe(
            f'<span class="tag tag-{variant}{size_cls}">{label}{close_html}</span>'
        )


class StepperHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        steps = kw.get("steps") or context.get("steps", [])
        if not isinstance(steps, (list, tuple)):
            steps = []
        try:
            active = int(kw.get("active", 0))
        except (ValueError, TypeError):
            active = 0
        event = conditional_escape(kw.get("event", "set_step"))
        parts = []
        for i, step in enumerate(steps):
            if isinstance(step, dict):
                label = conditional_escape(step.get("label", f"Step {i + 1}"))
                complete = step.get("complete", i < active)
            else:
                label = conditional_escape(str(step))
                complete = i < active
            cls = "stepper-step"
            if i == active:
                cls += " stepper-step-active"
            elif complete:
                cls += " stepper-step-complete"
            parts.append(
                f'<div class="{cls}" dj-click="{event}" data-value="{i}">'
                f'<div class="stepper-step-circle">{i + 1}</div>'
                f'<div class="stepper-step-label">{label}</div>'
                f"</div>"
            )
        return mark_safe(f'<div class="stepper">{"".join(parts)}</div>')


class DjButtonHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        label = conditional_escape(kw.get("label", ""))
        variant = conditional_escape(kw.get("variant", "primary"))
        event = conditional_escape(kw.get("event", ""))
        icon = kw.get("icon", "")
        disabled = kw.get("disabled", False)
        loading = kw.get("loading", False)
        size = kw.get("size", "md")
        classes = ["btn", f"btn-{variant}"]
        if size and size != "md":
            classes.append(f"btn-{conditional_escape(size)}")
        if loading:
            classes.append("btn-loading")
        attrs = [f'class="{" ".join(classes)}"']
        if event and not loading and not disabled:
            attrs.append(f'dj-click="{event}"')
        if disabled or loading:
            attrs.append("disabled")
        spinner = '<span class="btn-spinner"></span>' if loading else ""
        icon_html = (
            f'<span class="btn-icon">{conditional_escape(icon)}</span>' if icon else ""
        )
        return mark_safe(
            f'<button {" ".join(attrs)}>'
            f"{spinner}{icon_html}"
            f'<span class="btn-label">{label}</span>'
            f"</button>"
        )


class DjInputHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        name = conditional_escape(kw.get("name", ""))
        label = conditional_escape(kw.get("label", ""))
        value = conditional_escape(str(kw.get("value", "")))
        placeholder = conditional_escape(kw.get("placeholder", ""))
        input_type = conditional_escape(kw.get("type", "text"))
        error = conditional_escape(kw.get("error", ""))
        helper = conditional_escape(kw.get("helper", ""))
        required = kw.get("required", False)
        disabled = kw.get("disabled", False)
        event = conditional_escape(kw.get("event", name))
        input_cls = "form-input" + (" form-input-error" if error else "")
        required_attr = " required" if required else ""
        disabled_attr = " disabled" if disabled else ""
        required_span = '<span class="form-label-required">*</span>' if required else ""
        label_html = (
            f'<label class="form-label" for="{name}">{label}{required_span}</label>'
            if label
            else ""
        )
        error_html = f'<div class="form-error-message">{error}</div>' if error else ""
        helper_html = f'<div class="form-helper">{helper}</div>' if helper else ""
        return mark_safe(
            f'<div class="form-group">'
            f"{label_html}"
            f'<input type="{input_type}" id="{name}" name="{name}" class="{input_cls}" '
            f'value="{value}" placeholder="{placeholder}"{required_attr}{disabled_attr} '
            f'dj-input="{event}">'
            f"{error_html}{helper_html}"
            f"</div>"
        )


class DjSelectHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        name = conditional_escape(kw.get("name", ""))
        label = conditional_escape(kw.get("label", ""))
        current = str(kw.get("value", ""))
        options = kw.get("options") or context.get(kw.get("options_var", ""), [])
        error = conditional_escape(kw.get("error", ""))
        required = kw.get("required", False)
        disabled = kw.get("disabled", False)
        event = conditional_escape(kw.get("event", name))
        if not isinstance(options, (list, tuple)):
            options = []
        option_html = []
        for opt in options:
            if isinstance(opt, dict):
                ov = conditional_escape(str(opt.get("value", "")))
                ol = conditional_escape(str(opt.get("label", ov)))
            elif isinstance(opt, (list, tuple)) and len(opt) >= 2:
                ov, ol = conditional_escape(str(opt[0])), conditional_escape(str(opt[1]))
            else:
                ov = ol = conditional_escape(str(opt))
            sel = " selected" if str(ov) == str(current) else ""
            option_html.append(f'<option value="{ov}"{sel}>{ol}</option>')
        select_cls = "form-select" + (" form-select-error" if error else "")
        required_attr = " required" if required else ""
        disabled_attr = " disabled" if disabled else ""
        required_span = '<span class="form-label-required">*</span>' if required else ""
        label_html = (
            f'<label class="form-label" for="{name}">{label}{required_span}</label>'
            if label
            else ""
        )
        error_html = f'<div class="form-error-message">{error}</div>' if error else ""
        return mark_safe(
            f'<div class="form-group">'
            f"{label_html}"
            f'<select id="{name}" name="{name}" class="{select_cls}"'
            f'{required_attr}{disabled_attr} dj-change="{event}">'
            f'{"".join(option_html)}'
            f"</select>"
            f"{error_html}"
            f"</div>"
        )


class DjTextareaHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        name = conditional_escape(kw.get("name", ""))
        label = conditional_escape(kw.get("label", ""))
        value = conditional_escape(str(kw.get("value", "")))
        placeholder = conditional_escape(kw.get("placeholder", ""))
        error = conditional_escape(kw.get("error", ""))
        helper = conditional_escape(kw.get("helper", ""))
        required = kw.get("required", False)
        disabled = kw.get("disabled", False)
        event = conditional_escape(kw.get("event", name))
        try:
            rows = int(kw.get("rows", 4))
        except (ValueError, TypeError):
            rows = 4
        ta_cls = "form-textarea" + (" form-textarea-error" if error else "")
        required_attr = " required" if required else ""
        disabled_attr = " disabled" if disabled else ""
        required_span = '<span class="form-label-required">*</span>' if required else ""
        label_html = (
            f'<label class="form-label" for="{name}">{label}{required_span}</label>'
            if label
            else ""
        )
        error_html = f'<div class="form-error-message">{error}</div>' if error else ""
        helper_html = f'<div class="form-helper">{helper}</div>' if helper else ""
        return mark_safe(
            f'<div class="form-group">'
            f"{label_html}"
            f'<textarea id="{name}" name="{name}" class="{ta_cls}" rows="{rows}" '
            f'placeholder="{placeholder}"{required_attr}{disabled_attr} '
            f'dj-input="{event}">{value}</textarea>'
            f"{error_html}{helper_html}"
            f"</div>"
        )


class DjCheckboxHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        name = conditional_escape(kw.get("name", ""))
        label = conditional_escape(kw.get("label", ""))
        checked = kw.get("checked", False)
        value = conditional_escape(str(kw.get("value", "on")))
        event = conditional_escape(kw.get("event", name))
        disabled = kw.get("disabled", False)
        checked_attr = " checked" if checked else ""
        disabled_attr = " disabled" if disabled else ""
        return mark_safe(
            f'<div class="form-checkbox-wrapper">'
            f'<label class="form-checkbox-label">'
            f'<input type="checkbox" class="form-checkbox" name="{name}" value="{value}"'
            f'{checked_attr}{disabled_attr} dj-change="{event}">'
            f"{label}"
            f"</label>"
            f"</div>"
        )


class DjRadioHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        name = conditional_escape(kw.get("name", ""))
        label = conditional_escape(kw.get("label", ""))
        value = conditional_escape(str(kw.get("value", "")))
        current = str(kw.get("current_value", "") or context.get(str(kw.get("current_value_var", "")), ""))
        event = conditional_escape(kw.get("event", name))
        disabled = kw.get("disabled", False)
        checked_attr = " checked" if str(value) == str(current) else ""
        disabled_attr = " disabled" if disabled else ""
        return mark_safe(
            f'<div class="form-radio-wrapper">'
            f'<label class="form-radio-label">'
            f'<input type="radio" class="form-radio" name="{name}" value="{value}"'
            f'{checked_attr}{disabled_attr} dj-change="{event}">'
            f"{label}"
            f"</label>"
            f"</div>"
        )


class DataTableHandler:
    def render(self, args, context):
        kw = _parse_args(args, context)
        rows = kw.get("rows") or context.get("rows", [])
        columns = kw.get("columns") or context.get("columns", [])
        sort_by = conditional_escape(str(kw.get("sort_by", "")))
        sort_desc = kw.get("sort_desc", False)
        sort_event = conditional_escape(kw.get("sort_event", "table_sort"))
        if not isinstance(rows, (list, tuple)):
            rows = []
        if not isinstance(columns, (list, tuple)):
            columns = []
        header_cells = []
        for col in columns:
            if isinstance(col, dict):
                key = conditional_escape(str(col.get("key", "")))
                col_label = conditional_escape(str(col.get("label", key)))
            else:
                key = col_label = conditional_escape(str(col))
            active = "active" if key == sort_by else ""
            arrow = " ↓" if (key == sort_by and sort_desc) else " ↑" if key == sort_by else ""
            header_cells.append(
                f'<th class="sortable {active}" dj-click="{sort_event}" data-value="{key}">'
                f"{col_label}{arrow}</th>"
            )
        body_rows = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            cells = ""
            for col in columns:
                key = col.get("key", col) if isinstance(col, dict) else col
                cell_val = conditional_escape(str(row.get(str(key), "")))
                cells += f"<td>{cell_val}</td>"
            body_rows.append(f"<tr>{cells}</tr>")
        return mark_safe(
            f'<div class="data-table-wrapper">'
            f'<table class="data-table">'
            f"<thead><tr>{''.join(header_cells)}</tr></thead>"
            f"<tbody>{''.join(body_rows)}</tbody>"
            f"</table>"
            f"</div>"
        )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

# Inline handlers: (tag_name, handler_instance)
INLINE_HANDLERS = [
    ("toast_container", ToastContainerHandler()),
    ("progress", ProgressHandler()),
    ("badge", BadgeHandler()),
    ("pagination", PaginationHandler()),
    ("avatar", AvatarHandler()),
    ("data_table", DataTableHandler()),
    ("spinner", SpinnerHandler()),
    ("skeleton", SkeletonHandler()),
    ("breadcrumb", BreadcrumbHandler()),
    ("empty_state", EmptyStateHandler()),
    ("dj_divider", DividerHandler()),
    ("switch", SwitchHandler()),
    ("stat_card", StatCardHandler()),
    ("dj_tag", TagChipHandler()),
    ("stepper", StepperHandler()),
    ("dj_button", DjButtonHandler()),
    ("dj_input", DjInputHandler()),
    ("dj_select", DjSelectHandler()),
    ("dj_textarea", DjTextareaHandler()),
    ("dj_checkbox", DjCheckboxHandler()),
    ("dj_radio", DjRadioHandler()),
]

# Block handlers: (tag_name, end_tag_name, handler_instance)
BLOCK_HANDLERS = [
    ("modal", "endmodal", ModalHandler()),
    ("card", "endcard", CardHandler()),
    ("tabs", "endtabs", TabsHandler()),
    ("accordion", "endaccordion", AccordionHandler()),
    ("accordion_item", "endaccordion_item", AccordionItemHandler()),
    ("dropdown", "enddropdown", DropdownHandler()),
    ("alert", "endalert", AlertHandler()),
    ("form_group", "endform_group", FormGroupHandler()),
    ("timeline", "endtimeline", TimelineHandler()),
    ("timeline_item", "endtimeline_item", TimelineItemHandler()),
    ("tooltip", "endtooltip", TooltipHandler()),
]


def register_with_rust_engine():
    """Register all component tag handlers with the Rust template engine.

    Called from DjustComponentsConfig.ready(). Safe to call multiple times
    (subsequent calls overwrite existing registrations).
    """
    try:
        from djust._rust import (  # type: ignore[import]
            register_block_tag_handler,
            register_tag_handler,
        )
    except ImportError:
        # djust not installed — skip silently (components still work via
        # Django template engine with {% load djust_components %})
        return

    for tag_name, handler in INLINE_HANDLERS:
        register_tag_handler(tag_name, handler)

    for tag_name, end_tag, handler in BLOCK_HANDLERS:
        register_block_tag_handler(tag_name, end_tag, handler)


# ===========================================================================
# TIER 2 REMAINING + TIER 3 HANDLERS
# ===========================================================================

class CodeBlockHandler:
    """Inline handler for {% code_block code=... language=... %}"""
    def render(self, args, context):
        from django.utils.html import conditional_escape
        from djust_components.templatetags.djust_components import code_block as _cb
        kwargs = _parse_args(args, context)
        code = kwargs.get("code", "")
        language = kwargs.get("language", "")
        filename = kwargs.get("filename", "")
        return str(_cb(code=code, language=language, filename=filename))


class ComboboxHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import combobox as _cb
        kwargs = _parse_args(args, context)
        return str(_cb(
            name=kwargs.get("name", ""),
            label=kwargs.get("label", ""),
            value=kwargs.get("value", ""),
            placeholder=kwargs.get("placeholder", "Search…"),
            options=context.get(kwargs.get("options", ""), []),
            event=kwargs.get("event", ""),
            search_event=kwargs.get("search_event", ""),
        ))


class RatingHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import rating as _r
        kwargs = _parse_args(args, context)
        return str(_r(
            value=kwargs.get("value", 0),
            max_stars=kwargs.get("max_stars", 5),
            readonly=kwargs.get("readonly", False),
            event=kwargs.get("event", "set_rating"),
            size=kwargs.get("size", "md"),
        ))


class CopyButtonHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import copy_button as _c
        kwargs = _parse_args(args, context)
        return str(_c(
            text=kwargs.get("text", ""),
            label=kwargs.get("label", "Copy"),
            variant=kwargs.get("variant", "outline"),
            size=kwargs.get("size", "sm"),
        ))


class KbdHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import kbd as _k
        # args is a list of strings; filter out empty ones
        keys = [a.strip("'\"") for a in args if a.strip("'\"")]
        return str(_k(*keys))


class GaugeHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import gauge as _g
        kwargs = _parse_args(args, context)
        return str(_g(
            value=kwargs.get("value", 0),
            max_value=kwargs.get("max_value", 100),
            label=kwargs.get("label", ""),
            color=kwargs.get("color", "primary"),
            size=kwargs.get("size", "md"),
        ))


class NotificationCenterHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import notification_center as _nc
        kwargs = _parse_args(args, context)
        notifs_key = kwargs.get("notifications", "notifications")
        notifs = context.get(notifs_key, []) if isinstance(notifs_key, str) else notifs_key
        unread = sum(1 for n in notifs if isinstance(n, dict) and n.get("unread"))
        return str(_nc(
            notifications=notifs,
            unread_count=unread,
            open_event=kwargs.get("open_event", "toggle_notifications"),
        ))


class TreeViewHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import tree_view as _tv
        kwargs = _parse_args(args, context)
        nodes_key = kwargs.get("nodes", "tree_nodes")
        nodes = context.get(nodes_key, []) if isinstance(nodes_key, str) else nodes_key
        return str(_tv(
            nodes=nodes,
            expand_event=kwargs.get("expand_event", "tree_expand"),
            select_event=kwargs.get("select_event", "tree_select"),
            selected=kwargs.get("selected", ""),
        ))


class ColorPickerHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import color_picker as _cp
        kwargs = _parse_args(args, context)
        return str(_cp(
            name=kwargs.get("name", ""),
            value=kwargs.get("value", "#3B82F6"),
            event=kwargs.get("event", ""),
            label=kwargs.get("label", ""),
        ))


class CarouselHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import carousel as _car
        kwargs = _parse_args(args, context)
        imgs_key = kwargs.get("images", "carousel_images")
        images = context.get(imgs_key, []) if isinstance(imgs_key, str) else imgs_key
        return str(_car(
            images=images,
            active=kwargs.get("active", 0),
            prev_event=kwargs.get("prev_event", "carousel_prev"),
            next_event=kwargs.get("next_event", "carousel_next"),
        ))


class PaletteItemHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import palette_item as _pi
        kwargs = _parse_args(args, context)
        return str(_pi(
            label=kwargs.get("label", ""),
            shortcut=kwargs.get("shortcut", ""),
            description=kwargs.get("description", ""),
            event=kwargs.get("event", ""),
            icon=kwargs.get("icon", ""),
        ))


class ContextMenuItemHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import context_menu_item as _ci
        kwargs = _parse_args(args, context)
        return str(_ci(
            label=kwargs.get("label", ""),
            event=kwargs.get("event", ""),
            icon=kwargs.get("icon", ""),
            danger=kwargs.get("danger", False),
            divider=kwargs.get("divider", False),
        ))


class PopoverHandler:
    """Block handler for {% popover trigger="..." %}...{% endpopover %}"""
    def render(self, args, content, context):
        kwargs = _parse_args(args, context)
        trigger = kwargs.get("trigger", "Click me")
        placement = kwargs.get("placement", "bottom")
        title = kwargs.get("title", "")
        from django.utils.html import conditional_escape
        e_trigger = conditional_escape(trigger)
        e_placement = conditional_escape(placement)
        title_html = (
            f'<div class="popover-title">{conditional_escape(title)}</div>'
            if title else ""
        )
        return (
            f'<div class="popover-wrapper">'
            f'<button class="popover-trigger btn btn-outline btn-sm" '
            f"onclick=\"(function(el){{var p=el.parentElement;p.classList.toggle('popover-open');"
            f"document.addEventListener('click',function h(e){{if(!p.contains(e.target)){{p.classList.remove('popover-open');document.removeEventListener('click',h);}}}},true);"
            f'}})(this)">'
            f'{e_trigger}</button>'
            f'<div class="popover popover-{e_placement}">'
            f'{title_html}'
            f'<div class="popover-content">{content}</div>'
            f'</div>'
            f'</div>'
        )


class CollapsibleHandler:
    """Block handler for {% collapsible trigger="..." %}...{% endcollapsible %}"""
    def render(self, args, content, context):
        kwargs = _parse_args(args, context)
        trigger = kwargs.get("trigger", "Toggle")
        event = kwargs.get("event", "toggle_collapsible")
        open_ = kwargs.get("open", False)
        if isinstance(open_, str):
            open_ = open_.lower() not in ("false", "0", "")
        from django.utils.html import conditional_escape
        e_trigger = conditional_escape(trigger)
        e_event = conditional_escape(event)
        open_cls = " collapsible-open" if open_ else ""
        return (
            f'<div class="collapsible{open_cls}">'
            f'<button class="collapsible-trigger" '
            f'onclick="(function(el){{el.closest(\'.collapsible\').classList.toggle(\'collapsible-open\');}})(this)"'
            f' dj-click="{e_event}">'
            f'<span class="collapsible-label">{e_trigger}</span>'
            f'<span class="collapsible-icon">▾</span>'
            f'</button>'
            f'<div class="collapsible-content">{content}</div>'
            f'</div>'
        )


class SheetHandler:
    """Block handler for {% sheet side="right" open=show_sheet %}...{% endsheet %}"""
    def render(self, args, content, context):
        kwargs = _parse_args(args, context)
        open_ = kwargs.get("open", False)
        if isinstance(open_, str):
            open_ = open_.lower() not in ("false", "0", "")
        side = kwargs.get("side", "right")
        title = kwargs.get("title", "")
        close_event = kwargs.get("close_event", "close_sheet")
        from django.utils.html import conditional_escape
        e_side = conditional_escape(side)
        e_title = conditional_escape(title)
        e_close = conditional_escape(close_event)
        open_attr = ' data-open="true"' if open_ else ""
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
        return (
            f'<div class="sheet-overlay" dj-click="{e_close}"{open_attr}></div>'
            f'<div class="sheet sheet-{e_side}"{open_attr}>'
            f'{title_html}'
            f'<div class="sheet-body">{content}</div>'
            f'</div>'
        )


class CommandPaletteHandler:
    """Block handler for {% command_palette open=show_palette %}...{% endcommand_palette %}"""
    def render(self, args, content, context):
        kwargs = _parse_args(args, context)
        open_ = kwargs.get("open", False)
        if isinstance(open_, str):
            open_ = open_.lower() not in ("false", "0", "")
        search_event = kwargs.get("search_event", "palette_search")
        close_event = kwargs.get("close_event", "close_palette")
        placeholder = kwargs.get("placeholder", "Search commands…")
        from django.utils.html import conditional_escape
        e_search = conditional_escape(search_event)
        e_close = conditional_escape(close_event)
        e_placeholder = conditional_escape(placeholder)
        open_attr = ' data-open="true"' if open_ else ""
        return (
            f'<div class="palette-overlay" dj-click="{e_close}"{open_attr}></div>'
            f'<div class="palette"{open_attr}>'
            f'<div class="palette-search">'
            f'<span class="palette-search-icon">⌕</span>'
            f'<input class="palette-input" type="text" placeholder="{e_placeholder}" '
            f'dj-input="{e_search}">'
            f'<button class="palette-close" dj-click="{e_close}">Esc</button>'
            f'</div>'
            f'<div class="palette-results">{content}</div>'
            f'</div>'
        )


class ContextMenuHandler:
    """Block handler for {% context_menu label="..." %}...{% endcontext_menu %}"""
    def render(self, args, content, context):
        kwargs = _parse_args(args, context)
        label = kwargs.get("label", "Right-click here")
        from django.utils.html import conditional_escape
        e_label = conditional_escape(label)
        return (
            f'<div class="ctx-wrapper" '
            f"oncontextmenu=\"(function(e,el){{e.preventDefault();"
            f"document.querySelectorAll('.ctx-menu[data-open]').forEach(function(m){{delete m.dataset.open;}});"
            f"var m=el.querySelector('.ctx-menu');"
            f"m.style.left=e.offsetX+'px';m.style.top=e.offsetY+'px';"
            f"m.dataset.open='1';"
            f"document.addEventListener('click',function h(){{delete m.dataset.open;document.removeEventListener('click',h);}},{{once:true}});"
            f'}})(event,this)">'
            f'<div class="ctx-trigger">{e_label}</div>'
            f'<div class="ctx-menu">{content}</div>'
            f'</div>'
        )


# Extend lists with Tier 2/3 handlers (defined above, after the original lists)
INLINE_HANDLERS.extend([
    ("code_block", CodeBlockHandler()),
    ("combobox", ComboboxHandler()),
    ("rating", RatingHandler()),
    ("copy_button", CopyButtonHandler()),
    ("kbd", KbdHandler()),
    ("gauge", GaugeHandler()),
    ("notification_center", NotificationCenterHandler()),
    ("tree_view", TreeViewHandler()),
    ("color_picker", ColorPickerHandler()),
    ("carousel", CarouselHandler()),
    ("palette_item", PaletteItemHandler()),
    ("context_menu_item", ContextMenuItemHandler()),
])

BLOCK_HANDLERS.extend([
    ("popover", "endpopover", PopoverHandler()),
    ("collapsible", "endcollapsible", CollapsibleHandler()),
    ("sheet", "endsheet", SheetHandler()),
    ("command_palette", "endcommand_palette", CommandPaletteHandler()),
    ("context_menu", "endcontext_menu", ContextMenuHandler()),
])


# ===========================================================================
# v1.3 HANDLERS
# ===========================================================================

class DatePickerHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import date_picker as _dp
        kwargs = _parse_args(args, context)
        return str(_dp(
            year=kwargs.get("year"),
            month=kwargs.get("month"),
            selected=kwargs.get("selected", ""),
            prev_event=kwargs.get("prev_event", "date_prev_month"),
            next_event=kwargs.get("next_event", "date_next_month"),
            select_event=kwargs.get("select_event", "date_select"),
            name=kwargs.get("name", "date"),
            label=kwargs.get("label", ""),
        ))


class FileDropzoneHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import file_dropzone as _fd
        kwargs = _parse_args(args, context)
        return str(_fd(
            name=kwargs.get("name", "file"),
            label=kwargs.get("label", ""),
            accept=kwargs.get("accept", ""),
            multiple=kwargs.get("multiple", False),
            max_size_mb=kwargs.get("max_size_mb", 10),
            event=kwargs.get("event", "file_selected"),
        ))


class VirtualListHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import virtual_list as _vl
        kwargs = _parse_args(args, context)
        items_key = kwargs.get("items", "vl_items")
        items = context.get(items_key, []) if isinstance(items_key, str) else items_key
        return str(_vl(
            items=items,
            total=kwargs.get("total", len(items) if items else 0),
            page=kwargs.get("page", 1),
            page_size=kwargs.get("page_size", 20),
            load_more_event=kwargs.get("load_more_event", "load_more"),
        ))


class KanbanBoardHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import kanban_board as _kb
        kwargs = _parse_args(args, context)
        cols_key = kwargs.get("columns", "kanban_columns")
        columns = context.get(cols_key, []) if isinstance(cols_key, str) else cols_key
        return str(_kb(
            columns=columns,
            move_event=kwargs.get("move_event", "kanban_move"),
            add_card_event=kwargs.get("add_card_event", "kanban_add_card"),
        ))


class TableOfContentsHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import table_of_contents as _toc
        kwargs = _parse_args(args, context)
        items_key = kwargs.get("items", "toc_items")
        items = context.get(items_key, []) if isinstance(items_key, str) else items_key
        return str(_toc(
            items=items,
            title=kwargs.get("title", "Contents"),
            active=kwargs.get("active", ""),
        ))


class RichTextEditorHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import rich_text_editor as _rte
        kwargs = _parse_args(args, context)
        return str(_rte(
            name=kwargs.get("name", "content"),
            value=kwargs.get("value", ""),
            event=kwargs.get("event", "update_content"),
            label=kwargs.get("label", ""),
            height=kwargs.get("height", "200px"),
        ))


# Register v1.3 inline handlers
INLINE_HANDLERS.extend([
    ("date_picker", DatePickerHandler()),
    ("file_dropzone", FileDropzoneHandler()),
    ("virtual_list", VirtualListHandler()),
    ("kanban_board", KanbanBoardHandler()),
    ("table_of_contents", TableOfContentsHandler()),
    ("rich_text_editor", RichTextEditorHandler()),
])


class SplitPaneHandler:
    """Block handler for {% split_pane %}...{% pane %}...{% endsplit_pane %}"""
    def render(self, args, content, context):
        # For Rust engine, content is pre-rendered; we just wrap it
        kwargs = _parse_args(args, context)
        direction = kwargs.get("direction", "horizontal")
        initial = kwargs.get("initial", "50")
        from django.utils.html import conditional_escape as ce
        import uuid as _uuid
        uid = f"sp-{_uuid.uuid4().hex[:6]}"
        size_prop = "width" if direction == "horizontal" else "height"
        return (
            f'<div class="split-pane split-pane-{ce(direction)}" id="{uid}">'
            f'{content}'
            f'</div>'
        )


BLOCK_HANDLERS.extend([
    ("split_pane", "endsplit_pane", SplitPaneHandler()),
])
