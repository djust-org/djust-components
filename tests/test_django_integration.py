"""Tests for Django Integration Components: dj_form (#73) and model_table (#74).

Covers rendering, field type mapping, error display, XSS escaping,
column inference, queryset conversion, sorting, filtering, pagination,
search, selection, and edge cases.

Uses mock objects that mimic Django's form/field API since we can't
set up real Django models in the test environment without a full stack.
"""
from django.template import Template, Context
import pytest


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ==========================================================================
# Mock objects mimicking Django form/field/model APIs
# ==========================================================================

class MockWidget:
    """Minimal mock of a Django form widget."""
    def __init__(self, widget_type="TextInput", attrs=None):
        self.__class__ = type(widget_type, (), {})
        self.__class__.__name__ = widget_type
        self.attrs = attrs or {}


class MockField:
    """Minimal mock of a Django form field (not bound)."""
    def __init__(self, field_type="CharField", required=True, disabled=False,
                 widget_type="TextInput", choices=None, help_text="",
                 widget_attrs=None):
        self.__class__ = type(field_type, (), {})
        self.__class__.__name__ = field_type
        self.required = required
        self.disabled = disabled
        self.widget = MockWidget(widget_type, attrs=widget_attrs or {})
        self.help_text = help_text
        if choices is not None:
            self.choices = choices


class MockBoundField:
    """Minimal mock of a Django BoundField."""
    def __init__(self, name, field, label=None, value_val="", errors=None,
                 help_text=""):
        self.name = name
        self.html_name = name
        self.field = field
        self.label = label or name.replace("_", " ").title()
        self._value = value_val
        self.errors = errors or []
        self.help_text = help_text or field.help_text

    def value(self):
        return self._value


class MockForm:
    """Minimal mock of a Django Form."""
    def __init__(self, fields=None, non_field_errors_list=None, hidden=None):
        self._visible = fields or []
        self._hidden = hidden or []
        self._non_field = non_field_errors_list or []

    def visible_fields(self):
        return self._visible

    def hidden_fields(self):
        return self._hidden

    def non_field_errors(self):
        return self._non_field


# --- Model mocks for model_table ---

class MockModelField:
    """Minimal mock of a Django model field."""
    def __init__(self, name, field_type="CharField", verbose_name=None,
                 choices=None, column=True):
        self.name = name
        self.__class__ = type(field_type, (), {})
        self.__class__.__name__ = field_type
        self.verbose_name = verbose_name or name.replace("_", " ")
        if choices is not None:
            self.choices = choices
        # 'column' attribute distinguishes concrete fields from reverse relations
        if column:
            self.column = name


class MockMeta:
    """Minimal mock of a Django model's _meta."""
    def __init__(self, fields):
        self._fields = fields

    def get_fields(self):
        return self._fields


class MockModel:
    """Minimal mock of a Django model class."""
    def __init__(self, meta):
        self._meta = meta


class MockModelInstance:
    """Minimal mock of a Django model instance (row)."""
    def __init__(self, **kwargs):
        self.pk = kwargs.get("id", kwargs.get("pk", None))
        for k, v in kwargs.items():
            setattr(self, k, v)


class MockQuerySet:
    """Minimal mock of a Django QuerySet."""
    def __init__(self, model, objects=None):
        self.model = model
        self._objects = objects or []

    def __iter__(self):
        return iter(self._objects)

    def __len__(self):
        return len(self._objects)


# ==========================================================================
# 1. dj_form — Django Form Renderer (#73)
# ==========================================================================

class TestDjFormBasic:
    def test_renders_form_tag(self):
        form = MockForm()
        html = render('{% dj_form form=f %}', {"f": form})
        assert "<form" in html
        assert "</form>" in html
        assert 'class="dj-form"' in html

    def test_no_form_returns_empty(self):
        html = render('{% dj_form %}')
        assert html.strip() == ""

    def test_method_default_post(self):
        form = MockForm()
        html = render('{% dj_form form=f %}', {"f": form})
        assert 'method="post"' in html

    def test_custom_method(self):
        form = MockForm()
        html = render('{% dj_form form=f method="get" %}', {"f": form})
        assert 'method="get"' in html

    def test_action_attribute(self):
        form = MockForm()
        html = render('{% dj_form form=f action="/submit/" %}', {"f": form})
        assert 'action="/submit/"' in html

    def test_no_action_by_default(self):
        form = MockForm()
        html = render('{% dj_form form=f %}', {"f": form})
        assert "action=" not in html

    def test_custom_class(self):
        form = MockForm()
        html = render('{% dj_form form=f custom_class="my-form" %}', {"f": form})
        assert "my-form" in html
        assert "dj-form" in html

    def test_submit_button(self):
        form = MockForm()
        html = render('{% dj_form form=f %}', {"f": form})
        assert 'type="submit"' in html
        assert "Submit" in html

    def test_custom_submit_label(self):
        form = MockForm()
        html = render('{% dj_form form=f submit_label="Save" %}', {"f": form})
        assert "Save" in html

    def test_submit_event(self):
        form = MockForm()
        html = render('{% dj_form form=f submit_event="save_form" %}', {"f": form})
        assert 'dj-click="save_form"' in html
        assert 'type="button"' in html


