"""Tests for djust-components template tags."""
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


# ─── Modal ───

class TestModal:
    def test_modal_hidden_when_closed(self):
        html = render('{% modal id="m" open=False title="Hi" %}body{% endmodal %}')
        assert html.strip() == ""

    def test_modal_visible_when_open(self):
        html = render('{% modal id="m" open=is_open title="Confirm" %}body text{% endmodal %}', {"is_open": True})
        assert "dj-modal-backdrop" in html
        assert "Confirm" in html
        assert "body text" in html
        assert 'dj-click="close_modal"' in html

    def test_modal_custom_close_event(self):
        html = render('{% modal open=is_open close_event="my_close" %}x{% endmodal %}', {"is_open": True})
        assert 'dj-click="my_close"' in html

    def test_modal_sizes(self):
        for size in ("sm", "md", "lg", "xl"):
            html = render(f'{{% modal open=is_open size="{size}" %}}x{{% endmodal %}}', {"is_open": True})
            assert f"dj-modal--{size}" in html


# ─── Tabs ───

class TestTabs:
    def test_tabs_render_active(self):
        html = render(
            '{% tabs active=active %}'
            '{% tab id="a" label="Alpha" %}Alpha content{% endtab %}'
            '{% tab id="b" label="Beta" %}Beta content{% endtab %}'
            '{% endtabs %}',
            {"active": "a"},
        )
        assert "dj-tab--active" in html
        assert "Alpha content" in html
        assert "Beta content" not in html

    def test_tabs_switch(self):
        html = render(
            '{% tabs active=active %}'
            '{% tab id="a" label="A" %}AAA{% endtab %}'
            '{% tab id="b" label="B" %}BBB{% endtab %}'
            '{% endtabs %}',
            {"active": "b"},
        )
        assert "BBB" in html
        assert "AAA" not in html

    def test_tabs_custom_event(self):
        html = render(
            '{% tabs active="a" event="switch_tab" %}'
            '{% tab id="a" label="A" %}A{% endtab %}'
            '{% endtabs %}',
            {},
        )
        assert 'dj-click="switch_tab"' in html


# ─── Accordion ───

class TestAccordion:
    def test_accordion_open_item(self):
        html = render(
            '{% accordion active=open_id %}'
            '{% accordion_item id="q1" title="Question 1" %}Answer 1{% endaccordion_item %}'
            '{% accordion_item id="q2" title="Question 2" %}Answer 2{% endaccordion_item %}'
            '{% endaccordion %}',
            {"open_id": "q1"},
        )
        assert "Answer 1" in html
        assert "Answer 2" not in html
        assert "dj-accordion__chevron--open" in html

    def test_accordion_none_open(self):
        html = render(
            '{% accordion active="" %}'
            '{% accordion_item id="q1" title="Q1" %}A1{% endaccordion_item %}'
            '{% endaccordion %}',
            {},
        )
        assert "A1" not in html


# ─── Dropdown ───

class TestDropdown:
    def test_dropdown_closed(self):
        html = render('{% dropdown label="Menu" open=False %}items{% enddropdown %}')
        assert "dj-dropdown__menu" not in html

    def test_dropdown_open(self):
        html = render('{% dropdown label="Menu" open=is_open %}items{% enddropdown %}', {"is_open": True})
        assert "dj-dropdown__menu" in html
        assert "items" in html


# ─── Tooltip ───

class TestTooltip:
    def test_tooltip_renders(self):
        html = render('{% tooltip text="Hello" position="top" %}hover me{% endtooltip %}')
        assert "dj-tooltip--top" in html
        assert "Hello" in html
        assert "hover me" in html


# ─── Card ───

class TestCard:
    def test_card_with_title(self):
        html = render('{% card title="My Card" subtitle="sub" %}content{% endcard %}')
        assert "My Card" in html
        assert "sub" in html
        assert "content" in html
        assert "dj-card--default" in html

    def test_card_variant(self):
        html = render('{% card variant="elevated" %}x{% endcard %}')
        assert "dj-card--elevated" in html


# ─── Progress (inclusion tag) ───

class TestProgress:
    def test_progress_renders(self):
        html = render('{% progress value=75 label="Upload" color="success" %}')
        assert "75%" in html
        assert "Upload" in html
        assert "dj-progress__fill--success" in html


# ─── Badge (inclusion tag) ───

class TestBadge:
    def test_badge_renders(self):
        html = render('{% badge label="API" status="online" %}')
        assert "API" in html
        assert "dj-badge--online" in html

    def test_badge_pulse(self):
        html = render('{% badge label="X" status="error" pulse=True %}')
        assert "dj-badge__dot--pulse" in html


