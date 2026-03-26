"""Tests for Confirmation Dialog and Popconfirm components."""
from django.template import Template, Context
import pytest

from djust_components.rust_handlers import (
    ConfirmDialogHandler,
    PopconfirmHandler,
    _parse_args,
)


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ═══════════════════════════════════════════════════════════════════════════
# Confirmation Dialog — Template Tag
# ═══════════════════════════════════════════════════════════════════════════

class TestConfirmDialog:
    def test_not_rendered_when_closed(self):
        html = render('{% confirm_dialog message="Delete?" confirm_event="delete" %}')
        assert html.strip() == ""

    def test_not_rendered_when_open_false(self):
        html = render(
            '{% confirm_dialog open=show message="Delete?" confirm_event="delete" %}',
            {"show": False},
        )
        assert html.strip() == ""

    def test_rendered_when_open(self):
        html = render(
            '{% confirm_dialog open=show message="Delete?" confirm_event="delete" %}',
            {"show": True},
        )
        assert "dj-confirm-dialog-backdrop" in html
        assert "dj-confirm-dialog" in html
        assert "Delete?" in html

    def test_default_title(self):
        html = render(
            '{% confirm_dialog open=show message="Sure?" confirm_event="ok" %}',
            {"show": True},
        )
        assert "Confirm" in html

    def test_custom_title(self):
        html = render(
            '{% confirm_dialog open=show title="Warning" message="Sure?" confirm_event="ok" %}',
            {"show": True},
        )
        assert "Warning" in html

    def test_confirm_event_wired(self):
        html = render(
            '{% confirm_dialog open=show message="Sure?" confirm_event="do_delete" %}',
            {"show": True},
        )
        assert 'dj-click="do_delete"' in html

    def test_cancel_event_wired(self):
        html = render(
            '{% confirm_dialog open=show message="Sure?" confirm_event="ok" cancel_event="nope" %}',
            {"show": True},
        )
        assert 'dj-click="nope"' in html

    def test_default_cancel_event(self):
        html = render(
            '{% confirm_dialog open=show message="Sure?" confirm_event="ok" %}',
            {"show": True},
        )
        assert 'dj-click="cancel"' in html

    def test_danger_variant(self):
        html = render(
            '{% confirm_dialog open=show variant="danger" message="Delete?" confirm_event="del" %}',
            {"show": True},
        )
        assert "dj-confirm-dialog--danger" in html

    def test_default_variant_no_class(self):
        html = render(
            '{% confirm_dialog open=show message="Sure?" confirm_event="ok" %}',
            {"show": True},
        )
        assert "dj-confirm-dialog--default" not in html

    def test_custom_labels(self):
        html = render(
            '{% confirm_dialog open=show message="Sure?" confirm_event="ok" '
            'confirm_label="Delete it" cancel_label="Keep" %}',
            {"show": True},
        )
        assert "Delete it" in html
        assert "Keep" in html

    def test_default_labels(self):
        html = render(
            '{% confirm_dialog open=show message="Sure?" confirm_event="ok" %}',
            {"show": True},
        )
        assert "Confirm" in html  # confirm label
        assert "Cancel" in html   # cancel label

    def test_custom_class(self):
        html = render(
            '{% confirm_dialog open=show message="Sure?" confirm_event="ok" custom_class="my-dialog" %}',
            {"show": True},
        )
        assert "my-dialog" in html

    def test_aria_alertdialog_role(self):
        html = render(
            '{% confirm_dialog open=show message="Sure?" confirm_event="ok" %}',
            {"show": True},
        )
        assert 'role="alertdialog"' in html
        assert 'aria-modal="true"' in html

    def test_backdrop_click_cancels(self):
        html = render(
            '{% confirm_dialog open=show message="Sure?" confirm_event="ok" cancel_event="dismiss" %}',
            {"show": True},
        )
        assert 'dj-confirm-dialog-backdrop" dj-click="dismiss"' in html

    def test_close_button_present(self):
        html = render(
            '{% confirm_dialog open=show message="Sure?" confirm_event="ok" %}',
            {"show": True},
        )
        assert "dj-confirm-dialog__close" in html

    def test_message_from_context_variable(self):
        html = render(
            '{% confirm_dialog open=show message=msg confirm_event="ok" %}',
            {"show": True, "msg": "Really delete this?"},
        )
        assert "Really delete this?" in html


# ═══════════════════════════════════════════════════════════════════════════
# Popconfirm — Template Tag
# ═══════════════════════════════════════════════════════════════════════════

