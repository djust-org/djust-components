"""Tests for v1.5 remaining components (15 items)."""
from django.template import Template, Context
import pytest


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ─── Time Picker ───

class TestTimePicker:
    def test_basic_render(self):
        html = render('{% time_picker name="start_time" value="14:30" %}')
        assert "dj-time-picker" in html
        assert 'name="start_time"' in html
        assert 'value="14:30"' in html

    def test_24h_format(self):
        html = render('{% time_picker name="t" value="14:30" format_24h=True %}')
        assert "dj-time-picker__period" not in html
        # Should have 24h option
        assert '<option value="14" selected>14</option>' in html

    def test_12h_format_am_pm(self):
        html = render('{% time_picker name="t" value="14:30" %}')
        assert "dj-time-picker__period" in html
        assert "AM" in html
        assert "PM" in html

    def test_with_event(self):
        html = render('{% time_picker name="t" value="09:00" event="set_time" %}')
        assert 'dj-change="set_time"' in html

    def test_disabled(self):
        html = render('{% time_picker name="t" disabled=True %}')
        assert "dj-time-picker--disabled" in html
        assert " disabled" in html

    def test_with_label(self):
        html = render('{% time_picker name="t" label="Start Time" %}')
        assert "Start Time" in html
        assert "dj-time-picker__label" in html

    def test_step(self):
        html = render('{% time_picker name="t" step=15 %}')
        # Minute select should only have 0, 15, 30, 45
        assert '<option value="0"' in html
        assert '<option value="15"' in html
        assert '<option value="45"' in html
        # 5-minute mark should NOT appear in minute select (though "5" appears in hour)
        assert '>05</option>' not in html


# ─── Wizard / Multi-step Form ───

class TestWizard:
    def test_basic_render(self):
        html = render(
            '{% wizard steps=steps active="info" %}'
            '<p>Step content</p>'
            '{% endwizard %}',
            {"steps": [
                {"id": "info", "label": "Info"},
                {"id": "payment", "label": "Payment"},
            ]},
        )
        assert "dj-wizard" in html
        assert "dj-wizard__step--active" in html
        assert "Info" in html
        assert "Payment" in html
        assert "Step content" in html

    def test_completed_steps(self):
        html = render(
            '{% wizard steps=steps active="payment" %}'
            'content'
            '{% endwizard %}',
            {"steps": [
                {"id": "info", "label": "Info"},
                {"id": "payment", "label": "Payment"},
                {"id": "confirm", "label": "Confirm"},
            ]},
        )
        assert "dj-wizard__step--completed" in html
        assert "dj-wizard__connector--completed" in html

    def test_step_numbers(self):
        html = render(
            '{% wizard steps=steps active="a" %}'
            'x'
            '{% endwizard %}',
            {"steps": [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}]},
        )
        assert "dj-wizard__number" in html

    def test_custom_event(self):
        html = render(
            '{% wizard steps=steps active="a" event="goto_step" %}'
            'x'
            '{% endwizard %}',
            {"steps": [{"id": "a", "label": "A"}]},
        )
        assert 'dj-click="goto_step"' in html


# ─── Bottom Sheet ───

class TestBottomSheet:
    def test_hidden_when_closed(self):
        html = render('{% bottom_sheet open=False %}body{% endbottom_sheet %}')
        assert html.strip() == ""

    def test_visible_when_open(self):
        html = render(
            '{% bottom_sheet open=is_open title="Filters" %}'
            'Filter content'
            '{% endbottom_sheet %}',
            {"is_open": True},
        )
        assert "dj-bottom-sheet__backdrop" in html
        assert "Filters" in html
        assert "Filter content" in html
        assert "dj-bottom-sheet__handle-bar" in html

    def test_close_event(self):
        html = render(
            '{% bottom_sheet open=is_open close_event="close_it" %}'
            'x'
            '{% endbottom_sheet %}',
            {"is_open": True},
        )
        assert 'dj-click="close_it"' in html


# ─── Infinite Scroll ───

