"""Tests for text display + loading pattern components."""
from django.template import Template, Context
import pytest


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ===========================================================================
# 1. Expandable Text (#118)
# ===========================================================================


class TestExpandableText:
    def test_collapsed_renders_line_clamp(self):
        html = render(
            '{% expandable_text max_lines=3 %}'
            'This is a long text that should be truncated.'
            '{% endexpandable_text %}'
        )
        assert "dj-expandable-text" in html
        assert "-webkit-line-clamp:3" in html
        assert "Read more" in html
        assert "This is a long text" in html

    def test_expanded_no_clamp(self):
        html = render(
            '{% expandable_text expanded=is_expanded %}'
            'Full text visible'
            '{% endexpandable_text %}',
            {"is_expanded": True},
        )
        assert "dj-expandable-text--expanded" in html
        assert "-webkit-line-clamp" not in html
        assert "Show less" in html

    def test_custom_labels(self):
        html = render(
            '{% expandable_text more_label="Continue" less_label="Collapse" %}'
            'text'
            '{% endexpandable_text %}'
        )
        assert "Continue" in html
        assert "Collapse" not in html

    def test_custom_labels_expanded(self):
        html = render(
            '{% expandable_text expanded=True less_label="Collapse" %}'
            'text'
            '{% endexpandable_text %}'
        )
        assert "Collapse" in html

    def test_custom_toggle_event(self):
        html = render(
            '{% expandable_text toggle_event="my_toggle" %}'
            'text'
            '{% endexpandable_text %}'
        )
        assert 'dj-click="my_toggle"' in html

    def test_custom_max_lines(self):
        html = render(
            '{% expandable_text max_lines=5 %}'
            'text'
            '{% endexpandable_text %}'
        )
        assert "-webkit-line-clamp:5" in html

    def test_custom_class(self):
        html = render(
            '{% expandable_text class="my-class" %}'
            'text'
            '{% endexpandable_text %}'
        )
        assert "my-class" in html


# ===========================================================================
# 2. Truncated List (#150)
# ===========================================================================


class TestTruncatedList:
    def test_basic_list_truncation(self):
        items = ["Alice", "Bob", "Charlie", "Dave", "Eve"]
        html = render(
            '{% truncated_list items=items max=3 %}',
            {"items": items},
        )
        assert "dj-truncated-list" in html
        assert "Alice" in html
        assert "Bob" in html
        assert "Charlie" in html
        assert "Dave" not in html
        assert "+2 more" in html

    def test_no_overflow_when_within_max(self):
        items = ["Alice", "Bob"]
        html = render(
            '{% truncated_list items=items max=3 %}',
            {"items": items},
        )
        assert "Alice" in html
        assert "Bob" in html
        assert "dj-truncated-list__overflow" not in html

    def test_expanded_shows_all(self):
        items = ["Alice", "Bob", "Charlie", "Dave"]
        html = render(
            '{% truncated_list items=items max=2 expanded=is_expanded %}',
            {"items": items, "is_expanded": True},
        )
        assert "Alice" in html
        assert "Dave" in html
        assert "dj-truncated-list--expanded" in html
        assert "Show less" in html

    def test_dict_items_with_label(self):
        items = [{"label": "Tag A"}, {"label": "Tag B"}, {"label": "Tag C"}, {"label": "Tag D"}]
        html = render(
            '{% truncated_list items=items max=2 %}',
            {"items": items},
        )
        assert "Tag A" in html
        assert "Tag B" in html
        assert "Tag C" not in html
        assert "+2 more" in html

    def test_custom_toggle_event(self):
        items = ["A", "B", "C", "D"]
        html = render(
            '{% truncated_list items=items max=2 toggle_event="expand_tags" %}',
            {"items": items},
        )
        assert 'dj-click="expand_tags"' in html

    def test_role_list(self):
        html = render(
            '{% truncated_list items=items max=3 %}',
            {"items": ["a"]},
        )
        assert 'role="list"' in html

    def test_empty_items(self):
        html = render('{% truncated_list items=items max=3 %}', {"items": []})
        assert "dj-truncated-list" in html
        assert "dj-truncated-list__overflow" not in html


