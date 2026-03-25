"""Tests for app chrome components: Sidebar Nav, Navigation Menu, App Shell."""
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


# ===========================================================================
# Sidebar Nav (#86)
# ===========================================================================

class TestSidebar:
    def test_basic_sidebar_renders(self):
        html = render(
            '{% sidebar id="side" title="App" %}'
            '{% sidebar_item id="home" label="Home" href="/" %}{% endsidebar_item %}'
            '{% endsidebar %}'
        )
        assert 'class="dj-sidebar"' in html
        assert 'id="side"' in html
        assert 'role="navigation"' in html
        assert "Home" in html
        assert 'href="/"' in html

    def test_sidebar_title(self):
        html = render(
            '{% sidebar title="My App" %}'
            '{% endsidebar %}'
        )
        assert "dj-sidebar__title" in html
        assert "My App" in html

    def test_sidebar_collapsed(self):
        html = render(
            '{% sidebar collapsed=is_collapsed %}'
            '{% endsidebar %}',
            {"is_collapsed": True},
        )
        assert "dj-sidebar--collapsed" in html

    def test_sidebar_not_collapsed(self):
        html = render(
            '{% sidebar collapsed=is_collapsed %}'
            '{% endsidebar %}',
            {"is_collapsed": False},
        )
        assert "dj-sidebar--collapsed" not in html

    def test_sidebar_active_item(self):
        html = render(
            '{% sidebar active=active_item %}'
            '{% sidebar_item id="home" label="Home" href="/" %}{% endsidebar_item %}'
            '{% sidebar_item id="settings" label="Settings" href="/settings" %}{% endsidebar_item %}'
            '{% endsidebar %}',
            {"active_item": "settings"},
        )
        assert "dj-sidebar__item--active" in html

    def test_sidebar_section_headers(self):
        html = render(
            '{% sidebar %}'
            '{% sidebar_section label="Main" %}'
            '{% sidebar_item id="home" label="Home" %}{% endsidebar_item %}'
            '{% sidebar_section label="Admin" %}'
            '{% sidebar_item id="users" label="Users" %}{% endsidebar_item %}'
            '{% endsidebar %}'
        )
        assert "dj-sidebar__section" in html
        assert "Main" in html
        assert "Admin" in html

    def test_sidebar_item_with_icon(self):
        html = render(
            '{% sidebar %}'
            '{% sidebar_item id="home" label="Home" icon="H" %}{% endsidebar_item %}'
            '{% endsidebar %}'
        )
        assert "dj-sidebar__icon" in html

    def test_sidebar_item_with_event(self):
        html = render(
            '{% sidebar %}'
            '{% sidebar_item id="logout" label="Logout" event="do_logout" %}{% endsidebar_item %}'
            '{% endsidebar %}'
        )
        assert 'dj-click="do_logout"' in html
        assert "<button" in html

    def test_sidebar_nested_items(self):
        html = render(
            '{% sidebar %}'
            '{% sidebar_item id="parent" label="Parent" %}'
            '{% sidebar_item id="child" label="Child" href="/child" %}{% endsidebar_item %}'
            '{% endsidebar_item %}'
            '{% endsidebar %}'
        )
        assert "dj-sidebar__item--parent" in html
        assert "dj-sidebar__submenu" in html
        assert "Child" in html

    def test_sidebar_toggle_event(self):
        html = render(
            '{% sidebar title="App" toggle_event="my_toggle" %}'
            '{% endsidebar %}'
        )
        assert 'dj-click="my_toggle"' in html

    def test_sidebar_default_toggle_event(self):
        html = render(
            '{% sidebar title="App" %}'
            '{% endsidebar %}'
        )
        assert 'dj-click="toggle_sidebar"' in html

    def test_sidebar_backdrop(self):
        html = render('{% sidebar %}{% endsidebar %}')
        assert "dj-sidebar__backdrop" in html

    def test_sidebar_custom_class(self):
        html = render('{% sidebar class="my-class" %}{% endsidebar %}')
        assert "my-class" in html

    def test_sidebar_active_by_href(self):
        html = render(
            '{% sidebar active=active_path %}'
            '{% sidebar_item id="home" label="Home" href="/dashboard" %}{% endsidebar_item %}'
            '{% endsidebar %}',
            {"active_path": "/dashboard"},
        )
        assert "dj-sidebar__item--active" in html


