"""Tests for Loading Overlay and Announcement Bar components."""
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


# ─── Loading Overlay ───

class TestLoadingOverlay:
    def test_inactive_renders_content_only(self):
        html = render(
            '{% loading_overlay active=False %}<p>Content</p>{% endloading_overlay %}'
        )
        assert "<p>Content</p>" in html
        assert "dj-loading-overlay-wrap" in html
        assert "dj-loading-overlay__spinner" not in html

    def test_active_renders_overlay(self):
        html = render(
            '{% loading_overlay active=is_loading %}<p>Content</p>{% endloading_overlay %}',
            {"is_loading": True},
        )
        assert "dj-loading-overlay-wrap" in html
        assert "dj-loading-overlay__spinner" in html
        assert "<p>Content</p>" in html

    def test_active_false_no_overlay(self):
        html = render(
            '{% loading_overlay active=is_loading %}<p>Content</p>{% endloading_overlay %}',
            {"is_loading": False},
        )
        assert "dj-loading-overlay__spinner" not in html

    def test_text_shown_when_active(self):
        html = render(
            '{% loading_overlay active=is_loading text="Loading..." %}'
            '<p>Body</p>'
            '{% endloading_overlay %}',
            {"is_loading": True},
        )
        assert "Loading..." in html
        assert "dj-loading-overlay__text" in html

    def test_text_hidden_when_inactive(self):
        html = render(
            '{% loading_overlay active=False text="Loading..." %}'
            '<p>Body</p>'
            '{% endloading_overlay %}'
        )
        assert "dj-loading-overlay__text" not in html

    def test_spinner_size_sm(self):
        html = render(
            '{% loading_overlay active=True spinner_size="sm" %}x{% endloading_overlay %}'
        )
        assert "dj-loading-overlay__spinner--sm" in html

    def test_spinner_size_lg(self):
        html = render(
            '{% loading_overlay active=True spinner_size="lg" %}x{% endloading_overlay %}'
        )
        assert "dj-loading-overlay__spinner--lg" in html

    def test_default_spinner_size_md(self):
        html = render(
            '{% loading_overlay active=True %}x{% endloading_overlay %}'
        )
        assert "dj-loading-overlay__spinner--md" in html

    def test_custom_class(self):
        html = render(
            '{% loading_overlay active=True custom_class="my-overlay" %}x{% endloading_overlay %}'
        )
        assert "my-overlay" in html

    def test_wraps_content_in_relative_container(self):
        html = render(
            '{% loading_overlay active=False %}<div>inner</div>{% endloading_overlay %}'
        )
        assert "dj-loading-overlay-wrap" in html


# ─── Announcement Bar ───

class TestAnnouncementBar:
    def test_basic_render(self):
        html = render(
            '{% announcement_bar %}Important notice{% endannouncement_bar %}'
        )
        assert "dj-announcement-bar" in html
        assert "dj-announcement-bar--info" in html
        assert "Important notice" in html
        assert 'role="banner"' in html

    def test_type_success(self):
        html = render(
            '{% announcement_bar type="success" %}Done!{% endannouncement_bar %}'
        )
        assert "dj-announcement-bar--success" in html

    def test_type_warning(self):
        html = render(
            '{% announcement_bar type="warning" %}Heads up{% endannouncement_bar %}'
        )
        assert "dj-announcement-bar--warning" in html

    def test_type_danger(self):
        html = render(
            '{% announcement_bar type="danger" %}Critical{% endannouncement_bar %}'
        )
        assert "dj-announcement-bar--danger" in html

    def test_type_from_variable(self):
        html = render(
            '{% announcement_bar type=bar_type %}msg{% endannouncement_bar %}',
            {"bar_type": "success"},
        )
        assert "dj-announcement-bar--success" in html

    def test_not_dismissible_by_default(self):
        html = render(
            '{% announcement_bar %}msg{% endannouncement_bar %}'
        )
        assert "dj-announcement-bar__close" not in html

    def test_dismissible(self):
        html = render(
            '{% announcement_bar dismissible=True %}msg{% endannouncement_bar %}'
        )
        assert "dj-announcement-bar__close" in html
        assert 'dj-click="dismiss_announcement"' in html

    def test_custom_dismiss_event(self):
        html = render(
            '{% announcement_bar dismissible=True dismiss_event="hide_bar" %}msg{% endannouncement_bar %}'
        )
        assert 'dj-click="hide_bar"' in html

    def test_custom_class(self):
        html = render(
            '{% announcement_bar custom_class="promo-bar" %}msg{% endannouncement_bar %}'
        )
        assert "promo-bar" in html

    def test_content_rendered(self):
        html = render(
            '{% announcement_bar %}<strong>New</strong> feature{% endannouncement_bar %}'
        )
        assert "<strong>New</strong> feature" in html
        assert "dj-announcement-bar__content" in html


