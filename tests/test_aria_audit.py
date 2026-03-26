"""Tests for ARIA audit fixes (#ARIA-AUDIT).

Covers all 8 fix categories:
1. role="menu"/role="menuitem" on dropdown patterns
2. :focus-within alongside :hover (CSS — tested via tabindex presence)
3. role="status" on Status Indicator
4. role="region" with aria-label on Scroll Area
5. aria-live="polite" on Announcement Bar
6. Unique ARIA IDs per Confirmation Dialog instance
7. aria-expanded on toggle triggers
8. :focus-visible CSS states (verified in CSS file, not template tests)
"""

import re

import pytest


# ---------------------------------------------------------------------------
# 1. role="menu" / role="menuitem" on dropdown patterns
# ---------------------------------------------------------------------------

class TestDropdownRoles:
    """Split Button, Context Menu, and Dropdown Menu emit correct roles."""

    def test_split_button_menu_role(self, render):
        html = render(
            '{% split_button label="Save" event="save" '
            'options=opts open=True %}',
            {"opts": [{"label": "Save as", "event": "save_as"}]},
        )
        assert 'role="menu"' in html
        assert 'role="menuitem"' in html

    def test_split_button_option_has_menuitem(self, render):
        html = render(
            '{% split_button label="Save" event="save" '
            'options=opts open=True %}',
            {"opts": [
                {"label": "Draft", "event": "save_draft"},
                {"label": "Publish", "event": "publish"},
            ]},
        )
        assert html.count('role="menuitem"') == 2

    def test_context_menu_has_menu_role(self, render):
        html = render(
            '{% context_menu label="Right-click" %}'
            '{% context_menu_item label="Edit" event="edit" %}'
            '{% endcontext_menu %}'
        )
        assert 'role="menu"' in html

    def test_context_menu_item_has_menuitem_role(self, render):
        html = render(
            '{% context_menu_item label="Delete" event="delete" %}'
        )
        assert 'role="menuitem"' in html

    def test_dropdown_menu_has_menu_role(self, render):
        html = render(
            '{% dropdown_menu label="Actions" items=items open=True %}{% enddropdown_menu %}',
            {"items": [{"label": "Edit", "event": "edit"}]},
        )
        assert 'role="menu"' in html
        assert 'role="menuitem"' in html


# ---------------------------------------------------------------------------
# 2. Focus-within support (tabindex on hover-triggered components)
# ---------------------------------------------------------------------------

class TestFocusWithinSupport:
    """Hover-triggered components get tabindex for keyboard :focus-within."""

    def test_source_citation_has_tabindex(self, render):
        html = render(
            '{% source_citation index=1 title="Test" url="http://example.com" %}'
        )
        assert 'tabindex="0"' in html

    def test_hover_card_trigger_has_tabindex(self, render):
        html = render(
            '{% hover_card trigger="@user" %}<p>Card</p>{% endhover_card %}'
        )
        assert 'tabindex="0"' in html

    def test_popover_trigger_has_aria_expanded(self, render):
        html = render(
            '{% popover trigger="Info" %}Details{% endpopover %}'
        )
        assert 'aria-expanded="false"' in html

    def test_popover_has_role_tooltip(self, render):
        html = render(
            '{% popover trigger="Info" %}Details{% endpopover %}'
        )
        assert 'role="tooltip"' in html


# ---------------------------------------------------------------------------
# 3. role="status" on Status Indicator
# ---------------------------------------------------------------------------

class TestStatusIndicatorRole:
    def test_status_indicator_has_role_status(self, render):
        html = render('{% status_indicator status="online" label="API" %}')
        assert 'role="status"' in html

    def test_status_indicator_offline(self, render):
        html = render('{% status_indicator status="offline" %}')
        assert 'role="status"' in html


# ---------------------------------------------------------------------------
# 4. role="region" with aria-label on Scroll Area
# ---------------------------------------------------------------------------

class TestScrollAreaRegion:
    def test_scroll_area_has_region_role(self, render):
        html = render(
            '{% scroll_area %}<p>Content</p>{% endscroll_area %}'
        )
        assert 'role="region"' in html

    def test_scroll_area_has_default_aria_label(self, render):
        html = render(
            '{% scroll_area %}<p>Content</p>{% endscroll_area %}'
        )
        assert 'aria-label="Scrollable content"' in html

    def test_scroll_area_custom_label(self, render):
        html = render(
            '{% scroll_area label="Log output" %}<p>Logs</p>{% endscroll_area %}'
        )
        assert 'aria-label="Log output"' in html

    def test_scroll_area_has_tabindex(self, render):
        html = render(
            '{% scroll_area %}<p>Content</p>{% endscroll_area %}'
        )
        assert 'tabindex="0"' in html


# ---------------------------------------------------------------------------
# 5. aria-live="polite" on Announcement Bar
# ---------------------------------------------------------------------------

class TestAnnouncementBarLive:
    def test_announcement_bar_has_aria_live(self, render):
        html = render(
            '{% announcement_bar %}Important news{% endannouncement_bar %}'
        )
        assert 'aria-live="polite"' in html

    def test_announcement_bar_retains_banner_role(self, render):
        html = render(
            '{% announcement_bar %}News{% endannouncement_bar %}'
        )
        assert 'role="banner"' in html


# ---------------------------------------------------------------------------
# 6. Unique ARIA IDs per Confirmation Dialog instance
# ---------------------------------------------------------------------------

