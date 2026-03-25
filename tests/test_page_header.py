"""Tests for Page Header component (#179)."""
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


# --- Page Header ---

class TestPageHeader:
    def test_basic_title(self):
        html = render('{% page_header title="Products" %}{% endpage_header %}')
        assert "dj-page-header" in html
        assert '<h1 class="dj-page-header__title">Products</h1>' in html
        assert "<header" in html

    def test_title_from_variable(self):
        html = render(
            '{% page_header title=page_title %}{% endpage_header %}',
            {"page_title": "Orders"},
        )
        assert "Orders" in html
        assert "dj-page-header__title" in html

    def test_subtitle(self):
        html = render(
            '{% page_header title="Products" subtitle="Manage inventory" %}{% endpage_header %}'
        )
        assert "dj-page-header__subtitle" in html
        assert "Manage inventory" in html

    def test_description(self):
        html = render(
            '{% page_header title="Products" description="View and manage all products" %}{% endpage_header %}'
        )
        assert "dj-page-header__description" in html
        assert "View and manage all products" in html

    def test_subtitle_and_description(self):
        html = render(
            '{% page_header title="T" subtitle="S" description="D" %}{% endpage_header %}'
        )
        assert "dj-page-header__subtitle" in html
        assert "dj-page-header__description" in html

    def test_no_subtitle_no_subtitle_element(self):
        html = render('{% page_header title="T" %}{% endpage_header %}')
        assert "dj-page-header__subtitle" not in html

    def test_no_description_no_description_element(self):
        html = render('{% page_header title="T" %}{% endpage_header %}')
        assert "dj-page-header__description" not in html

    def test_no_title_no_h1(self):
        html = render('{% page_header %}{% endpage_header %}')
        assert "<h1" not in html

    def test_custom_class(self):
        html = render(
            '{% page_header title="T" custom_class="my-header" %}{% endpage_header %}'
        )
        assert "my-header" in html
        assert "dj-page-header my-header" in html

    def test_row_wrapper(self):
        html = render('{% page_header title="T" %}{% endpage_header %}')
        assert "dj-page-header__row" in html
        assert "dj-page-header__text" in html


# --- Page Header Actions ---

class TestPageHeaderActions:
    def test_actions_rendered(self):
        html = render(
            '{% page_header title="Products" %}'
            '{% page_header_actions %}'
            '<button>Add</button>'
            '{% endpage_header_actions %}'
            '{% endpage_header %}'
        )
        assert "dj-page-header__actions" in html
        assert "<button>Add</button>" in html

    def test_no_actions_no_actions_div(self):
        html = render('{% page_header title="T" %}{% endpage_header %}')
        assert "dj-page-header__actions" not in html

    def test_multiple_action_buttons(self):
        html = render(
            '{% page_header title="T" %}'
            '{% page_header_actions %}'
            '<button>Add</button><button>Export</button>'
            '{% endpage_header_actions %}'
            '{% endpage_header %}'
        )
        assert "<button>Add</button>" in html
        assert "<button>Export</button>" in html
        assert "dj-page-header__actions" in html

    def test_actions_with_subtitle(self):
        html = render(
            '{% page_header title="Products" subtitle="Manage" %}'
            '{% page_header_actions %}<button>Add</button>{% endpage_header_actions %}'
            '{% endpage_header %}'
        )
        assert "dj-page-header__subtitle" in html
        assert "dj-page-header__actions" in html


# --- Breadcrumb Slot ---

class TestPageHeaderBreadcrumb:
    def test_breadcrumb_content(self):
        html = render(
            '{% page_header title="T" %}'
            '<nav>Home / Products</nav>'
            '{% endpage_header %}'
        )
        assert "dj-page-header__breadcrumb" in html
        assert "Home / Products" in html

    def test_no_breadcrumb_no_breadcrumb_div(self):
        html = render('{% page_header title="T" %}{% endpage_header %}')
        assert "dj-page-header__breadcrumb" not in html

    def test_breadcrumb_with_actions(self):
        html = render(
            '{% page_header title="T" %}'
            '<nav>Home / T</nav>'
            '{% page_header_actions %}<button>Add</button>{% endpage_header_actions %}'
            '{% endpage_header %}'
        )
        assert "dj-page-header__breadcrumb" in html
        assert "Home / T" in html
        assert "dj-page-header__actions" in html
        assert "<button>Add</button>" in html


# --- XSS Escaping ---

