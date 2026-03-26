"""Tests for v2.0 Batch 1 — Drag & Interactive components (7)."""
from django.template import Template, Context
import pytest


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ─── Sortable List ───

class TestSortableList:
    def test_basic_render(self):
        html = render(
            '{% sortable_list items=items move_event="reorder" %}',
            {"items": [
                {"id": "1", "label": "Alpha"},
                {"id": "2", "label": "Beta"},
            ]},
        )
        assert "dj-sortable-list" in html
        assert 'dj-hook="SortableList"' in html
        assert 'data-move-event="reorder"' in html
        assert 'data-id="1"' in html
        assert "Alpha" in html
        assert "Beta" in html
        assert 'role="list"' in html

    def test_handle_visible_by_default(self):
        html = render(
            '{% sortable_list items=items %}',
            {"items": [{"id": "1", "label": "X"}]},
        )
        assert "dj-sortable-list__handle" in html

    def test_disabled(self):
        html = render(
            '{% sortable_list items=items disabled=True %}',
            {"items": [{"id": "1", "label": "X"}]},
        )
        assert "dj-sortable-list--disabled" in html
        assert 'draggable="true"' not in html
        assert 'data-disabled="true"' in html

    def test_draggable_attribute(self):
        html = render(
            '{% sortable_list items=items %}',
            {"items": [{"id": "1", "label": "X"}]},
        )
        assert 'draggable="true"' in html

    def test_empty_items(self):
        html = render('{% sortable_list items=items %}', {"items": []})
        assert "dj-sortable-list" in html
        assert "dj-sortable-list__item" not in html

    def test_custom_event(self):
        html = render(
            '{% sortable_list items=items move_event="sort_items" %}',
            {"items": [{"id": "1", "label": "X"}]},
        )
        assert 'data-move-event="sort_items"' in html


# ─── Sortable Grid ───

class TestSortableGrid:
    def test_basic_render(self):
        html = render(
            '{% sortable_grid items=items columns=3 move_event="reorder" %}',
            {"items": [
                {"id": "1", "label": "Item A"},
                {"id": "2", "label": "Item B"},
            ]},
        )
        assert "dj-sortable-grid" in html
        assert 'dj-hook="SortableGrid"' in html
        assert "repeat(3,1fr)" in html
        assert "Item A" in html
        assert 'role="grid"' in html

    def test_columns(self):
        html = render(
            '{% sortable_grid items=items columns=5 %}',
            {"items": [{"id": "1", "label": "X"}]},
        )
        assert "repeat(5,1fr)" in html
        assert 'data-columns="5"' in html

    def test_thumbnail(self):
        html = render(
            '{% sortable_grid items=items %}',
            {"items": [{"id": "1", "label": "Photo", "thumbnail": "/img/1.jpg"}]},
        )
        assert "dj-sortable-grid__thumb" in html
        assert 'src="/img/1.jpg"' in html

    def test_disabled(self):
        html = render(
            '{% sortable_grid items=items disabled=True %}',
            {"items": [{"id": "1", "label": "X"}]},
        )
        assert "dj-sortable-grid--disabled" in html
        assert 'draggable="true"' not in html

    def test_custom_gap(self):
        html = render(
            '{% sortable_grid items=items gap="1rem" %}',
            {"items": [{"id": "1", "label": "X"}]},
        )
        assert "gap:1rem" in html


# ─── Image Cropper ───

class TestImageCropper:
    def test_basic_render(self):
        html = render(
            '{% image_cropper src="/img/photo.jpg" crop_event="save_crop" %}'
        )
        assert "dj-image-cropper" in html
        assert 'dj-hook="ImageCropper"' in html
        assert 'src="/img/photo.jpg"' in html
        assert 'data-crop-event="save_crop"' in html

    def test_aspect_ratio(self):
        html = render(
            '{% image_cropper src="/img/x.jpg" aspect_ratio="16/9" %}'
        )
        assert 'data-aspect-ratio="16/9"' in html

    def test_no_aspect_ratio_by_default(self):
        html = render('{% image_cropper src="/img/x.jpg" %}')
        assert "data-aspect-ratio" not in html

    def test_min_dimensions(self):
        html = render(
            '{% image_cropper src="/img/x.jpg" min_width=100 min_height=75 %}'
        )
        assert 'data-min-width="100"' in html
        assert 'data-min-height="75"' in html

    def test_disabled(self):
        html = render('{% image_cropper src="/img/x.jpg" disabled=True %}')
        assert "dj-image-cropper--disabled" in html

    def test_actions(self):
        html = render('{% image_cropper src="/img/x.jpg" %}')
        assert "dj-image-cropper__crop-btn" in html
        assert "dj-image-cropper__reset-btn" in html
        assert "Crop" in html
        assert "Reset" in html