# ===========================================================================
# 3. Inline Markdown Preview (#169)
# ===========================================================================


class TestMarkdownTextarea:
    def test_write_mode_renders_textarea(self):
        html = render('{% markdown_textarea name="content" %}')
        assert "dj-md-textarea" in html
        assert '<textarea' in html
        assert 'name="content"' in html
        assert "dj-md-textarea--preview" not in html

    def test_preview_mode_renders_preview(self):
        html = render(
            '{% markdown_textarea name="body" value=text preview=True %}',
            {"text": "# Hello"},
        )
        assert "dj-md-textarea--preview" in html
        assert "dj-md-textarea__preview" in html
        assert '<textarea' not in html
        assert '<input type="hidden"' in html

    def test_toolbar_tabs(self):
        html = render('{% markdown_textarea name="x" %}')
        assert "Write" in html
        assert "Preview" in html
        assert "dj-md-textarea__tab--active" in html

    def test_active_tab_write(self):
        html = render('{% markdown_textarea name="x" %}')
        # Write tab should be active when not in preview
        assert 'data-mode="write">Write' in html

    def test_active_tab_preview(self):
        html = render('{% markdown_textarea name="x" preview=True %}')
        # Preview tab should be active
        assert 'dj-md-textarea__tab--active" dj-click=' in html

    def test_custom_event(self):
        html = render('{% markdown_textarea name="x" toggle_event="switch_mode" %}')
        assert 'dj-click="switch_mode"' in html

    def test_placeholder(self):
        html = render('{% markdown_textarea name="x" placeholder="Type here..." %}')
        assert 'placeholder="Type here..."' in html

    def test_disabled(self):
        html = render('{% markdown_textarea name="x" disabled=True %}')
        assert " disabled" in html

    def test_hook_attribute(self):
        html = render('{% markdown_textarea name="x" %}')
        assert 'dj-hook="MarkdownTextarea"' in html

    def test_rows(self):
        html = render('{% markdown_textarea name="x" rows=10 %}')
        assert 'rows="10"' in html


# ===========================================================================
# 4. Skeleton Factory (#144)
# ===========================================================================


class TestSkeletonFactory:
    def test_data_table_skeleton(self):
        html = render('{% skeleton_for component="data_table" columns=3 rows=2 %}')
        assert "dj-skeleton--data-table" in html
        assert "dj-skeleton__pulse" in html
        assert '<thead>' in html
        assert '<tbody>' in html
        # 3 columns in header
        assert html.count('<th>') == 3
        # 2 rows * 3 columns = 6 td cells
        assert html.count('<td>') == 6

    def test_card_skeleton(self):
        html = render('{% skeleton_for component="card" %}')
        assert "dj-skeleton--card" in html
        assert "dj-skeleton__card-image" in html
        assert "dj-skeleton__card-body" in html

    def test_list_skeleton(self):
        html = render('{% skeleton_for component="list" rows=4 %}')
        assert "dj-skeleton--list" in html
        assert "dj-skeleton__circle" in html
        assert html.count("dj-skeleton__list-item") == 4

    def test_text_skeleton(self):
        html = render('{% skeleton_for component="text" rows=3 %}')
        assert "dj-skeleton--text" in html
        assert html.count("dj-skeleton__line") == 3

    def test_default_is_text(self):
        html = render('{% skeleton_for %}')
        assert "dj-skeleton--text" in html

    def test_unsupported_component_falls_back(self):
        html = render('{% skeleton_for component="nonexistent" %}')
        assert "dj-skeleton--text" in html

    def test_aria_label(self):
        html = render('{% skeleton_for component="card" %}')
        assert 'role="status"' in html
        assert 'aria-label="Loading"' in html

    def test_custom_class(self):
        html = render('{% skeleton_for component="text" class="my-loader" %}')
        assert "my-loader" in html