class TestXSSEscaping:
    """Verify user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    def test_title_xss_script(self):
        html = render(
            '{% page_header title=xss %}{% endpage_header %}',
            {"xss": self.XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_title_xss_attr(self):
        html = render(
            '{% page_header title=xss %}{% endpage_header %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_subtitle_xss_script(self):
        html = render(
            '{% page_header title="T" subtitle=xss %}{% endpage_header %}',
            {"xss": self.XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_subtitle_xss_attr(self):
        html = render(
            '{% page_header title="T" subtitle=xss %}{% endpage_header %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_description_xss_script(self):
        html = render(
            '{% page_header title="T" description=xss %}{% endpage_header %}',
            {"xss": self.XSS},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_description_xss_attr(self):
        html = render(
            '{% page_header title="T" description=xss %}{% endpage_header %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_custom_class_xss(self):
        html = render(
            '{% page_header title="T" custom_class=xss %}{% endpage_header %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)


# --- Rust Handlers ---

class TestRustHandlers:
    """Test the Rust engine handler classes directly."""

    def test_page_header_basic(self):
        from djust_components.rust_handlers import PageHeaderHandler
        handler = PageHeaderHandler()
        html = handler.render(
            ["title='Products'", "subtitle='Manage inventory'"],
            "",
            {},
        )
        assert "dj-page-header" in html
        assert "Products" in html
        assert "Manage inventory" in html
        assert "dj-page-header__subtitle" in html
        assert "<header" in html

    def test_page_header_description(self):
        from djust_components.rust_handlers import PageHeaderHandler
        handler = PageHeaderHandler()
        html = handler.render(
            ["title='T'", "description='A longer description'"],
            "",
            {},
        )
        assert "dj-page-header__description" in html
        assert "A longer description" in html

    def test_page_header_custom_class(self):
        from djust_components.rust_handlers import PageHeaderHandler
        handler = PageHeaderHandler()
        html = handler.render(
            ["title='T'", "custom_class='admin-header'"],
            "",
            {},
        )
        assert "admin-header" in html

    def test_page_header_with_actions(self):
        from djust_components.rust_handlers import PageHeaderHandler
        handler = PageHeaderHandler()
        html = handler.render(
            ["title='Products'"],
            '<div class="dj-page-header__actions"><button>Add</button></div>',
            {},
        )
        assert "dj-page-header__actions" in html
        assert "<button>Add</button>" in html

    def test_page_header_with_breadcrumb(self):
        from djust_components.rust_handlers import PageHeaderHandler
        handler = PageHeaderHandler()
        html = handler.render(
            ["title='T'"],
            "<nav>Home / T</nav>",
            {},
        )
        assert "dj-page-header__breadcrumb" in html
        assert "Home / T" in html

    def test_page_header_with_breadcrumb_and_actions(self):
        from djust_components.rust_handlers import PageHeaderHandler
        handler = PageHeaderHandler()
        html = handler.render(
            ["title='T'"],
            '<nav>Home / T</nav><div class="dj-page-header__actions"><button>Add</button></div>',
            {},
        )
        assert "dj-page-header__breadcrumb" in html
        assert "Home / T" in html
        assert "dj-page-header__actions" in html

    def test_page_header_no_title(self):
        from djust_components.rust_handlers import PageHeaderHandler
        handler = PageHeaderHandler()
        html = handler.render([], "", {})
        assert "<h1" not in html
        assert "dj-page-header" in html

    def test_page_header_actions_handler(self):
        from djust_components.rust_handlers import PageHeaderActionsHandler
        handler = PageHeaderActionsHandler()
        html = handler.render([], "<button>Add</button>", {})
        assert "dj-page-header__actions" in html
        assert "<button>Add</button>" in html

    def test_page_header_title_xss(self):
        from djust_components.rust_handlers import PageHeaderHandler
        handler = PageHeaderHandler()
        html = handler.render(
            ["title='<script>alert(1)</script>'"],
            "",
            {},
        )
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_page_header_subtitle_xss(self):
        from djust_components.rust_handlers import PageHeaderHandler
        handler = PageHeaderHandler()
        html = handler.render(
            ["title='T'", """subtitle='" onmouseover="alert(1)" x="'"""],
            "",
            {},
        )
        assert '" onmouseover="' not in html

    def test_page_header_custom_class_xss(self):
        from djust_components.rust_handlers import PageHeaderHandler
        handler = PageHeaderHandler()
        html = handler.render(
            ["title='T'", """custom_class='" onmouseover="alert(1)" x="'"""],
            "",
            {},
        )
        assert '" onmouseover="' not in html
