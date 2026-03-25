"""Tests for utility components: Scroll to Top, Code Snippet, Responsive Image,
Relative Time, and Copyable Text."""
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


# ═══════════════════════════════════════════════════════════════════════════
# 1. Scroll to Top (#125)
# ═══════════════════════════════════════════════════════════════════════════

class TestScrollToTop:
    def test_default_renders_button(self):
        html = render("{% scroll_to_top %}")
        assert "dj-scroll-to-top" in html
        assert 'data-threshold="300px"' in html
        assert 'aria-label="Back to top"' in html
        assert "<svg" in html

    def test_custom_threshold(self):
        html = render('{% scroll_to_top threshold="500px" %}')
        assert 'data-threshold="500px"' in html

    def test_custom_label(self):
        html = render('{% scroll_to_top label="Go up" %}')
        assert 'aria-label="Go up"' in html
        assert 'title="Go up"' in html

    def test_custom_class(self):
        html = render('{% scroll_to_top custom_class="my-btn" %}')
        assert "dj-scroll-to-top my-btn" in html

    def test_hidden_by_default(self):
        html = render("{% scroll_to_top %}")
        assert 'style="display:none"' in html

    def test_variable_threshold(self):
        html = render('{% scroll_to_top threshold=val %}', {"val": "200px"})
        assert 'data-threshold="200px"' in html


# ═══════════════════════════════════════════════════════════════════════════
# 2. Code Snippet (#139)
# ═══════════════════════════════════════════════════════════════════════════

class TestCodeSnippet:
    def test_basic_render(self):
        html = render('{% code_snippet code="echo hi" language="bash" %}')
        assert "dj-code-snippet" in html
        assert "echo hi" in html
        assert "dj-code-snippet__lang" in html
        assert "bash" in html.upper() or "bash" in html

    def test_no_language_no_badge(self):
        html = render('{% code_snippet code="print(1)" %}')
        assert "dj-code-snippet__lang" not in html

    def test_copy_button_present(self):
        html = render('{% code_snippet code="x" %}')
        assert "dj-code-snippet__copy" in html
        assert 'aria-label="Copy code"' in html

    def test_custom_class(self):
        html = render('{% code_snippet code="x" custom_class="wide" %}')
        assert "dj-code-snippet wide" in html

    def test_code_in_pre_code(self):
        html = render('{% code_snippet code="hello world" %}')
        assert "<pre" in html
        assert "<code" in html
        assert "hello world" in html

    def test_html_entities_escaped_in_code(self):
        html = render('{% code_snippet code=val %}', {"val": "<div>test</div>"})
        assert "&lt;div&gt;" in html
        assert "<div>test</div>" not in html

    def test_variable_code(self):
        html = render('{% code_snippet code=snippet language=lang %}',
                       {"snippet": "pip install djust", "lang": "bash"})
        assert "pip install djust" in html
        assert "bash" in html.lower()


# ═══════════════════════════════════════════════════════════════════════════
# 3. Responsive Image (#140)
# ═══════════════════════════════════════════════════════════════════════════

class TestResponsiveImage:
    def test_basic_render(self):
        html = render('{% responsive_image src="/img.jpg" alt="test" %}')
        assert "dj-responsive-image" in html
        assert 'src="/img.jpg"' in html
        assert 'alt="test"' in html

    def test_lazy_loading_default(self):
        html = render('{% responsive_image src="/img.jpg" alt="" %}')
        assert 'loading="lazy"' in html

    def test_lazy_false(self):
        html = render('{% responsive_image src="/img.jpg" alt="" lazy=False %}')
        assert 'loading="lazy"' not in html

    def test_aspect_ratio(self):
        html = render('{% responsive_image src="/img.jpg" alt="" aspect_ratio="16/9" %}')
        assert "aspect-ratio:16/9" in html

    def test_srcset(self):
        html = render(
            '{% responsive_image src="/img.jpg" alt="" srcset="/img-2x.jpg 2x" %}'
        )
        assert 'srcset="/img-2x.jpg 2x"' in html

    def test_sizes(self):
        html = render(
            '{% responsive_image src="/img.jpg" alt="" sizes="(max-width:600px) 100vw" %}'
        )
        assert 'sizes="(max-width:600px) 100vw"' in html

    def test_placeholder_adds_blur_up_class(self):
        html = render(
            '{% responsive_image src="/img.jpg" alt="" placeholder="/thumb.jpg" %}'
        )
        assert "dj-responsive-image--blur-up" in html
        assert "dj-responsive-image__placeholder" in html
        assert 'src="/thumb.jpg"' in html

    def test_no_placeholder_no_blur_up(self):
        html = render('{% responsive_image src="/img.jpg" alt="" %}')
        assert "dj-responsive-image--blur-up" not in html
        assert "dj-responsive-image__placeholder" not in html

    def test_custom_class(self):
        html = render('{% responsive_image src="/img.jpg" alt="" custom_class="hero" %}')
        assert "dj-responsive-image hero" in html

    def test_variable_src(self):
        html = render('{% responsive_image src=url alt="img" %}', {"url": "/photo.webp"})
        assert 'src="/photo.webp"' in html