class TestConfirmDialogUniqueIds:
    def test_confirm_dialog_has_unique_ids(self, render):
        html = render(
            '{% confirm_dialog message="Delete?" title="Confirm" open=True %}'
        )
        # IDs should contain a unique hex suffix, not the static "dj-confirm-title"
        assert 'id="dj-confirm-title"' not in html
        assert 'id="dj-confirm-msg"' not in html
        # Should match pattern like dj-confirm-title-abcd1234
        assert re.search(r'id="dj-confirm-title-[0-9a-f]+"', html)
        assert re.search(r'id="dj-confirm-msg-[0-9a-f]+"', html)

    def test_confirm_dialog_aria_labelledby_matches_id(self, render):
        html = render(
            '{% confirm_dialog message="Sure?" open=True %}'
        )
        title_id = re.search(r'id="(dj-confirm-title-[0-9a-f]+)"', html)
        msg_id = re.search(r'id="(dj-confirm-msg-[0-9a-f]+)"', html)
        assert title_id and msg_id
        assert f'aria-labelledby="{title_id.group(1)}"' in html
        assert f'aria-describedby="{msg_id.group(1)}"' in html

    def test_two_confirm_dialogs_have_different_ids(self, render):
        html1 = render(
            '{% confirm_dialog message="First?" open=True %}'
        )
        html2 = render(
            '{% confirm_dialog message="Second?" open=True %}'
        )
        id1 = re.search(r'id="(dj-confirm-title-[0-9a-f]+)"', html1).group(1)
        id2 = re.search(r'id="(dj-confirm-title-[0-9a-f]+)"', html2).group(1)
        assert id1 != id2


# ---------------------------------------------------------------------------
# 7. aria-expanded on toggle triggers
# ---------------------------------------------------------------------------

class TestAriaExpanded:
    def test_split_button_toggle_has_aria_expanded(self, render):
        html = render(
            '{% split_button label="Save" event="save" '
            'options=opts %}',
            {"opts": [{"label": "Draft", "event": "draft"}]},
        )
        assert 'aria-expanded="false"' in html
        assert 'aria-haspopup="true"' in html

    def test_split_button_open_has_aria_expanded_true(self, render):
        html = render(
            '{% split_button label="Save" event="save" '
            'options=opts open=True %}',
            {"opts": [{"label": "Draft", "event": "draft"}]},
        )
        assert 'aria-expanded="true"' in html

    def test_toolbar_overflow_has_aria_expanded(self, render):
        html = render(
            '{% toolbar %}'
            '{% toolbar_overflow %}<button>Action</button>{% endtoolbar_overflow %}'
            '{% endtoolbar %}'
        )
        assert 'aria-expanded="false"' in html
        assert 'aria-haspopup="true"' in html

    def test_popconfirm_trigger_has_aria_expanded(self, render):
        html = render(
            '{% popconfirm message="Delete?" %}'
            '<button>Delete</button>'
            '{% endpopconfirm %}'
        )
        assert 'aria-expanded="false"' in html
        assert 'aria-haspopup="true"' in html

    def test_dropdown_menu_trigger_has_aria_expanded(self, render):
        html = render(
            '{% dropdown_menu label="Menu" %}{% enddropdown_menu %}'
        )
        assert 'aria-expanded="false"' in html

    def test_dropdown_menu_open_has_aria_expanded_true(self, render):
        html = render(
            '{% dropdown_menu label="Menu" open=True %}{% enddropdown_menu %}'
        )
        assert 'aria-expanded="true"' in html


# ---------------------------------------------------------------------------
# 8. CSS :focus-visible rules (spot-check file content)
# ---------------------------------------------------------------------------

class TestFocusVisibleCSS:
    """Verify :focus-visible rules exist in the CSS file."""

    @pytest.fixture(autouse=True)
    def load_css(self):
        import pathlib
        css_path = pathlib.Path(__file__).resolve().parent.parent / (
            "src/djust_components/static/djust_components/components.css"
        )
        self.css = css_path.read_text()

    def test_split_btn_focus_visible(self):
        assert ".split-btn-primary:focus-visible" in self.css
        assert ".split-btn-toggle:focus-visible" in self.css

    def test_ctx_item_focus_visible(self):
        assert ".ctx-item:focus-visible" in self.css

    def test_dropdown_menu_trigger_focus_visible(self):
        assert ".dj-dropdown-menu__trigger:focus-visible" in self.css

    def test_toolbar_overflow_focus_visible(self):
        assert ".dj-toolbar__overflow-trigger:focus-visible" in self.css

    def test_popconfirm_focus_visible(self):
        assert ".dj-popconfirm-trigger:focus-visible" in self.css

    def test_confirm_dialog_btn_focus_visible(self):
        assert ".dj-confirm-dialog__btn:focus-visible" in self.css

    def test_announcement_bar_close_focus_visible(self):
        assert ".dj-announcement-bar__close:focus-visible" in self.css

    def test_hover_card_trigger_focus_visible(self):
        assert ".dj-hover-card__trigger:focus-visible" in self.css

    def test_citation_focus_visible(self):
        assert ".dj-citation:focus-visible" in self.css

    def test_scroll_area_focus_visible(self):
        assert ".dj-scroll-area:focus-visible" in self.css

    def test_popover_focus_within(self):
        assert ".popover-wrapper:focus-within .popover" in self.css

    def test_citation_focus_within(self):
        import pathlib
        classes_css_path = pathlib.Path(__file__).resolve().parent.parent / (
            "src/djust_components/static/djust_components/components-classes.css"
        )
        classes_css = classes_css_path.read_text()
        assert ".dj-citation:focus-within .dj-citation__popover" in classes_css