# ─── XSS Escaping ───

class TestXSSEscaping:
    """Verify user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # Loading Overlay
    def test_loading_overlay_text_xss(self):
        html = render(
            '{% loading_overlay active=True text=xss %}x{% endloading_overlay %}',
            {"xss": self.XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_loading_overlay_spinner_size_xss(self):
        html = render(
            '{% loading_overlay active=True spinner_size=xss %}x{% endloading_overlay %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_loading_overlay_custom_class_xss(self):
        html = render(
            '{% loading_overlay active=True custom_class=xss %}x{% endloading_overlay %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Announcement Bar
    def test_announcement_bar_type_xss(self):
        html = render(
            '{% announcement_bar type=xss %}msg{% endannouncement_bar %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_announcement_bar_dismiss_event_xss(self):
        html = render(
            '{% announcement_bar dismissible=True dismiss_event=xss %}msg{% endannouncement_bar %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_announcement_bar_custom_class_xss(self):
        html = render(
            '{% announcement_bar custom_class=xss %}msg{% endannouncement_bar %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)


# ─── Rust Handlers ───

class TestRustHandlers:
    """Test the Rust engine handler classes directly."""

    def test_loading_overlay_handler_active(self):
        from djust_components.rust_handlers import LoadingOverlayHandler
        handler = LoadingOverlayHandler()
        html = handler.render(
            ["active='True'", "text='Please wait'", "spinner_size='lg'"],
            "<p>Inner</p>",
            {},
        )
        assert "dj-loading-overlay__spinner--lg" in html
        assert "Please wait" in html
        assert "<p>Inner</p>" in html

    def test_loading_overlay_handler_inactive(self):
        from djust_components.rust_handlers import LoadingOverlayHandler
        handler = LoadingOverlayHandler()
        html = handler.render(
            ["active=False"],
            "<p>Inner</p>",
            {},
        )
        assert "dj-loading-overlay__spinner" not in html
        assert "<p>Inner</p>" in html

    def test_announcement_bar_handler_basic(self):
        from djust_components.rust_handlers import AnnouncementBarHandler
        handler = AnnouncementBarHandler()
        html = handler.render(
            ["type='warning'", "dismissible='True'", "dismiss_event='close_bar'"],
            "Maintenance tonight",
            {},
        )
        assert "dj-announcement-bar--warning" in html
        assert "Maintenance tonight" in html
        assert 'dj-click="close_bar"' in html
        assert 'role="banner"' in html

    def test_announcement_bar_handler_not_dismissible(self):
        from djust_components.rust_handlers import AnnouncementBarHandler
        handler = AnnouncementBarHandler()
        html = handler.render(
            ["type='info'"],
            "Hello",
            {},
        )
        assert "dj-announcement-bar__close" not in html

    def test_loading_overlay_handler_xss(self):
        from djust_components.rust_handlers import LoadingOverlayHandler
        handler = LoadingOverlayHandler()
        html = handler.render(
            ['active=\'True\'', 'text=\'<script>alert(1)</script>\''],
            "content",
            {},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_announcement_bar_handler_xss(self):
        from djust_components.rust_handlers import AnnouncementBarHandler
        handler = AnnouncementBarHandler()
        html = handler.render(
            ['type=\'" onmouseover="alert(1)" x="\'', 'dismissible=\'True\'',
             'dismiss_event=\'" onclick="alert(2)" y="\''],
            "msg",
            {},
        )
        assert '" onmouseover="' not in html
        assert '" onclick="' not in html
        assert "&quot;" in html