class TestInfiniteScroll:
    def test_basic_render(self):
        html = render(
            '{% infinite_scroll load_event="load_more" %}'
            '<div>Item 1</div>'
            '{% endinfinite_scroll %}'
        )
        assert "dj-infinite-scroll" in html
        assert 'data-event="load_more"' in html
        assert "Item 1" in html

    def test_loading_state(self):
        html = render(
            '{% infinite_scroll load_event="load" loading=True %}'
            'content'
            '{% endinfinite_scroll %}'
        )
        assert "dj-infinite-scroll--loading" in html
        assert "dj-infinite-scroll__spinner" in html

    def test_finished_state(self):
        html = render(
            '{% infinite_scroll load_event="load" finished=True %}'
            'content'
            '{% endinfinite_scroll %}'
        )
        assert "dj-infinite-scroll--finished" in html
        assert "No more items" in html

    def test_custom_threshold(self):
        html = render(
            '{% infinite_scroll load_event="load" threshold="500px" %}'
            'x'
            '{% endinfinite_scroll %}'
        )
        assert 'data-threshold="500px"' in html


# ─── Countdown / Timer ───

class TestCountdown:
    def test_basic_render(self):
        html = render('{% countdown target="2026-04-01T00:00:00" %}')
        assert "dj-countdown" in html
        assert 'data-target="2026-04-01T00:00:00"' in html
        assert 'role="timer"' in html

    def test_with_event(self):
        html = render('{% countdown target="2026-04-01T00:00:00" event="done" %}')
        assert 'data-event="done"' in html

    def test_segments(self):
        html = render('{% countdown target="2026-04-01T00:00:00" %}')
        assert 'data-unit="days"' in html
        assert 'data-unit="hours"' in html
        assert 'data-unit="minutes"' in html
        assert 'data-unit="seconds"' in html
        assert "Days" in html

    def test_hide_days(self):
        html = render('{% countdown target="2026-04-01T00:00:00" show_days=False %}')
        assert 'data-unit="days"' not in html
        assert 'data-unit="hours"' in html

    def test_hide_seconds(self):
        html = render('{% countdown target="2026-04-01T00:00:00" show_seconds=False %}')
        assert 'data-unit="seconds"' not in html
        assert 'data-unit="minutes"' in html


# ─── Cookie Consent Banner ───

class TestCookieConsent:
    def test_basic_render(self):
        html = render(
            '{% cookie_consent accept_event="accept_cookies" %}'
            '{% endcookie_consent %}'
        )
        assert "dj-cookie-consent" in html
        assert 'dj-click="accept_cookies"' in html
        assert "Accept" in html

    def test_custom_message(self):
        html = render(
            '{% cookie_consent accept_event="ok" %}'
            'We use cookies.'
            '{% endcookie_consent %}'
        )
        assert "We use cookies." in html

    def test_with_reject(self):
        html = render(
            '{% cookie_consent accept_event="ok" reject_event="no" %}'
            '{% endcookie_consent %}'
        )
        assert 'dj-click="no"' in html
        assert "Decline" in html

    def test_privacy_url(self):
        html = render(
            '{% cookie_consent accept_event="ok" privacy_url="/privacy" %}'
            '{% endcookie_consent %}'
        )
        assert 'href="/privacy"' in html
        assert "Privacy Policy" in html

    def test_position_top(self):
        html = render(
            '{% cookie_consent accept_event="ok" position="top" %}'
            '{% endcookie_consent %}'
        )
        assert "dj-cookie-consent--top" in html

    def test_aria(self):
        html = render(
            '{% cookie_consent accept_event="ok" %}'
            '{% endcookie_consent %}'
        )
        assert 'role="banner"' in html
        assert 'aria-label="Cookie consent"' in html


# ─── Form Array ───