# ─── Signature Pad ───

class TestSignaturePad:
    def test_basic_render(self):
        html = render('{% signature_pad name="sig" save_event="save_signature" %}')
        assert "dj-signature-pad" in html
        assert 'dj-hook="SignaturePad"' in html
        assert 'name="sig"' in html
        assert 'data-save-event="save_signature"' in html

    def test_canvas_dimensions(self):
        html = render('{% signature_pad name="s" width=600 height=300 %}')
        assert 'width="600"' in html
        assert 'height="300"' in html

    def test_pen_color(self):
        html = render('{% signature_pad name="s" pen_color="#FF0000" %}')
        assert 'data-pen-color="#FF0000"' in html

    def test_pen_width(self):
        html = render('{% signature_pad name="s" pen_width=3 %}')
        assert 'data-pen-width="3"' in html

    def test_disabled(self):
        html = render('{% signature_pad name="s" disabled=True %}')
        assert "dj-signature-pad--disabled" in html
        assert " disabled" in html

    def test_hidden_input(self):
        html = render('{% signature_pad name="my_sig" %}')
        assert 'type="hidden"' in html
        assert 'name="my_sig"' in html

    def test_actions(self):
        html = render('{% signature_pad name="s" %}')
        assert "Clear" in html
        assert "Save" in html


# ─── Resizable Panel ───

class TestResizablePanel:
    def test_basic_render(self):
        html = render(
            '{% resizable_panel direction="horizontal" %}'
            '<p>Content</p>'
            '{% endresizable_panel %}'
        )
        assert "dj-resizable-panel" in html
        assert "dj-resizable-panel--horizontal" in html
        assert 'dj-hook="ResizablePanel"' in html
        assert "Content" in html

    def test_vertical(self):
        html = render(
            '{% resizable_panel direction="vertical" %}x{% endresizable_panel %}'
        )
        assert "dj-resizable-panel--vertical" in html
        assert 'data-direction="vertical"' in html
        assert 'aria-orientation="vertical"' in html

    def test_handle_role(self):
        html = render(
            '{% resizable_panel %}x{% endresizable_panel %}'
        )
        assert 'role="separator"' in html
        assert 'tabindex="0"' in html

    def test_disabled(self):
        html = render(
            '{% resizable_panel disabled=True %}x{% endresizable_panel %}'
        )
        assert "dj-resizable-panel--disabled" in html
        assert 'data-disabled="true"' in html

    def test_initial_size(self):
        html = render(
            '{% resizable_panel initial_size="300px" %}x{% endresizable_panel %}'
        )
        assert "width:300px" in html

    def test_min_max_size(self):
        html = render(
            '{% resizable_panel min_size="150px" max_size="600px" %}'
            'x'
            '{% endresizable_panel %}'
        )
        assert "min-width:150px" in html
        assert "max-width:600px" in html


# ─── Image Lightbox ───

