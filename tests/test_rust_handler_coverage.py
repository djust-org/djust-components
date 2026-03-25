"""Comprehensive test coverage for all Rust template engine handlers.

Covers 4 batches:
1. Rust handler rendering — all untested handlers: HTML output, CSS classes, attributes
2. Form component interaction — dj-* attribute emission for event handling
3. Complex component state — nested content, dynamic state, edge conditions
4. Edge cases — empty data, missing params, XSS payloads
"""
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "djust_components",
        ],
        TEMPLATES=[{
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
            "APP_DIRS": True,
            "OPTIONS": {"context_processors": []},
        }],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    )
    django.setup()

import pytest
from django.utils.safestring import SafeData


# ═══════════════════════════════════════════════════════════════════════════
# BATCH 1: Untested Rust Handler Rendering
# ═══════════════════════════════════════════════════════════════════════════


# ─── CardHandler ───


class TestCardHandler:
    def test_renders_with_title_and_subtitle(self):
        from djust_components.rust_handlers import CardHandler
        h = CardHandler()
        result = h.render(['title="My Card"', 'subtitle="A description"'], "body content", {})
        assert "card" in result
        assert "My Card" in result
        assert "A description" in result
        assert "body content" in result
        assert isinstance(result, SafeData)

    def test_variant_class(self):
        from djust_components.rust_handlers import CardHandler
        h = CardHandler()
        result = h.render(['variant="elevated"'], "content", {})
        assert "card-elevated" in result

    def test_default_variant(self):
        from djust_components.rust_handlers import CardHandler
        h = CardHandler()
        result = h.render([], "content", {})
        assert "card-default" in result

    def test_no_header_without_title(self):
        from djust_components.rust_handlers import CardHandler
        h = CardHandler()
        result = h.render([], "content", {})
        assert "card-header" not in result

    def test_extra_class(self):
        from djust_components.rust_handlers import CardHandler
        h = CardHandler()
        result = h.render(['class="my-extra"'], "content", {})
        assert "my-extra" in result


# ─── TabsHandler ───


class TestTabsHandler:
    def test_renders_container(self):
        from djust_components.rust_handlers import TabsHandler
        h = TabsHandler()
        result = h.render(['id="my-tabs"'], "tab content here", {})
        assert "tabs-container" in result
        assert 'id="my-tabs"' in result
        assert "tab content here" in result
        assert isinstance(result, SafeData)

    def test_default_id(self):
        from djust_components.rust_handlers import TabsHandler
        h = TabsHandler()
        result = h.render([], "content", {})
        assert 'id="tabs"' in result


# ─── AccordionHandler ───


class TestAccordionHandler:
    def test_renders_container(self):
        from djust_components.rust_handlers import AccordionHandler
        h = AccordionHandler()
        result = h.render(['id="faq"'], "accordion items", {})
        assert "accordion" in result
        assert 'id="faq"' in result
        assert "accordion items" in result
        assert isinstance(result, SafeData)

    def test_default_id(self):
        from djust_components.rust_handlers import AccordionHandler
        h = AccordionHandler()
        result = h.render([], "content", {})
        assert 'id="accordion"' in result


# ─── AccordionItemHandler ───


class TestAccordionItemHandler:
    def test_renders_closed(self):
        from djust_components.rust_handlers import AccordionItemHandler
        h = AccordionItemHandler()
        result = h.render(['title="Question 1"', 'id="q1"'], "Answer 1", {})
        assert "accordion-item" in result
        assert "Question 1" in result
        assert "Answer 1" in result
        assert 'aria-expanded="false"' in result
        assert "hidden" in result
        assert isinstance(result, SafeData)

    def test_renders_open(self):
        from djust_components.rust_handlers import AccordionItemHandler
        h = AccordionItemHandler()
        result = h.render(['title="Q"', 'id="q1"', "open=True"], "A", {})
        assert "accordion-item--open" in result
        assert 'aria-expanded="true"' in result

    def test_custom_event(self):
        from djust_components.rust_handlers import AccordionItemHandler
        h = AccordionItemHandler()
        result = h.render(['title="Q"', 'id="q1"', 'event="my_toggle"'], "A", {})
        assert 'dj-click="my_toggle"' in result


# ─── DropdownHandler ───


class TestDropdownHandler:
    def test_renders_open(self):
        from djust_components.rust_handlers import DropdownHandler
        h = DropdownHandler()
        result = h.render(['label="Menu"', "open=True"], "menu items", {})
        assert "dropdown" in result
        assert "Menu" in result
        assert "menu items" in result
        assert 'data-open="true"' in result
        assert isinstance(result, SafeData)

    def test_renders_closed(self):
        from djust_components.rust_handlers import DropdownHandler
        h = DropdownHandler()
        result = h.render(['label="Menu"', "open=False"], "items", {})
        assert 'data-open="false"' in result

    def test_custom_toggle_event(self):
        from djust_components.rust_handlers import DropdownHandler
        h = DropdownHandler()
        result = h.render(['label="X"', 'toggle_event="my_toggle"'], "items", {})
        assert 'dj-click="my_toggle"' in result


# ─── AlertHandler ───


class TestAlertHandler:
    def test_renders_info_alert(self):
        from djust_components.rust_handlers import AlertHandler
        h = AlertHandler()
        result = h.render(['type="info"'], "Info message", {})
        assert "alert alert-info" in result
        assert "Info message" in result
        assert isinstance(result, SafeData)

    def test_renders_error_alert(self):
        from djust_components.rust_handlers import AlertHandler
        h = AlertHandler()
        result = h.render(['type="error"'], "Error message", {})
        assert "alert-error" in result

    def test_danger_maps_to_error(self):
        from djust_components.rust_handlers import AlertHandler
        h = AlertHandler()
        result = h.render(['type="danger"'], "msg", {})
        assert "alert-error" in result

    def test_with_title(self):
        from djust_components.rust_handlers import AlertHandler
        h = AlertHandler()
        result = h.render(['type="warning"', 'title="Warning!"'], "details", {})
        assert "alert-title" in result
        assert "Warning!" in result

    def test_dismissible(self):
        from djust_components.rust_handlers import AlertHandler
        h = AlertHandler()
        result = h.render(['type="info"', "dismissible=True"], "msg", {})
        assert "alert-dismissible" in result
        assert "alert-close" in result
        assert 'dj-click="dismiss_alert"' in result

    def test_custom_dismiss_event(self):
        from djust_components.rust_handlers import AlertHandler
        h = AlertHandler()
        result = h.render(['type="info"', "dismissible=True", 'event="my_dismiss"'], "msg", {})
        assert 'dj-click="my_dismiss"' in result

    def test_icons_for_types(self):
        from djust_components.rust_handlers import AlertHandler
        h = AlertHandler()
        for alert_type, icon in [("info", "ℹ"), ("success", "✓"), ("warning", "⚠"), ("error", "✕")]:
            result = h.render([f'type="{alert_type}"'], "msg", {})
            assert icon in result


# ─── FormGroupHandler ───


class TestFormGroupHandler:
    def test_renders_with_label(self):
        from djust_components.rust_handlers import FormGroupHandler
        h = FormGroupHandler()
        result = h.render(['label="Email"', 'for_input="email"'], "<input>", {})
        assert "form-group" in result
        assert "Email" in result
        assert 'for="email"' in result
        assert isinstance(result, SafeData)

    def test_renders_error(self):
        from djust_components.rust_handlers import FormGroupHandler
        h = FormGroupHandler()
        result = h.render(['error="Required"'], "<input>", {})
        assert "form-error-message" in result
        assert "Required" in result

    def test_renders_helper(self):
        from djust_components.rust_handlers import FormGroupHandler
        h = FormGroupHandler()
        result = h.render(['helper="Enter your email"'], "<input>", {})
        assert "form-helper" in result
        assert "Enter your email" in result

    def test_required_indicator(self):
        from djust_components.rust_handlers import FormGroupHandler
        h = FormGroupHandler()
        result = h.render(['label="Name"', "required=True"], "<input>", {})
        assert "form-label-required" in result