class TestFormArray:
    def test_basic_render(self):
        html = render(
            '{% form_array name="items" add_event="add" remove_event="remove" %}'
            '{% endform_array %}'
        )
        assert "dj-form-array" in html
        assert 'name="items[0]"' in html

    def test_with_rows(self):
        html = render(
            '{% form_array name="items" rows=rows %}'
            '{% endform_array %}',
            {"rows": [{"value": "A"}, {"value": "B"}]},
        )
        assert 'value="A"' in html
        assert 'value="B"' in html
        assert 'name="items[0]"' in html
        assert 'name="items[1]"' in html

    def test_remove_buttons(self):
        html = render(
            '{% form_array name="items" rows=rows min=1 %}'
            '{% endform_array %}',
            {"rows": [{"value": "A"}, {"value": "B"}]},
        )
        assert "dj-form-array__remove" in html
        assert 'aria-label="Remove row' in html

    def test_add_button(self):
        html = render(
            '{% form_array name="items" add_event="add_row" add_label="Add item" %}'
            '{% endform_array %}'
        )
        assert 'dj-click="add_row"' in html
        assert "Add item" in html

    def test_max_reached_disables_add(self):
        rows = [{"value": str(i)} for i in range(10)]
        html = render(
            '{% form_array name="items" rows=rows max=10 %}'
            '{% endform_array %}',
            {"rows": rows},
        )
        assert "disabled" in html  # Add button should be disabled

    def test_min_reached_hides_remove(self):
        html = render(
            '{% form_array name="items" rows=rows min=1 %}'
            '{% endform_array %}',
            {"rows": [{"value": "only"}]},
        )
        assert "dj-form-array__remove" not in html


# ─── Scroll Spy ───

class TestScrollSpy:
    def test_basic_render(self):
        html = render(
            '{% scroll_spy sections=sections active="intro" %}',
            {"sections": ["intro", "features", "pricing"]},
        )
        assert "dj-scroll-spy" in html
        assert 'dj-hook="ScrollSpy"' in html
        assert 'role="navigation"' in html

    def test_active_section(self):
        html = render(
            '{% scroll_spy sections=sections active="features" %}',
            {"sections": ["intro", "features"]},
        )
        assert "dj-scroll-spy__item--active" in html

    def test_custom_event(self):
        html = render(
            '{% scroll_spy sections=sections active_event="nav_changed" %}',
            {"sections": ["a", "b"]},
        )
        assert 'data-event="nav_changed"' in html

    def test_section_links(self):
        html = render(
            '{% scroll_spy sections=sections %}',
            {"sections": ["intro", "features"]},
        )
        assert 'href="#intro"' in html
        assert 'href="#features"' in html


# ─── Page Alert / Banner ───

class TestPageAlert:
    def test_basic_render(self):
        html = render(
            '{% page_alert type="success" %}'
            'Saved!'
            '{% endpage_alert %}'
        )
        assert "dj-page-alert--success" in html
        assert "Saved!" in html
        assert 'role="alert"' in html

    def test_dismissible(self):
        html = render(
            '{% page_alert type="info" dismissible=True dismiss_event="close" %}'
            'Notice'
            '{% endpage_alert %}'
        )
        assert "dj-page-alert__dismiss" in html
        assert 'dj-click="close"' in html

    def test_with_icon(self):
        html = render(
            '{% page_alert type="warning" icon="!" %}'
            'Warning'
            '{% endpage_alert %}'
        )
        assert "dj-page-alert__icon" in html

    def test_error_variant(self):
        html = render(
            '{% page_alert type="error" %}'
            'Error'
            '{% endpage_alert %}'
        )
        assert "dj-page-alert--error" in html


# ─── Dropdown Menu ───

class TestDropdownMenu:
    def test_closed_state(self):
        html = render(
            '{% dropdown_menu label="Actions" open=False items=items %}'
            '{% enddropdown_menu %}',
            {"items": []},
        )
        assert "dj-dropdown-menu__trigger" in html
        assert "dj-dropdown-menu__content" not in html

    def test_open_state_with_items(self):
        html = render(
            '{% dropdown_menu label="Actions" open=is_open items=items %}'
            '{% enddropdown_menu %}',
            {
                "is_open": True,
                "items": [
                    {"label": "Edit", "event": "edit"},
                    {"divider": True},
                    {"label": "Delete", "event": "delete", "danger": True},
                ],
            },
        )
        assert "data-open" in html
        assert "Edit" in html
        assert "Delete" in html
        assert 'role="menu"' in html
        assert 'role="menuitem"' in html
        assert 'role="separator"' in html
        assert "dj-dropdown-menu__item--danger" in html

    def test_custom_toggle_event(self):
        html = render(
            '{% dropdown_menu label="Menu" toggle_event="toggle_actions" open=False %}'
            '{% enddropdown_menu %}'
        )
        assert 'dj-click="toggle_actions"' in html

    def test_with_child_tags(self):
        html = render(
            '{% dropdown_menu label="File" open=is_open %}'
            '{% menu_item label="New" event="new_file" %}'
            '{% menu_divider %}'
            '{% menu_item label="Quit" event="quit" danger=True %}'
            '{% enddropdown_menu %}',
            {"is_open": True},
        )
        assert "New" in html
        assert "Quit" in html
        assert 'dj-click="new_file"' in html
        assert 'role="separator"' in html

    def test_aria_expanded(self):
        html_closed = render(
            '{% dropdown_menu label="M" open=False %}{% enddropdown_menu %}'
        )
        assert 'aria-expanded="false"' in html_closed

        html_open = render(
            '{% dropdown_menu label="M" open=is_open %}{% enddropdown_menu %}',
            {"is_open": True},
        )
        assert 'aria-expanded="true"' in html_open


