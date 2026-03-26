"""Tests for security hardening sweep (#SEC-SWEEP + #EVAL-REPLACE).

Covers:
- custom_class XSS escaping in component _render_custom() methods
- Toast type allowlist
- Toast container position allowlist
- AuditLog action allowlist
- Spinner label escaping
- Safe arithmetic expression evaluator (eval() replacement)
"""

import pytest


# ---------------------------------------------------------------------------
# 1. custom_class XSS escaping across components
# ---------------------------------------------------------------------------

XSS_CLASS = '"><script>alert(1)</script><x class="'

COMPONENTS_WITH_CUSTOM_CLASS = [
    # (module_path, class_name, extra_kwargs)
    ("badge", "Badge", {"label": "ok"}),
    ("button", "Button", {"label": "ok", "action": "click"}),
    ("card", "Card", {}),
    ("spinner", "Spinner", {}),
    ("toast", "Toast", {"message": "hi"}),
    ("alert", "Alert", {"message": "hi"}),
    ("progress", "Progress", {"value": 50}),
    ("tag", "Tag", {"label": "hi"}),
    ("meter", "Meter", {"value": 50}),
    ("status_indicator", "StatusIndicator", {"status": "ok", "label": "ok"}),
    ("countdown", "Countdown", {"target": "2030-01-01"}),
    ("code_snippet", "CodeSnippet", {"code": "x=1", "language": "python"}),
    ("bar_chart", "BarChart", {"data": [10, 20], "labels": ["a", "b"]}),
    ("line_chart", "LineChart", {"data": [10, 20], "labels": ["a", "b"]}),
    ("pie_chart", "PieChart", {"data": [10, 20], "labels": ["a", "b"]}),
    ("heatmap", "Heatmap", {"data": [[1]], "labels": {"x": ["a"], "y": ["b"]}}),
    ("bottom_sheet", "BottomSheet", {}),
    ("scroll_to_top", "ScrollToTop", {}),
    ("error_boundary", "ErrorBoundary", {}),
    ("wizard", "Wizard", {"steps": [{"label": "s1"}]}),
    ("infinite_scroll", "InfiniteScroll", {"event": "load"}),
    ("sortable_list", "SortableList", {"items": [], "event": "sort"}),
    ("switch", "Switch", {"name": "sw", "checked": False}),
    ("audit_log", "AuditLog", {"entries": []}),
    ("stat_card", "StatCard", {"title": "t", "value": "1", "label": "l"}),
    ("relative_time", "RelativeTime", {"datetime": "2026-01-01"}),
    ("dropdown_menu", "DropdownMenu", {"trigger": "Menu", "items": []}),
    ("notification_badge", "NotificationBadge", {"count": 5}),
    ("page_alert", "PageAlert", {"message": "hi"}),
    ("signature_pad", "SignaturePad", {"name": "sig"}),
    ("image_lightbox", "ImageLightbox", {"images": []}),
    ("image_cropper", "ImageCropper", {"name": "crop"}),
    ("import_wizard", "ImportWizard", {"event": "imp"}),
    ("export_dialog", "ExportDialog", {"event": "exp"}),
    ("form_array", "FormArray", {"name": "fa", "event": "add"}),
    ("comparison_table", "ComparisonTable", {"columns": [], "rows": []}),
    ("diff_viewer", "DiffViewer", {"left": "a", "right": "b"}),
    ("dashboard_grid", "DashboardGrid", {"items": []}),
    ("masonry_grid", "MasonryGrid", {"items": []}),
    ("resizable_panel", "ResizablePanel", {"panels": []}),
    ("responsive_image", "ResponsiveImage", {"src": "x.jpg", "alt": "x"}),
    ("scroll_spy", "ScrollSpy", {"sections": []}),
    ("sortable_grid", "SortableGrid", {"items": [], "event": "sort"}),
    ("segmented_progress", "SegmentedProgress", {"segments": []}),
    ("sparkline", "Sparkline", {"data": [1, 2]}),
    ("progress_circle", "ProgressCircle", {"value": 50}),
    ("calendar_heatmap", "CalendarHeatmap", {"data": {}}),
    ("calendar_view", "CalendarView", {"events": []}),
    ("gantt_chart", "GanttChart", {"tasks": []}),
    ("treemap", "Treemap", {"data": []}),
    ("terminal", "Terminal", {"lines": []}),
    ("log_viewer", "LogViewer", {"lines": []}),
    ("json_viewer", "JsonViewer", {"data": {}}),
    ("file_tree", "FileTree", {"nodes": []}),
    ("markdown", "Markdown", {"content": "hi"}),
    ("markdown_editor", "MarkdownEditor", {"content": "hi", "event": "save"}),
    ("org_chart", "OrgChart", {"nodes": []}),
    ("pivot_table", "PivotTable", {"data": [], "rows": [], "cols": [], "value_key": "v"}),
    ("time_picker", "TimePicker", {"name": "tp", "value": "12:00"}),
    ("currency_input", "CurrencyInput", {"name": "ci"}),
    ("rich_select", "RichSelect", {"name": "rs", "options": []}),
    ("status_dot", "StatusDot", {"status": "ok"}),
    ("tour", "Tour", {"steps": []}),
    ("cookie_consent", "CookieConsent", {}),
    ("copyable_text", "CopyableText", {"text": "hi"}),
]