# ─── TimelineHandler ───


class TestTimelineHandler:
    def test_renders_container(self):
        from djust_components.rust_handlers import TimelineHandler
        h = TimelineHandler()
        result = h.render([], "timeline items", {})
        assert "timeline" in result
        assert "timeline items" in result
        assert isinstance(result, SafeData)


# ─── TimelineItemHandler ───


class TestTimelineItemHandler:
    def test_renders_with_title(self):
        from djust_components.rust_handlers import TimelineItemHandler
        h = TimelineItemHandler()
        result = h.render(['title="Deploy v1.0"', 'time="2h ago"'], "Details here", {})
        assert "timeline-item" in result
        assert "timeline-marker" in result
        assert "Deploy v1.0" in result
        assert "2h ago" in result
        assert "Details here" in result
        assert isinstance(result, SafeData)

    def test_no_time(self):
        from djust_components.rust_handlers import TimelineItemHandler
        h = TimelineItemHandler()
        result = h.render(['title="Event"'], "body", {})
        assert "timeline-time" not in result


# ─── TooltipHandler ───


class TestTooltipHandler:
    def test_renders_tooltip(self):
        from djust_components.rust_handlers import TooltipHandler
        h = TooltipHandler()
        result = h.render(['text="Help text"', 'position="top"'], "hover me", {})
        assert "tooltip-wrapper" in result
        assert "tooltip-top" in result
        assert "Help text" in result
        assert "hover me" in result
        assert isinstance(result, SafeData)

    def test_default_position(self):
        from djust_components.rust_handlers import TooltipHandler
        h = TooltipHandler()
        result = h.render(['text="tip"'], "content", {})
        assert "tooltip-top" in result


# ─── ToastContainerHandler ───


class TestToastContainerHandler:
    def test_renders_empty(self):
        from djust_components.rust_handlers import ToastContainerHandler
        h = ToastContainerHandler()
        result = h.render([], {"toasts": []})
        assert "toast-container" in result

    def test_renders_toasts(self):
        from djust_components.rust_handlers import ToastContainerHandler
        h = ToastContainerHandler()
        toasts = [
            {"id": 1, "type": "success", "message": "Done!"},
            {"id": 2, "type": "error", "message": "Failed"},
        ]
        result = h.render([], {"toasts": toasts})
        assert "toast-success" in result
        assert "toast-error" in result
        assert "Done!" in result
        assert "Failed" in result
        assert isinstance(result, SafeData)

    def test_skips_non_dict_toasts(self):
        from djust_components.rust_handlers import ToastContainerHandler
        h = ToastContainerHandler()
        result = h.render([], {"toasts": ["not a dict", 123]})
        assert "toast-container" in result
        assert "toast-message" not in result


# ─── ProgressHandler ───


class TestProgressHandler:
    def test_renders_progress(self):
        from djust_components.rust_handlers import ProgressHandler
        h = ProgressHandler()
        result = h.render(['value=75', 'label="Upload"', 'color="success"'], {})
        assert "progress-wrapper" in result
        assert "75%" in result
        assert "Upload" in result
        assert "success" in result
        assert isinstance(result, SafeData)

    def test_clamps_value(self):
        from djust_components.rust_handlers import ProgressHandler
        h = ProgressHandler()
        result = h.render(["value=150"], {})
        assert "100%" in result

    def test_negative_value_clamps_to_zero(self):
        from djust_components.rust_handlers import ProgressHandler
        h = ProgressHandler()
        result = h.render(["value=-10"], {})
        assert "0%" in result

    def test_track_size(self):
        from djust_components.rust_handlers import ProgressHandler
        h = ProgressHandler()
        result = h.render(['value=50', 'size="lg"'], {})
        assert "progress-track-lg" in result


# ─── BadgeHandler ───


class TestBadgeHandler:
    def test_renders_badge(self):
        from djust_components.rust_handlers import BadgeHandler
        h = BadgeHandler()
        result = h.render(['label="API"', 'status="online"'], {})
        assert "badge badge-online" in result
        assert "API" in result
        assert isinstance(result, SafeData)

    def test_pulse(self):
        from djust_components.rust_handlers import BadgeHandler
        h = BadgeHandler()
        result = h.render(['label="Live"', "pulse=True"], {})
        assert "badge-pulse" in result


# ─── PaginationHandler ───


class TestPaginationHandler:
    def test_renders_pagination(self):
        from djust_components.rust_handlers import PaginationHandler
        h = PaginationHandler()
        result = h.render(["page=3", "total_pages=10"], {})
        assert "pagination" in result
        assert "Page 3 of 10" in result
        assert isinstance(result, SafeData)

    def test_prev_disabled_on_first_page(self):
        from djust_components.rust_handlers import PaginationHandler
        h = PaginationHandler()
        result = h.render(["page=1", "total_pages=5"], {})
        # First button should be disabled
        assert "disabled" in result.split("&#8592;")[0]

    def test_next_disabled_on_last_page(self):
        from djust_components.rust_handlers import PaginationHandler
        h = PaginationHandler()
        result = h.render(["page=5", "total_pages=5"], {})
        # Last button should be disabled
        assert "disabled" in result.split("&#8594;")[0]

    def test_custom_events(self):
        from djust_components.rust_handlers import PaginationHandler
        h = PaginationHandler()
        result = h.render(["page=2", "total_pages=5", 'prev_event="go_prev"', 'next_event="go_next"'], {})
        assert 'dj-click="go_prev"' in result
        assert 'dj-click="go_next"' in result


# ─── AvatarHandler ───


class TestAvatarHandler:
    def test_renders_with_initials(self):
        from djust_components.rust_handlers import AvatarHandler
        h = AvatarHandler()
        result = h.render(['initials="JD"', 'size="lg"', 'status="online"'], {})
        assert "avatar" in result
        assert "avatar-lg" in result
        assert "JD" in result
        assert "avatar-status-online" in result
        assert isinstance(result, SafeData)

    def test_renders_with_image(self):
        from djust_components.rust_handlers import AvatarHandler
        h = AvatarHandler()
        result = h.render(['src="/img/me.jpg"', 'alt="Me"'], {})
        assert "avatar-image" in result
        assert 'src="/img/me.jpg"' in result

    def test_auto_initials_from_alt(self):
        from djust_components.rust_handlers import AvatarHandler
        h = AvatarHandler()
        result = h.render(['alt="John"'], {})
        assert "JO" in result


# ─── SpinnerHandler ───


class TestSpinnerHandler:
    def test_renders_spinner(self):
        from djust_components.rust_handlers import SpinnerHandler
        h = SpinnerHandler()
        result = h.render([], {})
        assert "spinner" in result
        assert "spinner-md" in result
        assert "spinner-primary" in result
        assert 'role="status"' in result
        assert isinstance(result, SafeData)

    def test_custom_size_and_color(self):
        from djust_components.rust_handlers import SpinnerHandler
        h = SpinnerHandler()
        result = h.render(['size="lg"', 'color="success"'], {})
        assert "spinner-lg" in result
        assert "spinner-success" in result


# ─── SkeletonHandler ───


class TestSkeletonHandler:
    def test_default_text_lines(self):
        from djust_components.rust_handlers import SkeletonHandler
        h = SkeletonHandler()
        result = h.render([], {})
        assert "skeleton-text" in result
        assert "skeleton-line" in result
        assert isinstance(result, SafeData)

    def test_avatar_type(self):
        from djust_components.rust_handlers import SkeletonHandler
        h = SkeletonHandler()
        result = h.render(['type="avatar"'], {})
        assert "skeleton-avatar" in result

    def test_card_type(self):
        from djust_components.rust_handlers import SkeletonHandler
        h = SkeletonHandler()
        result = h.render(['type="card"'], {})
        assert "skeleton-card" in result

    def test_table_type(self):
        from djust_components.rust_handlers import SkeletonHandler
        h = SkeletonHandler()
        result = h.render(['type="table"'], {})
        assert "skeleton-table" in result

    def test_custom_lines(self):
        from djust_components.rust_handlers import SkeletonHandler
        h = SkeletonHandler()
        result = h.render(["lines=2"], {})
        assert result.count("skeleton-line") == 2