class TestDjFormCharField:
    def test_renders_text_input(self):
        field = MockField("CharField")
        bf = MockBoundField("username", field, label="Username", value_val="john")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert 'type="text"' in html
        assert 'name="username"' in html
        assert 'value="john"' in html
        assert "Username" in html

    def test_required_marker(self):
        field = MockField("CharField", required=True)
        bf = MockBoundField("name", field, label="Name")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert "form-required" in html
        assert " *" in html
        assert " required" in html

    def test_not_required(self):
        field = MockField("CharField", required=False)
        bf = MockBoundField("name", field, label="Name")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert "form-required" not in html

    def test_disabled(self):
        field = MockField("CharField", disabled=True)
        bf = MockBoundField("name", field, label="Name")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert " disabled" in html


class TestDjFormEmailField:
    def test_renders_email_input(self):
        field = MockField("EmailField")
        bf = MockBoundField("email", field, label="Email")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert 'type="email"' in html


class TestDjFormChoiceField:
    def test_renders_select(self):
        field = MockField("ChoiceField", widget_type="Select",
                          choices=[("", "---"), ("a", "Alpha"), ("b", "Beta")])
        bf = MockBoundField("color", field, label="Color", value_val="a")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert "<select" in html
        assert 'name="color"' in html
        assert "Alpha" in html
        assert "Beta" in html
        assert 'value="a" selected' in html

    def test_model_choice_field(self):
        field = MockField("ModelChoiceField", widget_type="Select",
                          choices=[("", "---------"), ("1", "Item 1")])
        bf = MockBoundField("item", field, label="Item")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert "<select" in html


class TestDjFormBooleanField:
    def test_renders_checkbox(self):
        field = MockField("BooleanField", widget_type="CheckboxInput")
        bf = MockBoundField("agree", field, label="I agree", value_val="True")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert 'type="checkbox"' in html
        assert "I agree" in html
        assert " checked" in html

    def test_unchecked(self):
        field = MockField("BooleanField", widget_type="CheckboxInput")
        bf = MockBoundField("agree", field, label="I agree", value_val="")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert " checked" not in html


class TestDjFormTextarea:
    def test_renders_textarea(self):
        field = MockField("CharField", widget_type="Textarea")
        bf = MockBoundField("bio", field, label="Bio", value_val="Hello world")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert "<textarea" in html
        assert "Hello world" in html
        assert 'name="bio"' in html


class TestDjFormPasswordField:
    def test_renders_password(self):
        field = MockField("CharField", widget_type="PasswordInput")
        bf = MockBoundField("password", field, label="Password")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert 'type="password"' in html


class TestDjFormFileField:
    def test_renders_file_input(self):
        field = MockField("FileField", widget_type="ClearableFileInput")
        bf = MockBoundField("document", field, label="Document")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert 'type="file"' in html


class TestDjFormRadioGroup:
    def test_renders_radio_buttons(self):
        field = MockField("ChoiceField", widget_type="RadioSelect",
                          choices=[("s", "Small"), ("m", "Medium"), ("l", "Large")])
        bf = MockBoundField("size", field, label="Size", value_val="m")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert 'type="radio"' in html
        assert "Small" in html
        assert "Medium" in html
        assert "Large" in html
        assert html.count('type="radio"') == 3


class TestDjFormNumberField:
    def test_renders_number_input(self):
        field = MockField("IntegerField")
        bf = MockBoundField("age", field, label="Age", value_val="25")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert 'type="number"' in html
        assert 'value="25"' in html


class TestDjFormDateField:
    def test_renders_date_input(self):
        field = MockField("DateField")
        bf = MockBoundField("birthday", field, label="Birthday")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert 'type="date"' in html


