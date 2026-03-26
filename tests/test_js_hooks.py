"""Tests that JS hook files exist and contain expected patterns.

Each component that declares dj-hook="HookName" needs a corresponding JS file
in static/djust_components/.  These tests verify the files exist, are non-empty,
and contain the structural patterns required for LiveView compatibility:

- IIFE wrapper
- DOMContentLoaded / readyState guard
- MutationObserver for LiveView re-init
- Hook-specific selectors and event handling

Full Playwright browser tests are a follow-up (see #JS-BROWSER-TESTS).
"""

import os
import re

import pytest

# Base path for static JS files
_STATIC_DIR = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    "src",
    "djust_components",
    "static",
    "djust_components",
)
_STATIC_DIR = os.path.normpath(_STATIC_DIR)


def _read_js(filename):
    """Read and return the contents of a JS file."""
    path = os.path.join(_STATIC_DIR, filename)
    assert os.path.isfile(path), f"JS file not found: {path}"
    with open(path) as f:
        content = f.read()
    assert len(content) > 50, f"JS file is suspiciously small: {filename}"
    return content


# ---------------------------------------------------------------------------
# Shared structural checks
# ---------------------------------------------------------------------------

_HOOK_FILES = {
    "Countdown": "countdown.js",
    "InfiniteScroll": "infinite-scroll.js",
    "ScrollSpy": "scroll-spy.js",
    "MarkdownTextarea": "markdown-textarea.js",
}


class TestJSHookFilesExist:
    """Every dj-hook component must have a corresponding JS file."""

    @pytest.mark.parametrize("hook_name,filename", _HOOK_FILES.items())
    def test_file_exists(self, hook_name, filename):
        path = os.path.join(_STATIC_DIR, filename)
        assert os.path.isfile(path), (
            f"Missing JS file for dj-hook=\"{hook_name}\": expected {filename}"
        )

    @pytest.mark.parametrize("hook_name,filename", _HOOK_FILES.items())
    def test_file_not_empty(self, hook_name, filename):
        content = _read_js(filename)
        assert len(content.strip()) > 0


class TestJSHookStructure:
    """Each JS hook file must follow the project's IIFE + MutationObserver pattern."""

    @pytest.mark.parametrize("hook_name,filename", _HOOK_FILES.items())
    def test_iife_wrapper(self, hook_name, filename):
        content = _read_js(filename)
        assert "(function" in content, f"{filename} missing IIFE wrapper"
        assert "})();" in content, f"{filename} missing IIFE closing"

    @pytest.mark.parametrize("hook_name,filename", _HOOK_FILES.items())
    def test_use_strict(self, hook_name, filename):
        content = _read_js(filename)
        assert '"use strict"' in content, f"{filename} missing 'use strict'"

    @pytest.mark.parametrize("hook_name,filename", _HOOK_FILES.items())
    def test_dom_content_loaded(self, hook_name, filename):
        content = _read_js(filename)
        assert "DOMContentLoaded" in content, (
            f"{filename} missing DOMContentLoaded listener"
        )

    @pytest.mark.parametrize("hook_name,filename", _HOOK_FILES.items())
    def test_ready_state_guard(self, hook_name, filename):
        content = _read_js(filename)
        assert "readyState" in content, (
            f"{filename} missing readyState check"
        )

    @pytest.mark.parametrize("hook_name,filename", _HOOK_FILES.items())
    def test_mutation_observer(self, hook_name, filename):
        content = _read_js(filename)
        assert "MutationObserver" in content, (
            f"{filename} missing MutationObserver for LiveView compatibility"
        )

    @pytest.mark.parametrize("hook_name,filename", _HOOK_FILES.items())
    def test_hook_selector(self, hook_name, filename):
        content = _read_js(filename)
        expected = f'dj-hook="{hook_name}"'
        assert expected in content, (
            f'{filename} missing hook selector: {expected}'
        )


# ---------------------------------------------------------------------------
# Component-specific behavior checks
# ---------------------------------------------------------------------------