# ===========================================================================
# 5. Content Loader / Suspense (#152)
# ===========================================================================


class TestContentLoader:
    def test_loading_state_shows_placeholder(self):
        html = render(
            '{% await loading_event="data_loaded" %}'
            '{% skeleton_for component="text" rows=3 %}'
            '{% endawait %}'
        )
        assert "dj-content-loader" in html
        assert "dj-content-loader__placeholder" in html
        assert "dj-skeleton--text" in html
        assert 'role="status"' in html

    def test_loaded_state_shows_content(self):
        html = render(
            '{% await loading_event="data_loaded" loaded=True %}'
            '<p>Actual data here</p>'
            '{% endawait %}'
        )
        assert "dj-content-loader--loaded" in html
        assert "dj-content-loader__content" in html
        assert "Actual data here" in html
        assert "dj-content-loader__placeholder" not in html

    def test_loading_event_attribute(self):
        html = render(
            '{% await loading_event="fetch_users" %}'
            'placeholder'
            '{% endawait %}'
        )
        assert 'data-loading-event="fetch_users"' in html

    def test_error_state(self):
        html = render(
            '{% await loading_event="x" error=err %}placeholder{% endawait %}',
            {"err": "Network error"},
        )
        assert "dj-content-loader--error" in html
        assert "Network error" in html
        assert 'role="alert"' in html

    def test_error_with_retry(self):
        html = render(
            '{% await loading_event="x" error=err error_event="retry_load" %}'
            'placeholder'
            '{% endawait %}',
            {"err": "Timeout"},
        )
        assert "Retry" in html
        assert 'dj-click="retry_load"' in html

    def test_custom_class(self):
        html = render(
            '{% await loading_event="x" class="my-loader" %}'
            'placeholder'
            '{% endawait %}'
        )
        assert "my-loader" in html


# ===========================================================================
# Rust Handler Tests
# ===========================================================================


class TestRustHandlers:
    """Test the Rust engine handlers for the new components."""

    def test_expandable_text_handler_import(self):
        from djust_components.rust_handlers import ExpandableTextHandler
        handler = ExpandableTextHandler()
        result = handler.render(["max_lines=3"], "Hello world", {})
        assert "dj-expandable-text" in result
        assert "-webkit-line-clamp:3" in result
        assert "Hello world" in result

    def test_expandable_text_handler_expanded(self):
        from djust_components.rust_handlers import ExpandableTextHandler
        handler = ExpandableTextHandler()
        result = handler.render(["expanded=True"], "Full text", {})
        assert "dj-expandable-text--expanded" in result
        assert "Show less" in result

    def test_truncated_list_handler(self):
        from djust_components.rust_handlers import TruncatedListHandler
        handler = TruncatedListHandler()
        result = handler.render(
            ['max=2', 'items=items'],
            {"items": ["A", "B", "C", "D"]},
        )
        assert "dj-truncated-list" in result
        assert "A" in result
        assert "B" in result
        assert "+2 more" in result

    def test_markdown_textarea_handler(self):
        from djust_components.rust_handlers import MarkdownTextareaHandler
        handler = MarkdownTextareaHandler()
        result = handler.render(['name="body"'], {})
        assert "dj-md-textarea" in result
        assert '<textarea' in result
        assert 'name="body"' in result

    def test_markdown_textarea_handler_preview(self):
        from djust_components.rust_handlers import MarkdownTextareaHandler
        handler = MarkdownTextareaHandler()
        result = handler.render(['name="body"', 'preview=True', 'value="# Hi"'], {})
        assert "dj-md-textarea--preview" in result
        assert "dj-md-textarea__preview" in result

    def test_skeleton_for_handler_data_table(self):
        from djust_components.rust_handlers import SkeletonForHandler
        handler = SkeletonForHandler()
        result = handler.render(['component="data_table"', "columns=3", "rows=2"], {})
        assert "dj-skeleton--data-table" in result

    def test_skeleton_for_handler_card(self):
        from djust_components.rust_handlers import SkeletonForHandler
        handler = SkeletonForHandler()
        result = handler.render(['component="card"'], {})
        assert "dj-skeleton--card" in result

    def test_await_handler_loading(self):
        from djust_components.rust_handlers import AwaitHandler
        handler = AwaitHandler()
        result = handler.render(['loading_event="load"'], "skeleton here", {})
        assert "dj-content-loader__placeholder" in result
        assert "skeleton here" in result

    def test_await_handler_loaded(self):
        from djust_components.rust_handlers import AwaitHandler
        handler = AwaitHandler()
        result = handler.render(['loading_event="load"', "loaded=True"], "real data", {})
        assert "dj-content-loader--loaded" in result
        assert "dj-content-loader__content" in result

    def test_await_handler_error(self):
        from djust_components.rust_handlers import AwaitHandler
        handler = AwaitHandler()
        result = handler.render(['loading_event="load"', 'error="Failed"'], "x", {})
        assert "dj-content-loader--error" in result
        assert "Failed" in result