class TestDjFormHiddenField:
    def test_renders_hidden_input(self):
        field = MockField("CharField", widget_type="HiddenInput")
        bf = MockBoundField("csrf", field, value_val="token123")
        form = MockForm(hidden=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert 'type="hidden"' in html
        assert 'value="token123"' in html


class TestDjFormErrors:
    def test_non_field_errors(self):
        form = MockForm(non_field_errors_list=["Invalid credentials", "Try again"])
        html = render('{% dj_form form=f %}', {"f": form})
        assert "dj-form-errors" in html
        assert "Invalid credentials" in html
        assert "Try again" in html

    def test_no_non_field_errors(self):
        form = MockForm(non_field_errors_list=[])
        html = render('{% dj_form form=f %}', {"f": form})
        assert "dj-form-errors" not in html

    def test_field_errors(self):
        field = MockField("CharField")
        bf = MockBoundField("email", field, label="Email",
                            errors=["This field is required"])
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert "form-error-message" in html
        assert "This field is required" in html
        assert "form-input-error" in html

    def test_multiple_field_errors(self):
        field = MockField("CharField")
        bf = MockBoundField("email", field, label="Email",
                            errors=["Required", "Invalid format"])
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert "Required" in html
        assert "Invalid format" in html

    def test_show_errors_false(self):
        form = MockForm(non_field_errors_list=["Bad input"])
        html = render('{% dj_form form=f show_errors=False %}', {"f": form})
        assert "dj-form-errors" not in html


class TestDjFormHelpText:
    def test_help_text_rendered(self):
        field = MockField("CharField", help_text="Enter your full name")
        bf = MockBoundField("name", field, label="Name",
                            help_text="Enter your full name")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        assert "form-helper" in html
        assert "Enter your full name" in html


class TestDjFormEventPrefix:
    def test_event_prefix(self):
        field = MockField("CharField")
        bf = MockBoundField("username", field, label="Username")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f event_prefix="reg_" %}', {"f": form})
        assert 'dj-input="reg_username"' in html


class TestDjFormMultipleFields:
    def test_multiple_fields(self):
        f1 = MockBoundField("name", MockField("CharField"), label="Name")
        f2 = MockBoundField("email", MockField("EmailField"), label="Email")
        f3 = MockBoundField("agree", MockField("BooleanField", widget_type="CheckboxInput"),
                            label="Agree", value_val="")
        form = MockForm(fields=[f1, f2, f3])
        html = render('{% dj_form form=f %}', {"f": form})
        assert 'name="name"' in html
        assert 'name="email"' in html
        assert 'name="agree"' in html
        assert 'type="text"' in html
        assert 'type="email"' in html
        assert 'type="checkbox"' in html


