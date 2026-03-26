"""Tests for djust-components template tags."""
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


# ─── Scroll Area ───

class TestScrollArea:
    def test_scroll_area_default(self):
        html = render('{% scroll_area %}Some content{% endscroll_area %}')
        assert "dj-scroll-area" in html
        assert "Some content" in html
        assert "--dj-scroll-area-max-height: 400px" in html

    def test_scroll_area_custom_height(self):
        html = render('{% scroll_area max_height="600px" %}content{% endscroll_area %}')
        assert "--dj-scroll-area-max-height: 600px" in html

    def test_scroll_area_variable_height(self):
        html = render('{% scroll_area max_height=h %}content{% endscroll_area %}', {"h": "300px"})
        assert "--dj-scroll-area-max-height: 300px" in html

    def test_scroll_area_custom_class(self):
        html = render('{% scroll_area custom_class="my-scroller" %}content{% endscroll_area %}')
        assert "my-scroller" in html

    def test_scroll_area_xss_max_height(self):
        html = render(
            '{% scroll_area max_height=xss %}content{% endscroll_area %}',
            {"xss": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html or "&quot;" in html

    def test_scroll_area_xss_custom_class(self):
        html = render(
            '{% scroll_area custom_class=xss %}content{% endscroll_area %}',
            {"xss": '" onmouseover="alert(1)" x="'},
        )
        assert '" onmouseover="' not in html
        assert "&quot;" in html


# ─── Callout / Blockquote ───

class TestCallout:
    def test_callout_default(self):
        html = render('{% callout %}Important note{% endcallout %}')
        assert "dj-callout" in html
        assert "Important note" in html
        assert "dj-callout--" not in html  # no type variant for default

    def test_callout_with_type(self):
        for t in ("info", "warning", "danger", "success"):
            html = render(f'{{% callout type="{t}" %}}msg{{% endcallout %}}')
            assert f"dj-callout--{t}" in html

    def test_callout_with_title(self):
        html = render('{% callout title="Heads up" %}body{% endcallout %}')
        assert "dj-callout__title" in html
        assert "Heads up" in html

    def test_callout_with_icon(self):
        html = render('{% callout icon="!" %}body{% endcallout %}')
        assert "dj-callout__icon" in html
        assert "!" in html

    def test_callout_default_icon_for_type(self):
        html = render('{% callout type="info" %}body{% endcallout %}')
        assert "dj-callout__icon" in html

    def test_callout_variable_title(self):
        html = render('{% callout title=my_title %}body{% endcallout %}', {"my_title": "Dynamic"})
        assert "Dynamic" in html

    def test_callout_custom_class(self):
        html = render('{% callout custom_class="extra" %}body{% endcallout %}')
        assert "extra" in html

    def test_callout_xss_title(self):
        html = render(
            '{% callout title=xss %}body{% endcallout %}',
            {"xss": '<script>alert(1)</script>'},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_callout_xss_icon(self):
        html = render(
            '{% callout icon=xss %}body{% endcallout %}',
            {"xss": '<script>alert(1)</script>'},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_callout_xss_type_attr(self):
        html = render(
            '{% callout type=xss %}body{% endcallout %}',
            {"xss": '" onmouseover="alert(1)" x="'},
        )
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    def test_callout_xss_custom_class(self):
        html = render(
            '{% callout custom_class=xss %}body{% endcallout %}',
            {"xss": '" onmouseover="alert(1)" x="'},
        )
        assert '" onmouseover="' not in html
        assert "&quot;" in html


# ─── Aspect Ratio ───

class TestAspectRatio:
    def test_aspect_ratio_default(self):
        html = render('{% aspect_ratio %}child content{% endaspect_ratio %}')
        assert "dj-aspect-ratio" in html
        assert "child content" in html
        assert "aspect-ratio: 16/9" in html

    def test_aspect_ratio_custom(self):
        html = render('{% aspect_ratio ratio="4/3" %}content{% endaspect_ratio %}')
        assert "aspect-ratio: 4/3" in html

    def test_aspect_ratio_1_1(self):
        html = render('{% aspect_ratio ratio="1/1" %}content{% endaspect_ratio %}')
        assert "aspect-ratio: 1/1" in html

    def test_aspect_ratio_variable(self):
        html = render('{% aspect_ratio ratio=r %}content{% endaspect_ratio %}', {"r": "21/9"})
        assert "aspect-ratio: 21/9" in html

    def test_aspect_ratio_custom_class(self):
        html = render('{% aspect_ratio custom_class="video-frame" %}content{% endaspect_ratio %}')
        assert "video-frame" in html

    def test_aspect_ratio_xss_ratio(self):
        html = render(
            '{% aspect_ratio ratio=xss %}content{% endaspect_ratio %}',
            {"xss": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html or "&quot;" in html

    def test_aspect_ratio_xss_custom_class(self):
        html = render(
            '{% aspect_ratio custom_class=xss %}content{% endaspect_ratio %}',
            {"xss": '" onmouseover="alert(1)" x="'},
        )
        assert '" onmouseover="' not in html
        assert "&quot;" in html


# ─── Description List ───

class TestDescriptionList:
    def test_dl_basic(self):
        items = [{"term": "Name", "detail": "Alice"}, {"term": "Role", "detail": "Engineer"}]
        html = render('{% description_list items=items %}', {"items": items})
        assert "dj-dl" in html
        assert "Name" in html
        assert "Alice" in html
        assert "Role" in html
        assert "Engineer" in html

    def test_dl_horizontal(self):
        items = [{"term": "K", "detail": "V"}]
        html = render('{% description_list items=items layout="horizontal" %}', {"items": items})
        assert "dj-dl--horizontal" in html

    def test_dl_vertical_default(self):
        items = [{"term": "K", "detail": "V"}]
        html = render('{% description_list items=items %}', {"items": items})
        assert "dj-dl--horizontal" not in html

    def test_dl_empty_items(self):
        html = render('{% description_list items=items %}', {"items": []})
        assert "dj-dl" in html
        assert "<dt" not in html

    def test_dl_custom_class(self):
        items = [{"term": "A", "detail": "B"}]
        html = render('{% description_list items=items custom_class="extra" %}', {"items": items})
        assert "extra" in html

    def test_dl_structure(self):
        items = [{"term": "T", "detail": "D"}]
        html = render('{% description_list items=items %}', {"items": items})
        assert "dj-dl__pair" in html
        assert "dj-dl__term" in html
        assert "dj-dl__detail" in html

    def test_dl_xss_term(self):
        items = [{"term": '<script>alert(1)</script>', "detail": "safe"}]
        html = render('{% description_list items=items %}', {"items": items})
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_dl_xss_detail(self):
        items = [{"term": "safe", "detail": '<script>alert(1)</script>'}]
        html = render('{% description_list items=items %}', {"items": items})
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_dl_xss_custom_class(self):
        items = [{"term": "A", "detail": "B"}]
        html = render(
            '{% description_list items=items custom_class=xss %}',
            {"items": items, "xss": '" onmouseover="alert(1)" x="'},
        )
        assert '" onmouseover="' not in html
        assert "&quot;" in html


# ─── Sticky Header ───

class TestStickyHeader:
    def test_sticky_header_default(self):
        html = render('{% sticky_header %}Nav Bar{% endsticky_header %}')
        assert "dj-sticky-header" in html
        assert "Nav Bar" in html
        assert "position: sticky" in html
        assert "top: 0" in html

    def test_sticky_header_custom_offset(self):
        html = render('{% sticky_header offset="64px" %}content{% endsticky_header %}')
        assert "top: 64px" in html

    def test_sticky_header_custom_z_index(self):
        html = render('{% sticky_header z_index="50" %}content{% endsticky_header %}')
        assert "z-index: 50" in html

    def test_sticky_header_variable_offset(self):
        html = render('{% sticky_header offset=off %}content{% endsticky_header %}', {"off": "2rem"})
        assert "top: 2rem" in html

    def test_sticky_header_custom_class(self):
        html = render('{% sticky_header custom_class="my-header" %}content{% endsticky_header %}')
        assert "my-header" in html

    def test_sticky_header_xss_offset(self):
        html = render(
            '{% sticky_header offset=xss %}content{% endsticky_header %}',
            {"xss": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html or "&quot;" in html

    def test_sticky_header_xss_z_index(self):
        html = render(
            '{% sticky_header z_index=xss %}content{% endsticky_header %}',
            {"xss": '"><script>alert(1)</script>'},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html or "&quot;" in html

    def test_sticky_header_xss_custom_class(self):
        html = render(
            '{% sticky_header custom_class=xss %}content{% endsticky_header %}',
            {"xss": '" onmouseover="alert(1)" x="'},
        )
        assert '" onmouseover="' not in html
        assert "&quot;" in html