# ===========================================================================
# Navigation Menu (#90)
# ===========================================================================

class TestNavMenu:
    def test_basic_nav_renders(self):
        html = render(
            '{% nav_menu id="main-nav" brand="MyApp" %}'
            '{% nav_item id="home" label="Home" href="/" %}{% endnav_item %}'
            '{% endnav_menu %}'
        )
        assert 'class="dj-nav"' in html
        assert 'id="main-nav"' in html
        assert 'role="navigation"' in html
        assert "MyApp" in html
        assert "Home" in html

    def test_nav_brand(self):
        html = render(
            '{% nav_menu brand="BrandName" brand_href="/home" %}'
            '{% endnav_menu %}'
        )
        assert "dj-nav__brand" in html
        assert "BrandName" in html
        assert 'href="/home"' in html

    def test_nav_default_brand_href(self):
        html = render(
            '{% nav_menu brand="Logo" %}'
            '{% endnav_menu %}'
        )
        assert 'href="/"' in html

    def test_nav_hamburger(self):
        html = render(
            '{% nav_menu %}'
            '{% endnav_menu %}'
        )
        assert "dj-nav__hamburger" in html
        assert 'aria-label="Toggle navigation"' in html

    def test_nav_custom_toggle_event(self):
        html = render(
            '{% nav_menu toggle_event="my_toggle" %}'
            '{% endnav_menu %}'
        )
        assert 'dj-click="my_toggle"' in html

    def test_nav_default_toggle_event(self):
        html = render(
            '{% nav_menu %}'
            '{% endnav_menu %}'
        )
        assert 'dj-click="toggle_nav"' in html

    def test_nav_mobile_open(self):
        html = render(
            '{% nav_menu mobile_open=is_open %}'
            '{% nav_item id="a" label="A" %}{% endnav_item %}'
            '{% endnav_menu %}',
            {"is_open": True},
        )
        assert "dj-nav__list--open" in html

    def test_nav_mobile_closed(self):
        html = render(
            '{% nav_menu mobile_open=is_open %}'
            '{% nav_item id="a" label="A" %}{% endnav_item %}'
            '{% endnav_menu %}',
            {"is_open": False},
        )
        assert "dj-nav__list--open" not in html

    def test_nav_active_item(self):
        html = render(
            '{% nav_menu active=active_route %}'
            '{% nav_item id="home" label="Home" %}{% endnav_item %}'
            '{% nav_item id="about" label="About" %}{% endnav_item %}'
            '{% endnav_menu %}',
            {"active_route": "about"},
        )
        assert "dj-nav__item--active" in html

    def test_nav_item_with_event(self):
        html = render(
            '{% nav_menu %}'
            '{% nav_item label="Logout" event="do_logout" %}{% endnav_item %}'
            '{% endnav_menu %}'
        )
        assert 'dj-click="do_logout"' in html
        assert "<button" in html

    def test_nav_item_with_href(self):
        html = render(
            '{% nav_menu %}'
            '{% nav_item label="Docs" href="/docs" %}{% endnav_item %}'
            '{% endnav_menu %}'
        )
        assert 'href="/docs"' in html
        assert "<a " in html

    def test_nav_dropdown(self):
        html = render(
            '{% nav_menu %}'
            '{% nav_item label="Products" %}'
            '{% nav_item label="Widget" href="/widget" %}{% endnav_item %}'
            '{% nav_item label="Gadget" href="/gadget" %}{% endnav_item %}'
            '{% endnav_item %}'
            '{% endnav_menu %}'
        )
        assert "dj-nav__item--has-dropdown" in html
        assert "dj-nav__dropdown" in html
        assert "dj-nav__caret" in html
        assert "Widget" in html
        assert "Gadget" in html

    def test_nav_mega_menu(self):
        html = render(
            '{% nav_menu %}'
            '{% nav_item label="Solutions" mega=True %}'
            '{% nav_item label="Cloud" href="/cloud" %}{% endnav_item %}'
            '{% endnav_item %}'
            '{% endnav_menu %}'
        )
        assert "dj-nav__dropdown--mega" in html

    def test_nav_dropdown_description(self):
        html = render(
            '{% nav_menu %}'
            '{% nav_item label="Parent" %}'
            '{% nav_item label="Sub" href="/sub" description="A sub item" %}{% endnav_item %}'
            '{% endnav_item %}'
            '{% endnav_menu %}'
        )
        assert "dj-nav__dropdown-desc" in html
        assert "A sub item" in html

    def test_nav_custom_class(self):
        html = render('{% nav_menu class="dark-nav" %}{% endnav_menu %}')
        assert "dark-nav" in html

    def test_nav_no_brand(self):
        html = render('{% nav_menu %}{% endnav_menu %}')
        assert "dj-nav__brand" not in html