# ─── BreadcrumbHandler ───


class TestBreadcrumbHandler:
    def test_renders_breadcrumbs(self):
        from djust_components.rust_handlers import BreadcrumbHandler
        h = BreadcrumbHandler()
        items = [
            {"label": "Home", "url": "/"},
            {"label": "Products", "url": "/products"},
            {"label": "Widget"},
        ]
        result = h.render([], {"breadcrumb_items": items})
        assert "breadcrumb" in result
        assert "Home" in result
        assert "Products" in result
        assert "Widget" in result
        assert "breadcrumb-active" in result
        assert "breadcrumb-separator" in result
        assert isinstance(result, SafeData)

    def test_last_item_is_active(self):
        from djust_components.rust_handlers import BreadcrumbHandler
        h = BreadcrumbHandler()
        items = [{"label": "A"}, {"label": "B"}]
        result = h.render([], {"breadcrumb_items": items})
        # B should be active (last item)
        assert "breadcrumb-active" in result

    def test_links_in_non_active_items(self):
        from djust_components.rust_handlers import BreadcrumbHandler
        h = BreadcrumbHandler()
        items = [{"label": "Home", "url": "/"}, {"label": "Current"}]
        result = h.render([], {"breadcrumb_items": items})
        assert 'href="/"' in result
        assert "breadcrumb-link" in result

    def test_items_from_args(self):
        from djust_components.rust_handlers import BreadcrumbHandler
        h = BreadcrumbHandler()
        items = [{"label": "Dashboard", "url": "/dash"}, {"label": "Settings"}]
        result = h.render(['items=nav'], {"nav": items})
        assert "Dashboard" in result
        assert "Settings" in result


# ─── EmptyStateHandler ───


class TestEmptyStateHandler:
    def test_renders_default(self):
        from djust_components.rust_handlers import EmptyStateHandler
        h = EmptyStateHandler()
        result = h.render([], {})
        assert "empty-state" in result
        assert "No items found" in result
        assert isinstance(result, SafeData)

    def test_custom_title_and_description(self):
        from djust_components.rust_handlers import EmptyStateHandler
        h = EmptyStateHandler()
        result = h.render(['title="No results"', 'description="Try a different search"'], {})
        assert "No results" in result
        assert "Try a different search" in result

    def test_with_action(self):
        from djust_components.rust_handlers import EmptyStateHandler
        h = EmptyStateHandler()
        result = h.render(['action_label="Create"', 'action_event="create_item"'], {})
        assert "empty-state-action" in result
        assert "Create" in result
        assert 'dj-click="create_item"' in result

    def test_no_action_without_both_params(self):
        from djust_components.rust_handlers import EmptyStateHandler
        h = EmptyStateHandler()
        result = h.render(['action_label="Create"'], {})
        assert "empty-state-action" not in result


# ─── DividerHandler ───


class TestDividerHandler:
    def test_horizontal_default(self):
        from djust_components.rust_handlers import DividerHandler
        h = DividerHandler()
        result = h.render([], {})
        assert "divider divider-horizontal" in result
        assert isinstance(result, SafeData)

    def test_vertical(self):
        from djust_components.rust_handlers import DividerHandler
        h = DividerHandler()
        result = h.render(["vertical=True"], {})
        assert "divider-vertical" in result

    def test_with_label(self):
        from djust_components.rust_handlers import DividerHandler
        h = DividerHandler()
        result = h.render(['label="OR"'], {})
        assert "divider-label" in result
        assert "OR" in result


# ─── SwitchHandler ───


class TestSwitchHandler:
    def test_renders_switch(self):
        from djust_components.rust_handlers import SwitchHandler
        h = SwitchHandler()
        result = h.render(['name="dark_mode"', 'label="Dark Mode"'], {})
        assert "switch-wrapper" in result
        assert "switch-input" in result
        assert "switch-track" in result
        assert "switch-thumb" in result
        assert "Dark Mode" in result
        assert isinstance(result, SafeData)

    def test_checked(self):
        from djust_components.rust_handlers import SwitchHandler
        h = SwitchHandler()
        result = h.render(['name="toggle"', "checked=True"], {})
        assert "checked" in result

    def test_disabled(self):
        from djust_components.rust_handlers import SwitchHandler
        h = SwitchHandler()
        result = h.render(['name="toggle"', "disabled=True"], {})
        assert "disabled" in result

    def test_custom_event(self):
        from djust_components.rust_handlers import SwitchHandler
        h = SwitchHandler()
        result = h.render(['name="toggle"', 'event="switch_theme"'], {})
        assert 'dj-change="switch_theme"' in result

    def test_size_class(self):
        from djust_components.rust_handlers import SwitchHandler
        h = SwitchHandler()
        result = h.render(['name="toggle"', 'size="sm"'], {})
        assert "switch-sm" in result


# ─── StatCardHandler ───


class TestStatCardHandler:
    def test_renders_stat_card(self):
        from djust_components.rust_handlers import StatCardHandler
        h = StatCardHandler()
        result = h.render(['label="Revenue"', 'value="$12,345"', 'trend="+5%"', 'trend_direction="up"'], {})
        assert "stat-card" in result
        assert "Revenue" in result
        assert "$12,345" in result
        assert "+5%" in result
        assert "stat-trend-up" in result
        assert isinstance(result, SafeData)

    def test_with_description(self):
        from djust_components.rust_handlers import StatCardHandler
        h = StatCardHandler()
        result = h.render(['label="Users"', 'value="100"', 'description="Active this month"'], {})
        assert "stat-card-description" in result
        assert "Active this month" in result

    def test_no_trend(self):
        from djust_components.rust_handlers import StatCardHandler
        h = StatCardHandler()
        result = h.render(['label="Users"', 'value="50"'], {})
        assert "stat-card-trend" not in result

    def test_trend_icons(self):
        from djust_components.rust_handlers import StatCardHandler
        h = StatCardHandler()
        for direction, icon in [("up", "↑"), ("down", "↓"), ("flat", "—")]:
            result = h.render(['label="X"', 'value="1"', 'trend="5%"', f'trend_direction="{direction}"'], {})
            assert icon in result


# ─── TagChipHandler ───


class TestTagChipHandler:
    def test_renders_tag(self):
        from djust_components.rust_handlers import TagChipHandler
        h = TagChipHandler()
        result = h.render(['label="Python"', 'variant="primary"'], {})
        assert "tag tag-primary" in result
        assert "Python" in result
        assert isinstance(result, SafeData)

    def test_dismissible(self):
        from djust_components.rust_handlers import TagChipHandler
        h = TagChipHandler()
        result = h.render(['label="Tag"', "dismissible=True"], {})
        assert "tag-close" in result
        assert 'dj-click="dismiss_tag"' in result

    def test_custom_dismiss_event(self):
        from djust_components.rust_handlers import TagChipHandler
        h = TagChipHandler()
        result = h.render(['label="Tag"', "dismissible=True", 'event="remove_tag"'], {})
        assert 'dj-click="remove_tag"' in result

    def test_size_class(self):
        from djust_components.rust_handlers import TagChipHandler
        h = TagChipHandler()
        result = h.render(['label="Tag"', 'size="sm"'], {})
        assert "tag-sm" in result


# ─── StepperHandler ───