# ═══════════════════════════════════════════════════════════════════════════
# 4. Relative Time (#146)
# ═══════════════════════════════════════════════════════════════════════════

class TestRelativeTime:
    def test_basic_render(self):
        html = render('{% relative_time datetime="2026-01-01T00:00:00" %}')
        assert "dj-relative-time" in html
        assert "<time" in html
        assert 'datetime="2026-01-01T00:00:00"' in html

    def test_auto_update_default(self):
        html = render('{% relative_time datetime="2026-01-01T00:00:00" %}')
        assert 'data-auto-update="true"' in html

    def test_auto_update_false(self):
        html = render(
            '{% relative_time datetime="2026-01-01T00:00:00" auto_update=False %}'
        )
        assert 'data-auto-update="false"' in html

    def test_custom_interval(self):
        html = render(
            '{% relative_time datetime="2026-01-01T00:00:00" interval="30" %}'
        )
        assert 'data-interval="30"' in html

    def test_default_interval(self):
        html = render('{% relative_time datetime="2026-01-01T00:00:00" %}')
        assert 'data-interval="60"' in html

    def test_custom_class(self):
        html = render(
            '{% relative_time datetime="2026-01-01T00:00:00" custom_class="ts" %}'
        )
        assert "dj-relative-time ts" in html

    def test_variable_datetime(self):
        from datetime import datetime as dt
        html = render(
            '{% relative_time datetime=created %}',
            {"created": dt(2026, 3, 1, 12, 0, 0)},
        )
        assert "2026-03-01T12:00:00" in html

    def test_datetime_object_isoformat(self):
        from datetime import datetime as dt
        html = render(
            '{% relative_time datetime=ts %}',
            {"ts": dt(2025, 6, 15, 8, 30)},
        )
        assert "2025-06-15T08:30:00" in html


# ═══════════════════════════════════════════════════════════════════════════
# 5. Copyable Text (#153)
# ═══════════════════════════════════════════════════════════════════════════

class TestCopyableText:
    def test_basic_render(self):
        html = render("{% copyable_text %}my-api-key{% endcopyable_text %}")
        assert "dj-copyable-text" in html
        assert "my-api-key" in html
        assert 'data-copy-text="my-api-key"' in html

    def test_default_copied_label(self):
        html = render("{% copyable_text %}key{% endcopyable_text %}")
        assert 'data-copied-label="Copied!"' in html
        assert "dj-copyable-text__tooltip" in html

    def test_custom_copied_label(self):
        html = render(
            '{% copyable_text copied_label="Done!" %}key{% endcopyable_text %}'
        )
        assert 'data-copied-label="Done!"' in html

    def test_custom_class(self):
        html = render(
            '{% copyable_text custom_class="mono" %}key{% endcopyable_text %}'
        )
        assert "dj-copyable-text mono" in html

    def test_role_and_tabindex(self):
        html = render("{% copyable_text %}key{% endcopyable_text %}")
        assert 'role="button"' in html
        assert 'tabindex="0"' in html
        assert 'aria-label="Click to copy"' in html

    def test_nested_content_rendered(self):
        html = render(
            "{% copyable_text %}sk-abc123-xyz{% endcopyable_text %}"
        )
        assert "sk-abc123-xyz" in html

    def test_variable_copied_label(self):
        html = render(
            '{% copyable_text copied_label=lbl %}key{% endcopyable_text %}',
            {"lbl": "Saved!"},
        )
        assert 'data-copied-label="Saved!"' in html


# ═══════════════════════════════════════════════════════════════════════════
# XSS ESCAPING
# ═══════════════════════════════════════════════════════════════════════════

