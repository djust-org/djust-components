"""Tests for helpers module and presets registry + dj_button preset integration."""
from django.template import Template, Context
import pytest

from djust_components.helpers import push_toast, confirm_action
from djust_components.presets import (
    register_preset,
    get_preset,
    list_presets,
    clear_presets,
)


# ── helpers ──────────────────────────────────────────────────────────────────

class TestPushToast:
    def test_default_values(self):
        result = push_toast("Hello")
        assert result == {
            "message": "Hello",
            "type": "info",
            "duration": 3000,
            "dismissible": True,
            "dismiss_event": None,
        }

    def test_success_type(self):
        result = push_toast("Saved!", type="success")
        assert result["type"] == "success"
        assert result["message"] == "Saved!"

    def test_error_type_with_duration(self):
        result = push_toast("Oops", type="error", duration=5000)
        assert result["type"] == "error"
        assert result["duration"] == 5000

    def test_warning_non_dismissible(self):
        result = push_toast("Watch out", type="warning", dismissible=False)
        assert result["dismissible"] is False

    def test_dismiss_event(self):
        result = push_toast("Note", dismiss_event="clear_toast")
        assert result["dismiss_event"] == "clear_toast"

    def test_zero_duration_means_no_auto_dismiss(self):
        result = push_toast("Sticky", duration=0)
        assert result["duration"] == 0

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Invalid toast type"):
            push_toast("Bad", type="critical")

    def test_negative_duration_raises(self):
        with pytest.raises(ValueError, match="duration must be >= 0"):
            push_toast("Bad", duration=-1)


class TestConfirmAction:
    def test_default_values(self):
        result = confirm_action("Delete this?")
        assert result == {
            "message": "Delete this?",
            "risk": "medium",
            "approve_event": "confirm",
            "reject_event": "cancel",
            "approve_label": "Confirm",
            "reject_label": "Cancel",
            "pending": True,
            "data": {},
        }

    def test_high_risk_with_custom_events(self):
        result = confirm_action(
            "Purge all records?",
            risk="high",
            approve_event="do_purge",
            reject_event="abort",
        )
        assert result["risk"] == "high"
        assert result["approve_event"] == "do_purge"
        assert result["reject_event"] == "abort"
        assert result["pending"] is True

    def test_custom_labels(self):
        result = confirm_action(
            "Continue?",
            approve_label="Yes, do it",
            reject_label="No way",
        )
        assert result["approve_label"] == "Yes, do it"
        assert result["reject_label"] == "No way"

    def test_data_passthrough(self):
        result = confirm_action(
            "Delete item?",
            data={"item_id": 42, "cascade": True},
        )
        assert result["data"] == {"item_id": 42, "cascade": True}

    def test_critical_risk(self):
        result = confirm_action("Nuke it", risk="critical")
        assert result["risk"] == "critical"

    def test_low_risk(self):
        result = confirm_action("Archive?", risk="low")
        assert result["risk"] == "low"

    def test_invalid_risk_raises(self):
        with pytest.raises(ValueError, match="Invalid risk level"):
            confirm_action("Bad", risk="extreme")

    def test_pending_always_true(self):
        """The pending flag is always True so templates can check it."""
        result = confirm_action("Test")
        assert result["pending"] is True


# ── presets registry ─────────────────────────────────────────────────────────

class TestPresetRegistry:
    def setup_method(self):
        """Snapshot and restore registry state around each test."""
        self._snapshot = dict(list_presets())

    def teardown_method(self):
        clear_presets()
        for tag, presets in self._snapshot.items():
            for name, params in presets.items():
                register_preset(tag, name, params)

    def test_register_and_get(self):
        register_preset("dj_test", "my-preset", {"variant": "danger", "size": "lg"})
        result = get_preset("dj_test", "my-preset")
        assert result == {"variant": "danger", "size": "lg"}

    def test_get_returns_copy(self):
        register_preset("dj_test", "cp", {"a": 1})
        first = get_preset("dj_test", "cp")
        first["a"] = 999
        second = get_preset("dj_test", "cp")
        assert second["a"] == 1

    def test_get_unknown_returns_none(self):
        assert get_preset("no_tag", "no_preset") is None
        assert get_preset("dj_button", "nonexistent_preset_xyz") is None

    def test_list_presets_all(self):
        result = list_presets()
        assert "dj_button" in result
        assert "danger-confirm" in result["dj_button"]

    def test_list_presets_by_tag(self):
        result = list_presets("dj_button")
        assert "danger-confirm" in result

    def test_clear_specific_tag(self):
        register_preset("dj_test_clear", "x", {"a": 1})
        clear_presets("dj_test_clear")
        assert get_preset("dj_test_clear", "x") is None

    def test_register_empty_tag_raises(self):
        with pytest.raises(ValueError, match="tag_name must not be empty"):
            register_preset("", "x", {})

    def test_register_empty_preset_raises(self):
        with pytest.raises(ValueError, match="preset_name must not be empty"):
            register_preset("dj_button", "", {})


# ── built-in button presets ──────────────────────────────────────────────────

class TestBuiltinButtonPresets:
    def test_danger_confirm_preset(self):
        p = get_preset("dj_button", "danger-confirm")
        assert p is not None
        assert p["variant"] == "danger"
        assert "icon" in p

    def test_danger_sm_preset(self):
        p = get_preset("dj_button", "danger-sm")
        assert p["variant"] == "danger"
        assert p["size"] == "sm"

    def test_primary_lg_preset(self):
        p = get_preset("dj_button", "primary-lg")
        assert p["variant"] == "primary"
        assert p["size"] == "lg"

    def test_ghost_sm_preset(self):
        p = get_preset("dj_button", "ghost-sm")
        assert p["variant"] == "ghost"
        assert p["size"] == "sm"

    def test_loading_preset(self):
        p = get_preset("dj_button", "loading")
        assert p["loading"] is True


# ── dj_button template tag preset integration ───────────────────────────────

def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


class TestDjButtonPreset:
    def test_preset_applies_variant(self):
        html = render('{% dj_button label="Delete" preset="danger-confirm" event="del" %}')
        assert "btn-danger" in html
        assert "Delete" in html

    def test_preset_applies_size(self):
        html = render('{% dj_button label="Go" preset="primary-lg" event="go" %}')
        assert "btn-lg" in html

    def test_explicit_kwarg_overrides_preset(self):
        # preset says danger, but explicit variant=success should win
        html = render('{% dj_button label="OK" preset="danger-confirm" variant="success" event="ok" %}')
        assert "btn-success" in html
        assert "btn-danger" not in html

    def test_preset_applies_icon(self):
        html = render('{% dj_button label="Warn" preset="danger-confirm" event="w" %}')
        # danger-confirm preset includes icon
        assert "btn-icon" in html

    def test_unknown_preset_ignored(self):
        html = render('{% dj_button label="Safe" preset="does-not-exist" event="x" %}')
        assert "btn-primary" in html
        assert "Safe" in html

    def test_loading_preset_disables(self):
        html = render('{% dj_button label="Wait" preset="loading" %}')
        assert "disabled" in html
        assert "btn-loading" in html

    def test_preset_with_no_label(self):
        """Preset alone without label still renders a valid button."""
        html = render('{% dj_button preset="ghost-sm" event="x" %}')
        assert "btn-ghost" in html
        assert "btn-sm" in html
