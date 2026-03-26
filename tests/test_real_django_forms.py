"""Tests using real Django Form/ModelForm instances (not mocks).

These tests verify that dj_form and model_table work correctly with
actual Django field classes, widgets, and validation machinery.
No database is needed -- Django's SimpleTestCase and in-memory objects
are sufficient for form rendering and queryset-like iteration.
"""
from django import forms
from django.template import Template, Context

import pytest


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ==========================================================================
# Real Django Forms
# ==========================================================================

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, help_text="Your full name")
    email = forms.EmailField()
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={"placeholder": "Enter subject"}))
    message = forms.CharField(widget=forms.Textarea)
    priority = forms.ChoiceField(choices=[("low", "Low"), ("med", "Medium"), ("high", "High")])
    subscribe = forms.BooleanField(required=False, label="Subscribe to newsletter")


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    remember = forms.BooleanField(required=False)


class FileUploadForm(forms.Form):
    document = forms.FileField()
    description = forms.CharField(required=False)


class AdvancedForm(forms.Form):
    age = forms.IntegerField(min_value=0, max_value=150)
    price = forms.DecimalField(max_digits=10, decimal_places=2)
    website = forms.URLField(required=False)
    birthday = forms.DateField()
    meeting_time = forms.TimeField(required=False)
    appointment = forms.DateTimeField(required=False)
    slug = forms.SlugField()
    tags = forms.MultipleChoiceField(
        choices=[("py", "Python"), ("js", "JavaScript"), ("rs", "Rust")],
        widget=forms.CheckboxSelectMultiple,
    )
    color = forms.ChoiceField(
        choices=[("r", "Red"), ("g", "Green"), ("b", "Blue")],
        widget=forms.RadioSelect,
    )
    hidden_token = forms.CharField(widget=forms.HiddenInput, initial="abc123")


# ==========================================================================
# 1. dj_form with Real Django Forms
# ==========================================================================

class TestDjFormRealForms:
    """Test dj_form with actual Django Form instances."""

    def test_basic_contact_form(self):
        form = ContactForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert "<form" in html
        assert 'class="dj-form"' in html
        assert 'method="post"' in html
        assert 'type="submit"' in html

    def test_text_field_rendered(self):
        form = ContactForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'name="name"' in html
        assert 'type="text"' in html
        assert "Your full name" in html  # help_text

    def test_email_field_type(self):
        form = ContactForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'name="email"' in html
        assert 'type="email"' in html

    def test_textarea_widget(self):
        form = ContactForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert "<textarea" in html
        assert 'name="message"' in html

    def test_choice_field_select(self):
        form = ContactForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert "<select" in html
        assert 'name="priority"' in html
        assert "Low" in html
        assert "Medium" in html
        assert "High" in html

    def test_boolean_field_checkbox(self):
        form = ContactForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'type="checkbox"' in html
        assert 'name="subscribe"' in html

    def test_placeholder_from_widget_attrs(self):
        form = ContactForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'placeholder="Enter subject"' in html

    def test_password_field(self):
        form = LoginForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'type="password"' in html
        assert 'name="password"' in html

    def test_file_field(self):
        form = FileUploadForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'type="file"' in html
        assert 'name="document"' in html

    def test_number_fields(self):
        form = AdvancedForm()
        html = render("{% dj_form form=f %}", {"f": form})
        # IntegerField and DecimalField -> type="number"
        assert 'name="age"' in html
        assert 'name="price"' in html
        assert 'type="number"' in html

    def test_url_field(self):
        form = AdvancedForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'name="website"' in html
        assert 'type="url"' in html

    def test_date_field(self):
        form = AdvancedForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'name="birthday"' in html
        assert 'type="date"' in html

    def test_time_field(self):
        form = AdvancedForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'name="meeting_time"' in html
        assert 'type="time"' in html

    def test_datetime_field(self):
        form = AdvancedForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'name="appointment"' in html
        assert 'type="datetime-local"' in html

    def test_radio_select_widget(self):
        form = AdvancedForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'type="radio"' in html
        assert "Red" in html
        assert "Green" in html
        assert "Blue" in html

    def test_checkbox_select_multiple_widget(self):
        form = AdvancedForm()
        html = render("{% dj_form form=f %}", {"f": form})
        # CheckboxSelectMultiple should render checkboxes for each choice
        assert "Python" in html
        assert "JavaScript" in html
        assert "Rust" in html

    def test_hidden_field(self):
        form = AdvancedForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'type="hidden"' in html
        assert 'name="hidden_token"' in html
        assert 'value="abc123"' in html

    def test_required_fields_marked(self):
        form = ContactForm()
        html = render("{% dj_form form=f %}", {"f": form})
        # name, email, subject, message, priority are required
        assert "form-required" in html

    def test_disabled_field(self):
        """Test that disabled fields render the disabled attribute."""
        class DisabledForm(forms.Form):
            locked = forms.CharField(disabled=True)

        form = DisabledForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert "disabled" in html

    def test_custom_submit_label(self):
        form = ContactForm()
        html = render('{% dj_form form=f submit_label="Send" %}', {"f": form})
        assert "Send" in html

    def test_custom_method_get(self):
        form = ContactForm()
        html = render('{% dj_form form=f method="get" %}', {"f": form})
        assert 'method="get"' in html

    def test_custom_action(self):
        form = ContactForm()
        html = render('{% dj_form form=f action="/send/" %}', {"f": form})
        assert 'action="/send/"' in html

    def test_event_prefix(self):
        form = LoginForm()
        html = render('{% dj_form form=f event_prefix="login_" %}', {"f": form})
        assert 'dj-input="login_username"' in html

    def test_submit_event(self):
        form = LoginForm()
        html = render('{% dj_form form=f submit_event="do_login" %}', {"f": form})
        assert 'dj-click="do_login"' in html
        assert 'type="button"' in html