class TestLightbox:
    def test_hidden_when_closed(self):
        html = render(
            '{% lightbox images=images open=False %}',
            {"images": [{"src": "/a.jpg"}]},
        )
        assert html.strip() == ""

    def test_visible_when_open(self):
        html = render(
            '{% lightbox images=images open=is_open active=0 %}',
            {
                "images": [
                    {"src": "/a.jpg", "alt": "Photo A"},
                    {"src": "/b.jpg", "alt": "Photo B"},
                ],
                "is_open": True,
            },
        )
        assert "dj-lightbox" in html
        assert 'role="dialog"' in html
        assert 'aria-modal="true"' in html
        assert 'src="/a.jpg"' in html
        assert 'alt="Photo A"' in html

    def test_navigation_buttons(self):
        html = render(
            '{% lightbox images=images open=is_open %}',
            {
                "images": [{"src": "/a.jpg"}, {"src": "/b.jpg"}],
                "is_open": True,
            },
        )
        assert "dj-lightbox__prev" in html
        assert "dj-lightbox__next" in html

    def test_no_nav_single_image(self):
        html = render(
            '{% lightbox images=images open=is_open %}',
            {"images": [{"src": "/a.jpg"}], "is_open": True},
        )
        assert "dj-lightbox__prev" not in html
        assert "dj-lightbox__next" not in html

    def test_counter(self):
        html = render(
            '{% lightbox images=images open=is_open %}',
            {
                "images": [{"src": "/a.jpg"}, {"src": "/b.jpg"}],
                "is_open": True,
            },
        )
        assert "1 of 2" in html
        assert "dj-lightbox__counter" in html

    def test_caption(self):
        html = render(
            '{% lightbox images=images open=is_open %}',
            {
                "images": [{"src": "/a.jpg", "caption": "My caption"}],
                "is_open": True,
            },
        )
        assert "My caption" in html
        assert "dj-lightbox__caption" in html

    def test_close_event(self):
        html = render(
            '{% lightbox images=images open=is_open close_event="dismiss" %}',
            {"images": [{"src": "/a.jpg"}], "is_open": True},
        )
        assert 'dj-click="dismiss"' in html

    def test_navigate_event(self):
        html = render(
            '{% lightbox images=images open=is_open navigate_event="go_to" %}',
            {
                "images": [{"src": "/a.jpg"}, {"src": "/b.jpg"}],
                "is_open": True,
            },
        )
        assert 'dj-click="go_to"' in html


# ─── Dashboard Grid ───

class TestDashboardGrid:
    def test_basic_render(self):
        html = render(
            '{% dashboard_grid panels=panels columns=4 %}'
            '{% enddashboard_grid %}',
            {"panels": [
                {"id": "chart", "title": "Revenue", "col": 1, "row": 1,
                 "width": 2, "height": 1, "content": "<p>Chart</p>"},
            ]},
        )
        assert "dj-dashboard-grid" in html
        assert 'dj-hook="DashboardGrid"' in html
        assert "repeat(4,1fr)" in html
        assert "Revenue" in html
        assert "Chart" in html

    def test_panel_positioning(self):
        html = render(
            '{% dashboard_grid panels=panels %}'
            '{% enddashboard_grid %}',
            {"panels": [
                {"id": "p1", "title": "T", "col": 2, "row": 3,
                 "width": 3, "height": 2},
            ]},
        )
        assert "grid-column:2/span 3" in html
        assert "grid-row:3/span 2" in html

    def test_panel_draggable(self):
        html = render(
            '{% dashboard_grid panels=panels %}'
            '{% enddashboard_grid %}',
            {"panels": [{"id": "p1", "title": "T"}]},
        )
        assert 'draggable="true"' in html
        assert "dj-dashboard-grid__panel-drag" in html

    def test_panel_resize_handle(self):
        html = render(
            '{% dashboard_grid panels=panels %}'
            '{% enddashboard_grid %}',
            {"panels": [{"id": "p1", "title": "T"}]},
        )
        assert "dj-dashboard-grid__panel-resize" in html
        assert 'role="separator"' in html

    def test_events(self):
        html = render(
            '{% dashboard_grid panels=panels move_event="move" resize_event="resize" %}'
            '{% enddashboard_grid %}',
            {"panels": []},
        )
        assert 'data-move-event="move"' in html
        assert 'data-resize-event="resize"' in html

    def test_custom_row_height_and_gap(self):
        html = render(
            '{% dashboard_grid panels=panels row_height="150px" gap="0.5rem" %}'
            '{% enddashboard_grid %}',
            {"panels": []},
        )
        assert "minmax(150px,auto)" in html
        assert "gap:0.5rem" in html

    def test_child_content(self):
        html = render(
            '{% dashboard_grid panels=panels %}'
            '<div class="custom-panel">Custom</div>'
            '{% enddashboard_grid %}',
            {"panels": []},
        )
        assert "custom-panel" in html
        assert "Custom" in html


# ─── XSS Escaping ───

