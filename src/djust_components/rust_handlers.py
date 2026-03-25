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

def _parse_args(args: list[str], context: dict[str, object]) -> dict[str, object]:
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
        elif val in ("True", "true"):
            result[key] = True
        elif val in ("False", "false"):
            result[key] = False
        elif val == "":
            result[key] = ""
        # None
        elif val in ("None", "null"):
            result[key] = None
        else:
            # Try numeric before falling back to variable reference
            try:
                result[key] = int(val)
            except ValueError:
                try:
                    result[key] = float(val)
                except ValueError:
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
                f'<div class="divider-label">'
                f"<span>{conditional_escape(label)}</span>"
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
            f'<span class="switch">'
            f'<input type="checkbox" class="switch-input" name="{name}"'
            f'{checked_attr}{disabled_attr} dj-change="{event}">'
            f'<span class="switch-track"></span>'
            f'<span class="switch-thumb"></span>'
            f'</span>'
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

        # Phase 1 parameters (all opt-in)
        selectable = kw.get("selectable", False)
        selected_rows = kw.get("selected_rows") or []
        select_event = conditional_escape(kw.get("select_event", "table_select"))
        row_key = str(kw.get("row_key", "id"))
        search = kw.get("search", False)
        search_query = conditional_escape(str(kw.get("search_query", "")))
        search_event = conditional_escape(kw.get("search_event", "table_search"))
        try:
            search_debounce = int(kw.get("search_debounce", 300))
        except (ValueError, TypeError):
            search_debounce = 300
        filters = kw.get("filters") or {}
        filter_event = conditional_escape(kw.get("filter_event", "table_filter"))
        loading = kw.get("loading", False)
        empty_title = conditional_escape(str(kw.get("empty_title", "No data")))
        empty_description = conditional_escape(str(kw.get("empty_description", "")))
        empty_icon = conditional_escape(str(kw.get("empty_icon", "")))
        paginate = kw.get("paginate", False)
        try:
            page = int(kw.get("page", 1))
            total_pages = int(kw.get("total_pages", 1))
        except (ValueError, TypeError):
            page, total_pages = 1, 1
        page_event = conditional_escape(kw.get("page_event", "table_page"))
        striped = kw.get("striped", False)
        compact = kw.get("compact", False)

        # Phase 2 parameters (all opt-in)
        editable_columns = kw.get("editable_columns") or []
        edit_event = conditional_escape(kw.get("edit_event", "table_cell_edit"))
        resizable = kw.get("resizable", False)
        reorderable = kw.get("reorderable", False)
        reorder_event = conditional_escape(kw.get("reorder_event", "table_reorder"))
        try:
            frozen_left = int(kw.get("frozen_left", 0))
        except (ValueError, TypeError):
            frozen_left = 0
        try:
            frozen_right = int(kw.get("frozen_right", 0))
        except (ValueError, TypeError):
            frozen_right = 0
        column_visibility = kw.get("column_visibility", False)
        visibility_event = conditional_escape(kw.get("visibility_event", "table_visibility"))
        density = conditional_escape(str(kw.get("density", "comfortable")))
        density_toggle = kw.get("density_toggle", False)
        density_event = conditional_escape(kw.get("density_event", "table_density"))
        responsive_cards = kw.get("responsive_cards", False)
        editable_rows = kw.get("editable_rows", False)
        edit_row_event = conditional_escape(kw.get("edit_row_event", "table_row_edit"))
        save_row_event = conditional_escape(kw.get("save_row_event", "table_row_save"))
        cancel_row_event = conditional_escape(kw.get("cancel_row_event", "table_row_cancel"))
        editing_rows = kw.get("editing_rows") or []

        # Phase 3 parameters (all opt-in)
        expandable = kw.get("expandable", False)
        expand_event = conditional_escape(kw.get("expand_event", "table_expand"))
        expanded_rows = kw.get("expanded_rows") or []
        bulk_actions = kw.get("bulk_actions") or []
        bulk_action_event = conditional_escape(kw.get("bulk_action_event", "table_bulk_action"))
        exportable = kw.get("exportable", False)
        export_event = conditional_escape(kw.get("export_event", "table_export"))
        export_formats = kw.get("export_formats") or ["csv", "json"]
        group_by = str(kw.get("group_by", ""))
        group_event = conditional_escape(kw.get("group_event", "table_group"))
        group_toggle_event = conditional_escape(kw.get("group_toggle_event", "table_group_toggle"))
        collapsible_groups = kw.get("collapsible_groups", True)
        collapsed_groups = kw.get("collapsed_groups") or []
        keyboard_nav = kw.get("keyboard_nav", False)
        virtual_scroll = kw.get("virtual_scroll", False)
        try:
            virtual_row_height = int(kw.get("virtual_row_height", 40))
        except (ValueError, TypeError):
            virtual_row_height = 40
        try:
            virtual_buffer = int(kw.get("virtual_buffer", 5))
        except (ValueError, TypeError):
            virtual_buffer = 5
        server_mode = kw.get("server_mode", False)
        facets = kw.get("facets", False)
        facet_counts = kw.get("facet_counts") or {}
        persist_key = conditional_escape(str(kw.get("persist_key", "")))
        printable = kw.get("printable", False)
        column_stats = kw.get("column_stats") or {}

        if not isinstance(rows, (list, tuple)):
            rows = []
        if not isinstance(columns, (list, tuple)):
            columns = []
        if not isinstance(selected_rows, (list, tuple)):
            selected_rows = []
        if not isinstance(filters, dict):
            filters = {}
        if not isinstance(editable_columns, (list, tuple)):
            editable_columns = []
        if not isinstance(editing_rows, (list, tuple, set)):
            editing_rows = []
        if not isinstance(expanded_rows, (list, tuple, set)):
            expanded_rows = []
        if not isinstance(bulk_actions, (list, tuple)):
            bulk_actions = []
        if not isinstance(export_formats, (list, tuple)):
            export_formats = ["csv", "json"]
        if not isinstance(collapsed_groups, (list, tuple, set)):
            collapsed_groups = []
        if not isinstance(facet_counts, dict):
            facet_counts = {}
        if not isinstance(column_stats, dict):
            column_stats = {}

        # Convert to sets for fast lookup
        selected_set = {str(v) for v in selected_rows}
        editable_col_set = set(str(c) for c in editable_columns)
        editing_row_set = {str(v) for v in editing_rows}
        expanded_set = {str(v) for v in expanded_rows}
        collapsed_group_set = {str(v) for v in collapsed_groups}
        num_cols = len(columns)

        # --- Table classes ---
        table_classes = ["data-table"]
        if striped:
            table_classes.append("data-table-striped")
        if compact or density == "compact":
            table_classes.append("data-table-compact")
        if density == "spacious":
            table_classes.append("data-table-spacious")
        table_cls = " ".join(table_classes)

        # --- Wrapper attributes ---
        wrapper_classes = ["data-table-wrapper", "data-table-container"]
        if responsive_cards:
            wrapper_classes.append("data-table-responsive")
        if printable:
            wrapper_classes.append("data-table-printable")
        wrapper_attrs = []
        if resizable:
            wrapper_attrs.append('data-resizable="true"')
        if reorderable:
            wrapper_attrs.append('data-reorderable="true"')
            wrapper_attrs.append(f'data-reorder-event="{reorder_event}"')
        if editable_columns:
            wrapper_attrs.append(f'data-edit-event="{edit_event}"')
        if column_visibility:
            wrapper_attrs.append(f'data-visibility-event="{visibility_event}"')
        if keyboard_nav:
            wrapper_attrs.append('data-keyboard-nav="true" tabindex="0"')
        if virtual_scroll:
            wrapper_attrs.append(f'data-virtual-scroll="true"')
            wrapper_attrs.append(f'data-virtual-row-height="{virtual_row_height}"')
            wrapper_attrs.append(f'data-virtual-buffer="{virtual_buffer}"')
        if server_mode:
            wrapper_attrs.append('data-server-mode="true"')
        if persist_key:
            wrapper_attrs.append(f'data-persist-key="{persist_key}"')
        wrapper_attrs_str = (" " + " ".join(wrapper_attrs)) if wrapper_attrs else ""

        # --- Toolbar (column visibility + density toggle) ---
        toolbar_html = ""
        toolbar_parts = []

        if column_visibility:
            vis_items = ""
            for col in columns:
                if isinstance(col, dict):
                    ckey = conditional_escape(str(col.get("key", "")))
                    clabel = conditional_escape(str(col.get("label", ckey)))
                else:
                    ckey = clabel = conditional_escape(str(col))
                vis_items += (
                    f'<label class="data-table-visibility-item">'
                    f'<input type="checkbox" checked data-col-key="{ckey}"> {clabel}'
                    f'</label>'
                )
            toolbar_parts.append(
                f'<div class="data-table-visibility-dropdown">'
                f'<button type="button" class="data-table-visibility-btn">'
                f'&#9776; Columns</button>'
                f'<div class="data-table-visibility-menu">{vis_items}</div>'
                f'</div>'
            )

        if density_toggle:
            def _dbtn(val, label):
                active = " active" if val == density else ""
                return (
                    f'<button type="button" class="data-table-density-btn{active}"'
                    f' data-density="{val}"'
                    f' dj-click="{density_event}" data-value="{val}">{label}</button>'
                )
            toolbar_parts.append(
                f'<div class="data-table-density-toggle">'
                f'{_dbtn("compact", "Compact")}'
                f'{_dbtn("comfortable", "Comfortable")}'
                f'{_dbtn("spacious", "Spacious")}'
                f'</div>'
            )

        if exportable:
            export_btns = ""
            for fmt in export_formats:
                fmt_esc = conditional_escape(str(fmt))
                label = fmt_esc.upper()
                export_btns += (
                    f'<button type="button" class="data-table-export-btn"'
                    f' dj-click="{export_event}" data-value="{fmt_esc}">'
                    f'Export {label}</button>'
                )
            toolbar_parts.append(
                f'<div class="data-table-export">{export_btns}</div>'
            )

        # Bulk actions bar (rendered separately, shown conditionally)
        bulk_actions_html = ""
        if bulk_actions and selected_rows:
            ba_btns = ""
            for ba in bulk_actions:
                if isinstance(ba, dict):
                    ba_key = conditional_escape(str(ba.get("key", "")))
                    ba_label = conditional_escape(str(ba.get("label", ba_key)))
                else:
                    ba_key = ba_label = conditional_escape(str(ba))
                ba_btns += (
                    f'<button type="button" class="data-table-bulk-btn"'
                    f' dj-click="{bulk_action_event}" data-value="{ba_key}">'
                    f'{ba_label}</button>'
                )
            count = len(selected_rows)
            bulk_actions_html = (
                f'<div class="data-table-bulk-bar">'
                f'<span class="data-table-bulk-count">{count} selected</span>'
                f'{ba_btns}'
                f'</div>'
            )

        if toolbar_parts:
            toolbar_html = (
                f'<div class="data-table-toolbar">'
                f'{"".join(toolbar_parts)}'
                f'</div>'
            )

        # --- Search bar ---
        search_html = ""
        if search:
            search_html = (
                f'<div class="data-table-search">'
                f'<input type="text" role="searchbox" aria-label="Search table"'
                f' class="table-search" placeholder="Search..."'
                f' value="{search_query}"'
                f' dj-input="{search_event}" dj-debounce="{search_debounce}">'
                f'</div>'
            )

        # --- Loading state ---
        if loading:
            skeleton_rows = "".join(
                '<div class="skeleton skeleton-line" style="width:100%"></div>'
                for _ in range(5)
            )
            return mark_safe(
                f'<div class="{" ".join(wrapper_classes)}" role="grid"'
                f' aria-label="Data table" aria-busy="true"{wrapper_attrs_str}>'
                f'{toolbar_html}'
                f'{search_html}'
                f'<div class="data-table-loading skeleton-table">'
                f'{skeleton_rows}'
                f'</div>'
                f'</div>'
            )

        # --- Header cells ---
        has_filters = any(
            isinstance(col, dict) and col.get("filterable", False)
            for col in columns
        )
        header_cells = []
        filter_cells = []
        for col_idx, col in enumerate(columns):
            if isinstance(col, dict):
                key = conditional_escape(str(col.get("key", "")))
                col_label = conditional_escape(str(col.get("label", key)))
                sortable = col.get("sortable", True)
                filterable = col.get("filterable", False)
                filter_type = col.get("filter_type", "text")
                filter_options = col.get("filter_options", [])
                width = col.get("width", "")
            else:
                key = col_label = conditional_escape(str(col))
                sortable = True
                filterable = False
                filter_type = "text"
                filter_options = []
                width = ""

            # Frozen / pinned column class
            frozen_cls = ""
            pinned = col.get("pinned", "") if isinstance(col, dict) else ""
            if pinned == "left":
                frozen_cls = " data-table-pinned-left"
            elif pinned == "right":
                frozen_cls = " data-table-pinned-right"
            elif frozen_left > 0 and col_idx < frozen_left:
                frozen_cls = " data-table-frozen-left"
            elif frozen_right > 0 and col_idx >= (num_cols - frozen_right):
                frozen_cls = " data-table-frozen-right"

            # Width style
            width_attr = f' style="width:{conditional_escape(width)}"' if width else ""

            # Resize / reorder attributes
            extra_attrs = ""
            if resizable:
                extra_attrs += ' data-resizable="true"'
            if reorderable:
                extra_attrs += f' draggable="true" data-col-key="{key}"'
            elif column_visibility:
                extra_attrs += f' data-col-key="{key}"'

            # Sort state
            if sortable:
                active = " active" if key == sort_by else ""
                if key == sort_by:
                    arrow = " &#8595;" if sort_desc else " &#8593;"
                    aria_sort = "descending" if sort_desc else "ascending"
                else:
                    arrow = ""
                    aria_sort = "none"
                header_cells.append(
                    f'<th class="sortable{active}{frozen_cls}" role="columnheader"'
                    f' aria-sort="{aria_sort}"'
                    f' dj-click="{sort_event}" data-value="{key}"{width_attr}{extra_attrs}>'
                    f'{col_label}{arrow}</th>'
                )
            else:
                header_cells.append(
                    f'<th class="{frozen_cls.strip()}" role="columnheader"{width_attr}{extra_attrs}>'
                    f'{col_label}</th>'
                )

            # Filter cell
            if has_filters:
                frozen_f = f' class="{frozen_cls.strip()}"' if frozen_cls else ""
                if filterable:
                    filter_val = conditional_escape(str(filters.get(key, "")))
                    if filter_type == "select":
                        opts_html = '<option value="">All</option>'
                        for opt in filter_options:
                            if isinstance(opt, dict):
                                opt_val = conditional_escape(str(opt.get("value", "")))
                                opt_label = conditional_escape(str(opt.get("label", opt_val)))
                            else:
                                opt_val = opt_label = conditional_escape(str(opt))
                            selected = " selected" if opt_val == filter_val else ""
                            opts_html += f'<option value="{opt_val}"{selected}>{opt_label}</option>'
                        filter_cells.append(
                            f'<th{frozen_f}><select class="data-table-filter"'
                            f' aria-label="Filter {col_label}"'
                            f' dj-input="{filter_event}" data-column="{key}">'
                            f'{opts_html}'
                            f'</select></th>'
                        )
                    else:
                        filter_cells.append(
                            f'<th{frozen_f}><input type="text" class="data-table-filter"'
                            f' aria-label="Filter {col_label}"'
                            f' placeholder="Filter..."'
                            f' value="{filter_val}"'
                            f' dj-input="{filter_event}" data-column="{key}">'
                            f'</th>'
                        )
                else:
                    filter_cells.append(f"<th{frozen_f}></th>")

        # Prepend expand column
        if expandable:
            header_cells.insert(0, '<th class="data-table-expand-col" role="columnheader"></th>')
            if has_filters:
                filter_cells.insert(0, "<th></th>")

        # Prepend selection column
        if selectable:
            header_cells.insert(0,
                f'<th><input type="checkbox" class="data-table-select-all"'
                f' aria-label="Select all rows"'
                f' dj-click="{select_event}" data-value="__all__"></th>'
            )
            if has_filters:
                filter_cells.insert(0, "<th></th>")

        # Append actions column header for editable rows
        if editable_rows:
            header_cells.append('<th role="columnheader">Actions</th>')
            if has_filters:
                filter_cells.append("<th></th>")

        # --- Header rows ---
        thead_rows = f"<tr>{''.join(header_cells)}</tr>"
        if has_filters:
            thead_rows += f"<tr>{''.join(filter_cells)}</tr>"

        # --- Total columns (for colspan calculations) ---
        total_cols = num_cols + (1 if selectable else 0) + (1 if editable_rows else 0) + (1 if expandable else 0)

        # --- Helper: render a single row ---
        def _render_row(row):
            if not isinstance(row, dict):
                return ""
            row_id = str(row.get(row_key, ""))
            is_selected = row_id in selected_set
            is_editing = row_id in editing_row_set
            is_expanded = row_id in expanded_set
            row_attrs = ""
            row_classes = []

            if is_editing:
                row_classes.append("data-table-row-editing")
            if is_expanded:
                row_classes.append("data-table-row-expanded")
            row_attrs += f' data-row-key="{conditional_escape(row_id)}"'

            cells = ""
            # Expand toggle cell
            if expandable:
                exp_icon = "&#9660;" if is_expanded else "&#9654;"
                cells += (
                    f'<td class="data-table-expand-toggle">'
                    f'<button type="button" class="data-table-expand-btn"'
                    f' aria-label="Expand row" aria-expanded="{"true" if is_expanded else "false"}"'
                    f' dj-click="{expand_event}"'
                    f' data-value="{conditional_escape(row_id)}">{exp_icon}</button>'
                    f'</td>'
                )

            if selectable:
                checked = " checked" if is_selected else ""
                cells += (
                    f'<td><input type="checkbox" class="data-table-checkbox"'
                    f' aria-label="Select row"'
                    f'{checked}'
                    f' dj-click="{select_event}"'
                    f' data-value="{conditional_escape(row_id)}"></td>'
                )

            for col_idx, col in enumerate(columns):
                col_k = col.get("key", col) if isinstance(col, dict) else col
                col_k_str = str(col_k)
                cell_val = conditional_escape(str(row.get(col_k_str, "")))
                col_label_for_card = ""
                if responsive_cards and isinstance(col, dict):
                    col_label_for_card = conditional_escape(str(col.get("label", col_k_str)))

                # Frozen / pinned class for td
                td_classes = []
                if isinstance(col, dict) and col.get("pinned") == "left":
                    td_classes.append("data-table-pinned-left")
                elif isinstance(col, dict) and col.get("pinned") == "right":
                    td_classes.append("data-table-pinned-right")
                elif frozen_left > 0 and col_idx < frozen_left:
                    td_classes.append("data-table-frozen-left")
                elif frozen_right > 0 and col_idx >= (num_cols - frozen_right):
                    td_classes.append("data-table-frozen-right")

                td_cls_str = f' class="{" ".join(td_classes)}"' if td_classes else ""

                # Responsive card data-label
                label_attr = f' data-label="{col_label_for_card}"' if responsive_cards and col_label_for_card else ""

                # Cell renderer
                cell_template = col.get("cell_template", "") if isinstance(col, dict) else ""
                if cell_template:
                    cell_tpl_esc = conditional_escape(str(cell_template))
                    cell_val = (
                        f'<span class="cell-renderer cell-renderer-{cell_tpl_esc}"'
                        f' data-value="{cell_val}">{cell_val}</span>'
                    )

                # Editable cell (inline editing)
                is_col_editable = col_k_str in editable_col_set

                # Editable row mode: all cells become inputs when row is editing
                if editable_rows and is_editing:
                    raw_val = conditional_escape(str(row.get(col_k_str, "")))
                    cells += (
                        f'<td{td_cls_str}{label_attr}>'
                        f'<input type="text" value="{raw_val}"'
                        f' name="{conditional_escape(col_k_str)}"'
                        f' aria-label="Edit {conditional_escape(col_k_str)}">'
                        f'</td>'
                    )
                elif is_col_editable:
                    cells += (
                        f'<td data-editable="true"'
                        f' data-col-key="{conditional_escape(col_k_str)}"'
                        f'{td_cls_str}{label_attr}>'
                        f'{cell_val}</td>'
                    )
                else:
                    cells += f"<td{td_cls_str}{label_attr}>{cell_val}</td>"

            # Actions column for editable rows
            if editable_rows:
                if is_editing:
                    cells += (
                        f'<td class="data-table-row-actions">'
                        f'<button class="save-btn"'
                        f' dj-click="{save_row_event}"'
                        f' data-value="{conditional_escape(row_id)}">Save</button>'
                        f' <button class="cancel-btn"'
                        f' dj-click="{cancel_row_event}"'
                        f' data-value="{conditional_escape(row_id)}">Cancel</button>'
                        f'</td>'
                    )
                else:
                    cells += (
                        f'<td class="data-table-row-actions">'
                        f'<button dj-click="{edit_row_event}"'
                        f' data-value="{conditional_escape(row_id)}">Edit</button>'
                        f'</td>'
                    )

            # Row element
            result = ""
            if selectable:
                sel_attr = "true" if is_selected else "false"
                row_cls = f' class="{" ".join(row_classes)}"' if row_classes else ""
                result += f'<tr aria-selected="{sel_attr}"{row_cls}{row_attrs}>{cells}</tr>'
            else:
                row_cls = f' class="{" ".join(row_classes)}"' if row_classes else ""
                result += f"<tr{row_cls}{row_attrs}>{cells}</tr>"

            # Expansion detail row
            if expandable and is_expanded:
                result += (
                    f'<tr class="data-table-detail-row">'
                    f'<td colspan="{total_cols}" class="data-table-detail-cell">'
                    f'<div class="data-table-detail-content"'
                    f' data-row-key="{conditional_escape(row_id)}"></div>'
                    f'</td></tr>'
                )

            return result

        # --- Body rows ---
        body_rows = []
        if rows:
            if group_by:
                # Group rows by column value
                groups = {}
                group_order = []
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    val = str(row.get(group_by, ""))
                    if val not in groups:
                        groups[val] = []
                        group_order.append(val)
                    groups[val].append(row)

                for gval in group_order:
                    g_esc = conditional_escape(gval)
                    is_collapsed = gval in collapsed_group_set
                    toggle_attr = ""
                    if collapsible_groups:
                        toggle_attr = (
                            f' dj-click="{group_toggle_event}"'
                            f' data-value="{g_esc}"'
                        )
                    collapse_icon = "&#9654;" if is_collapsed else "&#9660;"
                    group_cls = "data-table-group-header"
                    if is_collapsed:
                        group_cls += " data-table-group-collapsed"
                    body_rows.append(
                        f'<tr class="{group_cls}">'
                        f'<td colspan="{total_cols}" class="data-table-group-cell">'
                        f'<button type="button" class="data-table-group-toggle"'
                        f'{toggle_attr}>{collapse_icon}</button>'
                        f' <span class="data-table-group-label">{g_esc}</span>'
                        f' <span class="data-table-group-count">({len(groups[gval])})</span>'
                        f'</td></tr>'
                    )
                    if not is_collapsed:
                        for row in groups[gval]:
                            body_rows.append(_render_row(row))
            else:
                for row in rows:
                    body_rows.append(_render_row(row))
            tbody_html = "".join(body_rows)
        else:
            # Empty state
            col_span = total_cols
            icon_html = f'<div class="data-table-empty-icon">{empty_icon}</div>' if empty_icon else ""
            desc_html = f'<p class="data-table-empty-description">{empty_description}</p>' if empty_description else ""
            tbody_html = (
                f'<tr><td colspan="{col_span}">'
                f'<div class="data-table-empty" role="status">'
                f'{icon_html}'
                f'<h3 class="data-table-empty-title">{empty_title}</h3>'
                f'{desc_html}'
                f'</div>'
                f'</td></tr>'
            )

        # --- Stats footer ---
        tfoot_html = ""
        has_stats = any(
            isinstance(col, dict) and col.get("stats", False)
            for col in columns
        )
        if has_stats and column_stats:
            stat_cells = []
            if expandable:
                stat_cells.append("<td></td>")
            if selectable:
                stat_cells.append("<td></td>")
            for col in columns:
                if isinstance(col, dict) and col.get("stats", False):
                    key = col.get("key", "")
                    s = column_stats.get(key, {})
                    if s and s.get("count", 0) > 0:
                        stat_cells.append(
                            f'<td class="data-table-stats-cell">'
                            f'<span class="data-table-stat" title="Min">{s.get("min", "")}</span>'
                            f'<span class="data-table-stat" title="Max">{s.get("max", "")}</span>'
                            f'<span class="data-table-stat" title="Avg">{s.get("avg", "")}</span>'
                            f'</td>'
                        )
                    else:
                        stat_cells.append('<td class="data-table-stats-cell">-</td>')
                else:
                    stat_cells.append("<td></td>")
            if editable_rows:
                stat_cells.append("<td></td>")
            tfoot_html = f'<tfoot><tr class="data-table-stats-row">{"".join(stat_cells)}</tr></tfoot>'

        # --- Pagination ---
        pagination_html = ""
        if paginate and total_pages > 1:
            prev_disabled = " disabled" if page <= 1 else ""
            next_disabled = " disabled" if page >= total_pages else ""
            prev_page = max(1, page - 1)
            next_page = min(total_pages, page + 1)
            pagination_html = (
                f'<div class="data-table-pagination" role="navigation"'
                f' aria-label="Table pagination">'
                f'<button class="pagination-btn"{prev_disabled}'
                f' dj-click="{page_event}" data-value="{prev_page}">&#8592;</button>'
                f'<span class="pagination-info">Page {page} of {total_pages}</span>'
                f'<button class="pagination-btn"{next_disabled}'
                f' dj-click="{page_event}" data-value="{next_page}">&#8594;</button>'
                f'</div>'
            )

        # --- Hidden triggers for JS events ---
        triggers_html = ""
        if reorderable:
            triggers_html += (
                f'<button class="data-table-reorder-trigger" style="display:none"'
                f' dj-click="{reorder_event}"></button>'
            )
        if editable_columns:
            triggers_html += (
                f'<button class="data-table-edit-trigger" style="display:none"'
                f' dj-click="{edit_event}"></button>'
            )
        if column_visibility:
            triggers_html += (
                f'<button class="data-table-visibility-trigger" style="display:none"'
                f' dj-click="{visibility_event}"></button>'
            )

        # --- Scrollable wrapper for frozen columns ---
        scroll_open = ""
        scroll_close = ""
        if frozen_left > 0 or frozen_right > 0:
            scroll_open = '<div class="data-table-scroll">'
            scroll_close = '</div>'

        # --- Facet counts display (appended to filter cells) ---
        # Facets are shown as counts next to filter options — handled via facet_counts data attr
        facet_attr = ""
        if facets and facet_counts:
            import json as _json
            facet_attr = f' data-facet-counts=\'{conditional_escape(_json.dumps(facet_counts))}\''

        return mark_safe(
            f'<div class="{" ".join(wrapper_classes)}" role="grid"'
            f' aria-label="Data table"{wrapper_attrs_str}{facet_attr}>'
            f'{toolbar_html}'
            f'{bulk_actions_html}'
            f'{search_html}'
            f'{scroll_open}'
            f'<table class="{table_cls}">'
            f"<thead>{thead_rows}</thead>"
            f"<tbody>{tbody_html}</tbody>"
            f"{tfoot_html}"
            f"</table>"
            f'{scroll_close}'
            f'{pagination_html}'
            f'{triggers_html}'
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
        highlight = kwargs.get("highlight", True)
        theme = kwargs.get("theme", "github-dark")
        return str(_cb(code=code, language=language, filename=filename,
                       highlight=highlight, theme=theme))


class ComboboxHandler:
    def render(self, args, context):
        from djust_components.templatetags.djust_components import combobox as _cb
        kwargs = _parse_args(args, context)
        options_val = kwargs.get("options", "")
        if isinstance(options_val, list):
            options = options_val
        else:
            options = context.get(options_val, [])
        selected_val = kwargs.get("selected", None)
        if isinstance(selected_val, str) and selected_val:
            selected_val = context.get(selected_val, [])
        return str(_cb(
            name=kwargs.get("name", ""),
            label=kwargs.get("label", ""),
            value=kwargs.get("value", ""),
            placeholder=kwargs.get("placeholder", "Search…"),
            options=options,
            event=kwargs.get("event", ""),
            search_event=kwargs.get("search_event", ""),
            multiple=kwargs.get("multiple", False),
            selected=selected_val,
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
        return mark_safe(
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
        return mark_safe(
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
        return mark_safe(
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
        return mark_safe(
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
        return mark_safe(
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
            range=kwargs.get("range", False),
            range_start=kwargs.get("range_start", ""),
            range_end=kwargs.get("range_end", ""),
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
        import json as _json
        from djust_components.templatetags.djust_components import virtual_list as _vl
        kwargs = _parse_args(args, context)
        items_val = kwargs.get("items", "vl_items")
        if isinstance(items_val, list):
            items = items_val
        elif isinstance(items_val, str):
            # Could be a context variable name or an already-resolved JSON string
            if items_val in context:
                items = context[items_val]
            else:
                items = items_val
            # If still a string, try JSON deserialization
            if isinstance(items, str):
                try:
                    items = _json.loads(items)
                except (ValueError, TypeError):
                    items = []
        else:
            items = []
        return str(_vl(
            items=items,
            total=kwargs.get("total", len(items) if items else 0),
            page=kwargs.get("page", 1),
            page_size=kwargs.get("page_size", 20),
            load_more_event=kwargs.get("load_more_event", "load_more"),
        ))


class KanbanBoardHandler:
    def render(self, args, context):
        import json as _json
        from djust_components.templatetags.djust_components import kanban_board as _kb
        kwargs = _parse_args(args, context)
        cols_val = kwargs.get("columns", "kanban_columns")
        if isinstance(cols_val, list):
            columns = cols_val
        elif isinstance(cols_val, str):
            if cols_val in context:
                columns = context[cols_val]
            else:
                columns = cols_val
            if isinstance(columns, str):
                try:
                    columns = _json.loads(columns)
                except (ValueError, TypeError):
                    columns = []
        else:
            columns = []
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
            event=kwargs.get("event", ""),
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
        return mark_safe(
            f'<div class="split-pane split-pane-{ce(direction)}" id="{uid}">'
            f'{content}'
            f'</div>'
        )


BLOCK_HANDLERS.extend([
    ("split_pane", "endsplit_pane", SplitPaneHandler()),
])


# ===========================================================================
# FORM INPUT COMPONENTS (v0.4)
# ===========================================================================


class MultiSelectHandler:
    """Inline handler for {% multi_select name="tags" options=opts %}"""
    def render(self, args, context):
        from djust_components.templatetags.djust_components import multi_select as _ms
        kwargs = _parse_args(args, context)
        return str(_ms(
            name=kwargs.get("name", ""),
            label=kwargs.get("label", ""),
            options=kwargs.get("options"),
            selected=kwargs.get("selected"),
            event=kwargs.get("event", ""),
            placeholder=kwargs.get("placeholder", "Search..."),
            disabled=kwargs.get("disabled", False),
        ))


class OtpInputHandler:
    """Inline handler for {% otp_input name="code" digits=6 %}"""
    def render(self, args, context):
        from djust_components.templatetags.djust_components import otp_input as _oi
        kwargs = _parse_args(args, context)
        return str(_oi(
            name=kwargs.get("name", ""),
            digits=kwargs.get("digits", 6),
            event=kwargs.get("event", ""),
            label=kwargs.get("label", ""),
            disabled=kwargs.get("disabled", False),
        ))


class NumberStepperHandler:
    """Inline handler for {% number_stepper name="qty" min=1 max=99 %}"""
    def render(self, args, context):
        from djust_components.templatetags.djust_components import number_stepper as _ns
        kwargs = _parse_args(args, context)
        return str(_ns(
            name=kwargs.get("name", ""),
            value=kwargs.get("value", 0),
            min_val=kwargs.get("min_val") or kwargs.get("min"),
            max_val=kwargs.get("max_val") or kwargs.get("max"),
            step=kwargs.get("step", 1),
            event=kwargs.get("event", ""),
            label=kwargs.get("label", ""),
            disabled=kwargs.get("disabled", False),
        ))


class TagInputHandler:
    """Inline handler for {% tag_input name="tags" suggestions=tags %}"""
    def render(self, args, context):
        from djust_components.templatetags.djust_components import tag_input as _ti
        kwargs = _parse_args(args, context)
        return str(_ti(
            name=kwargs.get("name", ""),
            tags=kwargs.get("tags"),
            suggestions=kwargs.get("suggestions"),
            event=kwargs.get("event", ""),
            placeholder=kwargs.get("placeholder", "Add tag..."),
            disabled=kwargs.get("disabled", False),
            label=kwargs.get("label", ""),
        ))


class InputGroupHandler:
    """Block handler for {% input_group %}...{% endinput_group %}"""
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        size = kw.get("size", "md")
        error = kw.get("error", "")
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


class InputAddonHandler:
    """Block handler for {% input_addon %}...{% endinput_addon %}"""
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        position = kw.get("position", "prefix")
        return mark_safe(
            f'<span class="input-addon input-addon-{conditional_escape(position)}">'
            f'{content}'
            f'</span>'
        )


class DjLabelHandler:
    """Block handler for {% dj_label for="email" %}Email{% enddj_label %}"""
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        for_input = kw.get("for", "")
        required = kw.get("required", False)
        extra_class = kw.get("class", "")
        for_attr = f' for="{conditional_escape(for_input)}"' if for_input else ""
        required_span = ' <span class="form-required">*</span>' if required else ""
        cls = f"form-label {conditional_escape(extra_class)}".strip()
        return mark_safe(
            f'<label class="{cls}"{for_attr}>'
            f'{content}{required_span}'
            f'</label>'
        )


class FieldsetHandler:
    """Block handler for {% fieldset legend="Account" %}...{% endfieldset %}"""
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        legend = kw.get("legend", "")
        disabled = kw.get("disabled", False)
        extra_class = kw.get("class", "")
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


# Register form input inline handlers
INLINE_HANDLERS.extend([
    ("multi_select", MultiSelectHandler()),
    ("otp_input", OtpInputHandler()),
    ("number_stepper", NumberStepperHandler()),
    ("tag_input", TagInputHandler()),
])

# Register form input block handlers
BLOCK_HANDLERS.extend([
    ("input_group", "endinput_group", InputGroupHandler()),
    ("input_addon", "endinput_addon", InputAddonHandler()),
    ("dj_label", "enddj_label", DjLabelHandler()),
    ("fieldset", "endfieldset", FieldsetHandler()),
])


# ===========================================================================
# BUTTON & CONTROL VARIANT HANDLERS
# ===========================================================================


class ToggleGroupHandler:
    """Inline handler for {% toggle_group name=... options=... value=... %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        name = conditional_escape(kw.get("name", ""))
        options = kw.get("options", [])
        if not isinstance(options, (list, tuple)):
            options = []
        value = kw.get("value", "")
        # In multi mode, value can be a list
        mode = kw.get("mode", "single")
        event = conditional_escape(kw.get("event", "toggle_select"))
        disabled = kw.get("disabled", False)
        size = kw.get("size", "md")

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

            # Determine if this option is active
            if mode == "multi" and isinstance(value, (list, tuple)):
                is_active = opt.get("value", "") in value
            else:
                is_active = str(opt.get("value", "")) == str(value)

            active_cls = " toggle-group-btn--active" if is_active else ""
            aria_pressed = "true" if is_active else "false"
            disabled_attr = " disabled" if disabled else ""
            click_attr = "" if disabled else f' dj-click="{event}" data-value="{opt_value}"'

            icon_html = ""
            if opt_icon:
                icon_html = f'<span class="toggle-group-icon">{conditional_escape(str(opt_icon))}</span>'

            buttons.append(
                f'<button class="toggle-group-btn{active_cls}" '
                f'aria-pressed="{aria_pressed}" '
                f'data-name="{name}"{click_attr}{disabled_attr}>'
                f'{icon_html}'
                f'<span class="toggle-group-label">{opt_label}</span>'
                f'</button>'
            )

        return mark_safe(
            f'<div class="toggle-group{size_cls}{disabled_cls}" '
            f'role="group" data-mode="{conditional_escape(mode)}">'
            f'{"".join(buttons)}'
            f'</div>'
        )


class FabHandler:
    """Inline handler for {% fab icon=... event=... position=... %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        icon = conditional_escape(kw.get("icon", "+"))
        event = conditional_escape(kw.get("event", ""))
        position = kw.get("position", "bottom-right")
        label = conditional_escape(kw.get("label", ""))
        size = kw.get("size", "md")
        variant = kw.get("variant", "primary")
        disabled = kw.get("disabled", False)
        actions = kw.get("actions", [])
        if not isinstance(actions, (list, tuple)):
            actions = []

        valid_positions = ("bottom-right", "bottom-left", "top-right", "top-left")
        pos_cls = position if position in valid_positions else "bottom-right"
        pos_cls = conditional_escape(pos_cls)

        size_cls = ""
        if size and size != "md":
            size_cls = f" fab-{conditional_escape(size)}"
        variant_cls = f" fab-{conditional_escape(variant)}"
        disabled_attr = " disabled" if disabled else ""
        click_attr = "" if disabled or not event else f' dj-click="{event}"'
        aria_label = f' aria-label="{label}"' if label else ""

        # Speed-dial sub-actions
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
            f'<span class="fab-icon">{icon}</span>'
            f'</button>'
            f'</div>'
        )


class SplitButtonHandler:
    """Inline handler for {% split_button label=... event=... options=... %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        label = conditional_escape(kw.get("label", ""))
        event = conditional_escape(kw.get("event", ""))
        options = kw.get("options", [])
        if not isinstance(options, (list, tuple)):
            options = []
        variant = kw.get("variant", "primary")
        size = kw.get("size", "md")
        disabled = kw.get("disabled", False)
        loading = kw.get("loading", False)
        is_open = kw.get("open", False)
        toggle_event = conditional_escape(kw.get("toggle_event", "toggle_split_menu"))

        variant_cls = f" split-btn-{conditional_escape(variant)}"
        size_cls = ""
        if size and size != "md":
            size_cls = f" split-btn-{conditional_escape(size)}"
        loading_cls = " split-btn-loading" if loading else ""
        disabled_attr = " disabled" if disabled or loading else ""
        click_attr = "" if disabled or loading or not event else f' dj-click="{event}"'

        spinner_html = '<span class="split-btn-spinner"></span>' if loading else ""

        # Build option items
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

        open_data = "true" if is_open else "false"
        toggle_disabled = " disabled" if disabled or loading else ""
        toggle_click = "" if disabled or loading else f' dj-click="{toggle_event}"'

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
            f'<span class="split-btn-label">{label}</span>'
            f'</button>'
            f'<button class="split-btn-toggle"{toggle_click}{toggle_disabled}>'
            f'<span class="split-btn-caret">&#9662;</span>'
            f'</button>'
            f'{menu_html}'
            f'</div>'
        )


# Register button & control variant inline handlers
INLINE_HANDLERS.extend([
    ("toggle_group", ToggleGroupHandler()),
    ("fab", FabHandler()),
    ("split_button", SplitButtonHandler()),
])


# ===========================================================================
# STATUS / PROGRESS INDICATOR HANDLERS
# ===========================================================================

class NotificationBadgeHandler:
    """Inline handler for {% notification_badge count=5 %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
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
        size = conditional_escape(kw.get("size", "md"))

        cls = f"dj-notification-badge dj-notification-badge--{size}"
        if pulse:
            cls += " dj-notification-badge--pulse"

        if dot:
            return mark_safe(f'<span class="{cls} dj-notification-badge--dot"></span>')

        if count <= 0:
            return ""

        display = f"{max_count}+" if count > max_count else str(count)
        return mark_safe(f'<span class="{cls}">{display}</span>')


class SegmentedProgressHandler:
    """Inline handler for {% segmented_progress steps=steps current=2 %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        steps = kw.get("steps", [])
        if not isinstance(steps, (list, tuple)):
            steps = []
        try:
            current = int(kw.get("current", 0))
        except (ValueError, TypeError):
            current = 0
        size = conditional_escape(kw.get("size", "md"))

        cls = f"dj-segmented-progress dj-segmented-progress--{size}"

        segments = []
        for i, step in enumerate(steps):
            if isinstance(step, dict):
                label = conditional_escape(str(step.get("label", "")))
            else:
                label = conditional_escape(str(step))
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

        parts = []
        for i, seg in enumerate(segments):
            parts.append(seg)
            if i < len(segments) - 1:
                step_num = i + 1
                line_state = "completed" if step_num < current else "pending"
                parts.append(
                    f'<div class="dj-segmented-progress__connector '
                    f'dj-segmented-progress__connector--{line_state}"></div>'
                )

        return mark_safe(f'<div class="{cls}">{"".join(parts)}</div>')


class ProgressCircleHandler:
    """Inline handler for {% progress_circle value=65 size="md" %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        try:
            value = max(0, min(100, int(kw.get("value", 0))))
        except (ValueError, TypeError):
            value = 0
        size = str(kw.get("size", "md"))
        color = conditional_escape(kw.get("color", "primary"))
        show_value = kw.get("show_value", True)

        sizes = {"sm": 48, "md": 80, "lg": 120}
        dim = sizes.get(size, 80)
        stroke_widths = {"sm": 4, "md": 6, "lg": 8}
        stroke_w = stroke_widths.get(size, 6)

        radius = (dim - stroke_w) / 2
        circumference = 2 * 3.14159265 * radius
        dash_offset = circumference * (1 - value / 100)

        e_size = conditional_escape(size)
        cls = f"dj-progress-circle dj-progress-circle--{e_size} dj-progress-circle--{color}"

        value_html = ""
        if show_value:
            font_sizes = {"sm": "0.625rem", "md": "1rem", "lg": "1.5rem"}
            fs = font_sizes.get(size, "1rem")
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


class StatusIndicatorHandler:
    """Inline handler for {% status_indicator status="online" label="API" %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        status = str(kw.get("status", "offline"))
        label = kw.get("label", "")
        pulse = kw.get("pulse", False)
        size = conditional_escape(kw.get("size", "md"))

        e_status = conditional_escape(status)
        e_label = conditional_escape(str(label))

        status_colors = {
            "online": "green",
            "degraded": "yellow",
            "offline": "red",
            "maintenance": "blue",
        }
        color = status_colors.get(status, "gray")

        cls = f"dj-status-indicator dj-status-indicator--{size} dj-status-indicator--{color}"
        if pulse:
            cls += " dj-status-indicator--pulse"

        dot_html = '<span class="dj-status-indicator__dot"></span>'
        label_html = f'<span class="dj-status-indicator__label">{e_label}</span>' if label else ""

        return mark_safe(f'<span class="{cls}">{dot_html}{label_html}</span>')


# Register status/progress indicator inline handlers
INLINE_HANDLERS.extend([
    ("notification_badge", NotificationBadgeHandler()),
    ("segmented_progress", SegmentedProgressHandler()),
    ("progress_circle", ProgressCircleHandler()),
    ("status_indicator", StatusIndicatorHandler()),
])


# ===========================================================================
# OVERLAY / FEEDBACK HANDLERS
# ===========================================================================

class LoadingOverlayHandler:
    """Block handler for {% loading_overlay active=... %}...{% endloading_overlay %}"""
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        active = kw.get("active", False)
        text = kw.get("text", "")
        spinner_size = kw.get("spinner_size", "md")
        custom_class = kw.get("custom_class", "")

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


class AnnouncementBarHandler:
    """Block handler for {% announcement_bar type=... %}...{% endannouncement_bar %}"""
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        bar_type = kw.get("type", "info")
        dismissible = kw.get("dismissible", False)
        dismiss_event = kw.get("dismiss_event", "dismiss_announcement")
        custom_class = kw.get("custom_class", "")

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


# Register overlay/feedback handlers
BLOCK_HANDLERS.extend([
    ("loading_overlay", "endloading_overlay", LoadingOverlayHandler()),
    ("announcement_bar", "endannouncement_bar", AnnouncementBarHandler()),
])


# ===========================================================================
# RICH SELECT & DATA GRID HANDLERS
# ===========================================================================


class RichSelectHandler:
    """Inline handler for {% rich_select name=... options=... %}"""
    def render(self, args, context):
        from djust_components.templatetags.djust_components import rich_select as _rs
        kwargs = _parse_args(args, context)
        return str(_rs(
            name=kwargs.get("name", ""),
            options=kwargs.get("options"),
            value=kwargs.get("value", ""),
            event=kwargs.get("event", ""),
            placeholder=kwargs.get("placeholder", "Select..."),
            disabled=kwargs.get("disabled", False),
            searchable=kwargs.get("searchable", False),
            label=kwargs.get("label", ""),
        ))


class DataGridHandler:
    """Inline handler for {% data_grid columns=cols rows=rows %}"""
    def render(self, args, context):
        from djust_components.templatetags.djust_components import data_grid as _dg
        kwargs = _parse_args(args, context)
        return str(_dg(
            columns=kwargs.get("columns"),
            rows=kwargs.get("rows"),
            row_key=kwargs.get("row_key", "id"),
            edit_event=kwargs.get("edit_event", "grid_cell_edit"),
            resizable=kwargs.get("resizable", True),
            frozen_left=kwargs.get("frozen_left", 0),
            frozen_right=kwargs.get("frozen_right", 0),
            striped=kwargs.get("striped", False),
            compact=kwargs.get("compact", False),
            keyboard_nav=kwargs.get("keyboard_nav", True),
            new_row_event=kwargs.get("new_row_event", ""),
            delete_row_event=kwargs.get("delete_row_event", ""),
            custom_class=kwargs.get("custom_class", ""),
        ))


INLINE_HANDLERS.extend([
    ("rich_select", RichSelectHandler()),
    ("data_grid", DataGridHandler()),
])


# ===========================================================================
# WEBSOCKET-POWERED COMPONENT HANDLERS
# ===========================================================================


class StreamingTextHandler:
    """Inline handler for {% streaming_text stream_event="stream_chunk" %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        stream_event = conditional_escape(str(kw.get("stream_event", "stream_chunk")))
        text = conditional_escape(str(kw.get("text", "")))
        markdown = kw.get("markdown", False)
        auto_scroll = kw.get("auto_scroll", True)
        cursor = kw.get("cursor", True)
        custom_class = conditional_escape(str(kw.get("custom_class", "")))

        cls = "dj-streaming-text"
        if cursor:
            cls += " dj-streaming-text--cursor"
        if custom_class:
            cls += f" {custom_class}"

        attrs = [
            f'class="{cls}"',
            f'data-stream-event="{stream_event}"',
        ]
        if auto_scroll:
            attrs.append('data-auto-scroll="true"')
        if markdown:
            attrs.append('data-markdown="true"')

        attrs_str = " ".join(attrs)
        return mark_safe(
            f'<div {attrs_str}>'
            f'<div class="dj-streaming-text__content">{text}</div>'
            f'</div>'
        )


class ConnectionStatusHandler:
    """Inline handler for {% connection_status %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        custom_class = conditional_escape(str(kw.get("custom_class", "")))
        reconnecting_text = conditional_escape(str(kw.get("reconnecting_text", "Reconnecting...")))
        connected_text = conditional_escape(str(kw.get("connected_text", "Reconnected")))

        cls = "dj-connection-status"
        if custom_class:
            cls += f" {custom_class}"

        return mark_safe(
            f'<div class="{cls}" '
            f'data-reconnecting-text="{reconnecting_text}" '
            f'data-connected-text="{connected_text}" '
            f'role="status" aria-live="polite" style="display:none">'
            f'<span class="dj-connection-status__text">{reconnecting_text}</span>'
            f'</div>'
        )


class LiveCounterHandler:
    """Inline handler for {% live_counter value=42 label="online" %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        try:
            value = int(kw.get("value", 0))
        except (ValueError, TypeError):
            value = 0
        label = conditional_escape(str(kw.get("label", "")))
        stream_event = conditional_escape(str(kw.get("stream_event", "counter_update")))
        custom_class = conditional_escape(str(kw.get("custom_class", "")))
        size = conditional_escape(str(kw.get("size", "md")))

        cls = f"dj-live-counter dj-live-counter--{size}"
        if custom_class:
            cls += f" {custom_class}"

        label_html = ""
        if label:
            label_html = f'<span class="dj-live-counter__label">{label}</span>'

        return mark_safe(
            f'<div class="{cls}" data-stream-event="{stream_event}">'
            f'<span class="dj-live-counter__value" data-value="{value}">{value}</span>'
            f'{label_html}'
            f'</div>'
        )


class ServerToastContainerHandler:
    """Inline handler for {% server_toast_container position="top-right" %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        position = conditional_escape(str(kw.get("position", "top-right")))
        custom_class = conditional_escape(str(kw.get("custom_class", "")))
        try:
            max_toasts = int(kw.get("max_toasts", 5))
        except (ValueError, TypeError):
            max_toasts = 5

        cls = f"dj-toast-container dj-toast-container--{position}"
        if custom_class:
            cls += f" {custom_class}"

        return mark_safe(
            f'<div class="{cls}" '
            f'data-max-toasts="{max_toasts}" '
            f'role="region" aria-live="polite" aria-label="Notifications">'
            f'</div>'
        )


class ScrollToTopHandler:
    """Inline handler for {% scroll_to_top threshold="300px" %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        threshold = conditional_escape(str(kw.get("threshold", "300px")))
        label = conditional_escape(str(kw.get("label", "Back to top")))
        custom_class = conditional_escape(str(kw.get("custom_class", "")))

        cls = "dj-scroll-to-top"
        if custom_class:
            cls += f" {custom_class}"

        return mark_safe(
            f'<button class="{cls}" '
            f'data-threshold="{threshold}" '
            f'aria-label="{label}" '
            f'title="{label}" '
            f'style="display:none">'
            f'<svg width="20" height="20" viewBox="0 0 20 20" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round">'
            f'<path d="M10 16V4M10 4l-6 6M10 4l6 6"/>'
            f'</svg>'
            f'</button>'
        )


class CodeSnippetHandler:
    """Inline handler for {% code_snippet language="bash" code="pip install djust" %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        code = conditional_escape(str(kw.get("code", "")))
        language = conditional_escape(str(kw.get("language", "")))
        custom_class = conditional_escape(str(kw.get("custom_class", "")))

        cls = "dj-code-snippet"
        if custom_class:
            cls += f" {custom_class}"

        lang_badge = ""
        if language:
            lang_badge = f'<span class="dj-code-snippet__lang">{language}</span>'

        return mark_safe(
            f'<div class="{cls}">'
            f'<div class="dj-code-snippet__header">'
            f'{lang_badge}'
            f'<button class="dj-code-snippet__copy" aria-label="Copy code" '
            f'type="button">Copy</button>'
            f'</div>'
            f'<pre class="dj-code-snippet__pre">'
            f'<code class="dj-code-snippet__code">{code}</code>'
            f'</pre>'
            f'</div>'
        )


class ResponsiveImageHandler:
    """Inline handler for {% responsive_image src=url alt="..." %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        src = conditional_escape(str(kw.get("src", "")))
        alt = conditional_escape(str(kw.get("alt", "")))
        aspect_ratio = conditional_escape(str(kw.get("aspect_ratio", "")))
        lazy = kw.get("lazy", True)
        srcset = conditional_escape(str(kw.get("srcset", "")))
        sizes = conditional_escape(str(kw.get("sizes", "")))
        placeholder = conditional_escape(str(kw.get("placeholder", "")))
        custom_class = conditional_escape(str(kw.get("custom_class", "")))

        if isinstance(lazy, str):
            lazy = lazy.lower() not in ("false", "0", "")

        cls = "dj-responsive-image"
        if placeholder:
            cls += " dj-responsive-image--blur-up"
        if custom_class:
            cls += f" {custom_class}"

        style = ""
        if aspect_ratio:
            style = f' style="aspect-ratio:{aspect_ratio}"'

        img_attrs = [f'src="{src}"', f'alt="{alt}"']
        if lazy:
            img_attrs.append('loading="lazy"')
        if srcset:
            img_attrs.append(f'srcset="{srcset}"')
        if sizes:
            img_attrs.append(f'sizes="{sizes}"')

        img_tag = f'<img {" ".join(img_attrs)} class="dj-responsive-image__img">'

        placeholder_html = ""
        if placeholder:
            placeholder_html = (
                f'<img src="{placeholder}" alt="" '
                f'class="dj-responsive-image__placeholder" aria-hidden="true">'
            )

        return mark_safe(
            f'<div class="{cls}"{style}>'
            f'{placeholder_html}'
            f'{img_tag}'
            f'</div>'
        )


class RelativeTimeHandler:
    """Inline handler for {% relative_time datetime=created_at %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        dt = kw.get("datetime", "")
        auto_update = kw.get("auto_update", True)
        interval = kw.get("interval", 60)
        custom_class = conditional_escape(str(kw.get("custom_class", "")))

        if isinstance(auto_update, str):
            auto_update = auto_update.lower() not in ("false", "0", "")

        cls = "dj-relative-time"
        if custom_class:
            cls += f" {custom_class}"

        iso_val = ""
        if dt:
            if hasattr(dt, "isoformat"):
                iso_val = dt.isoformat()
            else:
                iso_val = str(dt)

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


class CopyableTextHandler:
    """Block handler for {% copyable_text %}...{% endcopyable_text %}"""
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        copied_label = conditional_escape(str(kw.get("copied_label", "Copied!")))
        custom_class = conditional_escape(str(kw.get("custom_class", "")))

        e_content = conditional_escape(content.strip())

        cls = "dj-copyable-text"
        if custom_class:
            cls += f" {custom_class}"

        return mark_safe(
            f'<span class="{cls}" '
            f'data-copy-text="{e_content}" '
            f'data-copied-label="{copied_label}" '
            f'role="button" tabindex="0" '
            f'aria-label="Click to copy">'
            f'<span class="dj-copyable-text__value">{e_content}</span>'
            f'<span class="dj-copyable-text__tooltip" aria-hidden="true">{copied_label}</span>'
            f'</span>'
        )


INLINE_HANDLERS.extend([
    ("streaming_text", StreamingTextHandler()),
    ("connection_status", ConnectionStatusHandler()),
    ("live_counter", LiveCounterHandler()),
    ("server_toast_container", ServerToastContainerHandler()),
    ("scroll_to_top", ScrollToTopHandler()),
    ("code_snippet", CodeSnippetHandler()),
    ("responsive_image", ResponsiveImageHandler()),
    ("relative_time", RelativeTimeHandler()),
])

BLOCK_HANDLERS.extend([
    ("copyable_text", "endcopyable_text", CopyableTextHandler()),
])


# ===========================================================================
# ICON SYSTEM (#178) + THEME TOGGLE (#138)
# ===========================================================================

class IconHandler:
    """Inline handler for {% icon name="check" size="md" set="heroicons" %}"""
    def render(self, args, context):
        from djust_components.icons import render_icon
        kw = _parse_args(args, context)
        name = kw.get("name", "")
        size = kw.get("size", "md")
        icon_set = kw.get("set", "heroicons")
        custom_class = kw.get("custom_class", "")
        # Pass remaining kwargs as extra attrs
        extra = {k: v for k, v in kw.items()
                 if k not in ("name", "size", "set", "custom_class")}
        return str(render_icon(
            name=name, size=size, icon_set=icon_set,
            custom_class=custom_class, **extra,
        ))


class ThemeToggleHandler:
    """Inline handler for {% theme_toggle current="system" event="set_theme" %}"""
    def render(self, args, context):
        import uuid
        from djust_components.icons import render_icon
        kw = _parse_args(args, context)
        current = conditional_escape(kw.get("current", "system"))
        event = kw.get("event", "")
        custom_class = kw.get("custom_class", "")

        e_event = conditional_escape(event) if event else ""
        e_cls = conditional_escape(custom_class)

        cls = "dj-theme-toggle"
        if e_cls:
            cls += f" {e_cls}"

        click_attr = f' dj-click="{e_event}"' if e_event else ""
        sun_svg = render_icon("sun", size="sm")
        moon_svg = render_icon("moon", size="sm")
        monitor_svg = render_icon("computer-desktop", size="sm")
        toggle_id = f"dj-theme-toggle-{uuid.uuid4().hex[:8]}"

        return mark_safe(
            f'<div class="{cls}" id="{toggle_id}" '
            f'data-current="{current}"{click_attr} '
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


INLINE_HANDLERS.extend([
    ("icon", IconHandler()),
    ("theme_toggle", ThemeToggleHandler()),
])


# ===========================================================================
# PAGE HEADER HANDLER (#179)
# ===========================================================================

class PageHeaderActionsHandler:
    """Block handler for {% page_header_actions %}...{% endpage_header_actions %}"""
    def render(self, args, content, context):
        # Just wrap actions content in its container div
        return mark_safe(
            f'<div class="dj-page-header__actions">{content}</div>'
        )


class PageHeaderHandler:
    """Block handler for {% page_header title=... %}...{% endpage_header %}"""
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        title = kw.get("title", "")
        subtitle = kw.get("subtitle", "")
        description = kw.get("description", "")
        custom_class = kw.get("custom_class", "")

        e_title = conditional_escape(str(title))
        e_subtitle = conditional_escape(str(subtitle))
        e_description = conditional_escape(str(description))
        e_custom_class = conditional_escape(str(custom_class))

        cls = "dj-page-header"
        if e_custom_class:
            cls += f" {e_custom_class}"

        # In the Rust engine, nested block tags render inline.
        # page_header_actions renders its own wrapper div, so we need to
        # separate actions from breadcrumb content.
        actions_marker = '<div class="dj-page-header__actions">'
        actions_section = ""
        breadcrumb_content = content
        if actions_marker in content:
            idx = content.index(actions_marker)
            breadcrumb_content = content[:idx]
            actions_section = content[idx:]

        # Breadcrumb slot
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


BLOCK_HANDLERS.extend([
    ("page_header_actions", "endpage_header_actions", PageHeaderActionsHandler()),
    ("page_header", "endpage_header", PageHeaderHandler()),
])


# ===========================================================================
# FORM ESSENTIALS (v1.5)
# ===========================================================================


class SliderHandler:
    """Inline handler for {% slider name="price" min=0 max=100 value=50 %}"""

    def render(self, args, context):
        kw = _parse_args(args, context)
        name = conditional_escape(kw.get("name", ""))
        label = conditional_escape(kw.get("label", ""))
        min_val = int(kw.get("min", 0))
        max_val = int(kw.get("max", 100))
        step = int(kw.get("step", 1))
        value = kw.get("value", min_val)
        value_end = kw.get("value_end", None)
        event = conditional_escape(kw.get("event", name))
        disabled = kw.get("disabled", False)
        show_ticks = kw.get("show_ticks", False)
        show_value = kw.get("show_value", True)
        custom_class = conditional_escape(kw.get("custom_class", ""))

        disabled_attr = " disabled" if disabled else ""
        range_mode = value_end is not None
        cls = "dj-slider"
        if range_mode:
            cls += " dj-slider--range"
        if custom_class:
            cls += f" {custom_class}"

        label_html = (
            f'<label class="dj-slider__label" for="{name}">{label}</label>'
            if label else ""
        )

        value_display = ""
        if show_value:
            if range_mode:
                value_display = (
                    f'<output class="dj-slider__value">'
                    f'{conditional_escape(str(value))} &ndash; '
                    f'{conditional_escape(str(value_end))}'
                    f'</output>'
                )
            else:
                value_display = (
                    f'<output class="dj-slider__value">'
                    f'{conditional_escape(str(value))}'
                    f'</output>'
                )

        ticks_html = ""
        if show_ticks:
            tick_count = max(1, (max_val - min_val) // step)
            tick_items = "".join(
                f'<span class="dj-slider__tick"></span>'
                for _ in range(tick_count + 1)
            )
            ticks_html = f'<div class="dj-slider__ticks">{tick_items}</div>'

        input_html = (
            f'<input type="range" class="dj-slider__input" '
            f'name="{name}" id="{name}" '
            f'min="{min_val}" max="{max_val}" step="{step}" '
            f'value="{conditional_escape(str(value))}" '
            f'dj-input="{event}"{disabled_attr}>'
        )

        if range_mode:
            input_html += (
                f'<input type="range" class="dj-slider__input dj-slider__input--end" '
                f'name="{name}_end" id="{name}_end" '
                f'min="{min_val}" max="{max_val}" step="{step}" '
                f'value="{conditional_escape(str(value_end))}" '
                f'dj-input="{event}"{disabled_attr}>'
            )

        return mark_safe(
            f'<div class="{cls}">'
            f'{label_html}'
            f'<div class="dj-slider__track">{input_html}</div>'
            f'{ticks_html}'
            f'{value_display}'
            f'</div>'
        )


class SearchInputHandler:
    """Inline handler for {% search_input name="q" placeholder="Search..." %}"""

    def render(self, args, context):
        kw = _parse_args(args, context)
        name = conditional_escape(kw.get("name", ""))
        label = conditional_escape(kw.get("label", ""))
        value = conditional_escape(str(kw.get("value", "")))
        placeholder = conditional_escape(kw.get("placeholder", "Search..."))
        event = conditional_escape(kw.get("event", name))
        debounce = int(kw.get("debounce", 300))
        loading = kw.get("loading", False)
        disabled = kw.get("disabled", False)
        custom_class = conditional_escape(kw.get("custom_class", ""))

        disabled_attr = " disabled" if disabled else ""
        cls = "dj-search-input"
        if loading:
            cls += " dj-search-input--loading"
        if custom_class:
            cls += f" {custom_class}"

        label_html = (
            f'<label class="dj-search-input__label" for="{name}">{label}</label>'
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
            f'name="{name}" id="{name}" value="{value}" '
            f'placeholder="{placeholder}" autocomplete="off" '
            f'dj-input="{event}" data-debounce="{debounce}"{disabled_attr}>'
            f'{clear_html}'
            f'{spinner_html}'
            f'</div>'
        )


class PasswordInputHandler:
    """Inline handler for {% password_input name="pwd" %}"""

    def render(self, args, context):
        kw = _parse_args(args, context)
        name = conditional_escape(kw.get("name", ""))
        label = conditional_escape(kw.get("label", ""))
        value = conditional_escape(str(kw.get("value", "")))
        placeholder = conditional_escape(kw.get("placeholder", ""))
        event = conditional_escape(kw.get("event", name))
        error = conditional_escape(kw.get("error", ""))
        required = kw.get("required", False)
        disabled = kw.get("disabled", False)
        show_strength = kw.get("show_strength", False)
        strength = int(kw.get("strength", 0))
        custom_class = conditional_escape(kw.get("custom_class", ""))

        required_attr = " required" if required else ""
        disabled_attr = " disabled" if disabled else ""
        cls = "dj-password-input"
        if error:
            cls += " dj-password-input--error"
        if custom_class:
            cls += f" {custom_class}"

        label_html = ""
        if label:
            req_span = '<span class="form-required"> *</span>' if required else ""
            label_html = (
                f'<label class="form-label" for="{name}">{label}{req_span}</label>'
            )

        error_html = (
            f'<span class="form-error-message">{error}</span>' if error else ""
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
            s_cls = f"dj-password-strength--{min(max(strength, 0), 4)}"
            strength_html = (
                f'<div class="dj-password-strength {s_cls}" '
                f'role="meter" aria-valuenow="{strength}" '
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
            f'name="{name}" id="{name}" value="{value}" '
            f'placeholder="{placeholder}" '
            f'dj-input="{event}"{required_attr}{disabled_attr}>'
            f'{toggle_btn}'
            f'</div>'
            f'{strength_html}'
            f'{error_html}'
            f'</div>'
        )


class AutocompleteHandler:
    """Inline handler for {% autocomplete name="city" source_event="search_cities" %}"""

    def render(self, args, context):
        kw = _parse_args(args, context)
        name = conditional_escape(kw.get("name", ""))
        label = conditional_escape(kw.get("label", ""))
        value = conditional_escape(str(kw.get("value", "")))
        display_value = conditional_escape(str(kw.get("display_value", value)))
        placeholder = conditional_escape(kw.get("placeholder", ""))
        source_event = conditional_escape(kw.get("source_event", ""))
        event = conditional_escape(kw.get("event", name))
        debounce = int(kw.get("debounce", 300))
        min_chars = int(kw.get("min_chars", 1))
        suggestions = kw.get("suggestions") or context.get("suggestions", [])
        loading = kw.get("loading", False)
        disabled = kw.get("disabled", False)
        error = conditional_escape(kw.get("error", ""))
        required = kw.get("required", False)
        custom_class = conditional_escape(kw.get("custom_class", ""))

        if not isinstance(suggestions, (list, tuple)):
            suggestions = []

        disabled_attr = " disabled" if disabled else ""
        required_attr = " required" if required else ""
        cls = "dj-autocomplete"
        if loading:
            cls += " dj-autocomplete--loading"
        if error:
            cls += " dj-autocomplete--error"
        if custom_class:
            cls += f" {custom_class}"

        label_html = ""
        if label:
            req_span = '<span class="form-required"> *</span>' if required else ""
            label_html = (
                f'<label class="form-label" for="{name}">{label}{req_span}</label>'
            )

        error_html = (
            f'<span class="form-error-message">{error}</span>' if error else ""
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
            f'<div class="{cls}" data-source-event="{source_event}" '
            f'data-debounce="{debounce}" data-min-chars="{min_chars}">'
            f'<input type="text" class="dj-autocomplete__input form-input" '
            f'name="{name}_display" id="{name}" value="{display_value}" '
            f'placeholder="{placeholder}" autocomplete="off" '
            f'role="combobox" aria-autocomplete="list" '
            f'aria-expanded="{"true" if suggestion_items else "false"}" '
            f'dj-input="{source_event or event}" '
            f'data-debounce="{debounce}"{required_attr}{disabled_attr}>'
            f'<input type="hidden" name="{name}" value="{value}">'
            f'{spinner_html}'
            f'{suggestions_html}'
            f'</div>'
            f'{error_html}'
            f'</div>'
        )


INLINE_HANDLERS.extend([
    ("slider", SliderHandler()),
    ("search_input", SearchInputHandler()),
    ("password_input", PasswordInputHandler()),
    ("autocomplete", AutocompleteHandler()),
])


# ===========================================================================
# CONFIRMATION PATTERNS
# ===========================================================================

class ConfirmDialogHandler:
    """Inline handler for {% confirm_dialog message="Delete?" confirm_event="delete" %}"""
    def render(self, args, context):
        kw = _parse_args(args, context)
        is_open = kw.get("open", False)
        if not is_open:
            return ""
        message = conditional_escape(kw.get("message", "Are you sure?"))
        confirm_event = conditional_escape(kw.get("confirm_event", "confirm"))
        cancel_event = conditional_escape(kw.get("cancel_event", "cancel"))
        title = conditional_escape(kw.get("title", "Confirm"))
        variant = conditional_escape(kw.get("variant", "default"))
        confirm_label = conditional_escape(kw.get("confirm_label", "Confirm"))
        cancel_label = conditional_escape(kw.get("cancel_label", "Cancel"))
        custom_class = conditional_escape(kw.get("custom_class", ""))

        variant_cls = f" dj-confirm-dialog--{variant}" if variant != "default" else ""
        extra_cls = f" {custom_class}" if custom_class else ""

        return mark_safe(
            f'<div class="dj-confirm-dialog-backdrop" dj-click="{cancel_event}">'
            f'<div class="dj-confirm-dialog{variant_cls}{extra_cls}" '
            f'role="alertdialog" aria-modal="true" aria-labelledby="dj-confirm-title" '
            f'aria-describedby="dj-confirm-msg" onclick="event.stopPropagation()">'
            f'<div class="dj-confirm-dialog__header">'
            f'<h3 class="dj-confirm-dialog__title" id="dj-confirm-title">{title}</h3>'
            f'<button class="dj-confirm-dialog__close" dj-click="{cancel_event}" '
            f'aria-label="Close">&times;</button>'
            f'</div>'
            f'<div class="dj-confirm-dialog__body" id="dj-confirm-msg">'
            f'<p class="dj-confirm-dialog__message">{message}</p>'
            f'</div>'
            f'<div class="dj-confirm-dialog__footer">'
            f'<button class="dj-confirm-dialog__btn dj-confirm-dialog__btn--cancel" '
            f'dj-click="{cancel_event}">{cancel_label}</button>'
            f'<button class="dj-confirm-dialog__btn dj-confirm-dialog__btn--confirm" '
            f'dj-click="{confirm_event}">{confirm_label}</button>'
            f'</div>'
            f'</div>'
            f'</div>'
        )


class PopconfirmHandler:
    """Block handler for {% popconfirm message="Delete?" %}...{% endpopconfirm %}"""
    def render(self, args, content, context):
        kw = _parse_args(args, context)
        message = conditional_escape(kw.get("message", "Are you sure?"))
        confirm_event = conditional_escape(kw.get("confirm_event", "confirm"))
        cancel_event = conditional_escape(kw.get("cancel_event", "cancel"))
        confirm_label = conditional_escape(kw.get("confirm_label", "Yes"))
        cancel_label = conditional_escape(kw.get("cancel_label", "No"))
        placement = conditional_escape(kw.get("placement", "top"))
        variant = conditional_escape(kw.get("variant", "default"))
        custom_class = conditional_escape(kw.get("custom_class", ""))

        variant_cls = f" dj-popconfirm--{variant}" if variant != "default" else ""
        extra_cls = f" {custom_class}" if custom_class else ""

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
            f'<div class="dj-popconfirm-wrapper{variant_cls}{extra_cls}">'
            f'<div class="dj-popconfirm-trigger" onclick="{js_toggle}">'
            f'{content}'
            f'</div>'
            f'<div class="dj-popconfirm dj-popconfirm-{placement}" role="tooltip">'
            f'<p class="dj-popconfirm__message">{message}</p>'
            f'<div class="dj-popconfirm__actions">'
            f'<button class="dj-popconfirm__btn dj-popconfirm__btn--cancel" '
            f'onclick="{js_close}" dj-click="{cancel_event}">{cancel_label}</button>'
            f'<button class="dj-popconfirm__btn dj-popconfirm__btn--confirm" '
            f'onclick="{js_close}" dj-click="{confirm_event}">{confirm_label}</button>'
            f'</div>'
            f'</div>'
            f'</div>'
        )


INLINE_HANDLERS.extend([
    ("confirm_dialog", ConfirmDialogHandler()),
])

BLOCK_HANDLERS.extend([
    ("popconfirm", "endpopconfirm", PopconfirmHandler()),
])
