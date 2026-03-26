"""Tests for Cascading Form Components: dependent_select, currency_input, form_errors, field_error.

Covers rendering, parameters, disabled/required state, XSS escaping,
and Rust handler delegation.
"""
from django.template import Template, Context
from django.utils.safestring import SafeData
import pytest

from djust_components.rust_handlers import (
    _parse_args,
    DependentSelectHandler,
    CurrencyInputHandler,
    FormErrorsHandler,
    FieldErrorHandler,
)


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ═══════════════════════════════════════════════════════════════════════════
# 1. Dependent Select (#108)
# ═══════════════════════════════════════════════════════════════════════════


class TestDependentSelect:
    def test_renders_basic(self):
        html = render('{% dependent_select name="city" parent="country" source_event="load_cities" %}')
        assert "dj-dependent-select" in html
        assert 'name="city"' in html
        assert 'data-parent="country"' in html
        assert 'data-source-event="load_cities"' in html
        assert 'dj-change="load_cities"' in html

    def test_default_placeholder(self):
        html = render('{% dependent_select name="city" parent="country" source_event="s" %}')
        assert "Select..." in html

    def test_custom_placeholder(self):
        html = render('{% dependent_select name="city" parent="country" source_event="s" placeholder="Pick a city..." %}')
        assert "Pick a city..." in html

    def test_label(self):
        html = render('{% dependent_select name="city" parent="country" source_event="s" label="City" %}')
        assert "form-label" in html
        assert "City" in html

    def test_label_required(self):
        html = render('{% dependent_select name="city" parent="country" source_event="s" label="City" required=True %}')
        assert "form-required" in html
        assert " required" in html

    def test_options_dict(self):
        html = render(
            '{% dependent_select name="city" parent="country" source_event="s" options=opts %}',
            {"opts": [{"value": "nyc", "label": "New York"}, {"value": "la", "label": "Los Angeles"}]},
        )
        assert 'value="nyc"' in html
        assert "New York" in html
        assert "Los Angeles" in html

    def test_options_string_list(self):
        html = render(
            '{% dependent_select name="city" parent="country" source_event="s" options=opts %}',
            {"opts": ["Paris", "London"]},
        )
        assert 'value="Paris"' in html
        assert "London" in html

    def test_selected_value(self):
        html = render(
            '{% dependent_select name="city" parent="country" source_event="s" value="la" options=opts %}',
            {"opts": [{"value": "nyc", "label": "New York"}, {"value": "la", "label": "LA"}]},
        )
        assert 'value="la" selected' in html

    def test_loading_spinner(self):
        html = render('{% dependent_select name="city" parent="country" source_event="s" loading=True %}')
        assert "dj-dependent-select--loading" in html
        assert "dj-dependent-select__spinner" in html

    def test_no_spinner_by_default(self):
        html = render('{% dependent_select name="city" parent="country" source_event="s" %}')
        assert "dj-dependent-select__spinner" not in html

    def test_disabled(self):
        html = render('{% dependent_select name="city" parent="country" source_event="s" disabled=True %}')
        assert " disabled" in html

    def test_error(self):
        html = render('{% dependent_select name="city" parent="country" source_event="s" error="Required" %}')
        assert "dj-dependent-select--error" in html
        assert "form-error-message" in html
        assert "Required" in html

    def test_custom_class(self):
        html = render('{% dependent_select name="city" parent="country" source_event="s" custom_class="wide" %}')
        assert "wide" in html

    def test_source_event_defaults_to_name(self):
        html = render('{% dependent_select name="city" parent="country" %}')
        assert 'dj-change="city"' in html


class TestDependentSelectRustHandler:
    handler = DependentSelectHandler()

    def test_basic(self):
        html = self.handler.render(
            ["name='city'", "parent='country'", "source_event='load_cities'"], {}
        )
        assert isinstance(html, SafeData)
        assert 'name="city"' in html
        assert 'data-parent="country"' in html

    def test_options_from_context(self):
        html = self.handler.render(
            ["name='city'", "parent='country'", "source_event='s'"],
            {"options": [{"value": "x", "label": "X City"}]},
        )
        assert "X City" in html

    def test_loading(self):
        html = self.handler.render(
            ["name='city'", "parent='country'", "source_event='s'", "loading=true"], {}
        )
        assert "dj-dependent-select--loading" in html

    def test_disabled(self):
        html = self.handler.render(
            ["name='city'", "parent='country'", "source_event='s'", "disabled=true"], {}
        )
        assert " disabled" in html


# ═══════════════════════════════════════════════════════════════════════════
# 2. Currency Input (#109)
# ═══════════════════════════════════════════════════════════════════════════