class TestXSSEscaping:
    """Verify user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_script_escaped(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # Sortable List
    def test_sortable_list_xss_label(self):
        html = render(
            '{% sortable_list items=items %}',
            {"items": [{"id": "1", "label": self.XSS}]},
        )
        self._assert_script_escaped(html)

    def test_sortable_list_xss_event(self):
        html = render(
            '{% sortable_list items=items move_event=xss %}',
            {"items": [{"id": "1", "label": "X"}], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_sortable_list_xss_id(self):
        html = render(
            '{% sortable_list items=items %}',
            {"items": [{"id": self.XSS_ATTR, "label": "X"}]},
        )
        self._assert_attr_escaped(html)

    # Sortable Grid
    def test_sortable_grid_xss_label(self):
        html = render(
            '{% sortable_grid items=items %}',
            {"items": [{"id": "1", "label": self.XSS}]},
        )
        self._assert_script_escaped(html)

    def test_sortable_grid_xss_event(self):
        html = render(
            '{% sortable_grid items=items move_event=xss %}',
            {"items": [{"id": "1", "label": "X"}], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_sortable_grid_xss_thumbnail(self):
        html = render(
            '{% sortable_grid items=items %}',
            {"items": [{"id": "1", "label": "X", "thumbnail": self.XSS_ATTR}]},
        )
        self._assert_attr_escaped(html)

    # Image Cropper
    def test_image_cropper_xss_src(self):
        html = render(
            '{% image_cropper src=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_image_cropper_xss_event(self):
        html = render(
            '{% image_cropper src="/x.jpg" crop_event=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_image_cropper_xss_aspect_ratio(self):
        html = render(
            '{% image_cropper src="/x.jpg" aspect_ratio=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Signature Pad
    def test_signature_pad_xss_name(self):
        html = render(
            '{% signature_pad name=xss %}',
            {"xss": self.XSS},
        )
        self._assert_script_escaped(html)

    def test_signature_pad_xss_event(self):
        html = render(
            '{% signature_pad name="s" save_event=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_signature_pad_xss_pen_color(self):
        html = render(
            '{% signature_pad name="s" pen_color=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Resizable Panel
    def test_resizable_panel_xss_class(self):
        html = render(
            '{% resizable_panel class=xss %}x{% endresizable_panel %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_resizable_panel_xss_min_size(self):
        html = render(
            '{% resizable_panel min_size=xss %}x{% endresizable_panel %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Lightbox
    def test_lightbox_xss_close_event(self):
        html = render(
            '{% lightbox images=images open=is_open close_event=xss %}',
            {"images": [{"src": "/a.jpg"}], "is_open": True, "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_lightbox_xss_navigate_event(self):
        html = render(
            '{% lightbox images=images open=is_open navigate_event=xss %}',
            {
                "images": [{"src": "/a.jpg"}, {"src": "/b.jpg"}],
                "is_open": True,
                "xss": self.XSS_ATTR,
            },
        )
        self._assert_attr_escaped(html)

    def test_lightbox_xss_image_src(self):
        html = render(
            '{% lightbox images=images open=is_open %}',
            {"images": [{"src": self.XSS_ATTR}], "is_open": True},
        )
        self._assert_attr_escaped(html)

    def test_lightbox_xss_caption(self):
        html = render(
            '{% lightbox images=images open=is_open %}',
            {"images": [{"src": "/a.jpg", "caption": self.XSS}], "is_open": True},
        )
        assert "<script>" not in html

    def test_lightbox_xss_alt(self):
        html = render(
            '{% lightbox images=images open=is_open %}',
            {"images": [{"src": "/a.jpg", "alt": self.XSS_ATTR}], "is_open": True},
        )
        self._assert_attr_escaped(html)

    # Dashboard Grid
    def test_dashboard_grid_xss_move_event(self):
        html = render(
            '{% dashboard_grid panels=panels move_event=xss %}'
            '{% enddashboard_grid %}',
            {"panels": [], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_dashboard_grid_xss_resize_event(self):
        html = render(
            '{% dashboard_grid panels=panels resize_event=xss %}'
            '{% enddashboard_grid %}',
            {"panels": [], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_dashboard_grid_xss_panel_title(self):
        html = render(
            '{% dashboard_grid panels=panels %}'
            '{% enddashboard_grid %}',
            {"panels": [{"id": "p", "title": self.XSS}]},
        )
        assert "<script>" not in html

    def test_dashboard_grid_xss_panel_id(self):
        html = render(
            '{% dashboard_grid panels=panels %}'
            '{% enddashboard_grid %}',
            {"panels": [{"id": self.XSS_ATTR, "title": "T"}]},
        )
        self._assert_attr_escaped(html)
