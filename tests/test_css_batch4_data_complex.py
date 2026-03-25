"""Tests for CSS Batch 4 — Data & Complex Interactive components.

Verifies that Notification Center, Tree View, Gauge, Image Carousel,
Virtual List, Kanban Board, Table of Contents, Split Pane, and Rich Text
Editor render HTML containing the CSS classes defined in components.css.
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
    notification_center,
    tree_view,
    gauge,
    carousel,
    virtual_list,
    kanban_board,
    table_of_contents,
    rich_text_editor,
)


# ─── Notification Center ───


class TestNotificationCenterCSS:
    def test_wrapper_class(self):
        html = str(notification_center())
        assert 'class="notif-center"' in html

    def test_trigger_class(self):
        html = str(notification_center())
        assert 'class="notif-trigger"' in html

    def test_bell_class(self):
        html = str(notification_center())
        assert 'class="notif-bell"' in html

    def test_badge_class(self):
        html = str(notification_center(
            notifications=[{"id": "1", "message": "Hi", "unread": True}],
            unread_count=1,
        ))
        assert 'class="notif-badge"' in html

    def test_dropdown_class(self):
        html = str(notification_center())
        assert 'class="notif-dropdown"' in html

    def test_header_and_title_class(self):
        html = str(notification_center())
        assert 'class="notif-header"' in html
        assert 'class="notif-title"' in html

    def test_list_class(self):
        html = str(notification_center())
        assert 'class="notif-list"' in html

    def test_item_unread_class(self):
        html = str(notification_center(
            notifications=[{"id": "1", "message": "New", "unread": True}],
        ))
        assert "notif-item-unread" in html

    def test_item_msg_class(self):
        html = str(notification_center(
            notifications=[{"id": "1", "message": "Hello"}],
        ))
        assert 'class="notif-item-msg"' in html

    def test_item_time_class(self):
        html = str(notification_center(
            notifications=[{"id": "1", "message": "Hello", "time": "2m ago"}],
        ))
        assert 'class="notif-item-time"' in html

    def test_empty_class(self):
        html = str(notification_center(notifications=[]))
        assert 'class="notif-empty"' in html

    def test_footer_class(self):
        html = str(notification_center(
            notifications=[{"id": "1", "message": "Msg"}],
        ))
        assert 'class="notif-footer"' in html


# ─── Tree View ───


class TestTreeViewCSS:
    NODES = [
        {"id": "root", "label": "Root", "expanded": True, "children": [
            {"id": "child", "label": "Child"},
        ]},
    ]

    def test_wrapper_class(self):
        html = str(tree_view(nodes=self.NODES))
        assert 'class="tree"' in html

    def test_node_class(self):
        html = str(tree_view(nodes=self.NODES))
        assert "tree-node" in html

    def test_node_expanded_class(self):
        html = str(tree_view(nodes=self.NODES))
        assert "tree-node-expanded" in html

    def test_node_selected_class(self):
        html = str(tree_view(nodes=self.NODES, selected="root"))
        assert "tree-node-selected" in html

    def test_node_row_class(self):
        html = str(tree_view(nodes=self.NODES))
        assert 'class="tree-node-row"' in html

    def test_toggle_class(self):
        html = str(tree_view(nodes=self.NODES))
        assert 'class="tree-toggle"' in html

    def test_toggle_placeholder_class(self):
        html = str(tree_view(nodes=self.NODES))
        # Child node (leaf) gets placeholder
        assert 'class="tree-toggle-placeholder"' in html

    def test_node_label_class(self):
        html = str(tree_view(nodes=self.NODES))
        assert 'class="tree-node-label"' in html

    def test_children_class(self):
        html = str(tree_view(nodes=self.NODES))
        assert 'class="tree-children"' in html

    def test_has_children_class(self):
        html = str(tree_view(nodes=self.NODES))
        assert "tree-node-has-children" in html

    def test_leaf_class(self):
        html = str(tree_view(nodes=self.NODES))
        assert "tree-node-leaf" in html


# ─── Gauge / Donut ───


class TestGaugeCSS:
    def test_wrapper_class(self):
        html = str(gauge(value=50))
        assert "gauge" in html

    def test_color_variant_class(self):
        html = str(gauge(value=50, color="success"))
        assert "gauge-success" in html

    def test_track_class(self):
        html = str(gauge(value=50))
        assert 'class="gauge-track"' in html

    def test_fill_class(self):
        html = str(gauge(value=50))
        assert "gauge-fill" in html

    def test_fill_color_class(self):
        html = str(gauge(value=50, color="warning"))
        assert "gauge-fill-warning" in html

    def test_value_text_class(self):
        html = str(gauge(value=50))
        assert 'class="gauge-value-text"' in html

    def test_label_class(self):
        html = str(gauge(value=50, label="CPU"))
        assert 'class="gauge-label"' in html


# ─── Image Carousel ───


class TestCarouselCSS:
    IMAGES = [
        {"src": "/img/a.jpg", "alt": "A"},
        {"src": "/img/b.jpg", "alt": "B"},
    ]

    def test_wrapper_class(self):
        html = str(carousel(images=self.IMAGES))
        assert 'class="carousel"' in html

    def test_empty_class(self):
        html = str(carousel(images=[]))
        assert "carousel-empty" in html

    def test_track_class(self):
        html = str(carousel(images=self.IMAGES))
        assert 'class="carousel-track"' in html

    def test_slide_active_class(self):
        html = str(carousel(images=self.IMAGES, active=0))
        assert "carousel-slide-active" in html

    def test_img_class(self):
        html = str(carousel(images=self.IMAGES))
        assert 'class="carousel-img"' in html

    def test_caption_class(self):
        html = str(carousel(images=[{"src": "/a.jpg", "caption": "Hello"}]))
        assert 'class="carousel-caption"' in html

    def test_btn_prev_next_classes(self):
        html = str(carousel(images=self.IMAGES))
        assert "carousel-btn-prev" in html
        assert "carousel-btn-next" in html

    def test_dots_class(self):
        html = str(carousel(images=self.IMAGES))
        assert 'class="carousel-dots"' in html

    def test_dot_active_class(self):
        html = str(carousel(images=self.IMAGES, active=0))
        assert "carousel-dot-active" in html

    def test_counter_class(self):
        html = str(carousel(images=self.IMAGES))
        assert 'class="carousel-counter"' in html


# ─── Virtual List ───


class TestVirtualListCSS:
    ITEMS = [
        {"label": "Item 1", "sub": "desc"},
        {"label": "Item 2"},
    ]

    def test_wrapper_class(self):
        html = str(virtual_list(items=self.ITEMS, total=2))
        assert 'class="virtual-list"' in html

    def test_info_class(self):
        html = str(virtual_list(items=self.ITEMS, total=2))
        assert 'class="vl-info"' in html

    def test_scroll_class(self):
        html = str(virtual_list(items=self.ITEMS, total=2))
        assert 'class="vl-scroll"' in html

    def test_item_class(self):
        html = str(virtual_list(items=self.ITEMS, total=2))
        assert 'class="vl-item"' in html

    def test_item_label_class(self):
        html = str(virtual_list(items=self.ITEMS, total=2))
        assert 'class="vl-item-label"' in html

    def test_item_sub_class(self):
        html = str(virtual_list(items=self.ITEMS, total=2))
        assert 'class="vl-item-sub"' in html

    def test_load_more_class(self):
        html = str(virtual_list(items=[{"label": "A"}], total=100, page=1, page_size=1))
        assert 'class="vl-load-more"' in html


# ─── Kanban Board ───


class TestKanbanBoardCSS:
    COLUMNS = [
        {
            "id": "todo",
            "title": "To Do",
            "color": "#6366F1",
            "cards": [
                {"id": "c1", "title": "Task A", "label": "bug", "sub": "Fix it"},
            ],
        },
    ]

    def test_wrapper_class(self):
        html = str(kanban_board(columns=self.COLUMNS))
        assert 'class="kanban"' in html

    def test_col_class(self):
        html = str(kanban_board(columns=self.COLUMNS))
        assert 'class="kanban-col"' in html

    def test_col_header_class(self):
        html = str(kanban_board(columns=self.COLUMNS))
        assert 'class="kanban-col-header"' in html

    def test_col_title_class(self):
        html = str(kanban_board(columns=self.COLUMNS))
        assert 'class="kanban-col-title"' in html

    def test_col_count_class(self):
        html = str(kanban_board(columns=self.COLUMNS))
        assert 'class="kanban-col-count"' in html

    def test_cards_container_class(self):
        html = str(kanban_board(columns=self.COLUMNS))
        assert 'class="kanban-cards"' in html

    def test_card_class(self):
        html = str(kanban_board(columns=self.COLUMNS))
        assert 'class="kanban-card"' in html

    def test_card_title_class(self):
        html = str(kanban_board(columns=self.COLUMNS))
        assert 'class="kanban-card-title"' in html

    def test_card_sub_class(self):
        html = str(kanban_board(columns=self.COLUMNS))
        assert 'class="kanban-card-sub"' in html

    def test_card_label_class(self):
        html = str(kanban_board(columns=self.COLUMNS))
        assert "kanban-card-label" in html
        assert "kanban-label-bug" in html

    def test_add_card_class(self):
        html = str(kanban_board(columns=self.COLUMNS))
        assert 'class="kanban-add-card"' in html


# ─── Table of Contents ───


class TestTableOfContentsCSS:
    ITEMS = [
        {"id": "intro", "label": "Introduction", "level": 1},
        {"id": "details", "label": "Details", "level": 2},
    ]

    def test_wrapper_class(self):
        html = str(table_of_contents(items=self.ITEMS))
        assert 'class="toc"' in html

    def test_title_class(self):
        html = str(table_of_contents(items=self.ITEMS, title="Contents"))
        assert 'class="toc-title"' in html

    def test_list_class(self):
        html = str(table_of_contents(items=self.ITEMS))
        assert 'class="toc-list"' in html

    def test_item_class(self):
        html = str(table_of_contents(items=self.ITEMS))
        assert "toc-item" in html

    def test_item_active_class(self):
        html = str(table_of_contents(items=self.ITEMS, active="intro"))
        assert "toc-item-active" in html

    def test_level_classes(self):
        html = str(table_of_contents(items=self.ITEMS))
        assert "toc-level-1" in html
        assert "toc-level-2" in html


# ─── Split Pane ───


class TestSplitPaneCSS:
    """Test that the Rust handler / template tag produces correct CSS classes.

    Since SplitPaneNode is a block tag requiring template parsing, we test
    the Rust handler's render method which wraps content directly.
    """

    def test_wrapper_class(self):
        from djust_components.rust_handlers import SplitPaneHandler
        handler = SplitPaneHandler()
        html = handler.render([], "<p>A</p><p>B</p>", {})
        assert "split-pane" in html

    def test_direction_horizontal(self):
        from djust_components.rust_handlers import SplitPaneHandler
        handler = SplitPaneHandler()
        html = handler.render(['direction="horizontal"'], "content", {})
        assert "split-pane-horizontal" in html

    def test_direction_vertical(self):
        from djust_components.rust_handlers import SplitPaneHandler
        handler = SplitPaneHandler()
        html = handler.render(['direction="vertical"'], "content", {})
        assert "split-pane-vertical" in html


# ─── Rich Text Editor ───


class TestRichTextEditorCSS:
    def test_wrapper_class(self):
        html = str(rich_text_editor())
        assert 'class="rte"' in html

    def test_toolbar_class(self):
        html = str(rich_text_editor())
        assert 'class="rte-toolbar"' in html

    def test_btn_class(self):
        html = str(rich_text_editor())
        assert 'class="rte-btn"' in html

    def test_sep_class(self):
        html = str(rich_text_editor())
        assert 'class="rte-sep"' in html

    def test_editor_class(self):
        html = str(rich_text_editor())
        assert 'class="rte-editor"' in html

    def test_contenteditable(self):
        html = str(rich_text_editor())
        assert 'contenteditable="true"' in html

    def test_hidden_input(self):
        html = str(rich_text_editor(name="body"))
        assert 'name="body"' in html

    def test_label_rendered(self):
        html = str(rich_text_editor(label="Content"))
        assert "Content" in html
        assert "form-label" in html