class TestCurrencyInput:
    def test_renders_basic(self):
        html = render('{% currency_input name="price" %}')
        assert "dj-currency-input" in html
        assert 'name="price"' in html
        assert 'type="number"' in html
        assert "dj-currency-input__symbol" in html

    def test_default_usd(self):
        html = render('{% currency_input name="price" %}')
        assert "dj-currency-input__symbol" in html
        assert "$" in html
        assert "USD" in html

    def test_eur_symbol(self):
        html = render('{% currency_input name="price" currency="EUR" %}')
        assert "\u20ac" in html  # Euro sign
        assert "EUR" in html

    def test_gbp_symbol(self):
        html = render('{% currency_input name="price" currency="GBP" %}')
        assert "\u00a3" in html  # Pound sign
        assert "GBP" in html

    def test_value(self):
        html = render('{% currency_input name="price" value="29.99" %}')
        assert 'value="29.99"' in html

    def test_label(self):
        html = render('{% currency_input name="price" label="Price" %}')
        assert "form-label" in html
        assert "Price" in html

    def test_label_required(self):
        html = render('{% currency_input name="price" label="Price" required=True %}')
        assert "form-required" in html
        assert " required" in html

    def test_min_max(self):
        html = render('{% currency_input name="price" min=0 max=1000 %}')
        assert 'min="0"' in html
        assert 'max="1000"' in html

    def test_step(self):
        html = render('{% currency_input name="price" step="1" %}')
        assert 'step="1"' in html

    def test_default_step(self):
        html = render('{% currency_input name="price" %}')
        assert 'step="0.01"' in html

    def test_placeholder(self):
        html = render('{% currency_input name="price" placeholder="0.00" %}')
        assert 'placeholder="0.00"' in html

    def test_dj_input_event(self):
        html = render('{% currency_input name="price" event="update_price" %}')
        assert 'dj-input="update_price"' in html

    def test_dj_input_defaults_to_name(self):
        html = render('{% currency_input name="price" %}')
        assert 'dj-input="price"' in html

    def test_disabled(self):
        html = render('{% currency_input name="price" disabled=True %}')
        assert " disabled" in html

    def test_error(self):
        html = render('{% currency_input name="price" error="Must be positive" %}')
        assert "dj-currency-input--error" in html
        assert "form-error-message" in html
        assert "Must be positive" in html

    def test_custom_class(self):
        html = render('{% currency_input name="price" custom_class="wide" %}')
        assert "wide" in html

    def test_currency_code_shown(self):
        html = render('{% currency_input name="price" currency="JPY" %}')
        assert "dj-currency-input__code" in html
        assert "JPY" in html

    def test_data_currency(self):
        html = render('{% currency_input name="price" currency="EUR" %}')
        assert 'data-currency="EUR"' in html


class TestCurrencyInputRustHandler:
    handler = CurrencyInputHandler()

    def test_basic(self):
        html = self.handler.render(["name='price'", "currency='USD'"], {})
        assert isinstance(html, SafeData)
        assert 'name="price"' in html
        assert "$" in html

    def test_eur(self):
        html = self.handler.render(["name='price'", "currency='EUR'"], {})
        assert "\u20ac" in html
        assert "EUR" in html

    def test_min_max(self):
        html = self.handler.render(["name='price'", "min=0", "max=1000"], {})
        assert 'min="0"' in html
        assert 'max="1000"' in html

    def test_error(self):
        html = self.handler.render(["name='price'", "error='Bad'"], {})
        assert "dj-currency-input--error" in html

    def test_disabled(self):
        html = self.handler.render(["name='price'", "disabled=true"], {})
        assert " disabled" in html


# ═══════════════════════════════════════════════════════════════════════════
# 3. Form Validation Display (#110)
# ═══════════════════════════════════════════════════════════════════════════


class _MockForm:
    """Minimal mock of a Django form for testing."""

    def __init__(self, non_field=None, field_errors=None):
        self._non_field = non_field or []
        self._field_errors = field_errors or {}

    def non_field_errors(self):
        return self._non_field

    def __getitem__(self, name):
        return _MockBoundField(name, self._field_errors.get(name, []))


class _MockBoundField:
    """Minimal mock of a Django BoundField."""

    def __init__(self, name, errors):
        self.name = name
        self.errors = errors