class TestXSSEscaping:
    """Verify user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # ── Scroll to Top ──

    def test_scroll_to_top_threshold_xss(self):
        html = render('{% scroll_to_top threshold=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_scroll_to_top_label_xss(self):
        html = render('{% scroll_to_top label=xss %}', {"xss": self.XSS})
        self._assert_no_script(html)

    def test_scroll_to_top_label_attr_xss(self):
        html = render('{% scroll_to_top label=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_scroll_to_top_custom_class_xss(self):
        html = render('{% scroll_to_top custom_class=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    # ── Code Snippet ──

    def test_code_snippet_code_xss(self):
        html = render('{% code_snippet code=xss %}', {"xss": self.XSS})
        self._assert_no_script(html)

    def test_code_snippet_language_xss(self):
        html = render('{% code_snippet language=xss code="x" %}', {"xss": self.XSS})
        self._assert_no_script(html)

    def test_code_snippet_language_attr_xss(self):
        html = render('{% code_snippet language=xss code="x" %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_code_snippet_custom_class_xss(self):
        html = render('{% code_snippet code="x" custom_class=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    # ── Responsive Image ──

    def test_responsive_image_src_xss(self):
        html = render('{% responsive_image src=xss alt="" %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_responsive_image_alt_xss(self):
        html = render('{% responsive_image src="/x.jpg" alt=xss %}', {"xss": self.XSS})
        self._assert_no_script(html)

    def test_responsive_image_alt_attr_xss(self):
        html = render('{% responsive_image src="/x.jpg" alt=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_responsive_image_aspect_ratio_xss(self):
        html = render(
            '{% responsive_image src="/x.jpg" alt="" aspect_ratio=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_responsive_image_srcset_xss(self):
        html = render(
            '{% responsive_image src="/x.jpg" alt="" srcset=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_responsive_image_placeholder_xss(self):
        html = render(
            '{% responsive_image src="/x.jpg" alt="" placeholder=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_responsive_image_custom_class_xss(self):
        html = render(
            '{% responsive_image src="/x.jpg" alt="" custom_class=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # ── Relative Time ──

    def test_relative_time_datetime_xss(self):
        html = render('{% relative_time datetime=xss %}', {"xss": self.XSS})
        self._assert_no_script(html)

    def test_relative_time_datetime_attr_xss(self):
        html = render('{% relative_time datetime=xss %}', {"xss": self.XSS_ATTR})
        self._assert_attr_escaped(html)

    def test_relative_time_custom_class_xss(self):
        html = render(
            '{% relative_time datetime="2026-01-01" custom_class=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # ── Copyable Text ──

    def test_copyable_text_content_xss(self):
        html = render(
            '{% copyable_text %}' + self.XSS + '{% endcopyable_text %}'
        )
        self._assert_no_script(html)

    def test_copyable_text_copied_label_xss(self):
        html = render(
            '{% copyable_text copied_label=xss %}key{% endcopyable_text %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_copyable_text_copied_label_attr_xss(self):
        html = render(
            '{% copyable_text copied_label=xss %}key{% endcopyable_text %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_copyable_text_custom_class_xss(self):
        html = render(
            '{% copyable_text custom_class=xss %}key{% endcopyable_text %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)


# ═══════════════════════════════════════════════════════════════════════════
# Rust Handler Tests
# ═══════════════════════════════════════════════════════════════════════════

class TestRustHandlers:
    """Test Rust template engine handlers render correctly."""

    def _get_handler(self, name):
        from djust_components.rust_handlers import INLINE_HANDLERS, BLOCK_HANDLERS
        for tag_name, handler in INLINE_HANDLERS:
            if tag_name == name:
                return handler
        for entry in BLOCK_HANDLERS:
            if entry[0] == name:
                return entry[2]
        raise KeyError(f"Handler {name!r} not found")

    def test_scroll_to_top_handler(self):
        h = self._get_handler("scroll_to_top")
        result = h.render(["threshold='500px'", "label='Up'"], {})
        assert "dj-scroll-to-top" in result
        assert 'data-threshold="500px"' in result
        assert 'aria-label="Up"' in result

    def test_code_snippet_handler(self):
        h = self._get_handler("code_snippet")
        result = h.render(["code='echo hi'", "language='bash'"], {})
        assert "dj-code-snippet" in result
        assert "echo hi" in result
        assert "bash" in result

    def test_responsive_image_handler(self):
        h = self._get_handler("responsive_image")
        result = h.render(["src='/img.jpg'", "alt='photo'", "aspect_ratio='16/9'"], {})
        assert "dj-responsive-image" in result
        assert 'src="/img.jpg"' in result
        assert "aspect-ratio:16/9" in result

    def test_responsive_image_handler_lazy_false(self):
        h = self._get_handler("responsive_image")
        result = h.render(["src='/img.jpg'", "alt=''", "lazy=False"], {})
        assert 'loading="lazy"' not in result

    def test_relative_time_handler(self):
        h = self._get_handler("relative_time")
        result = h.render(["datetime='2026-01-01T00:00:00'", "auto_update=False"], {})
        assert "dj-relative-time" in result
        assert 'datetime="2026-01-01T00:00:00"' in result
        assert 'data-auto-update="false"' in result

    def test_copyable_text_handler(self):
        h = self._get_handler("copyable_text")
        result = h.render(["copied_label='Done!'"], "my-api-key", {})
        assert "dj-copyable-text" in result
        assert 'data-copy-text="my-api-key"' in result
        assert 'data-copied-label="Done!"' in result

    # XSS for Rust handlers

    def test_scroll_to_top_handler_xss(self):
        h = self._get_handler("scroll_to_top")
        result = h.render(["label='<script>alert(1)</script>'"], {})
        assert "<script>" not in result

    def test_code_snippet_handler_xss(self):
        h = self._get_handler("code_snippet")
        result = h.render(["code='<script>alert(1)</script>'"], {})
        assert "<script>" not in result

    def test_responsive_image_handler_xss(self):
        h = self._get_handler("responsive_image")
        result = h.render(["src='\" onload=\"alert(1)\"'", "alt=''"], {})
        assert '" onload="' not in result

    def test_relative_time_handler_xss(self):
        h = self._get_handler("relative_time")
        result = h.render(["datetime='<script>alert(1)</script>'"], {})
        assert "<script>" not in result

    def test_copyable_text_handler_xss(self):
        h = self._get_handler("copyable_text")
        result = h.render([], '<script>alert(1)</script>', {})
        assert "<script>" not in result


# ═══════════════════════════════════════════════════════════════════════════
# Component Class Tests
# ═══════════════════════════════════════════════════════════════════════════

import types
import sys

# Stub djust for component class imports
_stub = types.ModuleType("djust")


class _Component:
    def __init__(self, **kwargs):
        pass

    def __str__(self):
        return self._render_custom()

    def __html__(self):
        return self._render_custom()


_stub.Component = _Component
sys.modules.setdefault("djust", _stub)


class TestScrollToTopComponent:
    def test_render(self):
        from djust_components.components.scroll_to_top import ScrollToTop
        c = ScrollToTop(threshold="500px", label="Up")
        html = str(c)
        assert "dj-scroll-to-top" in html
        assert 'data-threshold="500px"' in html

    def test_xss(self):
        from djust_components.components.scroll_to_top import ScrollToTop
        c = ScrollToTop(label='<script>alert(1)</script>')
        html = str(c)
        assert "<script>" not in html


class TestCodeSnippetComponent:
    def test_render(self):
        from djust_components.components.code_snippet import CodeSnippet
        c = CodeSnippet(code="echo hi", language="bash")
        html = str(c)
        assert "dj-code-snippet" in html
        assert "echo hi" in html
        assert "bash" in html

    def test_xss(self):
        from djust_components.components.code_snippet import CodeSnippet
        c = CodeSnippet(code='<script>alert(1)</script>')
        html = str(c)
        assert "<script>" not in html


class TestResponsiveImageComponent:
    def test_render(self):
        from djust_components.components.responsive_image import ResponsiveImage
        c = ResponsiveImage(src="/img.jpg", alt="test", aspect_ratio="16/9")
        html = str(c)
        assert "dj-responsive-image" in html
        assert 'src="/img.jpg"' in html
        assert "aspect-ratio:16/9" in html

    def test_lazy_default(self):
        from djust_components.components.responsive_image import ResponsiveImage
        c = ResponsiveImage(src="/img.jpg", alt="")
        html = str(c)
        assert 'loading="lazy"' in html

    def test_xss(self):
        from djust_components.components.responsive_image import ResponsiveImage
        c = ResponsiveImage(src='" onload="alert(1)"', alt="")
        html = str(c)
        assert '" onload="' not in html


class TestRelativeTimeComponent:
    def test_render(self):
        from djust_components.components.relative_time import RelativeTime
        c = RelativeTime(datetime="2026-01-01T00:00:00")
        html = str(c)
        assert "dj-relative-time" in html
        assert 'datetime="2026-01-01T00:00:00"' in html

    def test_datetime_object(self):
        from datetime import datetime as dt
        from djust_components.components.relative_time import RelativeTime
        c = RelativeTime(datetime=dt(2026, 3, 1, 12, 0))
        html = str(c)
        assert "2026-03-01T12:00:00" in html

    def test_xss(self):
        from djust_components.components.relative_time import RelativeTime
        c = RelativeTime(datetime='<script>alert(1)</script>')
        html = str(c)
        assert "<script>" not in html


class TestCopyableTextComponent:
    def test_render(self):
        from djust_components.components.copyable_text import CopyableText
        c = CopyableText(text="my-key")
        html = str(c)
        assert "dj-copyable-text" in html
        assert 'data-copy-text="my-key"' in html

    def test_xss(self):
        from djust_components.components.copyable_text import CopyableText
        c = CopyableText(text='<script>alert(1)</script>')
        html = str(c)
        assert "<script>" not in html