# ─── Meter / Stacked Progress ───

class TestMeter:
    def test_basic_render(self):
        html = render(
            '{% meter segments=segs total=100 %}',
            {"segs": [
                {"value": 40, "color": "green", "label": "Used"},
                {"value": 20, "color": "yellow", "label": "Reserved"},
            ]},
        )
        assert "dj-meter" in html
        assert "dj-meter__bar" in html
        assert "dj-meter__segment" in html
        assert 'role="meter"' in html

    def test_legend(self):
        html = render(
            '{% meter segments=segs total=100 %}',
            {"segs": [{"value": 40, "color": "green", "label": "Used"}]},
        )
        assert "dj-meter__legend" in html
        assert "Used" in html

    def test_no_legend(self):
        html = render(
            '{% meter segments=segs total=100 show_legend=False %}',
            {"segs": [{"value": 40, "color": "green", "label": "Used"}]},
        )
        assert "dj-meter__legend" not in html

    def test_percentages(self):
        html = render(
            '{% meter segments=segs total=100 %}',
            {"segs": [{"value": 50, "color": "blue", "label": "Half"}]},
        )
        assert "width:50.0%" in html

    def test_with_label(self):
        html = render(
            '{% meter segments=segs total=100 label="Disk Usage" %}',
            {"segs": [{"value": 75, "color": "red", "label": "Used"}]},
        )
        assert "Disk Usage" in html
        assert "dj-meter__label" in html


# ─── Export Dialog ───

class TestExportDialog:
    def test_hidden_when_closed(self):
        html = render(
            '{% export_dialog formats=fmts columns=cols open=False %}',
            {"fmts": ["csv"], "cols": []},
        )
        assert html.strip() == ""

    def test_visible_when_open(self):
        html = render(
            '{% export_dialog formats=fmts columns=cols open=is_open event="export" %}',
            {
                "is_open": True,
                "fmts": ["csv", "xlsx"],
                "cols": [
                    {"id": "name", "label": "Name", "checked": True},
                    {"id": "email", "label": "Email", "checked": False},
                ],
            },
        )
        assert "dj-export-dialog" in html
        assert "CSV" in html
        assert "XLSX" in html
        assert "Name" in html
        assert "Email" in html
        assert 'dj-click="export"' in html

    def test_close_event(self):
        html = render(
            '{% export_dialog formats=fmts columns=cols open=is_open close_event="cancel" %}',
            {"is_open": True, "fmts": ["csv"], "cols": []},
        )
        assert 'dj-click="cancel"' in html

    def test_selected_format(self):
        html = render(
            '{% export_dialog formats=fmts columns=cols open=is_open selected_format="xlsx" %}',
            {"is_open": True, "fmts": ["csv", "xlsx"], "cols": []},
        )
        # xlsx radio should be checked
        assert 'value="xlsx" checked' in html


# ─── Import Wizard ───

class TestImportWizard:
    def test_upload_step(self):
        html = render(
            '{% import_wizard accepted_formats=".csv,.xlsx" step="upload" %}',
        )
        assert "dj-import-wizard" in html
        assert "dj-import-wizard__dropzone" in html
        assert '.csv,.xlsx' in html
        assert "dj-import-wizard__step--active" in html

    def test_map_step(self):
        html = render(
            '{% import_wizard step="map" model_fields=fields %}',
            {"fields": [
                {"id": "name", "label": "Name"},
                {"id": "email", "label": "Email"},
            ]},
        )
        assert "dj-import-wizard__mapping" in html
        assert "Name" in html
        assert "Email" in html

    def test_preview_step(self):
        html = render(
            '{% import_wizard step="preview" event="import_data" %}',
        )
        assert "dj-import-wizard__preview" in html
        assert 'dj-click="import_data"' in html
        assert "Import" in html