class TestCustomClassXSSEscaping:
    """Verify that every component escapes custom_class in _render_custom()."""

    @pytest.mark.parametrize(
        "module_name,class_name,kwargs",
        COMPONENTS_WITH_CUSTOM_CLASS,
        ids=[f"{m}.{c}" for m, c, _ in COMPONENTS_WITH_CUSTOM_CLASS],
    )
    def test_custom_class_escaped(self, module_name, class_name, kwargs):
        mod = __import__(
            f"djust_components.components.{module_name}",
            fromlist=[class_name],
        )
        cls = getattr(mod, class_name)
        instance = cls(custom_class=XSS_CLASS, **kwargs)
        rendered = instance._render_custom()
        assert "<script>" not in rendered, (
            f"{class_name} did not escape custom_class: {rendered[:200]}"
        )
        assert "&lt;script&gt;" in rendered or XSS_CLASS not in rendered


# ---------------------------------------------------------------------------
# 2. Spinner label escaping
# ---------------------------------------------------------------------------

class TestSpinnerLabelEscaping:
    def test_label_html_escaped(self):
        from djust_components.components.spinner import Spinner

        s = Spinner(label='<img src=x onerror="alert(1)">')
        rendered = s._render_custom()
        assert "<img" not in rendered
        assert "&lt;img" in rendered

    def test_label_in_aria_escaped(self):
        from djust_components.components.spinner import Spinner

        s = Spinner(label='" onmouseover="alert(1)')
        rendered = s._render_custom()
        # The quote in the label must be escaped so it cannot break out
        # of the aria-label attribute
        assert '&quot;' in rendered
        # The raw unescaped label should not appear
        assert '" onmouseover="' not in rendered


# ---------------------------------------------------------------------------
# 3. Toast type allowlist
# ---------------------------------------------------------------------------

class TestToastTypeAllowlist:
    def test_valid_types(self):
        from djust_components.components.toast import Toast

        for t in ("info", "success", "warning", "error"):
            toast = Toast("msg", type=t)
            rendered = toast._render_custom()
            assert f"dj-toast-{t}" in rendered

    def test_invalid_type_falls_back(self):
        from djust_components.components.toast import Toast

        toast = Toast("msg", type='" onclick="alert(1)')
        rendered = toast._render_custom()
        assert "dj-toast-info" in rendered
        assert "onclick" not in rendered


# ---------------------------------------------------------------------------
# 4. Toast container position allowlist (template tag)
# ---------------------------------------------------------------------------

class TestToastContainerPositionAllowlist:
    def test_valid_positions(self, render):
        for pos in ("top-left", "top-right", "bottom-left", "bottom-right",
                     "top-center", "bottom-center"):
            html = render(f'{{% server_toast_container position="{pos}" %}}')
            assert f"dj-toast-container--{pos}" in html

    def test_invalid_position_falls_back(self, render):
        html = render('{% server_toast_container position="\" onclick=\"alert(1)" %}')
        assert "dj-toast-container--top-right" in html
        assert "onclick" not in html

    def test_missing_position_defaults(self, render):
        html = render("{% server_toast_container %}")
        assert "dj-toast-container--top-right" in html


# ---------------------------------------------------------------------------
# 5. AuditLog action allowlist
# ---------------------------------------------------------------------------

class TestAuditLogActionAllowlist:
    def test_allowed_action_gets_css_class(self):
        from djust_components.components.audit_log import AuditLog

        log = AuditLog(entries=[{"action": "create"}])
        rendered = log._render_custom()
        assert "dj-audit-log__action--create" in rendered

    def test_disallowed_action_omits_css_class(self):
        from djust_components.components.audit_log import AuditLog

        log = AuditLog(entries=[{"action": '"><script>alert(1)</script>'}])
        rendered = log._render_custom()
        assert "dj-audit-log__action--" not in rendered
        assert "<script>" not in rendered

    def test_custom_allowed_actions(self):
        from djust_components.components.audit_log import AuditLog

        log = AuditLog(
            entries=[{"action": "archive"}],
            allowed_actions={"archive"},
        )
        rendered = log._render_custom()
        assert "dj-audit-log__action--archive" in rendered

    def test_action_value_still_escaped_in_cell(self):
        from djust_components.components.audit_log import AuditLog

        log = AuditLog(entries=[{"action": "<b>bold</b>"}])
        rendered = log._render_custom()
        assert "<b>" not in rendered
        assert "&lt;b&gt;" in rendered


# ---------------------------------------------------------------------------
# 6. Safe arithmetic expression evaluator (replaces eval)
# ---------------------------------------------------------------------------

