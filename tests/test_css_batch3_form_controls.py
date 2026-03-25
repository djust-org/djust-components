"""Tests for CSS Batch 3 — Form Control components.

Verifies that Combobox, Color Picker, Date Picker, and File Dropzone
render HTML containing the CSS classes defined in components.css.
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
from djust_components.templatetags.djust_components import (
    combobox,
    color_picker,
    date_picker,
    file_dropzone,
)


# ─── Combobox ───


class TestComboboxCSS:
    def test_wrapper_class(self):
        html = str(combobox(name="color", options=[]))
        assert 'class="combobox"' in html

    def test_input_class(self):
        html = str(combobox(name="color", options=[]))
        assert "combobox-input" in html
        assert "form-input" in html

    def test_dropdown_class(self):
        html = str(combobox(name="color", options=[{"value": "r", "label": "Red"}]))
        assert 'class="combobox-dropdown"' in html

    def test_option_class(self):
        html = str(combobox(name="c", options=[{"value": "r", "label": "Red"}]))
        assert 'class="combobox-option"' in html

    def test_option_selected_class(self):
        html = str(combobox(name="c", value="r",
                            options=[{"value": "r", "label": "Red"}]))
        assert "combobox-option-selected" in html

    def test_multi_tags_class(self):
        html = str(combobox(
            name="c", multiple=True, selected=["r"],
            options=[{"value": "r", "label": "Red"}],
        ))
        assert 'class="combobox-tags"' in html
        assert 'class="combobox-tag"' in html
        assert "combobox-tag-label" in html
        assert "combobox-tag-remove" in html

    def test_form_group_wrapper(self):
        html = str(combobox(name="c", label="Pick"))
        assert 'class="form-group"' in html
        assert 'class="form-label"' in html


# ─── Color Picker ───


class TestColorPickerCSS:
    def test_wrapper_class(self):
        html = str(color_picker(name="bg"))
        assert 'class="color-picker"' in html

    def test_preview_class(self):
        html = str(color_picker(name="bg", value="#FF0000"))
        assert 'class="color-preview"' in html
        assert "background:#FF0000" in html

    def test_swatches_container(self):
        html = str(color_picker(name="bg"))
        assert 'class="color-swatches"' in html

    def test_swatch_class(self):
        html = str(color_picker(name="bg"))
        assert 'class="color-swatch' in html

    def test_active_swatch_class(self):
        html = str(color_picker(name="bg", value="#3B82F6"))
        assert "color-swatch-active" in html

    def test_hex_input_class(self):
        html = str(color_picker(name="bg"))
        assert "color-hex-input" in html
        assert "form-input" in html

    def test_label_renders(self):
        html = str(color_picker(name="bg", label="Background"))
        assert 'class="form-label"' in html
        assert "Background" in html

    def test_form_group_wrapper(self):
        html = str(color_picker(name="bg"))
        assert 'class="form-group"' in html


# ─── Date Picker ───


class TestDatePickerCSS:
    def test_wrapper_class(self):
        html = str(date_picker(year=2026, month=3))
        assert 'class="date-picker"' in html

    def test_header_class(self):
        html = str(date_picker(year=2026, month=3))
        assert 'class="dp-header"' in html

    def test_nav_buttons(self):
        html = str(date_picker(year=2026, month=3))
        assert 'class="dp-nav-btn"' in html

    def test_month_label(self):
        html = str(date_picker(year=2026, month=3))
        assert 'class="dp-month-label"' in html
        assert "March 2026" in html

    def test_grid_class(self):
        html = str(date_picker(year=2026, month=3))
        assert 'class="dp-grid"' in html

    def test_weekday_headers(self):
        html = str(date_picker(year=2026, month=3))
        assert 'class="dp-weekday"' in html

    def test_day_class(self):
        html = str(date_picker(year=2026, month=3))
        assert 'class="dp-day"' in html or 'class="dp-day ' in html

    def test_day_empty_class(self):
        # Month starting not on Monday will have empty cells
        html = str(date_picker(year=2026, month=3))
        assert "dp-day-empty" in html

    def test_today_class(self):
        import datetime
        today = datetime.date.today()
        html = str(date_picker(year=today.year, month=today.month))
        assert "dp-day-today" in html

    def test_selected_class(self):
        html = str(date_picker(year=2026, month=3, selected="2026-03-15"))
        assert "dp-day-selected" in html

    def test_selected_value_display(self):
        html = str(date_picker(year=2026, month=3, selected="2026-03-15"))
        assert 'class="dp-selected-value"' in html
        assert "2026-03-15" in html

    def test_range_start_class(self):
        html = str(date_picker(
            year=2026, month=3, range=True,
            range_start="2026-03-10", range_end="2026-03-20",
        ))
        assert "dp-day-range-start" in html

    def test_range_end_class(self):
        html = str(date_picker(
            year=2026, month=3, range=True,
            range_start="2026-03-10", range_end="2026-03-20",
        ))
        assert "dp-day-range-end" in html

    def test_in_range_class(self):
        html = str(date_picker(
            year=2026, month=3, range=True,
            range_start="2026-03-10", range_end="2026-03-20",
        ))
        assert "dp-day-in-range" in html

    def test_label_renders(self):
        html = str(date_picker(year=2026, month=3, label="Start Date"))
        assert "Start Date" in html
        assert 'class="form-label"' in html

    def test_form_group_wrapper(self):
        html = str(date_picker(year=2026, month=3))
        assert 'class="form-group"' in html


# ─── File Dropzone ───


class TestFileDropzoneCSS:
    def test_wrapper_class(self):
        html = str(file_dropzone(name="upload"))
        assert 'class="dropzone"' in html

    def test_input_class(self):
        html = str(file_dropzone(name="upload"))
        assert 'class="dropzone-input"' in html

    def test_icon_class(self):
        html = str(file_dropzone(name="upload"))
        assert 'class="dz-icon"' in html

    def test_text_class(self):
        html = str(file_dropzone(name="upload"))
        assert 'class="dz-text"' in html

    def test_browse_class(self):
        html = str(file_dropzone(name="upload"))
        assert 'class="dz-browse"' in html

    def test_hint_class(self):
        html = str(file_dropzone(name="upload"))
        assert 'class="dz-hint"' in html

    def test_file_count_class(self):
        html = str(file_dropzone(name="upload"))
        assert 'class="dz-file-count"' in html

    def test_dragover_adds_class(self):
        html = str(file_dropzone(name="upload"))
        assert "dropzone-over" in html  # referenced in ondragover JS

    def test_has_file_class_in_js(self):
        html = str(file_dropzone(name="upload"))
        assert "dropzone-has-file" in html  # referenced in ondrop/onchange JS

    def test_accept_attribute(self):
        html = str(file_dropzone(name="upload", accept=".pdf,.doc"))
        assert 'accept=".pdf,.doc"' in html

    def test_multiple_attribute(self):
        html = str(file_dropzone(name="upload", multiple=True))
        assert "multiple" in html

    def test_label_renders(self):
        html = str(file_dropzone(name="upload", label="Upload Files"))
        assert 'class="form-label"' in html
        assert "Upload Files" in html

    def test_max_size_in_hint(self):
        html = str(file_dropzone(name="upload", max_size_mb=25))
        assert "25 MB" in html