class TestPopconfirm:
    def test_basic_render(self):
        html = render(
            '{% popconfirm message="Delete?" confirm_event="delete" %}'
            '<button>Delete</button>'
            '{% endpopconfirm %}'
        )
        assert "dj-popconfirm-wrapper" in html
        assert "Delete?" in html
        assert "<button>Delete</button>" in html

    def test_confirm_event_wired(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="do_it" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert 'dj-click="do_it"' in html

    def test_cancel_event_wired(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" cancel_event="nope" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert 'dj-click="nope"' in html

    def test_default_placement_top(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert "dj-popconfirm-top" in html

    def test_custom_placement_bottom(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" placement="bottom" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert "dj-popconfirm-bottom" in html

    def test_placement_left(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" placement="left" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert "dj-popconfirm-left" in html

    def test_placement_right(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" placement="right" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert "dj-popconfirm-right" in html

    def test_danger_variant(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" variant="danger" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert "dj-popconfirm--danger" in html

    def test_default_variant_no_class(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert "dj-popconfirm--default" not in html

    def test_custom_labels(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" '
            'confirm_label="Delete" cancel_label="Keep" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert "Delete" in html
        assert "Keep" in html

    def test_default_labels(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert ">Yes</button>" in html or "Yes</button>" in html
        assert ">No</button>" in html or "No</button>" in html

    def test_custom_class(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" custom_class="my-pop" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert "my-pop" in html

    def test_custom_id(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" id="pop-1" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert 'id="pop-1"' in html

    def test_auto_generated_id(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert 'id="popconfirm-' in html

    def test_tooltip_role(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert 'role="tooltip"' in html

    def test_trigger_wraps_content(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" %}'
            '<span class="btn">Click</span>'
            '{% endpopconfirm %}'
        )
        assert "dj-popconfirm-trigger" in html
        assert '<span class="btn">Click</span>' in html

    def test_js_toggle_present(self):
        html = render(
            '{% popconfirm message="Sure?" confirm_event="ok" %}'
            'Trigger{% endpopconfirm %}'
        )
        assert "data-open" in html  # toggle attribute referenced
        assert "onclick=" in html  # click handler present

    def test_message_from_context(self):
        html = render(
            '{% popconfirm message=msg confirm_event="ok" %}'
            'Trigger{% endpopconfirm %}',
            {"msg": "Really remove?"},
        )
        assert "Really remove?" in html


# ═══════════════════════════════════════════════════════════════════════════
# XSS Escaping
# ═══════════════════════════════════════════════════════════════════════════

class TestXSSEscaping:
    """Verify user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # --- Confirmation Dialog ---

    def test_confirm_dialog_message_xss(self):
        html = render(
            '{% confirm_dialog open=show message=xss confirm_event="ok" %}',
            {"show": True, "xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_confirm_dialog_title_xss(self):
        html = render(
            '{% confirm_dialog open=show title=xss message="m" confirm_event="ok" %}',
            {"show": True, "xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_confirm_dialog_confirm_event_xss(self):
        html = render(
            '{% confirm_dialog open=show message="m" confirm_event=xss %}',
            {"show": True, "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_confirm_dialog_cancel_event_xss(self):
        html = render(
            '{% confirm_dialog open=show message="m" confirm_event="ok" cancel_event=xss %}',
            {"show": True, "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_confirm_dialog_variant_xss(self):
        html = render(
            '{% confirm_dialog open=show message="m" confirm_event="ok" variant=xss %}',
            {"show": True, "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_confirm_dialog_confirm_label_xss(self):
        html = render(
            '{% confirm_dialog open=show message="m" confirm_event="ok" confirm_label=xss %}',
            {"show": True, "xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_confirm_dialog_cancel_label_xss(self):
        html = render(
            '{% confirm_dialog open=show message="m" confirm_event="ok" cancel_label=xss %}',
            {"show": True, "xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_confirm_dialog_custom_class_xss(self):
        html = render(
            '{% confirm_dialog open=show message="m" confirm_event="ok" custom_class=xss %}',
            {"show": True, "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Popconfirm ---

    def test_popconfirm_message_xss(self):
        html = render(
            '{% popconfirm message=xss confirm_event="ok" %}Trigger{% endpopconfirm %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_popconfirm_confirm_event_xss(self):
        html = render(
            '{% popconfirm message="m" confirm_event=xss %}Trigger{% endpopconfirm %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_popconfirm_cancel_event_xss(self):
        html = render(
            '{% popconfirm message="m" confirm_event="ok" cancel_event=xss %}Trigger{% endpopconfirm %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_popconfirm_confirm_label_xss(self):
        html = render(
            '{% popconfirm message="m" confirm_event="ok" confirm_label=xss %}Trigger{% endpopconfirm %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_popconfirm_cancel_label_xss(self):
        html = render(
            '{% popconfirm message="m" confirm_event="ok" cancel_label=xss %}Trigger{% endpopconfirm %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_popconfirm_placement_xss(self):
        html = render(
            '{% popconfirm message="m" confirm_event="ok" placement=xss %}Trigger{% endpopconfirm %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_popconfirm_variant_xss(self):
        html = render(
            '{% popconfirm message="m" confirm_event="ok" variant=xss %}Trigger{% endpopconfirm %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_popconfirm_custom_class_xss(self):
        html = render(
            '{% popconfirm message="m" confirm_event="ok" custom_class=xss %}Trigger{% endpopconfirm %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_popconfirm_id_xss(self):
        html = render(
            '{% popconfirm message="m" confirm_event="ok" id=xss %}Trigger{% endpopconfirm %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)


# ═══════════════════════════════════════════════════════════════════════════
# Rust Handlers
# ═══════════════════════════════════════════════════════════════════════════

class TestRustHandlers:
    """Test the Rust engine handler classes directly."""

    # --- ConfirmDialogHandler ---

    def test_confirm_dialog_handler_closed(self):
        handler = ConfirmDialogHandler()
        html = handler.render(["message='Delete?'", "confirm_event='del'"], {})
        assert html == ""

    def test_confirm_dialog_handler_open(self):
        handler = ConfirmDialogHandler()
        html = handler.render(
            ["open=True", "message='Delete this?'", "confirm_event='del'"], {}
        )
        assert "dj-confirm-dialog-backdrop" in html
        assert "Delete this?" in html
        assert 'dj-click="del"' in html

    def test_confirm_dialog_handler_danger(self):
        handler = ConfirmDialogHandler()
        html = handler.render(
            ["open=True", "variant='danger'", "message='m'", "confirm_event='ok'"], {}
        )
        assert "dj-confirm-dialog--danger" in html

    def test_confirm_dialog_handler_custom_labels(self):
        handler = ConfirmDialogHandler()
        html = handler.render(
            ["open=True", "message='m'", "confirm_event='ok'",
             "confirm_label='Remove'", "cancel_label='Keep'"], {}
        )
        assert "Remove" in html
        assert "Keep" in html

    def test_confirm_dialog_handler_custom_class(self):
        handler = ConfirmDialogHandler()
        html = handler.render(
            ["open=True", "message='m'", "confirm_event='ok'",
             "custom_class='extra'"], {}
        )
        assert "extra" in html

    def test_confirm_dialog_handler_xss(self):
        handler = ConfirmDialogHandler()
        html = handler.render(
            ["open=True", "message='<script>alert(1)</script>'",
             "confirm_event='ok'"], {}
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    # --- PopconfirmHandler ---

    def test_popconfirm_handler_basic(self):
        handler = PopconfirmHandler()
        html = handler.render(
            ["message='Sure?'", "confirm_event='go'"],
            "<button>Do it</button>", {}
        )
        assert "dj-popconfirm-wrapper" in html
        assert "Sure?" in html
        assert "<button>Do it</button>" in html

    def test_popconfirm_handler_placement(self):
        handler = PopconfirmHandler()
        html = handler.render(
            ["message='m'", "confirm_event='ok'", "placement='bottom'"],
            "trigger", {}
        )
        assert "dj-popconfirm-bottom" in html

    def test_popconfirm_handler_danger(self):
        handler = PopconfirmHandler()
        html = handler.render(
            ["message='m'", "confirm_event='ok'", "variant='danger'"],
            "trigger", {}
        )
        assert "dj-popconfirm--danger" in html

    def test_popconfirm_handler_custom_labels(self):
        handler = PopconfirmHandler()
        html = handler.render(
            ["message='m'", "confirm_event='ok'",
             "confirm_label='Delete'", "cancel_label='Keep'"],
            "trigger", {}
        )
        assert "Delete" in html
        assert "Keep" in html

    def test_popconfirm_handler_custom_class(self):
        handler = PopconfirmHandler()
        html = handler.render(
            ["message='m'", "confirm_event='ok'", "custom_class='my-pop'"],
            "trigger", {}
        )
        assert "my-pop" in html

    def test_popconfirm_handler_xss(self):
        handler = PopconfirmHandler()
        html = handler.render(
            ["message='<script>alert(1)</script>'", "confirm_event='ok'"],
            "trigger", {}
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_popconfirm_handler_event_xss(self):
        handler = PopconfirmHandler()
        html = handler.render(
            ["message='m'", """confirm_event='" onmouseover="alert(1)" x="'"""],
            "trigger", {}
        )
        assert '" onmouseover="' not in html
