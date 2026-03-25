"""Tests for v2.0 Batch 3 — Developer Tools + Specialized components (6)."""
import types
import sys

# Stub djust before importing components
_stub = types.ModuleType("djust")


class _Component:
    def __init__(self, **kwargs):
        pass

    def __html__(self):
        return self._render_custom()

    def __str__(self):
        return self._render_custom()


class _LV:
    pass


_stub.Component = _Component
_stub.LiveView = _LV
sys.modules.setdefault("djust", _stub)

# Stub djust.decorators
_dec_stub = types.ModuleType("djust.decorators")
_dec_stub.event_handler = lambda f: f
sys.modules.setdefault("djust.decorators", _dec_stub)

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

from djust_components.components.terminal import Terminal
from djust_components.components.markdown_editor import MarkdownEditor
from djust_components.components.json_viewer import JsonViewer
from djust_components.components.log_viewer import LogViewer
from djust_components.components.file_tree import FileTree
from djust_components.components.tour import Tour


def render(template_str, ctx=None):
    t = Template("{% load djust_components %}" + template_str)
    return t.render(Context(ctx or {}))


# ─── Terminal ───

class TestTerminal:
    def test_basic_render(self):
        html = render(
            '{% terminal output=lines %}',
            {"lines": ["$ ls", "file.txt"]},
        )
        assert "dj-terminal" in html
        assert 'dj-hook="Terminal"' in html
        assert "$ ls" in html
        assert "file.txt" in html

    def test_title_bar(self):
        html = render(
            '{% terminal output=lines title="Build" %}',
            {"lines": ["ok"]},
        )
        assert "dj-terminal__titlebar" in html
        assert "Build" in html
        assert "dj-terminal__dot--red" in html
        assert "dj-terminal__dot--yellow" in html
        assert "dj-terminal__dot--green" in html

    def test_line_numbers(self):
        html = render(
            '{% terminal output=lines show_line_numbers=True %}',
            {"lines": ["a", "b"]},
        )
        assert "dj-terminal__line-num" in html

    def test_stream_event(self):
        html = render(
            '{% terminal output=lines stream_event="new_output" %}',
            {"lines": []},
        )
        assert 'data-stream-event="new_output"' in html

    def test_wrap(self):
        html = render(
            '{% terminal output=lines wrap=True %}',
            {"lines": ["long line"]},
        )
        assert "dj-terminal--wrap" in html

    def test_empty_output(self):
        html = render('{% terminal output=lines %}', {"lines": []})
        assert "dj-terminal" in html
        assert "dj-terminal__line" not in html

    def test_component_class(self):
        t = Terminal(output=["hello"], title="Test")
        html = str(t)
        assert "dj-terminal" in html
        assert "Test" in html
        assert "hello" in html


# ─── Markdown Editor ───

class TestMarkdownEditor:
    def test_basic_render(self):
        html = render('{% markdown_editor name="content" %}')
        assert "dj-md-editor" in html
        assert 'dj-hook="MarkdownEditor"' in html
        assert 'name="content"' in html

    def test_preview_pane(self):
        html = render('{% markdown_editor name="c" preview=True %}')
        assert "dj-md-editor--split" in html
        assert "dj-md-editor__preview" in html

    def test_no_preview(self):
        html = render('{% markdown_editor name="c" preview=False %}')
        assert "dj-md-editor--split" not in html
        assert "dj-md-editor__preview" not in html

    def test_toolbar(self):
        html = render('{% markdown_editor name="c" %}')
        assert "dj-md-editor__toolbar" in html
        assert 'data-action="bold"' in html
        assert 'data-action="italic"' in html

    def test_no_toolbar(self):
        html = render('{% markdown_editor name="c" toolbar=False %}')
        assert "dj-md-editor__toolbar" not in html

    def test_disabled(self):
        html = render('{% markdown_editor name="c" disabled=True %}')
        assert "dj-md-editor--disabled" in html
        assert " disabled" in html

    def test_value(self):
        html = render(
            '{% markdown_editor name="c" value=val %}',
            {"val": "# Hello"},
        )
        assert "# Hello" in html

    def test_component_class(self):
        e = MarkdownEditor(name="body", preview=True, toolbar=True)
        html = str(e)
        assert "dj-md-editor" in html
        assert 'name="body"' in html


# ─── JSON Viewer ───