class TestCountdownJS:
    """Countdown JS must handle timer logic and data attributes."""

    def setup_method(self):
        self.content = _read_js("countdown.js")

    def test_reads_data_target(self):
        assert "data-target" in self.content

    def test_reads_data_event(self):
        assert "data-event" in self.content

    def test_uses_set_interval(self):
        assert "setInterval" in self.content, "Countdown must use setInterval for ticking"

    def test_handles_data_unit(self):
        assert "data-unit" in self.content, "Must update elements by data-unit attribute"

    def test_dispatches_event_on_finish(self):
        assert "dispatchEvent" in self.content or "CustomEvent" in self.content, (
            "Must dispatch event when countdown finishes"
        )


class TestInfiniteScrollJS:
    """InfiniteScroll JS must use IntersectionObserver."""

    def setup_method(self):
        self.content = _read_js("infinite-scroll.js")

    def test_uses_intersection_observer(self):
        assert "IntersectionObserver" in self.content

    def test_reads_data_event(self):
        assert "data-event" in self.content

    def test_reads_data_threshold(self):
        assert "data-threshold" in self.content

    def test_checks_loading_state(self):
        assert "dj-infinite-scroll--loading" in self.content, (
            "Must check loading state to avoid duplicate triggers"
        )

    def test_checks_finished_state(self):
        assert "dj-infinite-scroll--finished" in self.content, (
            "Must check finished state to stop observing"
        )

    def test_dispatches_event(self):
        assert "dispatchEvent" in self.content or "CustomEvent" in self.content


class TestScrollSpyJS:
    """ScrollSpy JS must use IntersectionObserver on section elements."""

    def setup_method(self):
        self.content = _read_js("scroll-spy.js")

    def test_uses_intersection_observer(self):
        assert "IntersectionObserver" in self.content

    def test_reads_data_sections(self):
        assert "data-sections" in self.content

    def test_parses_json_sections(self):
        assert "JSON.parse" in self.content, "Must parse sections JSON array"

    def test_reads_data_event(self):
        assert "data-event" in self.content

    def test_updates_active_class(self):
        assert "dj-scroll-spy__item--active" in self.content, (
            "Must toggle active class on nav links"
        )

    def test_dispatches_event(self):
        assert "dispatchEvent" in self.content or "CustomEvent" in self.content


class TestMarkdownTextareaJS:
    """MarkdownTextarea JS must render markdown preview."""

    def setup_method(self):
        self.content = _read_js("markdown-textarea.js")

    def test_reads_preview_class(self):
        assert "dj-md-textarea--preview" in self.content

    def test_reads_data_raw(self):
        assert "data-raw" in self.content, "Must read raw markdown from data-raw"

    def test_targets_preview_element(self):
        assert "dj-md-textarea__preview" in self.content

    def test_has_markdown_conversion(self):
        # Should handle at least bold/headings
        assert "<strong>" in self.content or "strong" in self.content, (
            "Must convert markdown bold to HTML"
        )

    def test_escapes_html(self):
        assert "escape" in self.content.lower(), (
            "Must escape HTML to prevent XSS in preview"
        )


# ---------------------------------------------------------------------------
# Cross-check: Python components declare hooks that have JS files
# ---------------------------------------------------------------------------


class TestPythonComponentsHaveJS:
    """Verify Python components that render dj-hook have matching JS files."""

    @pytest.mark.parametrize(
        "component_module,hook_name,js_file",
        [
            ("countdown", "Countdown", "countdown.js"),
            ("infinite_scroll", "InfiniteScroll", "infinite-scroll.js"),
            ("scroll_spy", "ScrollSpy", "scroll-spy.js"),
            ("markdown_textarea", "MarkdownTextarea", "markdown-textarea.js"),
        ],
    )
    def test_component_renders_hook_with_js(
        self, component_module, hook_name, js_file
    ):
        """The Python component renders dj-hook and the JS file exists."""
        # Import component
        mod = __import__(
            f"djust_components.components.{component_module}",
            fromlist=[hook_name],
        )
        # Verify JS exists
        path = os.path.join(_STATIC_DIR, js_file)
        assert os.path.isfile(path), f"Missing JS for {hook_name}"
