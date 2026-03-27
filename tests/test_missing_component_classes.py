"""Tests for the 61 missing component classes.

Each component has 3 tests:
  - test_{name}_basic: default render produces expected CSS class
  - test_{name}_params: non-default params appear in output
  - test_{name}_html_escaping: script injection in text params is escaped
"""

import pytest

from djust_components.components import (
    Accordion,
    AnnouncementBar,
    AppShell,
    AspectRatio,
    Avatar,
    Breadcrumb,
    Callout,
    Carousel,
    CodeBlock,
    Collapsible,
    ColorPicker,
    Combobox,
    CommandPalette,
    ContextMenu,
    CopyButton,
    DataTable,
    DatePicker,
    DescriptionList,
    Dropdown,
    EmptyState,
    Fab,
    Fieldset,
    FileDropzone,
    FilterBar,
    FormGroup,
    Gauge,
    Icon,
    InlineEdit,
    InputGroup,
    KanbanBoard,
    Kbd,
    LoadingOverlay,
    Modal,
    MultiSelect,
    NavMenu,
    NotificationCenter,
    NumberStepper,
    OtpInput,
    PageHeader,
    Pagination,
    Popover,
    Rating,
    RichTextEditor,
    ScrollArea,
    Sheet,
    Sidebar,
    Skeleton,
    SplitButton,
    SplitPane,
    Stepper,
    StickyHeader,
    TableOfContents,
    Tabs,
    TagInput,
    ThemeToggle,
    Timeline,
    ToggleGroup,
    Toolbar,
    Tooltip,
    TreeView,
    VirtualList,
)

XSS = '<script>alert("xss")</script>'
XSS_ESCAPED = "&lt;script&gt;"


# =========================================================================
# Modal
# =========================================================================

class TestModal:
    def test_modal_basic(self):
        m = Modal(title="Test", is_open=True)
        out = m._render_custom()
        assert "dj-modal" in out
        assert "dj-modal--md" in out

    def test_modal_params(self):
        m = Modal(title="Confirm", size="lg", is_open=True, close_event="close_it")
        out = m._render_custom()
        assert "dj-modal--lg" in out
        assert "Confirm" in out
        assert 'dj-click="close_it"' in out

    def test_modal_html_escaping(self):
        m = Modal(title=XSS, is_open=True)
        out = m._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out

    def test_modal_closed(self):
        m = Modal(title="Test", is_open=False)
        assert m._render_custom() == ""


# =========================================================================
# Tabs
# =========================================================================