class TestJsonViewer:
    def test_basic_render(self):
        html = render(
            '{% json_viewer data=data %}',
            {"data": {"key": "value"}},
        )
        assert "dj-json-viewer" in html
        assert 'dj-hook="JsonViewer"' in html
        assert "key" in html
        assert "value" in html

    def test_collapsed_depth(self):
        html = render(
            '{% json_viewer data=data collapsed_depth=1 %}',
            {"data": {"a": {"b": 1}}},
        )
        assert "dj-json__node--collapsed" in html

    def test_copy_button(self):
        html = render(
            '{% json_viewer data=data %}',
            {"data": {"x": 1}},
        )
        assert "dj-json-viewer__copy" in html

    def test_no_copy_button(self):
        html = render(
            '{% json_viewer data=data copy_button=False %}',
            {"data": {"x": 1}},
        )
        assert "dj-json-viewer__copy" not in html

    def test_string_value(self):
        html = render(
            '{% json_viewer data=data collapsed_depth=10 %}',
            {"data": {"name": "djust"}},
        )
        assert "dj-json__value--string" in html

    def test_number_value(self):
        html = render(
            '{% json_viewer data=data collapsed_depth=10 %}',
            {"data": {"count": 42}},
        )
        assert "dj-json__value--number" in html
        assert "42" in html

    def test_bool_value(self):
        html = render(
            '{% json_viewer data=data collapsed_depth=10 %}',
            {"data": {"active": True}},
        )
        assert "dj-json__value--bool" in html
        assert "true" in html

    def test_null_value(self):
        html = render(
            '{% json_viewer data=data collapsed_depth=10 %}',
            {"data": {"nothing": None}},
        )
        assert "dj-json__value--null" in html
        assert "null" in html

    def test_array(self):
        html = render(
            '{% json_viewer data=data collapsed_depth=10 %}',
            {"data": [1, 2, 3]},
        )
        assert "dj-json__node--array" in html

    def test_empty_object(self):
        html = render(
            '{% json_viewer data=data collapsed_depth=10 %}',
            {"data": {}},
        )
        assert "{}" in html

    def test_empty_array(self):
        html = render(
            '{% json_viewer data=data collapsed_depth=10 %}',
            {"data": []},
        )
        assert "[]" in html

    def test_root_label(self):
        html = render(
            '{% json_viewer data=data root_label="config" %}',
            {"data": {"x": 1}},
        )
        assert "config" in html

    def test_component_class(self):
        v = JsonViewer(data={"a": 1}, collapsed_depth=3)
        html = str(v)
        assert "dj-json-viewer" in html
        assert '"a"' in html


# ─── Log Viewer ───

class TestLogViewer:
    def test_basic_render(self):
        html = render(
            '{% log_viewer lines=lines %}',
            {"lines": ["2026-03-25 INFO Starting", "2026-03-25 ERROR Boom"]},
        )
        assert "dj-log-viewer" in html
        assert 'dj-hook="LogViewer"' in html
        assert 'role="log"' in html
        assert "Starting" in html
        assert "Boom" in html

    def test_level_detection(self):
        html = render(
            '{% log_viewer lines=lines %}',
            {"lines": [
                "INFO ok",
                "WARNING caution",
                "ERROR fail",
                "DEBUG trace",
            ]},
        )
        assert "dj-log-viewer__line--info" in html
        assert "dj-log-viewer__line--warn" in html
        assert "dj-log-viewer__line--error" in html
        assert "dj-log-viewer__line--debug" in html

    def test_line_numbers(self):
        html = render(
            '{% log_viewer lines=lines show_line_numbers=True %}',
            {"lines": ["a"]},
        )
        assert "dj-log-viewer__num" in html

    def test_no_line_numbers(self):
        html = render(
            '{% log_viewer lines=lines show_line_numbers=False %}',
            {"lines": ["a"]},
        )
        assert "dj-log-viewer__num" not in html

    def test_stream_event(self):
        html = render(
            '{% log_viewer lines=lines stream_event="new_logs" %}',
            {"lines": []},
        )
        assert 'data-stream-event="new_logs"' in html

    def test_auto_scroll(self):
        html = render(
            '{% log_viewer lines=lines auto_scroll=True %}',
            {"lines": []},
        )
        assert 'data-auto-scroll="true"' in html

    def test_wrap(self):
        html = render(
            '{% log_viewer lines=lines wrap=True %}',
            {"lines": ["long line"]},
        )
        assert "dj-log-viewer--wrap" in html

    def test_empty_lines(self):
        html = render('{% log_viewer lines=lines %}', {"lines": []})
        assert "dj-log-viewer" in html
        assert "dj-log-viewer__line" not in html

    def test_component_class(self):
        lv = LogViewer(lines=["INFO started", "ERROR stopped"])
        html = str(lv)
        assert "dj-log-viewer" in html
        assert "started" in html


# ─── File Tree ───