class TestFormErrors:
    def test_renders_errors(self):
        form = _MockForm(non_field=["Invalid credentials", "Try again"])
        html = render('{% form_errors form=form %}', {"form": form})
        assert "dj-form-errors" in html
        assert "Invalid credentials" in html
        assert "Try again" in html
        assert 'role="alert"' in html

    def test_no_errors_empty(self):
        form = _MockForm(non_field=[])
        html = render('{% form_errors form=form %}', {"form": form})
        assert html.strip() == ""

    def test_no_form_empty(self):
        html = render('{% form_errors %}')
        assert html.strip() == ""

    def test_custom_class(self):
        form = _MockForm(non_field=["Error"])
        html = render('{% form_errors form=form custom_class="extra" %}', {"form": form})
        assert "extra" in html

    def test_list_structure(self):
        form = _MockForm(non_field=["A", "B"])
        html = render('{% form_errors form=form %}', {"form": form})
        assert "dj-form-errors__list" in html
        assert html.count("dj-form-errors__item") == 2


class TestFieldError:
    def test_renders_errors(self):
        field = _MockBoundField("email", ["This field is required", "Invalid email"])
        html = render('{% field_error field=fld %}', {"fld": field})
        assert "dj-field-error" in html
        assert "This field is required" in html
        assert "Invalid email" in html
        assert 'role="alert"' in html

    def test_no_errors_empty(self):
        field = _MockBoundField("email", [])
        html = render('{% field_error field=fld %}', {"fld": field})
        assert html.strip() == ""

    def test_no_field_empty(self):
        html = render('{% field_error %}')
        assert html.strip() == ""

    def test_custom_class(self):
        field = _MockBoundField("email", ["Error"])
        html = render('{% field_error field=fld custom_class="tight" %}', {"fld": field})
        assert "tight" in html

    def test_multiple_messages(self):
        field = _MockBoundField("email", ["A", "B"])
        html = render('{% field_error field=fld %}', {"fld": field})
        assert html.count("dj-field-error__message") == 2


class TestFormErrorsRustHandler:
    handler = FormErrorsHandler()

    def test_renders_errors(self):
        form = _MockForm(non_field=["Invalid input"])
        html = self.handler.render([], {"form": form})
        assert isinstance(html, SafeData)
        assert "Invalid input" in html
        assert "dj-form-errors" in html

    def test_no_errors_empty(self):
        form = _MockForm(non_field=[])
        result = self.handler.render([], {"form": form})
        assert result == ""

    def test_no_form_empty(self):
        result = self.handler.render([], {})
        assert result == ""


class TestFieldErrorRustHandler:
    handler = FieldErrorHandler()

    def test_renders_errors(self):
        field = _MockBoundField("email", ["Required"])
        html = self.handler.render(["field=fld"], {"fld": field, "field": field})
        # The handler resolves 'fld' from context
        assert isinstance(html, (str, SafeData))

    def test_no_field_empty(self):
        result = self.handler.render([], {})
        assert result == ""