# ─── Avatar (inclusion tag) ───

class TestAvatar:
    def test_avatar_with_initials(self):
        html = render('{% avatar initials="JD" size="lg" status="online" %}')
        assert "JD" in html
        assert "dj-avatar--lg" in html
        assert "dj-avatar__status--online" in html

    def test_avatar_with_src(self):
        html = render('{% avatar src="/img/me.jpg" alt="Me" %}')
        assert 'src="/img/me.jpg"' in html


# ─── Toast (inclusion tag) ───

class TestToast:
    def test_toast_renders(self):
        toasts = [
            {"id": 1, "type": "success", "message": "Done!"},
            {"id": 2, "type": "error", "message": "Failed"},
        ]
        html = render('{% toast_container toasts %}', {"toasts": toasts})
        assert "Done!" in html
        assert "Failed" in html
        assert "dj-toast--success" in html
        assert "dj-toast--error" in html

    def test_toast_empty(self):
        html = render('{% toast_container toasts %}', {"toasts": []})
        assert "dj-toast-container--empty" in html


# ─── XSS Escaping ───

class TestXSSEscaping:
    """Verify that user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    # A payload that breaks out of an HTML attribute if quotes are not escaped
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_attr_escaped(self, html, payload=None):
        """Assert that a quote-injection payload cannot break out of an attribute."""
        if payload is None:
            payload = self.XSS_ATTR
        # The raw unescaped double-quote must not appear adjacent to the event handler
        assert '" onmouseover="' not in html
        # The attribute-breaking quote must be entity-encoded
        assert "&quot;" in html

    # Modal
    def test_modal_title_xss(self):
        html = render(
            '{% modal open=True title=xss_title %}body{% endmodal %}',
            {"xss_title": self.XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_modal_close_event_xss(self):
        html = render(
            '{% modal open=True close_event=bad_event %}body{% endmodal %}',
            {"bad_event": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Tabs
    def test_tabs_id_xss(self):
        html = render(
            '{% tabs id=xss_id active="a" %}'
            '{% tab id="a" label="A" %}A{% endtab %}'
            '{% endtabs %}',
            {"xss_id": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_tabs_label_xss(self):
        html = render(
            '{% tabs active="a" %}'
            '{% tab id="a" label=xss_label %}A{% endtab %}'
            '{% endtabs %}',
            {"xss_label": self.XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_tabs_event_xss(self):
        html = render(
            '{% tabs active="a" event=bad_event %}'
            '{% tab id="a" label="A" %}A{% endtab %}'
            '{% endtabs %}',
            {"bad_event": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Accordion
    def test_accordion_title_xss(self):
        html = render(
            '{% accordion active="q1" %}'
            '{% accordion_item id="q1" title=xss_title %}Answer{% endaccordion_item %}'
            '{% endaccordion %}',
            {"xss_title": self.XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_accordion_id_xss(self):
        html = render(
            '{% accordion active="" id=xss_id %}'
            '{% accordion_item id="q1" title="Q" %}A{% endaccordion_item %}'
            '{% endaccordion %}',
            {"xss_id": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Dropdown
    def test_dropdown_label_xss(self):
        html = render(
            '{% dropdown label=xss_label open=True %}items{% enddropdown %}',
            {"xss_label": self.XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_dropdown_toggle_event_xss(self):
        html = render(
            '{% dropdown label="Menu" open=True toggle_event=bad_event %}items{% enddropdown %}',
            {"bad_event": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_dropdown_id_xss(self):
        html = render(
            '{% dropdown label="Menu" open=True id=xss_id %}items{% enddropdown %}',
            {"xss_id": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Tooltip
    def test_tooltip_text_xss(self):
        html = render(
            '{% tooltip text=xss_text %}hover me{% endtooltip %}',
            {"xss_text": self.XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_tooltip_position_xss(self):
        html = render(
            '{% tooltip text="tip" position=xss_pos %}hover me{% endtooltip %}',
            {"xss_pos": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Card
    def test_card_title_xss(self):
        html = render(
            '{% card title=xss_title %}content{% endcard %}',
            {"xss_title": self.XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_card_subtitle_xss(self):
        html = render(
            '{% card title="Title" subtitle=xss_sub %}content{% endcard %}',
            {"xss_sub": self.XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_card_extra_class_xss(self):
        html = render(
            '{% card class=xss_class %}content{% endcard %}',
            {"xss_class": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)