# ===========================================================================
# App Shell (#167)
# ===========================================================================

class TestAppShell:
    def test_basic_shell_renders(self):
        html = render(
            '{% app_shell id="shell" %}'
            '{% app_sidebar %}Sidebar{% endapp_sidebar %}'
            '{% app_header %}Header{% endapp_header %}'
            '{% app_content %}Content{% endapp_content %}'
            '{% endapp_shell %}'
        )
        assert 'class="dj-app-shell"' in html
        assert 'id="shell"' in html
        assert "dj-app-shell__sidebar" in html
        assert "dj-app-shell__header" in html
        assert "dj-app-shell__content" in html
        assert "Sidebar" in html
        assert "Header" in html
        assert "Content" in html

    def test_shell_sidebar_collapsed(self):
        html = render(
            '{% app_shell sidebar_collapsed=collapsed %}'
            '{% app_sidebar %}S{% endapp_sidebar %}'
            '{% app_content %}C{% endapp_content %}'
            '{% endapp_shell %}',
            {"collapsed": True},
        )
        assert "dj-app-shell--sidebar-collapsed" in html

    def test_shell_sidebar_not_collapsed(self):
        html = render(
            '{% app_shell sidebar_collapsed=collapsed %}'
            '{% app_sidebar %}S{% endapp_sidebar %}'
            '{% app_content %}C{% endapp_content %}'
            '{% endapp_shell %}',
            {"collapsed": False},
        )
        assert "dj-app-shell--sidebar-collapsed" not in html

    def test_shell_custom_class(self):
        html = render(
            '{% app_shell class="my-shell" %}'
            '{% app_content %}C{% endapp_content %}'
            '{% endapp_shell %}'
        )
        assert "my-shell" in html

    def test_shell_without_sidebar(self):
        html = render(
            '{% app_shell %}'
            '{% app_header %}H{% endapp_header %}'
            '{% app_content %}C{% endapp_content %}'
            '{% endapp_shell %}'
        )
        assert "dj-app-shell__sidebar" not in html
        assert "dj-app-shell__header" in html
        assert "dj-app-shell__content" in html

    def test_shell_without_header(self):
        html = render(
            '{% app_shell %}'
            '{% app_sidebar %}S{% endapp_sidebar %}'
            '{% app_content %}C{% endapp_content %}'
            '{% endapp_shell %}'
        )
        assert "dj-app-shell__header" not in html
        assert "dj-app-shell__sidebar" in html

    def test_shell_content_only(self):
        html = render(
            '{% app_shell %}'
            '{% app_content %}Just content{% endapp_content %}'
            '{% endapp_shell %}'
        )
        assert "Just content" in html
        assert "dj-app-shell__content" in html

    def test_shell_sidebar_renders_content(self):
        html = render(
            '{% app_shell %}'
            '{% app_sidebar %}<ul><li>Nav</li></ul>{% endapp_sidebar %}'
            '{% app_content %}Main{% endapp_content %}'
            '{% endapp_shell %}'
        )
        assert "<ul><li>Nav</li></ul>" in html

    def test_shell_semantic_elements(self):
        html = render(
            '{% app_shell %}'
            '{% app_sidebar %}S{% endapp_sidebar %}'
            '{% app_header %}H{% endapp_header %}'
            '{% app_content %}C{% endapp_content %}'
            '{% endapp_shell %}'
        )
        assert "<aside " in html
        assert "<header " in html
        assert "<main " in html

    def test_shell_layout_structure(self):
        """Verify shell has main wrapper div for flex layout."""
        html = render(
            '{% app_shell %}'
            '{% app_header %}H{% endapp_header %}'
            '{% app_content %}C{% endapp_content %}'
            '{% endapp_shell %}'
        )
        assert "dj-app-shell__main" in html


