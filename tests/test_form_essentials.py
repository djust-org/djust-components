"""Tests for Form Essentials (v1.5): slider, search_input, password_input, autocomplete.

Covers rendering, parameters, disabled state, range mode, XSS escaping,
and Rust handler delegation.
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

from djust_components.rust_handlers import (
    _parse_args,
    SliderHandler,
    SearchInputHandler,
    PasswordInputHandler,
    AutocompleteHandler,
)


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ═══════════════════════════════════════════════════════════════════════════
# 1. Slider / Range
# ═══════════════════════════════════════════════════════════════════════════


class TestSlider:
    def test_renders_basic(self):
        html = render('{% slider name="price" min=0 max=100 value=50 %}')
        assert "dj-slider" in html
        assert 'name="price"' in html
        assert 'type="range"' in html
        assert 'value="50"' in html
        assert 'min="0"' in html
        assert 'max="100"' in html

    def test_default_value(self):
        html = render('{% slider name="vol" min=0 max=10 %}')
        assert 'value="0"' in html

    def test_step(self):
        html = render('{% slider name="p" step=5 %}')
        assert 'step="5"' in html

    def test_label(self):
        html = render('{% slider name="p" label="Price" %}')
        assert "dj-slider__label" in html
        assert "Price" in html

    def test_no_label(self):
        html = render('{% slider name="p" %}')
        assert "dj-slider__label" not in html

    def test_dj_input_event(self):
        html = render('{% slider name="p" event="update_price" %}')
        assert 'dj-input="update_price"' in html

    def test_dj_input_defaults_to_name(self):
        html = render('{% slider name="vol" %}')
        assert 'dj-input="vol"' in html

    def test_disabled(self):
        html = render('{% slider name="p" disabled=True %}')
        assert " disabled" in html

    def test_show_value(self):
        html = render('{% slider name="p" value=42 show_value=True %}')
        assert "dj-slider__value" in html
        assert "42" in html

    def test_hide_value(self):
        html = render('{% slider name="p" show_value=False %}')
        assert "dj-slider__value" not in html

    def test_range_mode(self):
        html = render('{% slider name="price" min=0 max=1000 value=200 value_end=800 %}')
        assert "dj-slider--range" in html
        assert 'name="price"' in html
        assert 'name="price_end"' in html
        assert 'value="200"' in html
        assert 'value="800"' in html

    def test_range_mode_two_inputs(self):
        html = render('{% slider name="r" value=10 value_end=90 %}')
        assert html.count('type="range"') == 2

    def test_show_ticks(self):
        html = render('{% slider name="p" min=0 max=10 step=2 show_ticks=True %}')
        assert "dj-slider__ticks" in html
        assert "dj-slider__tick" in html

    def test_no_ticks_by_default(self):
        html = render('{% slider name="p" %}')
        assert "dj-slider__ticks" not in html

    def test_custom_class(self):
        html = render('{% slider name="p" custom_class="my-slider" %}')
        assert "my-slider" in html

    def test_is_safe(self):
        t = Template("{% load djust_components %}{% slider name='p' %}")
        result = t.render(Context({}))
        # Should not be double-escaped
        assert "&amp;" not in result or "amp;" not in result


class TestSliderRustHandler:
    handler = SliderHandler()

    def test_basic(self):
        html = self.handler.render(["name='price'", "min=0", "max=100", "value=50"], {})
        assert isinstance(html, SafeData)
        assert 'name="price"' in html
        assert 'value="50"' in html

    def test_range(self):
        html = self.handler.render(
            ["name='r'", "value=20", "value_end=80"], {}
        )
        assert "dj-slider--range" in html
        assert html.count('type="range"') == 2

    def test_disabled(self):
        html = self.handler.render(["name='p'", "disabled=true"], {})
        assert " disabled" in html


# ═══════════════════════════════════════════════════════════════════════════
# 2. Search Input
# ═══════════════════════════════════════════════════════════════════════════


class TestSearchInput:
    def test_renders_basic(self):
        html = render('{% search_input name="q" %}')
        assert "dj-search-input" in html
        assert 'type="search"' in html
        assert 'name="q"' in html

    def test_default_placeholder(self):
        html = render('{% search_input name="q" %}')
        assert 'placeholder="Search..."' in html

    def test_custom_placeholder(self):
        html = render('{% search_input name="q" placeholder="Find items..." %}')
        assert 'placeholder="Find items..."' in html

    def test_value(self):
        html = render('{% search_input name="q" value="hello" %}')
        assert 'value="hello"' in html

    def test_label(self):
        html = render('{% search_input name="q" label="Search" %}')
        assert "dj-search-input__label" in html
        assert "Search" in html

    def test_search_icon(self):
        html = render('{% search_input name="q" %}')
        assert "dj-search-input__icon" in html
        assert "<svg" in html

    def test_clear_button(self):
        html = render('{% search_input name="q" %}')
        assert "dj-search-input__clear" in html
        assert "Clear search" in html

    def test_dj_input_event(self):
        html = render('{% search_input name="q" event="search" %}')
        assert 'dj-input="search"' in html

    def test_dj_input_defaults_to_name(self):
        html = render('{% search_input name="q" %}')
        assert 'dj-input="q"' in html

    def test_debounce(self):
        html = render('{% search_input name="q" debounce=500 %}')
        assert 'data-debounce="500"' in html

    def test_default_debounce(self):
        html = render('{% search_input name="q" %}')
        assert 'data-debounce="300"' in html

    def test_loading_spinner(self):
        html = render('{% search_input name="q" loading=True %}')
        assert "dj-search-input--loading" in html
        assert "dj-search-input__spinner" in html

    def test_no_spinner_by_default(self):
        html = render('{% search_input name="q" %}')
        assert "dj-search-input__spinner" not in html

    def test_disabled(self):
        html = render('{% search_input name="q" disabled=True %}')
        assert " disabled" in html

    def test_custom_class(self):
        html = render('{% search_input name="q" custom_class="wide" %}')
        assert "wide" in html


class TestSearchInputRustHandler:
    handler = SearchInputHandler()

    def test_basic(self):
        html = self.handler.render(["name='q'"], {})
        assert isinstance(html, SafeData)
        assert 'name="q"' in html
        assert "dj-search-input__icon" in html

    def test_loading(self):
        html = self.handler.render(["name='q'", "loading=true"], {})
        assert "dj-search-input--loading" in html

    def test_event(self):
        html = self.handler.render(["name='q'", "event='do_search'"], {})
        assert 'dj-input="do_search"' in html


# ═══════════════════════════════════════════════════════════════════════════
# 3. Password Input
# ═══════════════════════════════════════════════════════════════════════════


class TestPasswordInput:
    def test_renders_basic(self):
        html = render('{% password_input name="pwd" %}')
        assert "dj-password-input" in html
        assert 'type="password"' in html
        assert 'name="pwd"' in html

    def test_label(self):
        html = render('{% password_input name="pwd" label="Password" %}')
        assert "form-label" in html
        assert "Password" in html

    def test_label_required(self):
        html = render('{% password_input name="pwd" label="Password" required=True %}')
        assert "form-required" in html
        assert " required" in html

    def test_toggle_button(self):
        html = render('{% password_input name="pwd" %}')
        assert "dj-password-input__toggle" in html
        assert "Toggle password visibility" in html

    def test_eye_icon(self):
        html = render('{% password_input name="pwd" %}')
        assert "dj-password-input__eye" in html
        assert "<svg" in html

    def test_dj_input_event(self):
        html = render('{% password_input name="pwd" event="check_pwd" %}')
        assert 'dj-input="check_pwd"' in html

    def test_dj_input_defaults_to_name(self):
        html = render('{% password_input name="pwd" %}')
        assert 'dj-input="pwd"' in html

    def test_error(self):
        html = render('{% password_input name="pwd" error="Too short" %}')
        assert "dj-password-input--error" in html
        assert "form-error-message" in html
        assert "Too short" in html

    def test_disabled(self):
        html = render('{% password_input name="pwd" disabled=True %}')
        assert " disabled" in html

    def test_placeholder(self):
        html = render('{% password_input name="pwd" placeholder="Enter password" %}')
        assert 'placeholder="Enter password"' in html

    def test_strength_meter_hidden_by_default(self):
        html = render('{% password_input name="pwd" %}')
        assert "dj-password-strength" not in html

    def test_strength_meter_shown(self):
        html = render('{% password_input name="pwd" show_strength=True strength=3 %}')
        assert "dj-password-strength" in html
        assert "dj-password-strength--3" in html
        assert html.count("dj-password-strength__bar") == 4

    def test_strength_0(self):
        html = render('{% password_input name="pwd" show_strength=True strength=0 %}')
        assert "dj-password-strength--0" in html

    def test_strength_4(self):
        html = render('{% password_input name="pwd" show_strength=True strength=4 %}')
        assert "dj-password-strength--4" in html

    def test_custom_class(self):
        html = render('{% password_input name="pwd" custom_class="wide" %}')
        assert "wide" in html


class TestPasswordInputRustHandler:
    handler = PasswordInputHandler()

    def test_basic(self):
        html = self.handler.render(["name='pwd'"], {})
        assert isinstance(html, SafeData)
        assert 'type="password"' in html
        assert "dj-password-input__toggle" in html

    def test_strength(self):
        html = self.handler.render(
            ["name='pwd'", "show_strength=true", "strength=2"], {}
        )
        assert "dj-password-strength--2" in html

    def test_error(self):
        html = self.handler.render(["name='pwd'", "error='Bad'"], {})
        assert "dj-password-input--error" in html


# ═══════════════════════════════════════════════════════════════════════════
# 4. Autocomplete
# ═══════════════════════════════════════════════════════════════════════════


class TestAutocomplete:
    def test_renders_basic(self):
        html = render('{% autocomplete name="city" source_event="search_cities" %}')
        assert "dj-autocomplete" in html
        assert 'name="city_display"' in html
        assert 'name="city"' in html  # hidden input
        assert 'role="combobox"' in html

    def test_label(self):
        html = render('{% autocomplete name="city" label="City" source_event="s" %}')
        assert "form-label" in html
        assert "City" in html

    def test_placeholder(self):
        html = render('{% autocomplete name="city" placeholder="Type a city..." source_event="s" %}')
        assert 'placeholder="Type a city..."' in html

    def test_value_and_display(self):
        html = render(
            '{% autocomplete name="city" value="NYC" display_value="New York" source_event="s" %}'
        )
        assert 'value="New York"' in html  # display input
        assert 'value="NYC"' in html  # hidden input

    def test_source_event(self):
        html = render('{% autocomplete name="city" source_event="search_cities" %}')
        assert 'data-source-event="search_cities"' in html
        assert 'dj-input="search_cities"' in html

    def test_debounce(self):
        html = render('{% autocomplete name="city" source_event="s" debounce=500 %}')
        assert 'data-debounce="500"' in html

    def test_min_chars(self):
        html = render('{% autocomplete name="city" source_event="s" min_chars=3 %}')
        assert 'data-min-chars="3"' in html

    def test_suggestions_dict(self):
        html = render(
            '{% autocomplete name="city" source_event="s" suggestions=sugs %}',
            {"sugs": [{"value": "nyc", "label": "New York"}, {"value": "la", "label": "Los Angeles"}]},
        )
        assert "dj-autocomplete__item" in html
        assert "New York" in html
        assert "Los Angeles" in html
        assert 'data-value="nyc"' in html

    def test_suggestions_tuple(self):
        html = render(
            '{% autocomplete name="city" source_event="s" suggestions=sugs %}',
            {"sugs": [("nyc", "New York")]},
        )
        assert 'data-value="nyc"' in html
        assert "New York" in html

    def test_suggestions_string(self):
        html = render(
            '{% autocomplete name="city" source_event="s" suggestions=sugs %}',
            {"sugs": ["Paris", "London"]},
        )
        assert "Paris" in html
        assert "London" in html

    def test_no_suggestions_hidden(self):
        html = render('{% autocomplete name="city" source_event="s" %}')
        assert "dj-autocomplete__dropdown--hidden" in html
        assert 'aria-expanded="false"' in html

    def test_suggestions_expanded(self):
        html = render(
            '{% autocomplete name="city" source_event="s" suggestions=sugs %}',
            {"sugs": [{"value": "a", "label": "A"}]},
        )
        assert 'aria-expanded="true"' in html
        assert "dj-autocomplete__dropdown--hidden" not in html

    def test_loading(self):
        html = render('{% autocomplete name="city" source_event="s" loading=True %}')
        assert "dj-autocomplete--loading" in html
        assert "dj-autocomplete__spinner" in html

    def test_no_spinner_by_default(self):
        html = render('{% autocomplete name="city" source_event="s" %}')
        assert "dj-autocomplete__spinner" not in html

    def test_disabled(self):
        html = render('{% autocomplete name="city" source_event="s" disabled=True %}')
        assert " disabled" in html

    def test_required(self):
        html = render('{% autocomplete name="city" source_event="s" required=True %}')
        assert " required" in html

    def test_error(self):
        html = render('{% autocomplete name="city" source_event="s" error="Required" %}')
        assert "dj-autocomplete--error" in html
        assert "form-error-message" in html
        assert "Required" in html

    def test_custom_class(self):
        html = render('{% autocomplete name="city" source_event="s" custom_class="wide" %}')
        assert "wide" in html

    def test_listbox_role(self):
        html = render('{% autocomplete name="city" source_event="s" %}')
        assert 'role="listbox"' in html
        assert 'aria-autocomplete="list"' in html


class TestAutocompleteRustHandler:
    handler = AutocompleteHandler()

    def test_basic(self):
        html = self.handler.render(
            ["name='city'", "source_event='search_cities'"], {}
        )
        assert isinstance(html, SafeData)
        assert 'name="city"' in html
        assert 'role="combobox"' in html

    def test_suggestions(self):
        html = self.handler.render(
            ["name='city'", "source_event='s'"],
            {"suggestions": [{"value": "x", "label": "X City"}]},
        )
        # The handler reads from context fallback
        assert "X City" in html

    def test_loading(self):
        html = self.handler.render(
            ["name='city'", "source_event='s'", "loading=true"], {}
        )
        assert "dj-autocomplete--loading" in html


# ═══════════════════════════════════════════════════════════════════════════
# XSS Escaping Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestFormEssentialsXSS:
    """Verify that all user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_raw_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html

    # --- Slider ---
    def test_slider_name_xss(self):
        html = render('{% slider name=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_slider_label_xss(self):
        html = render('{% slider name="p" label=xss %}', {"xss": self.XSS})
        self._assert_no_raw_script(html)

    def test_slider_event_xss(self):
        html = render('{% slider name="p" event=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_slider_custom_class_xss(self):
        html = render('{% slider name="p" custom_class=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    # --- Search Input ---
    def test_search_name_xss(self):
        html = render('{% search_input name=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_search_label_xss(self):
        html = render('{% search_input name="q" label=xss %}', {"xss": self.XSS})
        self._assert_no_raw_script(html)

    def test_search_placeholder_xss(self):
        html = render(
            '{% search_input name="q" placeholder=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_search_value_xss(self):
        html = render('{% search_input name="q" value=xss %}', {"xss": self.XSS})
        self._assert_no_raw_script(html)

    def test_search_event_xss(self):
        html = render('{% search_input name="q" event=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_search_custom_class_xss(self):
        html = render(
            '{% search_input name="q" custom_class=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Password Input ---
    def test_password_name_xss(self):
        html = render('{% password_input name=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_password_label_xss(self):
        html = render(
            '{% password_input name="pwd" label=xss %}', {"xss": self.XSS}
        )
        self._assert_no_raw_script(html)

    def test_password_error_xss(self):
        html = render(
            '{% password_input name="pwd" error=xss %}', {"xss": self.XSS}
        )
        self._assert_no_raw_script(html)

    def test_password_placeholder_xss(self):
        html = render(
            '{% password_input name="pwd" placeholder=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_password_event_xss(self):
        html = render(
            '{% password_input name="pwd" event=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_password_custom_class_xss(self):
        html = render(
            '{% password_input name="pwd" custom_class=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Autocomplete ---
    def test_autocomplete_name_xss(self):
        html = render(
            '{% autocomplete name=xss source_event="s" %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_autocomplete_label_xss(self):
        html = render(
            '{% autocomplete name="c" label=xss source_event="s" %}',
            {"xss": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_autocomplete_error_xss(self):
        html = render(
            '{% autocomplete name="c" error=xss source_event="s" %}',
            {"xss": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_autocomplete_placeholder_xss(self):
        html = render(
            '{% autocomplete name="c" placeholder=xss source_event="s" %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_autocomplete_source_event_xss(self):
        html = render(
            '{% autocomplete name="c" source_event=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_autocomplete_suggestion_label_xss(self):
        html = render(
            '{% autocomplete name="c" source_event="s" suggestions=sugs %}',
            {"sugs": [{"value": "a", "label": self.XSS}]},
        )
        self._assert_no_raw_script(html)

    def test_autocomplete_suggestion_value_xss(self):
        html = render(
            '{% autocomplete name="c" source_event="s" suggestions=sugs %}',
            {"sugs": [{"value": self.XSS_ATTR, "label": "X"}]},
        )
        self._assert_attr_escaped(html)

    def test_autocomplete_display_value_xss(self):
        html = render(
            '{% autocomplete name="c" display_value=xss source_event="s" %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_autocomplete_custom_class_xss(self):
        html = render(
            '{% autocomplete name="c" source_event="s" custom_class=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Rust handler XSS ---
    def test_slider_rust_name_xss(self):
        handler = SliderHandler()
        html = handler.render([f"name='{self.XSS_ATTR}'"], {})
        self._assert_attr_escaped(html)

    def test_search_rust_name_xss(self):
        handler = SearchInputHandler()
        html = handler.render([f"name='{self.XSS_ATTR}'"], {})
        self._assert_attr_escaped(html)

    def test_password_rust_name_xss(self):
        handler = PasswordInputHandler()
        html = handler.render([f"name='{self.XSS_ATTR}'"], {})
        self._assert_attr_escaped(html)

    def test_autocomplete_rust_name_xss(self):
        handler = AutocompleteHandler()
        html = handler.render([f"name='{self.XSS_ATTR}'", "source_event='s'"], {})
        self._assert_attr_escaped(html)

    def test_autocomplete_rust_suggestion_xss(self):
        handler = AutocompleteHandler()
        html = handler.render(
            ["name='c'", "source_event='s'"],
            {"suggestions": [{"value": self.XSS_ATTR, "label": self.XSS}]},
        )
        self._assert_attr_escaped(html)
        self._assert_no_raw_script(html)


# ═══════════════════════════════════════════════════════════════════════════
# Handler Registration
# ═══════════════════════════════════════════════════════════════════════════


class TestRegistration:
    def test_slider_in_inline_handlers(self):
        from djust_components.rust_handlers import INLINE_HANDLERS
        names = [name for name, _ in INLINE_HANDLERS]
        assert "slider" in names

    def test_search_input_in_inline_handlers(self):
        from djust_components.rust_handlers import INLINE_HANDLERS
        names = [name for name, _ in INLINE_HANDLERS]
        assert "search_input" in names

    def test_password_input_in_inline_handlers(self):
        from djust_components.rust_handlers import INLINE_HANDLERS
        names = [name for name, _ in INLINE_HANDLERS]
        assert "password_input" in names

    def test_autocomplete_in_inline_handlers(self):
        from djust_components.rust_handlers import INLINE_HANDLERS
        names = [name for name, _ in INLINE_HANDLERS]
        assert "autocomplete" in names