class TestDjFormValidation:
    """Test dj_form rendering with bound forms that have errors."""

    def test_field_errors_displayed(self):
        form = ContactForm(data={"name": "", "email": "bad", "subject": "", "message": "", "priority": "low"})
        assert not form.is_valid()
        html = render("{% dj_form form=f %}", {"f": form})
        assert "form-error-message" in html

    def test_non_field_errors_displayed(self):
        class ValidatedForm(forms.Form):
            a = forms.CharField()
            b = forms.CharField()

            def clean(self):
                cleaned = super().clean()
                if cleaned.get("a") == cleaned.get("b"):
                    raise forms.ValidationError("A and B must differ")
                return cleaned

        form = ValidatedForm(data={"a": "same", "b": "same"})
        form.is_valid()
        html = render("{% dj_form form=f %}", {"f": form})
        assert "A and B must differ" in html
        assert "dj-form-errors" in html

    def test_bound_form_preserves_values(self):
        form = ContactForm(data={
            "name": "Alice",
            "email": "alice@example.com",
            "subject": "Test",
            "message": "Hello there",
            "priority": "high",
        })
        form.is_valid()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'value="Alice"' in html
        assert 'value="alice@example.com"' in html

    def test_choice_field_selected_value(self):
        form = ContactForm(data={
            "name": "Bob",
            "email": "bob@test.com",
            "subject": "Hi",
            "message": "Body",
            "priority": "high",
        })
        form.is_valid()
        html = render("{% dj_form form=f %}", {"f": form})
        assert 'value="high" selected' in html

    def test_checkbox_checked_when_true(self):
        form = ContactForm(data={
            "name": "Charlie",
            "email": "c@test.com",
            "subject": "Sub",
            "message": "Msg",
            "priority": "low",
            "subscribe": "on",
        })
        form.is_valid()
        html = render("{% dj_form form=f %}", {"f": form})
        assert "checked" in html


class TestDjFormXSS:
    """XSS prevention with real Django forms."""

    def test_xss_in_help_text(self):
        class XSSForm(forms.Form):
            field = forms.CharField(help_text='<script>alert("xss")</script>')

        form = XSSForm()
        html = render("{% dj_form form=f %}", {"f": form})
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_xss_in_bound_value(self):
        class SimpleForm(forms.Form):
            name = forms.CharField()

        form = SimpleForm(data={"name": '"><script>alert(1)</script>'})
        form.is_valid()
        html = render("{% dj_form form=f %}", {"f": form})
        assert "<script>" not in html

    def test_xss_in_choice_label(self):
        class ChoiceForm(forms.Form):
            pick = forms.ChoiceField(choices=[("a", '<img src=x onerror="alert(1)">')])

        form = ChoiceForm()
        html = render("{% dj_form form=f %}", {"f": form})
        # The raw <img> tag must not appear unescaped
        assert "<img " not in html
        assert "&lt;img" in html


# ==========================================================================
# 2. model_table with Mock QuerySet wrapping real-ish objects
# ==========================================================================

class _MockMeta:
    """Simulates Django model _meta with real-feeling field objects."""

    def __init__(self, fields):
        self._fields = fields

    def get_fields(self):
        return self._fields


class _MockField:
    """Simulates a Django model field with verbose_name and column."""

    def __init__(self, name, verbose_name=None, field_type="CharField"):
        self.name = name
        self.verbose_name = verbose_name or name.replace("_", " ")
        self.column = name
        self.__class__ = type(field_type, (), {})
        self.__class__.__name__ = field_type