# ===========================================================================
# XSS Escaping
# ===========================================================================

class TestXSSEscaping:
    """Verify that user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # -- Sidebar --

    def test_sidebar_title_xss(self):
        html = render(
            '{% sidebar title=xss %}{% endsidebar %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_sidebar_toggle_event_xss(self):
        html = render(
            '{% sidebar title="T" toggle_event=bad %}{% endsidebar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_sidebar_id_xss(self):
        html = render(
            '{% sidebar id=bad %}{% endsidebar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_sidebar_item_label_xss(self):
        html = render(
            '{% sidebar %}'
            '{% sidebar_item id="x" label=xss %}{% endsidebar_item %}'
            '{% endsidebar %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_sidebar_item_href_xss(self):
        html = render(
            '{% sidebar %}'
            '{% sidebar_item id="x" label="X" href=bad %}{% endsidebar_item %}'
            '{% endsidebar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_sidebar_item_event_xss(self):
        html = render(
            '{% sidebar %}'
            '{% sidebar_item id="x" label="X" event=bad %}{% endsidebar_item %}'
            '{% endsidebar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_sidebar_item_icon_xss(self):
        html = render(
            '{% sidebar %}'
            '{% sidebar_item id="x" label="X" icon=xss %}{% endsidebar_item %}'
            '{% endsidebar %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_sidebar_section_label_xss(self):
        html = render(
            '{% sidebar %}'
            '{% sidebar_section label=xss %}'
            '{% endsidebar %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_sidebar_class_xss(self):
        html = render(
            '{% sidebar class=bad %}{% endsidebar %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # -- Nav Menu --

    def test_nav_brand_xss(self):
        html = render(
            '{% nav_menu brand=xss %}{% endnav_menu %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_nav_brand_href_xss(self):
        html = render(
            '{% nav_menu brand="B" brand_href=bad %}{% endnav_menu %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_nav_toggle_event_xss(self):
        html = render(
            '{% nav_menu toggle_event=bad %}{% endnav_menu %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_nav_id_xss(self):
        html = render(
            '{% nav_menu id=bad %}{% endnav_menu %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_nav_item_label_xss(self):
        html = render(
            '{% nav_menu %}'
            '{% nav_item label=xss %}{% endnav_item %}'
            '{% endnav_menu %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_nav_item_href_xss(self):
        html = render(
            '{% nav_menu %}'
            '{% nav_item label="X" href=bad %}{% endnav_item %}'
            '{% endnav_menu %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_nav_item_event_xss(self):
        html = render(
            '{% nav_menu %}'
            '{% nav_item label="X" event=bad %}{% endnav_item %}'
            '{% endnav_menu %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_nav_item_description_xss(self):
        html = render(
            '{% nav_menu %}'
            '{% nav_item label="Parent" %}'
            '{% nav_item label="X" href="/x" description=xss %}{% endnav_item %}'
            '{% endnav_item %}'
            '{% endnav_menu %}',
            {"xss": self.XSS},
        )
        self._assert_no_script(html)

    def test_nav_class_xss(self):
        html = render(
            '{% nav_menu class=bad %}{% endnav_menu %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # -- App Shell --

    def test_shell_id_xss(self):
        html = render(
            '{% app_shell id=bad %}'
            '{% app_content %}C{% endapp_content %}'
            '{% endapp_shell %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_shell_class_xss(self):
        html = render(
            '{% app_shell class=bad %}'
            '{% app_content %}C{% endapp_content %}'
            '{% endapp_shell %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)


# ===========================================================================
# Rust Handler Tests
# ===========================================================================

from djust_components.rust_handlers import (
    _parse_args,
    SidebarHandler,
    SidebarItemHandler,
    SidebarSectionHandler,
    NavMenuHandler,
    NavItemHandler,
    AppShellHandler,
    AppSidebarHandler,
    AppHeaderHandler,
    AppContentHandler,
)
from django.utils.safestring import SafeData


class TestSidebarHandler:
    def test_basic_render(self):
        handler = SidebarHandler()
        result = handler.render(
            ['id="side"', 'title="App"'],
            '<li>item</li>',
            {},
        )
        assert isinstance(result, SafeData)
        assert 'id="side"' in result
        assert "App" in result
        assert "dj-sidebar" in result
        assert "role=\"navigation\"" in result

    def test_collapsed(self):
        handler = SidebarHandler()
        result = handler.render(['collapsed=true'], '', {})
        assert "dj-sidebar--collapsed" in result

    def test_toggle_event(self):
        handler = SidebarHandler()
        result = handler.render(
            ['title="T"', 'toggle_event="my_toggle"'], '', {},
        )
        assert 'dj-click="my_toggle"' in result

    def test_xss_title(self):
        handler = SidebarHandler()
        result = handler.render(
            ['title=xss'], '', {"xss": '<script>alert(1)</script>'},
        )
        assert "<script>" not in result
        assert "&lt;script&gt;" in result


class TestSidebarItemHandler:
    def test_basic_link(self):
        handler = SidebarItemHandler()
        result = handler.render(
            ['label="Home"', 'href="/"'], '', {},
        )
        assert isinstance(result, SafeData)
        assert "Home" in result
        assert 'href="/"' in result
        assert "<a " in result

    def test_event_button(self):
        handler = SidebarItemHandler()
        result = handler.render(
            ['label="Logout"', 'event="do_logout"'], '', {},
        )
        assert "<button" in result
        assert 'dj-click="do_logout"' in result

    def test_with_children(self):
        handler = SidebarItemHandler()
        result = handler.render(
            ['label="Parent"'],
            '<li>child</li>',
            {},
        )
        assert "dj-sidebar__item--parent" in result
        assert "dj-sidebar__submenu" in result

    def test_xss_label(self):
        handler = SidebarItemHandler()
        result = handler.render(
            ['label=xss'], '', {"xss": '<script>alert(1)</script>'},
        )
        assert "<script>" not in result

    def test_xss_href(self):
        handler = SidebarItemHandler()
        result = handler.render(
            ['label="X"', 'href=bad'], '',
            {"bad": '" onmouseover="alert(1)" x="'},
        )
        assert '" onmouseover="' not in result
        assert "&quot;" in result


class TestSidebarSectionHandler:
    def test_basic(self):
        handler = SidebarSectionHandler()
        result = handler.render(['label="Main"'], {})
        assert isinstance(result, SafeData)
        assert "Main" in result
        assert "dj-sidebar__section" in result

    def test_xss(self):
        handler = SidebarSectionHandler()
        result = handler.render(
            ['label=xss'], {"xss": '<script>alert(1)</script>'},
        )
        assert "<script>" not in result


class TestNavMenuHandler:
    def test_basic_render(self):
        handler = NavMenuHandler()
        result = handler.render(
            ['id="nav"', 'brand="App"'],
            '<li>item</li>',
            {},
        )
        assert isinstance(result, SafeData)
        assert 'id="nav"' in result
        assert "App" in result
        assert "dj-nav" in result
        assert "dj-nav__brand" in result

    def test_mobile_open(self):
        handler = NavMenuHandler()
        result = handler.render(['mobile_open=true'], '', {})
        assert "dj-nav__list--open" in result

    def test_no_brand(self):
        handler = NavMenuHandler()
        result = handler.render([], '', {})
        assert "dj-nav__brand" not in result

    def test_xss_brand(self):
        handler = NavMenuHandler()
        result = handler.render(
            ['brand=xss'], '', {"xss": '<script>alert(1)</script>'},
        )
        assert "<script>" not in result


class TestNavItemHandler:
    def test_link_item(self):
        handler = NavItemHandler()
        result = handler.render(
            ['label="Home"', 'href="/"'], '', {},
        )
        assert isinstance(result, SafeData)
        assert "Home" in result
        assert 'href="/"' in result

    def test_event_item(self):
        handler = NavItemHandler()
        result = handler.render(
            ['label="Act"', 'event="do_it"'], '', {},
        )
        assert 'dj-click="do_it"' in result

    def test_dropdown(self):
        handler = NavItemHandler()
        result = handler.render(
            ['label="Menu"'],
            '<li>sub</li>',
            {},
        )
        assert "dj-nav__item--has-dropdown" in result
        assert "dj-nav__dropdown" in result
        assert "dj-nav__caret" in result

    def test_mega_menu(self):
        handler = NavItemHandler()
        result = handler.render(
            ['label="Mega"', 'mega=true'],
            '<li>sub</li>',
            {},
        )
        assert "dj-nav__dropdown--mega" in result

    def test_xss_label(self):
        handler = NavItemHandler()
        result = handler.render(
            ['label=xss'], '', {"xss": '<script>alert(1)</script>'},
        )
        assert "<script>" not in result

    def test_xss_href(self):
        handler = NavItemHandler()
        result = handler.render(
            ['label="X"', 'href=bad'], '',
            {"bad": '" onmouseover="alert(1)" x="'},
        )
        assert '" onmouseover="' not in result


class TestAppShellHandler:
    def test_basic_render(self):
        handler = AppShellHandler()
        result = handler.render(
            ['id="shell"'],
            '<aside>S</aside><main>C</main>',
            {},
        )
        assert isinstance(result, SafeData)
        assert "dj-app-shell" in result
        assert 'id="shell"' in result

    def test_sidebar_collapsed(self):
        handler = AppShellHandler()
        result = handler.render(['sidebar_collapsed=true'], '', {})
        assert "dj-app-shell--sidebar-collapsed" in result

    def test_custom_class(self):
        handler = AppShellHandler()
        result = handler.render(['class="my-shell"'], '', {})
        assert "my-shell" in result

    def test_xss_id(self):
        handler = AppShellHandler()
        result = handler.render(
            ['id=bad'], '', {"bad": '" onmouseover="alert(1)" x="'},
        )
        assert '" onmouseover="' not in result


class TestAppSubHandlers:
    def test_sidebar_handler(self):
        handler = AppSidebarHandler()
        result = handler.render([], 'sidebar content', {})
        assert isinstance(result, SafeData)
        assert "dj-app-shell__sidebar" in result
        assert "<aside" in result
        assert "sidebar content" in result

    def test_header_handler(self):
        handler = AppHeaderHandler()
        result = handler.render([], 'header content', {})
        assert isinstance(result, SafeData)
        assert "dj-app-shell__header" in result
        assert "<header" in result
        assert "header content" in result

    def test_content_handler(self):
        handler = AppContentHandler()
        result = handler.render([], 'main content', {})
        assert isinstance(result, SafeData)
        assert "dj-app-shell__content" in result
        assert "<main" in result
        assert "main content" in result
