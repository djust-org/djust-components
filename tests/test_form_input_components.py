"""Tests for form input components: multi_select, otp_input, number_stepper,
tag_input, input_group, dj_label, fieldset.

Covers rendering, parameters, disabled state, XSS escaping, and Rust handler delegation.
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

from django.template import Template, Context
from django.utils.safestring import SafeData
import pytest


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ═══════════════════════════════════════════════════════════════════════════
# 1. Multi-select
# ═══════════════════════════════════════════════════════════════════════════


class TestMultiSelect:
    def test_renders_basic(self):
        html = render(
            '{% multi_select name="tags" options=opts %}',
            {"opts": [{"value": "a", "label": "Alpha"}, {"value": "b", "label": "Beta"}]},
        )
        assert "multi-select" in html
        assert 'name="tags"' in html
        assert "Alpha" in html
        assert "Beta" in html

    def test_selected_tags_shown(self):
        html = render(
            '{% multi_select name="tags" options=opts selected=sel %}',
            {
                "opts": [{"value": "a", "label": "Alpha"}, {"value": "b", "label": "Beta"}],
                "sel": ["a"],
            },
        )
        assert "multi-select-tag" in html
        assert "Alpha" in html
        assert " checked" in html

    def test_search_input_present(self):
        html = render('{% multi_select name="t" options=opts %}', {"opts": []})
        assert "multi-select-search" in html
        assert 'placeholder="Search..."' in html

    def test_custom_placeholder(self):
        html = render(
            '{% multi_select name="t" options=opts placeholder="Filter..." %}',
            {"opts": []},
        )
        assert 'placeholder="Filter..."' in html

    def test_disabled(self):
        html = render(
            '{% multi_select name="t" options=opts disabled=True %}',
            {"opts": [{"value": "x", "label": "X"}]},
        )
        assert " disabled" in html

    def test_dj_change_event(self):
        html = render(
            '{% multi_select name="tags" options=opts event="update_tags" %}',
            {"opts": [{"value": "a", "label": "A"}]},
        )
        assert 'dj-change="update_tags"' in html

    def test_tuple_options(self):
        html = render(
            '{% multi_select name="t" options=opts %}',
            {"opts": [("v1", "Label 1"), ("v2", "Label 2")]},
        )
        assert "Label 1" in html
        assert 'value="v1"' in html

    def test_label(self):
        html = render(
            '{% multi_select name="t" options=opts label="Pick items" %}',
            {"opts": []},
        )
        assert "Pick items" in html
        assert "form-label" in html

    def test_no_selected(self):
        html = render(
            '{% multi_select name="t" options=opts %}',
            {"opts": [{"value": "a", "label": "A"}]},
        )
        assert "multi-select-tag" not in html


# ═══════════════════════════════════════════════════════════════════════════
# 2. OTP Input
# ═══════════════════════════════════════════════════════════════════════════


class TestOtpInput:
    def test_renders_6_digits_default(self):
        html = render('{% otp_input name="code" %}')
        assert html.count("otp-digit") == 6

    def test_renders_4_digits(self):
        html = render('{% otp_input name="code" digits=4 %}')
        assert html.count("otp-digit") == 4

    def test_hidden_input_present(self):
        html = render('{% otp_input name="code" %}')
        assert 'name="code"' in html
        assert "otp-hidden" in html

    def test_dj_change_event(self):
        html = render('{% otp_input name="code" event="verify_otp" %}')
        assert 'dj-change="verify_otp"' in html

    def test_label(self):
        html = render('{% otp_input name="code" label="Enter code" %}')
        assert "Enter code" in html
        assert "form-label" in html

    def test_disabled(self):
        html = render('{% otp_input name="code" disabled=True %}')
        assert " disabled" in html

    def test_clamps_digits(self):
        html = render('{% otp_input name="code" digits=0 %}')
        # min is 1
        assert html.count("otp-digit") == 1

    def test_inputmode_numeric(self):
        html = render('{% otp_input name="code" digits=4 %}')
        assert 'inputmode="numeric"' in html


# ═══════════════════════════════════════════════════════════════════════════
# 3. Number Stepper
# ═══════════════════════════════════════════════════════════════════════════


class TestNumberStepper:
    def test_renders_basic(self):
        html = render('{% number_stepper name="qty" %}')
        assert "number-stepper" in html
        assert 'name="qty"' in html
        assert "number-stepper-dec" in html
        assert "number-stepper-inc" in html

    def test_value(self):
        html = render('{% number_stepper name="qty" value=5 %}')
        assert 'value="5"' in html

    def test_min_max(self):
        html = render('{% number_stepper name="qty" min_val=1 max_val=99 %}')
        assert 'min="1"' in html
        assert 'max="99"' in html

    def test_step(self):
        html = render('{% number_stepper name="qty" step=5 %}')
        assert 'step="5"' in html

    def test_dj_click_event(self):
        html = render('{% number_stepper name="qty" event="update_qty" %}')
        assert 'dj-click="update_qty"' in html

    def test_dj_change_event(self):
        html = render('{% number_stepper name="qty" event="update_qty" %}')
        assert 'dj-change="update_qty"' in html

    def test_label(self):
        html = render('{% number_stepper name="qty" label="Quantity" %}')
        assert "Quantity" in html
        assert "form-label" in html

    def test_disabled(self):
        html = render('{% number_stepper name="qty" disabled=True %}')
        assert " disabled" in html

    def test_dec_inc_data_values(self):
        html = render('{% number_stepper name="qty" %}')
        assert 'data-value="dec"' in html
        assert 'data-value="inc"' in html


# ═══════════════════════════════════════════════════════════════════════════
# 4. Tag Input
# ═══════════════════════════════════════════════════════════════════════════


class TestTagInput:
    def test_renders_basic(self):
        html = render('{% tag_input name="tags" %}')
        assert "tag-input" in html
        assert "tag-input-field" in html

    def test_existing_tags(self):
        html = render(
            '{% tag_input name="tags" tags=t %}',
            {"t": ["python", "django"]},
        )
        assert "tag-input-tag" in html
        assert "python" in html
        assert "django" in html

    def test_tag_hidden_inputs(self):
        html = render(
            '{% tag_input name="tags" tags=t %}',
            {"t": ["python"]},
        )
        assert 'name="tags"' in html
        assert 'value="python"' in html

    def test_suggestions_datalist(self):
        html = render(
            '{% tag_input name="tags" suggestions=s %}',
            {"s": ["python", "rust", "go"]},
        )
        assert "datalist" in html
        assert 'value="python"' in html
        assert 'value="rust"' in html

    def test_dj_event(self):
        html = render('{% tag_input name="tags" event="add_tag" %}')
        assert 'dj-keydown.enter="add_tag"' in html

    def test_placeholder(self):
        html = render('{% tag_input name="tags" placeholder="Type here..." %}')
        assert 'placeholder="Type here..."' in html

    def test_label(self):
        html = render('{% tag_input name="tags" label="Tags" %}')
        assert "Tags" in html
        assert "form-label" in html

    def test_disabled(self):
        html = render('{% tag_input name="tags" disabled=True %}')
        assert " disabled" in html

    def test_remove_data_value(self):
        html = render(
            '{% tag_input name="tags" tags=t event="handle_tag" %}',
            {"t": ["python"]},
        )
        assert 'data-value="remove:python"' in html


# ═══════════════════════════════════════════════════════════════════════════
# 5. Input Group
# ═══════════════════════════════════════════════════════════════════════════


class TestInputGroup:
    def test_renders_basic(self):
        html = render(
            '{% input_group %}'
            '{% input_addon %}${% endinput_addon %}'
            '{% dj_input name="price" %}'
            '{% endinput_group %}'
        )
        assert "input-group" in html
        assert "input-addon" in html
        assert "$" in html

    def test_suffix_addon(self):
        html = render(
            '{% input_group %}'
            '{% input_addon position="suffix" %}.00{% endinput_addon %}'
            '{% endinput_group %}'
        )
        assert "input-addon-suffix" in html
        assert ".00" in html

    def test_size_variant(self):
        html = render('{% input_group size="lg" %}content{% endinput_group %}')
        assert "input-group-lg" in html

    def test_error_state(self):
        html = render(
            '{% input_group error="Required" %}content{% endinput_group %}'
        )
        assert "input-group-error" in html
        assert "Required" in html
        assert "form-error-message" in html

    def test_no_error_no_class(self):
        html = render('{% input_group %}content{% endinput_group %}')
        assert "input-group-error" not in html


# ═══════════════════════════════════════════════════════════════════════════
# 6. Label
# ═══════════════════════════════════════════════════════════════════════════


class TestDjLabel:
    def test_renders_basic(self):
        html = render('{% dj_label for="email" %}Email{% enddj_label %}')
        assert "<label" in html
        assert 'for="email"' in html
        assert "Email" in html
        assert "form-label" in html

    def test_required(self):
        html = render('{% dj_label for="email" required=True %}Email{% enddj_label %}')
        assert "form-required" in html
        assert "*" in html

    def test_no_for(self):
        html = render('{% dj_label %}Name{% enddj_label %}')
        assert "<label" in html
        assert "Name" in html
        assert ' for="' not in html

    def test_extra_class(self):
        html = render('{% dj_label class="custom-cls" %}X{% enddj_label %}')
        assert "custom-cls" in html
        assert "form-label" in html

    def test_not_required(self):
        html = render('{% dj_label for="x" %}X{% enddj_label %}')
        assert "form-required" not in html


# ═══════════════════════════════════════════════════════════════════════════
# 7. Fieldset
# ═══════════════════════════════════════════════════════════════════════════


class TestFieldset:
    def test_renders_basic(self):
        html = render(
            '{% fieldset legend="Account" %}fields here{% endfieldset %}'
        )
        assert "<fieldset" in html
        assert "Account" in html
        assert "fieldset-legend" in html
        assert "fields here" in html

    def test_no_legend(self):
        html = render('{% fieldset %}content{% endfieldset %}')
        assert "<fieldset" in html
        assert "fieldset-legend" not in html

    def test_disabled(self):
        html = render('{% fieldset disabled=True %}content{% endfieldset %}')
        assert " disabled" in html

    def test_extra_class(self):
        html = render('{% fieldset class="my-fs" %}content{% endfieldset %}')
        assert "my-fs" in html
        assert "fieldset" in html

    def test_fieldset_content_wrapper(self):
        html = render('{% fieldset %}content{% endfieldset %}')
        assert "fieldset-content" in html


# ═══════════════════════════════════════════════════════════════════════════
# XSS Escaping Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestFormInputXSS:
    """Verify that all user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_raw_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html

    # Multi-select
    def test_multi_select_name_xss(self):
        html = render(
            '{% multi_select name=xss options=opts %}',
            {"xss": self.XSS_ATTR, "opts": []},
        )
        self._assert_attr_escaped(html)

    def test_multi_select_label_xss(self):
        html = render(
            '{% multi_select name="t" label=xss options=opts %}',
            {"xss": self.XSS, "opts": []},
        )
        self._assert_no_raw_script(html)

    def test_multi_select_option_label_xss(self):
        html = render(
            '{% multi_select name="t" options=opts selected=sel %}',
            {
                "opts": [{"value": "a", "label": self.XSS}],
                "sel": ["a"],
            },
        )
        self._assert_no_raw_script(html)

    def test_multi_select_option_value_xss(self):
        html = render(
            '{% multi_select name="t" options=opts %}',
            {"opts": [{"value": self.XSS_ATTR, "label": "X"}]},
        )
        self._assert_attr_escaped(html)

    # OTP Input
    def test_otp_name_xss(self):
        html = render(
            '{% otp_input name=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_otp_label_xss(self):
        html = render(
            '{% otp_input name="c" label=xss %}',
            {"xss": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_otp_event_xss(self):
        html = render(
            '{% otp_input name="c" event=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Number Stepper
    def test_stepper_name_xss(self):
        html = render(
            '{% number_stepper name=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_stepper_label_xss(self):
        html = render(
            '{% number_stepper name="q" label=xss %}',
            {"xss": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_stepper_event_xss(self):
        html = render(
            '{% number_stepper name="q" event=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Tag Input
    def test_tag_input_name_xss(self):
        html = render(
            '{% tag_input name=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_tag_input_tag_value_xss(self):
        html = render(
            '{% tag_input name="t" tags=t %}',
            {"t": [self.XSS]},
        )
        self._assert_no_raw_script(html)

    def test_tag_input_suggestion_xss(self):
        html = render(
            '{% tag_input name="t" suggestions=s %}',
            {"s": [self.XSS_ATTR]},
        )
        self._assert_attr_escaped(html)

    def test_tag_input_label_xss(self):
        html = render(
            '{% tag_input name="t" label=xss %}',
            {"xss": self.XSS},
        )
        self._assert_no_raw_script(html)

    # Input Group
    def test_input_group_error_xss(self):
        html = render(
            '{% input_group error=xss %}x{% endinput_group %}',
            {"xss": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_input_addon_position_xss(self):
        html = render(
            '{% input_addon position=xss %}${% endinput_addon %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Label
    def test_label_for_xss(self):
        html = render(
            '{% dj_label for=xss %}X{% enddj_label %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_label_class_xss(self):
        html = render(
            '{% dj_label class=xss %}X{% enddj_label %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Fieldset
    def test_fieldset_legend_xss(self):
        html = render(
            '{% fieldset legend=xss %}x{% endfieldset %}',
            {"xss": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_fieldset_class_xss(self):
        html = render(
            '{% fieldset class=xss %}x{% endfieldset %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)


# ═══════════════════════════════════════════════════════════════════════════
# Rust Handler Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestMultiSelectHandler:
    def test_renders(self):
        from djust_components.rust_handlers import MultiSelectHandler
        h = MultiSelectHandler()
        result = h.render(
            ['name="tags"'],
            {"tags_opts": [{"value": "a", "label": "A"}]},
        )
        assert "multi-select" in result

    def test_xss_name(self):
        from djust_components.rust_handlers import MultiSelectHandler
        h = MultiSelectHandler()
        result = h.render(['name="<script>alert(1)</script>"'], {})
        assert "<script>" not in result


class TestOtpInputHandler:
    def test_renders(self):
        from djust_components.rust_handlers import OtpInputHandler
        h = OtpInputHandler()
        result = h.render(['name="code"', 'digits=4'], {})
        assert "otp-input" in result
        assert result.count("otp-digit") == 4

    def test_xss_name(self):
        from djust_components.rust_handlers import OtpInputHandler
        h = OtpInputHandler()
        result = h.render(['name="<script>alert(1)</script>"'], {})
        assert "<script>" not in result


class TestNumberStepperHandler:
    def test_renders(self):
        from djust_components.rust_handlers import NumberStepperHandler
        h = NumberStepperHandler()
        result = h.render(['name="qty"', 'value=5'], {})
        assert "number-stepper" in result
        assert 'value="5"' in result

    def test_xss_name(self):
        from djust_components.rust_handlers import NumberStepperHandler
        h = NumberStepperHandler()
        result = h.render(['name="<script>alert(1)</script>"'], {})
        assert "<script>" not in result


class TestTagInputHandler:
    def test_renders(self):
        from djust_components.rust_handlers import TagInputHandler
        h = TagInputHandler()
        result = h.render(['name="tags"'], {"my_tags": ["python"]})
        assert "tag-input" in result

    def test_xss_name(self):
        from djust_components.rust_handlers import TagInputHandler
        h = TagInputHandler()
        result = h.render(['name="<script>alert(1)</script>"'], {})
        assert "<script>" not in result


class TestInputGroupHandler:
    def test_renders(self):
        from djust_components.rust_handlers import InputGroupHandler
        h = InputGroupHandler()
        result = h.render([], "<input>", {})
        assert "input-group" in result
        assert isinstance(result, SafeData)

    def test_error(self):
        from djust_components.rust_handlers import InputGroupHandler
        h = InputGroupHandler()
        result = h.render(['error="Required"'], "<input>", {})
        assert "input-group-error" in result
        assert "Required" in result

    def test_xss_error(self):
        from djust_components.rust_handlers import InputGroupHandler
        h = InputGroupHandler()
        result = h.render(['error="<script>alert(1)</script>"'], "<input>", {})
        assert "<script>" not in result


class TestInputAddonHandler:
    def test_renders(self):
        from djust_components.rust_handlers import InputAddonHandler
        h = InputAddonHandler()
        result = h.render([], "$", {})
        assert "input-addon" in result
        assert "$" in result
        assert isinstance(result, SafeData)

    def test_suffix(self):
        from djust_components.rust_handlers import InputAddonHandler
        h = InputAddonHandler()
        result = h.render(['position="suffix"'], ".00", {})
        assert "input-addon-suffix" in result

    def test_xss_position(self):
        from djust_components.rust_handlers import InputAddonHandler
        h = InputAddonHandler()
        result = h.render(['position="<script>alert(1)</script>"'], "$", {})
        assert "<script>" not in result


class TestDjLabelHandler:
    def test_renders(self):
        from djust_components.rust_handlers import DjLabelHandler
        h = DjLabelHandler()
        result = h.render(['for="email"'], "Email", {})
        assert "<label" in result
        assert 'for="email"' in result
        assert "Email" in result
        assert isinstance(result, SafeData)

    def test_required(self):
        from djust_components.rust_handlers import DjLabelHandler
        h = DjLabelHandler()
        result = h.render(['for="email"', "required=True"], "Email", {})
        assert "form-required" in result
        assert "*" in result

    def test_xss_for(self):
        from djust_components.rust_handlers import DjLabelHandler
        h = DjLabelHandler()
        result = h.render(['for="<script>alert(1)</script>"'], "X", {})
        assert "<script>" not in result


class TestFieldsetHandler:
    def test_renders(self):
        from djust_components.rust_handlers import FieldsetHandler
        h = FieldsetHandler()
        result = h.render(['legend="Account"'], "fields", {})
        assert "<fieldset" in result
        assert "Account" in result
        assert "fieldset-legend" in result
        assert isinstance(result, SafeData)

    def test_disabled(self):
        from djust_components.rust_handlers import FieldsetHandler
        h = FieldsetHandler()
        result = h.render(["disabled=True"], "fields", {})
        assert " disabled" in result

    def test_no_legend(self):
        from djust_components.rust_handlers import FieldsetHandler
        h = FieldsetHandler()
        result = h.render([], "fields", {})
        assert "fieldset-legend" not in result

    def test_xss_legend(self):
        from djust_components.rust_handlers import FieldsetHandler
        h = FieldsetHandler()
        result = h.render(['legend="<script>alert(1)</script>"'], "body", {})
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_xss_class(self):
        from djust_components.rust_handlers import FieldsetHandler
        h = FieldsetHandler()
        result = h.render(['class="\" onmouseover=\"alert(1)\" x=\""'], "body", {})
        assert '" onmouseover="' not in result


# ═══════════════════════════════════════════════════════════════════════════
# Registration Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestRegistration:
    """Verify all new handlers are registered in the INLINE/BLOCK lists."""

    def test_inline_handlers_registered(self):
        from djust_components.rust_handlers import INLINE_HANDLERS
        names = [name for name, _ in INLINE_HANDLERS]
        assert "multi_select" in names
        assert "otp_input" in names
        assert "number_stepper" in names
        assert "tag_input" in names

    def test_block_handlers_registered(self):
        from djust_components.rust_handlers import BLOCK_HANDLERS
        names = [name for name, _, _ in BLOCK_HANDLERS]
        assert "input_group" in names
        assert "input_addon" in names
        assert "dj_label" in names
        assert "fieldset" in names
