"""Tests for v2.0 final batch — 12 remaining components."""
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
import pytest


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ─── Map Picker ───

class TestMapPicker:
    def test_basic_render(self):
        html = render('{% map_picker lat=40.7128 lng=-74.006 pick_event="set_location" %}')
        assert "dj-map-picker" in html
        assert 'data-lat="40.7128"' in html
        assert 'data-lng="-74.006"' in html
        assert 'dj-hook="MapPicker"' in html

    def test_zoom(self):
        html = render('{% map_picker lat=0 lng=0 zoom=15 %}')
        assert 'data-zoom="15"' in html

    def test_height(self):
        html = render('{% map_picker lat=0 lng=0 height="300px" %}')
        assert 'height:300px' in html

    def test_pick_event(self):
        html = render('{% map_picker lat=0 lng=0 pick_event="location_picked" %}')
        assert 'data-pick-event="location_picked"' in html

    def test_custom_class(self):
        html = render('{% map_picker lat=0 lng=0 class="my-map" %}')
        assert "dj-map-picker my-map" in html

    def test_accessibility(self):
        html = render('{% map_picker lat=0 lng=0 %}')
        assert 'role="application"' in html
        assert 'aria-label="Map picker"' in html

    def test_xss_pick_event(self):
        html = render(
            '{% map_picker lat=0 lng=0 pick_event=xss %}',
            {"xss": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html or "&#" in html or "&quot;" in html


# ─── Prompt Editor ───

class TestPromptEditor:
    def test_basic_render(self):
        html = render(
            '{% prompt_editor template=t variables=v event="save" %}',
            {"t": "Hello {{name}}", "v": {"name": "Alice"}},
        )
        assert "dj-prompt-editor" in html
        assert "Hello {{name}}" in html
        assert "dj-prompt-editor__var" in html
        assert "name" in html

    def test_variable_highlight(self):
        html = render(
            '{% prompt_editor template=t variables=v %}',
            {"t": "Hi {{user}}", "v": {"user": "Bob"}},
        )
        assert "dj-prompt-editor__highlight" in html
        assert "Bob" in html

    def test_save_event(self):
        html = render(
            '{% prompt_editor template=t event="save_prompt" %}',
            {"t": "test"},
        )
        assert 'dj-click="save_prompt"' in html

    def test_rows(self):
        html = render(
            '{% prompt_editor template=t rows=10 %}',
            {"t": "test"},
        )
        assert 'rows="10"' in html

    def test_xss_template(self):
        html = render(
            '{% prompt_editor template=t event="save" %}',
            {"t": '<script>alert("xss")</script>'},
        )
        assert "<script>" not in html

    def test_xss_event(self):
        html = render(
            '{% prompt_editor template=t event=ev %}',
            {"t": "test", "ev": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html


# ─── Voice Input ───

class TestVoiceInput:
    def test_basic_render(self):
        html = render('{% voice_input event="transcribe" %}')
        assert "dj-voice-input" in html
        assert 'dj-hook="VoiceInput"' in html
        assert 'data-event="transcribe"' in html

    def test_lang(self):
        html = render('{% voice_input lang="fr-FR" %}')
        assert 'data-lang="fr-FR"' in html

    def test_default_lang(self):
        html = render('{% voice_input %}')
        assert 'data-lang="en-US"' in html

    def test_continuous(self):
        html = render('{% voice_input continuous=True %}')
        assert 'data-continuous="true"' in html

    def test_mic_svg(self):
        html = render('{% voice_input %}')
        assert "dj-voice-input__icon" in html
        assert "<svg" in html

    def test_pulse_element(self):
        html = render('{% voice_input %}')
        assert "dj-voice-input__pulse" in html

    def test_accessibility(self):
        html = render('{% voice_input %}')
        assert 'aria-label="Voice input"' in html
        assert 'aria-pressed="false"' in html

    def test_xss_event(self):
        html = render(
            '{% voice_input event=ev %}',
            {"ev": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html


# ─── Cron Input ───

class TestCronInput:
    def test_basic_render(self):
        html = render('{% cron_input name="schedule" value="0 9 * * 1-5" %}')
        assert "dj-cron-input" in html
        assert 'name="schedule"' in html
        assert 'value="0 9 * * 1-5"' in html

    def test_five_fields(self):
        html = render('{% cron_input name="s" value="0 9 * * 1-5" %}')
        assert "Minute" in html
        assert "Hour" in html
        assert "Day" in html
        assert "Month" in html
        assert "Weekday" in html

    def test_field_values(self):
        html = render('{% cron_input name="s" value="30 14 * * *" %}')
        assert 'value="30"' in html
        assert 'value="14"' in html

    def test_event(self):
        html = render('{% cron_input name="s" event="set_schedule" %}')
        assert 'dj-change="set_schedule"' in html

    def test_preview(self):
        html = render('{% cron_input name="s" value="0 9 * * 1-5" %}')
        assert "dj-cron-input__preview" in html
        assert "<code>" in html

    def test_xss_name(self):
        html = render(
            '{% cron_input name=n %}',
            {"n": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html

    def test_xss_event(self):
        html = render(
            '{% cron_input name="s" event=ev %}',
            {"ev": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html


# ─── Error Page ───

class TestErrorPage:
    def test_basic_render(self):
        html = render('{% error_page code=404 title="Not Found" %}')
        assert "dj-error-page" in html
        assert "404" in html
        assert "Not Found" in html

    def test_message(self):
        html = render('{% error_page code=500 title="Error" message="Something broke" %}')
        assert "Something broke" in html
        assert "dj-error-page__message" in html

    def test_action(self):
        html = render('{% error_page code=404 title="Not Found" action_url="/" action_label="Home" %}')
        assert 'href="/"' in html
        assert "Home" in html

    def test_role_alert(self):
        html = render('{% error_page code=500 %}')
        assert 'role="alert"' in html

    def test_custom_class(self):
        html = render('{% error_page code=404 class="my-error" %}')
        assert "dj-error-page my-error" in html

    def test_xss_title(self):
        html = render(
            '{% error_page code=404 title=t %}',
            {"t": '<script>alert(1)</script>'},
        )
        assert "<script>" not in html

    def test_xss_message(self):
        html = render(
            '{% error_page code=500 message=m %}',
            {"m": '<img src=x onerror=alert(1)>'},
        )
        # The < and > should be escaped so the img tag is not rendered
        assert "<img " not in html
        assert "&lt;img" in html


# ─── Image Upload Preview ───

class TestImageUploadPreview:
    def test_basic_render(self):
        html = render('{% image_upload_preview name="photos" max=5 event="upload" %}')
        assert "dj-img-upload" in html
        assert 'name="photos"' in html
        assert "Max 5 images" in html
        assert 'dj-hook="ImageUploadPreview"' in html

    def test_accept(self):
        html = render('{% image_upload_preview name="f" accept="image/png" %}')
        assert 'accept="image/png"' in html

    def test_dropzone(self):
        html = render('{% image_upload_preview name="f" %}')
        assert "dj-img-upload__dropzone" in html
        assert "Drop images here" in html

    def test_previews(self):
        html = render(
            '{% image_upload_preview name="f" previews=p %}',
            {"p": ["/img/1.jpg", "/img/2.jpg"]},
        )
        assert "dj-img-upload__previews" in html
        assert "dj-img-upload__thumb" in html
        assert "/img/1.jpg" in html

    def test_accessibility(self):
        html = render('{% image_upload_preview name="f" %}')
        assert 'aria-label="Upload images"' in html

    def test_xss_name(self):
        html = render(
            '{% image_upload_preview name=n %}',
            {"n": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html

    def test_xss_preview_url(self):
        html = render(
            '{% image_upload_preview name="f" previews=p %}',
            {"p": ['"><script>alert(1)</script>']},
        )
        assert "<script>" not in html


# ─── Animated Number ───

class TestAnimatedNumber:
    def test_basic_render(self):
        html = render('{% animated_number value=12345 %}')
        assert "dj-animated-number" in html
        assert 'dj-hook="AnimatedNumber"' in html
        assert "12,345" in html

    def test_prefix(self):
        html = render('{% animated_number value=100 prefix="$" %}')
        assert "dj-animated-number__prefix" in html
        assert "$" in html

    def test_suffix(self):
        html = render('{% animated_number value=95 suffix="%" %}')
        assert "dj-animated-number__suffix" in html
        assert "%" in html

    def test_duration(self):
        html = render('{% animated_number value=100 duration=1200 %}')
        assert 'data-duration="1200"' in html

    def test_decimals(self):
        html = render('{% animated_number value=99 decimals=2 %}')
        assert 'data-decimals="2"' in html

    def test_data_value(self):
        html = render('{% animated_number value=500 %}')
        assert 'data-value="500' in html

    def test_xss_prefix(self):
        html = render(
            '{% animated_number value=100 prefix=p %}',
            {"p": '<script>alert(1)</script>'},
        )
        assert "<script>" not in html

    def test_xss_suffix(self):
        html = render(
            '{% animated_number value=100 suffix=s %}',
            {"s": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html


# ─── Ribbon Badge ───

class TestRibbon:
    def test_basic_render(self):
        html = render('{% ribbon text="Popular" %}')
        assert "dj-ribbon" in html
        assert "Popular" in html
        assert "dj-ribbon__text" in html

    def test_variant_primary(self):
        html = render('{% ribbon text="New" variant="primary" %}')
        assert "dj-ribbon--primary" in html

    def test_variant_success(self):
        html = render('{% ribbon text="Sale" variant="success" %}')
        assert "dj-ribbon--success" in html

    def test_variant_danger(self):
        html = render('{% ribbon text="Hot" variant="danger" %}')
        assert "dj-ribbon--danger" in html

    def test_position_top_right(self):
        html = render('{% ribbon text="New" position="top-right" %}')
        assert "dj-ribbon--top-right" in html

    def test_position_top_left(self):
        html = render('{% ribbon text="New" position="top-left" %}')
        assert "dj-ribbon--top-left" in html

    def test_position_bottom_right(self):
        html = render('{% ribbon text="X" position="bottom-right" %}')
        assert "dj-ribbon--bottom-right" in html

    def test_aria_label(self):
        html = render('{% ribbon text="Featured" %}')
        assert 'aria-label="Featured"' in html

    def test_xss_text(self):
        html = render(
            '{% ribbon text=t %}',
            {"t": '<script>alert(1)</script>'},
        )
        assert "<script>" not in html

    def test_xss_class(self):
        html = render(
            '{% ribbon text="X" class=c %}',
            {"c": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html


# ─── Breadcrumb Dropdown ───

class TestBreadcrumbDropdown:
    def test_basic_render(self):
        items = [
            {"label": "Home", "url": "/"},
            {"label": "Products", "url": "/products"},
            {"label": "Item"},
        ]
        html = render(
            '{% breadcrumb_dropdown items=items %}',
            {"items": items},
        )
        assert "dj-breadcrumb" in html
        assert "Home" in html
        assert "Products" in html
        assert "Item" in html
        assert 'aria-label="Breadcrumb"' in html

    def test_links(self):
        items = [
            {"label": "Home", "url": "/"},
            {"label": "Current"},
        ]
        html = render(
            '{% breadcrumb_dropdown items=items %}',
            {"items": items},
        )
        assert 'href="/"' in html
        assert "dj-breadcrumb__link" in html

    def test_current_item(self):
        items = [
            {"label": "Home", "url": "/"},
            {"label": "Current"},
        ]
        html = render(
            '{% breadcrumb_dropdown items=items %}',
            {"items": items},
        )
        assert "dj-breadcrumb__current" in html
        assert 'aria-current="page"' in html

    def test_collapse_overflow(self):
        items = [
            {"label": "Home", "url": "/"},
            {"label": "A", "url": "/a"},
            {"label": "B", "url": "/b"},
            {"label": "C", "url": "/c"},
            {"label": "D", "url": "/d"},
            {"label": "Current"},
        ]
        html = render(
            '{% breadcrumb_dropdown items=items max_visible=4 %}',
            {"items": items},
        )
        assert "dj-breadcrumb__ellipsis" in html
        assert "dj-breadcrumb__dropdown" in html
        assert "dj-breadcrumb__toggle" in html

    def test_no_collapse_small_list(self):
        items = [
            {"label": "Home", "url": "/"},
            {"label": "Current"},
        ]
        html = render(
            '{% breadcrumb_dropdown items=items %}',
            {"items": items},
        )
        assert "dj-breadcrumb__ellipsis" not in html

    def test_xss_label(self):
        items = [{"label": '<script>alert(1)</script>', "url": "/"}]
        html = render(
            '{% breadcrumb_dropdown items=items %}',
            {"items": items},
        )
        assert "<script>" not in html

    def test_xss_url(self):
        items = [{"label": "X", "url": 'javascript:alert(1)" onclick="alert(1)'}]
        html = render(
            '{% breadcrumb_dropdown items=items %}',
            {"items": items},
        )
        assert "onclick" not in html


# ─── Data Card Grid ───

class TestDataCardGrid:
    def test_basic_render(self):
        items = [
            {"title": "Card 1", "description": "Desc 1", "category": "A"},
            {"title": "Card 2", "description": "Desc 2", "category": "B"},
        ]
        html = render(
            '{% data_card_grid items=items columns=3 %}',
            {"items": items},
        )
        assert "dj-data-card-grid" in html
        assert "Card 1" in html
        assert "Card 2" in html
        assert "dj-data-card-grid__grid" in html

    def test_columns(self):
        html = render(
            '{% data_card_grid items=items columns=4 %}',
            {"items": [{"title": "X"}]},
        )
        assert "--dj-data-card-grid-cols:4" in html

    def test_filter_buttons(self):
        items = [
            {"title": "X", "category": "Alpha"},
            {"title": "Y", "category": "Beta"},
        ]
        html = render(
            '{% data_card_grid items=items %}',
            {"items": items},
        )
        assert "dj-data-card-grid__filters" in html
        assert "Alpha" in html
        assert "Beta" in html
        assert "All" in html

    def test_event(self):
        items = [{"title": "X"}]
        html = render(
            '{% data_card_grid items=items event="select" %}',
            {"items": items},
        )
        assert 'dj-click="select"' in html

    def test_image(self):
        items = [{"title": "X", "image": "/img/card.jpg"}]
        html = render(
            '{% data_card_grid items=items %}',
            {"items": items},
        )
        assert "dj-data-card-grid__img" in html
        assert "/img/card.jpg" in html

    def test_role_list(self):
        html = render(
            '{% data_card_grid items=items %}',
            {"items": [{"title": "X"}]},
        )
        assert 'role="list"' in html
        assert 'role="listitem"' in html

    def test_xss_title(self):
        items = [{"title": '<script>alert(1)</script>'}]
        html = render(
            '{% data_card_grid items=items %}',
            {"items": items},
        )
        assert "<script>" not in html

    def test_xss_image(self):
        items = [{"title": "X", "image": '"><script>alert(1)</script>'}]
        html = render(
            '{% data_card_grid items=items %}',
            {"items": items},
        )
        assert "<script>" not in html


# ─── Agent Step Card ───

class TestAgentStep:
    def test_basic_render(self):
        html = render(
            '{% agent_step tool="search_db" status="complete" %}'
            'Found 12 results'
            '{% endagent_step %}'
        )
        assert "dj-agent-step" in html
        assert "search_db" in html
        assert "Found 12 results" in html
        assert "dj-agent-step--complete" in html

    def test_pending_status(self):
        html = render(
            '{% agent_step tool="fetch" status="pending" %}'
            'Waiting'
            '{% endagent_step %}'
        )
        assert "dj-agent-step--pending" in html

    def test_running_status(self):
        html = render(
            '{% agent_step tool="compute" status="running" %}'
            'Processing...'
            '{% endagent_step %}'
        )
        assert "dj-agent-step--running" in html

    def test_error_status(self):
        html = render(
            '{% agent_step tool="api_call" status="error" %}'
            'Connection refused'
            '{% endagent_step %}'
        )
        assert "dj-agent-step--error" in html

    def test_duration(self):
        html = render(
            '{% agent_step tool="search" status="complete" duration="1.2s" %}'
            'Done'
            '{% endagent_step %}'
        )
        assert "1.2s" in html
        assert "dj-agent-step__duration" in html

    def test_tool_name_display(self):
        html = render(
            '{% agent_step tool="vector_search" status="complete" %}'
            'Results'
            '{% endagent_step %}'
        )
        assert "dj-agent-step__tool" in html
        assert "vector_search" in html

    def test_role_listitem(self):
        html = render(
            '{% agent_step tool="x" status="complete" %}y{% endagent_step %}'
        )
        assert 'role="listitem"' in html

    def test_xss_tool(self):
        html = render(
            '{% agent_step tool=t status="complete" %}'
            'content'
            '{% endagent_step %}',
            {"t": '<script>alert(1)</script>'},
        )
        assert "<script>" not in html

    def test_xss_content(self):
        html = render(
            '{% agent_step tool="x" status="complete" %}'
            '<script>alert(1)</script>'
            '{% endagent_step %}'
        )
        assert "<script>" not in html


# ─── QR Code ───

class TestQRCode:
    def test_basic_render(self):
        html = render('{% qr_code data="https://example.com" %}')
        assert "dj-qr-code" in html
        assert "<svg" in html
        assert "<rect" in html

    def test_size_md(self):
        html = render('{% qr_code data="test" size="md" %}')
        assert 'width="200"' in html
        assert 'height="200"' in html

    def test_size_sm(self):
        html = render('{% qr_code data="test" size="sm" %}')
        assert 'width="128"' in html

    def test_size_lg(self):
        html = render('{% qr_code data="test" size="lg" %}')
        assert 'width="300"' in html

    def test_aria_label(self):
        html = render('{% qr_code data="https://example.com" %}')
        assert 'aria-label="QR code: https://example.com"' in html

    def test_fg_bg_colors(self):
        html = render('{% qr_code data="test" fg_color="#333" bg_color="#eee" %}')
        assert 'fill="#333"' in html
        assert 'fill="#eee"' in html

    def test_custom_class(self):
        html = render('{% qr_code data="test" class="my-qr" %}')
        assert "dj-qr-code my-qr" in html

    def test_finder_patterns_present(self):
        """QR code should have finder patterns (groups of filled rects in corners)."""
        html = render('{% qr_code data="test" %}')
        # Should have multiple rect elements for the matrix
        assert html.count("<rect") > 10

    def test_xss_data(self):
        html = render(
            '{% qr_code data=d %}',
            {"d": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html

    def test_xss_fg_color(self):
        html = render(
            '{% qr_code data="test" fg_color=c %}',
            {"c": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html