class TestStepperHandler:
    def test_renders_steps(self):
        from djust_components.rust_handlers import StepperHandler
        h = StepperHandler()
        steps = [{"label": "Cart"}, {"label": "Shipping"}, {"label": "Payment"}]
        result = h.render(["active=1"], {"steps": steps})
        assert "stepper" in result
        assert "Cart" in result
        assert "Shipping" in result
        assert "Payment" in result
        assert isinstance(result, SafeData)

    def test_active_step_class(self):
        from djust_components.rust_handlers import StepperHandler
        h = StepperHandler()
        steps = ["Step A", "Step B", "Step C"]
        result = h.render(["active=1"], {"steps": steps})
        assert "stepper-step-active" in result

    def test_complete_step_class(self):
        from djust_components.rust_handlers import StepperHandler
        h = StepperHandler()
        steps = ["Step A", "Step B", "Step C"]
        result = h.render(["active=2"], {"steps": steps})
        assert "stepper-step-complete" in result

    def test_custom_event(self):
        from djust_components.rust_handlers import StepperHandler
        h = StepperHandler()
        steps = ["A"]
        result = h.render(["active=0", 'event="go_step"'], {"steps": steps})
        assert 'dj-click="go_step"' in result


# ─── DjButtonHandler ───


class TestDjButtonHandler:
    def test_renders_button(self):
        from djust_components.rust_handlers import DjButtonHandler
        h = DjButtonHandler()
        result = h.render(['label="Save"', 'event="save"', 'variant="primary"'], {})
        assert "btn btn-primary" in result
        assert "Save" in result
        assert 'dj-click="save"' in result
        assert isinstance(result, SafeData)

    def test_disabled(self):
        from djust_components.rust_handlers import DjButtonHandler
        h = DjButtonHandler()
        result = h.render(['label="Save"', 'event="save"', "disabled=True"], {})
        assert "disabled" in result
        assert "dj-click" not in result

    def test_loading(self):
        from djust_components.rust_handlers import DjButtonHandler
        h = DjButtonHandler()
        result = h.render(['label="Save"', 'event="save"', "loading=True"], {})
        assert "btn-loading" in result
        assert "btn-spinner" in result
        assert "disabled" in result
        assert "dj-click" not in result

    def test_icon(self):
        from djust_components.rust_handlers import DjButtonHandler
        h = DjButtonHandler()
        result = h.render(['label="Save"', 'icon="💾"'], {})
        assert "btn-icon" in result
        assert "💾" in result

    def test_size_class(self):
        from djust_components.rust_handlers import DjButtonHandler
        h = DjButtonHandler()
        result = h.render(['label="X"', 'size="sm"'], {})
        assert "btn-sm" in result


# ─── DjInputHandler ───


class TestDjInputHandler:
    def test_renders_input(self):
        from djust_components.rust_handlers import DjInputHandler
        h = DjInputHandler()
        result = h.render(['name="email"', 'label="Email"', 'placeholder="you@example.com"'], {})
        assert "form-group" in result
        assert "form-input" in result
        assert 'name="email"' in result
        assert "Email" in result
        assert isinstance(result, SafeData)

    def test_error_state(self):
        from djust_components.rust_handlers import DjInputHandler
        h = DjInputHandler()
        result = h.render(['name="email"', 'error="Required field"'], {})
        assert "form-input-error" in result
        assert "form-error-message" in result
        assert "Required field" in result

    def test_required(self):
        from djust_components.rust_handlers import DjInputHandler
        h = DjInputHandler()
        result = h.render(['name="email"', 'label="Email"', "required=True"], {})
        assert "required" in result
        assert "form-label-required" in result

    def test_disabled(self):
        from djust_components.rust_handlers import DjInputHandler
        h = DjInputHandler()
        result = h.render(['name="email"', "disabled=True"], {})
        assert "disabled" in result

    def test_helper_text(self):
        from djust_components.rust_handlers import DjInputHandler
        h = DjInputHandler()
        result = h.render(['name="email"', 'helper="We won\'t share it"'], {})
        assert "form-helper" in result


# ─── DjSelectHandler ───


class TestDjSelectHandler:
    def test_renders_select(self):
        from djust_components.rust_handlers import DjSelectHandler
        h = DjSelectHandler()
        options = [{"value": "us", "label": "United States"}, {"value": "uk", "label": "United Kingdom"}]
        result = h.render(['name="country"', 'label="Country"'], {"country_options": options, "": options})
        # Pass options directly
        result = h.render(['name="country"', 'label="Country"'], {})
        assert "form-group" in result
        assert "form-select" in result
        assert isinstance(result, SafeData)

    def test_options_from_args(self):
        from djust_components.rust_handlers import DjSelectHandler
        h = DjSelectHandler()
        options = [{"value": "a", "label": "Alpha"}, {"value": "b", "label": "Beta"}]
        result = h.render(['name="choice"', 'options=my_opts'], {"my_opts": options})
        assert "Alpha" in result
        assert "Beta" in result

    def test_selected_value(self):
        from djust_components.rust_handlers import DjSelectHandler
        h = DjSelectHandler()
        options = [{"value": "a", "label": "A"}, {"value": "b", "label": "B"}]
        result = h.render(['name="choice"', 'value="b"', 'options=opts'], {"opts": options})
        assert "selected" in result

    def test_error_state(self):
        from djust_components.rust_handlers import DjSelectHandler
        h = DjSelectHandler()
        result = h.render(['name="x"', 'error="Pick one"'], {})
        assert "form-select-error" in result
        assert "Pick one" in result

    def test_tuple_options(self):
        from djust_components.rust_handlers import DjSelectHandler
        h = DjSelectHandler()
        options = [("a", "Alpha"), ("b", "Beta")]
        result = h.render(['name="choice"', 'options=opts'], {"opts": options})
        assert "Alpha" in result


# ─── DjTextareaHandler ───


class TestDjTextareaHandler:
    def test_renders_textarea(self):
        from djust_components.rust_handlers import DjTextareaHandler
        h = DjTextareaHandler()
        result = h.render(['name="notes"', 'label="Notes"', 'placeholder="Type here"'], {})
        assert "form-group" in result
        assert "form-textarea" in result
        assert 'name="notes"' in result
        assert isinstance(result, SafeData)

    def test_custom_rows(self):
        from djust_components.rust_handlers import DjTextareaHandler
        h = DjTextareaHandler()
        result = h.render(['name="notes"', "rows=8"], {})
        assert 'rows="8"' in result

    def test_error_state(self):
        from djust_components.rust_handlers import DjTextareaHandler
        h = DjTextareaHandler()
        result = h.render(['name="notes"', 'error="Too short"'], {})
        assert "form-textarea-error" in result
        assert "Too short" in result


# ─── DjCheckboxHandler ───


class TestDjCheckboxHandler:
    def test_renders_checkbox(self):
        from djust_components.rust_handlers import DjCheckboxHandler
        h = DjCheckboxHandler()
        result = h.render(['name="agree"', 'label="I agree"'], {})
        assert "form-checkbox-wrapper" in result
        assert "form-checkbox" in result
        assert "I agree" in result
        assert isinstance(result, SafeData)

    def test_checked(self):
        from djust_components.rust_handlers import DjCheckboxHandler
        h = DjCheckboxHandler()
        result = h.render(['name="agree"', "checked=True"], {})
        assert "checked" in result

    def test_disabled(self):
        from djust_components.rust_handlers import DjCheckboxHandler
        h = DjCheckboxHandler()
        result = h.render(['name="agree"', "disabled=True"], {})
        assert "disabled" in result


# ─── DjRadioHandler ───


class TestDjRadioHandler:
    def test_renders_radio(self):
        from djust_components.rust_handlers import DjRadioHandler
        h = DjRadioHandler()
        result = h.render(['name="color"', 'label="Red"', 'value="red"'], {})
        assert "form-radio-wrapper" in result
        assert "form-radio" in result
        assert "Red" in result
        assert isinstance(result, SafeData)

    def test_checked_when_current_matches(self):
        from djust_components.rust_handlers import DjRadioHandler
        h = DjRadioHandler()
        result = h.render(['name="color"', 'label="Red"', 'value="red"', 'current_value="red"'], {})
        assert "checked" in result

    def test_not_checked_when_different(self):
        from djust_components.rust_handlers import DjRadioHandler
        h = DjRadioHandler()
        result = h.render(['name="color"', 'label="Red"', 'value="red"', 'current_value="blue"'], {})
        assert " checked" not in result