class TestFileTree:
    def test_basic_render(self):
        html = render(
            '{% file_tree nodes=nodes event="select_file" %}',
            {"nodes": [
                {"name": "src", "type": "folder", "children": [
                    {"name": "main.py", "type": "file"},
                ]},
                {"name": "README.md", "type": "file"},
            ]},
        )
        assert "dj-file-tree" in html
        assert 'dj-hook="FileTree"' in html
        assert 'role="tree"' in html
        assert "src" in html
        assert "main.py" in html
        assert "README.md" in html

    def test_selected_file(self):
        html = render(
            '{% file_tree nodes=nodes selected="main.py" %}',
            {"nodes": [{"name": "main.py", "type": "file"}]},
        )
        assert "dj-file-tree__node--selected" in html

    def test_folder_expanded(self):
        html = render(
            '{% file_tree nodes=nodes %}',
            {"nodes": [{"name": "src", "type": "folder", "children": [
                {"name": "a.py", "type": "file"},
            ]}]},
        )
        assert "dj-file-tree__node--expanded" in html
        assert "dj-file-tree__children" in html

    def test_file_icons(self):
        html = render(
            '{% file_tree nodes=nodes show_icons=True %}',
            {"nodes": [{"name": "test.py", "type": "file"}]},
        )
        assert "dj-file-tree__icon" in html

    def test_no_icons(self):
        html = render(
            '{% file_tree nodes=nodes show_icons=False %}',
            {"nodes": [{"name": "test.py", "type": "file"}]},
        )
        assert "dj-file-tree__icon" not in html

    def test_event(self):
        html = render(
            '{% file_tree nodes=nodes event="open" %}',
            {"nodes": [{"name": "a.py", "type": "file"}]},
        )
        assert 'dj-click="open"' in html
        assert 'data-event="open"' in html

    def test_empty_nodes(self):
        html = render('{% file_tree nodes=nodes %}', {"nodes": []})
        assert "dj-file-tree" in html
        assert "dj-file-tree__node" not in html

    def test_treeitem_role(self):
        html = render(
            '{% file_tree nodes=nodes %}',
            {"nodes": [{"name": "a.py", "type": "file"}]},
        )
        assert 'role="treeitem"' in html

    def test_component_class(self):
        ft = FileTree(
            nodes=[{"name": "app.py", "type": "file"}],
            selected="app.py",
        )
        html = str(ft)
        assert "dj-file-tree" in html
        assert "app.py" in html
        assert "dj-file-tree__node--selected" in html


# ─── Tour / Onboarding Guide ───