class TestTabs:
    def test_tabs_basic(self):
        t = Tabs(tabs=[{"id": "a", "label": "Tab A"}], active="a")
        out = t._render_custom()
        assert "dj-tabs" in out
        assert "Tab A" in out

    def test_tabs_params(self):
        t = Tabs(tabs=[{"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
                 active="a", event="change_tab")
        out = t._render_custom()
        assert "dj-tab--active" in out
        assert 'dj-click="change_tab"' in out

    def test_tabs_html_escaping(self):
        t = Tabs(tabs=[{"id": "a", "label": XSS}], active="a")
        out = t._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Accordion
# =========================================================================

class TestAccordion:
    def test_accordion_basic(self):
        a = Accordion(items=[{"id": "1", "title": "Section", "content": "Body"}])
        out = a._render_custom()
        assert "dj-accordion" in out

    def test_accordion_params(self):
        a = Accordion(items=[{"id": "1", "title": "S1"}, {"id": "2", "title": "S2"}],
                      active="1", event="toggle")
        out = a._render_custom()
        assert "dj-accordion-item--open" in out
        assert 'dj-click="toggle"' in out

    def test_accordion_html_escaping(self):
        a = Accordion(items=[{"id": "1", "title": XSS}])
        out = a._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Dropdown
# =========================================================================

class TestDropdown:
    def test_dropdown_basic(self):
        d = Dropdown(label="Menu", is_open=True)
        out = d._render_custom()
        assert "dj-dropdown" in out

    def test_dropdown_params(self):
        d = Dropdown(label="Actions", variant="primary", is_open=True,
                     toggle_event="toggle_menu")
        out = d._render_custom()
        assert "dj-dropdown--primary" in out
        assert 'dj-click="toggle_menu"' in out

    def test_dropdown_html_escaping(self):
        d = Dropdown(label=XSS, is_open=True)
        out = d._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Tooltip
# =========================================================================

class TestTooltip:
    def test_tooltip_basic(self):
        t = Tooltip(text="Help", content="<button>Hover</button>")
        out = t._render_custom()
        assert "dj-tooltip" in out

    def test_tooltip_params(self):
        t = Tooltip(text="Info", position="bottom", content="<span>X</span>")
        out = t._render_custom()
        assert "dj-tooltip--bottom" in out

    def test_tooltip_html_escaping(self):
        t = Tooltip(text=XSS, content="<span>X</span>")
        out = t._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Popover
# =========================================================================

class TestPopover:
    def test_popover_basic(self):
        p = Popover(trigger="Click", content="<p>Content</p>")
        out = p._render_custom()
        assert "popover-wrapper" in out

    def test_popover_params(self):
        p = Popover(trigger="Open", title="Title", placement="top")
        out = p._render_custom()
        assert "popover-top" in out
        assert "Title" in out

    def test_popover_html_escaping(self):
        p = Popover(trigger=XSS, title=XSS)
        out = p._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Collapsible
# =========================================================================

class TestCollapsible:
    def test_collapsible_basic(self):
        c = Collapsible(trigger="Toggle", content="<p>Body</p>")
        out = c._render_custom()
        assert "collapsible" in out

    def test_collapsible_params(self):
        c = Collapsible(trigger="Show", is_open=True, event="toggle_it")
        out = c._render_custom()
        assert "collapsible-open" in out
        assert 'dj-click="toggle_it"' in out

    def test_collapsible_html_escaping(self):
        c = Collapsible(trigger=XSS)
        out = c._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Sheet
# =========================================================================

class TestSheet:
    def test_sheet_basic(self):
        s = Sheet(content="<p>Body</p>", is_open=True)
        out = s._render_custom()
        assert "sheet" in out

    def test_sheet_params(self):
        s = Sheet(title="Settings", side="left", is_open=True, close_event="close_it")
        out = s._render_custom()
        assert "sheet-left" in out
        assert "Settings" in out
        assert 'dj-click="close_it"' in out

    def test_sheet_html_escaping(self):
        s = Sheet(title=XSS, is_open=True)
        out = s._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# CommandPalette
# =========================================================================

class TestCommandPalette:
    def test_command_palette_basic(self):
        cp = CommandPalette(is_open=True)
        out = cp._render_custom()
        assert "palette" in out

    def test_command_palette_params(self):
        cp = CommandPalette(is_open=True, placeholder="Find...",
                           search_event="search", close_event="close")
        out = cp._render_custom()
        assert "Find..." in out
        assert 'dj-input="search"' in out

    def test_command_palette_html_escaping(self):
        cp = CommandPalette(is_open=True, placeholder=XSS)
        out = cp._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# ContextMenu
# =========================================================================

class TestContextMenu:
    def test_context_menu_basic(self):
        cm = ContextMenu(label="Area")
        out = cm._render_custom()
        assert "ctx-wrapper" in out

    def test_context_menu_params(self):
        cm = ContextMenu(label="Click here", content='<div class="ctx-item">Edit</div>')
        out = cm._render_custom()
        assert "Click here" in out
        assert "ctx-menu" in out

    def test_context_menu_html_escaping(self):
        cm = ContextMenu(label=XSS)
        out = cm._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Carousel
# =========================================================================

class TestCarousel:
    def test_carousel_basic(self):
        c = Carousel(images=[{"src": "/img.jpg", "alt": "Test"}])
        out = c._render_custom()
        assert "carousel" in out

    def test_carousel_empty(self):
        c = Carousel()
        out = c._render_custom()
        assert "carousel-empty" in out

    def test_carousel_html_escaping(self):
        c = Carousel(images=[{"src": XSS, "alt": XSS}])
        out = c._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# LoadingOverlay
# =========================================================================

class TestLoadingOverlay:
    def test_loading_overlay_basic(self):
        lo = LoadingOverlay(content="<p>Content</p>", active=True)
        out = lo._render_custom()
        assert "dj-loading-overlay" in out

    def test_loading_overlay_params(self):
        lo = LoadingOverlay(content="<p>X</p>", active=True, text="Loading...", spinner_size="lg")
        out = lo._render_custom()
        assert "Loading..." in out
        assert "dj-loading-overlay__spinner--lg" in out

    def test_loading_overlay_html_escaping(self):
        lo = LoadingOverlay(content="<p>X</p>", active=True, text=XSS)
        out = lo._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# AnnouncementBar
# =========================================================================

class TestAnnouncementBar:
    def test_announcement_bar_basic(self):
        ab = AnnouncementBar(content="Hello")
        out = ab._render_custom()
        assert "dj-announcement-bar" in out

    def test_announcement_bar_params(self):
        ab = AnnouncementBar(content="Sale!", variant="warning", dismissible=True)
        out = ab._render_custom()
        assert "dj-announcement-bar--warning" in out
        assert "dj-announcement-bar__close" in out

    def test_announcement_bar_html_escaping(self):
        ab = AnnouncementBar(content="ok", custom_class=XSS)
        out = ab._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Callout
# =========================================================================

class TestCallout:
    def test_callout_basic(self):
        c = Callout(content="<p>Note</p>")
        out = c._render_custom()
        assert "dj-callout" in out

    def test_callout_params(self):
        c = Callout(content="<p>X</p>", variant="warning", title="Warning")
        out = c._render_custom()
        assert "dj-callout--warning" in out
        assert "Warning" in out

    def test_callout_html_escaping(self):
        c = Callout(content="<p>X</p>", title=XSS)
        out = c._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# SplitPane
# =========================================================================

class TestSplitPane:
    def test_split_pane_basic(self):
        sp = SplitPane(left="<p>L</p>", right="<p>R</p>")
        out = sp._render_custom()
        assert "split-pane" in out

    def test_split_pane_params(self):
        sp = SplitPane(left="L", right="R", direction="vertical", initial=30)
        out = sp._render_custom()
        assert "split-pane-vertical" in out
        assert "height:30%" in out

    def test_split_pane_html_escaping(self):
        sp = SplitPane(left="L", right="R", custom_class=XSS)
        out = sp._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# ScrollArea
# =========================================================================

class TestScrollArea:
    def test_scroll_area_basic(self):
        sa = ScrollArea(content="<p>Stuff</p>")
        out = sa._render_custom()
        assert "dj-scroll-area" in out

    def test_scroll_area_params(self):
        sa = ScrollArea(content="<p>X</p>", max_height="200px", label="List")
        out = sa._render_custom()
        assert "200px" in out
        assert 'aria-label="List"' in out

    def test_scroll_area_html_escaping(self):
        sa = ScrollArea(content="<p>X</p>", label=XSS)
        out = sa._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# StickyHeader
# =========================================================================

class TestStickyHeader:
    def test_sticky_header_basic(self):
        sh = StickyHeader(content="<h1>Title</h1>")
        out = sh._render_custom()
        assert "dj-sticky-header" in out

    def test_sticky_header_params(self):
        sh = StickyHeader(content="<h1>Title</h1>", offset="20px", z_index="50")
        out = sh._render_custom()
        assert "top: 20px" in out
        assert "z-index: 50" in out

    def test_sticky_header_html_escaping(self):
        sh = StickyHeader(content="<h1>X</h1>", custom_class=XSS)
        out = sh._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# DescriptionList
# =========================================================================

class TestDescriptionList:
    def test_description_list_basic(self):
        dl = DescriptionList(items=[{"term": "Name", "detail": "Value"}])
        out = dl._render_custom()
        assert "dj-dl" in out

    def test_description_list_params(self):
        dl = DescriptionList(items=[{"term": "A", "detail": "B"}], layout="horizontal")
        out = dl._render_custom()
        assert "dj-dl--horizontal" in out

    def test_description_list_html_escaping(self):
        dl = DescriptionList(items=[{"term": XSS, "detail": XSS}])
        out = dl._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# AspectRatio
# =========================================================================

class TestAspectRatio:
    def test_aspect_ratio_basic(self):
        ar = AspectRatio(content="<img>")
        out = ar._render_custom()
        assert "dj-aspect-ratio" in out

    def test_aspect_ratio_params(self):
        ar = AspectRatio(content="<img>", ratio="4/3")
        out = ar._render_custom()
        assert "aspect-ratio: 4/3" in out

    def test_aspect_ratio_html_escaping(self):
        ar = AspectRatio(content="<img>", custom_class=XSS)
        out = ar._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Timeline
# =========================================================================

class TestTimeline:
    def test_timeline_basic(self):
        t = Timeline(items=[{"title": "Event", "time": "2024-01-01"}])
        out = t._render_custom()
        assert "timeline" in out

    def test_timeline_params(self):
        t = Timeline(items=[{"title": "Deploy", "time": "3pm", "content": "<p>Done</p>"}])
        out = t._render_custom()
        assert "Deploy" in out
        assert "3pm" in out

    def test_timeline_html_escaping(self):
        t = Timeline(items=[{"title": XSS, "time": XSS}])
        out = t._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Stepper
# =========================================================================

class TestStepper:
    def test_stepper_basic(self):
        s = Stepper(steps=["Step 1", "Step 2"])
        out = s._render_custom()
        assert "stepper" in out

    def test_stepper_params(self):
        s = Stepper(steps=[{"label": "A"}, {"label": "B"}], active=1, event="go")
        out = s._render_custom()
        assert "stepper-step-active" in out
        assert 'dj-click="go"' in out

    def test_stepper_html_escaping(self):
        s = Stepper(steps=[XSS])
        out = s._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Rating
# =========================================================================

class TestRating:
    def test_rating_basic(self):
        r = Rating(value=3)
        out = r._render_custom()
        assert "rating" in out

    def test_rating_params(self):
        r = Rating(value=4, max_stars=5, readonly=True)
        out = r._render_custom()
        assert "rating-star-full" in out
        # readonly uses spans not buttons
        assert "<span" in out

    def test_rating_html_escaping(self):
        r = Rating(value=1, custom_class=XSS)
        out = r._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Gauge
# =========================================================================

class TestGauge:
    def test_gauge_basic(self):
        g = Gauge(value=50)
        out = g._render_custom()
        assert "gauge" in out

    def test_gauge_params(self):
        g = Gauge(value=75, max_value=100, color="success", label="CPU")
        out = g._render_custom()
        assert "gauge-success" in out
        assert "CPU" in out

    def test_gauge_html_escaping(self):
        g = Gauge(value=50, label=XSS)
        out = g._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# TreeView
# =========================================================================

class TestTreeView:
    def test_tree_view_basic(self):
        tv = TreeView(nodes=[{"id": "1", "label": "Root"}])
        out = tv._render_custom()
        assert "tree" in out

    def test_tree_view_params(self):
        tv = TreeView(
            nodes=[{"id": "1", "label": "Root", "expanded": True,
                    "children": [{"id": "1a", "label": "Child"}]}],
            selected="1a"
        )
        out = tv._render_custom()
        assert "tree-node-selected" in out
        assert "tree-node-expanded" in out

    def test_tree_view_html_escaping(self):
        tv = TreeView(nodes=[{"id": "1", "label": XSS}])
        out = tv._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# NotificationCenter
# =========================================================================

class TestNotificationCenter:
    def test_notification_center_basic(self):
        nc = NotificationCenter()
        out = nc._render_custom()
        assert "notif-center" in out

    def test_notification_center_params(self):
        nc = NotificationCenter(
            notifications=[{"id": "1", "message": "New msg", "unread": True}],
            unread_count=1
        )
        out = nc._render_custom()
        assert "notif-badge" in out
        assert "New msg" in out

    def test_notification_center_html_escaping(self):
        nc = NotificationCenter(
            notifications=[{"id": "1", "message": XSS}]
        )
        out = nc._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# KanbanBoard
# =========================================================================

class TestKanbanBoard:
    def test_kanban_board_basic(self):
        kb = KanbanBoard(columns=[{"id": "todo", "title": "To Do", "cards": []}])
        out = kb._render_custom()
        assert "kanban" in out

    def test_kanban_board_params(self):
        kb = KanbanBoard(columns=[{
            "id": "done", "title": "Done",
            "cards": [{"title": "Task A"}]
        }])
        out = kb._render_custom()
        assert "Task A" in out
        assert "Done" in out

    def test_kanban_board_html_escaping(self):
        kb = KanbanBoard(columns=[{"id": "1", "title": XSS, "cards": [{"title": XSS}]}])
        out = kb._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# VirtualList
# =========================================================================

class TestVirtualList:
    def test_virtual_list_basic(self):
        vl = VirtualList(items=["Item 1", "Item 2"], total=2)
        out = vl._render_custom()
        assert "virtual-list" in out

    def test_virtual_list_params(self):
        vl = VirtualList(items=["A"], total=100, page=1, page_size=20)
        out = vl._render_custom()
        assert "Load more" in out

    def test_virtual_list_html_escaping(self):
        vl = VirtualList(items=[XSS], total=1)
        out = vl._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# TableOfContents
# =========================================================================

class TestTableOfContents:
    def test_table_of_contents_basic(self):
        toc = TableOfContents(items=[{"id": "s1", "label": "Intro", "level": 1}])
        out = toc._render_custom()
        assert "toc" in out

    def test_table_of_contents_params(self):
        toc = TableOfContents(
            items=[{"id": "s1", "label": "Intro", "level": 1}],
            active="s1", title="TOC"
        )
        out = toc._render_custom()
        assert "toc-item-active" in out
        assert "TOC" in out

    def test_table_of_contents_html_escaping(self):
        toc = TableOfContents(items=[{"id": "s1", "label": XSS, "level": 1}])
        out = toc._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# CopyButton
# =========================================================================

class TestCopyButton:
    def test_copy_button_basic(self):
        cb = CopyButton(text="hello")
        out = cb._render_custom()
        assert "copy-btn" in out

    def test_copy_button_params(self):
        cb = CopyButton(text="abc", label="Copy it", variant="primary")
        out = cb._render_custom()
        assert "Copy it" in out
        assert "btn-primary" in out

    def test_copy_button_html_escaping(self):
        cb = CopyButton(text=XSS)
        out = cb._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# EmptyState
# =========================================================================

class TestEmptyState:
    def test_empty_state_basic(self):
        es = EmptyState(title="No data")
        out = es._render_custom()
        assert "empty-state" in out

    def test_empty_state_params(self):
        es = EmptyState(title="Empty", description="Nothing here",
                       action_label="Add", action_event="add_item")
        out = es._render_custom()
        assert "Nothing here" in out
        assert 'dj-click="add_item"' in out

    def test_empty_state_html_escaping(self):
        es = EmptyState(title=XSS, description=XSS)
        out = es._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Pagination
# =========================================================================

class TestPagination:
    def test_pagination_basic(self):
        p = Pagination(page=1, total_pages=5)
        out = p._render_custom()
        assert "dj-pagination" in out

    def test_pagination_params(self):
        p = Pagination(page=3, total_pages=10, prev_event="prev", next_event="next")
        out = p._render_custom()
        assert "Page 3 of 10" in out
        assert 'dj-click="prev"' in out

    def test_pagination_html_escaping(self):
        p = Pagination(page=1, total_pages=1, custom_class=XSS)
        out = p._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Avatar
# =========================================================================

class TestAvatar:
    def test_avatar_basic(self):
        a = Avatar(src="/img.jpg", alt="User")
        out = a._render_custom()
        assert "dj-avatar" in out

    def test_avatar_params(self):
        a = Avatar(initials="JD", size="lg", status="online")
        out = a._render_custom()
        assert "dj-avatar-lg" in out
        assert "dj-avatar-status-online" in out
        assert "JD" in out

    def test_avatar_html_escaping(self):
        a = Avatar(src=XSS, alt=XSS)
        out = a._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Skeleton
# =========================================================================

class TestSkeleton:
    def test_skeleton_basic(self):
        s = Skeleton()
        out = s._render_custom()
        assert "skeleton-text" in out

    def test_skeleton_params(self):
        s = Skeleton(skeleton_type="card", lines=2)
        out = s._render_custom()
        assert "skeleton-card" in out

    def test_skeleton_avatar(self):
        s = Skeleton(skeleton_type="avatar")
        out = s._render_custom()
        assert "skeleton-avatar" in out


# =========================================================================
# CodeBlock
# =========================================================================

class TestCodeBlock:
    def test_code_block_basic(self):
        cb = CodeBlock(code="print('hello')", language="python")
        out = cb._render_custom()
        assert "code-block" in out
        assert "language-python" in out

    def test_code_block_params(self):
        cb = CodeBlock(code="x = 1", language="python", filename="test.py")
        out = cb._render_custom()
        assert "test.py" in out

    def test_code_block_html_escaping(self):
        cb = CodeBlock(code=XSS, language=XSS)
        out = cb._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Breadcrumb
# =========================================================================

class TestBreadcrumb:
    def test_breadcrumb_basic(self):
        b = Breadcrumb(items=[{"label": "Home", "url": "/"}])
        out = b._render_custom()
        assert "breadcrumb" in out

    def test_breadcrumb_params(self):
        b = Breadcrumb(items=[
            {"label": "Home", "url": "/"},
            {"label": "Products", "active": True}
        ])
        out = b._render_custom()
        assert "breadcrumb-active" in out
        assert "breadcrumb-separator" in out

    def test_breadcrumb_html_escaping(self):
        b = Breadcrumb(items=[{"label": XSS, "url": XSS}])
        out = b._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# InlineEdit
# =========================================================================

class TestInlineEdit:
    def test_inline_edit_basic(self):
        ie = InlineEdit(value="Hello", name="field")
        out = ie._render_custom()
        assert "dj-inline-edit" in out

    def test_inline_edit_editing(self):
        ie = InlineEdit(value="Hello", name="field", editing=True)
        out = ie._render_custom()
        assert "dj-inline-edit--editing" in out
        assert '<input' in out

    def test_inline_edit_html_escaping(self):
        ie = InlineEdit(value=XSS, name="field")
        out = ie._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# DataTable
# =========================================================================

class TestDataTable:
    def test_data_table_basic(self):
        dt = DataTable(
            columns=[{"key": "name", "label": "Name"}],
            rows=[{"name": "Alice"}]
        )
        out = dt._render_custom()
        assert "dj-data-table" in out
        assert "Alice" in out

    def test_data_table_params(self):
        dt = DataTable(
            columns=[{"key": "id"}, {"key": "name"}],
            rows=[{"id": "1", "name": "Bob"}],
            striped=True, compact=True
        )
        out = dt._render_custom()
        assert "dj-data-table--striped" in out
        assert "dj-data-table--compact" in out

    def test_data_table_html_escaping(self):
        dt = DataTable(
            columns=[{"key": "name", "label": XSS}],
            rows=[{"name": XSS}]
        )
        out = dt._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Kbd
# =========================================================================

class TestKbd:
    def test_kbd_basic(self):
        k = Kbd(keys=["Ctrl", "K"])
        out = k._render_custom()
        assert "kbd-group" in out
        assert "Ctrl" in out

    def test_kbd_empty(self):
        k = Kbd()
        assert k._render_custom() == ""

    def test_kbd_html_escaping(self):
        k = Kbd(keys=[XSS])
        out = k._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Combobox
# =========================================================================

class TestCombobox:
    def test_combobox_basic(self):
        cb = Combobox(name="city", options=[{"value": "ny", "label": "New York"}])
        out = cb._render_custom()
        assert "combobox" in out

    def test_combobox_params(self):
        cb = Combobox(name="city", label="City", value="ny",
                     options=[{"value": "ny", "label": "NYC"}])
        out = cb._render_custom()
        assert "City" in out
        assert "NYC" in out

    def test_combobox_html_escaping(self):
        cb = Combobox(name="x", label=XSS)
        out = cb._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# DatePicker
# =========================================================================

class TestDatePicker:
    def test_date_picker_basic(self):
        dp = DatePicker(year=2024, month=6)
        out = dp._render_custom()
        assert "date-picker" in out
        assert "June" in out

    def test_date_picker_params(self):
        dp = DatePicker(year=2024, month=1, label="Birthday",
                       select_event="pick_date")
        out = dp._render_custom()
        assert "Birthday" in out
        assert 'dj-click="pick_date"' in out

    def test_date_picker_html_escaping(self):
        dp = DatePicker(label=XSS, year=2024, month=1)
        out = dp._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# ColorPicker
# =========================================================================

class TestColorPicker:
    def test_color_picker_basic(self):
        cp = ColorPicker(name="color")
        out = cp._render_custom()
        assert "color-picker" in out

    def test_color_picker_params(self):
        cp = ColorPicker(name="color", value="#FF0000", label="Pick color")
        out = cp._render_custom()
        assert "#FF0000" in out
        assert "Pick color" in out

    def test_color_picker_html_escaping(self):
        cp = ColorPicker(name="x", label=XSS)
        out = cp._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# MultiSelect
# =========================================================================

class TestMultiSelect:
    def test_multi_select_basic(self):
        ms = MultiSelect(name="tags", options=[{"value": "a", "label": "A"}])
        out = ms._render_custom()
        assert "multi-select" in out

    def test_multi_select_params(self):
        ms = MultiSelect(name="tags", label="Tags",
                        options=[{"value": "a", "label": "A"}], selected=["a"])
        out = ms._render_custom()
        assert "checked" in out

    def test_multi_select_html_escaping(self):
        ms = MultiSelect(name="x", label=XSS)
        out = ms._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# OtpInput
# =========================================================================

class TestOtpInput:
    def test_otp_input_basic(self):
        oi = OtpInput(name="code")
        out = oi._render_custom()
        assert "otp-input" in out

    def test_otp_input_params(self):
        oi = OtpInput(name="code", digits=4, label="Enter code")
        out = oi._render_custom()
        assert "Enter code" in out
        assert out.count("otp-digit") == 4

    def test_otp_input_html_escaping(self):
        oi = OtpInput(name="x", label=XSS)
        out = oi._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# NumberStepper
# =========================================================================

class TestNumberStepper:
    def test_number_stepper_basic(self):
        ns = NumberStepper(name="qty")
        out = ns._render_custom()
        assert "number-stepper" in out

    def test_number_stepper_params(self):
        ns = NumberStepper(name="qty", value=5, label="Quantity")
        out = ns._render_custom()
        assert 'value="5"' in out
        assert "Quantity" in out

    def test_number_stepper_html_escaping(self):
        ns = NumberStepper(name="x", label=XSS)
        out = ns._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# TagInput
# =========================================================================

class TestTagInput:
    def test_tag_input_basic(self):
        ti = TagInput(name="tags")
        out = ti._render_custom()
        assert "tag-input" in out

    def test_tag_input_params(self):
        ti = TagInput(name="tags", tags=["python", "django"], label="Skills")
        out = ti._render_custom()
        assert "python" in out
        assert "Skills" in out

    def test_tag_input_html_escaping(self):
        ti = TagInput(name="x", tags=[XSS])
        out = ti._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# ToggleGroup
# =========================================================================

class TestToggleGroup:
    def test_toggle_group_basic(self):
        tg = ToggleGroup(options=[{"value": "a", "label": "A"}])
        out = tg._render_custom()
        assert "toggle-group" in out

    def test_toggle_group_params(self):
        tg = ToggleGroup(options=[{"value": "a", "label": "A"}, {"value": "b", "label": "B"}],
                        value="a")
        out = tg._render_custom()
        assert "toggle-group-btn--active" in out

    def test_toggle_group_html_escaping(self):
        tg = ToggleGroup(options=[{"value": "a", "label": XSS}])
        out = tg._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# FileDropzone
# =========================================================================

class TestFileDropzone:
    def test_file_dropzone_basic(self):
        fd = FileDropzone()
        out = fd._render_custom()
        assert "dropzone" in out

    def test_file_dropzone_params(self):
        fd = FileDropzone(name="upload", label="Upload", accept=".pdf", multiple=True)
        out = fd._render_custom()
        assert "Upload" in out
        assert "multiple" in out
        assert ".pdf" in out

    def test_file_dropzone_html_escaping(self):
        fd = FileDropzone(label=XSS)
        out = fd._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# RichTextEditor
# =========================================================================

class TestRichTextEditor:
    def test_rich_text_editor_basic(self):
        rte = RichTextEditor()
        out = rte._render_custom()
        assert "rte" in out

    def test_rich_text_editor_params(self):
        rte = RichTextEditor(name="body", label="Content", height="300px")
        out = rte._render_custom()
        assert "Content" in out
        assert "300px" in out

    def test_rich_text_editor_html_escaping(self):
        rte = RichTextEditor(label=XSS, placeholder=XSS)
        out = rte._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# SplitButton
# =========================================================================

class TestSplitButton:
    def test_split_button_basic(self):
        sb = SplitButton(label="Save")
        out = sb._render_custom()
        assert "split-btn" in out

    def test_split_button_params(self):
        sb = SplitButton(label="Save", event="save", variant="success",
                        options=[{"label": "Save as", "event": "save_as"}])
        out = sb._render_custom()
        assert "split-btn-success" in out
        assert "Save as" in out

    def test_split_button_html_escaping(self):
        sb = SplitButton(label=XSS)
        out = sb._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# PageHeader
# =========================================================================

class TestPageHeader:
    def test_page_header_basic(self):
        ph = PageHeader(title="Dashboard")
        out = ph._render_custom()
        assert "dj-page-header" in out

    def test_page_header_params(self):
        ph = PageHeader(title="Products", subtitle="Manage items",
                       description="All your products")
        out = ph._render_custom()
        assert "Products" in out
        assert "Manage items" in out

    def test_page_header_html_escaping(self):
        ph = PageHeader(title=XSS, subtitle=XSS)
        out = ph._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Sidebar
# =========================================================================

class TestSidebar:
    def test_sidebar_basic(self):
        s = Sidebar(items=[{"label": "Home", "href": "/"}])
        out = s._render_custom()
        assert "dj-sidebar" in out

    def test_sidebar_params(self):
        s = Sidebar(items=[{"label": "Home", "href": "/", "active": True}],
                   title="App", collapsed=True)
        out = s._render_custom()
        assert "dj-sidebar--collapsed" in out
        assert "dj-sidebar__item--active" in out

    def test_sidebar_html_escaping(self):
        s = Sidebar(items=[{"label": XSS, "href": XSS}])
        out = s._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# NavMenu
# =========================================================================

class TestNavMenu:
    def test_nav_menu_basic(self):
        nm = NavMenu(items=[{"label": "Home", "href": "/"}])
        out = nm._render_custom()
        assert "dj-nav" in out

    def test_nav_menu_params(self):
        nm = NavMenu(items=[{"label": "Home", "href": "/", "active": True}],
                    brand="MyApp")
        out = nm._render_custom()
        assert "MyApp" in out
        assert "dj-nav__item--active" in out

    def test_nav_menu_html_escaping(self):
        nm = NavMenu(brand=XSS, items=[{"label": XSS, "href": XSS}])
        out = nm._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# AppShell
# =========================================================================

class TestAppShell:
    def test_app_shell_basic(self):
        a = AppShell(content="<main>Hello</main>")
        out = a._render_custom()
        assert "dj-app-shell" in out

    def test_app_shell_params(self):
        a = AppShell(sidebar="<nav>Nav</nav>", header="<h1>Header</h1>",
                    content="<p>Body</p>")
        out = a._render_custom()
        assert "dj-app-shell__sidebar" in out
        assert "dj-app-shell__header" in out

    def test_app_shell_html_escaping(self):
        a = AppShell(content="<p>X</p>", custom_class=XSS)
        out = a._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Toolbar
# =========================================================================

class TestToolbar:
    def test_toolbar_basic(self):
        t = Toolbar(content="<button>Action</button>")
        out = t._render_custom()
        assert "dj-toolbar" in out

    def test_toolbar_params(self):
        t = Toolbar(content="<button>X</button>", align="center", variant="compact")
        out = t._render_custom()
        assert "dj-toolbar--center" in out
        assert "dj-toolbar--compact" in out

    def test_toolbar_html_escaping(self):
        t = Toolbar(content="<button>X</button>", custom_class=XSS)
        out = t._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# FilterBar
# =========================================================================

class TestFilterBar:
    def test_filter_bar_basic(self):
        fb = FilterBar(content="<select>...</select>")
        out = fb._render_custom()
        assert "dj-filter-bar" in out

    def test_filter_bar_params(self):
        fb = FilterBar(content="<select>X</select>", active_count=3,
                      clear_event="reset_filters")
        out = fb._render_custom()
        assert "Clear filters" in out
        assert 'dj-click="reset_filters"' in out

    def test_filter_bar_html_escaping(self):
        fb = FilterBar(content="<select>X</select>", custom_class=XSS)
        out = fb._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# ThemeToggle
# =========================================================================

class TestThemeToggle:
    def test_theme_toggle_basic(self):
        tt = ThemeToggle()
        out = tt._render_custom()
        assert "dj-theme-toggle" in out

    def test_theme_toggle_params(self):
        tt = ThemeToggle(current="dark", event="set_theme")
        out = tt._render_custom()
        assert 'data-current="dark"' in out
        assert 'dj-click="set_theme"' in out

    def test_theme_toggle_html_escaping(self):
        tt = ThemeToggle(custom_class=XSS)
        out = tt._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# FormGroup
# =========================================================================

class TestFormGroup:
    def test_form_group_basic(self):
        fg = FormGroup(content="<input>", label="Name")
        out = fg._render_custom()
        assert "form-group" in out

    def test_form_group_params(self):
        fg = FormGroup(content="<input>", label="Email", required=True,
                      error="Invalid email", helper="Enter your email")
        out = fg._render_custom()
        assert "form-required" in out
        assert "Invalid email" in out
        assert "Enter your email" in out

    def test_form_group_html_escaping(self):
        fg = FormGroup(content="<input>", label=XSS, error=XSS)
        out = fg._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# InputGroup
# =========================================================================

class TestInputGroup:
    def test_input_group_basic(self):
        ig = InputGroup(content="<input>")
        out = ig._render_custom()
        assert "input-group" in out

    def test_input_group_params(self):
        ig = InputGroup(content="<input>", size="lg", error="Bad value")
        out = ig._render_custom()
        assert "input-group-lg" in out
        assert "Bad value" in out

    def test_input_group_html_escaping(self):
        ig = InputGroup(content="<input>", error=XSS)
        out = ig._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Fieldset
# =========================================================================

class TestFieldset:
    def test_fieldset_basic(self):
        f = Fieldset(content="<input>", legend="Personal Info")
        out = f._render_custom()
        assert "fieldset" in out
        assert "Personal Info" in out

    def test_fieldset_params(self):
        f = Fieldset(content="<input>", legend="Settings", disabled=True)
        out = f._render_custom()
        assert " disabled" in out

    def test_fieldset_html_escaping(self):
        f = Fieldset(content="<input>", legend=XSS)
        out = f._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Fab
# =========================================================================

class TestFab:
    def test_fab_basic(self):
        f = Fab()
        out = f._render_custom()
        assert "fab" in out

    def test_fab_params(self):
        f = Fab(icon="📝", event="create", position="bottom-left", variant="success")
        out = f._render_custom()
        assert "fab-bottom-left" in out
        assert "fab-success" in out
        assert 'dj-click="create"' in out

    def test_fab_html_escaping(self):
        f = Fab(icon=XSS, label=XSS)
        out = f._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out


# =========================================================================
# Icon
# =========================================================================

class TestIcon:
    def test_icon_basic(self):
        i = Icon(name="check")
        out = i._render_custom()
        assert "dj-icon" in out

    def test_icon_params(self):
        i = Icon(name="sun", size="lg", icon_set="heroicons")
        out = i._render_custom()
        assert "dj-icon--lg" in out
        assert 'data-icon="sun"' in out

    def test_icon_html_escaping(self):
        i = Icon(name=XSS, custom_class=XSS)
        out = i._render_custom()
        assert XSS_ESCAPED in out
        assert "<script>" not in out