# ─── DataTableHandler (basic) ───


class TestDataTableHandlerBasic:
    def test_renders_basic_table(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        columns = [{"key": "name", "label": "Name"}, {"key": "age", "label": "Age"}]
        rows = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = h.render([], {"columns": columns, "rows": rows})
        assert "data-table" in result
        assert "Name" in result
        assert "Age" in result
        assert "Alice" in result
        assert "Bob" in result
        assert isinstance(result, SafeData)

    def test_empty_state(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        columns = [{"key": "name", "label": "Name"}]
        result = h.render([], {"columns": columns, "rows": []})
        assert "data-table-empty" in result
        assert "No data" in result

    def test_striped_class(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        result = h.render(["striped=True"], {"columns": [{"key": "a", "label": "A"}], "rows": [{"a": "1"}]})
        assert "data-table-striped" in result

    def test_compact_class(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        result = h.render(["compact=True"], {"columns": [{"key": "a", "label": "A"}], "rows": [{"a": "1"}]})
        assert "data-table-compact" in result


# ═══════════════════════════════════════════════════════════════════════════
# BATCH 2: Form Component Interaction — dj-* attribute emission
# ═══════════════════════════════════════════════════════════════════════════


class TestFormInteractionEvents:
    """Verify all form handlers emit correct dj-* attributes for event handling."""

    def test_dj_input_emits_dj_input(self):
        from djust_components.rust_handlers import DjInputHandler
        h = DjInputHandler()
        result = h.render(['name="email"', 'event="email_changed"'], {})
        assert 'dj-input="email_changed"' in result

    def test_dj_input_default_event_is_name(self):
        from djust_components.rust_handlers import DjInputHandler
        h = DjInputHandler()
        result = h.render(['name="email"'], {})
        assert 'dj-input="email"' in result

    def test_dj_select_emits_dj_change(self):
        from djust_components.rust_handlers import DjSelectHandler
        h = DjSelectHandler()
        result = h.render(['name="country"', 'event="country_changed"'], {})
        assert 'dj-change="country_changed"' in result

    def test_dj_select_default_event_is_name(self):
        from djust_components.rust_handlers import DjSelectHandler
        h = DjSelectHandler()
        result = h.render(['name="country"'], {})
        assert 'dj-change="country"' in result

    def test_dj_textarea_emits_dj_input(self):
        from djust_components.rust_handlers import DjTextareaHandler
        h = DjTextareaHandler()
        result = h.render(['name="notes"', 'event="notes_changed"'], {})
        assert 'dj-input="notes_changed"' in result

    def test_dj_checkbox_emits_dj_change(self):
        from djust_components.rust_handlers import DjCheckboxHandler
        h = DjCheckboxHandler()
        result = h.render(['name="agree"', 'event="agree_changed"'], {})
        assert 'dj-change="agree_changed"' in result

    def test_dj_radio_emits_dj_change(self):
        from djust_components.rust_handlers import DjRadioHandler
        h = DjRadioHandler()
        result = h.render(['name="color"', 'value="red"', 'event="color_changed"'], {})
        assert 'dj-change="color_changed"' in result

    def test_switch_emits_dj_change(self):
        from djust_components.rust_handlers import SwitchHandler
        h = SwitchHandler()
        result = h.render(['name="dark_mode"', 'event="toggle_theme"'], {})
        assert 'dj-change="toggle_theme"' in result

    def test_dropdown_emits_dj_click(self):
        from djust_components.rust_handlers import DropdownHandler
        h = DropdownHandler()
        result = h.render(['toggle_event="toggle_menu"'], "items", {})
        assert 'dj-click="toggle_menu"' in result

    def test_accordion_item_emits_dj_click(self):
        from djust_components.rust_handlers import AccordionItemHandler
        h = AccordionItemHandler()
        result = h.render(['title="Q"', 'id="q1"', 'event="toggle_faq"'], "A", {})
        assert 'dj-click="toggle_faq"' in result

    def test_modal_emits_dj_click_close(self):
        from djust_components.rust_handlers import ModalHandler
        h = ModalHandler()
        result = h.render(["open=True", 'close_event="dismiss"'], "body", {})
        assert 'dj-click="dismiss"' in result

    def test_pagination_emits_dj_click(self):
        from djust_components.rust_handlers import PaginationHandler
        h = PaginationHandler()
        result = h.render(["page=2", "total_pages=5", 'prev_event="go_prev"', 'next_event="go_next"'], {})
        assert 'dj-click="go_prev"' in result
        assert 'dj-click="go_next"' in result


# ═══════════════════════════════════════════════════════════════════════════
# BATCH 3: Complex Component State
# ═══════════════════════════════════════════════════════════════════════════


class TestDataTableSortIndicators:
    def test_sort_ascending_indicator(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        columns = [{"key": "name", "label": "Name", "sortable": True}]
        rows = [{"name": "Alice"}]
        result = h.render(['sort_by="name"', "sort_desc=False"], {"columns": columns, "rows": rows})
        assert "&#8593;" in result  # up arrow
        assert 'aria-sort="ascending"' in result

    def test_sort_descending_indicator(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        columns = [{"key": "name", "label": "Name", "sortable": True}]
        rows = [{"name": "Alice"}]
        result = h.render(['sort_by="name"', "sort_desc=True"], {"columns": columns, "rows": rows})
        assert "&#8595;" in result  # down arrow
        assert 'aria-sort="descending"' in result

    def test_unsorted_column_no_arrow(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        columns = [{"key": "name", "label": "Name"}, {"key": "age", "label": "Age"}]
        rows = [{"name": "A", "age": 1}]
        result = h.render(['sort_by="name"'], {"columns": columns, "rows": rows})
        # Age column should have aria-sort="none"
        assert 'aria-sort="none"' in result


class TestStepperComplexState:
    def test_all_complete_before_active(self):
        from djust_components.rust_handlers import StepperHandler
        h = StepperHandler()
        steps = ["One", "Two", "Three", "Four"]
        result = h.render(["active=3"], {"steps": steps})
        # Steps 0, 1, 2 should be complete; step 3 should be active
        assert result.count("stepper-step-complete") == 3
        assert result.count("stepper-step-active") == 1

    def test_step_with_dict_items(self):
        from djust_components.rust_handlers import StepperHandler
        h = StepperHandler()
        steps = [{"label": "Review"}, {"label": "Approve", "complete": True}]
        result = h.render(["active=0"], {"steps": steps})
        assert "Review" in result
        assert "Approve" in result

    def test_empty_steps(self):
        from djust_components.rust_handlers import StepperHandler
        h = StepperHandler()
        result = h.render(["active=0"], {"steps": []})
        assert "stepper" in result
        assert "stepper-step" not in result


class TestBreadcrumbComplexState:
    def test_explicit_active_flag(self):
        from djust_components.rust_handlers import BreadcrumbHandler
        h = BreadcrumbHandler()
        items = [
            {"label": "Home", "url": "/", "active": True},
            {"label": "Products", "url": "/products"},
        ]
        result = h.render([], {"breadcrumb_items": items})
        # Home should be active despite not being last
        assert "breadcrumb-active" in result

    def test_string_items(self):
        from djust_components.rust_handlers import BreadcrumbHandler
        h = BreadcrumbHandler()
        result = h.render([], {"breadcrumb_items": ["Home", "Products", "Widget"]})
        assert "Home" in result
        assert "Widget" in result

    def test_empty_items(self):
        from djust_components.rust_handlers import BreadcrumbHandler
        h = BreadcrumbHandler()
        result = h.render([], {"breadcrumb_items": []})
        assert "breadcrumb" in result


class TestDataTableSelectable:
    def test_checkbox_rendered(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        columns = [{"key": "name", "label": "Name"}]
        rows = [{"id": "1", "name": "Alice"}]
        result = h.render(["selectable=True"], {"columns": columns, "rows": rows})
        assert "data-table-checkbox" in result
        assert "data-table-select-all" in result

    def test_selected_row_checked(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        columns = [{"key": "name", "label": "Name"}]
        rows = [{"id": "1", "name": "Alice"}]
        result = h.render(['selectable=True', 'selected_rows=["1"]'], {"columns": columns, "rows": rows})
        assert 'aria-selected="true"' in result

    def test_loading_shows_skeleton(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        columns = [{"key": "name", "label": "Name"}]
        result = h.render(["loading=True"], {"columns": columns, "rows": []})
        assert "data-table-loading" in result
        assert 'aria-busy="true"' in result


class TestDataTablePagination:
    def test_pagination_rendered(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        columns = [{"key": "name", "label": "Name"}]
        rows = [{"name": "A"}]
        result = h.render(["paginate=True", "page=2", "total_pages=5"], {"columns": columns, "rows": rows})
        assert "data-table-pagination" in result
        assert "Page 2 of 5" in result

    def test_search_rendered(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        columns = [{"key": "name", "label": "Name"}]
        rows = [{"name": "A"}]
        result = h.render(["search=True"], {"columns": columns, "rows": rows})
        assert "data-table-search" in result
        assert "table-search" in result


# ═══════════════════════════════════════════════════════════════════════════
# BATCH 4: Edge Cases — Empty Data, Missing Params, XSS
# ═══════════════════════════════════════════════════════════════════════════


class TestEdgeCasesEmptyData:
    """Verify handlers handle empty/missing parameters gracefully."""

    def test_card_no_args(self):
        from djust_components.rust_handlers import CardHandler
        h = CardHandler()
        result = h.render([], "content", {})
        assert "card" in result
        assert "content" in result

    def test_alert_no_args(self):
        from djust_components.rust_handlers import AlertHandler
        h = AlertHandler()
        result = h.render([], "message", {})
        assert "alert" in result
        assert "message" in result

    def test_modal_no_args_is_hidden(self):
        from djust_components.rust_handlers import ModalHandler
        h = ModalHandler()
        result = h.render([], "body", {})
        assert result == ""

    def test_dropdown_no_args(self):
        from djust_components.rust_handlers import DropdownHandler
        h = DropdownHandler()
        result = h.render([], "items", {})
        assert "dropdown" in result
        assert "Menu" in result  # default label

    def test_progress_no_args(self):
        from djust_components.rust_handlers import ProgressHandler
        h = ProgressHandler()
        result = h.render([], {})
        assert "progress-wrapper" in result

    def test_spinner_no_args(self):
        from djust_components.rust_handlers import SpinnerHandler
        h = SpinnerHandler()
        result = h.render([], {})
        assert "spinner" in result

    def test_badge_no_args(self):
        from djust_components.rust_handlers import BadgeHandler
        h = BadgeHandler()
        result = h.render([], {})
        assert "badge" in result

    def test_avatar_no_args(self):
        from djust_components.rust_handlers import AvatarHandler
        h = AvatarHandler()
        result = h.render([], {})
        assert "avatar" in result

    def test_empty_state_no_args(self):
        from djust_components.rust_handlers import EmptyStateHandler
        h = EmptyStateHandler()
        result = h.render([], {})
        assert "empty-state" in result

    def test_divider_no_args(self):
        from djust_components.rust_handlers import DividerHandler
        h = DividerHandler()
        result = h.render([], {})
        assert "divider" in result

    def test_switch_no_args(self):
        from djust_components.rust_handlers import SwitchHandler
        h = SwitchHandler()
        result = h.render([], {})
        assert "switch" in result

    def test_stat_card_no_args(self):
        from djust_components.rust_handlers import StatCardHandler
        h = StatCardHandler()
        result = h.render([], {})
        assert "stat-card" in result

    def test_tag_no_args(self):
        from djust_components.rust_handlers import TagChipHandler
        h = TagChipHandler()
        result = h.render([], {})
        assert "tag" in result

    def test_stepper_no_steps(self):
        from djust_components.rust_handlers import StepperHandler
        h = StepperHandler()
        result = h.render([], {})
        assert "stepper" in result

    def test_pagination_no_args(self):
        from djust_components.rust_handlers import PaginationHandler
        h = PaginationHandler()
        result = h.render([], {})
        assert "pagination" in result
        assert "Page 1 of 1" in result

    def test_dj_button_no_args(self):
        from djust_components.rust_handlers import DjButtonHandler
        h = DjButtonHandler()
        result = h.render([], {})
        assert "btn" in result

    def test_dj_input_no_args(self):
        from djust_components.rust_handlers import DjInputHandler
        h = DjInputHandler()
        result = h.render([], {})
        assert "form-group" in result

    def test_dj_select_no_args(self):
        from djust_components.rust_handlers import DjSelectHandler
        h = DjSelectHandler()
        result = h.render([], {})
        assert "form-group" in result

    def test_dj_textarea_no_args(self):
        from djust_components.rust_handlers import DjTextareaHandler
        h = DjTextareaHandler()
        result = h.render([], {})
        assert "form-group" in result

    def test_dj_checkbox_no_args(self):
        from djust_components.rust_handlers import DjCheckboxHandler
        h = DjCheckboxHandler()
        result = h.render([], {})
        assert "form-checkbox" in result

    def test_dj_radio_no_args(self):
        from djust_components.rust_handlers import DjRadioHandler
        h = DjRadioHandler()
        result = h.render([], {})
        assert "form-radio" in result

    def test_breadcrumb_no_items(self):
        from djust_components.rust_handlers import BreadcrumbHandler
        h = BreadcrumbHandler()
        result = h.render([], {})
        assert "breadcrumb" in result

    def test_toast_container_no_toasts(self):
        from djust_components.rust_handlers import ToastContainerHandler
        h = ToastContainerHandler()
        result = h.render([], {})
        assert "toast-container" in result

    def test_data_table_no_args(self):
        from djust_components.rust_handlers import DataTableHandler
        h = DataTableHandler()
        result = h.render([], {})
        assert "data-table" in result

    def test_skeleton_invalid_lines(self):
        from djust_components.rust_handlers import SkeletonHandler
        h = SkeletonHandler()
        result = h.render(['lines="invalid"'], {})
        assert "skeleton" in result  # falls back to default 3

    def test_progress_invalid_value(self):
        from djust_components.rust_handlers import ProgressHandler
        h = ProgressHandler()
        result = h.render(['value="not_a_number"'], {})
        assert "0%" in result  # falls back to 0


class TestXSSPayloads:
    """Verify all handlers that accept user text properly escape XSS payloads."""

    XSS_SCRIPT = '<script>alert("xss")</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_raw_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html

    # Card
    def test_card_title_xss(self):
        from djust_components.rust_handlers import CardHandler
        h = CardHandler()
        result = h.render(['title="<script>alert(1)</script>"'], "body", {})
        self._assert_no_raw_script(result)

    def test_card_subtitle_xss(self):
        from djust_components.rust_handlers import CardHandler
        h = CardHandler()
        result = h.render(['title="T"', 'subtitle="<script>alert(1)</script>"'], "body", {})
        self._assert_no_raw_script(result)

    def test_card_variant_xss(self):
        from djust_components.rust_handlers import CardHandler
        h = CardHandler()
        result = h.render([f'variant="{self.XSS_ATTR}"'], "body", {})
        self._assert_attr_escaped(result)

    def test_card_class_xss(self):
        from djust_components.rust_handlers import CardHandler
        h = CardHandler()
        result = h.render([f'class="{self.XSS_ATTR}"'], "body", {})
        self._assert_attr_escaped(result)

    # Alert
    def test_alert_title_xss(self):
        from djust_components.rust_handlers import AlertHandler
        h = AlertHandler()
        result = h.render(['title="<script>alert(1)</script>"', 'type="info"'], "msg", {})
        self._assert_no_raw_script(result)

    def test_alert_event_xss(self):
        from djust_components.rust_handlers import AlertHandler
        h = AlertHandler()
        result = h.render([f'event="{self.XSS_ATTR}"', "dismissible=True"], "msg", {})
        self._assert_attr_escaped(result)

    # FormGroup
    def test_form_group_label_xss(self):
        from djust_components.rust_handlers import FormGroupHandler
        h = FormGroupHandler()
        result = h.render(['label="<script>alert(1)</script>"'], "<input>", {})
        self._assert_no_raw_script(result)

    def test_form_group_error_xss(self):
        from djust_components.rust_handlers import FormGroupHandler
        h = FormGroupHandler()
        result = h.render(['error="<script>alert(1)</script>"'], "<input>", {})
        self._assert_no_raw_script(result)

    # Timeline
    def test_timeline_item_title_xss(self):
        from djust_components.rust_handlers import TimelineItemHandler
        h = TimelineItemHandler()
        result = h.render(['title="<script>alert(1)</script>"'], "body", {})
        self._assert_no_raw_script(result)

    def test_timeline_item_time_xss(self):
        from djust_components.rust_handlers import TimelineItemHandler
        h = TimelineItemHandler()
        result = h.render(['time="<script>alert(1)</script>"'], "body", {})
        self._assert_no_raw_script(result)

    # Tooltip
    def test_tooltip_text_xss(self):
        from djust_components.rust_handlers import TooltipHandler
        h = TooltipHandler()
        result = h.render(['text="<script>alert(1)</script>"'], "content", {})
        self._assert_no_raw_script(result)

    def test_tooltip_position_xss(self):
        from djust_components.rust_handlers import TooltipHandler
        h = TooltipHandler()
        result = h.render([f'position="{self.XSS_ATTR}"'], "content", {})
        self._assert_attr_escaped(result)

    # Toast
    def test_toast_message_xss(self):
        from djust_components.rust_handlers import ToastContainerHandler
        h = ToastContainerHandler()
        result = h.render([], {"toasts": [{"id": 1, "type": "info", "message": self.XSS_SCRIPT}]})
        self._assert_no_raw_script(result)

    def test_toast_type_xss(self):
        from djust_components.rust_handlers import ToastContainerHandler
        h = ToastContainerHandler()
        result = h.render([], {"toasts": [{"id": 1, "type": self.XSS_ATTR, "message": "hi"}]})
        self._assert_attr_escaped(result)

    # Progress
    def test_progress_label_xss(self):
        from djust_components.rust_handlers import ProgressHandler
        h = ProgressHandler()
        result = h.render(['label="<script>alert(1)</script>"', "value=50"], {})
        self._assert_no_raw_script(result)

    # Badge
    def test_badge_label_xss(self):
        from djust_components.rust_handlers import BadgeHandler
        h = BadgeHandler()
        result = h.render(['label="<script>alert(1)</script>"'], {})
        self._assert_no_raw_script(result)

    def test_badge_status_xss(self):
        from djust_components.rust_handlers import BadgeHandler
        h = BadgeHandler()
        result = h.render([f'status="{self.XSS_ATTR}"'], {})
        self._assert_attr_escaped(result)

    # Avatar
    def test_avatar_src_xss(self):
        from djust_components.rust_handlers import AvatarHandler
        h = AvatarHandler()
        result = h.render([f'src="{self.XSS_ATTR}"'], {})
        self._assert_attr_escaped(result)

    def test_avatar_alt_xss(self):
        from djust_components.rust_handlers import AvatarHandler
        h = AvatarHandler()
        # With src, alt is used in the img tag
        result = h.render(['src="/img.jpg"', 'alt="<script>alert(1)</script>"'], {})
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    # EmptyState
    def test_empty_state_title_xss(self):
        from djust_components.rust_handlers import EmptyStateHandler
        h = EmptyStateHandler()
        result = h.render(['title="<script>alert(1)</script>"'], {})
        self._assert_no_raw_script(result)

    def test_empty_state_description_xss(self):
        from djust_components.rust_handlers import EmptyStateHandler
        h = EmptyStateHandler()
        result = h.render(['description="<script>alert(1)</script>"'], {})
        self._assert_no_raw_script(result)

    # Divider
    def test_divider_label_xss(self):
        from djust_components.rust_handlers import DividerHandler
        h = DividerHandler()
        result = h.render(['label="<script>alert(1)</script>"'], {})
        self._assert_no_raw_script(result)

    # Switch
    def test_switch_label_xss(self):
        from djust_components.rust_handlers import SwitchHandler
        h = SwitchHandler()
        result = h.render(['label="<script>alert(1)</script>"', 'name="x"'], {})
        self._assert_no_raw_script(result)

    def test_switch_name_xss(self):
        from djust_components.rust_handlers import SwitchHandler
        h = SwitchHandler()
        result = h.render([f'name="{self.XSS_ATTR}"'], {})
        self._assert_attr_escaped(result)

    # StatCard
    def test_stat_card_label_xss(self):
        from djust_components.rust_handlers import StatCardHandler
        h = StatCardHandler()
        result = h.render(['label="<script>alert(1)</script>"', 'value="1"'], {})
        self._assert_no_raw_script(result)

    def test_stat_card_value_xss(self):
        from djust_components.rust_handlers import StatCardHandler
        h = StatCardHandler()
        result = h.render(['value="<script>alert(1)</script>"'], {})
        self._assert_no_raw_script(result)

    # TagChip
    def test_tag_label_xss(self):
        from djust_components.rust_handlers import TagChipHandler
        h = TagChipHandler()
        result = h.render(['label="<script>alert(1)</script>"'], {})
        self._assert_no_raw_script(result)

    def test_tag_variant_xss(self):
        from djust_components.rust_handlers import TagChipHandler
        h = TagChipHandler()
        result = h.render([f'variant="{self.XSS_ATTR}"'], {})
        self._assert_attr_escaped(result)

    # DjButton
    def test_dj_button_label_xss(self):
        from djust_components.rust_handlers import DjButtonHandler
        h = DjButtonHandler()
        result = h.render(['label="<script>alert(1)</script>"'], {})
        self._assert_no_raw_script(result)

    def test_dj_button_event_xss(self):
        from djust_components.rust_handlers import DjButtonHandler
        h = DjButtonHandler()
        result = h.render([f'event="{self.XSS_ATTR}"'], {})
        self._assert_attr_escaped(result)

    # DjInput
    def test_dj_input_label_xss(self):
        from djust_components.rust_handlers import DjInputHandler
        h = DjInputHandler()
        result = h.render(['name="x"', 'label="<script>alert(1)</script>"'], {})
        self._assert_no_raw_script(result)

    def test_dj_input_name_xss(self):
        from djust_components.rust_handlers import DjInputHandler
        h = DjInputHandler()
        result = h.render([f'name="{self.XSS_ATTR}"'], {})
        self._assert_attr_escaped(result)

    def test_dj_input_error_xss(self):
        from djust_components.rust_handlers import DjInputHandler
        h = DjInputHandler()
        result = h.render(['name="x"', 'error="<script>alert(1)</script>"'], {})
        self._assert_no_raw_script(result)

    # DjSelect
    def test_dj_select_label_xss(self):
        from djust_components.rust_handlers import DjSelectHandler
        h = DjSelectHandler()
        result = h.render(['name="x"', 'label="<script>alert(1)</script>"'], {})
        self._assert_no_raw_script(result)

    # DjTextarea
    def test_dj_textarea_label_xss(self):
        from djust_components.rust_handlers import DjTextareaHandler
        h = DjTextareaHandler()
        result = h.render(['name="x"', 'label="<script>alert(1)</script>"'], {})
        self._assert_no_raw_script(result)

    # DjCheckbox
    def test_dj_checkbox_label_xss(self):
        from djust_components.rust_handlers import DjCheckboxHandler
        h = DjCheckboxHandler()
        result = h.render(['name="x"', 'label="<script>alert(1)</script>"'], {})
        self._assert_no_raw_script(result)

    # DjRadio
    def test_dj_radio_label_xss(self):
        from djust_components.rust_handlers import DjRadioHandler
        h = DjRadioHandler()
        result = h.render(['name="x"', 'label="<script>alert(1)</script>"', 'value="v"'], {})
        self._assert_no_raw_script(result)

    # AccordionItem
    def test_accordion_item_title_xss(self):
        from djust_components.rust_handlers import AccordionItemHandler
        h = AccordionItemHandler()
        result = h.render(['title="<script>alert(1)</script>"', 'id="q1"'], "body", {})
        self._assert_no_raw_script(result)

    def test_accordion_item_id_xss(self):
        from djust_components.rust_handlers import AccordionItemHandler
        h = AccordionItemHandler()
        result = h.render([f'id="{self.XSS_ATTR}"', 'title="T"'], "body", {})
        self._assert_attr_escaped(result)

    # Dropdown
    def test_dropdown_label_xss(self):
        from djust_components.rust_handlers import DropdownHandler
        h = DropdownHandler()
        result = h.render(['label="<script>alert(1)</script>"'], "items", {})
        self._assert_no_raw_script(result)

    def test_dropdown_id_xss(self):
        from djust_components.rust_handlers import DropdownHandler
        h = DropdownHandler()
        result = h.render([f'id="{self.XSS_ATTR}"'], "items", {})
        self._assert_attr_escaped(result)

    # Breadcrumb
    def test_breadcrumb_label_xss(self):
        from djust_components.rust_handlers import BreadcrumbHandler
        h = BreadcrumbHandler()
        items = [{"label": self.XSS_SCRIPT}]
        result = h.render([], {"breadcrumb_items": items})
        self._assert_no_raw_script(result)

    def test_breadcrumb_url_xss(self):
        from djust_components.rust_handlers import BreadcrumbHandler
        h = BreadcrumbHandler()
        items = [{"label": "A", "url": self.XSS_ATTR}, {"label": "B"}]
        result = h.render([], {"breadcrumb_items": items})
        self._assert_attr_escaped(result)

    # Stepper
    def test_stepper_label_xss(self):
        from djust_components.rust_handlers import StepperHandler
        h = StepperHandler()
        steps = [{"label": self.XSS_SCRIPT}]
        result = h.render(["active=0"], {"steps": steps})
        self._assert_no_raw_script(result)

    # Modal
    def test_modal_title_xss(self):
        from djust_components.rust_handlers import ModalHandler
        h = ModalHandler()
        result = h.render(["open=True", 'title="<script>alert(1)</script>"'], "body", {})
        self._assert_no_raw_script(result)

    def test_modal_close_event_xss(self):
        from djust_components.rust_handlers import ModalHandler
        h = ModalHandler()
        result = h.render(["open=True", f'close_event="{self.XSS_ATTR}"'], "body", {})
        self._assert_attr_escaped(result)


# ═══════════════════════════════════════════════════════════════════════════
# Delegating Handlers (call template tag functions, verify Rust handler path)
# ═══════════════════════════════════════════════════════════════════════════


class TestDelegatingHandlers:
    """Handlers that delegate to template tag functions should produce valid HTML."""

    def test_combobox_handler(self):
        from djust_components.rust_handlers import ComboboxHandler
        h = ComboboxHandler()
        options = [{"value": "r", "label": "Red"}, {"value": "b", "label": "Blue"}]
        result = h.render(['name="color"'], {"color_options": options})
        assert "combobox" in result

    def test_gauge_handler(self):
        from djust_components.rust_handlers import GaugeHandler
        h = GaugeHandler()
        result = h.render(["value=75"], {})
        assert "gauge" in result

    def test_notification_center_handler(self):
        from djust_components.rust_handlers import NotificationCenterHandler
        h = NotificationCenterHandler()
        notifs = [{"id": "1", "message": "Hello", "unread": True}]
        result = h.render([], {"notifications": notifs})
        assert "notif-center" in result
        assert "Hello" in result

    def test_tree_view_handler(self):
        from djust_components.rust_handlers import TreeViewHandler
        h = TreeViewHandler()
        nodes = [{"id": "root", "label": "Root", "children": []}]
        result = h.render([], {"tree_nodes": nodes})
        assert "tree" in result
        assert "Root" in result

    def test_color_picker_handler(self):
        from djust_components.rust_handlers import ColorPickerHandler
        h = ColorPickerHandler()
        result = h.render(['name="bg"', 'value="#FF0000"'], {})
        assert "color-picker" in result

    def test_carousel_handler(self):
        from djust_components.rust_handlers import CarouselHandler
        h = CarouselHandler()
        images = [{"src": "/a.jpg", "alt": "A"}]
        result = h.render([], {"carousel_images": images})
        assert "carousel" in result

    def test_date_picker_handler(self):
        from djust_components.rust_handlers import DatePickerHandler
        h = DatePickerHandler()
        result = h.render(["year=2026", "month=3"], {})
        assert "date-picker" in result

    def test_file_dropzone_handler(self):
        from djust_components.rust_handlers import FileDropzoneHandler
        h = FileDropzoneHandler()
        result = h.render(['name="upload"'], {})
        assert "dropzone" in result

    def test_virtual_list_handler(self):
        from djust_components.rust_handlers import VirtualListHandler
        h = VirtualListHandler()
        items = [{"label": "Item A"}, {"label": "Item B"}]
        result = h.render([], {"vl_items": items})
        assert "virtual-list" in result

    def test_kanban_board_handler(self):
        from djust_components.rust_handlers import KanbanBoardHandler
        h = KanbanBoardHandler()
        cols = [{"id": "todo", "title": "To Do", "cards": [{"id": "c1", "title": "Task"}]}]
        result = h.render([], {"kanban_columns": cols})
        assert "kanban" in result

    def test_table_of_contents_handler(self):
        from djust_components.rust_handlers import TableOfContentsHandler
        h = TableOfContentsHandler()
        items = [{"id": "intro", "label": "Introduction", "level": 1}]
        result = h.render([], {"toc_items": items})
        assert "toc" in result

    def test_rich_text_editor_handler(self):
        from djust_components.rust_handlers import RichTextEditorHandler
        h = RichTextEditorHandler()
        result = h.render(['name="content"'], {})
        assert "rte" in result

    def test_code_block_handler(self):
        from djust_components.rust_handlers import CodeBlockHandler
        h = CodeBlockHandler()
        result = h.render(['code="print(1)"', 'language="python"'], {})
        assert "code-block" in result
        assert "print(1)" in result

    def test_rating_handler(self):
        from djust_components.rust_handlers import RatingHandler
        h = RatingHandler()
        result = h.render(["value=3"], {})
        assert "rating" in result

    def test_copy_button_handler(self):
        from djust_components.rust_handlers import CopyButtonHandler
        h = CopyButtonHandler()
        result = h.render(['text="hello"'], {})
        assert "copy-btn" in result

    def test_kbd_handler(self):
        from djust_components.rust_handlers import KbdHandler
        h = KbdHandler()
        result = h.render(["Ctrl", "C"], {})
        assert "kbd" in result

    def test_palette_item_handler(self):
        from djust_components.rust_handlers import PaletteItemHandler
        h = PaletteItemHandler()
        result = h.render(['label="Open"', 'shortcut="Ctrl+O"', 'event="open_file"'], {})
        assert "palette-item" in result
        assert "Open" in result

    def test_context_menu_item_handler(self):
        from djust_components.rust_handlers import ContextMenuItemHandler
        h = ContextMenuItemHandler()
        result = h.render(['label="Copy"', 'event="copy"'], {})
        assert "ctx-item" in result
        assert "Copy" in result