class TestDjFormXSS:
    XSS = '<script>alert("x")</script>'
    XSS_ATTR = '" onmouseover="alert(1)'

    def _assert_no_raw_script(self, html):
        assert "<script>" not in html

    def _assert_attr_escaped(self, html):
        # The raw " must be escaped to &quot; so the attribute boundary is not broken
        assert '" onmouseover="' not in html

    def test_field_label_xss(self):
        field = MockField("CharField")
        bf = MockBoundField("name", field, label=self.XSS)
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        self._assert_no_raw_script(html)

    def test_field_value_xss(self):
        field = MockField("CharField")
        bf = MockBoundField("name", field, label="Name", value_val=self.XSS_ATTR)
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        self._assert_attr_escaped(html)

    def test_field_error_xss(self):
        field = MockField("CharField")
        bf = MockBoundField("name", field, label="Name", errors=[self.XSS])
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        self._assert_no_raw_script(html)

    def test_non_field_error_xss(self):
        form = MockForm(non_field_errors_list=[self.XSS])
        html = render('{% dj_form form=f %}', {"f": form})
        self._assert_no_raw_script(html)

    def test_custom_class_xss(self):
        form = MockForm()
        html = render('{% dj_form form=f custom_class=xss %}',
                       {"f": form, "xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_action_xss(self):
        form = MockForm()
        html = render('{% dj_form form=f action=xss %}',
                       {"f": form, "xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_submit_event_xss(self):
        form = MockForm()
        html = render('{% dj_form form=f submit_event=xss %}',
                       {"f": form, "xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_help_text_xss(self):
        field = MockField("CharField", help_text=self.XSS)
        bf = MockBoundField("name", field, label="Name", help_text=self.XSS)
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        self._assert_no_raw_script(html)

    def test_choice_value_xss(self):
        field = MockField("ChoiceField", widget_type="Select",
                          choices=[(self.XSS_ATTR, "Bad")])
        bf = MockBoundField("pick", field, label="Pick")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        self._assert_attr_escaped(html)

    def test_choice_label_xss(self):
        field = MockField("ChoiceField", widget_type="Select",
                          choices=[("a", self.XSS)])
        bf = MockBoundField("pick", field, label="Pick")
        form = MockForm(fields=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        self._assert_no_raw_script(html)

    def test_hidden_field_value_xss(self):
        field = MockField("CharField", widget_type="HiddenInput")
        bf = MockBoundField("tok", field, value_val=self.XSS_ATTR)
        form = MockForm(hidden=[bf])
        html = render('{% dj_form form=f %}', {"f": form})
        self._assert_attr_escaped(html)


# ==========================================================================
# 2. model_table — Django ModelForm Table (#74)
# ==========================================================================

def _make_model_and_qs(fields=None, rows=None):
    """Helper to create a MockModel + MockQuerySet."""
    if fields is None:
        fields = [
            MockModelField("id", "AutoField", verbose_name="ID"),
            MockModelField("name", "CharField", verbose_name="name"),
            MockModelField("email", "EmailField", verbose_name="email"),
            MockModelField("active", "BooleanField", verbose_name="active"),
        ]
    meta = MockMeta(fields)
    model = MockModel(meta)
    objects = []
    if rows:
        for r in rows:
            objects.append(MockModelInstance(**r))
    return MockQuerySet(model, objects)


class TestModelTableBasic:
    def test_renders_table(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        assert "<table" in html
        assert "</table>" in html
        assert "dj-model-table" in html

    def test_no_queryset_returns_empty(self):
        html = render('{% model_table %}')
        assert html.strip() == ""

    def test_infers_columns(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        assert "Name" in html
        assert "Email" in html
        assert "Active" in html

    def test_renders_rows(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
            {"id": 2, "name": "Bob", "email": "b@b.com", "active": False},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        assert "Alice" in html
        assert "Bob" in html
        assert "a@b.com" in html
        assert "b@b.com" in html

    def test_empty_queryset(self):
        qs = _make_model_and_qs(rows=[])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        assert "No data" in html
        assert "data-table__empty" in html

    def test_custom_empty_title(self):
        qs = _make_model_and_qs(rows=[])
        html = render('{% model_table queryset=qs empty_title="Nothing here" %}',
                       {"qs": qs})
        assert "Nothing here" in html


class TestModelTableExcludeInclude:
    def test_exclude_columns(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs exclude=exc %}',
                       {"qs": qs, "exc": ["email", "active"]})
        assert "Email" not in html
        assert "Active" not in html
        assert "Name" in html

    def test_include_columns(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs include=inc %}',
                       {"qs": qs, "inc": ["name"]})
        assert "Name" in html
        assert "Email" not in html


class TestModelTableSorting:
    def test_sortable_columns(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        assert "data-table__th--sortable" in html
        assert "table_sort" in html

    def test_sort_indicator(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs sort_by="name" %}', {"qs": qs})
        assert "data-table__th--sorted" in html
        # Ascending arrow
        assert "&#9650;" in html

    def test_sort_desc_indicator(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs sort_by="name" sort_desc=True %}',
                       {"qs": qs})
        assert "&#9660;" in html


class TestModelTableSearch:
    def test_search_box(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs search=True %}', {"qs": qs})
        assert "data-table__search" in html
        assert "table_search" in html

    def test_no_search_by_default(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        assert "data-table__search" not in html


class TestModelTablePagination:
    def test_pagination(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render(
            '{% model_table queryset=qs paginate=True page=2 total_pages=5 %}',
            {"qs": qs})
        assert "data-table__pagination" in html
        assert "Page 2 of 5" in html
        assert "table_prev" in html
        assert "table_next" in html

    def test_no_pagination_by_default(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        assert "data-table__pagination" not in html

    def test_prev_disabled_on_first_page(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render(
            '{% model_table queryset=qs paginate=True page=1 total_pages=3 %}',
            {"qs": qs})
        # The prev button should be disabled
        assert 'dj-click="table_prev" disabled' in html

    def test_next_disabled_on_last_page(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render(
            '{% model_table queryset=qs paginate=True page=3 total_pages=3 %}',
            {"qs": qs})
        assert 'dj-click="table_next" disabled' in html


class TestModelTableSelection:
    def test_selectable(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs selectable=True %}', {"qs": qs})
        assert "data-table__th--select" in html
        assert "table_select" in html

    def test_selected_rows(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
            {"id": 2, "name": "Bob", "email": "b@b.com", "active": False},
        ])
        html = render(
            '{% model_table queryset=qs selectable=True selected_rows=sel %}',
            {"qs": qs, "sel": [1]})
        assert "data-table__tr--selected" in html


class TestModelTableFilters:
    def test_filterable_columns(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        # CharField and EmailField should be filterable
        assert "data-table__filter-row" in html
        assert "data-table__filter-input" in html

    def test_boolean_filter_as_select(self):
        fields = [
            MockModelField("id", "AutoField", verbose_name="ID"),
            MockModelField("active", "BooleanField", verbose_name="active"),
        ]
        qs = _make_model_and_qs(fields=fields, rows=[
            {"id": 1, "active": True},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        assert "data-table__filter-select" in html
        assert "Yes" in html
        assert "No" in html


class TestModelTableLoading:
    def test_loading_state(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs loading=True %}', {"qs": qs})
        assert "data-table__loading" in html
        assert "dj-spinner" in html


class TestModelTableStyling:
    def test_striped_by_default(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        assert "data-table--striped" in html

    def test_compact(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs compact=True %}', {"qs": qs})
        assert "data-table--compact" in html

    def test_custom_class(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs custom_class="products" %}',
                       {"qs": qs})
        assert "products" in html


class TestModelTableFieldTypes:
    def test_choices_field_filter(self):
        fields = [
            MockModelField("id", "AutoField", verbose_name="ID"),
            MockModelField("status", "CharField", verbose_name="status",
                           choices=[("active", "Active"), ("inactive", "Inactive")]),
        ]
        qs = _make_model_and_qs(fields=fields, rows=[
            {"id": 1, "status": "active"},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        assert "Active" in html
        assert "Inactive" in html

    def test_foreign_key_display(self):
        """FK values should be converted to str() for display."""
        class FKValue:
            def __init__(self, pk, name):
                self.pk = pk
                self._name = name
            def __str__(self):
                return self._name

        fields = [
            MockModelField("id", "AutoField", verbose_name="ID"),
            MockModelField("category", "ForeignKey", verbose_name="category"),
        ]
        obj = MockModelInstance(id=1, category=FKValue(5, "Electronics"))
        qs = MockQuerySet(MockModel(MockMeta(fields)), [obj])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        assert "Electronics" in html

    def test_skips_reverse_relations(self):
        """Fields that are reverse relations (no 'column' attr) should be skipped."""
        class ReverseRelation:
            name = "order_set"
            related_model = True  # has related_model but no column
            verbose_name = "orders"
        fields = [
            MockModelField("id", "AutoField", verbose_name="ID"),
            MockModelField("name", "CharField", verbose_name="name"),
            ReverseRelation(),
        ]
        qs = _make_model_and_qs(fields=fields, rows=[
            {"id": 1, "name": "Alice"},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        assert "Order Set" not in html
        assert "Name" in html


class TestModelTableXSS:
    XSS = '<script>alert("x")</script>'
    XSS_ATTR = '" onmouseover="alert(1)'

    def _assert_no_raw_script(self, html):
        assert "<script>" not in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html

    def test_row_data_xss(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": self.XSS, "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        self._assert_no_raw_script(html)

    def test_row_data_attr_xss(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": self.XSS_ATTR, "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs %}', {"qs": qs})
        self._assert_attr_escaped(html)

    def test_custom_class_xss(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs custom_class=xss %}',
                       {"qs": qs, "xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_empty_title_xss(self):
        qs = _make_model_and_qs(rows=[])
        html = render('{% model_table queryset=qs empty_title=xss %}',
                       {"qs": qs, "xss": self.XSS})
        self._assert_no_raw_script(html)

    def test_search_query_xss(self):
        qs = _make_model_and_qs(rows=[
            {"id": 1, "name": "Alice", "email": "a@b.com", "active": True},
        ])
        html = render('{% model_table queryset=qs search=True search_query=xss %}',
                       {"qs": qs, "xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)


# ==========================================================================
# 3. Helper function unit tests
# ==========================================================================

class TestFieldTypeMapping:
    """Test _get_field_type helper for various Django field/widget combos."""

    def test_charfield_text(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("CharField")
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "text"

    def test_email_field(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("EmailField")
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "email"

    def test_textarea_widget_override(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("CharField", widget_type="Textarea")
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "textarea"

    def test_checkbox_widget(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("BooleanField", widget_type="CheckboxInput")
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "checkbox"

    def test_radio_widget(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("ChoiceField", widget_type="RadioSelect",
                          choices=[("a", "A")])
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "radio_group"

    def test_password_widget(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("CharField", widget_type="PasswordInput")
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "password"

    def test_hidden_widget(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("CharField", widget_type="HiddenInput")
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "hidden"

    def test_integer_field(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("IntegerField")
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "number"

    def test_date_field(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("DateField")
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "date"

    def test_url_field(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("URLField")
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "url"

    def test_file_field_via_widget(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("FileField", widget_type="ClearableFileInput")
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "file"

    def test_select_multiple_widget(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("MultipleChoiceField", widget_type="SelectMultiple",
                          choices=[("a", "A")])
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "select_multiple"

    def test_checkbox_select_multiple(self):
        from djust_components.templatetags.djust_components import _get_field_type
        field = MockField("MultipleChoiceField", widget_type="CheckboxSelectMultiple",
                          choices=[("a", "A")])
        bf = MockBoundField("x", field)
        assert _get_field_type(bf) == "checkbox_group"


class TestColumnInference:
    def test_basic_inference(self):
        from djust_components.templatetags.djust_components import _infer_columns
        meta = MockMeta([
            MockModelField("id", "AutoField"),
            MockModelField("name", "CharField"),
            MockModelField("price", "DecimalField"),
        ])
        cols = _infer_columns(meta)
        keys = [c["key"] for c in cols]
        assert "id" in keys
        assert "name" in keys
        assert "price" in keys

    def test_exclude(self):
        from djust_components.templatetags.djust_components import _infer_columns
        meta = MockMeta([
            MockModelField("id", "AutoField"),
            MockModelField("name", "CharField"),
        ])
        cols = _infer_columns(meta, exclude=["id"])
        keys = [c["key"] for c in cols]
        assert "id" not in keys
        assert "name" in keys

    def test_include(self):
        from djust_components.templatetags.djust_components import _infer_columns
        meta = MockMeta([
            MockModelField("id", "AutoField"),
            MockModelField("name", "CharField"),
            MockModelField("email", "EmailField"),
        ])
        cols = _infer_columns(meta, include=["name"])
        keys = [c["key"] for c in cols]
        assert keys == ["name"]

    def test_sortable_fields(self):
        from djust_components.templatetags.djust_components import _infer_columns
        meta = MockMeta([
            MockModelField("name", "CharField"),
            MockModelField("photo", "ImageField"),
        ])
        cols = _infer_columns(meta)
        name_col = [c for c in cols if c["key"] == "name"][0]
        photo_col = [c for c in cols if c["key"] == "photo"][0]
        assert name_col["sortable"] is True
        assert photo_col["sortable"] is False

    def test_filterable_fields(self):
        from djust_components.templatetags.djust_components import _infer_columns
        meta = MockMeta([
            MockModelField("name", "CharField"),
            MockModelField("photo", "ImageField"),
        ])
        cols = _infer_columns(meta)
        name_col = [c for c in cols if c["key"] == "name"][0]
        photo_col = [c for c in cols if c["key"] == "photo"][0]
        assert name_col.get("filterable") is True
        assert photo_col.get("filterable") is None


class TestQuerysetToRows:
    def test_basic_conversion(self):
        from djust_components.templatetags.djust_components import _queryset_to_rows
        columns = [{"key": "id"}, {"key": "name"}]
        obj = MockModelInstance(id=1, name="Alice")
        rows = _queryset_to_rows([obj], columns)
        assert len(rows) == 1
        assert rows[0]["id"] == 1
        assert rows[0]["name"] == "Alice"

    def test_missing_attr_defaults_empty(self):
        from djust_components.templatetags.djust_components import _queryset_to_rows
        columns = [{"key": "id"}, {"key": "missing"}]
        obj = MockModelInstance(id=1)
        rows = _queryset_to_rows([obj], columns)
        assert rows[0]["missing"] == ""

    def test_none_value(self):
        from djust_components.templatetags.djust_components import _queryset_to_rows
        columns = [{"key": "id"}, {"key": "name"}]
        obj = MockModelInstance(id=1, name=None)
        rows = _queryset_to_rows([obj], columns)
        assert rows[0]["name"] == ""