class TestTour:
    STEPS = [
        {"target": "#nav", "title": "Navigation", "content": "Browse here."},
        {"target": "#btn", "title": "Action", "content": "Click to act."},
        {"target": "#end", "title": "Done", "content": "All done."},
    ]

    def test_basic_render(self):
        html = render(
            '{% tour steps=steps active=0 %}',
            {"steps": self.STEPS},
        )
        assert "dj-tour" in html
        assert 'dj-hook="Tour"' in html
        assert 'role="dialog"' in html
        assert "Navigation" in html
        assert "Browse here." in html

    def test_step_navigation(self):
        html = render(
            '{% tour steps=steps active=1 %}',
            {"steps": self.STEPS},
        )
        assert "Action" in html
        assert "dj-tour__prev" in html
        assert "Back" in html
        assert "Next" in html

    def test_first_step_no_back(self):
        html = render(
            '{% tour steps=steps active=0 %}',
            {"steps": self.STEPS},
        )
        assert "dj-tour__prev" not in html

    def test_last_step_finish(self):
        html = render(
            '{% tour steps=steps active=2 %}',
            {"steps": self.STEPS},
        )
        assert "Finish" in html
        assert 'data-value="finish"' in html

    def test_skip_button(self):
        html = render(
            '{% tour steps=steps active=0 show_skip=True %}',
            {"steps": self.STEPS},
        )
        assert "dj-tour__skip" in html
        assert "Skip tour" in html

    def test_no_skip_on_last(self):
        html = render(
            '{% tour steps=steps active=2 show_skip=True %}',
            {"steps": self.STEPS},
        )
        assert "dj-tour__skip" not in html

    def test_no_skip(self):
        html = render(
            '{% tour steps=steps active=0 show_skip=False %}',
            {"steps": self.STEPS},
        )
        assert "dj-tour__skip" not in html

    def test_progress_dots(self):
        html = render(
            '{% tour steps=steps active=1 show_progress=True %}',
            {"steps": self.STEPS},
        )
        assert "dj-tour__progress" in html
        assert "dj-tour__dot--active" in html
        assert "dj-tour__dot--completed" in html

    def test_no_progress(self):
        html = render(
            '{% tour steps=steps active=0 show_progress=False %}',
            {"steps": self.STEPS},
        )
        assert "dj-tour__progress" not in html

    def test_overlay(self):
        html = render(
            '{% tour steps=steps active=0 %}',
            {"steps": self.STEPS},
        )
        assert "dj-tour__overlay" in html

    def test_empty_steps_no_output(self):
        html = render('{% tour steps=steps active=0 %}', {"steps": []})
        assert "dj-tour" not in html

    def test_step_label(self):
        html = render(
            '{% tour steps=steps active=0 %}',
            {"steps": self.STEPS},
        )
        assert "Step 1 of 3" in html

    def test_target_data_attribute(self):
        html = render(
            '{% tour steps=steps active=0 %}',
            {"steps": self.STEPS},
        )
        assert 'data-target="#nav"' in html

    def test_component_class(self):
        t = Tour(steps=self.STEPS, active=0)
        html = str(t)
        assert "dj-tour" in html
        assert "Navigation" in html


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

    # Terminal
    def test_terminal_xss_output(self):
        html = render(
            '{% terminal output=lines %}',
            {"lines": [self.XSS]},
        )
        self._assert_script_escaped(html)

    def test_terminal_xss_title(self):
        html = render(
            '{% terminal output=lines title=xss %}',
            {"lines": [], "xss": self.XSS},
        )
        self._assert_script_escaped(html)

    def test_terminal_xss_stream_event(self):
        html = render(
            '{% terminal output=lines stream_event=xss %}',
            {"lines": [], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Markdown Editor
    def test_md_editor_xss_name(self):
        html = render(
            '{% markdown_editor name=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_md_editor_xss_value(self):
        html = render(
            '{% markdown_editor name="c" value=xss %}',
            {"xss": self.XSS},
        )
        self._assert_script_escaped(html)

    def test_md_editor_xss_placeholder(self):
        html = render(
            '{% markdown_editor name="c" placeholder=xss %}',
            {"xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # JSON Viewer
    def test_json_viewer_xss_key(self):
        html = render(
            '{% json_viewer data=data collapsed_depth=10 %}',
            {"data": {self.XSS: "val"}},
        )
        self._assert_script_escaped(html)

    def test_json_viewer_xss_string_value(self):
        html = render(
            '{% json_viewer data=data collapsed_depth=10 %}',
            {"data": {"k": self.XSS}},
        )
        self._assert_script_escaped(html)

    def test_json_viewer_xss_root_label(self):
        html = render(
            '{% json_viewer data=data root_label=xss %}',
            {"data": {"a": 1}, "xss": self.XSS},
        )
        self._assert_script_escaped(html)

    # Log Viewer
    def test_log_viewer_xss_line(self):
        html = render(
            '{% log_viewer lines=lines %}',
            {"lines": [self.XSS]},
        )
        self._assert_script_escaped(html)

    def test_log_viewer_xss_stream_event(self):
        html = render(
            '{% log_viewer lines=lines stream_event=xss %}',
            {"lines": [], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # File Tree
    def test_file_tree_xss_name(self):
        html = render(
            '{% file_tree nodes=nodes %}',
            {"nodes": [{"name": self.XSS, "type": "file"}]},
        )
        self._assert_script_escaped(html)

    def test_file_tree_xss_event(self):
        html = render(
            '{% file_tree nodes=nodes event=xss %}',
            {"nodes": [{"name": "a", "type": "file"}], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    def test_file_tree_xss_selected(self):
        html = render(
            '{% file_tree nodes=nodes selected=xss %}',
            {"nodes": [{"name": "a", "type": "file"}], "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)

    # Tour
    def test_tour_xss_title(self):
        html = render(
            '{% tour steps=steps active=0 %}',
            {"steps": [{"target": "#x", "title": self.XSS, "content": "ok"}]},
        )
        self._assert_script_escaped(html)

    def test_tour_xss_content(self):
        html = render(
            '{% tour steps=steps active=0 %}',
            {"steps": [{"target": "#x", "title": "T", "content": self.XSS}]},
        )
        self._assert_script_escaped(html)

    def test_tour_xss_target(self):
        html = render(
            '{% tour steps=steps active=0 %}',
            {"steps": [{"target": self.XSS_ATTR, "title": "T", "content": "C"}]},
        )
        self._assert_attr_escaped(html)

    def test_tour_xss_event(self):
        html = render(
            '{% tour steps=steps active=0 event=xss %}',
            {"steps": [{"target": "#x", "title": "T", "content": "C"}],
             "xss": self.XSS_ATTR},
        )
        self._assert_attr_escaped(html)