# ─── Audit Log Table ───

class TestAuditLog:
    def test_empty_state(self):
        html = render('{% audit_log entries=entries %}', {"entries": []})
        assert "dj-audit-log" in html
        assert "No entries" in html

    def test_with_entries(self):
        html = render(
            '{% audit_log entries=entries %}',
            {"entries": [
                {"timestamp": "2026-03-25 14:30", "user": "admin",
                 "action": "create", "resource": "User #42", "detail": "Created user"},
            ]},
        )
        assert "admin" in html
        assert "User #42" in html
        assert "Created user" in html
        assert "dj-audit-log__row" in html

    def test_headers(self):
        html = render('{% audit_log entries=entries %}', {"entries": []})
        assert "Timestamp" in html
        assert "User" in html
        assert "Action" in html
        assert "Resource" in html
        assert "Detail" in html

    def test_stream_event(self):
        html = render(
            '{% audit_log entries=entries stream_event="new_entry" %}',
            {"entries": []},
        )
        assert 'data-stream-event="new_entry"' in html

    def test_action_class(self):
        html = render(
            '{% audit_log entries=entries %}',
            {"entries": [{"timestamp": "now", "user": "a", "action": "delete",
                         "resource": "x", "detail": ""}]},
        )
        assert "dj-audit-log__action--delete" in html


# ─── Error Boundary ───

class TestErrorBoundary:
    def test_normal_render(self):
        html = render(
            '{% error_boundary fallback="Failed" %}'
            '<p>Works fine</p>'
            '{% enderror_boundary %}'
        )
        assert "dj-error-boundary" in html
        assert "Works fine" in html
        assert "dj-error-boundary--error" not in html

    def test_fallback_on_error(self):
        # Test with a template that raises an error
        html = render(
            '{% error_boundary fallback="Component failed" %}'
            '{{ undefined_var }}'
            '{% enderror_boundary %}'
        )
        # Even without error (undefined_var resolves to ""), boundary wraps content
        assert "dj-error-boundary" in html

    def test_custom_class(self):
        html = render(
            '{% error_boundary class="my-boundary" %}'
            'content'
            '{% enderror_boundary %}'
        )
        assert "my-boundary" in html


# ─── XSS Escaping ───