# ===========================================================================
# XSS Escaping
# ===========================================================================


class TestXSSEscaping:
    """Verify that user-controlled values are escaped to prevent XSS."""

    XSS = '<script>alert(1)</script>'
    XSS_ATTR = '" onmouseover="alert(1)" x="'

    def _assert_no_raw_script(self, html):
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def _assert_attr_escaped(self, html):
        assert '" onmouseover="' not in html
        assert "&quot;" in html

    # --- Expandable Text ---

    def test_expandable_text_content_xss(self):
        html = render(
            '{% expandable_text %}{{ xss }}{% endexpandable_text %}',
            {"xss": self.XSS},
        )
        # Django auto-escapes {{ xss }} in template content
        self._assert_no_raw_script(html)

    def test_expandable_text_toggle_event_xss(self):
        html = render(
            '{% expandable_text toggle_event=bad %}text{% endexpandable_text %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_expandable_text_more_label_xss(self):
        html = render(
            '{% expandable_text more_label=bad %}text{% endexpandable_text %}',
            {"bad": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_expandable_text_class_xss(self):
        html = render(
            '{% expandable_text class=bad %}text{% endexpandable_text %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Truncated List ---

    def test_truncated_list_items_xss(self):
        items = [self.XSS, "safe"]
        html = render(
            '{% truncated_list items=items max=5 %}',
            {"items": items},
        )
        self._assert_no_raw_script(html)

    def test_truncated_list_toggle_event_xss(self):
        items = ["a", "b", "c", "d"]
        html = render(
            '{% truncated_list items=items max=2 toggle_event=bad %}',
            {"items": items, "bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Markdown Textarea ---

    def test_markdown_textarea_name_xss(self):
        html = render(
            '{% markdown_textarea name=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_markdown_textarea_value_xss(self):
        html = render(
            '{% markdown_textarea name="x" value=bad preview=True %}',
            {"bad": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_markdown_textarea_placeholder_xss(self):
        html = render(
            '{% markdown_textarea name="x" placeholder=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_markdown_textarea_toggle_event_xss(self):
        html = render(
            '{% markdown_textarea name="x" toggle_event=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Skeleton Factory ---

    def test_skeleton_for_class_xss(self):
        html = render(
            '{% skeleton_for component="text" class=bad %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Content Loader / Await ---

    def test_await_loading_event_xss(self):
        html = render(
            '{% await loading_event=bad %}x{% endawait %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_await_error_xss(self):
        html = render(
            '{% await loading_event="x" error=bad %}x{% endawait %}',
            {"bad": self.XSS},
        )
        self._assert_no_raw_script(html)

    def test_await_error_event_xss(self):
        html = render(
            '{% await loading_event="x" error="oops" error_event=bad %}x{% endawait %}',
            {"bad": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # --- Rust Handler XSS ---

    def test_rust_expandable_text_xss(self):
        from djust_components.rust_handlers import ExpandableTextHandler
        handler = ExpandableTextHandler()
        result = handler.render(
            [f'toggle_event={self.XSS_ATTR}'],
            "text",
            {"toggle_event": self.XSS_ATTR},
        )
        assert '" onmouseover="' not in result

    def test_rust_truncated_list_items_xss(self):
        from djust_components.rust_handlers import TruncatedListHandler
        handler = TruncatedListHandler()
        result = handler.render(
            ["max=5", "items=items"],
            {"items": [self.XSS]},
        )
        assert "<script>" not in result

    def test_rust_markdown_textarea_xss(self):
        from djust_components.rust_handlers import MarkdownTextareaHandler
        handler = MarkdownTextareaHandler()
        result = handler.render(
            [f'name={self.XSS_ATTR}'],
            {"name": self.XSS_ATTR},
        )
        assert '" onmouseover="' not in result

    def test_rust_await_error_xss(self):
        from djust_components.rust_handlers import AwaitHandler
        handler = AwaitHandler()
        result = handler.render(
            [f'error={self.XSS}', 'loading_event="x"'],
            "x",
            {"error": self.XSS},
        )
        assert "<script>" not in result


# ===========================================================================
# Component Class Tests
# ===========================================================================


class TestComponentClasses:
    """Test the Python component classes (programmatic API)."""

    def test_expandable_text_class(self):
        from djust_components.components.expandable_text import ExpandableText
        comp = ExpandableText(text="Hello world", max_lines=2)
        html = comp.render()
        assert "dj-expandable-text" in html
        assert "-webkit-line-clamp:2" in html
        assert "Hello world" in html

    def test_expandable_text_class_expanded(self):

        from djust_components.components.expandable_text import ExpandableText
        comp = ExpandableText(text="Full", expanded=True)
        html = comp.render()
        assert "dj-expandable-text--expanded" in html

    def test_truncated_list_class(self):

        from djust_components.components.truncated_list import TruncatedList
        comp = TruncatedList(items=["A", "B", "C", "D"], max=2)
        html = comp.render()
        assert "A" in html
        assert "B" in html
        assert "+2 more" in html

    def test_markdown_textarea_class(self):

        from djust_components.components.markdown_textarea import MarkdownTextarea
        comp = MarkdownTextarea(name="body")
        html = comp.render()
        assert "dj-md-textarea" in html
        assert 'name="body"' in html

    def test_skeleton_factory_class(self):

        from djust_components.components.skeleton_factory import SkeletonFactory
        comp = SkeletonFactory(component="data_table", columns=3, rows=2)
        html = comp.render()
        assert "dj-skeleton--data-table" in html

    def test_content_loader_class(self):

        from djust_components.components.content_loader import ContentLoader
        comp = ContentLoader(loading_event="load", loaded=False)
        html = comp.render()
        assert "dj-content-loader" in html
        assert "dj-content-loader__placeholder" in html

    def test_content_loader_class_loaded(self):

        from djust_components.components.content_loader import ContentLoader
        comp = ContentLoader(loading_event="load", loaded=True, content="<p>Data</p>")
        html = comp.render()
        assert "dj-content-loader--loaded" in html
        assert "dj-content-loader__content" in html

    def test_content_loader_class_error(self):

        from djust_components.components.content_loader import ContentLoader
        comp = ContentLoader(loading_event="x", error="Failed!", error_event="retry")
        html = comp.render()
        assert "dj-content-loader--error" in html
        assert "Failed!" in html
        assert 'dj-click="retry"' in html