class _MockModel:
    """Model class stand-in with _meta."""

    def __init__(self, fields):
        self._meta = _MockMeta(fields)


class _MockInstance:
    """Represents a single row."""

    def __init__(self, **kwargs):
        self.pk = kwargs.get("id", kwargs.get("pk", None))
        for k, v in kwargs.items():
            setattr(self, k, v)


class _MockQuerySet:
    """Iterable with .model attribute -- enough for model_table."""

    def __init__(self, model, objects):
        self.model = model
        self._objects = objects

    def __iter__(self):
        return iter(self._objects)

    def __len__(self):
        return len(self._objects)


def _make_user_qs():
    """Build a fake User queryset for testing."""
    fields = [
        _MockField("id", "ID", "AutoField"),
        _MockField("username", "Username"),
        _MockField("email", "Email", "EmailField"),
        _MockField("is_active", "Is Active", "BooleanField"),
    ]
    model = _MockModel(fields)
    objects = [
        _MockInstance(id=1, username="alice", email="alice@example.com", is_active=True),
        _MockInstance(id=2, username="bob", email="bob@test.com", is_active=False),
        _MockInstance(id=3, username="charlie", email="charlie@test.com", is_active=True),
    ]
    return _MockQuerySet(model, objects)


class TestModelTableReal:
    """Test model_table with realistic queryset mocks."""

    def test_basic_rendering(self):
        qs = _make_user_qs()
        html = render("{% model_table queryset=qs %}", {"qs": qs})
        assert "<table" in html
        assert "alice" in html
        assert "bob" in html
        assert "charlie" in html

    def test_column_headers_from_verbose_name(self):
        qs = _make_user_qs()
        html = render("{% model_table queryset=qs %}", {"qs": qs})
        assert "Username" in html
        assert "Email" in html
        assert "Is Active" in html

    def test_exclude_columns(self):
        qs = _make_user_qs()
        html = render(
            '{% model_table queryset=qs exclude=excluded %}',
            {"qs": qs, "excluded": ["email", "is_active"]},
        )
        assert "Username" in html
        assert "alice@example.com" not in html

    def test_include_columns(self):
        qs = _make_user_qs()
        html = render(
            '{% model_table queryset=qs include=inc %}',
            {"qs": qs, "inc": ["username"]},
        )
        assert "Username" in html
        assert "Email" not in html

    def test_empty_queryset(self):
        fields = [_MockField("id", "ID"), _MockField("name", "Name")]
        model = _MockModel(fields)
        qs = _MockQuerySet(model, [])
        html = render("{% model_table queryset=qs %}", {"qs": qs})
        assert "No data" in html

    def test_custom_empty_message(self):
        fields = [_MockField("id", "ID")]
        model = _MockModel(fields)
        qs = _MockQuerySet(model, [])
        html = render(
            '{% model_table queryset=qs empty_title="Nothing here" %}',
            {"qs": qs},
        )
        assert "Nothing here" in html

    def test_striped_default(self):
        qs = _make_user_qs()
        html = render("{% model_table queryset=qs %}", {"qs": qs})
        assert "data-table--striped" in html

    def test_compact_mode(self):
        qs = _make_user_qs()
        html = render("{% model_table queryset=qs compact=True %}", {"qs": qs})
        assert "data-table--compact" in html

    def test_xss_in_cell_values(self):
        fields = [_MockField("id", "ID"), _MockField("name", "Name")]
        model = _MockModel(fields)
        objects = [_MockInstance(id=1, name='<script>alert("xss")</script>')]
        qs = _MockQuerySet(model, objects)
        html = render("{% model_table queryset=qs %}", {"qs": qs})
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_selectable_rows(self):
        qs = _make_user_qs()
        html = render(
            "{% model_table queryset=qs selectable=True %}",
            {"qs": qs},
        )
        assert 'type="checkbox"' in html

    def test_search_enabled(self):
        qs = _make_user_qs()
        html = render(
            "{% model_table queryset=qs search=True %}",
            {"qs": qs},
        )
        assert "data-table__search" in html

    def test_pagination_controls(self):
        qs = _make_user_qs()
        html = render(
            "{% model_table queryset=qs paginate=True page=1 total_pages=3 %}",
            {"qs": qs},
        )
        assert "pagination" in html.lower() or "page" in html.lower()

    def test_none_queryset_returns_empty(self):
        html = render("{% model_table %}")
        assert html.strip() == ""

    def test_custom_class(self):
        qs = _make_user_qs()
        html = render(
            '{% model_table queryset=qs custom_class="my-table" %}',
            {"qs": qs},
        )
        assert "my-table" in html