class TestSafeArithmeticEvaluator:
    """Test the _safe_eval_arithmetic function and DataTableMixin._eval_expression."""

    @pytest.fixture()
    def eval_fn(self):
        from djust_components.mixins.data_table import _safe_eval_arithmetic
        return _safe_eval_arithmetic

    def test_simple_addition(self, eval_fn):
        assert eval_fn("a + b", {"a": 3.0, "b": 4.0}) == 7.0

    def test_subtraction(self, eval_fn):
        assert eval_fn("a - b", {"a": 10.0, "b": 3.0}) == 7.0

    def test_multiplication(self, eval_fn):
        assert eval_fn("a * b", {"a": 3.0, "b": 4.0}) == 12.0

    def test_division(self, eval_fn):
        assert eval_fn("a / b", {"a": 10.0, "b": 4.0}) == 2.5

    def test_modulo(self, eval_fn):
        assert eval_fn("a % b", {"a": 10.0, "b": 3.0}) == 1.0

    def test_parentheses(self, eval_fn):
        assert eval_fn("(a + b) * c", {"a": 2.0, "b": 3.0, "c": 4.0}) == 20.0

    def test_nested_parens(self, eval_fn):
        assert eval_fn("((a + b))", {"a": 1.0, "b": 2.0}) == 3.0

    def test_unary_minus(self, eval_fn):
        assert eval_fn("-a + b", {"a": 3.0, "b": 10.0}) == 7.0

    def test_numeric_literal(self, eval_fn):
        assert eval_fn("a + 100", {"a": 5.0}) == 105.0

    def test_float_literal(self, eval_fn):
        assert eval_fn("a * 1.5", {"a": 10.0}) == 15.0

    def test_operator_precedence(self, eval_fn):
        # 2 + 3 * 4 = 14, not 20
        assert eval_fn("a + b * c", {"a": 2.0, "b": 3.0, "c": 4.0}) == 14.0

    def test_division_by_zero_raises(self, eval_fn):
        with pytest.raises(ValueError, match="Division by zero"):
            eval_fn("a / b", {"a": 1.0, "b": 0.0})

    def test_modulo_by_zero_raises(self, eval_fn):
        with pytest.raises(ValueError, match="Modulo by zero"):
            eval_fn("a % b", {"a": 1.0, "b": 0.0})

    def test_unknown_column_raises(self, eval_fn):
        with pytest.raises(ValueError, match="Unknown column"):
            eval_fn("nonexistent + 1", {})

    def test_illegal_chars_raises(self, eval_fn):
        with pytest.raises(ValueError, match="Illegal"):
            eval_fn("a; import os", {"a": 1.0})

    def test_function_call_rejected(self, eval_fn):
        """eval() allowed __import__('os').system('...'), this must not."""
        with pytest.raises((ValueError, Exception)):
            eval_fn("__import__('os')", {})

    def test_dot_access_rejected(self, eval_fn):
        """Dot access (attribute lookup) is not supported."""
        with pytest.raises((ValueError, Exception)):
            eval_fn("a.real", {"a": 1.0})

    def test_double_star_rejected(self, eval_fn):
        with pytest.raises((ValueError, Exception)):
            eval_fn("a ** b", {"a": 2.0, "b": 3.0})

    def test_empty_expression_raises(self, eval_fn):
        with pytest.raises(Exception):
            eval_fn("", {})

    def test_mixin_eval_expression_uses_safe_parser(self):
        """Ensure DataTableMixin._eval_expression no longer calls eval()."""
        from djust_components.mixins.data_table import DataTableMixin

        mixin = DataTableMixin()
        # Normal arithmetic should work
        assert mixin._eval_expression("price * qty", {"price": "10", "qty": "5"}) == 50

        # Dangerous expressions should return "" (caught as error)
        assert mixin._eval_expression("__import__('os')", {"x": "1"}) == ""

    def test_mixin_computed_columns_integration(self):
        """End-to-end: computed columns use the safe evaluator."""
        from djust_components.mixins.data_table import DataTableMixin

        mixin = DataTableMixin()
        mixin.table_computed_columns = [
            {"key": "total", "expression": "price * qty + tax"},
        ]
        rows = [{"price": "10", "qty": "3", "tax": "5"}]
        result = mixin.evaluate_computed_columns(rows)
        assert result[0]["total"] == 35


# ---------------------------------------------------------------------------
# 7. Rust handler toast type/position allowlists
# ---------------------------------------------------------------------------

class TestRustHandlerToastAllowlists:
    def test_toast_container_invalid_type(self):
        from djust_components.rust_handlers import ToastContainerHandler

        handler = ToastContainerHandler()
        result = handler.render(
            {}, {"toasts": [{"type": "<script>", "id": "1", "message": "hi"}]}
        )
        assert "<script>" not in str(result)
        assert "toast-info" in str(result)

    def test_server_toast_container_invalid_position(self):
        from djust_components.rust_handlers import ServerToastContainerHandler

        handler = ServerToastContainerHandler()
        result = handler.render(
            ["position='\" onclick=\"alert(1)'"], {}
        )
        assert "onclick" not in str(result)
        assert "dj-toast-container--top-right" in str(result)

    def test_server_toast_container_valid_position(self):
        from djust_components.rust_handlers import ServerToastContainerHandler

        handler = ServerToastContainerHandler()
        result = handler.render(["position='bottom-left'"], {})
        assert "dj-toast-container--bottom-left" in str(result)