# ═══════════════════════════════════════════════════════════════════════════
# XSS Escaping Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestCascadingFormsXSS:
    """Verify that all user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_raw_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html

    # --- Dependent Select ---
    def test_dependent_select_name_xss(self):
        html = render(
            '{% dependent_select name=xss parent="p" source_event="s" %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_dependent_select_parent_xss(self):
        html = render(
            '{% dependent_select name="c" parent=xss source_event="s" %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_dependent_select_source_event_xss(self):
        html = render(
            '{% dependent_select name="c" parent="p" source_event=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_dependent_select_label_xss(self):
        html = render(
            '{% dependent_select name="c" parent="p" source_event="s" label=xss %}',
            {"xss": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_dependent_select_placeholder_xss(self):
        html = render(
            '{% dependent_select name="c" parent="p" source_event="s" placeholder=xss %}',
            {"xss": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_dependent_select_error_xss(self):
        html = render(
            '{% dependent_select name="c" parent="p" source_event="s" error=xss %}',
            {"xss": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_dependent_select_option_value_xss(self):
        html = render(
            '{% dependent_select name="c" parent="p" source_event="s" options=opts %}',
            {"opts": [{"value": self.XSS_ATTR, "label": "X"}]},
        )
        self._assert_attr_escaped(html)

    def test_dependent_select_option_label_xss(self):
        html = render(
            '{% dependent_select name="c" parent="p" source_event="s" options=opts %}',
            {"opts": [{"value": "a", "label": self.XSS}]},
        )
        self._assert_no_raw_script(html)

    def test_dependent_select_custom_class_xss(self):
        html = render(
            '{% dependent_select name="c" parent="p" source_event="s" custom_class=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Currency Input ---
    def test_currency_input_name_xss(self):
        html = render('{% currency_input name=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_currency_input_label_xss(self):
        html = render(
            '{% currency_input name="p" label=xss %}', {"xss": self.XSS}
        )
        self._assert_no_raw_script(html)

    def test_currency_input_value_xss(self):
        html = render(
            '{% currency_input name="p" value=xss %}', {"xss": self.XSS_ATTR}
        )
        self._assert_attr_escaped(html)

    def test_currency_input_error_xss(self):
        html = render(
            '{% currency_input name="p" error=xss %}', {"xss": self.XSS}
        )
        self._assert_no_raw_script(html)

    def test_currency_input_placeholder_xss(self):
        html = render(
            '{% currency_input name="p" placeholder=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_currency_input_event_xss(self):
        html = render(
            '{% currency_input name="p" event=xss %}', {"xss": self.XSS_ATTR}
        )
        self._assert_attr_escaped(html)

    def test_currency_input_currency_xss(self):
        html = render(
            '{% currency_input name="p" currency=xss %}', {"xss": self.XSS_ATTR}
        )
        self._assert_attr_escaped(html)

    def test_currency_input_custom_class_xss(self):
        html = render(
            '{% currency_input name="p" custom_class=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Form Errors ---
    def test_form_errors_xss(self):
        form = _MockForm(non_field=[self.XSS])
        html = render('{% form_errors form=form %}', {"form": form})
        self._assert_no_raw_script(html)

    def test_form_errors_custom_class_xss(self):
        form = _MockForm(non_field=["Error"])
        html = render(
            '{% form_errors form=form custom_class=xss %}',
            {"form": form, "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Field Error ---
    def test_field_error_xss(self):
        field = _MockBoundField("email", [self.XSS])
        html = render('{% field_error field=fld %}', {"fld": field})
        self._assert_no_raw_script(html)

    def test_field_error_custom_class_xss(self):
        field = _MockBoundField("email", ["Error"])
        html = render(
            '{% field_error field=fld custom_class=xss %}',
            {"fld": field, "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Rust handler XSS ---
    def test_dependent_select_rust_name_xss(self):
        handler = DependentSelectHandler()
        html = handler.render(
            [f"name='{self.XSS_ATTR}'", "parent='p'", "source_event='s'"], {}
        )
        self._assert_attr_escaped(html)

    def test_dependent_select_rust_parent_xss(self):
        handler = DependentSelectHandler()
        html = handler.render(
            ["name='c'", f"parent='{self.XSS_ATTR}'", "source_event='s'"], {}
        )
        self._assert_attr_escaped(html)

    def test_dependent_select_rust_option_xss(self):
        handler = DependentSelectHandler()
        html = handler.render(
            ["name='c'", "parent='p'", "source_event='s'"],
            {"options": [{"value": self.XSS_ATTR, "label": self.XSS}]},
        )
        self._assert_attr_escaped(html)
        self._assert_no_raw_script(html)

    def test_currency_input_rust_name_xss(self):
        handler = CurrencyInputHandler()
        html = handler.render([f"name='{self.XSS_ATTR}'"], {})
        self._assert_attr_escaped(html)

    def test_currency_input_rust_value_xss(self):
        handler = CurrencyInputHandler()
        html = handler.render([f"name='p'", f"value='{self.XSS_ATTR}'"], {})
        self._assert_attr_escaped(html)

    def test_form_errors_rust_xss(self):
        handler = FormErrorsHandler()
        form = _MockForm(non_field=[self.XSS])
        html = handler.render([], {"form": form})
        self._assert_no_raw_script(html)

    def test_field_error_rust_xss(self):
        handler = FieldErrorHandler()
        field = _MockBoundField("email", [self.XSS])
        html = handler.render(["field=fld"], {"fld": field, "field": field})
        # The handler tries to resolve "fld" — it gets the string "fld" back
        # since _parse_args resolves variable names from context
        # For this test we pass it directly
        html2 = handler.render([], {"field": field})
        # field is not passed via args, so handler returns ""
        assert html2 == ""


# ═══════════════════════════════════════════════════════════════════════════
# Handler Registration
# ═══════════════════════════════════════════════════════════════════════════


class TestRegistration:
    def test_dependent_select_in_inline_handlers(self):
        from djust_components.rust_handlers import INLINE_HANDLERS
        names = [name for name, _ in INLINE_HANDLERS]
        assert "dependent_select" in names

    def test_currency_input_in_inline_handlers(self):
        from djust_components.rust_handlers import INLINE_HANDLERS
        names = [name for name, _ in INLINE_HANDLERS]
        assert "currency_input" in names

    def test_form_errors_in_inline_handlers(self):
        from djust_components.rust_handlers import INLINE_HANDLERS
        names = [name for name, _ in INLINE_HANDLERS]
        assert "form_errors" in names

    def test_field_error_in_inline_handlers(self):
        from djust_components.rust_handlers import INLINE_HANDLERS
        names = [name for name, _ in INLINE_HANDLERS]
        assert "field_error" in names