class TestXSSEscaping:
    """Verify user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_script_escaped(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    def test_time_picker_xss_name(self):
        html = render('{% time_picker name=xss %}', {"xss": self.XSS})
        self._assert_script_escaped(html)

    def test_time_picker_xss_label(self):
        html = render('{% time_picker name="t" label=xss %}', {"xss": self.XSS})
        assert "<script>" not in html

    def test_time_picker_xss_event(self):
        html = render('{% time_picker name="t" event=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_wizard_xss_step_label(self):
        html = render(
            '{% wizard steps=steps active="a" %}x{% endwizard %}',
            {"steps": [{"id": "a", "label": self.XSS}]},
        )
        assert "<script>" not in html

    def test_wizard_xss_event(self):
        html = render(
            '{% wizard steps=steps active="a" event=xss %}x{% endwizard %}',
            {"steps": [{"id": "a", "label": "A"}], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_bottom_sheet_xss_title(self):
        html = render(
            '{% bottom_sheet open=is_open title=xss %}x{% endbottom_sheet %}',
            {"is_open": True, "xss": self.XSS},
        )
        assert "<script>" not in html

    def test_bottom_sheet_xss_close_event(self):
        html = render(
            '{% bottom_sheet open=is_open close_event=xss %}x{% endbottom_sheet %}',
            {"is_open": True, "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_infinite_scroll_xss_event(self):
        html = render(
            '{% infinite_scroll load_event=xss %}x{% endinfinite_scroll %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_countdown_xss_target(self):
        html = render('{% countdown target=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_countdown_xss_event(self):
        html = render('{% countdown target="x" event=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_cookie_consent_xss_accept_event(self):
        html = render(
            '{% cookie_consent accept_event=xss %}{% endcookie_consent %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_cookie_consent_xss_privacy_url(self):
        html = render(
            '{% cookie_consent accept_event="ok" privacy_url=xss %}{% endcookie_consent %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_form_array_xss_name(self):
        html = render(
            '{% form_array name=xss %}{% endform_array %}',
            {"xss": self.XSS},
        )
        assert "<script>" not in html

    def test_form_array_xss_events(self):
        html = render(
            '{% form_array name="items" add_event=xss remove_event=xss2 rows=rows %}{% endform_array %}',
            {"xss": self.XSS_ATTR, "xss2": self.XSS_ATTR,
             "rows": [{"value": "a"}, {"value": "b"}]},
        )
        self._assert_attr_escaped(html)

    def test_scroll_spy_xss_event(self):
        html = render(
            '{% scroll_spy sections=sections active_event=xss %}',
            {"sections": ["a"], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_page_alert_xss_dismiss_event(self):
        html = render(
            '{% page_alert type="info" dismissible=True dismiss_event=xss %}'
            'msg'
            '{% endpage_alert %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_page_alert_xss_icon(self):
        html = render(
            '{% page_alert type="info" icon=xss %}'
            'msg'
            '{% endpage_alert %}',
            {"xss": self.XSS},
        )
        assert "<script>" not in html

    def test_dropdown_menu_xss_label(self):
        html = render(
            '{% dropdown_menu label=xss open=False %}{% enddropdown_menu %}',
            {"xss": self.XSS},
        )
        assert "<script>" not in html

    def test_dropdown_menu_xss_item_event(self):
        html = render(
            '{% dropdown_menu label="M" open=is_open items=items %}{% enddropdown_menu %}',
            {
                "is_open": True,
                "items": [{"label": "X", "event": self.XSS_ATTR}],
            },
        )
        self._assert_attr_escaped(html)

    def test_meter_xss_label(self):
        html = render(
            '{% meter segments=segs total=100 label=xss %}',
            {"segs": [], "xss": self.XSS},
        )
        assert "<script>" not in html

    def test_meter_xss_segment_label(self):
        html = render(
            '{% meter segments=segs total=100 %}',
            {"segs": [{"value": 50, "color": "blue", "label": self.XSS}]},
        )
        assert "<script>" not in html

    def test_export_dialog_xss_title(self):
        html = render(
            '{% export_dialog formats=fmts columns=cols open=is_open title=xss %}',
            {"is_open": True, "fmts": [], "cols": [], "xss": self.XSS},
        )
        assert "<script>" not in html

    def test_export_dialog_xss_event(self):
        html = render(
            '{% export_dialog formats=fmts columns=cols open=is_open event=xss %}',
            {"is_open": True, "fmts": [], "cols": [], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_import_wizard_xss_event(self):
        html = render(
            '{% import_wizard event=xss step="preview" %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_import_wizard_xss_formats(self):
        html = render(
            '{% import_wizard accepted_formats=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_audit_log_xss_entry(self):
        html = render(
            '{% audit_log entries=entries %}',
            {"entries": [{"timestamp": self.XSS, "user": self.XSS,
                         "action": self.XSS, "resource": self.XSS, "detail": self.XSS}]},
        )
        assert "<script>" not in html
        assert html.count("&lt;script&gt;") >= 5

    def test_audit_log_xss_stream_event(self):
        html = render(
            '{% audit_log entries=entries stream_event=xss %}',
            {"entries": [], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_error_boundary_xss_fallback(self):
        html = render(
            '{% error_boundary class=xss %}x{% enderror_boundary %}',
            {"xss": self.XSS},
        )
        assert "<script>" not in html

    def test_menu_item_xss_label(self):
        html = render(
            '{% dropdown_menu label="M" open=is_open %}'
            '{% menu_item label=xss event="x" %}'
            '{% enddropdown_menu %}',
            {"is_open": True, "xss": self.XSS},
        )
        assert "<script>" not in html

    def test_menu_item_xss_event(self):
        html = render(
            '{% dropdown_menu label="M" open=is_open %}'
            '{% menu_item label="X" event=xss %}'
            '{% enddropdown_menu %}',
            {"is_open": True, "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)
